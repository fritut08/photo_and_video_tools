FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl exiftool \
    && rm -rf /var/lib/apt/lists/*

# Fetch the xmp2exif.args file used by exiftool to map XMP -> EXIF
WORKDIR /exiftool_args_file
RUN curl -fsSL -o xmp2exif.args \
    https://raw.githubusercontent.com/exiftool/exiftool/master/arg_files/xmp2exif.args

WORKDIR /app
