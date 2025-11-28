"""Central launcher for photo and video tools."""

import sys

# Import all tool classes
from photo_video_tools.tools import *

# Tool registry: list of tool classes
TOOLS = [
    SortImagesIntoFoldersTool,
    RemoveUnmatchedRawFilesTool,
    AddTimezoneInfoTool,
    ShiftTimeAndTimezoneTool,
    CopyGeotagFromXmpToJpegFilesTool,
    MergeSrtWithMp4Tool,
    AddGeotagToDjiDroneVideoTool,
]


def print_menu() -> None:
    """Display the tool selection menu."""
    print("=" * 70)
    print("  Photo and Video Tools")
    print("=" * 70)
    print()
    for i, tool_class in enumerate(TOOLS, start=1):
        print(f"  {i}. {tool_class.name}")
        print(f"     {tool_class.description}")
        print()
    print("  q. Quit")
    print()


def get_user_choice() -> int | None:
    """Get tool selection from user."""
    while True:
        choice = input(f"Select a tool (1-{len(TOOLS)}, q): ").strip().lower()
        if choice == "q":
            return None
        try:
            num = int(choice)
        except ValueError:
            print(f"Invalid choice: {choice}")
            continue
        
        if 1 <= num <= len(TOOLS):
            return num - 1  # Convert to 0-based index
        print(f"Invalid choice: {choice}")


def run_tool(tool_index: int) -> int:
    """Run the selected tool."""
    tool_class = TOOLS[tool_index]

    print(f"\nLaunching: {tool_class.name}")
    
    return tool_class.run()


def main() -> int:
    """Main entry point."""
    try:
        print_menu()
        choice = get_user_choice()
        
        if choice is None:
            print("Exiting...")
            return 0
        
        exit_code = run_tool(choice)
        
        if exit_code != 0:
            print(f"\nTool exited with code {exit_code}")
        
        return exit_code
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
