FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libglib2.0-0 libgl1 libgomp1 espeak-ng curl ca-certificates openssl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ai_server/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
COPY ai_server/main.py /app/main.py
COPY ai_server/zara_ai_server /app/zara_ai_server
COPY ai_server/scripts /app/scripts
RUN mkdir -p /data /models/piper && python /app/scripts/init_database.py
EXPOSE 8443
CMD ["uvicorn", "zara_ai_server.main:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-keyfile", "/run/secrets/zara_tls_key", "--ssl-certfile", "/run/secrets/zara_tls_cert"]
