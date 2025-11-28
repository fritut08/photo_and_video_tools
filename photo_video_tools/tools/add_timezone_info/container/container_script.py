"""Add timezone information to image files using ExifTool."""

import sys
import subprocess
from pathlib import Path
from alive_progress import alive_bar

WORK_DIR = Path("/work")
OUTPUT_DIR = WORK_DIR / "photos_with_added_timezone_info"
SUPPORTED_EXTENSIONS = {'.dng', '.arw', '.jpg', '.jpeg'}


if __name__ == "__main__":
	# Parse timezone info from command-line argument in format <hours>:<minutes>
	if len(sys.argv) != 2:
		print("Usage: python container_script.py <sign><hours>:<minutes>")
		print("Example: python container_script.py -9:30")
		raise SystemExit(1)
	timezone_info = sys.argv[1]

	# Get all ARW and JPEG files in the directory
	image_files = [
		file for file in WORK_DIR.iterdir()
		if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
	]

	if not image_files:
		print(f"No supported image files found. Abort.")
		raise SystemExit(0)
	
	print(f"Found {len(image_files)} image files to process.")

	# Ensure output directory exists
	OUTPUT_DIR.mkdir(exist_ok=True)

	# Process each image file
	print(f"Processing {len(image_files)} files with timezone offset: {timezone_info} hours")

	processed = 0
	failed = 0
	
	with alive_bar(
		len(image_files),
		title="Adding Timezone Information",
		bar="smooth",
		spinner="waves",
		dual_line=True,
		enrich_print=True,
	) as bar:
		for image_file in image_files:
			bar.text(f"{image_file.name}")
			# Construct the ExifTool command
			output_path = OUTPUT_DIR / image_file.name
			command = [
				"exiftool",
				'-m', # ignore maker notes offset warning
				f'-OffsetTime={timezone_info}',
				f'-OffsetTimeOriginal={timezone_info}',
				f'-OffsetTimeDigitized={timezone_info}',
				"-o", str(output_path),  # Write corrected copy to output directory
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
				print(f"✗ Failed to process {image_file.name} (exiftool exit code {return_code})")
				failed += 1
			else:
				print(f"✓ Processed {image_file.name}")
				processed += 1

			bar()

	print(f"Processed: {processed}")
	print(f"Failed: {failed}")
	
	print(f"Output written to: {OUTPUT_DIR}")

	if failed != 0:
		print("Completed with failures!")
		raise SystemExit(1)
	
	raise SystemExit(0)