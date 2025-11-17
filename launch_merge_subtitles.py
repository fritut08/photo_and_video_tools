"""Host launcher for the Dockerized merge_subtitles container."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

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


def build_container_command(directory: Path) -> List[str]:
    command: List[str] = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{directory}:/work",
        "-w",
        CONTAINER_WORKDIR,
        DEFAULT_IMAGE,
    ]

    return command


def ensure_docker_ready() -> None:
    info = subprocess.run([
        "docker",
        "info",
    ])
    if info.returncode != 0:
        raise RuntimeError(
            "Docker is not available."
        )


def ensure_image_exists() -> None:
    inspect = subprocess.run(
        ["docker", "image", "inspect", DEFAULT_IMAGE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if inspect.returncode == 0:
        return
    print(f"Docker image '{DEFAULT_IMAGE}' not found. Building it now...")
    build = subprocess.run(["docker", "build", "-t", DEFAULT_IMAGE, str(Path(__file__).parent)])
    if build.returncode != 0:
        raise RuntimeError(f"Failed to build Docker image '{DEFAULT_IMAGE}'.")


def main() -> int:
    directory = select_directory_gui("Select the folder containing MP4/SRT pairs")
    if directory is None:
        print("No directory selected. Abort.")
        return 1

    directory = directory.expanduser().resolve()
    if not directory.exists() or not directory.is_dir():
        print(f"Provided path is not a directory: {directory}")
        return 1

    try:
        ensure_docker_ready()
        ensure_image_exists()
        command = build_container_command(directory)
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
