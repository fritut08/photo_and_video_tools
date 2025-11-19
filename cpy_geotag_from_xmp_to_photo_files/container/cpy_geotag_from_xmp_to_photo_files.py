"""Container-friendly geotag copier: copies GPS/location tags from .xmp sidecars
into matching .jpg/.jpeg files.

Non-destructive: writes corrected files into /work/photos_with_copied_geotags.
Relies on exiftool plus the xmp2exif.args mapping file fetched at build time.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from alive_progress import alive_bar

ARGS_FILE = "/app/xmp2exif.args"
OUTPUT_SUBDIR = "photos_with_copied_geotags"
SUPPORTED_EXTS = {".jpg", ".jpeg"}


def collect_pairs(directory: Path) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for xmp in directory.glob("*.xmp"):
        stem = xmp.stem
        for ext in (".jpg", ".jpeg", ".JPG", ".JPEG"):
            cand = directory / f"{stem}{ext}"
            if cand.exists():
                pairs.append((xmp, cand))
                break
    return pairs


def main() -> int:
    directory = Path("/work")
    output_dir = directory / OUTPUT_SUBDIR
    output_dir.mkdir(exist_ok=True)

    pairs = collect_pairs(directory)
    if not pairs:
        print(f"No matching .xmp + (.jpg/.jpeg) pairs found in {directory}")
        return 0

    failures: list[tuple[str, str]] = []
    with alive_bar(
        len(pairs),
        title="Copying geotags",
        bar="smooth",
        spinner="waves",
        dual_line=True,
        enrich_print=True,
    ) as bar:
        for xmp_path, image_path in pairs:
            bar.text(image_path.name)
            output_path = output_dir / image_path.name

            command: list[str] = [
                "exiftool",
                "-tagsfromfile", str(xmp_path),
                "-location:all",
                "-@", ARGS_FILE,
                "-o", str(output_path),
                str(image_path),
            ]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            if process.stdout is not None:
                for line in process.stdout:
                    line = line.rstrip()
                    if line:
                        print(line)
            return_code = process.wait()

            if return_code != 0:
                failures.append((image_path.name, f"exiftool exited with {return_code}"))
                print(f"exiftool failed for {image_path.name}")
            else:
                print(f"Wrote geotagged {output_path.name}")

            bar()

    if failures:
        print("\nCompleted with failures:")
        for fn, reason in failures:
            print(f" - {fn}: {reason}")
        return 1

    print("\nAll geotags copied successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
