# merge_subtitles

Double-clickable Windows helper that launches a Docker container containing `ffmpeg` and muxes matching `.mp4`/`.srt` pairs via:

```
ffmpeg -i infile.mp4 -i infile.srt -c copy -c:s mov_text outfile.mp4
```

## Prerequisites

- Windows 10/11 with Python 3.9+ (for the Tk folder picker)
- Docker Desktop (or any Docker daemon that can run Linux containers)

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

3. Build the container image that packages `ffmpeg` and the merging script:

	```powershell
	docker build -t merge-subtitles .
	```

## Everyday usage

- Run `run_merge.ps1` (double-clickable) or execute the launcher manually:

  ```powershell
  python launch_merge_subtitles.py
  ```

- A folder picker opens if `--directory` is omitted. Otherwise supply a Windows path via `--directory`.
- The launcher mounts the chosen folder at `/work` in the container and forwards flags such as `--recursive`, `--suffix`, `--output-dir`, `--overwrite`, and `--dry-run`.
- `--output-dir` must reside inside the selected folder so that the container can write to it.
- Before running the container the launcher checks `docker info`; if Docker Desktop is not running you’ll get a friendly reminder instead of a cryptic CLI error.
- Add `--print-command` to see the exact `docker run ...` invocation without starting the container (useful for testing).

