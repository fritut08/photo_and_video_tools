"""Add subtitle tracks from SRT files into MP4 video files."""

import shutil
import subprocess
from pathlib import Path

from alive_progress import alive_bar


WORK_DIR = Path("/work")
TEMP_DIR = Path("/tmp/processing")
OUTPUT_DIR = WORK_DIR / "videos_with_merged_subtitles"


if __name__ == "__main__":

    # Collect SRT files
    srt_files = [
        file for file in WORK_DIR.iterdir() if file.is_file() and file.suffix.lower() == ".srt"
    ]

    # Find matching MP4 files
    pairs: list[tuple[Path, Path]] = []
    for srt_file in srt_files:
        stem = srt_file.stem
        for ext in [".mp4", ".MP4"]:
            mp4_candidate = WORK_DIR / f"{stem}{ext}"
            if mp4_candidate.exists():
                pairs.append((srt_file, mp4_candidate))
                break
    
    if not pairs:
        print("No matching SRT + MP4 pairs found. Abort.")
        raise SystemExit(0)
    
    print(f"Found {len(pairs)} SRT + MP4 pairs to process.")
    
    # Create temp and output directories
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Process each pair
    processed = 0
    failed = 0
    
    with alive_bar(
        len(pairs),
        title="Merging SRT with MP4",
        bar="smooth",
        spinner="waves",
        dual_line=True,
        enrich_print=True,
    ) as bar:
        for srt_file, mp4_file in pairs:

            # Copy file into container for fast processing
            bar.text(f"Copying {mp4_file.name} into container")

            temp_input = TEMP_DIR / f"in_{mp4_file.name}"
            temp_output = TEMP_DIR / f"out_{mp4_file.name}"
            
            try:
                shutil.copy2(mp4_file, temp_input)
            except Exception as e:
                print(f"✗ Failed to copy {mp4_file.name} into container: {e}")
                failed += 1
                bar()
                continue
                    
            # Process on container's filesystem (turned out to be faster)
            bar.text(f"Processing {mp4_file.name}")

            command = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel", "warning",
                "-y",
                "-i", str(temp_input),
                "-i", str(srt_file),
                "-c", "copy",
                "-c:s", "mov_text",
                str(temp_output),
            ]

            # Execute ffmpeg and stream output so the progress bar stays clean
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
                print(f"✗ Failed to process {mp4_file.name} (ffmpeg exit code {return_code})")
                failed += 1
            else:
                # Copy result back to mount
                bar.text(f"Copying back {mp4_file.name} to host")
                final_output = OUTPUT_DIR / mp4_file.name
                try:
                    shutil.copy2(temp_output, final_output)
                    print(f"✓ Processed {mp4_file.name}")
                    processed += 1
                except Exception as e:
                    print(f"✗ Failed to copy {mp4_file.name} back to host: {e}")
                    failed += 1
            
            # Cleanup temp files
            temp_input.unlink(missing_ok=True)
            temp_output.unlink(missing_ok=True)

            bar()

    print(f"Processed: {processed}")
    print(f"Failed: {failed}")
    
    print(f"Output written to: {OUTPUT_DIR}")

    if failed != 0:
        print("Completed with failures!")
        raise SystemExit(1)
    
    raise SystemExit(0)
