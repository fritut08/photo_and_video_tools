# correct_timezone

Host launcher + Dockerized exiftool workflow to correct timestamps of photo files (`.arw`, `.jpg`, `.jpeg`) if the photos were taken with a camera that was not set to the correct timezone.

## Project layout

- `Dockerfile` — builds the runtime image with exiftool
- `launcher.py` — host-side launcher with a Tk folder picker
- `container/correct_timezone.py` — script executed inside the container
- `container/requirements.txt` — Python deps for the container

## Prerequisites

- Python 3.9+ with Tkinter available (for the folder picker GUI)
- Docker Engine capable of running Linux containers (e.g., Docker Desktop)

## Run

Use the launcher to pick a folder and run the container:

```powershell
python launcher.py
```

What it does:
- Prompts for a folder containing image files
- Asks for a timezone difference (e.g., -3, 5.5)
- Mounts the folder to `/work` in the container
- Adjusts date/time and timezone offset metadata using exiftool

## Example

Example: Photos were taken in timezone UTC-2 but the camera was set to UTC+1. Thus, pictures taken at 14:00 local time will have an incorrect timestamp of 17:00. If `-3` is entered as the timezone difference, this script will correct the metadata as necessary. This includes not only the time but also the date and timezone parameters of the files' exif data.
