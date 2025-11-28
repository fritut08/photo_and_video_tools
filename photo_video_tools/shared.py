"""Shared base class and utilities for photo and video tools."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog

from photo_video_tools.docker_utils import run_container

class ToolBase:
    name = ""

    @classmethod
    def announce(cls):
        print("-" * 60)
        print(f"  {cls.name}")
        print("-" * 60)
        print()

    @classmethod
    def run_default(cls, file_selection_prompt: str, container_dir: Path, container_name: str) -> int:
        cls.announce()

        work_dir = select_directory_gui(file_selection_prompt)
        if work_dir is None:
            print("No directory selected. Abort.")
            return 1

        docker_options = [
            "-it", "--rm",
            f"-v", f"{work_dir}:/work",
            f"-v", f"{container_dir}:/app:ro",
            "-w", "/work",
        ]

        command_and_args = [
            "sh", "-c",
            (
                "python -m venv /venv && "
                ". /venv/bin/activate && "
                "pip install --upgrade pip && "
                "pip install --no-cache-dir -r /app/requirements.txt && "
                f"python /app/container_script.py"
            ),
        ]

        print(f"Running container '{container_name}'...")
        return run_container(container_name, docker_options, command_and_args)

def select_directory_gui(title: str) -> Path | None:
    """Prompt the user for a directory using a Tk folder picker."""

    print(title + "...")
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(title=title)
    root.destroy()
    if not selected:
        return None
    return Path(selected)

def parse_timezone_input(input_str: str) -> str | None:
    try:
        if input_str.count(':') != 1:
            raise ValueError("Argument must be in format <hours>:<minutes>.")
        hours_str, minutes_str = input_str.split(':', 1)
        hours = int(hours_str)
        minutes = int(minutes_str)
        if not (0 <= abs(minutes) < 60):
            raise ValueError("Minutes must be between 0 and 59.")
        timezone_offset = f"{hours:+d}:{abs(minutes):02d}"
    except ValueError as e:
        print(f"Invalid input: {e}")
        return None
    return timezone_offset