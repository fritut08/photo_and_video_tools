FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends exiftool \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY container/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY container/correct_timezone.py .

ENTRYPOINT ["python", "/app/correct_timezone.py"]
