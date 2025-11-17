FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY merge_subtitles.py .

ENTRYPOINT ["python", "/app/merge_subtitles.py"]
CMD ["--directory", "/work"]
