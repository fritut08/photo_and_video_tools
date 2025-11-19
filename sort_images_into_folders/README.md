# sort_images_into_folders

Python script to reorganize image files into `YYYY-MM-DD` subfolders based on the `EXIF DateTimeOriginal` tag.

## Project layout

- `sort_images_into_folders.py` — main script (Tk folder picker + organizer)
- `requirements.txt` — Python dependencies
- `run.ps1` — convenience PowerShell helper that creates/activates a venv, installs deps, runs the script, then deactivates

## Prerequisites

- Python 3.9+ with Tkinter available (for the folder picker GUI)
- Ability to install packages listed in `requirements.txt`

## Supported extensions

Currently: `.jpg`, `.JPG`, `.arw`, `.ARW` (case-insensitive match applied internally).

## Run

Direct (assuming dependencies already installed in current interpreter):

```powershell
python sort_images_into_folders.py
```

Or use the helper which manages an isolated virtual environment automatically:

```powershell
./run.ps1
```

## What it does

- Prompts you to select a directory containing image files
- Reads EXIF `DateTimeOriginal` for each supported file
- Creates subfolders named `YYYY-MM-DD` inside the selected directory as needed
- Moves files into the matching date folder (same filename preserved)
- Skips files lacking EXIF `DateTimeOriginal` (leaves them where they are) and reports them at the end
- Shows a live progress bar with per-file status lines (alive-progress)
