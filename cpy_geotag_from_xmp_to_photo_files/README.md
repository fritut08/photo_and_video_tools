# cpy_geotag_from_xmp_to_photo_files

This is a Python script to copy geotag information from sidecar `.xmp` files into the `.jpeg`/`.jpg` files with the same name. The script calls the [exiftool](https://github.com/exiftool/exiftool). This will therefore either have to be in the system's PATH variable or located in the same folder as this script. Furthermore, the scripts needs the `xmp2exif.args` file found [here](https://raw.githubusercontent.com/exiftool/exiftool/master/arg_files/xmp2exif.args) to be present in the directory of the exiftool.
