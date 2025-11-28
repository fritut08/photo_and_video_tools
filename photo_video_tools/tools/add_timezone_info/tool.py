"""Host launcher for the Docker container executing the script of the add_timezone_info tool."""

from pathlib import Path
from photo_video_tools.docker_utils import run_container
from photo_video_tools.shared import select_directory_gui, parse_timezone_input, ToolBase

TOOL_PATH = Path(__file__).parent
CONTAINER_DIR = TOOL_PATH / "container"


class AddTimezoneInfoTool(ToolBase):
    """Add timezone information."""
    
    name = "Add Timezone Information"
    description = "Add timezone information to photos' tags"
    
    @classmethod
    def run(cls) -> int:
        cls.announce()

        work_dir = select_directory_gui("Select folder containing image files")
        if work_dir is None:
            print("No directory selected. Abort.")
            return 1

        # Get timezone info from user
        timezone_info = None
        while timezone_info is None:
            user_input = input("Enter the timezone information as an offset from UTC (e.g., -9:00, 5:30): ")
            timezone_info = parse_timezone_input(user_input)
            if timezone_info is None:
                print("Invalid timezone offset format. Please try again.")

        docker_options = [
            "-it", "--rm",
            "-v", f"{work_dir}:/work",
            "-v", f"{CONTAINER_DIR}:/app:ro",
            "-w", "/work",
        ]

        # command to run inside container
        command_and_args = [
            "sh", "-c",
            (
                "python -m venv /venv && "
                ". /venv/bin/activate && "
                "pip install --upgrade pip && "
                "pip install --no-cache-dir -r /app/requirements.txt && "
                f"python /app/container_script.py {timezone_info}"
            ),
        ]

        print(f"Running container...")
        return run_container("exiftool", docker_options, command_and_args)
