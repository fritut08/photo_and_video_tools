"""Host launcher for the Dockerized correct_timezone container."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import tkinter as tk
from tkinter import filedialog

DEFAULT_IMAGE = "correct-timezone:latest"
CONTAINER_WORKDIR = "/work"

SOURCE_FILES = [
    Path(__file__).parent / "Dockerfile",
    Path(__file__).parent / "container" / "correct_timezone.py",
    Path(__file__).parent / "container" / "requirements.txt",
]

def compute_source_hash() -> str:
    import hashlib
    sha = hashlib.sha256()
    for p in SOURCE_FILES:
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


def parse_timezone_input(input_str: str) -> float:
    try:
        return float(input_str)
    except ValueError:
        raise ValueError("Invalid input. Please enter a valid floating-point number.")


def build_container_command(directory: Path, timezone_offset: float) -> List[str]:
    command: List[str] = [
        "docker",
        "run",
        "-it",
        "--rm",
        "-v",
        f"{directory}:/work",
        "-w",
        CONTAINER_WORKDIR,
        "-e",
        f"TIMEZONE_OFFSET={timezone_offset}",
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
        print(f"Docker image '{DEFAULT_IMAGE}' missing or unlabeled. Building it now...")
    build = subprocess.run([
        "docker", "build",
        "--label", f"source_hash={wanted_hash}",
        "-t", DEFAULT_IMAGE,
        str(Path(__file__).parent),
    ])
    if build.returncode != 0:
        raise RuntimeError(f"Failed to build Docker image '{DEFAULT_IMAGE}'.")
    print(f"Docker image '{DEFAULT_IMAGE}' built successfully.")


def main() -> int:
    print("=" * 60)
    print("  Correct Timezone")
    print("=" * 60)
    print()
    print("Opening directory selection dialog...")
    directory = select_directory_gui("Select the folder containing image files")
    if directory is None:
        print("No directory selected. Abort.")
        return 1

    directory = directory.expanduser().resolve()
    print(f"Selected directory: {directory}")
    if not directory.exists() or not directory.is_dir():
        print(f"Provided path is not a directory: {directory}")
        return 1

    # Get timezone offset from user
    user_input = input("Enter the timezone difference (e.g., -9, 5.5): ")
    try:
        timezone_offset = parse_timezone_input(user_input)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    try:
        print("Checking Docker availability...")
        ensure_docker_ready()
        print("Ensuring Docker image is ready...")
        ensure_image_exists()
        command = build_container_command(directory, timezone_offset)
    except RuntimeError as exc:
        print(exc)
        return 1

    print(f"Launching container with directory: {directory}")
    return subprocess.run(command).returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except tk.TclError as exc:
        print(f"Tkinter failed to initialize: {exc}")
        sys.exit(1)
