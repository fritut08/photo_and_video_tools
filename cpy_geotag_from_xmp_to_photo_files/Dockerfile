FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl exiftool \
    && rm -rf /var/lib/apt/lists/*

# Fetch the xmp2exif.args file used by exiftool to map XMP -> EXIF
# Pinned to upstream master raw URL; adjust if needed.
WORKDIR /app
RUN curl -fsSL -o xmp2exif.args \
    https://raw.githubusercontent.com/exiftool/exiftool/master/arg_files/xmp2exif.args

COPY container/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY container/cpy_geotag_from_xmp_to_photo_files.py .

ENTRYPOINT ["python", "/app/cpy_geotag_from_xmp_to_photo_files.py"]
