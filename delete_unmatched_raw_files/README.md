# delete_unmatched_raw_files

This is a Python script one can use to delete raw files in one directory that do not correspond to a jpeg file in another directory.

If setup accordingly, Sony cameras will generate two files for every photo taken with it: one raw file (ending in .arw) and one jpeg file (ending in .jpeg).
I usually go through the jpeg files to sort out and delete undesirable photos.
To avoid doing the same thing again with the raw files, I use this Python script, which will match up the names of the jpeg files with those of the raw files and delete the raw files that do not correspond to a jpeg file with the same name.

This script was written with ChatGPT.