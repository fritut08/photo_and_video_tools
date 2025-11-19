"""Container-friendly timezone corrector that runs entirely inside Linux."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from alive_progress import alive_bar


def parse_timezone_input(input_str: str) -> float:
    try:
        return float(input_str)
    except ValueError:
        raise ValueError("Invalid input. Please enter a valid floating-point number.")


def correct_timestamps_in_directory(directory: Path, timezone_difference: float) -> int:
    # Get all ARW and JPEG files in the directory
    supported_extensions = {'.arw', '.jpg', '.jpeg'}
    image_files = [
        file for file in directory.iterdir()
        if file.is_file() and file.suffix.lower() in supported_extensions
    ]

    if not image_files:
        print(f"No supported image files found in {directory}")
        return 0

    # Determine the operator for date tags based on the sign of timezone_difference
    date_operator = "+" if timezone_difference >= 0 else "-"

    # Create the time_offset string in the format 'hh:mm:ss'
    hours, remainder = divmod(abs(timezone_difference) * 3600, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_offset = f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}'

    # Create the timezone_offset string in the format '+HH:MM' or '-HH:MM' for timezone tags
    timezone_offset = f'{date_operator}{int(hours):02d}:{int(minutes):02d}'

    print(f"Processing {len(image_files)} files with timezone offset: {timezone_difference} hours")
    print(f"Time adjustment: {date_operator}{time_offset}")
    print(f"Timezone offset: {timezone_offset}\n")

    failures = []
    # alive-progress bar for consistent UX
    with alive_bar(
        len(image_files),
        title="Correcting timestamps",
        bar="smooth",
        spinner="waves",
        dual_line=True,
        enrich_print=True,
    ) as bar:
        for image_file in image_files:
            bar.text(f"{image_file.name}")
            # Construct the ExifTool command to adjust date, timezone, and "SonyDateTime" tags
            command = [
                "exiftool",
                f'-DateTimeOriginal{date_operator}={time_offset}',
                f'-CreateDate{date_operator}={time_offset}',
                f'-ModifyDate{date_operator}={time_offset}',
                f'-SonyDateTime{date_operator}={time_offset}',
                f'-OffsetTime+={timezone_offset}',
                f'-OffsetTimeOriginal+={timezone_offset}',
                f'-OffsetTimeDigitized+={timezone_offset}',
                "-overwrite_original",  # Don't create backup files
                str(image_file),
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
                failures.append((image_file.name, f"exiftool exited with {return_code}"))
                print(f"exiftool failed for {image_file.name}")
            else:
                print(f"Updated {image_file.name}")

            bar()

    if failures:
        print("\nCompleted with failures:")
        for filename, reason in failures:
            print(f" - {filename}: {reason}")
        return 1

    print("\nAll timestamps corrected successfully.")
    return 0


def main() -> int:
    directory = Path("/work")
    
    # Read timezone difference from environment variable
    timezone_str = os.environ.get("TIMEZONE_OFFSET")
    if not timezone_str:
        print("Error: TIMEZONE_OFFSET environment variable not set")
        return 1
    
    try:
        timezone_difference = parse_timezone_input(timezone_str)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    return correct_timestamps_in_directory(directory, timezone_difference)


if __name__ == "__main__":
    raise SystemExit(main())
