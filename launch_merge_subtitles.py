"""Windows host launcher for the Dockerized merge_subtitles container."""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence

import tkinter as tk
from tkinter import filedialog

DEFAULT_IMAGE = "merge-subtitles:latest"
CONTAINER_WORKDIR = "/work"


def select_directory_gui(title: str) -> Optional[Path]:
    """Prompt the user for a directory using a Tk folder picker."""
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(title=title)
    root.destroy()
    if not selected:
        return None
    return Path(selected)


def ensure_relative_path(child: Path, base: Path) -> Path:
    """Ensure child resides within base and return the relative path."""
    try:
        return child.resolve().relative_to(base.resolve())
    except ValueError as exc:
        raise ValueError(f"{child} is not inside the selected directory {base}") from exc


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the Dockerized subtitle merger")
    parser.add_argument(
        "--directory",
        "-d",
        type=Path,
        help="Folder on the Windows host that contains the MP4/SRT files",
    )
    parser.add_argument("--recursive", action="store_true", help="Search sub-folders too")
    parser.add_argument(
        "--suffix",
        default="_merged",
        help="Suffix added before the .mp4 extension for outputs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional sub-directory (inside the selected folder) for outputs",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Forward the dry-run flag to the container (no ffmpeg execution)",
    )
    parser.add_argument(
        "--docker-bin",
        default="docker",
        help="Docker executable to call (default: docker)",
    )
    parser.add_argument(
        "--image-name",
        default=DEFAULT_IMAGE,
        help=f"Container image to run (default: {DEFAULT_IMAGE})",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="Print the docker command instead of executing it (handy for tests)",
    )
    return parser.parse_args(argv)


def build_container_command(args: argparse.Namespace, directory: Path) -> List[str]:
    command: List[str] = [
        args.docker_bin,
        "run",
        "--rm",
        "-v",
        f"{directory}:/work",
        "-w",
        CONTAINER_WORKDIR,
        args.image_name,
        "--directory",
        CONTAINER_WORKDIR,
    ]

    if args.recursive:
        command.append("--recursive")
    command.extend(["--suffix", args.suffix])

    if args.output_dir:
        rel = ensure_relative_path(args.output_dir, directory)
        rel_posix = rel.as_posix()
        if rel_posix in ("", "."):
            container_output = CONTAINER_WORKDIR
        else:
            container_output = f"{CONTAINER_WORKDIR}/{rel_posix}"
        command.extend(["--output-dir", container_output])

    if args.overwrite:
        command.append("--overwrite")
    if args.dry_run:
        command.append("--dry-run")

    return command


def ensure_docker_running(docker_bin: str) -> None:
    """Raise RuntimeError if the Docker daemon is unreachable."""
    probe = subprocess.run(
        [docker_bin, "info"],
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0:
        stderr = probe.stderr.strip() or probe.stdout.strip()
        raise RuntimeError(
            "Docker is not available. Start Docker Desktop and try again."
            + (f"\nDetails: {stderr}" if stderr else "")
        )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    directory = args.directory
    if directory is None:
        directory = select_directory_gui("Select the folder containing MP4/SRT pairs")
        if directory is None:
            print("No directory selected. Abort.")
            return 1

    directory = directory.expanduser().resolve()
    if not directory.exists() or not directory.is_dir():
        print(f"Provided path is not a directory: {directory}")
        return 1

    if args.output_dir is not None:
        output_dir = args.output_dir.expanduser()
        if not output_dir.is_absolute():
            output_dir = (directory / output_dir).resolve()
        else:
            output_dir = output_dir.resolve()
        args.output_dir = output_dir

    try:
        command = build_container_command(args, directory)
    except ValueError as exc:
        print(exc)
        return 1

    if args.print_command:
        print("Docker command:")
        print(" ".join(shlex.quote(part) for part in command))
        return 0

    try:
        ensure_docker_running(args.docker_bin)
    except RuntimeError as exc:
        print(exc)
        return 1

    return subprocess.run(command).returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except tk.TclError as exc:
        print(f"Tkinter failed to initialize: {exc}")
        sys.exit(1)
