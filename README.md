# HAL's Music Player

Een geavanceerde muziekspeler met PyQt6 GUI, ondersteuning voor meerdere talen, karaoke functionaliteit en uitgebreide playlist management.

## 🎵 Functies

- **Multi-language Support**: Nederlands, Engels, Duits en Frans
- **Karaoke Display**: SRT bestanden ondersteuning met gesynchroniseerde tekst
- **Playlist Management**: Maak, beheer en sla playlists op
- **Favorites & History**: Automatische bijhouding van favorieten en afspeelgeschiedenis
- **Lyrics Support**: TXT, ODT en SRT bestanden
- **Drive Scanning**: Scan netwerkstations en lokale schijven
- **File Filtering**: Geavanceerde filteropties voor bestanden
- **Dark Theme**: Modern donker thema
- **Keyboard Shortcuts**: Volledige toetsenbord ondersteuning

## 📋 Vereisten

- Python 3.8 of hoger
- PyQt6
- pygame
- mutagen
- odfpy

## 🚀 Installatie

1. **Clone de repository:**
   ```bash
   git clone https://github.com/yourusername/hals-music-player.git
   cd hals-music-player
   ```

2. **Installeer dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start de applicatie:**
   ```bash
   python music_player.py
   ```

## 🎮 Gebruik

### Basis Bediening
- **Spatiebalk**: Afspelen/Pauzeren
- **Pijltjes Links/Rechts**: Vorige/Volgende nummer
- **F**: Favoriet in-/uitschakelen
- **H**: Help menu
- **L**: Taal wisselen
- **M**: Geluid aan/uit
- **+/-**: Volume aanpassen
- **S**: Stoppen
- **V**: Wisselen tussen bestandsnaam en pad weergave

### Schijven Scannen
1. Selecteer een schijf uit de dropdown
2. Klik op "Scan Selected Drive"
3. Wacht tot het scannen voltooid is
4. Bestanden worden automatisch geladen

### Playlists
- **Opslaan**: Filter bestanden en klik "Save Filtered List"
- **Laden**: Selecteer playlist uit dropdown en klik "Load Playlist"
- **Bewerken**: Rechtsklik op nummers voor context menu

### Songteksten
- **TXT/ODT**: Worden getoond in het rechter paneel
- **SRT**: Open karaoke venster met "Show Karaoke"
- **Koppelen**: Gebruik "Edit Lyrics" om bestanden te koppelen

## 🌍 Taal Ondersteuning

De applicatie ondersteunt automatisch:
- **Nederlands** (standaard)
- **English**
- **Deutsch**
- **Français**

Gebruik de 🌐 knop of druk op **L** om van taal te wisselen.

## 📁 Bestandsstructuur

```
hals-music-player/
├── music_player.py          # Hoofdprogramma
├── languages_db.py          # Taalsysteem
├── requirements.txt         # Dependencies
├── README.md               # Deze documentatie
├── .gitignore              # Git ignore regels
├── lyrics/                 # Songteksten (wordt aangemaakt)
├── playlists/              # Playlists (wordt aangemaakt)
└── help_images/            # Help afbeeldingen (optioneel)
```

## 🔧 Configuratie

De applicatie slaat automatisch op:
- Laatst gebruikte mappen
- Favorieten en afspeelgeschiedenis
- Taal voorkeur
- Songtekst koppelingen
- Weergave instellingen

## 🎵 Ondersteunde Bestandsformaten

### Audio
- MP3, WAV, OGG, FLAC, M4A, AAC

### Songteksten
- TXT (gewone tekst)
- ODT (OpenDocument tekst)
- SRT (karaoke/ondertiteling)

  
### SRT-file maken
SRT_Maker is een apart programma om SRT-files te maken voor het Karaoke gedeelte.

- Laad een songtekst (TXT of ODT) of kopieer de songtext in het tekst gedeelte
- Schoon de text op: Alleen de titel en de songtext. Je kunt op een regel gaan staan en verwijderen klikken.
- Koppel de audio-file van de songtekst
- Start de sessie.
- Muis klik is tijd start, muis ingedrukt houden tot de regel gespeeld is.
- Muis loslaten is tijd stop van die regel.
-  Aan het eind komt de functie vrij om de SRT-file een naam te geven en op te slaan.



## 🐛 Problemen Oplossen

### Database Problemen
Als er problemen zijn met de taal database:
- Verwijder `languages.db` (wordt automatisch opnieuw aangemaakt)
- Start de applicatie opnieuw

### Audio Problemen
- Controleer of pygame correct is geïnstalleerd
- Zorg dat audio drivers up-to-date zijn

### PyQt6 Problemen
- Installeer PyQt6 opnieuw: `pip install --force-reinstall PyQt6`
- Controleer Python versie (3.8+ vereist)

## 🤝 Bijdragen

Bijdragen zijn welkom! Voel je vrij om:
- Issues te melden
- Feature requests in te dienen
- Pull requests te maken

## 📄 Licentie

Dit project is vrijgegeven onder de MIT licentie.

## 🙏 Credits

- **PyQt6**: Qt framework voor Python
- **pygame**: Audio processing
- **mutagen**: Audio metadata handling
- **odfpy**: OpenDocument format support

---

**Gemaakt met ❤️ door HAL** 
