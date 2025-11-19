# merge_srt_with_mp4

Host launcher + Dockerized ffmpeg workflow to mux matching `.mp4`/`.srt` pairs via:

```
ffmpeg -i infile.mp4 -i infile.srt -c copy -c:s mov_text outfile.mp4
```

## Project layout

- `Dockerfile` — builds the runtime image
- `launch_merge_srt_with_mp4.py` — host-side launcher with a Tk folder picker
- `container/merge_srt_with_mp4.py` — script executed inside the container
- `container/requirements.txt` — Python deps for the container

## Prerequisites

- Python 3.9+ with Tkinter available (for the folder picker GUI)
- Docker Engine capable of running Linux containers (e.g., Docker Desktop)

## Run

Use the launcher to pick a folder and run the container:

```powershell
python launch_merge_srt_with_mp4.py
```

What it does:
- Prompts for a folder containing `.mp4` + `.srt` pairs
- Mounts it to `/work` in the container
- Writes outputs to `<selected>/videos_with_merged_subtitles`
- Allocates `-it` for a real TTY so the progress bar shows ETA and time suffixes
