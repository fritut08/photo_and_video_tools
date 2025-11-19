import os
import subprocess
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog

def select_directory():
    print("Select the directory:")
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title="Image Files")
    print(f"Selected directory: {directory}\n")
    return directory

def parse_timezone_input(input_str):
    try:
        return float(input_str)
    except ValueError:
        raise ValueError("Invalid input. Please enter a valid floating-point number.")

def correct_timestamps_in_directory(directory_path, timezone_difference):
    # Get all ARW and JPEG files in the directory
    supported_extensions = {'.arw', '.jpg', '.jpeg'}
    image_files = [file for file in os.listdir(directory_path) if os.path.splitext(file.lower())[1] in supported_extensions]

    # Determine the operator for date tags based on the sign of timezone_difference
    date_operator = "+" if timezone_difference >= 0 else "-"

    # Create the time_offset string in the format 'hh:mm:ss'
    hours, remainder = divmod(abs(timezone_difference) * 3600, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_offset = f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}'

    # Create the timezone_offset string in the format '+HH:MM' or '-HH:MM' for timezone tags
    timezone_offset = f'{date_operator}{int(hours):02d}:{int(minutes):02d}'

    # Use tqdm to display a progress bar
    for image_file in tqdm(image_files, desc="Processing files", unit="file"):
        # Construct the ExifTool command to adjust date, timezone, and "SonyDateTime" tags
        exiftool_command = (
            f'exiftool -DateTimeOriginal{date_operator}="{time_offset}" '
            f'-CreateDate{date_operator}="{time_offset}" '
            f'-ModifyDate{date_operator}="{time_offset}" '
            f'-SonyDateTime{date_operator}="{time_offset}" '
            f'-OffsetTime+="{timezone_offset}" '
            f'-OffsetTimeOriginal+="{timezone_offset}" '
            f'-OffsetTimeDigitized+="{timezone_offset}" '
            f'"{os.path.join(directory_path, image_file)}"'
        )

        # Execute the ExifTool command
        subprocess.run(exiftool_command, shell=True)

if __name__ == "__main__":
    # Select the directory using the GUI
    directory_path = select_directory()

    # Allow user input for timezone difference
    user_input = input("Enter the timezone difference (e.g., -9, 5.5): ")
    try:
        timezone_difference = parse_timezone_input(user_input)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    correct_timestamps_in_directory(directory_path, timezone_difference)
