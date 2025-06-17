# HAL's Music Player

An advanced music player with PyQt6 GUI, multi-language support, karaoke functionality and comprehensive playlist management.

## 🎵 Features

- **Multi-language Support**: Dutch, English, German and French
- **Karaoke Display**: SRT file support with synchronized text
- **Playlist Management**: Create, manage and save playlists
- **Favorites & History**: Automatic tracking of favorites and playback history
- **Lyrics Support**: TXT, ODT and SRT files
- **Drive Scanning**: Scan network drives and local disks
- **File Filtering**: Advanced filtering options for files
- **Dark Theme**: Modern dark theme
- **Keyboard Shortcuts**: Full keyboard support

## 📋 Requirements

- Python 3.8 or higher
- PyQt6
- pygame
- mutagen
- odfpy

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/hals-music-player.git
   cd hals-music-player
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application:**
   ```bash
   python music_player.py
   ```

## 🎮 Usage

### Basic Controls
- **Spacebar**: Play/Pause
- **Left/Right Arrows**: Previous/Next track
- **F**: Toggle favorite
- **H**: Help menu
- **L**: Switch language
- **M**: Mute/Unmute
- **+/-**: Adjust volume
- **S**: Stop
- **V**: Toggle between filename and path display

### Scanning Drives
1. Select a drive from the dropdown
2. Click "Scan Selected Drive"
3. Wait for scanning to complete
4. Files are automatically loaded

### Playlists
- **Save**: Filter files and click "Save Filtered List"
- **Load**: Select playlist from dropdown and click "Load Playlist"
- **Edit**: Right-click on tracks for context menu

### Lyrics
- **TXT/ODT**: Displayed in the right panel
- **SRT**: Open karaoke window with "Show Karaoke"
- **Link**: Use "Edit Lyrics" to link files

## 🌍 Language Support

The application automatically supports:
- **Dutch** (default)
- **English**
- **German**
- **French**

Use the 🌐 button or press **L** to switch languages.

## 📁 File Structure

```
hals-music-player/
├── music_player.py          # Main program
├── languages_db.py          # Language system
├── requirements.txt         # Dependencies
├── README.md               # This documentation
├── .gitignore              # Git ignore rules
├── lyrics/                 # Lyrics (will be created)
├── playlists/              # Playlists (will be created)
└── help_images/            # Help images (optional)
```

## 🔧 Configuration

The application automatically saves:
- Last used folders
- Favorites and playback history
- Language preference
- Lyrics file links
- Display settings

## 🎵 Supported File Formats

### Audio
- MP3, WAV, OGG, FLAC, M4A, AAC

### Lyrics
- TXT (plain text)
- ODT (OpenDocument text)
- SRT (karaoke/subtitles)

### Creating SRT Files
SRT_Maker is a separate program to create SRT files for the Karaoke section.

- Load a lyrics file (TXT or ODT) or copy the lyrics into the text section
- Clean up the text: Only the title and lyrics. You can go to a line and click delete.
- Link the audio file of the lyrics
- Start the session.
- Mouse click is time start, hold mouse down until the line is played.
- Release mouse is time stop for that line.
- At the end, the function becomes available to give the SRT file a name and save it.

## 🐛 Troubleshooting

### Database Issues
If there are problems with the language database:
- Delete `languages.db` (will be automatically recreated)
- Restart the application

### Audio Issues
- Check if pygame is correctly installed
- Make sure audio drivers are up-to-date

### PyQt6 Issues
- Reinstall PyQt6: `pip install --force-reinstall PyQt6`
- Check Python version (3.8+ required)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report issues
- Submit feature requests
- Make pull requests

## 📄 License

This project is released under the MIT license.

## 🙏 Credits

- **PyQt6**: Qt framework for Python
- **pygame**: Audio processing
- **mutagen**: Audio metadata handling
- **odfpy**: OpenDocument format support

---

**Made with ❤️ by HAL** 
