import sqlite3
import os
from typing import Dict, List, Optional

class LanguageDatabase:
    def __init__(self, db_path: str = "languages.db"):
        """Initialize the language database"""
        # Try to find the database in the same directory as this script
        if not os.path.exists(db_path):
            # Try relative to the script location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            alt_db_path = os.path.join(script_dir, "languages.db")
            if os.path.exists(alt_db_path):
                db_path = alt_db_path
                print(f"DEBUG: Using database at: {db_path}")
        
        self.db_path = db_path
        print(f"DEBUG: LanguageDatabase initialized with: {self.db_path}")
        self.init_database()
    
    def init_database(self):
        """Initialize the database with tables and default data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create languages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS languages (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create translations table with dynamic columns for each language
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                function_key TEXT PRIMARY KEY,
                category TEXT,
                description TEXT
            )
        ''')
        
        # Insert default languages
        languages = [
            ('nl', 'Nederlands'),
            ('en', 'English'),
            ('de', 'Deutsch'),
            ('fr', 'Français')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO languages (code, name) VALUES (?, ?)
        ''', languages)
        
        # Create language columns in translations table
        for lang_code, _ in languages:
            try:
                cursor.execute(f'ALTER TABLE translations ADD COLUMN {lang_code} TEXT')
            except sqlite3.OperationalError:
                # Column already exists
                pass
        
        # Insert default translations
        self.insert_default_translations(cursor)
        
        conn.commit()
        conn.close()
    
    def insert_default_translations(self, cursor):
        """Insert default translations into the database"""
        translations = [
            # Main window
            ('window_title', 'Main window', 'Main window title', 'nl', "HAL's Music Player", 'en', "HAL's Music Player", 'de', "HAL's Musik Player", 'fr', "Lecteur de Musique HAL"),
            ('title_label', 'Main window', 'Main title label', 'nl', "HAL's Music Player", 'en', "HAL's Music Player", 'de', "HAL's Musik Player", 'fr', "Lecteur de Musique HAL"),
            ('help_button', 'Main window', 'Help button text', 'nl', 'Hulp', 'en', 'Help', 'de', 'Hilfe', 'fr', 'Aide'),
            ('language_button', 'Main window', 'Language button symbol', 'nl', '🌐', 'en', '🌐', 'de', '🌐', 'fr', '🌐'),
            ('language_tooltip', 'Main window', 'Language button tooltip', 'nl', 'Wissel taal (L) - Huidige taal: Nederlands', 'en', 'Switch language (L) - Current language: English', 'de', 'Sprache wechseln (L) - Aktuelle Sprache: Deutsch', 'fr', 'Changer de langue (L) - Langue actuelle: Français'),
            ('current_language', 'Main window', 'Current language status', 'nl', 'Huidige taal: {language_name}', 'en', 'Current language: {language_name}', 'de', 'Aktuelle Sprache: {language_name}', 'fr', 'Langue actuelle: {language_name}'),
            
            # Drive controls
            ('select_drive', 'Drive controls', 'Drive selection placeholder', 'nl', 'Selecteer Schijf', 'en', 'Select Drive', 'de', 'Laufwerk auswählen', 'fr', 'Sélectionner le lecteur'),
            ('refresh_drives', 'Drive controls', 'Refresh drives button', 'nl', 'Ververs Schijven', 'en', 'Refresh Drives', 'de', 'Laufwerke aktualisieren', 'fr', 'Actualiser les lecteurs'),
            ('read_files', 'Drive controls', 'Read files button', 'nl', 'Lees Bestanden', 'en', 'Read Files', 'de', 'Dateien lesen', 'fr', 'Lire les fichiers'),
            ('scan_drive', 'Drive controls', 'Scan drive button', 'nl', 'Scan Geselecteerde Schijf', 'en', 'Scan Selected Drive', 'de', 'Ausgewähltes Laufwerk scannen', 'fr', 'Scanner le lecteur sélectionné'),
            ('cleanup_files', 'Drive controls', 'Cleanup files button', 'nl', 'Ruim Bestanden Op', 'en', 'Cleanup Files', 'de', 'Dateien bereinigen', 'fr', 'Nettoyer les fichiers'),
            ('toggle_view', 'Drive controls', 'Toggle view button', 'nl', 'Toon Bestandsnaam', 'en', 'Show Filename', 'de', 'Dateiname anzeigen', 'fr', 'Afficher le nom de fichier'),
            
            # Tooltips
            ('toggle_view_tooltip', 'Tooltips', 'Toggle view tooltip', 'nl', 'Wisselen tussen bestandsnaam en pad weergave (V)', 'en', 'Toggle between filename and path display (V)', 'de', 'Zwischen Dateiname und Pfad wechseln (V)', 'fr', 'Basculer entre nom de fichier et chemin (V)'),
            ('scan_button_tooltip', 'Tooltips', 'Scan button tooltip', 'nl', 'Scan geselecteerde schijf voor muziekbestanden', 'en', 'Scan selected drive for music files', 'de', 'Ausgewähltes Laufwerk nach Musikdateien scannen', 'fr', 'Scanner le lecteur sélectionné pour les fichiers musicaux'),
            ('read_button_tooltip', 'Tooltips', 'Read button tooltip', 'nl', 'Laad opgeslagen bestanden van geselecteerde schijf', 'en', 'Load saved files from selected drive', 'de', 'Gespeicherte Dateien vom ausgewählten Laufwerk laden', 'fr', 'Charger les fichiers sauvegardés du lecteur sélectionné'),
            ('refresh_button_tooltip', 'Tooltips', 'Refresh button tooltip', 'nl', 'Ververs lijst met beschikbare schijven', 'en', 'Refresh list of available drives', 'de', 'Liste der verfügbaren Laufwerke aktualisieren', 'fr', 'Actualiser la liste des lecteurs disponibles'),
            
            # Playback controls
            ('play_button', 'Playback controls', 'Play button text', 'nl', 'Afspelen', 'en', 'Play', 'de', 'Abspielen', 'fr', 'Lecture'),
            ('pause_button', 'Playback controls', 'Pause button text', 'nl', 'Pauze', 'en', 'Pause', 'de', 'Pause', 'fr', 'Pause'),
            ('stop_button', 'Playback controls', 'Stop button text', 'nl', 'Stop', 'en', 'Stop', 'de', 'Stopp', 'fr', 'Arrêt'),
            ('prev_button', 'Playback controls', 'Previous button text', 'nl', 'Vorige', 'en', 'Previous', 'de', 'Zurück', 'fr', 'Précédent'),
            ('next_button', 'Playback controls', 'Next button text', 'nl', 'Volgende', 'en', 'Next', 'de', 'Weiter', 'fr', 'Suivant'),
            ('favorite_button', 'Playback controls', 'Favorite button text', 'nl', 'Favoriet', 'en', 'Favorite', 'de', 'Favorit', 'fr', 'Favori'),
            
            # Playback tooltips
            ('play_tooltip', 'Playback tooltips', 'Play button tooltip', 'nl', 'Afspelen/Pauzeren (Spatiebalk)', 'en', 'Play/Pause (Spacebar)', 'de', 'Abspielen/Pause (Leertaste)', 'fr', 'Lecture/Pause (Barre d\'espace)'),
            ('stop_tooltip', 'Playback tooltips', 'Stop button tooltip', 'nl', 'Stoppen (S)', 'en', 'Stop (S)', 'de', 'Stoppen (S)', 'fr', 'Arrêt (S)'),
            ('prev_tooltip', 'Playback tooltips', 'Previous button tooltip', 'nl', 'Vorige nummer (Pijltje Links)', 'en', 'Previous track (Left Arrow)', 'de', 'Vorheriger Titel (Pfeil Links)', 'fr', 'Piste précédente (Flèche gauche)'),
            ('next_tooltip', 'Playback tooltips', 'Next button tooltip', 'nl', 'Volgende nummer (Pijltje Rechts)', 'en', 'Next track (Right Arrow)', 'de', 'Nächster Titel (Pfeil Rechts)', 'fr', 'Piste suivante (Flèche droite)'),
            ('favorite_tooltip', 'Playback tooltips', 'Favorite button tooltip', 'nl', 'Toevoegen aan/verwijderen uit favorieten (F)', 'en', 'Add to/remove from favorites (F)', 'de', 'Zu Favoriten hinzufügen/entfernen (F)', 'fr', 'Ajouter/supprimer des favoris (F)'),
            
            # Status messages
            ('ready', 'Status messages', 'Ready status', 'nl', 'Gereed', 'en', 'Ready', 'de', 'Bereit', 'fr', 'Prêt'),
            ('files_label', 'Status messages', 'Files count label', 'nl', 'Bestanden: 0', 'en', 'Files: 0', 'de', 'Dateien: 0', 'fr', 'Fichiers: 0'),
            ('scanning_complete', 'Status messages', 'Scanning complete message', 'nl', 'Scannen voltooid. {count} bestanden gevonden op schijf {drive}', 'en', 'Scanning complete. Found {count} files on drive {drive}', 'de', 'Scanning abgeschlossen. {count} Dateien auf Laufwerk {drive} gefunden', 'fr', 'Scan terminé. {count} fichiers trouvés sur le lecteur {drive}'),
            
            # Error messages
            ('error_loading_config', 'Error messages', 'Config loading error', 'nl', 'Fout bij laden configuratie: {error}', 'en', 'Error loading configuration: {error}', 'de', 'Fehler beim Laden der Konfiguration: {error}', 'fr', 'Erreur lors du chargement de la configuration: {error}'),
            ('error_saving_config', 'Error messages', 'Config saving error', 'nl', 'Fout bij opslaan configuratie: {error}', 'en', 'Error saving configuration: {error}', 'de', 'Fehler beim Speichern der Konfiguration: {error}', 'fr', 'Erreur lors de la sauvegarde de la configuration: {error}'),
            
            # Tree view sections
            ('favorites', 'Tree view', 'Favorites section', 'nl', 'Favorieten', 'en', 'Favorites', 'de', 'Favoriten', 'fr', 'Favoris'),
            ('play_history', 'Tree view', 'Play history section', 'nl', 'Afspeelgeschiedenis', 'en', 'Play History', 'de', 'Wiedergabeverlauf', 'fr', 'Historique de lecture'),
            
            # Filter section
            ('filter_options', 'Filter section', 'Filter options group title', 'nl', 'Filter Opties', 'en', 'Filter Options', 'de', 'Filteroptionen', 'fr', 'Options de filtre'),
            ('positive_filter', 'Filter section', 'Positive filter placeholder', 'nl', 'Voer tekst in die in de bestandsnaam moet voorkomen', 'en', 'Enter text that must be in filename', 'de', 'Text eingeben, der im Dateinamen enthalten sein muss', 'fr', 'Entrez le texte qui doit être dans le nom de fichier'),
            ('negative_filter', 'Filter section', 'Negative filter placeholder', 'nl', 'Voer tekst in die NIET in de bestandsnaam mag voorkomen', 'en', 'Enter text that must NOT be in filename', 'de', 'Text eingeben, der NICHT im Dateinamen enthalten sein darf', 'fr', 'Entrez le texte qui ne doit PAS être dans le nom de fichier'),
            ('filter_button', 'Filter section', 'Filter button', 'nl', 'Filter', 'en', 'Filter', 'de', 'Filter', 'fr', 'Filtrer'),
            ('reset_filter', 'Filter section', 'Reset filter button', 'nl', 'Reset Filter', 'en', 'Reset Filter', 'de', 'Filter zurücksetzen', 'fr', 'Réinitialiser le filtre'),
            ('save_filtered', 'Filter section', 'Save filtered list button', 'nl', 'Sla Gefilterde Lijst Op', 'en', 'Save Filtered List', 'de', 'Gefilterte Liste speichern', 'fr', 'Sauvegarder la liste filtrée'),
            
            # Playlist controls
            ('select_playlist', 'Playlist controls', 'Select playlist placeholder', 'nl', 'Selecteer Playlist', 'en', 'Select Playlist', 'de', 'Playlist auswählen', 'fr', 'Sélectionner la playlist'),
            ('load_playlist', 'Playlist controls', 'Load playlist button', 'nl', 'Laad Playlist', 'en', 'Load Playlist', 'de', 'Playlist laden', 'fr', 'Charger la playlist'),
            
            # Checkbox
            ('append_checkbox', 'Checkbox', 'Append checkbox text', 'nl', 'Lijsten aanvullen in plaats van vervangen', 'en', 'Append lists instead of replacing', 'de', 'Listen anhängen statt ersetzen', 'fr', 'Ajouter aux listes au lieu de remplacer'),
            
            # Right panel
            ('lyrics_title', 'Right panel', 'Lyrics title', 'nl', 'Songtekst', 'en', 'Lyrics', 'de', 'Songtext', 'fr', 'Paroles'),
            ('edit_lyrics', 'Right panel', 'Edit lyrics button', 'nl', 'Bewerk Songtekst', 'en', 'Edit Lyrics', 'de', 'Songtext bearbeiten', 'fr', 'Modifier les paroles'),
            ('show_karaoke', 'Right panel', 'Show karaoke button', 'nl', 'Toon Karaoke', 'en', 'Show Karaoke', 'de', 'Karaoke anzeigen', 'fr', 'Afficher le karaoké'),
            
            # Lyrics directory
            ('lyrics_dir_label', 'Lyrics directory', 'Lyrics directory label', 'nl', 'Songteksten map:', 'en', 'Lyrics directory:', 'de', 'Songtext-Verzeichnis:', 'fr', 'Répertoire des paroles:'),
            ('change_lyrics_dir', 'Lyrics directory', 'Change lyrics directory button', 'nl', 'Wijzigen', 'en', 'Change', 'de', 'Ändern', 'fr', 'Modifier'),
            
            # Help dialog translations
            ('help_title', 'Help dialog', 'Help dialog title', 'nl', 'HAL\'s Music Player - Gebruikershandleiding', 'en', 'HAL\'s Music Player - User Manual', 'de', 'HAL\'s Musik Player - Benutzerhandbuch', 'fr', 'Lecteur de Musique HAL - Manuel Utilisateur'),
            ('close_button', 'Help dialog', 'Close button text', 'nl', 'Sluiten', 'en', 'Close', 'de', 'Schließen', 'fr', 'Fermer'),
            ('image_not_found', 'Help dialog', 'Image not found message', 'nl', 'Afbeelding niet gevonden: {image}', 'en', 'Image not found: {image}', 'de', 'Bild nicht gefunden: {image}', 'fr', 'Image non trouvée: {image}'),
            
            # Help section titles
            ('help_section_1_title', 'Help dialog', 'Section 1 title', 'nl', '1. Netwerkstations Scannen', 'en', '1. Scanning Network Drives', 'de', '1. Netzwerkstationen Scannen', 'fr', '1. Scanner les Lecteurs Réseau'),
            ('help_section_2_title', 'Help dialog', 'Section 2 title', 'nl', '2. Bestanden Laden', 'en', '2. Loading Files', 'de', '2. Dateien Laden', 'fr', '2. Charger les Fichiers'),
            ('help_section_3_title', 'Help dialog', 'Section 3 title', 'nl', '3. Weergave Aanpassen', 'en', '3. Adjusting Display', 'de', '3. Anzeige Anpassen', 'fr', '3. Ajuster l\'Affichage'),
            ('help_section_4_title', 'Help dialog', 'Section 4 title', 'nl', '4. Boomweergave en Navigatie', 'en', '4. Tree View and Navigation', 'de', '4. Baumansicht und Navigation', 'fr', '4. Vue Arborescente et Navigation'),
            ('help_section_5_title', 'Help dialog', 'Section 5 title', 'nl', '5. Filteren van Bestanden', 'en', '5. Filtering Files', 'de', '5. Dateien Filtern', 'fr', '5. Filtrer les Fichiers'),
            ('help_section_6_title', 'Help dialog', 'Section 6 title', 'nl', '6. Muziek Afspelen', 'en', '6. Playing Music', 'de', '6. Musik Abspielen', 'fr', '6. Lire la Musique'),
            ('help_section_7_title', 'Help dialog', 'Section 7 title', 'nl', '7. Favorieten en Geschiedenis', 'en', '7. Favorites and History', 'de', '7. Favoriten und Verlauf', 'fr', '7. Favoris et Historique'),
            ('help_section_8_title', 'Help dialog', 'Section 8 title', 'nl', '8. Songteksten', 'en', '8. Lyrics', 'de', '8. Songtexte', 'fr', '8. Paroles'),
            ('help_section_9_title', 'Help dialog', 'Section 9 title', 'nl', '9. Playlists Beheren', 'en', '9. Managing Playlists', 'de', '9. Wiedergabelisten Verwalten', 'fr', '9. Gérer les Listes de Lecture'),
            ('help_section_10_title', 'Help dialog', 'Section 10 title', 'nl', '10. Bestandstypen', 'en', '10. File Types', 'de', '10. Dateitypen', 'fr', '10. Types de Fichiers'),
            ('help_section_11_title', 'Help dialog', 'Section 11 title', 'nl', '11. Configuratie', 'en', '11. Configuration', 'de', '11. Konfiguration', 'fr', '11. Configuration'),
            
            # Help section texts
            ('help_section_1_text', 'Help dialog', 'Section 1 text', 'nl', '1. Selecteer een schijf uit de dropdown lijst\n2. Klik op \'Scan Selected Drive\' om de geselecteerde schijf te scannen\n3. Er verschijnt een popup met \'Schijf aan het scannen, even geduld\'\n4. Daarna wordt een voortgangsvenster getoond met het aantal gevonden bestanden\n5. De gevonden bestanden worden in de lijst weergegeven met het aantal bestanden per type\n\nGebruik de checkbox \'Lijsten aanvullen in plaats van vervangen\' om bestanden toe te voegen aan de bestaande lijst.', 'en', '1. Select a drive from the dropdown list\n2. Click \'Scan Selected Drive\' to scan the selected drive\n3. A popup appears with \'Scanning drive, please wait\'\n4. Then a progress window is shown with the number of files found\n5. The found files are displayed in the list with the number of files per type\n\nUse the checkbox \'Append lists instead of replacing\' to add files to the existing list.', 'de', '1. Wählen Sie ein Laufwerk aus der Dropdown-Liste\n2. Klicken Sie auf \'Ausgewähltes Laufwerk Scannen\' um das ausgewählte Laufwerk zu scannen\n3. Ein Popup erscheint mit \'Laufwerk wird gescannt, bitte warten\'\n4. Dann wird ein Fortschrittsfenster mit der Anzahl gefundener Dateien angezeigt\n5. Die gefundenen Dateien werden in der Liste mit der Anzahl Dateien pro Typ angezeigt\n\nVerwenden Sie die Checkbox \'Listen ergänzen statt ersetzen\' um Dateien zur bestehenden Liste hinzuzufügen.', 'fr', '1. Sélectionnez un lecteur dans la liste déroulante\n2. Cliquez sur \'Scanner le Lecteur Sélectionné\' pour scanner le lecteur sélectionné\n3. Une popup apparaît avec \'Scan du lecteur, veuillez patienter\'\n4. Puis une fenêtre de progression est affichée avec le nombre de fichiers trouvés\n5. Les fichiers trouvés sont affichés dans la liste avec le nombre de fichiers par type\n\nUtilisez la case à cocher \'Ajouter aux listes au lieu de remplacer\' pour ajouter des fichiers à la liste existante.'),
            ('help_section_2_text', 'Help dialog', 'Section 2 text', 'nl', 'Selecteer een station uit de dropdown en klik op \'Read Files\' om de muziekbestanden te laden. De bestanden worden in de boomweergave getoond met artiest en titel uit de ID3 tags of bestandsnaam.\n\nGebruik de checkbox \'Lijsten aanvullen in plaats van vervangen\' om bestanden toe te voegen aan de bestaande lijst.', 'en', 'Select a drive from the dropdown and click \'Read Files\' to load the music files. The files are shown in the tree view with artist and title from ID3 tags or filename.\n\nUse the checkbox \'Append lists instead of replacing\' to add files to the existing list.', 'de', 'Wählen Sie ein Laufwerk aus der Dropdown-Liste und klicken Sie auf \'Dateien Lesen\' um die Musikdateien zu laden. Die Dateien werden in der Baumansicht mit Künstler und Titel aus den ID3-Tags oder Dateinamen angezeigt.\n\nVerwenden Sie die Checkbox \'Listen ergänzen statt ersetzen\' um Dateien zur bestehenden Liste hinzuzufügen.', 'fr', 'Sélectionnez un lecteur dans la liste déroulante et cliquez sur \'Lire les Fichiers\' pour charger les fichiers musicaux. Les fichiers sont affichés dans la vue arborescente avec l\'artiste et le titre des tags ID3 ou du nom de fichier.\n\nUtilisez la case à cocher \'Ajouter aux listes au lieu de remplacer\' pour ajouter des fichiers à la liste existante.'),
            ('help_section_3_text', 'Help dialog', 'Section 3 text', 'nl', 'Gebruik de \'Toon Bestandsnaam\' knop om te wisselen tussen:\n- Volledig pad met artiest en titel\n- Alleen artiest en titel\n\nDe weergave wordt automatisch bijgewerkt voor alle bestanden in de lijst.', 'en', 'Use the \'Show Filename\' button to toggle between:\n- Full path with artist and title\n- Artist and title only\n\nThe display is automatically updated for all files in the list.', 'de', 'Verwenden Sie die \'Dateiname Anzeigen\' Schaltfläche um zwischen zu wechseln:\n- Vollständiger Pfad mit Künstler und Titel\n- Nur Künstler und Titel\n\nDie Anzeige wird automatisch für alle Dateien in der Liste aktualisiert.', 'fr', 'Utilisez le bouton \'Afficher Nom de Fichier\' pour basculer entre:\n- Chemin complet avec artiste et titre\n- Artiste et titre seulement\n\nL\'affichage est automatiquement mis à jour pour tous les fichiers de la liste.'),
            ('help_section_4_text', 'Help dialog', 'Section 4 text', 'nl', 'De boomweergave toont je bestanden in een hiërarchische structuur:\n\nHoofdsecties:\n- Favorieten: Je favoriete nummers\n- Afspeelgeschiedenis: Recent afgespeelde nummers\n- Drive/Playlist secties: Bestanden van schijven of playlists\n\nNavigatie:\n- Klik op het pijltje (▶) naast een sectie om deze uit te klappen\n- Klik op het pijltje (▼) om een sectie in te klappen\n- Enkele klik op een nummer: selecteer en laad songtekst\n- Dubbelklik op een nummer: start afspelen\n- Rechtsklik op een nummer: context menu\n\nTip: Je kunt secties in- en uitklappen om de lijst overzichtelijk te houden.', 'en', 'The tree view shows your files in a hierarchical structure:\n\nMain sections:\n- Favorites: Your favorite tracks\n- Play History: Recently played tracks\n- Drive/Playlist sections: Files from drives or playlists\n\nNavigation:\n- Click the arrow (▶) next to a section to expand it\n- Click the arrow (▼) to collapse a section\n- Single click on a track: select and load lyrics\n- Double click on a track: start playback\n- Right click on a track: context menu\n\nTip: You can expand and collapse sections to keep the list organized.', 'de', 'Die Baumansicht zeigt Ihre Dateien in einer hierarchischen Struktur:\n\nHauptabschnitte:\n- Favoriten: Ihre Lieblingstitel\n- Wiedergabeverlauf: Kürzlich abgespielte Titel\n- Laufwerk/Wiedergabelisten-Abschnitte: Dateien von Laufwerken oder Wiedergabelisten\n\nNavigation:\n- Klicken Sie auf den Pfeil (▶) neben einem Abschnitt um ihn zu erweitern\n- Klicken Sie auf den Pfeil (▼) um einen Abschnitt zu reduzieren\n- Einzelklick auf einen Titel: auswählen und Songtext laden\n- Doppelklick auf einen Titel: Wiedergabe starten\n- Rechtsklick auf einen Titel: Kontextmenü\n\nTipp: Sie können Abschnitte erweitern und reduzieren um die Liste übersichtlich zu halten.', 'fr', 'La vue arborescente affiche vos fichiers dans une structure hiérarchique:\n\nSections principales:\n- Favoris: Vos titres favoris\n- Historique de lecture: Titres récemment lus\n- Sections Lecteur/Liste de lecture: Fichiers des lecteurs ou listes de lecture\n\nNavigation:\n- Cliquez sur la flèche (▶) à côté d\'une section pour l\'étendre\n- Cliquez sur la flèche (▼) pour réduire une section\n- Clic simple sur un titre: sélectionner et charger les paroles\n- Double-clic sur un titre: démarrer la lecture\n- Clic droit sur un titre: menu contextuel\n\nConseil: Vous pouvez étendre et réduire les sections pour garder la liste organisée.'),
            ('help_section_5_text', 'Help dialog', 'Section 5 text', 'nl', 'Gebruik de filteropties om specifieke bestanden te vinden:\n- Wel: Voer tekst in die in de bestandsnaam moet voorkomen\n- Niet: Voer tekst in die NIET in de bestandsnaam mag voorkomen\nKlik op \'Filter\' om de filter toe te passen.\n\nGebruik \'Reset Filter\' om alle bestanden weer te tonen.', 'en', 'Use the filter options to find specific files:\n- Include: Enter text that must be in the filename\n- Exclude: Enter text that must NOT be in the filename\nClick \'Filter\' to apply the filter.\n\nUse \'Reset Filter\' to show all files again.', 'de', 'Verwenden Sie die Filteroptionen um spezifische Dateien zu finden:\n- Einschließen: Geben Sie Text ein der im Dateinamen vorkommen muss\n- Ausschließen: Geben Sie Text ein der NICHT im Dateinamen vorkommen darf\nKlicken Sie auf \'Filtern\' um den Filter anzuwenden.\n\nVerwenden Sie \'Filter Zurücksetzen\' um alle Dateien wieder anzuzeigen.', 'fr', 'Utilisez les options de filtre pour trouver des fichiers spécifiques:\n- Inclure: Entrez du texte qui doit être dans le nom de fichier\n- Exclure: Entrez du texte qui ne doit PAS être dans le nom de fichier\nCliquez sur \'Filtrer\' pour appliquer le filtre.\n\nUtilisez \'Réinitialiser le Filtre\' pour afficher à nouveau tous les fichiers.'),
            ('help_section_6_text', 'Help dialog', 'Section 6 text', 'nl', 'Er zijn verschillende manieren om muziek af te spelen:\n- Klik op een nummer om het direct af te spelen\n- Klik op een lege plek in de playlist om het eerste nummer te starten\n- Dubbelklik op een nummer om het af te spelen\n\nGebruik de knoppen:\n- Afspelen/Pauzeren: Start of pauzeer het afspelen\n- Stop: Stop het afspelen\n- Vorige: Speel het vorige nummer\n- Volgende: Speel het volgende nummer\n- Favoriet: Markeer het huidige nummer als favoriet\n\nToetsenbord sneltoetsen:\n- Spatiebalk: Afspelen/Pauzeren\n- Pijltje Links/Rechts: Vorige/Volgende nummer\n- F: Favoriet in-/uitschakelen\n- H: Help menu\n- M: Geluid aan/uit\n- +/-: Volume aanpassen\n\nDe voortgangsbalk toont de afspeelpositie en resterende tijd.\nHet volgende nummer wordt automatisch afgespeeld wanneer het huidige nummer eindigt.', 'en', 'There are several ways to play music:\n- Click on a track to play it directly\n- Click on an empty spot in the playlist to start the first track\n- Double click on a track to play it\n\nUse the buttons:\n- Play/Pause: Start or pause playback\n- Stop: Stop playback\n- Previous: Play the previous track\n- Next: Play the next track\n- Favorite: Mark the current track as favorite\n\nKeyboard shortcuts:\n- Spacebar: Play/Pause\n- Left/Right arrows: Previous/Next track\n- F: Toggle favorite\n- H: Help menu\n- M: Mute/Unmute\n- +/-: Adjust volume\n\nThe progress bar shows the playback position and remaining time.\nThe next track is automatically played when the current track ends.', 'de', 'Es gibt verschiedene Möglichkeiten Musik abzuspielen:\n- Klicken Sie auf einen Titel um ihn direkt abzuspielen\n- Klicken Sie auf eine leere Stelle in der Wiedergabeliste um den ersten Titel zu starten\n- Doppelklicken Sie auf einen Titel um ihn abzuspielen\n\nVerwenden Sie die Schaltflächen:\n- Abspielen/Pause: Wiedergabe starten oder pausieren\n- Stopp: Wiedergabe stoppen\n- Zurück: Vorherigen Titel abspielen\n- Weiter: Nächsten Titel abspielen\n- Favorit: Aktuellen Titel als Favorit markieren\n\nTastenkürzel:\n- Leertaste: Abspielen/Pause\n- Pfeiltasten Links/Rechts: Vorheriger/Nächster Titel\n- F: Favorit umschalten\n- H: Hilfe-Menü\n- M: Stummschalten/Stummschaltung aufheben\n- +/-: Lautstärke anpassen\n\nDie Fortschrittsleiste zeigt die Wiedergabeposition und verbleibende Zeit.\nDer nächste Titel wird automatisch abgespielt wenn der aktuelle Titel endet.', 'fr', 'Il y a plusieurs façons de lire de la musique:\n- Cliquez sur un titre pour le lire directement\n- Cliquez sur un endroit vide dans la liste de lecture pour démarrer le premier titre\n- Double-cliquez sur un titre pour le lire\n\nUtilisez les boutons:\n- Lecture/Pause: Démarrer ou mettre en pause la lecture\n- Arrêt: Arrêter la lecture\n- Précédent: Lire le titre précédent\n- Suivant: Lire le titre suivant\n- Favori: Marquer le titre actuel comme favori\n\nRaccourcis clavier:\n- Barre d\'espace: Lecture/Pause\n- Flèches Gauche/Droite: Titre précédent/suivant\n- F: Basculer favori\n- H: Menu d\'aide\n- M: Couper/Rétablir le son\n- +/-: Ajuster le volume\n\nLa barre de progression montre la position de lecture et le temps restant.\nLe titre suivant est automatiquement lu quand le titre actuel se termine.'),
            ('help_section_7_text', 'Help dialog', 'Section 7 text', 'nl', 'De speler houdt bij welke nummers je vaak afspeelt en welke je favoriet zijn:\n\nFavorieten:\n- Klik op de \'Favoriet\' knop of druk op \'F\' om een nummer als favoriet te markeren\n- Favorieten worden getoond in een aparte sectie in de boomweergave\n- Je kunt een nummer opnieuw als favoriet markeren om het te verwijderen\n- Klik op het pijltje (▶) naast \'Favorieten\' om de lijst uit te klappen\n- Klik opnieuw op het pijltje (▼) om de lijst in te klappen\n\nAfspeelgeschiedenis:\n- De laatste 100 afgespeelde nummers worden automatisch bijgehouden\n- De geschiedenis is te vinden in een aparte sectie in de boomweergave\n- Nummers die niet meer bestaan worden automatisch verwijderd\n- Klik op het pijltje (▶) naast \'Afspeelgeschiedenis\' om de lijst uit te klappen\n- Klik opnieuw op het pijltje (▼) om de lijst in te klappen\n\nZowel favorieten als geschiedenis worden automatisch opgeslagen en\nbij het opstarten van het programma weer geladen.\n\nTip: Je kunt de secties in- en uitklappen om de lijst overzichtelijk te houden.', 'en', 'The player keeps track of which tracks you play often and which are your favorites:\n\nFavorites:\n- Click the \'Favorite\' button or press \'F\' to mark a track as favorite\n- Favorites are shown in a separate section in the tree view\n- You can mark a track as favorite again to remove it\n- Click the arrow (▶) next to \'Favorites\' to expand the list\n- Click the arrow (▼) again to collapse the list\n\nPlay History:\n- The last 100 played tracks are automatically tracked\n- The history can be found in a separate section in the tree view\n- Tracks that no longer exist are automatically removed\n- Click the arrow (▶) next to \'Play History\' to expand the list\n- Click the arrow (▼) again to collapse the list\n\nBoth favorites and history are automatically saved and\nloaded when the program starts.\n\nTip: You can expand and collapse sections to keep the list organized.', 'de', 'Der Player verfolgt welche Titel Sie oft abspielen und welche Ihre Favoriten sind:\n\nFavoriten:\n- Klicken Sie auf die \'Favorit\' Schaltfläche oder drücken Sie \'F\' um einen Titel als Favorit zu markieren\n- Favoriten werden in einem separaten Abschnitt in der Baumansicht angezeigt\n- Sie können einen Titel erneut als Favorit markieren um ihn zu entfernen\n- Klicken Sie auf den Pfeil (▶) neben \'Favoriten\' um die Liste zu erweitern\n- Klicken Sie erneut auf den Pfeil (▼) um die Liste zu reduzieren\n\nWiedergabeverlauf:\n- Die letzten 100 abgespielten Titel werden automatisch verfolgt\n- Der Verlauf kann in einem separaten Abschnitt in der Baumansicht gefunden werden\n- Titel die nicht mehr existieren werden automatisch entfernt\n- Klicken Sie auf den Pfeil (▶) neben \'Wiedergabeverlauf\' um die Liste zu erweitern\n- Klicken Sie erneut auf den Pfeil (▼) um die Liste zu reduzieren\n\nSowohl Favoriten als auch Verlauf werden automatisch gespeichert und\nbeim Start des Programms wieder geladen.\n\nTipp: Sie können Abschnitte erweitern und reduzieren um die Liste übersichtlich zu halten.', 'fr', 'Le lecteur garde une trace des titres que vous écoutez souvent et de vos favoris:\n\nFavoris:\n- Cliquez sur le bouton \'Favori\' ou appuyez sur \'F\' pour marquer un titre comme favori\n- Les favoris sont affichés dans une section séparée dans la vue arborescente\n- Vous pouvez marquer un titre comme favori à nouveau pour le supprimer\n- Cliquez sur la flèche (▶) à côté de \'Favoris\' pour étendre la liste\n- Cliquez à nouveau sur la flèche (▼) pour réduire la liste\n\nHistorique de lecture:\n- Les 100 derniers titres lus sont automatiquement suivis\n- L\'historique peut être trouvé dans une section séparée dans la vue arborescente\n- Les titres qui n\'existent plus sont automatiquement supprimés\n- Cliquez sur la flèche (▶) à côté d\'\'Historique de lecture\' pour étendre la liste\n- Cliquez à nouveau sur la flèche (▼) pour réduire la liste\n\nLes favoris et l\'historique sont automatiquement sauvegardés et\nchargés au démarrage du programme.\n\nConseil: Vous pouvez étendre et réduire les sections pour garder la liste organisée.'),
            ('help_section_8_text', 'Help dialog', 'Section 8 text', 'nl', 'Het programma ondersteunt verschillende soorten songteksten:\n\n1. Tekstbestanden (TXT/ODT):\n   - Worden getoond in het rechter paneel\n   - Klik op \'Bewerk Songtekst\' om de tekst te bewerken\n   - Bij het opslaan kun je kiezen tussen TXT of ODT formaat\n\n2. Karaoke bestanden (SRT):\n   - Worden getoond in een apart venster\n   - Klik op \'Toon Karaoke\' om het venster te openen/sluiten\n   - Het venster kan worden versleept naar een gewenste positie\n   - De tekst wordt automatisch gesynchroniseerd met de muziek\n\nBestandsnamen:\n- De songtekst moet dezelfde naam hebben als het muziekbestand\n- Bijvoorbeeld: \'muziek.mp3\' en \'muziek.txt\' of \'muziek.srt\'\n\nKoppelen van bestanden:\n- Bij het bewerken van een songtekst kun je een bestand koppelen\n- Kies het type bestand (TXT, ODT of SRT)\n- Selecteer het bestand dat je wilt koppelen\n- De koppeling wordt onthouden voor volgende keer\n\nJe kunt zowel een tekstbestand als een karaoke bestand tegelijk gebruiken.', 'en', 'The program supports different types of lyrics:\n\n1. Text files (TXT/ODT):\n   - Are displayed in the right panel\n   - Click \'Edit Lyrics\' to edit the text\n   - When saving you can choose between TXT or ODT format\n\n2. Karaoke files (SRT):\n   - Are displayed in a separate window\n   - Click \'Show Karaoke\' to open/close the window\n   - The window can be dragged to a desired position\n   - The text is automatically synchronized with the music\n\nFile names:\n- The lyrics must have the same name as the music file\n- For example: \'music.mp3\' and \'music.txt\' or \'music.srt\'\n\nLinking files:\n- When editing lyrics you can link a file\n- Choose the file type (TXT, ODT or SRT)\n- Select the file you want to link\n- The link is remembered for next time\n\nYou can use both a text file and a karaoke file at the same time.', 'de', 'Das Programm unterstützt verschiedene Arten von Songtexten:\n\n1. Textdateien (TXT/ODT):\n   - Werden im rechten Bereich angezeigt\n   - Klicken Sie auf \'Songtext Bearbeiten\' um den Text zu bearbeiten\n   - Beim Speichern können Sie zwischen TXT oder ODT Format wählen\n\n2. Karaoke-Dateien (SRT):\n   - Werden in einem separaten Fenster angezeigt\n   - Klicken Sie auf \'Karaoke Anzeigen\' um das Fenster zu öffnen/schließen\n   - Das Fenster kann an eine gewünschte Position gezogen werden\n   - Der Text wird automatisch mit der Musik synchronisiert\n\nDateinamen:\n- Der Songtext muss den gleichen Namen wie die Musikdatei haben\n- Zum Beispiel: \'musik.mp3\' und \'musik.txt\' oder \'musik.srt\'\n\nDateien verknüpfen:\n- Beim Bearbeiten eines Songtexts können Sie eine Datei verknüpfen\n- Wählen Sie den Dateityp (TXT, ODT oder SRT)\n- Wählen Sie die Datei aus die Sie verknüpfen möchten\n- Die Verknüpfung wird für das nächste Mal gespeichert\n\nSie können sowohl eine Textdatei als auch eine Karaoke-Datei gleichzeitig verwenden.', 'fr', 'Le programme prend en charge différents types de paroles:\n\n1. Fichiers texte (TXT/ODT):\n   - Sont affichés dans le panneau de droite\n   - Cliquez sur \'Modifier les Paroles\' pour éditer le texte\n   - Lors de la sauvegarde vous pouvez choisir entre les formats TXT ou ODT\n\n2. Fichiers karaoké (SRT):\n   - Sont affichés dans une fenêtre séparée\n   - Cliquez sur \'Afficher le Karaoké\' pour ouvrir/fermer la fenêtre\n   - La fenêtre peut être déplacée vers une position souhaitée\n   - Le texte est automatiquement synchronisé avec la musique\n\nNoms de fichiers:\n- Les paroles doivent avoir le même nom que le fichier musical\n- Par exemple: \'musique.mp3\' et \'musique.txt\' ou \'musique.srt\'\n\nLiaison de fichiers:\n- Lors de l\'édition des paroles vous pouvez lier un fichier\n- Choisissez le type de fichier (TXT, ODT ou SRT)\n- Sélectionnez le fichier que vous voulez lier\n- Le lien est mémorisé pour la prochaine fois\n\nVous pouvez utiliser à la fois un fichier texte et un fichier karaoké.'),
            ('help_section_9_text', 'Help dialog', 'Section 9 text', 'nl', 'Na het filteren kun je een playlist opslaan:\n- Klik op \'Save Filtered List\'\n- Geef de playlist een naam\n- Kies zelf waar je de playlist wilt opslaan\n- De gekozen locatie wordt onthouden voor volgende keer\n\nOm een playlist te laden:\n- Selecteer de playlist uit de dropdown\n- Klik op \'Load Playlist\'\n\nOm een nummer uit de playlist te verwijderen:\n- Rechtsklik op het nummer\n- Kies \'Verwijder uit playlist\'\n- Bevestig de verwijdering', 'en', 'After filtering you can save a playlist:\n- Click \'Save Filtered List\'\n- Give the playlist a name\n- Choose where you want to save the playlist\n- The chosen location is remembered for next time\n\nTo load a playlist:\n- Select the playlist from the dropdown\n- Click \'Load Playlist\'\n\nTo remove a track from the playlist:\n- Right click on the track\n- Choose \'Remove from playlist\'\n- Confirm the removal', 'de', 'Nach dem Filtern können Sie eine Wiedergabeliste speichern:\n- Klicken Sie auf \'Gefilterte Liste Speichern\'\n- Geben Sie der Wiedergabeliste einen Namen\n- Wählen Sie selbst wo Sie die Wiedergabeliste speichern möchten\n- Der gewählte Ort wird für das nächste Mal gespeichert\n\nUm eine Wiedergabeliste zu laden:\n- Wählen Sie die Wiedergabeliste aus der Dropdown-Liste\n- Klicken Sie auf \'Wiedergabeliste Laden\'\n\nUm einen Titel aus der Wiedergabeliste zu entfernen:\n- Rechtsklick auf den Titel\n- Wählen Sie \'Aus Wiedergabeliste Entfernen\'\n- Bestätigen Sie die Entfernung', 'fr', 'Après le filtrage vous pouvez sauvegarder une liste de lecture:\n- Cliquez sur \'Sauvegarder la Liste Filtrée\'\n- Donnez un nom à la liste de lecture\n- Choisissez où vous voulez sauvegarder la liste de lecture\n- L\'emplacement choisi est mémorisé pour la prochaine fois\n\nPour charger une liste de lecture:\n- Sélectionnez la liste de lecture dans la liste déroulante\n- Cliquez sur \'Charger la Liste de Lecture\'\n\nPour supprimer un titre de la liste de lecture:\n- Clic droit sur le titre\n- Choisissez \'Supprimer de la Liste de Lecture\'\n- Confirmez la suppression'),
            ('help_section_10_text', 'Help dialog', 'Section 10 text', 'nl', 'Het programma ondersteunt de volgende bestandstypen:\n\nAudio bestanden:\n- .mp3\n- .wav\n- .ogg\n- .flac\n- .m4a\n- .aac\n\nSongtekst bestanden:\n- .txt (gewone tekst)\n- .odt (OpenDocument tekst)\n- .srt (karaoke/ondertiteling)\n\nHet aantal bestanden per type wordt getoond:\n- In de boomweergave bij elke schijf\n- In de statusbalk voor alle schijven samen', 'en', 'The program supports the following file types:\n\nAudio files:\n- .mp3\n- .wav\n- .ogg\n- .flac\n- .m4a\n- .aac\n\nLyrics files:\n- .txt (plain text)\n- .odt (OpenDocument text)\n- .srt (karaoke/subtitles)\n\nThe number of files per type is shown:\n- In the tree view for each drive\n- In the status bar for all drives together', 'de', 'Das Programm unterstützt die folgenden Dateitypen:\n\nAudiodateien:\n- .mp3\n- .wav\n- .ogg\n- .flac\n- .m4a\n- .aac\n\nSongtext-Dateien:\n- .txt (einfacher Text)\n- .odt (OpenDocument Text)\n- .srt (Karaoke/Untertitel)\n\nDie Anzahl der Dateien pro Typ wird angezeigt:\n- In der Baumansicht für jedes Laufwerk\n- In der Statusleiste für alle Laufwerke zusammen', 'fr', 'Le programme prend en charge les types de fichiers suivants:\n\nFichiers audio:\n- .mp3\n- .wav\n- .ogg\n- .flac\n- .m4a\n- .aac\n\nFichiers de paroles:\n- .txt (texte simple)\n- .odt (texte OpenDocument)\n- .srt (karaoké/sous-titres)\n\nLe nombre de fichiers par type est affiché:\n- Dans la vue arborescente pour chaque lecteur\n- Dans la barre d\'état pour tous les lecteurs ensemble'),
            ('help_section_11_text', 'Help dialog', 'Section 11 text', 'nl', 'Het programma onthoudt de volgende instellingen:\n- De laatst gebruikte map voor songteksten\n- De laatst gebruikte map voor playlists\n- De koppeling tussen muziekbestanden en songteksten\n- De weergave-instellingen (pad of bestandsnaam)\n- De lijst met gescande schijven en bestanden\n- Je favoriete nummers\n- Je afspeelgeschiedenis\n\nDeze instellingen worden automatisch opgeslagen en\nbij het opstarten van het programma weer geladen.', 'en', 'The program remembers the following settings:\n- The last used folder for lyrics\n- The last used folder for playlists\n- The link between music files and lyrics\n- The display settings (path or filename)\n- The list of scanned drives and files\n- Your favorite tracks\n- Your play history\n\nThese settings are automatically saved and\nloaded when the program starts.', 'de', 'Das Programm merkt sich die folgenden Einstellungen:\n- Den zuletzt verwendeten Ordner für Songtexte\n- Den zuletzt verwendeten Ordner für Wiedergabelisten\n- Die Verknüpfung zwischen Musikdateien und Songtexten\n- Die Anzeigeeinstellungen (Pfad oder Dateiname)\n- Die Liste der gescannten Laufwerke und Dateien\n- Ihre Lieblingstitel\n- Ihren Wiedergabeverlauf\n\nDiese Einstellungen werden automatisch gespeichert und\nbeim Start des Programms wieder geladen.', 'fr', 'Le programme mémorise les paramètres suivants:\n- Le dernier dossier utilisé pour les paroles\n- Le dernier dossier utilisé pour les listes de lecture\n- Le lien entre les fichiers musicaux et les paroles\n- Les paramètres d\'affichage (chemin ou nom de fichier)\n- La liste des lecteurs et fichiers scannés\n- Vos titres favoris\n- Votre historique de lecture\n\nCes paramètres sont automatiquement sauvegardés et\nchargés au démarrage du programme.'),
            
            # Additional missing translations
            ('favorite_added', 'Status messages', 'Favorite added message', 'nl', 'Toegevoegd aan favorieten', 'en', 'Added to favorites', 'de', 'Zu Favoriten hinzugefügt', 'fr', 'Ajouté aux favoris'),
            ('favorite_removed', 'Status messages', 'Favorite removed message', 'nl', 'Verwijderd uit favorieten', 'en', 'Removed from favorites', 'de', 'Aus Favoriten entfernt', 'fr', 'Supprimé des favoris'),
            ('unknown_artist', 'Metadata', 'Unknown artist fallback', 'nl', 'Onbekend', 'en', 'Unknown', 'de', 'Unbekannt', 'fr', 'Inconnu'),
            ('unknown_album', 'Metadata', 'Unknown album fallback', 'nl', 'Onbekend', 'en', 'Unknown', 'de', 'Unbekannt', 'fr', 'Inconnu'),
            ('unknown_title', 'Metadata', 'Unknown title fallback', 'nl', 'Onbekend', 'en', 'Unknown', 'de', 'Unbekannt', 'fr', 'Inconnu'),
            
            # Lyrics dialog translations
            ('lyrics_title', 'Lyrics dialog', 'Lyrics dialog title', 'nl', 'Songtekst', 'en', 'Lyrics', 'de', 'Songtext', 'fr', 'Paroles'),
            ('save_button', 'Lyrics dialog', 'Save button text', 'nl', 'Opslaan', 'en', 'Save', 'de', 'Speichern', 'fr', 'Sauvegarder'),
            
            # Lyrics mapping dialog translations
            ('lyrics_mapping_title', 'Lyrics mapping dialog', 'Lyrics mapping dialog title', 'nl', 'Songtekst Koppelen', 'en', 'Link Lyrics', 'de', 'Songtext Verknüpfen', 'fr', 'Lier les Paroles'),
            ('music_file_label', 'Lyrics mapping dialog', 'Music file label', 'nl', 'Muziekbestand: {file}', 'en', 'Music file: {file}', 'de', 'Musikdatei: {file}', 'fr', 'Fichier musical: {file}'),
            ('text_lyrics_group', 'Lyrics mapping dialog', 'Text lyrics group title', 'nl', 'Songtekst (TXT/ODT)', 'en', 'Lyrics (TXT/ODT)', 'de', 'Songtext (TXT/ODT)', 'fr', 'Paroles (TXT/ODT)'),
            ('karaoke_group', 'Lyrics mapping dialog', 'Karaoke group title', 'nl', 'Karaoke (SRT)', 'en', 'Karaoke (SRT)', 'de', 'Karaoke (SRT)', 'fr', 'Karaoké (SRT)'),
            ('browse_button', 'Lyrics mapping dialog', 'Browse button text', 'nl', 'Bladeren', 'en', 'Browse', 'de', 'Durchsuchen', 'fr', 'Parcourir'),
            ('clear_button', 'Lyrics mapping dialog', 'Clear button text', 'nl', 'Wissen', 'en', 'Clear', 'de', 'Löschen', 'fr', 'Effacer'),
            ('select_lyrics', 'Lyrics mapping dialog', 'Select lyrics dialog title', 'nl', 'Selecteer Songtekst', 'en', 'Select Lyrics', 'de', 'Songtext Auswählen', 'fr', 'Sélectionner les Paroles'),
            ('select_karaoke', 'Lyrics mapping dialog', 'Select karaoke dialog title', 'nl', 'Selecteer Karaoke Bestand', 'en', 'Select Karaoke File', 'de', 'Karaoke-Datei Auswählen', 'fr', 'Sélectionner le Fichier Karaoké'),
            
            # Karaoke dialog translations
            ('karaoke_title', 'Karaoke dialog', 'Karaoke dialog title', 'nl', 'Songtekst Karaoke', 'en', 'Lyrics Karaoke', 'de', 'Songtext Karaoke', 'fr', 'Paroles Karaoké'),
            ('fullscreen_button', 'Karaoke dialog', 'Fullscreen button text', 'nl', 'Volledig scherm', 'en', 'Fullscreen', 'de', 'Vollbild', 'fr', 'Plein écran'),
            ('normal_screen_button', 'Karaoke dialog', 'Normal screen button text', 'nl', 'Normaal scherm', 'en', 'Normal screen', 'de', 'Normales Fenster', 'fr', 'Écran normal'),
            ('close_karaoke', 'Karaoke dialog', 'Close karaoke button text', 'nl', 'Sluiten', 'en', 'Close', 'de', 'Schließen', 'fr', 'Fermer'),
            
            # Scanning dialog translations
            ('scanning_title', 'Scanning dialog', 'Scanning dialog title', 'nl', 'Scannen', 'en', 'Scanning', 'de', 'Scannen', 'fr', 'Scan'),
            ('scanning_message', 'Scanning dialog', 'Scanning message', 'nl', 'Schijf {drive} aan het scannen, even geduld...', 'en', 'Scanning drive {drive}, please wait...', 'de', 'Laufwerk {drive} wird gescannt, bitte warten...', 'fr', 'Scan du lecteur {drive}, veuillez patienter...'),
        ]
        
        for translation in translations:
            function_key, category, description = translation[0], translation[1], translation[2]
            
            # Check if translation already exists
            cursor.execute('SELECT function_key FROM translations WHERE function_key = ?', (function_key,))
            if not cursor.fetchone():
                # Insert new translation
                cursor.execute('''
                    INSERT INTO translations (function_key, category, description, nl, en, de, fr)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (function_key, category, description, translation[4], translation[6], translation[8], translation[10]))
    
    def get_text(self, function_key: str, language: str = 'nl', **kwargs) -> str:
        """Get translated text for a function key and language"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get translation for the specified language
            cursor.execute(f'SELECT {language} FROM translations WHERE function_key = ?', (function_key,))
            result = cursor.fetchone()
            
            if result and result[0]:
                text = result[0]
                
                # Format the text with provided kwargs
                if kwargs:
                    try:
                        text = text.format(**kwargs)
                    except (KeyError, ValueError):
                        # If formatting fails, return the text as is
                        pass
                
                return text
            else:
                # Fallback to English if translation not found
                if language != 'en':
                    return self.get_text(function_key, 'en', **kwargs)
                else:
                    # If not found in English either, return the key itself
                    return function_key
                    
        except sqlite3.OperationalError:
            # Language column doesn't exist, fallback to English
            if language != 'en':
                return self.get_text(function_key, 'en', **kwargs)
            else:
                return function_key
        finally:
            conn.close()
    
    def get_language_name(self, language_code: str) -> str:
        """Get the display name for a language code"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT name FROM languages WHERE code = ?', (language_code,))
            result = cursor.fetchone()
            return result[0] if result else language_code
        finally:
            conn.close()
    
    def get_available_languages(self) -> List[str]:
        """Get list of available language codes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT code FROM languages WHERE is_active = 1 ORDER BY code')
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def add_language(self, language_code: str, language_name: str, translations: Dict[str, str]):
        """Add a new language to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Add language to languages table
            cursor.execute('''
                INSERT OR REPLACE INTO languages (code, name, is_active)
                VALUES (?, ?, 1)
            ''', (language_code, language_name))
            
            # Add language column to translations table
            try:
                cursor.execute(f'ALTER TABLE translations ADD COLUMN {language_code} TEXT')
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            # Add translations
            for function_key, translation in translations.items():
                cursor.execute(f'''
                    UPDATE translations SET {language_code} = ?
                    WHERE function_key = ?
                ''', (translation, function_key))
            
            conn.commit()
        finally:
            conn.close()
    
    def update_translation(self, function_key: str, language: str, translation: str):
        """Update a specific translation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                UPDATE translations SET {language} = ?
                WHERE function_key = ?
            ''', (translation, function_key))
            conn.commit()
        finally:
            conn.close()
    
    def get_all_translations(self, language: str) -> Dict[str, str]:
        """Get all translations for a specific language"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT function_key, {language} FROM translations')
            return {row[0]: row[1] for row in cursor.fetchall() if row[1]}
        finally:
            conn.close()

# Global database instance
_language_db = None

def get_language_db() -> LanguageDatabase:
    """Get the global language database instance"""
    global _language_db
    if _language_db is None:
        _language_db = LanguageDatabase()
    return _language_db

# Convenience functions that match the old API
def get_text(key: str, language: str = 'nl', **kwargs) -> str:
    """Get text for a given key and language, with optional formatting"""
    return get_language_db().get_text(key, language, **kwargs)

def get_language_name(language_code: str) -> str:
    """Get the display name for a language code"""
    return get_language_db().get_language_name(language_code)

def get_available_languages() -> List[str]:
    """Get list of available language codes"""
    return get_language_db().get_available_languages()

def add_language(language_code: str, language_name: str, translations: Dict[str, str]):
    """Add a new language to the system"""
    get_language_db().add_language(language_code, language_name, translations) 