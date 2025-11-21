FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY container/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY container/merge_srt_with_mp4.py .

ENTRYPOINT ["python", "/app/merge_srt_with_mp4.py"]
