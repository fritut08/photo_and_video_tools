import os
import subprocess
import glob
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm

def select_directory():
    print("Select the directory:")
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title="Image Files")
    print(f"Selected directory: {directory}\n")
    return directory

def copy_tags_from_xmp(xmp_path, image_path):
    subprocess.run(['exiftool', '-tagsfromfile', xmp_path, '-location:all', '-@', 'xmp2exif.args', image_path])

def process_directory(dir_path):
    xmp_files = glob.glob(os.path.join(dir_path, '*.xmp'))
    for xmp_path in tqdm(xmp_files, desc="Processing files"):
        for ext in ['jpg', 'jpeg']:
            image_path = xmp_path.rsplit('.', 1)[0] + '.' + ext
            if os.path.exists(image_path):
                copy_tags_from_xmp(xmp_path, image_path)

if __name__ == "__main__":
    # Select the directory using the GUI
    directory_path = select_directory()
    process_directory(directory_path)