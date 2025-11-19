import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm
import exifread
from datetime import datetime

def extract_createdate(file_path):
    with open(file_path, 'rb') as file:
        tags = exifread.process_file(file, details=False)
        createdate_tag = 'EXIF DateTimeOriginal'
        if createdate_tag in tags:
            createdate_str = str(tags[createdate_tag])
            createdate = datetime.strptime(createdate_str, '%Y:%m:%d %H:%M:%S')
            return createdate
        return None

def select_directory():
    print(f"Select the directory:")
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title="Select Directory")
    print(f"Selected directory: {directory}\n")
    return directory

def organize_files_by_createdate(directory_path):
    # Get all JPG and ARW files in the directory
    supported_extensions = {'.jpg', '.arw'}
    image_files = [file for file in os.listdir(directory_path) if os.path.splitext(file.lower())[1] in supported_extensions]

    # Use tqdm to display a progress bar
    for image_file in tqdm(image_files, desc="Organizing files", unit="file"):
        image_file_path = os.path.join(directory_path, image_file)

        # Extract creation date from EXIF data
        createdate = extract_createdate(image_file_path)

        if createdate:
            # Create a subdirectory based on the creation date
            subdirectory = createdate.strftime('%Y-%m-%d')
            subdirectory_path = os.path.join(directory_path, subdirectory)
            os.makedirs(subdirectory_path, exist_ok=True)

            # Move the image file to the appropriate subdirectory
            shutil.move(image_file_path, os.path.join(subdirectory_path, image_file))

if __name__ == "__main__":
    # Select the directory using the GUI
    directory_path = select_directory()

    organize_files_by_createdate(directory_path)
