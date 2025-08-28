# 🎵 Lofi Channel - Automated Music Mix Generator

An automated system for creating beautiful lofi hip-hop playlists with custom audio mixing, video generation, and YouTube-ready content production.

## 🌟 What It Does

This project automatically generates relaxing lofi music mixes by:
- Combining individual song files into seamless playlists with crossfade transitions
- Adding producer tags and custom audio effects
- Converting audio to video format with visualizations
- Generating YouTube descriptions with timestamps and hashtags
- Creating lofi style content at scale

## 🚀 Key Features

- **Automated Audio Stitching**: Combines multiple tracks with customizable crossfade transitions and silence gaps
- **Producer Tag Integration**: Adds intro tags to brand your content
- **Timestamp Generation**: Creates accurate tracklists with timestamps for easy navigation
- **Video Conversion**: Converts audio mixes to MP4 format for video platforms
- **Description Generation**: Automatically creates YouTube-ready descriptions with hashtags
- **Multiple Genres**: Supports both lofi and DNB playlist generation
- **High Quality Output**: 320kbps MP3 encoding for professional audio quality

## 📁 Project Structure

```
lofi-channel/
├── services/           # Core functionality
│   ├── main.py        # Main orchestration script
│   ├── audio_stitcher.py   # FFmpeg-based audio mixing
│   ├── mp3_to_mp4.py      # Video conversion utilities
│   └── musicgpt_api.py  # Deprecated API logic for MusicGPT
|   └── stability_api.py  # Deprecated API logic for Stable Audio
|   └── description_generator.py  # YouTube description creation
├── songs/             # Individual track files
├── playlists/         # Generated audio/video mixes
├── descriptions/      # Generated YouTube descriptions
├── producer_tags/     # Intro/outro audio tags
├── thumbnails/        # Video thumbnail images
└── *.json            # Playlist configuration data
```

## 🛠️ Prerequisites

- **Python 3.7+**
- **FFmpeg** (for audio processing)
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: Download from https://ffmpeg.org/

## ⚡ Quick Start

1. **Add your songs** to the `songs/` directory (MP3, WAV, M4A, FLAC, AAC supported). Previously the API calls would send the files here, but the performance of those songs wasn't all that great, so Suno was used instead manually (as they have no official API at time of development)

2. **Configure your playlist** in `lofi_playlist_data.json`:
   ```json
   {
     "title": "Your Playlist Title",
     "description": "Your playlist description",
     "song_names": ["Song 1", "Song 2", "Song 3"]
   }
   ```

3. **Run the generator**:
   ```bash
   cd services
   python main.py
   ```

4. **Find your content** in the `playlists/` directory:
   - Mixed audio file (`.mp3`)
   - Video file (`.mp4`) 
   - Tracklist (`.txt`)
   - YouTube description (`.txt`)

## 🎛️ Customization Options

### Audio Settings
- **Crossfade Duration**: Adjust fade transitions between tracks
- **Silence Gaps**: Add breathing room between songs
- **Audio Quality**: 320kbps MP3 encoding by default

### Output Formats
- High-quality MP3 audio files
- MP4 video files for YouTube/streaming
- Formatted descriptions with hashtags
- Timestamp tracklists for navigation

---

## 🎬 YouTube Channel

<!-- YouTube Channel Information Section -->
### 📺 Official Channel
**Channel Name:** Naturalist.mp3
**Link:** [\[Naturalist.mp3 Channel\]](https://www.youtube.com/channel/UClIOcu7tgrkgM_aaDdTZlpw)

### 📈 Channel Stats
- **Subscribers:** 394
- **Total Views:** 2.5k 
- **Videos:** 22

### 🔔 Subscribe for:
- ✨ New lofi mixes daily
- 🌙 Study & relaxation playlists  
- 🎧 High-quality audio content
- 🌊 Calming nature-themed beats

## 🛠️ Other Tools & Future Considerations

### 🔧 Tools
- **Figma:** Used to design/edit the thumbnails
- **Audacity:** For tweaks to most of the AI generated content and mixing the producer tags
- **Unsplash:** For sourcing the images used in the thumbnails

### 🔜 Future Considerations
- **Eleven Labs API:** May have more consistent performance similar to Sunos model but has official API