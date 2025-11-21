# Stage 1: Build Node.js parser dependencies
FROM node:20-slim AS parser-build

WORKDIR /parser
COPY container/DJI_SRT_Parser/package*.json ./
RUN npm ci --only=production

# Stage 2: Final runtime image
FROM python:3.11-slim

# Install exiftool and Node.js runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends exiftool nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy parser with dependencies
COPY --from=parser-build /parser/node_modules ./parser/node_modules
COPY container/DJI_SRT_Parser ./parser

# Python setup
COPY container/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY container/add_geotag_to_dji_drone_video.py .
COPY container/parse_srt.js .

ENTRYPOINT ["python", "/app/add_geotag_to_dji_drone_video.py"]
