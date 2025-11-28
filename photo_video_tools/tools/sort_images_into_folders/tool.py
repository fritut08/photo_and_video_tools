"""Sort images into YYYY-MM-DD folders based on EXIF DateTimeOriginal."""

import shutil
from pathlib import Path
from datetime import datetime
import exifread
from alive_progress import alive_bar

from photo_video_tools.shared import select_directory_gui, ToolBase

OUTPUT_SUBDIR = "sorted_images"
SUPPORTED_EXTS = (".jpg", ".jpeg", ".dng", ".arw")


class SortImagesIntoFoldersTool(ToolBase):
    """Sort images into YYYY-MM-DD folders based on EXIF DateTimeOriginal."""
    
    name = "Sort Images into Folders"
    description = "Organize images by date into year/month folders"

    @staticmethod
    def extract_createdate(file_path: Path) -> datetime | None:
        """Extract EXIF DateTimeOriginal from an image file."""
        try:
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f, details=False)
                if "EXIF DateTimeOriginal" in tags:
                    date_str = str(tags["EXIF DateTimeOriginal"])
                    return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass
        return None
    
    @classmethod
    def run(cls) -> int:
        cls.announce()

        work_dir = select_directory_gui("Select folder containing image files")
        if work_dir is None:
            print("No directory selected. Abort.")
            return 1

        image_files = [
            file for file in work_dir.iterdir()
            if file.is_file() and file.name.lower().endswith(SUPPORTED_EXTS)
        ]

        if not image_files:
            print(f"No supported image files found in {work_dir}")
            return 0
        
        # Ensure output directory exists
        output_dir = work_dir / OUTPUT_SUBDIR
        output_dir.mkdir(exist_ok=True)

        # Process each image file
        processed = 0
        failed = 0

        with alive_bar(
            len(image_files),
            title="Organizing images",
            bar="smooth",
            spinner="waves",
            dual_line=True,
            enrich_print=True,
        ) as bar:
            for img_file in image_files:
                bar.text(img_file.name)
                createdate = cls.extract_createdate(img_file)

                if createdate is None:                   
                    print(f"✗ Skipped {img_file.name} (could not read create date)")
                    failed += 1
                    bar()
                    continue
                
                subdir_name = createdate.strftime("%Y-%m-%d")
                subdir_path = output_dir / subdir_name
                subdir_path.mkdir(exist_ok=True)

                output_path = subdir_path / img_file.name
                try:
                    shutil.copy2(img_file, output_path)
                except Exception as e:
                    print(f"✗ Failed to copy {img_file.name} to folder '{subdir_name}': {e}")
                    failed += 1
                    bar()
                    continue

                print(f"✓ Copied {img_file.name} to folder '{subdir_name}'")
                processed += 1
                bar()

        print(f"Processed: {processed}")
        print(f"Failed: {failed}")
        
        print(f"Output written to: {output_dir}")

        if failed != 0:
            print("Completed with failures!")
            return 1
        
        return 0