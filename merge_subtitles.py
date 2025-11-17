"""Container-friendly subtitle muxer that runs entirely inside Linux."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Tuple

from tqdm import tqdm

VIDEO_EXT = ".mp4"
SUBTITLE_EXT = ".srt"
OUTPUT_SUBDIR = "videos_with_merged_subtitles"

def collect_pairs(directory: Path) -> List[Tuple[Path, Path]]:
    pattern = "*"
    videos = {}
    subtitles = {}
    for path in directory.glob(f"{pattern}{VIDEO_EXT}"):
        videos[path.stem.lower()] = path
    for path in directory.glob(f"{pattern}{SUBTITLE_EXT}"):
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
    progress = tqdm(pairs, desc="Merging subtitles", unit="file")
    for video_path, subtitle_path in progress:
        output_path = output_dir / video_path.name

        command: List[str] = [
            "ffmpeg",
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

        result = subprocess.run(command)
        if result.returncode != 0:
            failures.append((video_path, f"ffmpeg exited with {result.returncode}"))
            tqdm.write(f"ffmpeg failed for {video_path.name}")

    if failures:
        print("\nCompleted with failures:")
        for video_path, reason in failures:
            print(f" - {video_path.name}: {reason}")
        return 1

    print("\nAll subtitle tracks merged successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
