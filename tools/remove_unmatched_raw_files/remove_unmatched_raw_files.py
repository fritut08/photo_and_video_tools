"""Move unmatched RAW (.ARW) files to a subfolder."""
from __future__ import annotations

from pathlib import Path
import shutil
import tkinter as tk
from tkinter import filedialog

OUTPUT_SUBDIR = "removed raw files"


def select_directory(title: str) -> Path | None:
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(title=title)
    root.destroy()
    if not selected:
        return None
    return Path(selected)


def collect_map(directory: Path, exts: tuple[str, ...]) -> dict[str, Path]:
    """Return mapping stem -> Path for files matching any extension (case-insensitive).

    Preserves original filename casing. If multiple case variants exist for same stem,
    the first encountered is kept.
    """
    mapping: dict[str, Path] = {}
    lowered = {e.lower() for e in exts}
    for entry in directory.iterdir():
        if not entry.is_file():
            continue
        lower_name = entry.name.lower()
        for ext in lowered:
            if lower_name.endswith(ext):
                mapping.setdefault(entry.stem, entry)
                break
    return mapping


def main() -> int:
    print("=" * 60)
    print("  Remove Unmatched RAW Files")
    print("=" * 60)
    print()

    print("Select folder containing JPG/JPEG files...")
    jpg_dir = select_directory("JPG/JPEG Files")
    if jpg_dir is None:
        print("No JPG directory selected. Abort.")
        return 1

    print("Select folder containing RAW (.ARW) files...")
    raw_dir = select_directory("RAW Files")
    if raw_dir is None:
        print("No RAW directory selected. Abort.")
        return 1

    jpg_map = collect_map(jpg_dir, (".jpg", ".jpeg", ".JPG", ".JPEG"))
    raw_map = collect_map(raw_dir, (".arw", ".ARW"))

    unmatched_paths = [path for stem, path in raw_map.items() if stem not in jpg_map]
    unmatched_paths.sort(key=lambda p: p.stem)
    if not unmatched_paths:
        print("No unmatched RAW files found.")
        return 0

    print(f"Unmatched RAW files ({len(unmatched_paths)}):")
    for path in unmatched_paths:
        print(f" - {path.name}")

    confirm = input(f"Remove these {len(unmatched_paths)} RAW files? Type YES to confirm: ").strip()
    if confirm.lower() not in ['yes', 'y']:
        print("Operation cancelled.")
        return 1

    target_dir = raw_dir / OUTPUT_SUBDIR
    target_dir.mkdir(exist_ok=True)

    moved = 0
    for src in unmatched_paths:
        dest = target_dir / src.name
        try:
            shutil.move(str(src), str(dest))
            moved += 1
        except OSError as exc:
            print(f"Failed to remove {src.name}: {exc}")

    print(f"Moved {moved} RAW files to '{OUTPUT_SUBDIR}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
