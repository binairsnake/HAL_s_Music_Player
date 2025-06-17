import sys
import os
import json
import pygame
from odf import text, teletype
from odf.opendocument import OpenDocumentText, load
from mutagen import File
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QTreeView, QVBoxLayout, QHBoxLayout, QWidget,
                             QLineEdit, QMessageBox, QProgressDialog, QStatusBar,
                             QComboBox, QFileDialog, QGroupBox, QFormLayout,
                             QDialog, QDialogButtonBox, QProgressBar, QScrollArea,
                             QTextEdit, QSplitter, QCheckBox, QFrame, QMenu,
                             QStyledItemDelegate)
from PyQt6.QtCore import Qt, QDir, QTimer, QEvent, QTime, QRect
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap, QFont, QPainter, QColor

# Import the language system
try:
    from languages_db import get_text, get_language_name, get_available_languages, add_language
except ImportError:
    # Fallback if languages_db.py is not found
    def get_text(key, language='nl', **kwargs):
        return key
    def get_language_name(language_code):
        return language_code
    def get_available_languages():
        return ['nl', 'en']
    def add_language(language_code, language_name, translations):
        pass


class PlaylistNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Playlist")
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Create input field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter playlist name")
        layout.addWidget(self.name_input)

        # Create buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_name(self):
        return self.name_input.text().strip()


class HelpDialog(QDialog):
    def __init__(self, parent=None, language='nl'):
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(get_text('help_title', self.language))
        self.setModal(True)
        self.setMinimumSize(800, 600)

        # Create help images directory if it doesn't exist
        self.help_images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "help_images")
        if not os.path.exists(self.help_images_dir):
            os.makedirs(self.help_images_dir)

        layout = QVBoxLayout(self)

        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Add title
        title = QLabel(get_text('help_title', self.language))
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        content_layout.addWidget(title)

        # Add sections (dynamically from language file)
        for i in range(1, 12):
            section_title = get_text(f'help_section_{i}_title', self.language)
            section_text = get_text(f'help_section_{i}_text', self.language)
            image_name = [
                "scan_drives.png", "read_files.png", "toggle_view.png", "tree_view.png", "filter.png",
                "playback.png", "favorites.png", "lyrics.png", "playlists.png", "file_types.png", "config.png"
            ][i-1]

            # Add section title
            section_title_label = QLabel(section_title)
            section_title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
            content_layout.addWidget(section_title_label)

            # Add section text
            section_text_label = QLabel(section_text)
            section_text_label.setWordWrap(True)
            content_layout.addWidget(section_text_label)

            # Add section image
            image_path = os.path.join(self.help_images_dir, image_name)
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                # Scale image if it's too large
                if pixmap.width() > 700:
                    pixmap = pixmap.scaled(700, 400, Qt.AspectRatioMode.KeepAspectRatio)
                image_label = QLabel()
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                content_layout.addWidget(image_label)
            else:
                # Show placeholder if image doesn't exist
                placeholder = QLabel(get_text('image_not_found', self.language, image=image_name))
                placeholder.setStyleSheet("font-style: italic; color: gray;")
                content_layout.addWidget(placeholder)

        # Add close button
        close_button = QPushButton(get_text('close_button', self.language))
        close_button.clicked.connect(self.accept)
        content_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        scroll.setWidget(content)
        layout.addWidget(scroll)


class LyricsDialog(QDialog):
    def __init__(self, parent=None, language='nl'):
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(get_text('lyrics_title', self.language))
        self.setModal(True)
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # Create text edit for lyrics
        self.lyrics_text = QTextEdit()
        self.lyrics_text.setReadOnly(False)  # Allow editing
        layout.addWidget(self.lyrics_text)

        # Create buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton(get_text('save_button', self.language))
        save_button.clicked.connect(self.save_lyrics)
        close_button = QPushButton(get_text('close_button', self.language))
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def set_lyrics(self, lyrics):
        self.lyrics_text.setText(lyrics)

    def get_lyrics(self):
        return self.lyrics_text.toPlainText()

    def save_lyrics(self):
        self.accept()


class LyricsMappingDialog(QDialog):
    def __init__(self, parent=None, music_file=None, current_text_file=None, current_srt_file=None, language='nl'):
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(get_text('lyrics_mapping_title', self.language))
        self.setModal(True)

        self.music_file = music_file
        self.current_text_file = current_text_file
        self.current_srt_file = current_srt_file

        layout = QVBoxLayout(self)

        # Add labels
        music_label = QLabel(get_text('music_file_label', self.language, file=os.path.basename(music_file)))
        layout.addWidget(music_label)

        # Add text lyrics section
        text_group = QGroupBox(get_text('text_lyrics_group', self.language))
        text_layout = QVBoxLayout()

        self.text_path = QLineEdit()
        self.text_path.setReadOnly(True)
        if current_text_file:
            self.text_path.setText(current_text_file)

        text_button_layout = QHBoxLayout()
        text_browse_button = QPushButton(get_text('browse_button', self.language))
        text_browse_button.clicked.connect(self.browse_text)
        text_clear_button = QPushButton(get_text('clear_button', self.language))
        text_clear_button.clicked.connect(lambda: self.text_path.clear())
        text_button_layout.addWidget(text_browse_button)
        text_button_layout.addWidget(text_clear_button)

        text_layout.addWidget(self.text_path)
        text_layout.addLayout(text_button_layout)
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        # Add SRT section
        srt_group = QGroupBox(get_text('karaoke_group', self.language))
        srt_layout = QVBoxLayout()

        self.srt_path = QLineEdit()
        self.srt_path.setReadOnly(True)
        if current_srt_file:
            self.srt_path.setText(current_srt_file)

        srt_button_layout = QHBoxLayout()
        srt_browse_button = QPushButton(get_text('browse_button', self.language))
        srt_browse_button.clicked.connect(self.browse_srt)
        srt_clear_button = QPushButton(get_text('clear_button', self.language))
        srt_clear_button.clicked.connect(lambda: self.srt_path.clear())
        srt_button_layout.addWidget(srt_browse_button)
        srt_button_layout.addWidget(srt_clear_button)

        srt_layout.addWidget(self.srt_path)
        srt_layout.addLayout(srt_button_layout)
        srt_group.setLayout(srt_layout)
        layout.addWidget(srt_group)

        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def browse_text(self):
        """Browse for text lyrics file (TXT or ODT)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            get_text('select_lyrics', self.language),
            self.parent().lyrics_dir,
            "Text Files (*.txt);;ODT Files (*.odt)"
        )

        if file_path:
            self.text_path.setText(file_path)

    def browse_srt(self):
        """Browse for SRT file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            get_text('select_karaoke', self.language),
            self.parent().lyrics_dir,
            "SRT Files (*.srt)"
        )

        if file_path:
            self.srt_path.setText(file_path)

    def get_text_path(self):
        return self.text_path.text()

    def get_srt_path(self):
        return self.srt_path.text()

    def load_lyrics(self, music_file):
        """Load lyrics for a music file with improved error handling"""
        if not music_file:
            self.show_error("Fout", "Geen muziekbestand geselecteerd")
            return

        print(f"Loading lyrics for: {music_file}")  # Debug logging

        try:
            # Clear current lyrics display first
            self._clear_lyrics_display()

            # Get current mappings
            mapping = self.lyrics_mapping.get(music_file, {})
            text_path = None
            srt_path = None

            if isinstance(mapping, dict):
                text_path = mapping.get('text_path')
                srt_path = mapping.get('srt_path')
            else:
                # Handle old format
                if mapping and isinstance(mapping, str):  # Ensure mapping is a string
                    ext = os.path.splitext(mapping)[1].lower()
                    if ext == '.srt':
                        srt_path = mapping
                    else:
                        text_path = mapping

            # Try to load text lyrics first
            text_loaded = False
            if text_path and isinstance(text_path, str) and os.path.exists(text_path):
                ext = os.path.splitext(text_path)[1].lower()
                if ext == '.odt':
                    text_loaded = self._load_odt_file(text_path)
                else:
                    text_loaded = self._load_txt_file(text_path)

            # If no text lyrics found from mapping, try to find one with same name
            if not text_loaded:
                text_loaded = self._try_load_text_lyrics(music_file)

            # Handle SRT display
            if self.srt_display and self.srt_display.isVisible():
                # Try to load SRT from mapping first
                if srt_path and isinstance(srt_path, str) and os.path.exists(srt_path):
                    self._load_srt_file(srt_path)
                else:
                    # Try to find SRT with same name
                    base_name = os.path.splitext(os.path.basename(music_file))[0]
                    srt_path = os.path.join(self.lyrics_dir, f"{base_name}.srt")
                    if os.path.exists(srt_path):
                        self._load_srt_file(srt_path)
                    else:
                        # No SRT file found, clear the display
                        self.srt_display.stop_display()
                        self.srt_display.subtitle_label.clear()

            # If no lyrics found at all, show a message
            if not text_loaded and not (self.srt_display and self.srt_display.isVisible()):
                print("No lyrics found for this track")  # Debug logging
                if hasattr(self, 'lyrics_display'):
                    self.lyrics_display.setText("Geen songtekst gevonden")
                self.statusBar.showMessage("Geen songtekst gevonden voor dit nummer")

        except Exception as e:
            self.show_error("Onverwachte fout", "Fout bij laden songtekst", str(e))
            if hasattr(self, 'lyrics_display'):
                self.lyrics_display.setText("Fout bij laden songtekst")


class SRTParser:
    def __init__(self):
        self.subtitles = []

    def parse_srt(self, file_path):
        """Parse an SRT file and return a list of subtitle entries"""
        self.subtitles = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split into subtitle blocks
            blocks = content.strip().split('\n\n')

            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Parse time
                    time_line = lines[1]
                    start_time, end_time = time_line.split(' --> ')

                    # Convert time to seconds
                    start_seconds = self.time_to_seconds(start_time)
                    end_seconds = self.time_to_seconds(end_time)

                    # Get text (can be multiple lines)
                    text = '\n'.join(lines[2:])

                    self.subtitles.append({
                        'start': start_seconds,
                        'end': end_seconds,
                        'text': text
                    })

            # Sort by start time
            self.subtitles.sort(key=lambda x: x['start'])
            return True
        except Exception as e:
            print(f"Error parsing SRT file: {str(e)}")
            return False

    def time_to_seconds(self, time_str):
        """Convert SRT time format (HH:MM:SS,mmm) to seconds"""
        try:
            hours, minutes, seconds = time_str.replace(',', '.').split(':')
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        except:
            return 0.0

    def get_subtitle_at_time(self, current_time):
        """Get the subtitle text for the current time"""
        for subtitle in self.subtitles:
            if subtitle['start'] <= current_time <= subtitle['end']:
                return subtitle['text']
        return ""


class LyricsDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.srt_parser = SRTParser()
        self.current_subtitle = ""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_subtitle)
        self.update_timer.setInterval(100)  # Update every 100ms

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create label for subtitle display
        self.subtitle_label = QLabel()
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 0.7);
                padding: 20px;
                border-radius: 10px;
            }
        """)

        # Set large font
        font = QFont()
        font.setPointSize(24)  # Large font size
        font.setBold(True)
        self.subtitle_label.setFont(font)

        layout.addWidget(self.subtitle_label)

    def load_srt(self, file_path):
        """Load and parse an SRT file"""
        if self.srt_parser.parse_srt(file_path):
            self.start_display()
            return True
        return False

    def start_display(self):
        """Start the subtitle display timer"""
        self.update_timer.start()

    def stop_display(self):
        """Stop the subtitle display timer"""
        self.update_timer.stop()
        self.subtitle_label.clear()

    def update_subtitle(self):
        """Update the displayed subtitle based on current playback time"""
        if not self.parent() or not self.parent().is_playing:
            return

        current_time = pygame.mixer.music.get_pos() / 1000.0
        if self.parent().pause_position > 0:
            current_time = self.parent().pause_position

        subtitle = self.srt_parser.get_subtitle_at_time(current_time)
        if subtitle != self.current_subtitle:
            self.current_subtitle = subtitle
            self.subtitle_label.setText(subtitle)


class SRTDisplayDialog(QDialog):
    def __init__(self, parent=None, language='nl'):
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(get_text('karaoke_title', self.language))
        self.setModal(False)  # Non-modal so it can stay open while using main window
        self.is_fullscreen = False  # Track fullscreen state

        # Set window flags for a frameless window that stays on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # No window frame
            Qt.WindowType.Tool |  # Tool window
            Qt.WindowType.WindowStaysOnTopHint  # Always on top
        )

        # Create main layout with no margins in fullscreen
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        # Create container widget for the label to control its size
        self.label_container = QWidget()
        self.label_container.setStyleSheet("background-color: transparent;")
        label_container_layout = QVBoxLayout(self.label_container)
        label_container_layout.setContentsMargins(0, 0, 0, 0)
        label_container_layout.setSpacing(0)

        # Create label for subtitle display with larger font and better wrapping
        self.subtitle_label = QLabel()
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 0.8);
                padding: 30px;
                border-radius: 15px;
                font-size: 48px;
                font-weight: bold;
                min-height: 200px;
                max-width: 1200px;
            }
        """)

        # Set large font with better line spacing
        font = QFont()
        font.setPointSize(48)
        font.setBold(True)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.subtitle_label.setFont(font)

        # Set text format for better wrapping
        text_format = Qt.TextFormat.RichText
        self.subtitle_label.setTextFormat(text_format)

        # Add label to container
        label_container_layout.addWidget(self.subtitle_label)

        # Add container to main layout
        self.main_layout.addWidget(self.label_container)

        # Create button container widget
        self.button_container = QWidget()
        self.button_container.setObjectName("button_container")
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Add fullscreen toggle button
        self.fullscreen_button = QPushButton(get_text('fullscreen_button', self.language))
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_button.setStyleSheet("""
            QPushButton {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555555;
                padding: 10px;
                border-radius: 5px;
                min-width: 120px;
                margin-top: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
            }
        """)
        button_layout.addWidget(self.fullscreen_button)

        # Add close button
        self.close_button = QPushButton(get_text('close_karaoke', self.language))
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555555;
                padding: 10px;
                border-radius: 5px;
                min-width: 100px;
                margin-top: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
            }
        """)
        button_layout.addWidget(self.close_button)

        self.main_layout.addWidget(self.button_container)

        # Initialize SRT parser and timer
        self.srt_parser = SRTParser()
        self.current_subtitle = ""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_subtitle)
        self.update_timer.setInterval(100)

        # Store original geometry
        self.normal_geometry = None

        # Calculate initial window size and position
        screen = QApplication.primaryScreen().geometry()
        window_width = min(int(screen.width() * 0.9), 1200)
        window_height = int(screen.height() * 0.4)
        window_x = (screen.width() - window_width) // 2
        window_y = int(screen.height() * 0.5)

        # Set initial size and position
        self.setFixedSize(window_width, window_height)
        self.move(window_x, window_y)

        # Make window draggable
        self.old_pos = None

    def toggle_fullscreen(self):
        """Toggle between normal and fullscreen mode"""
        try:
            if not self.is_fullscreen:
                # Store current geometry before going fullscreen
                self.normal_geometry = self.geometry()

                # Get screen geometry
                screen = QApplication.primaryScreen().geometry()

                # Hide button container
                self.button_container.hide()

                # Remove margins in fullscreen
                self.main_layout.setContentsMargins(0, 0, 0, 0)
                self.main_layout.setSpacing(0)

                # Adjust label container and label style for fullscreen
                self.label_container.setStyleSheet("""
                    QWidget {
                        background-color: rgba(0, 0, 0, 0.8);
                        width: 100%;
                        height: 100%;
                    }
                """)
                self.subtitle_label.setStyleSheet("""
                    QLabel {
                        color: white;
                        background-color: transparent;
                        padding: 50px;
                        border-radius: 0px;
                        font-size: 72px;
                        font-weight: bold;
                        min-height: 300px;
                        max-width: none;
                        width: 90%;
                        margin: 0 auto;
                        qproperty-alignment: AlignCenter;
                    }
                """)

                # Set fullscreen geometry and ensure label takes full width
                self.setFixedSize(screen.width(), screen.height())
                self.move(0, 0)
                self.label_container.setFixedWidth(screen.width())
                self.subtitle_label.setFixedWidth(int(screen.width() * 0.9))

                # Update button text
                self.fullscreen_button.setText(get_text('normal_screen_button', self.language))
                self.is_fullscreen = True

            else:
                # Restore normal geometry
                if self.normal_geometry:
                    self.setFixedSize(self.normal_geometry.width(), self.normal_geometry.height())
                    self.move(self.normal_geometry.x(), self.normal_geometry.y())

                # Restore margins and spacing
                self.main_layout.setContentsMargins(20, 20, 20, 20)
                self.main_layout.setSpacing(10)

                # Show button container again
                self.button_container.show()

                # Restore label container and label style
                self.label_container.setStyleSheet("background-color: transparent;")
                self.label_container.setFixedWidth(self.normal_geometry.width())
                self.subtitle_label.setStyleSheet("""
                    QLabel {
                        color: white;
                        background-color: rgba(0, 0, 0, 0.8);
                        padding: 30px;
                        border-radius: 15px;
                        font-size: 48px;
                        font-weight: bold;
                        min-height: 200px;
                        max-width: 1200px;
                        margin: 0 auto;
                        qproperty-alignment: AlignCenter;
                    }
                """)
                self.subtitle_label.setFixedWidth(1200)

                # Update button text
                self.fullscreen_button.setText(get_text('fullscreen_button', self.language))
                self.is_fullscreen = False

        except Exception as e:
            print(f"Error in toggle_fullscreen: {str(e)}")
            # Try to recover normal state
            self.is_fullscreen = False
            if self.normal_geometry:
                self.setFixedSize(self.normal_geometry.width(), self.normal_geometry.height())
                self.move(self.normal_geometry.x(), self.normal_geometry.y())
            self.main_layout.setContentsMargins(20, 20, 20, 20)
            self.main_layout.setSpacing(10)
            self.button_container.show()
            self.label_container.setStyleSheet("background-color: transparent;")
            self.subtitle_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: rgba(0, 0, 0, 0.8);
                    padding: 30px;
                    border-radius: 15px;
                    font-size: 48px;
                    font-weight: bold;
                    min-height: 200px;
                    max-width: 1200px;
                    margin: 0 auto;
                    qproperty-alignment: AlignCenter;
                }
            """)
            self.fullscreen_button.setText(get_text('fullscreen_button', self.language))

    def update_subtitle(self):
        """Update the displayed subtitle based on current playback time"""
        if not self.parent() or not self.parent().is_playing:
            return

        current_time = pygame.mixer.music.get_pos() / 1000.0
        if self.parent().pause_position > 0:
            current_time = self.parent().pause_position

        subtitle = self.srt_parser.get_subtitle_at_time(current_time)
        if subtitle != self.current_subtitle:
            self.current_subtitle = subtitle
            # Format text with HTML for better wrapping and line breaks
            formatted_text = subtitle.replace('\n', '<br>')
            # Add extra line height and center alignment in HTML
            self.subtitle_label.setText(f"<div style='line-height: 1.4; text-align: center;'>{formatted_text}</div>")

    def keyPressEvent(self, event):
        """Handle keyboard events"""
        try:
            if event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
                self.toggle_fullscreen()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"Error in keyPressEvent: {str(e)}")
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Stop the display timer
            self.update_timer.stop()
            # Accept the close event
            event.accept()
        except Exception as e:
            print(f"Error in closeEvent: {str(e)}")
            event.accept()

    def showEvent(self, event):
        """Ensure dialog stays centered when shown"""
        try:
            super().showEvent(event)
            if not self.is_fullscreen and self.parent():
                parent_geometry = self.parent().geometry()
                dialog_geometry = self.geometry()
                x = parent_geometry.x() + (parent_geometry.width() - dialog_geometry.width()) // 2
                y = parent_geometry.y() + (parent_geometry.height() - dialog_geometry.height()) // 2
                self.move(x, y)
        except Exception as e:
            print(f"Error in showEvent: {str(e)}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def load_srt(self, file_path):
        """Load and parse an SRT file"""
        if self.srt_parser.parse_srt(file_path):
            self.start_display()
            return True
        return False

    def start_display(self):
        """Start the subtitle display timer"""
        self.update_timer.start()

    def stop_display(self):
        """Stop the subtitle display timer"""
        self.update_timer.stop()
        self.subtitle_label.clear()

    def update_subtitle(self):
        """Update the displayed subtitle based on current playback time"""
        if not self.parent() or not self.parent().is_playing:
            return

        current_time = pygame.mixer.music.get_pos() / 1000.0
        if self.parent().pause_position > 0:
            current_time = self.parent().pause_position

        subtitle = self.srt_parser.get_subtitle_at_time(current_time)
        if subtitle != self.current_subtitle:
            self.current_subtitle = subtitle
            # Format text with HTML for better wrapping and line breaks
            formatted_text = subtitle.replace('\n', '<br>')
            # Add extra line height and center alignment in HTML
            self.subtitle_label.setText(f"<div style='line-height: 1.4; text-align: center;'>{formatted_text}</div>")


class TreeViewDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Check if this item has children and is a branch
        model = index.model()
        if model.hasChildren(index):
            # Get the item rect
            rect = option.rect
            
            # Calculate arrow position (further to the left)
            arrow_x = rect.left() - 15  # Move arrow further left
            arrow_y = rect.center().y()
            
            # Set up painter for drawing
            painter.setPen(QColor(255, 255, 255))  # White color
            painter.setFont(QFont("Arial", 10))
            
            # Draw arrow based on expansion state
            tree_view = self.parent()
            if tree_view and tree_view.isExpanded(index):
                # Draw down arrow (▼) for expanded
                painter.drawText(arrow_x, arrow_y + 5, "▼")
            else:
                # Draw right arrow (▶) for collapsed
                painter.drawText(arrow_x, arrow_y + 5, "▶")
        
        # Call the parent paint method to draw the text
        super().paint(painter, option, index)


class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Debug: Print database info
        import os
        db_path = "languages.db"
        print(f"DEBUG: Looking for database at: {os.path.abspath(db_path)}")
        print(f"DEBUG: Database exists: {os.path.exists(db_path)}")
        print(f"DEBUG: Current working directory: {os.getcwd()}")
        
        # Laad eerst de config zodat de taal bekend is
        self.config_file = 'music_player_config.json'
        self.current_language = 'nl'  # fallback, wordt direct overschreven
        self.config = {}
        self.lyrics_dir = ''
        self.playlist_dir = ''
        self.favorites = set()
        self.play_history = []
        self.lyrics_mapping = {}
        self.max_history_items = 100
        self.is_muted = False
        self.previous_volume = 1.0
        self.metadata_cache = {}
        self.metadata_cache_size_limit = 1000
        self.drive_file_counts = {}
        self.pause_position = 0
        self.start_time = 0
        self.pause_time = 0
        self.total_play_time = 0
        self.last_update_time = 0
        self.show_full_path = True
        self.srt_display = None
        self.current_track = None
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.filtered_files = []
        self.saved_files = {}
        self.available_drives = []
        self.current_drive = None
        self.original_files = []
        self.track_length = 0
        self.current_lyrics = ""
        self.lyrics_dialog = None
        
        # Add language status tracking
        self.language_status_text = ""
        self.last_status_update = 0
        self.status_restore_timer = QTimer()
        self.status_restore_timer.timeout.connect(self.restore_language_status)
        self.status_restore_timer.setInterval(2000)  # Restore every 2 seconds
        
        # Laad config en zet self.current_language
        self.load_config()
        # Nu is de taal bekend, bouw de UI op met de juiste taal
        self.setWindowTitle(get_text('window_title', self.current_language))

        # Calculate window size based on screen resolution (80%)
        screen = QApplication.primaryScreen().geometry()
        window_width = int(screen.width() * 0.8)
        window_height = int(screen.height() * 0.8)
        window_x = (screen.width() - window_width) // 2
        window_y = (screen.height() - window_height) // 2

        # Set window size and position
        self.setGeometry(window_x, window_y, window_width, window_height)

        # Initialize new variables for history and favorites
        self.play_history = []  # List of recently played tracks
        self.favorites = set()  # Set of favorite tracks
        self.max_history_items = 100  # Maximum number of history items to keep
        self.is_muted = False
        self.previous_volume = 1.0  # Store volume before muting

        # Create status bar first
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.update_language_status()

        # Add file count label to status bar
        self.file_count_label = QLabel(get_text('files_label', self.current_language))
        self.statusBar.addPermanentWidget(self.file_count_label)

        # Initialize variables
        self.current_track = None
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.filtered_files = []
        self.saved_files = {}
        self.available_drives = []
        self.current_drive = None
        self.original_files = []
        self.track_length = 0
        self.current_lyrics = ""
        self.lyrics_dialog = None
        self.metadata_cache = {}
        self.metadata_cache_size_limit = 1000  # Maximum number of cached metadata entries
        self.drive_file_counts = {}
        self.pause_position = 0
        self.start_time = 0
        self.pause_time = 0
        self.total_play_time = 0
        self.last_update_time = 0
        self.show_full_path = True
        self.srt_display = None

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Create left panel for file browser
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(5)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Create title and help button layout
        title_layout = QHBoxLayout()
        title_label = QLabel(get_text('title_label', self.current_language))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        # Add language switch button
        self.language_button = QPushButton("🌐")
        self.language_button.setToolTip(get_text('language_tooltip', self.current_language))
        self.language_button.clicked.connect(self.switch_language)
        self.language_button.setStyleSheet("""
            QPushButton {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
                min-width: 40px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
            }
        """)
        title_layout.addWidget(self.language_button)
        
        help_button = QPushButton(get_text('help_button', self.current_language))
        help_button.clicked.connect(self.show_help)
        title_layout.addWidget(help_button)
        left_layout.addLayout(title_layout)
        
        # Store help button as instance variable
        self.help_button = help_button

        # Create drive selection and scan controls
        drive_layout = QHBoxLayout()
        drive_layout.setSpacing(5)
        self.drive_combo = QComboBox()
        self.drive_combo.setPlaceholderText(get_text('select_drive', self.current_language))
        self.drive_combo.setStyleSheet("color: #90EE90;")
        self.drive_combo.activated.connect(self.on_drive_selected)
        self.refresh_button = QPushButton(get_text('refresh_drives', self.current_language))
        self.refresh_button.clicked.connect(self.refresh_drives)
        self.read_button = QPushButton(get_text('read_files', self.current_language))
        self.read_button.clicked.connect(self.read_saved_files)
        self.read_button.setStyleSheet("color: #90EE90;")
        self.toggle_view_button = QPushButton(get_text('toggle_view', self.current_language))
        self.toggle_view_button.clicked.connect(self.toggle_path_display)
        self.scan_button = QPushButton(get_text('scan_drive', self.current_language))
        self.scan_button.clicked.connect(self.scan_selected_drive)
        
        # Add cleanup button
        self.cleanup_button = QPushButton(get_text('cleanup_files', self.current_language))
        self.cleanup_button.clicked.connect(self.manual_cleanup)
        self.cleanup_button.setToolTip(get_text('cleanup_files', self.current_language))
        
        drive_layout.addWidget(self.drive_combo)
        drive_layout.addWidget(self.refresh_button)
        drive_layout.addWidget(self.read_button)
        drive_layout.addWidget(self.toggle_view_button)
        drive_layout.addWidget(self.scan_button)
        drive_layout.addWidget(self.cleanup_button)
        left_layout.addLayout(drive_layout)

        # Add lyrics directory selection
        lyrics_dir_layout = QHBoxLayout()
        lyrics_dir_layout.setSpacing(5)
        self.lyrics_dir_label = QLabel(get_text('lyrics_dir_label', self.current_language))
        self.lyrics_dir_path = QLineEdit()
        self.lyrics_dir_path.setReadOnly(True)
        self.lyrics_dir_button = QPushButton(get_text('change_lyrics_dir', self.current_language))
        self.lyrics_dir_button.clicked.connect(self.change_lyrics_dir)
        lyrics_dir_layout.addWidget(self.lyrics_dir_label)
        lyrics_dir_layout.addWidget(self.lyrics_dir_path)
        lyrics_dir_layout.addWidget(self.lyrics_dir_button)
        left_layout.addLayout(lyrics_dir_layout)

        # Create tree view for drives and files
        self.tree_view = QTreeView()
        self.tree_view.setRootIsDecorated(True)  # Ensure expand/collapse arrows are visible
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels([""])  # Add empty header
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setHeaderHidden(True)  # Hide the header
        self.tree_view.doubleClicked.connect(self.play_selected_track)
        self.tree_view.clicked.connect(self.play_on_click)
        self.tree_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tree_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tree_view.setFrameShape(QFrame.Shape.NoFrame)
        self.tree_view.setFrameShadow(QFrame.Shadow.Plain)
        self.tree_view.setLineWidth(0)
        self.tree_view.setMidLineWidth(0)
        self.tree_view.setContentsMargins(0, 0, 0, 0)

        # Set custom delegate for visible arrows
        delegate = TreeViewDelegate(self.tree_view)
        self.tree_view.setItemDelegate(delegate)

        # Enable context menu
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

        left_layout.addWidget(self.tree_view)

        # Create playlist controls
        playlist_layout = QHBoxLayout()
        playlist_layout.setSpacing(0)
        playlist_layout.setContentsMargins(0, 0, 0, 0)
        self.playlist_combo = QComboBox()
        self.playlist_combo.setPlaceholderText("Select Playlist")
        self.playlist_combo.activated.connect(self.on_playlist_selected)
        load_playlist_button = QPushButton("Load Playlist")
        load_playlist_button.clicked.connect(self.load_playlist)
        playlist_layout.addWidget(self.playlist_combo)
        playlist_layout.addWidget(load_playlist_button)
        left_layout.addLayout(playlist_layout)

        # Create filter section
        filter_group = QGroupBox("Filter Options")
        filter_layout = QFormLayout()
        filter_layout.setSpacing(0)
        filter_layout.setContentsMargins(5, 5, 5, 5)

        self.positive_filter = QLineEdit()
        self.positive_filter.setPlaceholderText("Enter text that must be in filename")
        filter_layout.addRow("Wel:", self.positive_filter)

        self.negative_filter = QLineEdit()
        self.negative_filter.setPlaceholderText("Enter text that must NOT be in filename")
        filter_layout.addRow("Niet:", self.negative_filter)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        filter_button = QPushButton("Filter")
        filter_button.clicked.connect(self.apply_filter)
        reset_filter_button = QPushButton("Reset Filter")
        reset_filter_button.clicked.connect(self.reset_filter)
        save_list_button = QPushButton("Save Filtered List")
        save_list_button.clicked.connect(self.save_filtered_list)
        button_layout.addWidget(filter_button)
        button_layout.addWidget(reset_filter_button)
        button_layout.addWidget(save_list_button)
        filter_layout.addRow(button_layout)

        filter_group.setLayout(filter_layout)
        left_layout.addWidget(filter_group)

        # Create playback controls
        control_layout = QHBoxLayout()
        control_layout.setSpacing(5)
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_pause)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_playback)
        self.prev_button = QPushButton("Vorige")
        self.prev_button.clicked.connect(self.play_previous_track)
        self.next_button = QPushButton("Volgende")
        self.next_button.clicked.connect(self.play_next_track)
        self.favorite_button = QPushButton("Favoriet")
        self.favorite_button.setCheckable(True)  # Make button checkable
        self.favorite_button.clicked.connect(self.toggle_favorite)
        self.favorite_button.setStyleSheet("""
            QPushButton {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:checked {
                background-color: #ffd700;
                color: #000000;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
            }
            QPushButton:checked:hover {
                background-color: #ffed4a;
            }
            QPushButton:pressed {
                background-color: #2b2b2b;
            }
        """)

        self.append_checkbox = QCheckBox("Lijsten aanvullen in plaats van vervangen")
        self.append_checkbox.setChecked(False)

        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.next_button)
        control_layout.addWidget(self.favorite_button)
        control_layout.addWidget(self.append_checkbox)
        left_layout.addLayout(control_layout)

        # Create playback time indicator
        time_layout = QHBoxLayout()
        time_layout.setSpacing(5)

        self.current_time_label = QLabel("00:00")
        self.current_time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        time_layout.addWidget(self.current_time_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        time_layout.addWidget(self.progress_bar)

        self.total_time_label = QLabel("00:00")
        self.total_time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        time_layout.addWidget(self.total_time_label)

        left_layout.addLayout(time_layout)

        # Create right panel for lyrics
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.lyrics_title = QLabel(get_text('lyrics_title', self.current_language))
        self.lyrics_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lyrics_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        right_layout.addWidget(self.lyrics_title)

        self.lyrics_display = QTextEdit()
        self.lyrics_display.setReadOnly(True)
        self.lyrics_display.setStyleSheet("font-size: 14px;")
        right_layout.addWidget(self.lyrics_display)

        button_layout = QHBoxLayout()

        self.edit_button = QPushButton(get_text('edit_lyrics_button', self.current_language))
        self.edit_button.clicked.connect(self.edit_lyrics)
        button_layout.addWidget(self.edit_button)

        self.srt_button = QPushButton(get_text('show_karaoke_button', self.current_language))
        self.srt_button.clicked.connect(self.toggle_srt_display)
        button_layout.addWidget(self.srt_button)

        right_layout.addLayout(button_layout)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])

        # Create timer for updating playback position
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        self.position_timer.setInterval(200)  # Increased from 100ms to 200ms

        # Initialize pygame
        pygame.init()
        pygame.mixer.init()

        # Add track end event
        self.track_end_event = pygame.USEREVENT
        pygame.mixer.music.set_endevent(self.track_end_event)

        # Load configuration
        self.config_file = 'music_player_config.json'
        self.load_config()

        # Create directories if they don't exist
        for directory in [self.playlist_dir, self.lyrics_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Clean up saved files to remove references to non-existent drives
        # Commented out to prevent startup delays - can be run manually if needed
        # self.cleanup_saved_files()

        # Update lyrics directory path display
        self.lyrics_dir_path.setText(self.lyrics_dir)

        # Load saved files if they exist
        try:
            if os.path.exists('saved_files.json'):
                with open('saved_files.json', 'r') as f:
                    loaded_saved_files = json.load(f)
                
                # Load saved files without validation to prevent startup delays
                # Validation can be done manually using the Cleanup Files button
                self.saved_files = loaded_saved_files
                self.statusBar.showMessage(f"Loaded {len(self.saved_files)} saved drives (not validated)")
        except Exception as e:
            self.statusBar.showMessage(f"Error loading saved files: {str(e)}")
            self.saved_files = {}

        # Initial drive scan
        self.refresh_drives()

        # Load playlists
        self.refresh_playlists()

        # Update file count status
        self.update_file_count_status()

        # Set dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
            }
            QPushButton:pressed {
                background-color: #2b2b2b;
            }
            QLineEdit {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QTreeView {
                background-color: #2b2b2b;
                color: #ffffff;
                border: none;
                padding: 0px;
                margin: 0px;
            }
            QTreeView::item {
                padding: 5px;
                border: none;
                background-color: #2b2b2b;
                margin: 0px;
                spacing: 0px;
                height: 25px;
            }
            QTreeView::item:selected {
                background-color: #4b4b4b;
                height: 25px;
            }
            QTreeView::branch {
                background-color: #2b2b2b;
                margin: 0px;
                padding: 0px;
                color: white;
            }
            QTreeView::branch:has-siblings:!adjoins-item {
                background-color: #2b2b2b;
                margin: 0px;
                padding: 0px;
                color: white;
            }
            QTreeView::branch:has-siblings:adjoins-item {
                background-color: #2b2b2b;
                margin: 0px;
                padding: 0px;
                color: white;
            }
            QTreeView::branch:!has-children:!has-siblings:adjoins-item {
                background-color: #2b2b2b;
                margin: 0px;
                padding: 0px;
                color: white;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                background-color: #2b2b2b;
                margin: 0px;
                padding: 0px;
                color: white;
                image: none;
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                background-color: #2b2b2b;
                margin: 0px;
                padding: 0px;
                color: white;
                image: none;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2b2b2b;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #4b4b4b;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: #2b2b2b;
            }
            QScrollBar:horizontal {
                border: none;
                background-color: #2b2b2b;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #4b4b4b;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background-color: #2b2b2b;
            }
            QAbstractItemView {
                background-color: #2b2b2b;
                alternate-background-color: #2b2b2b;
                padding: 0px;
                margin: 0px;
            }
            QAbstractScrollArea {
                background-color: #2b2b2b;
                padding: 0px;
                margin: 0px;
            }
            QAbstractItemView::item {
                background-color: #2b2b2b;
                padding: 0px;
                margin: 0px;
                min-height: 25px;
            }
            QAbstractItemView::item:selected {
                background-color: #4b4b4b;
                min-height: 25px;
            }
            QStatusBar {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QStatusBar::item {
                border: none;
            }
        """)

        # Enable drag and drop for tree view
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(True)
        self.tree_view.setDropIndicatorShown(True)
        self.tree_view.setDragDropMode(QTreeView.DragDropMode.InternalMove)
        self.tree_view.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)

        # Add tooltips to buttons
        self.play_button.setToolTip("Afspelen/Pauzeren (Spatiebalk)")
        self.stop_button.setToolTip("Stoppen (S)")
        self.prev_button.setToolTip("Vorige nummer (Pijltje Links)")
        self.next_button.setToolTip("Volgende nummer (Pijltje Rechts)")
        self.favorite_button.setToolTip(get_text('favorite_tooltip', self.current_language))
        self.toggle_view_button.setToolTip("Wisselen tussen bestandsnaam en pad weergave (V)")
        self.scan_button.setToolTip("Scan geselecteerde schijf voor muziekbestanden")
        self.read_button.setToolTip("Laad opgeslagen bestanden van geselecteerde schijf")
        self.refresh_button.setToolTip("Ververs lijst met beschikbare schijven")

        # Add status bar widgets for more information
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 2px;
            }
            QStatusBar QLabel {
                padding: 2px 5px;
                border-right: 1px solid #555555;
            }
        """)

        # Add status labels
        self.current_track_label = QLabel("")
        self.next_track_label = QLabel("")
        self.playlist_info_label = QLabel("")

        # Add permanent widgets to status bar
        self.statusBar.addPermanentWidget(self.playlist_info_label)
        self.statusBar.addPermanentWidget(self.next_track_label)
        self.statusBar.addPermanentWidget(self.current_track_label)
        self.statusBar.addPermanentWidget(self.file_count_label)

        # Voeg deze toe aan het einde van __init__:
        self.update_favorites_display()
        self.update_history_display()
        
        # Start the status restore timer
        self.status_restore_timer.start()

    def load_config(self):
        """Load configuration from file"""
        default_config = {
            'lyrics_dir': os.path.join(os.path.dirname(os.path.abspath(__file__)), "lyrics"),
            'playlist_dir': os.path.join(os.path.dirname(os.path.abspath(__file__)), "playlists"),
            'lyrics_mapping': {},
            'favorites': [],  # Add favorites to config
            'play_history': [],  # Add play history to config
            'language': 'nl'  # Add language preference
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    self.lyrics_dir = self.config.get('lyrics_dir', default_config['lyrics_dir'])
                    self.playlist_dir = self.config.get('playlist_dir', default_config['playlist_dir'])
                    self.favorites = set(self.config.get('favorites', []))  # Load favorites
                    self.play_history = self.config.get('play_history', [])  # Load history
                    
                    # Load language preference
                    saved_language = self.config.get('language', 'nl')
                    if saved_language in get_available_languages():
                        self.current_language = saved_language
                    else:
                        self.current_language = 'nl'  # Fallback to Dutch

                # (Verplaatst) self.update_favorites_display()
                # (Verplaatst) self.update_history_display()

            # Load and validate lyrics mappings
            self.lyrics_mapping = {}
            saved_mappings = self.config.get('lyrics_mapping', {})

            for music_file, mapping in saved_mappings.items():
                # Convert old format to new format
                if isinstance(mapping, str):
                    # Old format: just a path string
                    ext = os.path.splitext(mapping)[1].lower()
                    if ext == '.srt':
                        self.lyrics_mapping[music_file] = {
                            'text_path': None,
                            'srt_path': mapping
                        }
                    else:
                        self.lyrics_mapping[music_file] = {
                            'text_path': mapping,
                            'srt_path': None
                        }
                elif isinstance(mapping, dict):
                    # New format: check if it has the new structure
                    if 'text_path' in mapping or 'srt_path' in mapping:
                        self.lyrics_mapping[music_file] = {
                            'text_path': mapping.get('text_path'),
                            'srt_path': mapping.get('srt_path')
                        }
                    else:
                        # Old format with type: convert to new format
                        path = mapping.get('path')
                        file_type = mapping.get('type')
                        if path:
                            if file_type == 'SRT':
                                self.lyrics_mapping[music_file] = {
                                    'text_path': None,
                                    'srt_path': path
                                }
                            else:
                                self.lyrics_mapping[music_file] = {
                                    'text_path': path,
                                    'srt_path': None
                                }

                # Validate that files exist
                if music_file in self.lyrics_mapping:
                    mapping = self.lyrics_mapping[music_file]
                    if mapping['text_path'] and not os.path.exists(mapping['text_path']):
                        mapping['text_path'] = None
                    if mapping['srt_path'] and not os.path.exists(mapping['srt_path']):
                        mapping['srt_path'] = None
                    # Remove mapping if both paths are None
                    if not mapping['text_path'] and not mapping['srt_path']:
                        del self.lyrics_mapping[music_file]
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            self.config = default_config
            self.lyrics_dir = default_config['lyrics_dir']
            self.playlist_dir = default_config['playlist_dir']
            self.lyrics_mapping = {}
            self.current_language = 'nl'  # Fallback to Dutch
            if hasattr(self, 'statusBar'):
                self.statusBar.showMessage(get_text('error_loading_config', self.current_language, error=str(e)))

        # Save the validated mappings
        self.save_config()

    def format_time(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_position(self):
        """Update the playback position display"""
        if not self.is_playing:  # Only check is_playing, remove track_length check
            return

        try:
            # Process pygame events
            pygame.event.pump()

            # Get current position in seconds
            current_pos = pygame.mixer.music.get_pos() / 1000.0

            # If we're paused, use the stored position
            if current_pos == 0 and self.pause_position > 0:
                current_pos = self.pause_position

            # Calculate progress based on time since start
            if self.track_length > 0:  # Prevent division by zero
                elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000.0
                progress = int((elapsed_time / self.track_length) * 1000)

                # Check if track has ended (progress >= 100% or current_pos == 0)
                if (progress >= 1000 or (
                        current_pos == 0 and self.pause_position == 0)) and not pygame.mixer.music.get_busy():
                    # Reset progress bar
                    self.progress_bar.setValue(0)
                    self.current_time_label.setText("00:00")

                    # Play next track
                    self.play_next_track()
                    return

                # Update progress bar
                self.progress_bar.setValue(min(progress, 1000))  # Ensure we don't exceed 1000

                # Update time labels
                self.current_time_label.setText(self.format_time(current_pos))
                remaining = max(0, self.track_length - current_pos)
                self.total_time_label.setText(f"-{self.format_time(remaining)}")

        except Exception as e:
            print(f"Error updating position: {str(e)}")

    def play_previous_track(self):
        """Play the previous track in the playlist"""
        if not self.filtered_files:
            return

        # Find current track index
        current_index = self.filtered_files.index(
            self.current_track) if self.current_track in self.filtered_files else -1

        # Get previous track index
        prev_index = current_index - 1
        if prev_index < 0:
            prev_index = len(self.filtered_files) - 1  # Loop to end

        # Play previous track
        prev_track = self.filtered_files[prev_index]
        self.play_selected_track_by_path(prev_track)

    def play_next_track(self):
        """Play the next track in the playlist"""
        if not self.filtered_files:
            return

        # Find current track index
        current_index = self.filtered_files.index(
            self.current_track) if self.current_track in self.filtered_files else -1

        # Get next track index
        next_index = current_index + 1
        if next_index >= len(self.filtered_files):
            next_index = 0  # Loop back to start

        # Stop current SRT display if it exists
        if self.srt_display and self.srt_display.isVisible():
            self.srt_display.stop_display()
            self.srt_display.close()
            self.srt_display = None

        # Play next track
        next_track = self.filtered_files[next_index]
        self.play_selected_track_by_path(next_track)

        # Update status bar
        self.statusBar.showMessage(f"Playing next track: {os.path.basename(next_track)}")

    def play_selected_track_by_path(self, file_path):
        """Play a track by its file path"""
        if not file_path:
            return

        try:
            # Update favorite button state
            self.favorite_button.setChecked(file_path in self.favorites)

            # Add to history
            self.add_to_history(file_path)

            # Stop any current playback and timer
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            self.position_timer.stop()

            # Reset all playback state
            self.current_track = file_path
            self.is_playing = False
            self.pause_position = 0
            self.progress_bar.setValue(0)
            self.current_time_label.setText("00:00")

            # Initialize pygame mixer if needed
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            # Load the track and get its length
            sound = pygame.mixer.Sound(file_path)
            self.track_length = sound.get_length()

            # Update total time label
            self.total_time_label.setText(self.format_time(self.track_length))

            # Load lyrics before starting playback
            self.load_lyrics(file_path)

            # Start playback
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            # Record start time and update UI
            self.start_time = pygame.time.get_ticks()
            self.play_button.setText("Pause")
            self.is_playing = True
            self.statusBar.showMessage(f"Playing: {os.path.basename(file_path)}")

            # Update favorites display if this is a favorite
            if file_path in self.favorites:
                self.statusBar.showMessage(f"Playing favorite: {os.path.basename(file_path)}")

            # Ensure timer is properly initialized and started
            if not self.position_timer.isActive():
                self.position_timer = QTimer()
                self.position_timer.timeout.connect(self.update_position)
                self.position_timer.setInterval(200)  # Increased from 100ms to 200ms

            # Start timer with a small delay to ensure pygame is ready
            QTimer.singleShot(50, self._start_timer)

            # Update current track label
            if hasattr(self, 'current_track_label'):
                metadata = self.get_metadata(file_path)
                self.current_track_label.setText(f"Nu: {metadata['artist']} - {metadata['title']}")

            # Update playlist info
            self.update_playlist_info()

        except Exception as e:
            self.statusBar.showMessage(f"Error playing track: {str(e)}")
            try:
                pygame.mixer.quit()
                pygame.mixer.init()
            except:
                pass

    def _start_timer(self):
        """Start the position timer with a small delay"""
        try:
            if self.is_playing:  # Only start if we're still playing
                self.position_timer.start()
                # Force an immediate position update
                self.update_position()
        except Exception as e:
            self.statusBar.showMessage(f"Error starting timer: {str(e)}")

    def refresh_playlists(self):
        """Load all playlists from the playlist directory"""
        self.playlist_combo.clear()
        try:
            playlists = [f for f in os.listdir(self.playlist_dir) if f.endswith('.json')]
            if playlists:
                self.playlist_combo.addItems(playlists)
                self.statusBar.showMessage(f"Loaded {len(playlists)} playlists")
            else:
                self.statusBar.showMessage("No playlists found")
        except Exception as e:
            self.statusBar.showMessage(f"Error loading playlists: {str(e)}")

    def on_playlist_selected(self, index):
        """Handle playlist selection"""
        selected_playlist = self.playlist_combo.currentText()
        if selected_playlist:
            # Load the playlist immediately when selected
            self.load_playlist()

    def load_playlist(self):
        """Load the selected playlist"""
        selected_playlist = self.playlist_combo.currentText()
        if not selected_playlist:
            QMessageBox.warning(self, "Warning", "Please select a playlist first")
            return

        try:
            # Get the playlist path
            playlist_path = os.path.join(self.playlist_dir, selected_playlist)
            if not os.path.exists(playlist_path):
                self.statusBar.showMessage(f"Playlist file not found: {selected_playlist}")
                return

            # Load the playlist files
            with open(playlist_path, 'r') as f:
                files = json.load(f)

            # Create a new model to rebuild the tree
            new_model = QStandardItemModel()
            new_model.setHorizontalHeaderLabels([""])

            # Add favorites and history items first
            favorites_item = QStandardItem(get_text('favorites', self.current_language))
            favorites_item.setEditable(False)
            favorites_item.setData(get_text('favorites', self.current_language), Qt.ItemDataRole.UserRole)
            new_model.appendRow(favorites_item)

            history_item = QStandardItem(get_text('play_history', self.current_language))
            history_item.setEditable(False)
            history_item.setData(get_text('play_history', self.current_language), Qt.ItemDataRole.UserRole)
            new_model.appendRow(history_item)

            # Add favorite items
            for track in sorted(self.favorites):
                if os.path.exists(track):
                    metadata = self.get_metadata(track)
                    display_text = f"{metadata['artist']} - {metadata['title']}"
                    if self.show_full_path:
                        display_text += f" ({track})"
                    file_item = QStandardItem(display_text)
                    file_item.setData(track, Qt.ItemDataRole.UserRole)
                    file_item.setEditable(False)
                    favorites_item.appendRow(file_item)

            # Add history items
            for track in self.play_history:
                if os.path.exists(track):
                    metadata = self.get_metadata(track)
                    display_text = f"{metadata['artist']} - {metadata['title']}"
                    if self.show_full_path:
                        display_text += f" ({track})"
                    file_item = QStandardItem(display_text)
                    file_item.setData(track, Qt.ItemDataRole.UserRole)
                    file_item.setEditable(False)
                    history_item.appendRow(file_item)

            # Add playlist item
            playlist_item = QStandardItem(selected_playlist)
            new_model.appendRow(playlist_item)

            # Add files to playlist
            for file in files:
                if os.path.exists(file):  # Only add files that still exist
                    file_item = QStandardItem(file if self.show_full_path else os.path.basename(file))
                    file_item.setData(file, Qt.ItemDataRole.UserRole)
                    playlist_item.appendRow(file_item)

            # Replace the old model with the new one
            self.tree_view.setModel(new_model)
            self.tree_model = new_model

            # Expand only drive/playlist sections, not favorites and history
            for i in range(self.tree_model.rowCount()):
                item = self.tree_model.item(i)
                if item and item.text() not in [get_text('favorites', self.current_language), get_text('play_history', self.current_language)]:
                    index = self.tree_model.indexFromItem(item)
                    self.tree_view.expand(index)

            # Update filtered files
            self.filtered_files = files
            self.statusBar.showMessage(f"Loaded {len(files)} tracks from {selected_playlist}")

            # Update file count
            self.update_file_count()

        except Exception as e:
            self.statusBar.showMessage(f"Error loading playlist: {str(e)}")
            print(f"Error in load_playlist: {str(e)}")

    def refresh_drives(self):
        """Quick scan for available drives"""
        # Get currently available drives with simple error handling
        self.available_drives = []
        
        for drive in range(65, 91):  # A-Z
            drive_letter = f"{chr(drive)}:"
            try:
                if os.path.exists(drive_letter):
                    self.available_drives.append(drive_letter)
            except Exception as e:
                print(f"Error checking drive {drive_letter}: {str(e)}")
                continue

        # Update combo box with both saved and available drives
        self.drive_combo.clear()

        # Add saved drives first
        saved_drives = list(self.saved_files.keys())
        if saved_drives:
            self.drive_combo.addItem("--- Saved Drives ---")
            for drive in saved_drives:
                status = "✓" if drive in self.available_drives else "✗"
                self.drive_combo.addItem(f"{drive} {status}")

        # Add available drives that aren't saved
        new_drives = [d for d in self.available_drives if d not in self.saved_files]
        if new_drives:
            self.drive_combo.addItem("--- Available Drives ---")
            for drive in new_drives:
                self.drive_combo.addItem(f"{drive} (New)")

        self.statusBar.showMessage(f"Found {len(self.available_drives)} available drives")

    def on_drive_selected(self, index):
        """Handle drive selection"""
        selected_text = self.drive_combo.currentText()
        if selected_text and not selected_text.startswith("---"):
            # Extract drive letter from the display text
            drive = selected_text.split()[0]
            self.current_drive = drive

            # Check if drive has saved files
            if drive in self.saved_files:
                # Count file types
                file_types = {}
                for file in self.saved_files[drive]:
                    ext = os.path.splitext(file)[1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1

                # Create type info string
                type_info = []
                for ext, count in file_types.items():
                    type_info.append(f"{ext}: {count}")

                # Update status bar
                self.statusBar.showMessage(
                    f"Drive {drive} heeft {len(self.saved_files[drive])} bestanden - {', '.join(type_info)}")
            else:
                self.statusBar.showMessage(f"Drive {drive} heeft geen opgeslagen bestanden")

    def read_saved_files(self):
        selected_text = self.drive_combo.currentText()
        if not selected_text or selected_text.startswith("---"):
            QMessageBox.warning(self, "Warning", "Please select a drive first")
            return

        # Extract drive letter from the display text
        selected_drive = selected_text.split()[0]
        self.current_drive = selected_drive

        try:
            # Create a new model to rebuild the tree
            new_model = QStandardItemModel()
            new_model.setHorizontalHeaderLabels([""])

            # Add favorites and history items first
            favorites_item = QStandardItem(get_text('favorites', self.current_language))
            favorites_item.setEditable(False)
            favorites_item.setData(get_text('favorites', self.current_language), Qt.ItemDataRole.UserRole)
            new_model.appendRow(favorites_item)

            history_item = QStandardItem(get_text('play_history', self.current_language))
            history_item.setEditable(False)
            history_item.setData(get_text('play_history', self.current_language), Qt.ItemDataRole.UserRole)
            new_model.appendRow(history_item)

            # Add favorite items
            for track in sorted(self.favorites):
                if os.path.exists(track):
                    metadata = self.get_metadata(track)
                    display_text = f"{metadata['artist']} - {metadata['title']}"
                    if self.show_full_path:
                        display_text += f" ({track})"
                    file_item = QStandardItem(display_text)
                    file_item.setData(track, Qt.ItemDataRole.UserRole)
                    file_item.setEditable(False)
                    favorites_item.appendRow(file_item)

            # Add history items
            for track in self.play_history:
                if os.path.exists(track):
                    metadata = self.get_metadata(track)
                    display_text = f"{metadata['artist']} - {metadata['title']}"
                    if self.show_full_path:
                        display_text += f" ({track})"
                    file_item = QStandardItem(display_text)
                    file_item.setData(track, Qt.ItemDataRole.UserRole)
                    file_item.setEditable(False)
                    history_item.appendRow(file_item)

            # Create drive item
            drive_item = QStandardItem(selected_drive)
            new_model.appendRow(drive_item)

            if selected_drive in self.saved_files:
                # Store original files if this is the first time loading this drive
                if not self.append_checkbox.isChecked():
                    self.original_files = self.saved_files[selected_drive].copy()
                    self.filtered_files = self.original_files.copy()
                else:
                    # Add new files to original_files and filtered_files
                    new_files = [f for f in self.saved_files[selected_drive] if f not in self.original_files]
                    self.original_files.extend(new_files)
                    self.filtered_files.extend(new_files)

                # Add files to the tree view in batches
                existing_files = set()
                for j in range(drive_item.rowCount()):
                    child = drive_item.child(j)
                    if child:
                        existing_files.add(child.data(Qt.ItemDataRole.UserRole))

                files_to_add = [f for f in self.saved_files[selected_drive] if f not in existing_files]

                # Process in batches of 100
                batch_size = 100
                total_files = len(files_to_add)

                for i in range(0, total_files, batch_size):
                    batch = files_to_add[i:i + batch_size]
                    for file in batch:
                        try:
                            file_item = QStandardItem(file if self.show_full_path else os.path.basename(file))
                            file_item.setData(file, Qt.ItemDataRole.UserRole)
                            drive_item.appendRow(file_item)
                        except Exception as e:
                            print(f"Error adding file {file}: {str(e)}")
                            continue

                    # Update status bar with progress
                    progress = min(i + batch_size, total_files)
                    self.statusBar.showMessage(f"Loading files... {progress}/{total_files}")
                    QApplication.processEvents()

                # Update drive item text with file count
                drive_item.setText(f"{selected_drive} ({drive_item.rowCount()} bestanden)")

                self.statusBar.showMessage(
                    f"Loaded {len(self.saved_files[selected_drive])} files from {selected_drive}")

                # Replace the old model with the new one
                self.tree_view.setModel(new_model)
                self.tree_model = new_model

                # Expand only drive/playlist sections, not favorites and history
                for i in range(self.tree_model.rowCount()):
                    item = self.tree_model.item(i)
                    if item and item.text() not in [get_text('favorites', self.current_language), get_text('play_history', self.current_language)]:
                        index = self.tree_model.indexFromItem(item)
                        self.tree_view.expand(index)

                # After loading files, reload lyrics mappings
                self.load_lyrics_mappings()

                # Update file count
                self.update_file_count()
            else:
                self.statusBar.showMessage(f"No saved files found for {selected_drive}")

        except Exception as e:
            self.statusBar.showMessage(f"Error loading files: {str(e)}")
            print(f"Error in read_saved_files: {str(e)}")
            # Try to recover by clearing the tree
            self.tree_model.clear()
            self.filtered_files = []
            self.original_files = []
            self.update_file_count()

    def scan_selected_drive(self):
        """Scan only the selected drive for audio files"""
        selected_text = self.drive_combo.currentText()
        if not selected_text or selected_text.startswith("---"):
            QMessageBox.warning(self, "Warning", "Please select a drive first")
            return

        # Extract drive letter from the display text
        drive = selected_text.split()[0]

        # Show scanning popup
        scanning_dialog = ScanningDialog(self, drive, self.current_language)
        scanning_dialog.show()
        QApplication.processEvents()

        try:
            # Clear existing items if not appending
            if not self.append_checkbox.isChecked():
                self._clear_drive_items(drive)

            # Create progress dialog
            progress = QProgressDialog(f"Scanning drive {drive}...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setWindowTitle("Scanning Progress")
            progress.setAutoClose(True)

            # Create drive item
            drive_item = QStandardItem(drive)
            self.tree_model.appendRow(drive_item)

            # Scan for audio files
            audio_files = self._scan_drive_for_audio_files(drive, progress)

            if not progress.wasCanceled():
                self._process_scan_results(drive, drive_item, audio_files)

        except Exception as e:
            self.show_error("Scanning Error", f"Error scanning drive {drive}", str(e))
        finally:
            # Always close the scanning dialog
            scanning_dialog.close()
            scanning_dialog.deleteLater()
            QApplication.processEvents()

    def _clear_drive_items(self, drive):
        """Clear existing items for a drive while preserving favorites and history"""
        # Store favorites and history items
        favorites_item = None
        history_item = None
        for i in range(self.tree_model.rowCount()):
            item = self.tree_model.item(i)
            if item.text() == get_text('favorites', self.current_language):
                favorites_item = item
            elif item.text() == get_text('play_history', self.current_language):
                history_item = item

        # Remove existing drive item if it exists
        for i in range(self.tree_model.rowCount()):
            item = self.tree_model.item(i)
            if item and item.text().startswith(drive):
                self.tree_model.removeRow(i)
                break

        # Restore favorites and history items if they existed
        if favorites_item and not any(
                self.tree_model.item(i).text() == get_text('favorites', self.current_language) for i in range(self.tree_model.rowCount())):
            self.tree_model.insertRow(0, favorites_item)
        if history_item and not any(
                self.tree_model.item(i).text() == get_text('play_history', self.current_language) for i in range(self.tree_model.rowCount())):
            self.tree_model.insertRow(1 if favorites_item else 0, history_item)

        self.drive_file_counts.pop(drive, None)
        self.filtered_files = [f for f in self.filtered_files if not f.startswith(drive)]
        QApplication.processEvents()

    def _scan_drive_for_audio_files(self, drive, progress):
        """Scan drive for audio files with progress updates"""
        audio_files = []
        total_files = 0
        scanned_files = 0

        try:
            # First count total files for progress bar
            for root, _, files in os.walk(drive):
                for file in files:
                    if file.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac')):
                        total_files += 1
                        if total_files % 100 == 0:  # Update UI periodically
                            QApplication.processEvents()

            # Now scan and add files
            for root, _, files in os.walk(drive):
                if progress.wasCanceled():
                    break

                for file in files:
                    if file.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac')):
                        file_path = os.path.join(root, file)
                        audio_files.append(file_path)
                        scanned_files += 1

                        # Update progress
                        progress_value = int((scanned_files / total_files) * 100)
                        progress.setValue(progress_value)
                        progress.setLabelText(f"Scanning drive {drive}... ({scanned_files}/{total_files} files)")

                        # Update UI periodically
                        if scanned_files % 50 == 0:
                            QApplication.processEvents()

        except Exception as e:
            print(f"Error scanning drive {drive}: {str(e)}")
            # Return whatever files we found before the error
            return audio_files

        return audio_files

    def _process_scan_results(self, drive, drive_item, audio_files):
        """Process and display scan results"""
        # Update file counts
        file_types = {}
        for file in audio_files:
            ext = os.path.splitext(file)[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1

        # Update drive_file_counts
        self.drive_file_counts[drive] = {
            'total': len(audio_files),
            'types': file_types
        }

        # Update drive item text
        type_info = []
        for ext, count in file_types.items():
            type_info.append(f"{ext}: {count}")
        drive_item.setText(f"{drive} ({len(audio_files)} bestanden) - {', '.join(type_info)}")

        # Add files to tree view in batches
        batch_size = 100
        total_files = len(audio_files)

        for i in range(0, total_files, batch_size):
            batch = audio_files[i:i + batch_size]
            for file in batch:
                try:
                    file_item = QStandardItem(file if self.show_full_path else os.path.basename(file))
                    file_item.setData(file, Qt.ItemDataRole.UserRole)
                    drive_item.appendRow(file_item)
                    self.filtered_files.append(file)
                except Exception as e:
                    print(f"Error adding file {file}: {str(e)}")
                    continue

            # Update status bar with progress
            progress = min(i + batch_size, total_files)
            self.statusBar.showMessage(f"Loading files... {progress}/{total_files}")
            QApplication.processEvents()

        # Save the scanned files
        self.saved_files[drive] = audio_files
        self.save_files()

        # Update status
        self.statusBar.showMessage(get_text('scanning_complete', self.current_language, count=len(audio_files), drive=drive))

        # Automatically expand the drive item
        index = self.tree_model.indexFromItem(drive_item)
        self.tree_view.expand(index)

        # Update file count
        self.update_file_count_status()

    def update_file_count(self):
        """Update the file count in the status bar"""
        count = len(self.filtered_files)
        self.file_count_label.setText(get_text('files_label', self.current_language).replace('0', str(count)))

    def apply_filter(self):
        if not self.current_drive:
            QMessageBox.warning(self, "Warning", "Please select a drive first")
            return

        # Get filter terms
        positive_term = self.positive_filter.text().strip().lower()
        negative_term = self.negative_filter.text().strip().lower()

        if not positive_term and not negative_term:
            QMessageBox.warning(self, "Warning", "Please enter at least one filter term")
            return

        try:
            # Create a new model
            new_model = QStandardItemModel()
            new_model.setHorizontalHeaderLabels([""])

            # Create new favorites and history items
            favorites_item = QStandardItem(get_text('favorites', self.current_language))
            favorites_item.setEditable(False)
            favorites_item.setData(get_text('favorites', self.current_language), Qt.ItemDataRole.UserRole)
            new_model.appendRow(favorites_item)

            history_item = QStandardItem(get_text('play_history', self.current_language))
            history_item.setEditable(False)
            history_item.setData(get_text('play_history', self.current_language), Qt.ItemDataRole.UserRole)
            new_model.appendRow(history_item)

            # Add favorite items
            for track in sorted(self.favorites):
                if os.path.exists(track):
                    metadata = self.get_metadata(track)
                    display_text = f"{metadata['artist']} - {metadata['title']}"
                    if self.show_full_path:
                        display_text += f" ({track})"
                    file_item = QStandardItem(display_text)
                    file_item.setData(track, Qt.ItemDataRole.UserRole)
                    file_item.setEditable(False)
                    favorites_item.appendRow(file_item)

            # Add history items
            for track in self.play_history:
                if os.path.exists(track):
                    metadata = self.get_metadata(track)
                    display_text = f"{metadata['artist']} - {metadata['title']}"
                    if self.show_full_path:
                        display_text += f" ({track})"
                    file_item = QStandardItem(display_text)
                    file_item.setData(track, Qt.ItemDataRole.UserRole)
                    file_item.setEditable(False)
                    history_item.appendRow(file_item)

            # Apply filter logic
            drive_item = QStandardItem(self.current_drive)

            # If this is the first filter, start with original files
            if not self.filtered_files and self.original_files:
                self.filtered_files = self.original_files.copy()

            # Apply new filter to current filtered files
            new_filtered_files = []
            for file in self.filtered_files:
                file_lower = file.lower()
                # Check both positive and negative conditions
                if (not positive_term or positive_term in file_lower) and \
                        (not negative_term or negative_term not in file_lower):
                    file_item = QStandardItem(file if self.show_full_path else os.path.basename(file))
                    file_item.setData(file, Qt.ItemDataRole.UserRole)  # Store full path
                    drive_item.appendRow(file_item)
                    new_filtered_files.append(file)

            self.filtered_files = new_filtered_files

            if drive_item.rowCount() > 0:
                new_model.appendRow(drive_item)
                self.statusBar.showMessage(f"Filter applied. Found {len(self.filtered_files)} matching files")

                # Replace the old model with the new one
                self.tree_view.setModel(new_model)
                self.tree_model = new_model

                # Automatically expand all items
                for i in range(self.tree_model.rowCount()):
                    index = self.tree_model.indexFromItem(self.tree_model.item(i))
                    self.tree_view.expand(index)
            else:
                self.statusBar.showMessage("No files match the filter criteria")

            # Update file count
            self.update_file_count()

        except Exception as e:
            self.statusBar.showMessage(f"Error applying filter: {str(e)}")
            print(f"Error in apply_filter: {str(e)}")
            # Try to recover by resetting the filter
            self.reset_filter()

    def reset_filter(self):
        """Reset the filter to show all files from the current drive"""
        if not self.current_drive:
            QMessageBox.warning(self, "Warning", "Please select a drive first")
            return

        try:
            # Create a new model to rebuild the tree safely
            new_model = QStandardItemModel()
            new_model.setHorizontalHeaderLabels([""])

            # Add favorites and history items first
            favorites_item = QStandardItem(get_text('favorites', self.current_language))
            favorites_item.setEditable(False)
            favorites_item.setData(get_text('favorites', self.current_language), Qt.ItemDataRole.UserRole)
            new_model.appendRow(favorites_item)

            history_item = QStandardItem(get_text('play_history', self.current_language))
            history_item.setEditable(False)
            history_item.setData(get_text('play_history', self.current_language), Qt.ItemDataRole.UserRole)
            new_model.appendRow(history_item)

            # Add favorite items
            for track in sorted(self.favorites):
                if os.path.exists(track):
                    metadata = self.get_metadata(track)
                    display_text = f"{metadata['artist']} - {metadata['title']}"
                    if self.show_full_path:
                        display_text += f" ({track})"
                    file_item = QStandardItem(display_text)
                    file_item.setData(track, Qt.ItemDataRole.UserRole)
                    file_item.setEditable(False)
                    favorites_item.appendRow(file_item)

            # Add history items
            for track in self.play_history:
                if os.path.exists(track):
                    metadata = self.get_metadata(track)
                    display_text = f"{metadata['artist']} - {metadata['title']}"
                    if self.show_full_path:
                        display_text += f" ({track})"
                    file_item = QStandardItem(display_text)
                    file_item.setData(track, Qt.ItemDataRole.UserRole)
                    file_item.setEditable(False)
                    history_item.appendRow(file_item)

            # Create drive item
            drive_item = QStandardItem(self.current_drive)

            if self.current_drive in self.saved_files:
                self.filtered_files = self.saved_files[self.current_drive].copy()
                for file in self.filtered_files:
                    file_item = QStandardItem(file if self.show_full_path else os.path.basename(file))
                    file_item.setData(file, Qt.ItemDataRole.UserRole)  # Store full path
                    drive_item.appendRow(file_item)
                self.statusBar.showMessage(f"Reset filter. Showing all {len(self.filtered_files)} files")
            else:
                self.statusBar.showMessage("No files found for current drive")

            new_model.appendRow(drive_item)
            self.positive_filter.clear()
            self.negative_filter.clear()

            # Replace the old model with the new one
            self.tree_view.setModel(new_model)
            self.tree_model = new_model

            # Expand only drive/playlist sections, not favorites and history
            for i in range(self.tree_model.rowCount()):
                item = self.tree_model.item(i)
                if item and item.text() not in [get_text('favorites', self.current_language), get_text('play_history', self.current_language)]:
                    index = self.tree_model.indexFromItem(item)
                    self.tree_view.expand(index)

            # Update file count
            self.update_file_count()

        except Exception as e:
            self.statusBar.showMessage(f"Error resetting filter: {str(e)}")
            print(f"Error in reset_filter: {str(e)}")
            # Try to recover by creating a minimal model
            try:
                self.tree_model.clear()
                self.filtered_files = []
                self.update_file_count()
            except:
                pass

    def save_filtered_list(self):
        if not self.filtered_files:
            QMessageBox.warning(self, "Warning", "No filtered list to save")
            return

        # Create and show the dialog
        dialog = PlaylistNameDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_name()
            if not name:
                QMessageBox.warning(self, "Warning", "Please enter a playlist name")
                return

            # Ensure .json extension
            if not name.endswith('.json'):
                name += '.json'

            # Ask for save location
            playlist_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Playlist",
                os.path.join(self.playlist_dir, name),
                "JSON Files (*.json)"
            )

            if playlist_path:
                try:
                    # Update playlist directory to the directory of the saved file
                    self.playlist_dir = os.path.dirname(playlist_path)
                    self.save_config()

                    with open(playlist_path, 'w') as f:
                        json.dump(self.filtered_files, f)
                    self.statusBar.showMessage(f"Playlist '{name}' saved successfully")
                    # Refresh playlist list
                    self.refresh_playlists()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error saving playlist: {str(e)}")
                    self.statusBar.showMessage(f"Error saving playlist: {str(e)}")

    def play_selected_track(self, index):
        """Handle double click on track"""
        item = self.tree_model.itemFromIndex(index)
        if not item:  # Skip if no item
            return

        # Handle double click on favorites or history section
        if not item.parent() and item.text() in [get_text('favorites', self.current_language), get_text('play_history', self.current_language)]:
            # Toggle expansion state
            if self.tree_view.isExpanded(index):
                self.tree_view.collapse(index)
            else:
                self.tree_view.expand(index)
            return

        if not item.parent():  # Skip if not a file
            return

        # Get the full path from the item's data
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if not file_path:  # Fallback to text if no data
            file_path = item.text()

        # Play the selected track
        self.play_selected_track_by_path(file_path)

    def play_pause(self):
        if not self.current_track:
            return

        if self.is_playing:
            # Store current position before pausing
            self.pause_position = pygame.mixer.music.get_pos() / 1000.0
            pygame.mixer.music.pause()
            self.play_button.setText("Play")
            self.is_playing = False
            self.statusBar.showMessage("Playback paused")
            self.position_timer.stop()
        else:
            # Use play_selected_track_by_path for consistency
            if self.pause_position > 0:
                # Resume from pause position
                self.play_selected_track_by_path(self.current_track)
            else:
                # Start from beginning
                self.play_selected_track_by_path(self.current_track)

    def stop_playback(self):
        """Stop the current playback"""
        try:
            # Stop the music
            pygame.mixer.music.stop()

            # Reset playback state
            self.play_button.setText("Play")
            self.is_playing = False
            self.statusBar.showMessage("Playback stopped")
            self.position_timer.stop()
            self.progress_bar.setValue(0)
            self.current_time_label.setText("00:00")
            self.total_time_label.setText("00:00")
            self.pause_position = 0

            # Clear lyrics display
            if hasattr(self, 'lyrics_display'):
                self.lyrics_display.clear()

            # Stop SRT display if open
            if self.srt_display and self.srt_display.isVisible():
                self.srt_display.stop_display()
                self.srt_display.close()
                self.srt_display = None

        except Exception as e:
            self.statusBar.showMessage(f"Error stopping playback: {str(e)}")
            print(f"Error in stop_playback: {str(e)}")

    def closeEvent(self, event):
        """Handle application close"""
        try:
            # Stop playback and cleanup
            self.stop_playback()

            # Stop timers
            self.position_timer.stop()
            self.status_restore_timer.stop()

            # Close pygame mixer
            pygame.mixer.quit()

            # Close any open ODT documents
            if hasattr(self, 'lyrics_dialog') and self.lyrics_dialog:
                self.lyrics_dialog.close()

            # Close SRT display if open
            if hasattr(self, 'srt_display') and self.srt_display:
                self.srt_display.close()

            # Save configuration
            self.save_config()

            # Accept the close event
            event.accept()

        except Exception as e:
            print(f"Error during application close: {str(e)}")
            event.accept()  # Still close the application even if there's an error

    def show_help(self):
        """Show the help dialog"""
        dialog = HelpDialog(self, self.current_language)
        dialog.exec()

    def get_lyrics_path(self, music_file, extension='.txt'):
        """Get the path for the lyrics file corresponding to a music file"""
        # First check if there's a mapping for this music file
        if music_file in self.lyrics_mapping:
            return self.lyrics_mapping[music_file]

        # If no mapping, use the default naming convention
        base_name = os.path.splitext(os.path.basename(music_file))[0]
        return os.path.join(self.lyrics_dir, f"{base_name}{extension}")

    def get_metadata(self, file_path):
        """Get metadata from audio file with cache size management"""
        if file_path in self.metadata_cache:
            # Move to end of dict (most recently used)
            metadata = self.metadata_cache.pop(file_path)
            self.metadata_cache[file_path] = metadata
            return metadata

        try:
            audio = File(file_path)
            metadata = {}

            # Try to get metadata from ID3 tags
            if audio is not None:
                metadata = {
                    "title": audio.get("title", [""])[0],
                    "artist": audio.get("artist", [""])[0],
                    "album": audio.get("album", [""])[0]
                }

            # If title or artist is missing, try to parse from filename
            filename = os.path.splitext(os.path.basename(file_path))[0]
            if not metadata.get("title") or not metadata.get("artist"):
                # Try to split on common separators
                for separator in [" - ", "-", "_", " – "]:
                    if separator in filename:
                        parts = filename.split(separator, 1)
                        if len(parts) == 2:
                            if not metadata.get("artist"):
                                metadata["artist"] = parts[0].strip()
                            if not metadata.get("title"):
                                metadata["title"] = parts[1].strip()
                            break

            # If still no title, use filename
            if not metadata.get("title"):
                metadata["title"] = filename

            # If still no artist, use Unknown
            if not metadata.get("artist"):
                metadata["artist"] = get_text('unknown_artist', self.current_language)

            # Ensure album is set
            if not metadata.get("album"):
                metadata["album"] = get_text('unknown_album', self.current_language)

            # Manage cache size
            if len(self.metadata_cache) >= self.metadata_cache_size_limit:
                # Remove oldest entry (first in dict)
                self.metadata_cache.pop(next(iter(self.metadata_cache)))

            # Store in cache
            self.metadata_cache[file_path] = metadata
            return metadata

        except Exception as e:
            error_msg = f"Fout bij lezen metadata: {str(e)}"
            print(error_msg)  # Log for debugging
            self.statusBar.showMessage(error_msg)  # Show to user

            # Try to parse from filename as fallback
            filename = os.path.splitext(os.path.basename(file_path))[0]
            for separator in [" - ", "-", "_", " – "]:
                if separator in filename:
                    parts = filename.split(separator, 1)
                    if len(parts) == 2:
                        return {
                            "title": parts[1].strip(),
                            "artist": parts[0].strip(),
                            "album": get_text('unknown_album', self.current_language)
                        }
            return {
                "title": filename,
                "artist": get_text('unknown_artist', self.current_language),
                "album": get_text('unknown_album', self.current_language)
            }

    def show_error(self, title, message, details=None):
        """Show error message to user with optional details"""
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        if details:
            error_dialog.setDetailedText(details)
        error_dialog.exec()
        self.statusBar.showMessage(message)

    def load_lyrics(self, music_file):
        """Load lyrics for a music file with improved error handling"""
        if not music_file:
            self.show_error("Fout", "Geen muziekbestand geselecteerd")
            return

        try:
            # Clear current lyrics display first
            self._clear_lyrics_display()

            # Get current mappings
            mapping = self.lyrics_mapping.get(music_file, {})
            text_path = None
            srt_path = None

            if isinstance(mapping, dict):
                text_path = mapping.get('text_path')
                srt_path = mapping.get('srt_path')
            else:
                # Handle old format
                if mapping and isinstance(mapping, str):  # Ensure mapping is a string
                    ext = os.path.splitext(mapping)[1].lower()
                    if ext == '.srt':
                        srt_path = mapping
                    else:
                        text_path = mapping

            # Try to load text lyrics first
            text_loaded = False
            if text_path and isinstance(text_path, str) and os.path.exists(text_path):
                ext = os.path.splitext(text_path)[1].lower()
                if ext == '.odt':
                    text_loaded = self._load_odt_file(text_path)
                else:
                    text_loaded = self._load_txt_file(text_path)

            # If no text lyrics found from mapping, try to find one with same name
            if not text_loaded:
                text_loaded = self._try_load_text_lyrics(music_file)

            # Handle SRT display
            if self.srt_display and self.srt_display.isVisible():
                # Try to load SRT from mapping first
                if srt_path and isinstance(srt_path, str) and os.path.exists(srt_path):
                    self._load_srt_file(srt_path)
                else:
                    # Try to find SRT with same name
                    base_name = os.path.splitext(os.path.basename(music_file))[0]
                    srt_path = os.path.join(self.lyrics_dir, f"{base_name}.srt")
                    if os.path.exists(srt_path):
                        self._load_srt_file(srt_path)
                    else:
                        # No SRT file found, clear the display
                        self.srt_display.stop_display()
                        self.srt_display.subtitle_label.clear()

            # If no lyrics found at all, show a message
            if not text_loaded and not (self.srt_display and self.srt_display.isVisible()):
                if hasattr(self, 'lyrics_display'):
                    self.lyrics_display.setText("Geen songtekst gevonden")
                self.statusBar.showMessage("Geen songtekst gevonden voor dit nummer")

        except Exception as e:
            self.show_error("Onverwachte fout", "Fout bij laden songtekst", str(e))
            if hasattr(self, 'lyrics_display'):
                self.lyrics_display.setText("Fout bij laden songtekst")

    def _clear_lyrics_display(self):
        """Clear the current lyrics display"""
        self.current_lyrics = ""
        if hasattr(self, 'lyrics_display'):
            self.lyrics_display.clear()

    def _try_load_mapped_lyrics(self, music_file):
        """Try to load lyrics from mapping"""
        if music_file not in self.lyrics_mapping:
            return False

        mapping = self.lyrics_mapping[music_file]
        lyrics_path = None
        file_type = None

        if isinstance(mapping, dict):
            lyrics_path = mapping.get('path')
            file_type = mapping.get('type')
        else:
            lyrics_path = mapping
            # Determine file type from extension
            ext = os.path.splitext(lyrics_path)[1].lower()
            if ext == '.odt':
                file_type = "ODT"
            elif ext == '.srt':
                file_type = "SRT"
            else:
                file_type = "TXT"

        if not lyrics_path:
            self.show_error("Fout", "Geen songtekst pad gevonden in mapping")
            return False

        if not os.path.exists(lyrics_path):
            self.show_error("Fout", f"Songtekst bestand niet gevonden: {os.path.basename(lyrics_path)}")
            return False

        try:
            if file_type == "SRT":
                # For SRT files, only load in the main display if no karaoke window is open
                if not self.srt_display or not self.srt_display.isVisible():
                    return self._load_srt_file(lyrics_path)
                return True
            elif file_type == "ODT":
                return self._load_odt_file(lyrics_path)
            elif file_type == "TXT":
                return self._load_txt_file(lyrics_path)
        except Exception as e:
            self.show_error("Fout", "Fout bij laden songtekst", str(e))
            return False

    def _load_odt_file(self, odt_path):
        """Load and display ODT file"""
        try:
            doc = load(odt_path)
            text_content = []
            for para in doc.getElementsByType(text.P):
                text_content.append(teletype.extractText(para))
            self.current_lyrics = '\n'.join(text_content)
            if hasattr(self, 'lyrics_display'):
                self.lyrics_display.setText(self.current_lyrics)
            self.statusBar.showMessage(f"ODT bestand geladen: {os.path.basename(odt_path)}")
            return True
        except Exception as e:
            self.show_error("Fout", f"Fout bij laden ODT bestand: {str(e)}")
            return False

    def _load_txt_file(self, txt_path):
        """Load and display TXT file"""
        try:
            # Try UTF-8 first
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    self.current_lyrics = f.read()
                    if hasattr(self, 'lyrics_display'):
                        self.lyrics_display.setText(self.current_lyrics)
                    self.statusBar.showMessage(f"TXT bestand geladen: {os.path.basename(txt_path)}")
                    return True
            except UnicodeDecodeError:
                with open(txt_path, 'r', encoding='latin-1') as f:
                    self.current_lyrics = f.read()
                    if hasattr(self, 'lyrics_display'):
                        self.lyrics_display.setText(self.current_lyrics)
                    self.statusBar.showMessage(f"TXT bestand geladen (latin-1): {os.path.basename(txt_path)}")
                    return True
        except Exception as e:
            self.show_error("Fout", f"Fout bij laden TXT bestand: {str(e)}")
            return False

    def _try_load_text_lyrics(self, music_file):
        """Try to load text lyrics (ODT or TXT) for a music file"""
        base_name = os.path.splitext(os.path.basename(music_file))[0]

        # Try ODT first
        odt_path = os.path.join(self.lyrics_dir, f"{base_name}.odt")
        if os.path.exists(odt_path):
            return self._load_odt_file(odt_path)

        # Try TXT
        txt_path = os.path.join(self.lyrics_dir, f"{base_name}.txt")
        if os.path.exists(txt_path):
            return self._load_txt_file(txt_path)

        return False

    def edit_lyrics(self):
        """Open dialog to edit lyrics"""
        if not self.current_track:
            QMessageBox.warning(self, "Waarschuwing", "Selecteer eerst een nummer")
            return

        try:
            # Get current mappings for this track
            current_mappings = self.lyrics_mapping.get(self.current_track, {})
            if isinstance(current_mappings, dict):
                current_text_file = current_mappings.get('text_path')
                current_srt_file = current_mappings.get('srt_path')
            else:
                # Convert old format to new format
                current_text_file = current_mappings if current_mappings else None
                current_srt_file = None
                if current_text_file:
                    ext = os.path.splitext(current_text_file)[1].lower()
                    if ext == '.srt':
                        current_srt_file = current_text_file
                        current_text_file = None

            # Show mapping dialog
            mapping_dialog = LyricsMappingDialog(self, self.current_track, current_text_file, current_srt_file, self.current_language)
            if mapping_dialog.exec() == QDialog.DialogCode.Accepted:
                new_text_path = mapping_dialog.get_text_path()
                new_srt_path = mapping_dialog.get_srt_path()

                # Update mapping with both paths
                if new_text_path or new_srt_path:
                    self.lyrics_mapping[self.current_track] = {
                        'text_path': new_text_path,
                        'srt_path': new_srt_path
                    }
                    # Update lyrics directory to the directory of the selected file
                    if new_text_path:
                        self.lyrics_dir = os.path.dirname(new_text_path)
                    elif new_srt_path:
                        self.lyrics_dir = os.path.dirname(new_srt_path)
                    self.save_config()

                    # Load and display the lyrics immediately
                    self.load_lyrics(self.current_track)
                    return  # Exit after successful mapping and loading

            # If we get here, either the mapping dialog was cancelled or no file was selected
            # Show edit dialog for existing lyrics
            self.lyrics_dialog = LyricsDialog(self, self.current_language)

            # If we have current lyrics, show them in the dialog
            if hasattr(self, 'lyrics_display'):
                current_text = self.lyrics_display.toPlainText()
                if current_text and current_text != "Geen songtekst gevonden":
                    self.lyrics_dialog.set_lyrics(current_text)

            if self.lyrics_dialog.exec() == QDialog.DialogCode.Accepted:
                new_lyrics = self.lyrics_dialog.get_lyrics()
                self.current_lyrics = new_lyrics

                # Ask user which format to save in
                format_dialog = QMessageBox(self)
                format_dialog.setWindowTitle("Opslaan als")
                format_dialog.setText("In welk formaat wil je de songtekst opslaan?")
                format_dialog.addButton("TXT", QMessageBox.ButtonRole.AcceptRole)
                format_dialog.addButton("ODT", QMessageBox.ButtonRole.AcceptRole)
                format_dialog.addButton("Annuleren", QMessageBox.ButtonRole.RejectRole)

                result = format_dialog.exec()

                if result == 0:  # TXT
                    try:
                        lyrics_path = self.get_lyrics_path(self.current_track, '.txt')
                        with open(lyrics_path, 'w', encoding='utf-8') as f:
                            f.write(new_lyrics)
                            # Update mapping while preserving SRT path if it exists
                            current_mapping = self.lyrics_mapping.get(self.current_track, {})
                            if isinstance(current_mapping, dict):
                                current_mapping['text_path'] = lyrics_path
                            else:
                                current_mapping = {'text_path': lyrics_path}
                            self.lyrics_mapping[self.current_track] = current_mapping
                            self.save_config()
                            if hasattr(self, 'lyrics_display'):
                                self.lyrics_display.setText(new_lyrics)
                        self.statusBar.showMessage("Songtekst opgeslagen als TXT")
                    except Exception as e:
                        self.statusBar.showMessage(f"Fout bij opslaan TXT: {str(e)}")

                elif result == 1:  # ODT
                    try:
                        lyrics_path = self.get_lyrics_path(self.current_track, '.odt')
                        doc = OpenDocumentText()
                        para = text.P()
                        para.addText(new_lyrics)
                        doc.text.addElement(para)
                        doc.save(lyrics_path)
                        # Update mapping while preserving SRT path if it exists
                        current_mapping = self.lyrics_mapping.get(self.current_track, {})
                        if isinstance(current_mapping, dict):
                            current_mapping['text_path'] = lyrics_path
                        else:
                            current_mapping = {'text_path': lyrics_path}
                        self.lyrics_mapping[self.current_track] = current_mapping
                        self.save_config()
                        if hasattr(self, 'lyrics_display'):
                            self.lyrics_display.setText(new_lyrics)
                        self.statusBar.showMessage("Songtekst opgeslagen als ODT")
                    except Exception as e:
                        self.statusBar.showMessage(f"Fout bij opslaan ODT: {str(e)}")

        except Exception as e:
            self.statusBar.showMessage(f"Fout bij bewerken songtekst: {str(e)}")
            print(f"Error in edit_lyrics: {str(e)}")

    def toggle_path_display(self):
        """Toggle between showing full path and filename only"""
        # Update button text first
        self.show_full_path = not self.show_full_path
        self.toggle_view_button.setText("Toon Bestandsnaam" if self.show_full_path else "Toon Pad")

        # Show status message
        self.statusBar.showMessage("Moment geduld, lijst wordt bijgewerkt...")
        QApplication.processEvents()  # Force UI update

        # Update all items in the tree view
        self.update_tree_view_display()

        # Clear status message
        self.statusBar.showMessage("Lijst bijgewerkt")

    def update_tree_view_display(self):
        """Update the display of all items in the tree view while preserving favorites and history"""
        try:
            # Create a new model instead of clearing the old one
            new_model = QStandardItemModel()
            new_model.setHorizontalHeaderLabels([""])

            # Copy all items to the new model
            root = self.tree_model.invisibleRootItem()
            for i in range(root.rowCount()):
                old_item = root.child(i)
                if not old_item:
                    continue

                # Create new item with same text
                new_item = QStandardItem(old_item.text())
                new_item.setData(old_item.data(Qt.ItemDataRole.UserRole), Qt.ItemDataRole.UserRole)
                new_item.setEditable(False)

                # Copy all child items
                for j in range(old_item.rowCount()):
                    old_child = old_item.child(j)
                    if not old_child:
                        continue

                    # Get the file path from data
                    file_path = old_child.data(Qt.ItemDataRole.UserRole)
                    if not file_path:
                        file_path = old_child.text()
                    
                    # Create new child item
                    new_child = QStandardItem()
                    new_child.setData(file_path, Qt.ItemDataRole.UserRole)
                    new_child.setEditable(False)
                    
                    # For main list items (not favorites/history), use the original display text
                    if old_item.text() not in [get_text('favorites', self.current_language), get_text('play_history', self.current_language)]:
                        # For main list, just use the filename without path
                        if self.show_full_path:
                            new_child.setText(f"{os.path.basename(file_path)} ({file_path})")
                        else:
                            new_child.setText(os.path.basename(file_path))
                    else:
                        # For favorites and history, use the artist - title format
                        display_text = old_child.text()
                        if " - " in display_text:
                            # If it's already in artist - title format, extract just that part
                            display_text = display_text.split(" (")[0]
                        
                        if self.show_full_path:
                            new_child.setText(f"{display_text} ({file_path})")
                        else:
                            new_child.setText(display_text)

                    new_item.appendRow(new_child)

                    # Process events periodically to keep UI responsive
                    if j % 100 == 0:  # Update every 100 items
                        QApplication.processEvents()

                new_model.appendRow(new_item)

            # Replace the old model with the new one
            self.tree_view.setModel(new_model)
            self.tree_model = new_model

            # Expand all items
            for i in range(self.tree_model.rowCount()):
                index = self.tree_model.indexFromItem(self.tree_model.item(i))
                self.tree_view.expand(index)

        except Exception as e:
            self.show_error("Fout", "Fout bij bijwerken weergave", str(e))
            self.statusBar.showMessage("Fout bij bijwerken weergave")

    def scan_drives(self):
        """Scan all available drives for audio files"""
        # Clear existing items if not appending
        if not self.append_checkbox.isChecked():
            self.tree_model.clear()
            self.drive_file_counts.clear()
            self.filtered_files = []

        # Get available drives with error handling
        drives = []
        for drive in range(65, 91):  # A-Z
            drive_letter = f"{chr(drive)}:"
            try:
                if os.path.exists(drive_letter):
                    drives.append(drive_letter)
            except Exception as e:
                print(f"Error checking drive {drive_letter}: {str(e)}")
                continue

        for drive in drives:
            try:
                # Check if drive already exists in the tree
                drive_item = None
                for i in range(self.tree_model.rowCount()):
                    item = self.tree_model.item(i)
                    if item.text().startswith(drive):
                        drive_item = item
                        break

                # If drive doesn't exist, create new item
                if not drive_item:
                    drive_item = QStandardItem(drive)
                    self.tree_model.appendRow(drive_item)

                # Scan de schijf voor audio bestanden
                audio_files = []
                try:
                    for root, _, files in os.walk(drive):
                        for file in files:
                            if file.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac')):
                                audio_files.append(os.path.join(root, file))
                except Exception as e:
                    print(f"Error scanning drive {drive}: {str(e)}")
                    continue

                # Update bestandsaantallen per type
                file_types = {}
                for file in audio_files:
                    ext = os.path.splitext(file)[1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1

                # Update of voeg toe aan drive_file_counts
                if drive in self.drive_file_counts:
                    # Update existing counts
                    self.drive_file_counts[drive]['total'] += len(audio_files)
                    for ext, count in file_types.items():
                        self.drive_file_counts[drive]['types'][ext] = self.drive_file_counts[drive]['types'].get(ext,
                                                                                                                 0) + count
                else:
                    # Add new drive counts
                    self.drive_file_counts[drive] = {
                        'total': len(audio_files),
                        'types': file_types
                    }

                # Update de drive item tekst met aantallen
                type_info = []
                for ext, count in self.drive_file_counts[drive]['types'].items():
                    type_info.append(f"{ext}: {count}")
                drive_item.setText(
                    f"{drive} ({self.drive_file_counts[drive]['total']} bestanden) - {', '.join(type_info)}")

                # Voeg bestanden toe aan de tree
                for file in audio_files:
                    # Check if file already exists under this drive
                    file_exists = False
                    for j in range(drive_item.rowCount()):
                        child_item = drive_item.child(j)
                        if child_item.data(Qt.ItemDataRole.UserRole) == file:
                            file_exists = True
                            break

                    if not file_exists:
                        file_item = QStandardItem(file if self.show_full_path else os.path.basename(file))
                        file_item.setData(file, Qt.ItemDataRole.UserRole)
                        drive_item.appendRow(file_item)
                        self.filtered_files.append(file)

                # Update status bar
                self.update_file_count_status()

            except Exception as e:
                print(f"Fout bij scannen van {drive}: {e}")
                continue

        # Automatically expand all drive items
        for i in range(self.tree_model.rowCount()):
            index = self.tree_model.indexFromItem(self.tree_model.item(i))
            self.tree_view.expand(index)

        self.statusBar.showMessage("Scanning complete")

    def update_file_count_status(self):
        total_files = sum(counts['total'] for counts in self.drive_file_counts.values())
        type_counts = {}

        for drive_counts in self.drive_file_counts.values():
            for ext, count in drive_counts['types'].items():
                type_counts[ext] = type_counts.get(ext, 0) + count

        type_info = []
        for ext, count in type_counts.items():
            type_info.append(f"{ext}: {count}")

        self.file_count_label.setText(f"Totaal: {total_files} bestanden - {', '.join(type_info)}")

    def save_files(self):
        """Save the current file list to disk"""
        try:
            with open('saved_files.json', 'w') as f:
                json.dump(self.saved_files, f)
            self.statusBar.showMessage("Files saved successfully")
        except Exception as e:
            self.statusBar.showMessage(f"Error saving files: {str(e)}")

    def save_config(self):
        """Save configuration to file"""
        try:
            self.config.update({
                'lyrics_dir': self.lyrics_dir,
                'playlist_dir': self.playlist_dir,
                'lyrics_mapping': self.lyrics_mapping,
                'favorites': list(self.favorites),  # Save favorites
                'play_history': self.play_history,  # Save history
                'language': self.current_language  # Save language preference
            })
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
        except Exception as e:
            self.statusBar.showMessage(get_text('error_saving_config', self.current_language, error=str(e)))

    def change_lyrics_dir(self):
        """Change the lyrics directory"""
        new_dir = QFileDialog.getExistingDirectory(
            self,
            "Selecteer Songteksten Map",
            self.lyrics_dir
        )
        if new_dir:
            self.lyrics_dir = new_dir
            self.lyrics_dir_path.setText(new_dir)
            self.save_config()

    def load_lyrics_mappings(self):
        """Load lyrics mappings from config file with improved error handling"""
        try:
            if not os.path.exists(self.config_file):
                print("Config file not found, starting with empty mappings")
                self.lyrics_mapping = {}
                return

            with open(self.config_file, 'r') as f:
                config = json.load(f)

            # Get mappings with fallback to empty dict
            mappings = config.get('lyrics_mapping', {})
            if not isinstance(mappings, dict):
                print("Invalid mappings format in config, resetting to empty dict")
                self.lyrics_mapping = {}
                return

            # Validate and clean up mappings
            valid_mappings = {}
            for music_file, mapping in mappings.items():
                try:
                    # Skip if music file doesn't exist
                    if not os.path.exists(music_file):
                        print(f"Skipping mapping for non-existent music file: {music_file}")
                        continue

                    # Handle both old and new mapping formats
                    if isinstance(mapping, dict):
                        # New format: {'text_path': path, 'srt_path': path}
                        text_path = mapping.get('text_path')
                        srt_path = mapping.get('srt_path')
                        
                        # Validate paths if they exist
                        if text_path and not os.path.exists(text_path):
                            print(f"Text file not found: {text_path}")
                            text_path = None
                        if srt_path and not os.path.exists(srt_path):
                            print(f"SRT file not found: {srt_path}")
                            srt_path = None
                            
                        # Only keep mapping if at least one valid path exists
                        if text_path or srt_path:
                            valid_mappings[music_file] = {
                                'text_path': text_path,
                                'srt_path': srt_path
                            }
                    elif isinstance(mapping, str):
                        # Old format: direct path string
                        if os.path.exists(mapping):
                            ext = os.path.splitext(mapping)[1].lower()
                            if ext == '.srt':
                                valid_mappings[music_file] = {'srt_path': mapping}
                            else:
                                valid_mappings[music_file] = {'text_path': mapping}
                        else:
                            print(f"Lyrics file not found: {mapping}")
                    else:
                        print(f"Invalid mapping format for {music_file}: {mapping}")

                except Exception as e:
                    print(f"Error processing mapping for {music_file}: {str(e)}")
                    continue

            # Update mappings with validated data
            self.lyrics_mapping = valid_mappings
            print(f"Successfully loaded {len(valid_mappings)} valid lyrics mappings")

            # Save the cleaned up mappings
            self.save_config()

        except json.JSONDecodeError as e:
            print(f"Error decoding config file: {str(e)}")
            self.lyrics_mapping = {}
            # Create backup of corrupted config
            try:
                backup_path = f"{self.config_file}.bak"
                if os.path.exists(self.config_file):
                    import shutil
                    shutil.copy2(self.config_file, backup_path)
                    print(f"Created backup of corrupted config at: {backup_path}")
            except Exception as backup_error:
                print(f"Failed to create config backup: {str(backup_error)}")
        except Exception as e:
            print(f"Unexpected error loading lyrics mappings: {str(e)}")
            self.lyrics_mapping = {}

    def show_context_menu(self, position):
        """Show context menu for tree view items"""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return

        item = self.tree_model.itemFromIndex(index)
        if not item:
            return

        # Create context menu
        menu = QMenu(self)

        if not item.parent():  # This is a playlist or drive item
            if item.text().endswith('.json'):  # This is a playlist
                delete_playlist_action = menu.addAction("Verwijder playlist")
                action = menu.exec(self.tree_view.viewport().mapToGlobal(position))
                if action == delete_playlist_action:
                    self.delete_playlist(item.text())
        else:  # This is a file item
            delete_action = menu.addAction("Verwijder uit playlist")
            action = menu.exec(self.tree_view.viewport().mapToGlobal(position))
            if action == delete_action:
                self.delete_track_from_playlist(item)

    def delete_playlist(self, playlist_name):
        """Delete a playlist file"""
        try:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Bevestig verwijderen",
                f"Weet je zeker dat je de playlist '{playlist_name}' wilt verwijderen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Get full path to playlist file
                playlist_path = os.path.join(self.playlist_dir, playlist_name)

                # Delete the file
                if os.path.exists(playlist_path):
                    os.remove(playlist_path)

                    # Remove from combo box
                    index = self.playlist_combo.findText(playlist_name)
                    if index >= 0:
                        self.playlist_combo.removeItem(index)

                    # Remove from tree view
                    for i in range(self.tree_model.rowCount()):
                        item = self.tree_model.item(i)
                        if item and item.text() == playlist_name:
                            self.tree_model.removeRow(i)
                            break

                    # Clear filtered files if this was the current playlist
                    if self.current_track and playlist_name == self.playlist_combo.currentText():
                        self.filtered_files = []
                        self.update_file_count()

                    self.statusBar.showMessage(f"Playlist '{playlist_name}' verwijderd")
                else:
                    self.statusBar.showMessage(f"Playlist '{playlist_name}' niet gevonden")

        except Exception as e:
            self.show_error("Fout", f"Fout bij verwijderen playlist: {str(e)}")

    def delete_track_from_playlist(self, item):
        """Delete a track from the playlist"""
        if not item or not item.parent():
            return

        # Get the file path
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if not file_path:
            file_path = item.text()

        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Bevestig verwijderen",
            f"Weet je zeker dat je '{os.path.basename(file_path)}' uit de playlist wilt verwijderen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from filtered files
            if file_path in self.filtered_files:
                self.filtered_files.remove(file_path)

            # Remove from tree view
            parent = item.parent()
            parent.removeRow(item.row())

            # Update status
            self.statusBar.showMessage(f"Nummer verwijderd uit playlist")

            # Update file count
            self.update_file_count()

            # If this was the current track, stop playback
            if file_path == self.current_track:
                self.stop_playback()

    def play_on_click(self, index):
        """Handle single click on track"""
        item = self.tree_model.itemFromIndex(index)
        if not item or not item.parent():  # Skip if not a file
            return

        # Get the full path from the item's data
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if not file_path:  # Fallback to text if no data
            file_path = item.text()

        # Update current track and load lyrics immediately
        self.current_track = file_path
        self.load_lyrics(file_path)  # Load lyrics immediately on selection
        self.statusBar.showMessage(f"Selected: {os.path.basename(file_path)}")

        # If we're already playing, start the new track
        if self.is_playing:
            self.play_selected_track_by_path(file_path)
        else:
            # Just update the UI to show it's selected
            self.progress_bar.setValue(0)
            self.current_time_label.setText("00:00")
            self.total_time_label.setText("00:00")

    def toggle_srt_display(self):
        """Toggle the SRT display window"""
        if not self.current_track:
            QMessageBox.warning(self, "Waarschuwing", "Selecteer eerst een nummer")
            return

        try:
            if self.srt_display is None or not self.srt_display.isVisible():
                # Create and show SRT display
                self.srt_display = SRTDisplayDialog(self, self.current_language)

                # Try to load SRT file
                srt_loaded = False

                # First try mapping
                if self.current_track in self.lyrics_mapping:
                    mapping = self.lyrics_mapping[self.current_track]
                    if isinstance(mapping, dict):
                        srt_path = mapping.get('srt_path')
                        if srt_path and isinstance(srt_path, str) and os.path.exists(srt_path):
                            srt_loaded = self.srt_display.load_srt(srt_path)
                    elif isinstance(mapping, str) and mapping.lower().endswith('.srt'):
                        if os.path.exists(mapping):
                            srt_loaded = self.srt_display.load_srt(mapping)

                # If not loaded from mapping, try to find SRT file with same name
                if not srt_loaded:
                    base_name = os.path.splitext(os.path.basename(self.current_track))[0]
                    srt_path = os.path.join(self.lyrics_dir, f"{base_name}.srt")
                    if os.path.exists(srt_path):
                        srt_loaded = self.srt_display.load_srt(srt_path)

                if srt_loaded:
                    self.srt_display.show()
                    self.statusBar.showMessage("Karaoke venster geopend")
                else:
                    # Clean up SRT display if no file was found
                    if self.srt_display:
                        self.srt_display.close()
                        self.srt_display.deleteLater()
                        self.srt_display = None
                    QMessageBox.information(self, "Geen karaoke bestand",
                                            "Er is geen SRT bestand gevonden voor dit nummer.\n\n"
                                            "Je kunt een SRT bestand maken via 'Bewerk Songtekst' en dan 'Koppelen'.")
            else:
                # Hide SRT display
                if self.srt_display:
                    self.srt_display.stop_display()
                    self.srt_display.close()
                    self.srt_display.deleteLater()
                    self.srt_display = None
                self.statusBar.showMessage("Karaoke venster gesloten")

        except Exception as e:
            # Clean up in case of error
            if self.srt_display:
                try:
                    self.srt_display.stop_display()
                    self.srt_display.close()
                    self.srt_display.deleteLater()
                except:
                    pass
                self.srt_display = None
            self.show_error("Fout", "Fout bij openen karaoke venster", str(e))
            self.statusBar.showMessage("Fout bij openen karaoke venster")

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        try:
            key = event.key()

            # Space bar for play/pause
            if key == Qt.Key.Key_Space:
                self.play_pause()

            # Left/Right arrows for previous/next
            elif key == Qt.Key.Key_Left:
                self.play_previous_track()
            elif key == Qt.Key.Key_Right:
                self.play_next_track()

            # F for favorite
            elif key == Qt.Key.Key_F:
                self.toggle_favorite()

            # H for help
            elif key == Qt.Key.Key_H:
                self.show_help()

            # L for language switch
            elif key == Qt.Key.Key_L:
                self.switch_language()

            # M for mute
            elif key == Qt.Key.Key_M:
                self.toggle_mute()

            # S for stop
            elif key == Qt.Key.Key_S:
                self.stop_playback()

            # V for toggle view
            elif key == Qt.Key.Key_V:
                self.toggle_path_display()

            # +/- for volume
            elif key == Qt.Key.Key_Plus or key == Qt.Key.Key_Equal:
                self.adjust_volume(0.1)  # Increase volume
            elif key == Qt.Key.Key_Minus:
                self.adjust_volume(-0.1)  # Decrease volume

            else:
                super().keyPressEvent(event)

        except Exception as e:
            print(f"Error in keyPressEvent: {str(e)}")
            super().keyPressEvent(event)

    def toggle_favorite(self):
        """Toggle favorite status of current track"""
        if not self.current_track:
            return

        if self.current_track in self.favorites:
            self.favorites.remove(self.current_track)
            self.statusBar.showMessage(get_text('favorite_removed', self.current_language))
            self.favorite_button.setChecked(False)
        else:
            self.favorites.add(self.current_track)
            self.statusBar.showMessage(get_text('favorite_added', self.current_language))
            self.favorite_button.setChecked(True)

        self.save_config()  # Save changes
        self.update_favorites_display()

    def toggle_mute(self):
        """Toggle mute state"""
        try:
            if self.is_muted:
                # Unmute
                pygame.mixer.music.set_volume(self.previous_volume)
                self.is_muted = False
                self.statusBar.showMessage(f"Geluid aan (volume: {int(self.previous_volume * 100)}%)")
            else:
                # Mute
                self.previous_volume = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(0)
                self.is_muted = True
                self.statusBar.showMessage("Geluid uit")
        except Exception as e:
            print(f"Error in toggle_mute: {str(e)}")

    def adjust_volume(self, delta):
        """Adjust volume by delta (-1.0 to 1.0)"""
        try:
            current_volume = pygame.mixer.music.get_volume()
            new_volume = max(0.0, min(1.0, current_volume + delta))
            pygame.mixer.music.set_volume(new_volume)
            self.is_muted = False
            self.previous_volume = new_volume
            self.statusBar.showMessage(f"Volume: {int(new_volume * 100)}%")
        except Exception as e:
            print(f"Error in adjust_volume: {str(e)}")

    def add_to_history(self, track):
        """Add track to play history"""
        if track in self.play_history:
            self.play_history.remove(track)  # Remove if already exists
        self.play_history.insert(0, track)  # Add to front
        if len(self.play_history) > self.max_history_items:
            self.play_history.pop()  # Remove oldest if too many
        self.save_config()
        self.update_history_display()

    def update_history_display(self):
        """Update the history display in the tree view"""
        # Verzamel alle mogelijke vertalingen van 'play_history'
        history_names = [get_text('play_history', lang) for lang in get_available_languages()]
        # Verwijder alle bestaande geschiedenis-secties ongeacht de taal
        root = self.tree_model.invisibleRootItem()
        rows_to_remove = []
        for i in range(root.rowCount()):
            item = root.child(i)
            if item and item.text() in history_names:
                rows_to_remove.append(i)
        for i in reversed(rows_to_remove):
            root.removeRow(i)
        # Voeg de geschiedenis-sectie toe in de huidige taal
        history_item = QStandardItem(get_text('play_history', self.current_language))
        history_item.setEditable(False)
        history_item.setData(get_text('play_history', self.current_language), Qt.ItemDataRole.UserRole)
        # Voeg toe na favorieten (indien aanwezig)
        fav_index = 0
        for i in range(root.rowCount()):
            item = root.child(i)
            if item and item.text() == get_text('favorites', self.current_language):
                fav_index = i + 1
        root.insertRow(fav_index, history_item)
        # Voeg geschiedenis-items toe
        for track in self.play_history:
            if os.path.exists(track):
                metadata = self.get_metadata(track)
                display_text = f"{metadata['artist']} - {metadata['title']}"
                if self.show_full_path:
                    display_text += f" ({track})"
                file_item = QStandardItem(display_text)
                file_item.setData(track, Qt.ItemDataRole.UserRole)
                file_item.setEditable(False)
                history_item.appendRow(file_item)

    def update_favorites_display(self):
        """Update the favorites display in the tree view"""
        # Verzamel alle mogelijke vertalingen van 'favorites'
        favorite_names = [get_text('favorites', lang) for lang in get_available_languages()]
        # Verwijder alle bestaande favorieten-secties ongeacht de taal
        root = self.tree_model.invisibleRootItem()
        rows_to_remove = []
        for i in range(root.rowCount()):
            item = root.child(i)
            if item and item.text() in favorite_names:
                rows_to_remove.append(i)
        for i in reversed(rows_to_remove):
            root.removeRow(i)
        # Voeg de favorieten-sectie toe in de huidige taal
        favorites_item = QStandardItem(get_text('favorites', self.current_language))
        favorites_item.setEditable(False)
        favorites_item.setData(get_text('favorites', self.current_language), Qt.ItemDataRole.UserRole)
        root.insertRow(0, favorites_item)
        # Voeg favoriete items toe
        for track in sorted(self.favorites):
            if os.path.exists(track):
                metadata = self.get_metadata(track)
                display_text = f"{metadata['artist']} - {metadata['title']}"
                if self.show_full_path:
                    display_text += f" ({track})"
                file_item = QStandardItem(display_text)
                file_item.setData(track, Qt.ItemDataRole.UserRole)
                file_item.setEditable(False)
                favorites_item.appendRow(file_item)

    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.source() == self.tree_view:
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event"""
        if event.source() == self.tree_view:
            # Get the source and target items
            source_index = self.tree_view.currentIndex()
            target_index = self.tree_view.indexAt(event.pos())

            if not source_index.isValid() or not target_index.isValid():
                return

            source_item = self.tree_model.itemFromIndex(source_index)
            target_item = self.tree_model.itemFromIndex(target_index)

            # Only allow moving items within the same playlist
            if source_item.parent() and target_item.parent() and source_item.parent() == target_item.parent():
                # Get the playlist name
                playlist_name = source_item.parent().text()

                # Get the file paths
                source_path = source_item.data(Qt.ItemDataRole.UserRole)
                target_path = target_item.data(Qt.ItemDataRole.UserRole)

                if source_path and target_path:
                    # Update the filtered files list
                    source_idx = self.filtered_files.index(source_path)
                    target_idx = self.filtered_files.index(target_path)

                    # Move the item
                    self.filtered_files.insert(target_idx, self.filtered_files.pop(source_idx))

                    # Update the tree view
                    source_row = source_item.row()
                    target_row = target_item.row()

                    # Move the item in the tree
                    source_item.parent().takeChild(source_row)
                    source_item.parent().insertRow(target_row, source_item)

                    # Save the updated playlist
                    self.save_playlist(playlist_name)

                    # Update status
                    self.statusBar.showMessage(f"Nummer verplaatst in {playlist_name}")

                    # Update playlist info
                    self.update_playlist_info()

    def save_playlist(self, playlist_name):
        """Save the current playlist to file"""
        try:
            playlist_path = os.path.join(self.playlist_dir, playlist_name)
            with open(playlist_path, 'w') as f:
                json.dump(self.filtered_files, f)
            self.statusBar.showMessage(f"Playlist '{playlist_name}' opgeslagen")
        except Exception as e:
            self.statusBar.showMessage(f"Fout bij opslaan playlist: {str(e)}")

    def update_playlist_info(self):
        """Update the playlist information in the status bar"""
        if self.current_track and self.filtered_files:
            current_idx = self.filtered_files.index(self.current_track)
            total_tracks = len(self.filtered_files)
            self.playlist_info_label.setText(f"Track {current_idx + 1} van {total_tracks}")

            # Update next track info
            if current_idx < total_tracks - 1:
                next_track = self.filtered_files[current_idx + 1]
                metadata = self.get_metadata(next_track)
                self.next_track_label.setText(f"Volgende: {metadata['artist']} - {metadata['title']}")
            else:
                self.next_track_label.setText("Volgende: Einde afspeellijst")
        else:
            self.playlist_info_label.setText("")
            self.next_track_label.setText("")

    def cleanup_saved_files(self):
        """Clean up saved_files.json to remove references to non-existent drives and files"""
        try:
            if not os.path.exists('saved_files.json'):
                return
            
            with open('saved_files.json', 'r') as f:
                loaded_saved_files = json.load(f)
            
            # Filter out non-existent drives and files
            cleaned_saved_files = {}
            for drive, files in loaded_saved_files.items():
                try:
                    if os.path.exists(drive):
                        # Only keep files that still exist
                        valid_files = [f for f in files if os.path.exists(f)]
                        if valid_files:
                            cleaned_saved_files[drive] = valid_files
                        else:
                            print(f"Drive {drive} exists but no valid files found, removing from saved files")
                    else:
                        print(f"Drive {drive} not found, removing from saved files")
                except Exception as e:
                    print(f"Error validating drive {drive}: {str(e)}")
                    continue
            
            # Save cleaned version back to file
            with open('saved_files.json', 'w') as f:
                json.dump(cleaned_saved_files, f)
            
            print(f"Cleaned saved_files.json: {len(loaded_saved_files)} drives -> {len(cleaned_saved_files)} drives")
            
        except Exception as e:
            print(f"Error cleaning up saved_files.json: {str(e)}")

    def check_path_exists_with_timeout(self, path, timeout=1.0):
        """Check if a path exists with a timeout"""
        import threading
        
        path_exists = [False]
        path_error = [None]
        
        def check_path():
            try:
                path_exists[0] = os.path.exists(path)
            except Exception as e:
                path_error[0] = e
        
        # Start path check in separate thread
        thread = threading.Thread(target=check_path)
        thread.daemon = True
        thread.start()
        
        # Wait for the specified timeout
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            print(f"Timeout checking path: {path}")
            return False
        
        if path_error[0]:
            print(f"Error checking path {path}: {str(path_error[0])}")
            return False
        
        return path_exists[0]

    def manual_cleanup(self):
        """Manually clean up saved files with user confirmation and progress"""
        try:
            # Check if saved_files.json exists
            if not os.path.exists('saved_files.json'):
                QMessageBox.information(self, "Cleanup", "No saved files to clean up.")
                return
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Cleanup Confirmation",
                "This will remove references to non-existent drives and files.\n"
                "This process may take some time if you have network drives.\n\n"
                "Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
            
            # Load saved files
            with open('saved_files.json', 'r') as f:
                loaded_saved_files = json.load(f)
            
            # Create progress dialog
            progress = QProgressDialog("Cleaning up saved files...", "Cancel", 0, len(loaded_saved_files), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setWindowTitle("Cleanup Progress")
            progress.setAutoClose(True)
            
            # Filter out non-existent drives and files
            cleaned_saved_files = {}
            processed_drives = 0
            
            for drive, files in loaded_saved_files.items():
                if progress.wasCanceled():
                    break
                
                try:
                    progress.setLabelText(f"Checking drive {drive}...")
                    progress.setValue(processed_drives)
                    QApplication.processEvents()
                    
                    if os.path.exists(drive):
                        # Check files with progress updates
                        valid_files = []
                        for i, file in enumerate(files):
                            if progress.wasCanceled():
                                break
                            
                            # Update progress every 10 files
                            if i % 10 == 0:
                                progress.setLabelText(f"Checking drive {drive}... ({i}/{len(files)} files)")
                                QApplication.processEvents()
                            
                            if os.path.exists(file):
                                valid_files.append(file)
                        
                        if valid_files:
                            cleaned_saved_files[drive] = valid_files
                            print(f"Drive {drive}: {len(valid_files)} valid files kept")
                        else:
                            print(f"Drive {drive}: no valid files found, removing")
                    else:
                        print(f"Drive {drive}: not found, removing")
                        
                except Exception as e:
                    print(f"Error processing drive {drive}: {str(e)}")
                    continue
                
                processed_drives += 1
            
            progress.setValue(len(loaded_saved_files))
            
            if not progress.wasCanceled():
                # Save cleaned version back to file
                with open('saved_files.json', 'w') as f:
                    json.dump(cleaned_saved_files, f)
                
                # Show results
                removed_drives = len(loaded_saved_files) - len(cleaned_saved_files)
                total_files_before = sum(len(files) for files in loaded_saved_files.values())
                total_files_after = sum(len(files) for files in cleaned_saved_files.values())
                
                QMessageBox.information(
                    self,
                    "Cleanup Complete",
                    f"Cleanup completed successfully!\n\n"
                    f"Drives removed: {removed_drives}\n"
                    f"Files removed: {total_files_before - total_files_after}\n"
                    f"Remaining drives: {len(cleaned_saved_files)}\n"
                    f"Remaining files: {total_files_after}"
                )
                
                # Refresh the drive list
                self.refresh_drives()
            else:
                QMessageBox.information(self, "Cleanup Cancelled", "Cleanup was cancelled by user.")
            
        except Exception as e:
            QMessageBox.critical(self, "Cleanup Error", f"Error during cleanup: {str(e)}")
            print(f"Error in manual_cleanup: {str(e)}")

    def switch_language(self):
        """Switch to the next available language"""
        available_languages = get_available_languages()
        current_index = available_languages.index(self.current_language)
        next_index = (current_index + 1) % len(available_languages)
        new_language = available_languages[next_index]
        
        self.current_language = new_language
        
        # Update window title
        self.setWindowTitle(get_text('window_title', self.current_language))
        
        # Update all other UI elements (including help button)
        self.update_ui_language()
        
        # Save language preference
        self.save_config()
        
        # Update language status
        self.update_language_status()

    def update_ui_language(self):
        """Update all UI elements to use the current language"""
        try:
            # Update window title
            self.setWindowTitle(get_text('window_title', self.current_language))
            
            # Update language button (always use globe emoji)
            self.language_button.setText("🌐")
            self.language_button.setToolTip(get_text('language_tooltip', self.current_language))
            
            # Update help button
            if hasattr(self, 'help_button'):
                self.help_button.setText(get_text('help_button', self.current_language))
            
            # Update basic controls directly
            self.drive_combo.setPlaceholderText(get_text('select_drive', self.current_language))
            self.refresh_button.setText(get_text('refresh_drives', self.current_language))
            self.read_button.setText(get_text('read_files', self.current_language))
            self.toggle_view_button.setText(get_text('toggle_view', self.current_language))
            self.scan_button.setText(get_text('scan_drive', self.current_language))
            self.cleanup_button.setText(get_text('cleanup_files', self.current_language))
            
            # Update lyrics directory controls
            self.lyrics_dir_label.setText(get_text('lyrics_dir_label', self.current_language))
            self.lyrics_dir_button.setText(get_text('change_lyrics_dir', self.current_language))
            
            # Update lyrics panel
            self.lyrics_title.setText(get_text('lyrics_title', self.current_language))
            self.edit_button.setText(get_text('edit_lyrics_button', self.current_language))
            self.srt_button.setText(get_text('show_karaoke_button', self.current_language))
            
            # Update tooltips
            self.toggle_view_button.setToolTip(get_text('toggle_view_tooltip', self.current_language))
            self.scan_button.setToolTip(get_text('scan_button_tooltip', self.current_language))
            self.read_button.setToolTip(get_text('read_button_tooltip', self.current_language))
            self.refresh_button.setToolTip(get_text('refresh_button_tooltip', self.current_language))
            
            # Update playlist controls
            self.playlist_combo.setPlaceholderText(get_text('select_playlist', self.current_language))
            
            # Update filter placeholders
            self.positive_filter.setPlaceholderText(get_text('positive_filter', self.current_language))
            self.negative_filter.setPlaceholderText(get_text('negative_filter', self.current_language))
            
            # Update append checkbox
            self.append_checkbox.setText(get_text('append_checkbox', self.current_language))
            
            # Update playback controls
            self.play_button.setText(get_text('play_button', self.current_language))
            self.stop_button.setText(get_text('stop_button', self.current_language))
            self.prev_button.setText(get_text('prev_button', self.current_language))
            self.next_button.setText(get_text('next_button', self.current_language))
            self.favorite_button.setText(get_text('favorite_button', self.current_language))
            
            # Update tooltips
            self.play_button.setToolTip(get_text('play_tooltip', self.current_language))
            self.stop_button.setToolTip(get_text('stop_tooltip', self.current_language))
            self.prev_button.setToolTip(get_text('prev_tooltip', self.current_language))
            self.next_button.setToolTip(get_text('next_tooltip', self.current_language))
            self.favorite_button.setToolTip(get_text('favorite_tooltip', self.current_language))
            
            # Update file count label
            current_count = self.file_count_label.text().split(': ')[-1] if ': ' in self.file_count_label.text() else '0'
            self.file_count_label.setText(get_text('files_label', self.current_language).replace('0', current_count))
            
            # Update status bar
            try:
                language_text = get_text('current_language', self.current_language, 
                                       language_name=get_language_name(self.current_language))
                # Fallback als placeholder niet vervangen is
                if '{language_name}' in language_text:
                    language_name = get_language_name(self.current_language)
                    language_text = language_text.replace('{language_name}', language_name)
                self.statusBar.showMessage(language_text)
            except Exception as e:
                print(f"Error formatting current language: {e}")
                # Simpele fallback
                language_name = get_language_name(self.current_language)
                self.statusBar.showMessage(f"Current language: {language_name}")
            
            # Update tree view favorites and history section names
            self.update_favorites_display()
            self.update_history_display()
            
        except Exception as e:
            print(f"Error updating UI language: {str(e)}")
            # Continue with basic updates even if some fail
            pass

    def restore_language_status(self):
        """Restore the language status text if no other important status is shown"""
        if self.language_status_text:
            current_status = self.statusBar.currentMessage()
            # Only restore if current status is empty or contains language-related text
            if not current_status or any(keyword in current_status.lower() for keyword in ['language', 'taal', 'sprache', 'langue']):
                self.statusBar.showMessage(self.language_status_text)
    
    def update_language_status(self):
        """Update the language status text and start the restore timer"""
        # Eenvoudige mapping van taal codes naar namen
        language_names = {
            'nl': 'Nederlands',
            'en': 'English', 
            'de': 'Deutsch',
            'fr': 'Français'
        }
        
        # Haal de taalnaam op uit de mapping
        language_name = language_names.get(self.current_language, self.current_language)
        
        # Maak de status tekst
        status_texts = {
            'nl': f'Huidige taal: {language_name}',
            'en': f'Current language: {language_name}',
            'de': f'Aktuelle Sprache: {language_name}',
            'fr': f'Langue actuelle: {language_name}'
        }
        
        # Kies de juiste status tekst voor de huidige taal
        status_text = status_texts.get(self.current_language, status_texts['en'])
        
        # Update de status
        self.language_status_text = status_text
        self.statusBar.showMessage(status_text)
        
        # Start de restore timer
        self.status_restore_timer.start()


class ScanningDialog(QDialog):
    def __init__(self, parent=None, drive=None, language='nl'):
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(get_text('scanning_title', self.language))
        self.setModal(True)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Add some padding

        # Create and style the label
        label = QLabel(get_text('scanning_message', self.language, drive=drive))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Remove window frame and set window flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # No window frame
            Qt.WindowType.Tool |  # Tool window (stays on top)
            Qt.WindowType.WindowStaysOnTopHint  # Always on top
        )

        # Set background color
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border: 2px solid #555555;
                border-radius: 10px;
            }
        """)

        # Size the dialog based on content
        self.adjustSize()

        # Center the dialog in the parent window
        if parent:
            parent_geometry = parent.geometry()
            dialog_geometry = self.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - dialog_geometry.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_geometry.height()) // 2
            self.move(x, y)

    def closeEvent(self, event):
        event.accept()

    def showEvent(self, event):
        """Ensure dialog stays centered when shown"""
        super().showEvent(event)
        if self.parent():
            parent_geometry = self.parent().geometry()
            dialog_geometry = self.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - dialog_geometry.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_geometry.height()) // 2
            self.move(x, y)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        player = MusicPlayer()
        player.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        # Try to show a simple error dialog if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Startup Error", f"Error starting HAL's Music Player:\n{str(e)}\n\nPlease check that all required files are present.")
            root.destroy()
        except:
            # If tkinter is not available, just print to console
            print("Failed to show error dialog. Please check the console for error details.")
        sys.exit(1) 