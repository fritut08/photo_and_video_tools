"""Add geotag from XMP sidecar files to JPEG image files."""

import subprocess
from pathlib import Path
from alive_progress import alive_bar

WORK_DIR = Path("/work")
OUTPUT_DIR = WORK_DIR / "photos_with_copied_geotags"
ARGS_FILE = "/exiftool_args_file/xmp2exif.args"

if __name__ == "__main__":

    # Collect XMP files
    xmp_files = [
        file for file in WORK_DIR.iterdir() if file.is_file() and file.suffix.lower() == ".xmp"
    ]

    # Find matching JPEG files
    supported_extensions = {".jpg", ".jpeg"}
    pairs: list[tuple[Path, Path]] = []
    for xmp_file in xmp_files:
        stem = xmp_file.stem
        for ext in supported_extensions:
            jpeg_candidate = WORK_DIR / f"{stem}{ext}"
            if jpeg_candidate.exists():
                pairs.append((xmp_file, jpeg_candidate))
                break

    if not pairs:
        print(f"No matching XMP + JPEG pairs found in. Abort.")
        raise SystemExit(0)
    
    print(f"Found {len(pairs)} XMP + JPEG pairs to process.")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Process each pair
    processed = 0
    failed = 0
    
    with alive_bar(
        len(pairs),
        title="Copying geotags",
        bar="smooth",
        spinner="waves",
        dual_line=True,
        enrich_print=True,
    ) as bar:
        for xmp_path, jpeg_path in pairs:
            bar.text(jpeg_path.name)
            output_path = OUTPUT_DIR / jpeg_path.name

			# Construct the ExifTool command
            command: list[str] = [
                "exiftool",
                '-m', # ignore maker notes offset warning
                "-tagsfromfile", str(xmp_path),
                "-location:all",          # copy only location-related tags from XMP
                "-@", ARGS_FILE,
                "--Orientation",          # after args file: ignore orientation from XMP
                "-o", str(output_path),
                str(jpeg_path),
            ]

            # Execute exiftool and stream output so the progress bar stays clean
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
                print(f"✗ Failed to process {jpeg_path.name} (exiftool exit code {return_code})")
                failed += 1
            else:
                print(f"✓ Processed {jpeg_path.name}")
                processed += 1

            bar()

    print(f"Processed: {processed}")
    print(f"Failed: {failed}")

    print(f"Output written to: {OUTPUT_DIR}")

    if failed != 0:
        print("Completed with failures.")
        raise SystemExit(1)
    
    raise SystemExit(0)

