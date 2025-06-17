import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTextEdit, QFileDialog, QProgressBar,
                             QGroupBox, QMessageBox, QDialog, QLineEdit, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor
import time
import os
import docx
import pygame
from odf.opendocument import load
from odf.text import P


class EditLineDialog(QDialog):
    def __init__(self, parent=None, current_text=""):
        super().__init__(parent)
        self.setWindowTitle("Regel Bewerken")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Label en invoerveld
        self.label = QLabel("Bewerk de tekst:")
        self.entry = QLineEdit()
        self.entry.setText(current_text)
        self.entry.selectAll()

        # Knoppen
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Opslaan")
        self.cancel_button = QPushButton("Annuleren")

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        # Layout toevoegen
        layout.addWidget(self.label)
        layout.addWidget(self.entry)
        layout.addLayout(button_layout)

        # Connect signals
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.entry.returnPressed.connect(self.accept)

        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                font-size: 12px;
                color: #ffffff;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #555555;
                border-radius: 4px;
                background: #3b3b3b;
                color: #ffffff;
            }
            QPushButton {
                padding: 8px 16px;
                font-size: 12px;
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
            }
            QPushButton[text="Annuleren"] {
                background-color: #3b3b3b;
            }
            QPushButton[text="Annuleren"]:hover {
                background-color: #4b4b4b;
            }
        """)


class SRTGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRT Maker voor Liedjes")
        self.setMinimumSize(800, 600)  # Reduced minimum height
        self.resize(800, 800)  # Default size

        # Initialize variables
        self.text_lines = []
        self.timestamps = []
        self.end_timestamps = []
        self.line_index = 0
        self.audio_file = None
        self.start_time = None
        self.is_start_time = True
        self.is_loading = False
        self.current_line_tag = None  # For tracking the current line

        # Setup UI
        self.setup_ui()
        self.setup_style()

        # Initialize pygame for audio
        pygame.mixer.init()

    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #ffffff;
            }
            QPushButton {
                padding: 6px 12px;
                font-size: 12px;
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                min-width: 100px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
            }
            QPushButton:pressed {
                background-color: #2b2b2b;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #666666;
                border-color: #444444;
            }
            QPushButton#clickButton {
                background-color: #2d5a27;
                color: white;
                border-color: #1a3d17;
                min-height: 90px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#clickButton:hover {
                background-color: #3a7233;
                border-color: #2d5a27;
            }
            QPushButton#clickButton:pressed {
                background-color: #1a3d17;
            }
            QPushButton#newSessionButton {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                min-width: 100px;
                min-height: 25px;
                font-weight: bold;
            }
            QPushButton#newSessionButton:hover {
                background-color: #4b4b4b;
            }
            QTextEdit {
                font-size: 13px;
                padding: 8px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #3b3b3b;
                color: #ffffff;
                line-height: 1.4;
                selection-background-color: #4a6da7;
                selection-color: #ffffff;
            }
            QTextEdit:focus {
                border: 1px solid #00a0ff;
            }
            QLabel {
                font-size: 12px;
                color: #ffffff;
            }
            QLabel#titleLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
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
        """)

    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Create a scroll area for the main content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create a widget to hold the scrollable content
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title_label = QLabel("Songtekst Ondertiteling Generator")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # File selection group
        file_group = QGroupBox("Bestandsselectie")
        file_layout = QVBoxLayout(file_group)

        self.file_label = QLabel("Selecteer een tekstbestand")
        self.file_label.setStyleSheet("font-weight: bold;")

        self.button_open = QPushButton("Open Songtekst")
        self.button_audio = QPushButton("Open Audiobestand")

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.button_open)
        file_layout.addWidget(self.button_audio)
        layout.addWidget(file_group)

        # Text editing group
        text_group = QGroupBox("Songtekst Bewerken")
        text_layout = QVBoxLayout(text_group)

        # Text manipulation buttons
        text_buttons_layout = QHBoxLayout()
        self.button_clear = QPushButton("Wis Tekst")
        self.button_remove_line = QPushButton("Verwijder Regel")
        self.button_add_line = QPushButton("Voeg Regel Toe")
        self.button_edit_line = QPushButton("Bewerk Regel")
        self.button_clean_lines = QPushButton("Verwijder Blanco Regels")

        text_buttons_layout.addWidget(self.button_clear)
        text_buttons_layout.addWidget(self.button_remove_line)
        text_buttons_layout.addWidget(self.button_add_line)
        text_buttons_layout.addWidget(self.button_edit_line)
        text_buttons_layout.addWidget(self.button_clean_lines)
        text_buttons_layout.addStretch()

        # Text display
        self.text_display = QTextEdit()
        self.text_display.setMinimumHeight(250)
        self.text_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_display.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_display.setCursorWidth(2)
        self.text_display.setAcceptRichText(False)

        self.text_display.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                margin: 0px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #3b3b3b;
                color: #ffffff;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        self.text_status = QLabel("")

        text_layout.addLayout(text_buttons_layout)
        text_layout.addWidget(self.text_display)
        text_layout.addWidget(self.text_status)

        layout.addWidget(text_group)

        # Add the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Add control buttons outside scroll area to keep them always visible
        control_layout = QHBoxLayout()
        self.button_play = QPushButton("Start Timing")
        self.button_new_session = QPushButton("Nieuwe Sessie")
        self.button_click = QPushButton("Regel Vastleggen\nstart=muis ingedrukt, stop=loslaten")
        self.button_click.setObjectName("clickButton")
        self.button_save = QPushButton("Sla SRT op")

        control_layout.addWidget(self.button_play)
        control_layout.addWidget(self.button_new_session)
        control_layout.addWidget(self.button_click)
        control_layout.addWidget(self.button_save)

        main_layout.addLayout(control_layout)

        # Status label outside scroll area
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        # Connect signals
        self.button_open.clicked.connect(self.open_file)
        self.button_audio.clicked.connect(self.open_audio)
        self.button_play.clicked.connect(self.play_audio)
        self.button_new_session.clicked.connect(self.start_new_session)
        self.button_click.pressed.connect(self.record_start)
        self.button_click.released.connect(self.record_end)
        self.button_save.clicked.connect(self.save_srt)
        self.button_clear.clicked.connect(self.clear_text)
        self.button_remove_line.clicked.connect(self.remove_current_line)
        self.button_add_line.clicked.connect(self.add_line)
        self.button_edit_line.clicked.connect(self.edit_current_line)
        self.button_clean_lines.clicked.connect(self.remove_blank_lines)
        self.text_display.textChanged.connect(self.on_text_change)

        # Initial button states
        self.button_play.setEnabled(False)
        self.button_click.setEnabled(False)
        self.button_save.setEnabled(False)

    def on_text_change(self):
        try:
            # Skip text change handling during loading
            if self.is_loading:
                return

            current_text = self.text_display.toPlainText()
            new_lines = [line.strip() for line in current_text.splitlines() if line.strip()]

            # Only update if the text actually changed
            if new_lines != self.text_lines:
                self.text_lines = new_lines
                self.text_status.setText(f"Aantal regels: {len(self.text_lines)}")
                self.button_play.setEnabled(bool(self.text_lines and self.audio_file))
                print(f"Text changed: {len(self.text_lines)} lines")  # Debug

        except Exception as e:
            print(f"Error in on_text_change: {str(e)}")  # Debug

    def clear_text(self):
        reply = QMessageBox.question(self, 'Bevestig',
                                     'Weet je zeker dat je alle tekst wilt wissen?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.text_display.clear()
            self.text_lines = []
            self.on_text_change()
            self.button_play.setEnabled(False)
            # Make text editable after clearing
            self.text_display.setReadOnly(False)

    def remove_current_line(self):
        cursor = self.text_display.textCursor()
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        if cursor.hasSelection():
            cursor.removeSelectedText()
            self.on_text_change()
            # Make text editable after removing line
            self.text_display.setReadOnly(False)
        else:
            self.text_status.setText("Selecteer eerst een regel om te verwijderen")

    def add_line(self):
        cursor = self.text_display.textCursor()
        cursor.insertBlock()
        self.text_display.setTextCursor(cursor)
        self.text_display.setFocus()
        # Make text editable after adding line
        self.text_display.setReadOnly(False)

    def edit_current_line(self):
        cursor = self.text_display.textCursor()
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        if cursor.hasSelection():
            current_text = cursor.selectedText()
            dialog = EditLineDialog(self, current_text)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_text = dialog.entry.text().strip()
                if new_text:
                    cursor.insertText(new_text)
                    self.on_text_change()
                    # Make text editable after editing line
                    self.text_display.setReadOnly(False)
        else:
            self.text_status.setText("Selecteer eerst een regel om te bewerken")

    def open_file(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Songtekst",
                "",
                "Text files (*.txt);;Word files (*.docx);;OpenOffice files (*.odt)"
            )

            if file_path:
                print(f"Opening file: {file_path}")  # Debug
                self.text_lines = self.read_text_from_file(file_path)
                print(f"Read {len(self.text_lines)} lines")  # Debug

                if self.text_lines:
                    self.file_label.setText(f"Gekozen bestand: {os.path.basename(file_path)}")
                    self.display_text()
                    self.button_play.setEnabled(bool(self.audio_file))
                    self.status_label.setText(f"Bestand geladen: {len(self.text_lines)} regels")
                    # Make text editable after loading
                    self.text_display.setReadOnly(False)
                else:
                    print("No lines were loaded")  # Debug
                    self.file_label.setText("Selecteer een tekstbestand")
                    self.button_play.setEnabled(False)
                    self.status_label.setText("Geen tekst gevonden in bestand")

        except Exception as e:
            print(f"Error in open_file: {str(e)}")  # Debug
            self.status_label.setText(f"Fout bij openen bestand: {str(e)}")
            QMessageBox.critical(self, "Fout", f"Kon bestand niet openen:\n{str(e)}")
            self.file_label.setText("Selecteer een tekstbestand")
            self.button_play.setEnabled(False)

    def open_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audiobestand", "", "Audio files (*.mp3;*.wav)")
        if file_path:
            self.audio_file = file_path
            self.button_play.setEnabled(bool(self.text_lines))
            self.status_label.setText(f"Audiobestand geladen: {os.path.basename(file_path)}")

    def read_text_from_file(self, file_path):
        def clean_text(text):
            """Helper function to thoroughly clean text"""
            if not text:
                return ""
            # Replace various special characters and spaces
            replacements = {
                '\u00A0': ' ',  # non-breaking space
                '\u202F': ' ',  # narrow non-breaking space
                '\u2007': ' ',  # figure space
                '\u200B': '',  # zero-width space
                '\u200C': '',  # zero-width non-joiner
                '\u200D': '',  # zero-width joiner
                '\u200E': '',  # left-to-right mark
                '\u200F': '',  # right-to-left mark
                '\uFEFF': '',  # zero-width no-break space
                '\t': ' ',  # tab
                '\r': '',  # carriage return
                '\f': '',  # form feed
                '\v': '',  # vertical tab
            }

            # Apply replacements
            for old, new in replacements.items():
                text = text.replace(old, new)

            # Normalize whitespace and strip
            text = ' '.join(text.split())
            return text.strip()

        try:
            if not file_path or not isinstance(file_path, str):
                raise ValueError("Ongeldig bestandspad")

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Bestand niet gevonden: {file_path}")

            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == ".txt":
                encodings = ['utf-8', 'latin-1', 'cp1252']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                            # Split into lines and clean each line
                            lines = [clean_text(line) for line in content.splitlines()]
                            # Filter out empty lines
                            lines = [line for line in lines if line]
                            print(f"Loaded {len(lines)} lines from text file")  # Debug
                            return lines
                    except UnicodeDecodeError:
                        continue
                raise UnicodeError(f"Kon bestand niet lezen met ondersteunde tekencoderingen: {encodings}")

            elif file_ext == ".docx":
                try:
                    doc = docx.Document(file_path)
                    lines = []
                    for para in doc.paragraphs:
                        # Get plain text and clean it
                        text = clean_text(para.text)
                        if text:
                            lines.append(text)
                    print(f"Loaded {len(lines)} lines from docx file")  # Debug
                    return lines
                except Exception as e:
                    raise Exception(f"Fout bij lezen van DOCX bestand: {str(e)}")

            elif file_ext == ".odt":
                try:
                    doc = load(file_path)
                    text_lines = []

                    # Process all text elements
                    for element in doc.getElementsByType(P):
                        try:
                            # Collect all text from the paragraph
                            paragraph_text = ""
                            for node in element.childNodes:
                                if node.nodeType == node.TEXT_NODE:
                                    paragraph_text += node.data

                            # Clean the collected text
                            cleaned_text = clean_text(paragraph_text)
                            if cleaned_text:
                                text_lines.append(cleaned_text)

                        except Exception as e:
                            print(f"Waarschuwing: Kon regel niet verwerken: {str(e)}")
                            continue

                    print(f"Loaded {len(text_lines)} lines from odt file")  # Debug
                    return text_lines

                except Exception as e:
                    raise Exception(f"Fout bij lezen van ODT bestand: {str(e)}")

            else:
                raise ValueError(f"Niet-ondersteund bestandsformaat: {file_ext}")

        except Exception as e:
            self.status_label.setText(f"Fout bij laden bestand: {str(e)}")
            QMessageBox.critical(self, "Fout", f"Kon bestand niet laden:\n{str(e)}")
            return []

    def display_text(self):
        try:
            print(f"Displaying {len(self.text_lines)} lines")  # Debug
            if not self.text_lines:
                self.text_display.clear()
                return

            # Set loading flag to prevent text change events
            self.is_loading = True

            # Clear the text widget first
            self.text_display.clear()

            # Set the text without line numbers
            text_content = "\n".join(self.text_lines)
            self.text_display.setPlainText(text_content)

            # Automatically remove blank lines
            self.remove_blank_lines()

            # Scroll to the beginning of the text
            cursor = self.text_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.text_display.setTextCursor(cursor)

            # Update the status
            self.text_status.setText(f"Aantal regels: {len(self.text_lines)}")
            print("Text display updated")  # Debug

            # Reset loading flag
            self.is_loading = False

        except Exception as e:
            self.is_loading = False  # Make sure to reset flag even if there's an error
            print(f"Error in display_text: {str(e)}")  # Debug
            self.status_label.setText(f"Fout bij weergeven tekst: {str(e)}")
            QMessageBox.critical(self, "Fout", f"Kon tekst niet weergeven:\n{str(e)}")

    def play_audio(self):
        if self.audio_file:
            # Make text read-only before starting timing
            self.text_display.setReadOnly(True)
            pygame.mixer.music.load(self.audio_file)
            pygame.mixer.music.play()
            self.start_timing()

    def start_timing(self):
        try:
            self.start_time = time.time()
            self.timestamps = []
            self.end_timestamps = []
            self.line_index = 0
            self.button_click.setEnabled(True)
            self.button_save.setEnabled(False)
            self.status_label.setText("Klik op de groene knop om timing vast te leggen")

            # Make text read-only during timing
            self.text_display.setReadOnly(True)

            # Reset cursor to start
            cursor = self.text_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.clearSelection()
            self.text_display.setTextCursor(cursor)

        except Exception as e:
            print(f"Error in start_timing: {str(e)}")  # Debug
            self.status_label.setText(f"Fout bij starten timing: {str(e)}")

    def record_start(self):
        try:
            if self.line_index < len(self.text_lines):
                # Record start time
                elapsed_time = time.time() - self.start_time
                self.timestamps.append(elapsed_time)

                # Move to current line and highlight it
                cursor = self.text_display.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                for _ in range(self.line_index):
                    cursor.movePosition(QTextCursor.MoveOperation.NextBlock)

                # Select and highlight the current line
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                self.text_display.setTextCursor(cursor)

                # Calculate scroll position to show current line and next lines
                viewport_height = self.text_display.viewport().height()
                line_height = self.text_display.fontMetrics().height()
                visible_lines = viewport_height / line_height

                # Calculate how many lines to show after current line
                lines_after = min(3, len(self.text_lines) - self.line_index - 1)

                # Calculate target scroll position
                if self.line_index > 0:
                    # Move cursor down to show some context
                    scroll_cursor = self.text_display.textCursor()
                    for _ in range(lines_after):
                        scroll_cursor.movePosition(QTextCursor.MoveOperation.NextBlock)

                    # Scroll to show the context
                    self.text_display.setTextCursor(scroll_cursor)
                    self.text_display.ensureCursorVisible()

                    # Move back to current line
                    cursor = self.text_display.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
                    for _ in range(self.line_index):
                        cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                    self.text_display.setTextCursor(cursor)

                # Update status
                self.status_label.setText(f"Timing regel {self.line_index + 1} van {len(self.text_lines)}")

        except Exception as e:
            print(f"Error in record_start: {str(e)}")  # Debug
            self.status_label.setText(f"Fout bij start timing: {str(e)}")

    def record_end(self):
        try:
            if self.line_index < len(self.text_lines):
                # Record end time
                elapsed_time = time.time() - self.start_time
                self.end_timestamps.append(elapsed_time)

                # Move to next line
                self.line_index += 1

                # Clear selection
                cursor = self.text_display.textCursor()
                cursor.clearSelection()

                # If we're not at the end, move to next line
                if self.line_index < len(self.text_lines):
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
                    for _ in range(self.line_index):
                        cursor.movePosition(QTextCursor.MoveOperation.NextBlock)

                self.text_display.setTextCursor(cursor)

                # Update status and buttons
                if self.line_index >= len(self.text_lines):
                    self.button_click.setEnabled(False)
                    self.button_save.setEnabled(True)
                    self.status_label.setText("Alle regels getimed")
                else:
                    self.status_label.setText(f"Klaar voor regel {self.line_index + 1} van {len(self.text_lines)}")

        except Exception as e:
            print(f"Error in record_end: {str(e)}")  # Debug
            self.status_label.setText(f"Fout bij stop timing: {str(e)}")

    def save_srt(self):
        if not self.timestamps or len(self.text_lines) != len(self.timestamps):
            return

        srt_content = ""
        for i in range(len(self.text_lines)):
            start_time = self.format_srt_time(self.timestamps[i])
            end_time = self.format_srt_time(self.end_timestamps[i])
            srt_content += f"{i + 1}\n{start_time} --> {end_time}\n{self.text_lines[i]}\n\n"

        srt_path, _ = QFileDialog.getSaveFileName(self, "Sla SRT op", "", "SRT files (*.srt)")
        if srt_path:
            try:
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                self.status_label.setText(f"SRT bestand opgeslagen: {os.path.basename(srt_path)}")
            except Exception as e:
                self.status_label.setText(f"Fout bij opslaan SRT: {str(e)}")
                QMessageBox.critical(self, "Fout", f"Kon SRT bestand niet opslaan:\n{str(e)}")

    def format_srt_time(self, timestamp):
        t = time.gmtime(int(timestamp))
        milliseconds = int((timestamp - int(timestamp)) * 1000)
        return time.strftime(f"%H:%M:%S,{milliseconds:03d}", t)

    def remove_blank_lines(self):
        try:
            # Get current text and split into lines
            current_text = self.text_display.toPlainText()
            lines = current_text.splitlines()

            # Remove blank lines from start and end
            while lines and not lines[0].strip():
                lines.pop(0)
            while lines and not lines[-1].strip():
                lines.pop()

            # Remove any remaining blank lines in the middle
            lines = [line for line in lines if line.strip()]

            # Update the text
            self.is_loading = True  # Prevent text change events
            self.text_display.setPlainText("\n".join(lines))
            self.is_loading = False

            # Update status
            removed_lines = len(current_text.splitlines()) - len(lines)
            if removed_lines > 0:
                self.status_label.setText(f"{removed_lines} blanco regels verwijderd")
            else:
                self.status_label.setText("Geen blanco regels gevonden")

        except Exception as e:
            print(f"Error in remove_blank_lines: {str(e)}")  # Debug
            self.status_label.setText(f"Fout bij verwijderen blanco regels: {str(e)}")

    def start_new_session(self):
        try:
            # Stop any playing audio
            pygame.mixer.music.stop()

            # Reset all timing variables
            self.timestamps = []
            self.end_timestamps = []
            self.line_index = 0
            self.start_time = None
            self.is_start_time = True

            # Reset button states
            self.button_play.setEnabled(bool(self.text_lines and self.audio_file))
            self.button_click.setEnabled(False)
            self.button_save.setEnabled(False)

            # Make text editable again
            self.text_display.setReadOnly(False)

            # Reset cursor to start
            cursor = self.text_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.clearSelection()
            self.text_display.setTextCursor(cursor)

            # Update status
            self.status_label.setText("Nieuwe sessie gestart")

        except Exception as e:
            print(f"Error in start_new_session: {str(e)}")  # Debug
            self.status_label.setText(f"Fout bij starten nieuwe sessie: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SRTGenerator()
    window.show()
    sys.exit(app.exec()) 