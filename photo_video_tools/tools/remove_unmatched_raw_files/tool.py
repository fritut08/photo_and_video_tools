"""Move files without a matching counterpart (by filename stem) to a subfolder."""

import shutil

from alive_progress import alive_bar

from photo_video_tools.shared import select_directory_gui, ToolBase


def parse_extensions_input(input_str: str) -> set[str] | None:
    """Parse a comma-separated list of file extensions into a normalized set, e.g. '.jpg', '.jpeg'."""

    parts = [part.strip().lower().lstrip('.') for part in input_str.split(',') if part.strip()]
    if not parts:
        return None
    return {f".{part}" for part in parts}


def ask_extensions(prompt: str) -> set[str] | None:
    """Repeatedly prompt until the user provides a valid, non-empty list of extensions."""

    while True:
        raw = input(prompt).strip()
        extensions = parse_extensions_input(raw)
        if extensions is not None:
            return extensions
        print("Please enter at least one file extension, e.g. 'arw' or 'jpg, jpeg'.")


class RemoveUnmatchedRawFilesTool(ToolBase):
    """Move files without a matching counterpart (by filename stem) to a subfolder."""

    name = "Remove Unmatched Files"
    description = (
        "Move files that have no matching counterpart (same filename, different extension) "
        "in a reference folder to a subfolder, e.g. RAW without JPEG or JPEG without RAW"
    )

    @classmethod
    def run(cls) -> int:
        cls.announce()

        template_extensions = ask_extensions(
            "Which file extension(s) should serve as the template/reference? "
            "(comma-separated, e.g. 'arw' or 'jpg, jpeg'): "
        )
        target_extensions = ask_extensions(
            "Which file extension(s) should be checked against the template and moved if unmatched? "
            "(comma-separated, e.g. 'jpg, jpeg' or 'arw'): "
        )

        if template_extensions & target_extensions:
            print(
                "Template and target extensions must not overlap: "
                f"{', '.join(sorted(template_extensions & target_extensions))}"
            )
            return 1

        template_dir = select_directory_gui(
            f"Select folder containing template files ({', '.join(sorted(template_extensions))})"
        )
        if template_dir is None:
            print("No template directory selected. Abort.")
            return 1

        target_dir = select_directory_gui(
            f"Select folder containing files to check ({', '.join(sorted(target_extensions))})"
        )
        if target_dir is None:
            print("No target directory selected. Abort.")
            return 1

        # Collect template file stems
        template_file_stems = {
            file.stem for file in template_dir.iterdir()
            if file.is_file() and file.suffix.lower() in template_extensions
        }

        # Collect target files
        target_files = [
            file for file in target_dir.iterdir()
            if file.is_file() and file.suffix.lower() in target_extensions
        ]

        # Find unmatched target files
        unmatched_files = [
            target_file for target_file in target_files
            if target_file.stem not in template_file_stems
        ]

        if not unmatched_files:
            print("No unmatched files found.")
            return 0

        # Ask user for confirmation
        print(f"Unmatched files ({len(unmatched_files)}):")
        for path in unmatched_files:
            print(f" - {path.name}")

        confirm = input(f"Move these {len(unmatched_files)} files? Type YES to confirm: ").strip()
        if confirm.lower() not in ['yes', 'y']:
            print("Operation cancelled.")
            return 1

        # Ensure move directory exists
        extensions_label = "_".join(sorted(ext.lstrip('.') for ext in target_extensions))
        target_subdir = target_dir / f"unmatched_{extensions_label}_files"
        target_subdir.mkdir(exist_ok=True)

        # Process each unmatched file
        moved = 0
        failed = 0

        with alive_bar(
            len(unmatched_files),
            title="Moving unmatched files",
            bar="smooth",
            spinner="waves",
            dual_line=True,
            enrich_print=True,
        ) as bar:
            for file in unmatched_files:
                bar.text(f"Moving {file.name}")
                dest = target_subdir / file.name
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
