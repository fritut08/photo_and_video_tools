"""Host launcher for the Dockerized add_geotag_to_dji_drone_video container."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import tkinter as tk
from tkinter import filedialog

DEFAULT_IMAGE = "add-geotag-to-dji-drone-video:latest"
CONTAINER_WORKDIR = "/work"

SOURCE_FILES = [
    Path(__file__).parent / "Dockerfile",
    Path(__file__).parent / "container" / "add_geotag_to_dji_drone_video.py",
    Path(__file__).parent / "container" / "parse_srt.js",
    Path(__file__).parent / "container" / "requirements.txt",
]

def compute_source_hash() -> str:
    import hashlib
    sha = hashlib.sha256()
    
    # Hash main source files
    for p in SOURCE_FILES:
        if p.exists():
            sha.update(p.read_bytes())
        else:
            sha.update(f"missing:{p}".encode())
    
    # Hash DJI_SRT_Parser submodule (package.json and main index.js)
    parser_dir = Path(__file__).parent / "container" / "DJI_SRT_Parser"
    parser_files = [
        parser_dir / "package.json",
        parser_dir / "package-lock.json",
        parser_dir / "index.js",
    ]
    for p in parser_files:
        if p.exists():
            sha.update(p.read_bytes())
        else:
            sha.update(f"missing:{p}".encode())
    
    return sha.hexdigest()


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
        "-it",
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
        "version",
        "--format",
        "{{.Server.Version}}",
    ])
    if info.returncode != 0:
        raise RuntimeError(
            "Docker is not available."
        )
    print("Docker is available.")


def ensure_image_exists() -> None:
    wanted_hash = compute_source_hash()
    proc = subprocess.run(["docker", "image", "inspect", DEFAULT_IMAGE, "--format", "{{ index .Config.Labels \"source_hash\"}}"], capture_output=True, text=True)
    existing_hash = proc.stdout.strip() if proc.returncode == 0 else ""
    if existing_hash == wanted_hash:
        return
    if existing_hash:
        print(f"Docker image hash mismatch (have {existing_hash[:12]}, want {wanted_hash[:12]}). Rebuilding...")
    else:
        print(f"Docker image {DEFAULT_IMAGE} not found or missing source_hash label. Building...")

    build_cmd = [
        "docker",
        "build",
        "--label", f"source_hash={wanted_hash}",
        "-t", DEFAULT_IMAGE,
        str(Path(__file__).parent),
    ]

    result = subprocess.run(build_cmd)
    if result.returncode != 0:
        raise RuntimeError("Docker build failed.")
    print(f"Image {DEFAULT_IMAGE} built successfully (hash {wanted_hash[:12]}).")


def main() -> int:
    print("=" * 60)
    print("  Add Geotag to DJI Drone Video")
    print("=" * 60)
    print()

    print("Select folder containing MP4 + SRT files...")
    directory = select_directory_gui("MP4 + SRT Files")
    if directory is None:
        print("No directory selected. Abort.")
        return 1

    try:
        ensure_docker_ready()
        ensure_image_exists()
    except RuntimeError as e:
        print(f"Error: {e}")
        return 1

    cmd = build_container_command(directory)
    print(f"\nRunning container...")
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except tk.TclError as exc:
        print(f"Tkinter failed to initialize: {exc}")
        raise SystemExit(1)
