# add_geotag_to_dji_drone_video

Host launcher + Dockerized exiftool workflow to extract GPS coordinates from DJI drone `.srt` sidecar files and embed them into matching `.mp4` video files.

## Project layout

- `Dockerfile` — multi-stage build: Node.js parser deps + Python/exiftool runtime
- `launcher.py` — host-side launcher with a Tk folder picker
- `container/add_geotag_to_dji_drone_video.py` — script executed inside the container
- `container/requirements.txt` — Python deps for the container
- `container/DJI_SRT_Parser/` — Git submodule with the Node.js SRT parser

## Prerequisites

- Python 3.9+ with Tkinter available (for the folder picker GUI)
- Docker Engine capable of running Linux containers (e.g., Docker Desktop)
- Git submodule initialized: `git submodule update --init --recursive` (if cloning fresh)

## Run

Use the launcher to pick a folder and run the container:

```powershell
python launcher.py
```

What it does:
- Prompts for a folder containing `.mp4` + `.srt` pairs (DJI drone format)
- Parses the **first GPS coordinate and altitude** from each SRT file using the [DJI_SRT_Parser](https://github.com/JuanIrache/DJI_SRT_Parser) library
- Uses exiftool to write `GPSLatitude`, `GPSLongitude`, and `GPSAltitude` tags to the MP4 file
- Writes updated videos to `<selected>/videos_with_geotags` (non-destructive)
- Streams progress with alive-progress bar

## Dependencies

This tool uses the [DJI_SRT_Parser](https://github.com/JuanIrache/DJI_SRT_Parser) library by Juan Irache for parsing DJI drone SRT files.

