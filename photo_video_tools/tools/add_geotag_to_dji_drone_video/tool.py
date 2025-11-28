"""Host launcher for the Docker container executing the script of the add_geotag_to_dji_drone_video tool."""

from pathlib import Path
from photo_video_tools.shared import ToolBase

TOOL_PATH = Path(__file__).parent
CONTAINER_DIR = TOOL_PATH / "container"


class AddGeotagToDjiDroneVideoTool(ToolBase):
    """Extract GPS data from SRT and embed into MP4 files."""

    name = "Add Geotag to DJI Drone Video"
    description = "Extract GPS data from SRT and embed into MP4 files"
    
    @classmethod
    def run(cls) -> int:
        return cls.run_default(
            "Select folder containing MP4 + SRT file pairs",
            CONTAINER_DIR,
            "exiftool-nodejs"
        )