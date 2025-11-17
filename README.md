# merge_subtitles

Double-clickable Windows helper that launches a Docker container containing `ffmpeg` and muxes matching `.mp4`/`.srt` pairs via:

```
ffmpeg -i infile.mp4 -i infile.srt -c copy -c:s mov_text outfile.mp4
```

## Prerequisites

- Python 3.9+ with Tkinter available (for the folder picker GUI)
- Docker Engine capable of running Linux containers (e.g., Docker Desktop, Docker CE, Colima, etc.)

## One-time setup

1. Create and activate a virtual environment:

	```powershell
	python -m venv .venv
	.\.venv\Scripts\activate
	```

2. Install the Python dependency used by the scripts (currently just `tqdm`):

	```powershell
	python -m pip install -r requirements.txt
	```

## Everyday usage

1. Activate the virtual environment:

	```powershell
	.\.venv\Scripts\activate
	```

2. Run the launcher:

	```powershell
	python launch_merge_subtitles.py
	```

	Alternatively, double-click `run.ps1`, which simply activates the environment and starts the launcher for you.

- A Tk folder picker always prompts you for the Windows folder containing matching `.mp4` and `.srt` files.
- The launcher mounts the chosen folder at `/work` inside the container and muxes every top-level pair it finds.
- Outputs land in `<selected folder>/videos_with_merged_subtitles` with the original filenames, overwriting any existing files.
- The launcher runs a quiet `docker version --format "{{.Server.Version}}"` check (so you get a friendly error if Docker isn’t running) and auto-builds `merge-subtitles:latest` whenever it’s missing; subsequent runs skip the build once the image exists.

