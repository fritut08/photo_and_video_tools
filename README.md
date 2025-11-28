# Photo and Video Tools

A collection of Python utilities for managing and processing photos and videos.

## Quick Start

**Option 1: Auto-setup script (recommended)**

```powershell
.\run.ps1
```

This PowerShell script automatically creates the virtual environment, installs dependencies, and runs the launcher which will let the user select the tool.
The tool then either performs the task itself or takes care of preparing and calling the Docker container which performs the task.

**Option 2: Manual setup**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python launcher.py
```

## Architecture

This repository uses a **shared container architecture** to reduce duplication:

- **`containers/`** - Shared Docker base images (exiftool, ffmpeg, etc.)
- **`tools/`** - Individual tool implementations with their own scripts
- **`launcher.py`** - Central menu-based launcher for all tools

Most tools use Docker containers with base environments mounted dynamically at runtime. Tool-specific scripts are located in their respective `tools/*/container/` directories.

## Available Tools

### 1. Sort Images into Folders
Organize images by date into year/month folder structure.

### 2. Remove Unmatched RAW Files
Remove RAW files (.arw or .dng) that don't have corresponding JPEG counterparts.

### 3. Add Timezone Information
Add custom timezone to photos' tags

### 4. Shift Time and Timezone
Adjust photo time and timezone tags. Useful when camera was set to wrong timezone.

### 5. Copy Geotags from XMP to JPEG files
Copy GPS data from XMP sidecar files to JPEG files.

### 6. Merge SRT with MP4
Merge SRT subtitles files directly into MP4 video files as subtitle tracks.

### 7. Add Geotag to DJI Drone Video
Extract GPS coordinates from DJI drone SRT files and embed into MP4 videos.

## Prerequisites

- **Python 3.10+** with Tkinter (for GUI folder pickers)
- **Docker Desktop** (for containerized tools)

## Dependencies

Python dependencies are managed at the repository level in `requirements.txt`:

Install with: `pip install -r requirements.txt`

## Acknowledgments

This code was written with assistance from AI tools ChatGPT and GitHub Copilot.

## License

See the LICENSE file and individual tool directories for licensing information.
