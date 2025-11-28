"""Host launcher for the Docker container executing the script of the cpy_geotag_from_xmp_to_jpeg_files tool."""

from pathlib import Path
from photo_video_tools.shared import ToolBase

TOOL_PATH = Path(__file__).parent
CONTAINER_DIR = TOOL_PATH / "container"


class CopyGeotagFromXmpToJpegFilesTool(ToolBase):
    """Copy GPS data from XMP sidecars to JPEG files."""
    
    name = "Copy Geotags from XMP to JPEG Files"
    description = "Copy GPS data from XMP sidecars to JPEG files"
    
    @classmethod
    def run(cls) -> int:
        return cls.run_default(
            "Select folder containing XMP + JPG file pairs",
            CONTAINER_DIR,
            "exiftool"
        )
