"""Move unmatched RAW (.DNG or .ARW) files to a subfolder."""

import shutil
from alive_progress import alive_bar

from photo_video_tools.shared import select_directory_gui, ToolBase

OUTPUT_SUBDIR = "removed_raw_files"


class RemoveUnmatchedRawFilesTool(ToolBase):
    """Move unmatched RAW (.DNG or .ARW) files to a subfolder."""
    
    name = "Remove Unmatched RAW Files"
    description = "Move RAW files without corresponding JPEG files to a subfolder"
    
    @classmethod
    def run(cls) -> int:
        cls.announce()

        jpg_dir = select_directory_gui("Select folder containing JPG files")
        if jpg_dir is None:
            print("No JPG directory selected. Abort.")
            return 1

        raw_dir = select_directory_gui("Select folder containing RAW files (.DNG or .ARW)")
        if raw_dir is None:
            print("No RAW directory selected. Abort.")
            return 1
        
        # Collect jpg file stems in set
        jpg_file_stems = {
            file.stem for file in jpg_dir.iterdir()
            if file.is_file() and file.suffix.lower() in {'.jpg', '.jpeg'}
        }

        # Collect raw files
        raw_files = [
            file for file in raw_dir.iterdir()
            if file.is_file() and file.suffix.lower() in {'.dng', '.arw'}
        ]

        # Find unmatched raw files
        unmatched_raw_files = [
            raw_file for raw_file in raw_files
            if raw_file.stem not in jpg_file_stems
        ]

        if not unmatched_raw_files:
            print("No unmatched RAW files found.")
            return 0

        # Ask user for confirmation
        print(f"Unmatched RAW files ({len(unmatched_raw_files)}):")
        for path in unmatched_raw_files:
            print(f" - {path.name}")

        confirm = input(f"Remove these {len(unmatched_raw_files)} RAW files? Type YES to confirm: ").strip()
        if confirm.lower() not in ['yes', 'y']:
            print("Operation cancelled.")
            return 1

        # Ensure move directory exists
        target_dir = raw_dir / OUTPUT_SUBDIR
        target_dir.mkdir(exist_ok=True)

        # Process each unmatched raw file
        moved = 0
        failed = 0

        with alive_bar(
            len(unmatched_raw_files),
            title="Removing raw files",
            bar="smooth",
            spinner="waves",
            dual_line=True,
            enrich_print=True,
        ) as bar:
            for file in unmatched_raw_files:
                bar.text(f"Moving {file.name}")
                dest = target_dir / file.name
                try:
                    shutil.move(str(file), str(dest))
                    moved += 1
                except Exception as e:
                    print(f"✗ Failed to move {file.name}: {e}")
                    failed += 1
                    bar()
                    continue

                
                print(f"✓ Moved {file.name}")
                bar()

        print(f"Moved: {moved}")
        print(f"Failed: {failed}")

        if failed != 0:
            print("Completed with failures.")
            return 1
        
        return 0
