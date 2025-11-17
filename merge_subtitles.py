"""Container-friendly subtitle muxer that runs entirely inside Linux."""
from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from tqdm import tqdm

VIDEO_EXT = ".mp4"
SUBTITLE_EXT = ".srt"

def collect_pairs(directory: Path, recursive: bool = False) -> List[Tuple[Path, Path]]:
    pattern = "**/*" if recursive else "*"
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


def build_ffmpeg_command(
    ffmpeg_bin: str,
    video_path: Path,
    subtitle_path: Path,
    output_path: Path,
    overwrite: bool,
) -> List[str]:
    command: List[str] = [ffmpeg_bin]
    if overwrite:
        command.append("-y")
    command.extend(
        [
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
    )
    return command


def ensure_output_path(video_path: Path, output_dir: Optional[Path], suffix: str) -> Path:
    target_dir = output_dir if output_dir is not None else video_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / f"{video_path.stem}{suffix}{video_path.suffix}"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch mux subtitles inside a container")
    parser.add_argument(
        "--directory",
        "-d",
        type=Path,
        default=Path("/work"),
        help="Folder (inside the container) containing MP4/SRT files (default: /work)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search through all sub-directories as well",
    )
    parser.add_argument(
        "--suffix",
        default="_merged",
        help="Suffix to append before the .mp4 extension for the output",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional folder for all rendered files (defaults to each video's folder)",
    )
    parser.add_argument(
        "--ffmpeg-bin",
        default="ffmpeg",
        help="Name or path of the ffmpeg binary inside the container",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files instead of skipping them",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the ffmpeg commands without executing them",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    directory = args.directory.expanduser().resolve()

    if not directory.exists() or not directory.is_dir():
        print(f"Provided path is not a directory: {directory}")
        return 1

    pairs = collect_pairs(directory, recursive=args.recursive)
    if not pairs:
        print(f"No matching {VIDEO_EXT}/{SUBTITLE_EXT} pairs found in {directory}")
        return 0

    failures = []
    progress = tqdm(pairs, desc="Merging subtitles", unit="file")
    for video_path, subtitle_path in progress:
        output_path = ensure_output_path(video_path, args.output_dir, args.suffix)
        if output_path.exists() and not args.overwrite:
            tqdm.write(f"Skipping {output_path.name} (already exists; use --overwrite)")
            continue

        command = build_ffmpeg_command(
            args.ffmpeg_bin,
            video_path,
            subtitle_path,
            output_path,
            overwrite=args.overwrite,
        )

        if args.dry_run:
            tqdm.write("DRY RUN: " + " ".join(shlex.quote(part) for part in command))
            continue

        result = subprocess.run(command)
        if result.returncode != 0:
            failures.append((video_path, f"ffmpeg exited with {result.returncode}"))
            tqdm.write(f"ffmpeg failed for {video_path.name}")

    if failures:
        print("\nCompleted with failures:")
        for video_path, reason in failures:
            print(f" - {video_path.name}: {reason}")
        return 2

    print("\nAll subtitle tracks merged successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
