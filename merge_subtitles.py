"""Container-friendly subtitle muxer that runs entirely inside Linux."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

VIDEO_EXT = ".mp4"
SUBTITLE_EXT = ".srt"
OUTPUT_SUBDIR = "videos_with_merged_subtitles"

console = Console(force_terminal=True)

def collect_pairs(directory: Path) -> List[Tuple[Path, Path]]:
    pattern = "*"
    videos = {}
    subtitles = {}
    for path in directory.glob(f"{pattern}{VIDEO_EXT}"):
        videos[path.stem.lower()] = path
    for path in directory.glob(f"{pattern}{VIDEO_EXT.upper()}"):
        videos[path.stem.lower()] = path
    for path in directory.glob(f"{pattern}{SUBTITLE_EXT}"):
        subtitles[path.stem.lower()] = path
    for path in directory.glob(f"{pattern}{SUBTITLE_EXT.upper()}"):
        subtitles[path.stem.lower()] = path
    matched = []
    for stem, video_path in videos.items():
        if stem in subtitles:
            matched.append((video_path, subtitles[stem]))
    return matched
def main() -> int:
    directory = Path("/work")
    output_dir = directory / OUTPUT_SUBDIR
    output_dir.mkdir(exist_ok=True)

    pairs = collect_pairs(directory)
    if not pairs:
        print(f"No matching {VIDEO_EXT}/{SUBTITLE_EXT} pairs found in {directory}")
        return 0

    failures = []
    with Progress(
        TextColumn("{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
        expand=True,
    ) as progress:
        task_id = progress.add_task("Merging subtitles", total=len(pairs))
        for video_path, subtitle_path in pairs:
            output_path = output_dir / video_path.name

            command: List[str] = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "warning",
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(subtitle_path),
                "-c",
                "copy",
                "-c:s",
                "mov_text",
                str(output_path),
            ]

            console.print(f"Starting {video_path.name}")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            if process.stdout is not None:
                for line in process.stdout:
                    clean_line = line.rstrip()
                    if clean_line:
                        console.print(clean_line)
            return_code = process.wait()

            if return_code != 0:
                failures.append((video_path, f"ffmpeg exited with {return_code}"))
                console.print(f"ffmpeg failed for {video_path.name}")
            else:
                console.print(f"Merged {video_path.name}")

            progress.advance(task_id)

    if failures:
        console.print("\nCompleted with failures:")
        for video_path, reason in failures:
            console.print(f" - {video_path.name}: {reason}")
        return 1

    console.print("\nAll subtitle tracks merged successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
