import os
import shutil
import tkinter as tk
from tkinter import filedialog

def select_directory(title):
    print(f"Select the directory for {title}:")
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title=title)
    print(f"Selected {title} directory: {directory}\n")
    return directory

if __name__ == "__main__":
    # Select directory for jpg files
    print("Waiting for directory selection...")
    input("Press Enter to select the directory for JPG files...")
    jpg_directory = select_directory("JPG Files")
    if not jpg_directory:
        print("No directory selected for JPG files.")
        input("Press Enter to exit...")
        exit()

    # Select directory for raw files
    print("Waiting for directory selection...")
    input("Press Enter to select the directory for RAW files...")
    raw_directory = select_directory("RAW Files")
    if not raw_directory:
        print("No directory selected for RAW files.")
        input("Press Enter to exit...")
        exit()

    # Get the list of jpg files
    jpg_files = set()
    for filename in os.listdir(jpg_directory):
        if filename.lower().endswith('.jpg'):
            jpg_files.add(filename.split('.')[0])

    # Get the list of raw files
    raw_files = set()
    for filename in os.listdir(raw_directory):
        if filename.lower().endswith('.arw'):
            raw_files.add(filename.split('.')[0])

    # Find raw files without corresponding jpg files
    files_to_delete = []
    for raw_file in raw_files:
        if raw_file not in jpg_files:
            files_to_delete.append(raw_file)

    # Display information and ask for confirmation
    num_files_to_delete = len(files_to_delete)
    if num_files_to_delete > 0:
        print("Number of files to be deleted:", num_files_to_delete)
        print("Files to be deleted:")
        for file in files_to_delete:
            print(file)

        confirmation = input(f"Do you want to delete {num_files_to_delete} files? (yes/no): ")
        if confirmation.lower() in ['yes', 'y']:
            # Delete raw files
            for file in files_to_delete:
                raw_file_path = os.path.join(raw_directory, file + '.ARW')
                os.remove(raw_file_path)
            print("Files deleted successfully.")
        else:
            print("Deletion canceled by user.")
    else:
        print("No files to delete.")

    input("Press Enter to exit...")
