"""Host launcher for the Docker container executing the script of the merge_srt_with_mp4 tool."""

from pathlib import Path
from photo_video_tools.shared import ToolBase

TOOL_PATH = Path(__file__).parent
CONTAINER_DIR = TOOL_PATH / "container"


class MergeSrtWithMp4Tool(ToolBase):
    """Merge SRT subtitle files into MP4 videos as a subtitle track."""
    
    name = "Merge SRT with MP4"
    description = "Merge SRT subtitle files into MP4 videos as a subtitle track"
    
    @classmethod
    def run(cls) -> int:
        return cls.run_default(
            "Select the folder containing MP4 + SRT file pairs", 
            CONTAINER_DIR, 
            "ffmpeg"
        )
