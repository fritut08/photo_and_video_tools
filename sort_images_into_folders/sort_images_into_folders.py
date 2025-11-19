"""Sort images into YYYY-MM-DD folders based on EXIF DateTimeOriginal."""
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import exifread
from alive_progress import alive_bar

SUPPORTED_EXTS = (".jpg", ".arw", ".JPG", ".ARW")


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


def select_directory(title: str) -> Path | None:
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(title=title)
    root.destroy()
    if not selected:
        return None
    return Path(selected)


def organize_files_by_createdate(directory: Path) -> int:
    """Organize image files into YYYY-MM-DD subdirectories based on EXIF creation date."""
    lowered_exts = tuple(e.lower() for e in SUPPORTED_EXTS)
    image_files = [
        entry for entry in directory.iterdir()
        if entry.is_file() and entry.name.lower().endswith(lowered_exts)
    ]

    if not image_files:
        print(f"No supported image files found in {directory}")
        return 0

    failures: list[tuple[str, str]] = []
    with alive_bar(
        len(image_files),
        title="Organizing images",
        bar="smooth",
        spinner="waves",
        dual_line=True,
        enrich_print=True,
    ) as bar:
        for img_path in image_files:
            bar.text(img_path.name)
            createdate = extract_createdate(img_path)

            if createdate:
                subdir_name = createdate.strftime("%Y-%m-%d")
                subdir_path = directory / subdir_name
                subdir_path.mkdir(exist_ok=True)

                dest = subdir_path / img_path.name
                try:
                    img_path.rename(dest)
                    print(f"Moved {img_path.name} → {subdir_name}/")
                except OSError as exc:
                    failures.append((img_path.name, f"Move failed: {exc}"))
                    print(f"Failed to move {img_path.name}")
            else:
                failures.append((img_path.name, "No EXIF DateTimeOriginal"))
                print(f"Skipped {img_path.name} (no date)")

            bar()

    if failures:
        print("\nCompleted with issues:")
        for fn, reason in failures:
            print(f" - {fn}: {reason}")
        return 1

    print("\nAll files organized successfully.")
    return 0


def main() -> int:
    print("=" * 60)
    print("  Sort Images Into Folders")
    print("=" * 60)
    print()

    print("Select folder containing image files...")
    directory = select_directory("Image Files")
    if directory is None:
        print("No directory selected. Abort.")
        return 1

    return organize_files_by_createdate(directory)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except tk.TclError as exc:
        print(f"Tkinter failed to initialize: {exc}")
        raise SystemExit(1)
