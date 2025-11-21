"""Add geotag from DJI drone SRT sidecar files to MP4 video files."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from alive_progress import alive_bar

WORK_DIR = Path("/work")
TEMP_DIR = Path("/tmp/processing")
OUTPUT_SUBDIR = "videos_with_geotags"


def parse_first_geotag(srt_path: Path) -> Optional[tuple[float, float, float]]:
    """Extract latitude, longitude, and absolute altitude from the first entry in a DJI SRT file using DJI_SRT_Parser."""
    try:
        result = subprocess.run(
            ["node", "/app/parse_srt.js", str(srt_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout.strip())
            return data["latitude"], data["longitude"], data["altitude"]
        
        if result.stderr:
            print(f"Parser error for {srt_path.name}: {result.stderr.strip()}")
                
    except subprocess.TimeoutExpired:
        print(f"Parser timeout for {srt_path.name}")
    except Exception as e:
        print(f"Error parsing {srt_path.name}: {e}")
    
    return None


def collect_video_srt_pairs(directory: Path) -> list[tuple[Path, Path]]:
    """Find all MP4 files with matching SRT sidecar files."""
    pairs = []
    for mp4_file in list(directory.glob("*.mp4")) + list(directory.glob("*.MP4")):
        for srt_ext in [".srt", ".SRT"]:
            srt_file = mp4_file.with_suffix(srt_ext)
            if srt_file.exists():
                pairs.append((mp4_file, srt_file))
                break
    return pairs


def apply_geotag_to_video(mp4_path: Path, latitude: float, longitude: float, altitude: float, output_path: Path) -> bool:
    """Use exiftool to write GPS coordinates and altitude to MP4 file."""
    cmd = [
        "exiftool",
        f"-GPSLatitude={latitude}",
        f"-GPSLongitude={longitude}",
        f"-GPSAltitude={altitude}",
        "-o", str(output_path),
        str(mp4_path),
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def main() -> int:
    # Collect video/SRT pairs
    pairs = collect_video_srt_pairs(WORK_DIR)
    
    if not pairs:
        print("No MP4 files with matching SRT sidecar files found.")
        return 0
    
    print(f"Found {len(pairs)} video(s) with SRT sidecar files.\n")
    
    # Create temp and output directories
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    output_dir = WORK_DIR / OUTPUT_SUBDIR
    output_dir.mkdir(exist_ok=True)
    
    processed = 0
    skipped = 0
    
    with alive_bar(
        len(pairs),
        title="Adding geotags",
        bar="smooth",
        spinner="waves",
        dual_line=True,
        enrich_print=True,
    ) as bar:
        for mp4_file, srt_file in pairs:
            
            # Parse geotag from SRT            
            bar.text(f"Parsing Geotag from {srt_file.name}")
            geotag = parse_first_geotag(srt_file)
            if geotag is None:
                print(f"✗ Skipped {mp4_file.name} (no geotag found in {srt_file.name})")
                skipped += 1
                bar()
                continue
            
            latitude, longitude, altitude = geotag
            
            # Copy file into container for fast processing
            bar.text(f"Copying {mp4_file.name}")

            temp_input = TEMP_DIR / mp4_file.name
            temp_output = TEMP_DIR / f"out_{mp4_file.name}"
            
            # Check if output already exists to avoid overwriting
            final_output = output_dir / mp4_file.name
            if final_output.exists():
                print(f"✗ Skipped {mp4_file.name} (output already exists)")
                skipped += 1
                bar()
                continue
            
            shutil.copy2(mp4_file, temp_input)
                    
            # Process on container's filesystem (fast)
            bar.text(f"Processing {mp4_file.name}")    
            if apply_geotag_to_video(temp_input, latitude, longitude, altitude, temp_output):
                # Copy result back to mount
                bar.text(f"Copying back {mp4_file.name}")
                shutil.copy2(temp_output, final_output)
                
                print(f"✓ {mp4_file.name} → GPS: {latitude:.6f}, {longitude:.6f}, Alt: {altitude:.1f}m")
                processed += 1
                
                # Cleanup temp files
                temp_input.unlink()
                temp_output.unlink()
            else:
                print(f"✗ Failed to process {mp4_file.name}")
                skipped += 1
                if temp_input.exists():
                    temp_input.unlink()
            
            bar()
    
    print(f"\nProcessed: {processed}")
    if skipped > 0:
        print(f"Skipped: {skipped}")
    
    print(f"\nOutput written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
