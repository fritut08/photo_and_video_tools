# correct_timezone

This is a Python script one can use to correct timestamps of photo files (`.arw`, `.jpg`, `.jpeg`) if the photos were taken with a camera that was not set to the correct timezone. The script calls the [exiftool](https://github.com/exiftool/exiftool). This will therefore either have to be in the system's PATH variable or located in the same folder as this script.

The script will ask for a timezone difference and then correct the metadata of all files in a selected directory.

Example: Photos were taken in timezone UTC-2 but the camera was set to UTC+1. Thus, pictures taken at 14:00 local time will have an incorrect timestamp of 17:00. If `-3` is entered as the timezone difference, this script will correct the metadata as necessary. This includes not only the time but also the date and timezone parameters of the files' exif data.

This script was written with ChatGPT.
