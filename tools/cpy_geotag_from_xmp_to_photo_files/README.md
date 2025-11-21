# cpy_geotag_from_xmp_to_photo_files

Host launcher + Dockerized exiftool workflow to copy geotag information from sidecar `.xmp` files into matching `.jpeg`/`.jpg` files.

## Project layout

- `Dockerfile` — builds the runtime image with exiftool and downloads `xmp2exif.args`
- `launcher.py` — host-side launcher with a Tk folder picker
- `container/cpy_geotag_from_xmp_to_photo_files.py` — script executed inside the container
- `container/requirements.txt` — Python deps for the container (alive-progress)

## Prerequisites

- Python 3.9+ with Tkinter available (for the folder picker GUI)
- Docker Engine capable of running Linux containers (e.g., Docker Desktop)

## Run

Use the launcher to pick a folder and run the container:

```powershell
python launcher.py
```

What it does:
- Prompts for a folder containing `.xmp` + `.jpg`/`.jpeg` pairs
- Downloads and uses `xmp2exif.args` inside the image (no host setup needed)
- Writes updated JPEG copies to `<selected>/photos_with_copied_geotags` (non-destructive)
- Streams exiftool output while showing a progress bar
