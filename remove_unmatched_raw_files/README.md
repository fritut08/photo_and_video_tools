# remove_unmatched_raw_files

Move RAW `.ARW` files that have no matching `.jpg`/`.jpeg` file into a subfolder named `removed raw files` inside the RAW directory.

## What it solves
If setup accordingly, Sony cameras will generate two files for every photo taken with it: a RAW (`.ARW`) and a JPEG (`.JPG`/`.JPEG`) file. You can first curate the JPEGs (delete the bad shots) and then this tool safely relocates the RAW files that no longer have a JPEG counterpart, so you keep only RAW versions of the photos you actually want to keep.

## Run

```powershell
python remove_unmatched_raw_files.py
```

What it does:
- Prompts for the JPEG directory, then the RAW directory via GUI folder pickers.
- Compares filenames (supports `.jpg`, `.jpeg`, `.JPG`, `.JPEG`, `.arw`, `.ARW`).
- Lists unmatched RAW files and asks for explicit confirmation (`YES`).
- Moves unmatched RAW files into `<RAW directory>/removed raw files`.
- Leaves original JPEGs untouched.