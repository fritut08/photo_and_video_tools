# Stage 1: Build Node.js parser dependencies
FROM node:20-slim AS parser-build

WORKDIR /parser
COPY DJI_SRT_Parser/package*.json ./
RUN npm ci --only=production

# Stage 2: Final runtime image
FROM python:3.11-slim

# Install exiftool and Node.js runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends exiftool nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy parser with dependencies
WORKDIR /parser
COPY --from=parser-build /parser/node_modules ./node_modules
COPY DJI_SRT_Parser .

WORKDIR /app