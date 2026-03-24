# YouVideo Downloader
YouVideo Downloader is a clean, professional desktop app built with Python + Tkinter for downloading YouTube videos. It uses `yt-dlp` behind the scenes, shows live progress and speed, and saves files to your Downloads folder.

**Features**
- Clean, modern UI with a light theme
- 720p max video quality (best available up to 720p)
- Live download progress, size, and speed
- Auto-save to your system Downloads folder

**Requirements**
- Python 3.10+ (3.13 is fine)
- Tkinter (system package on Linux)
- Optional: `ffmpeg` for best audio+video merging

**Install and Run**
1. Clone the repo:
```bash
git clone https://github.com/Samuelatsyatsya/you-video.git
cd you-video
```
2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
. .venv/bin/activate
```
3. Install Python dependencies:
```bash
pip install -r requirements.txt
```
4. Run the app:
```bash
python YouVideo.py
```

**Linux Notes**
If you see `ModuleNotFoundError: No module named 'tkinter'`, install Tkinter:
```bash
sudo apt-get update && sudo apt-get install -y python3-tk
```
To enable best audio+video merge (MP4 output), install `ffmpeg`:
```bash
sudo apt-get install -y ffmpeg
```

**Quality Behavior**
The app requests 720p max:
- If 720p is available, it downloads that.
- If not, it falls back to the best available quality under 720p.
- When `ffmpeg` is installed, the app can merge best video + best audio into MP4.

**Troubleshooting**
- If downloads fail, try another link to confirm the video is available.
- If speed shows 0 briefly, it will update as `yt-dlp` reports new stats.

---
Created by @little_things  
Inspired by MRR KORK, STREET, DR ASSEM, BEN RICHH
