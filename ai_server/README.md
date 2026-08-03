# Zara AI Server

Dockerized AI inference backend for ZaraOS. It exposes the exact HTTPS endpoints used by the ESP32-S3 firmware AI client and also accepts simplified local JSON bodies for development tests.

## Requirements

- Python 3.11+
- Docker + Docker Compose for container deployment
- 8 GB RAM minimum for local test mode; 16 GB+ RAM recommended for full AI models
- Optional NVIDIA GPU for faster Qwen/Whisper/YOLO inference
- `openssl` for local TLS certificate generation

## Models

- LLM: Qwen2.5-0.5B-Instruct by default; Qwen3 or Llama-compatible Hugging Face causal/chat models can be selected with `ZARA_LLM_MODEL`.
- Face: InsightFace ArcFace embeddings through `FACE_MODEL=buffalo_l`.
- Vision: YOLO11n through `VISION_MODEL=yolo11n.pt`.
- OCR: PaddleOCR.
- STT: Whisper through `WHISPER_MODEL=base`.
- TTS: Piper, using voice files under `PIPER_MODEL_PATH=models/piper`.
- Memory: SQLite plus FAISS vector index with SentenceTransformers embeddings.

## Install on a fresh machine

```bash
cd ai_server
cp .env.example .env
./setup.sh
```

`setup.sh` creates a virtual environment, installs Python dependencies, creates required folders, downloads/load-checks Qwen, YOLO11n, PaddleOCR, InsightFace buffalo_l, Whisper, SentenceTransformers, creates SQLite tables, and creates a self-signed development TLS certificate.

## Run locally

```bash
cd ai_server
./run.sh
```

For fast local endpoint testing, keep `ZARA_LOCAL_TESTING=true` in `.env`. For real inference, set `ZARA_LOCAL_TESTING=false`, ensure the models are downloaded, and provide a Piper `.onnx` voice in `PIPER_MODEL_PATH`.

## Run with Docker

```bash
cd ai_server
docker compose --env-file .env up --build
```

The container serves HTTPS on port `8443` using `ai_server/certs/server.key` and `ai_server/certs/server.crt` as Docker secrets.

## API examples

Local testing mode accepts simple bodies without JWT:

```bash
curl -k -X POST https://localhost:8443/v1/llm/chat -H 'Content-Type: application/json' -d '{"message":"Hello Zara"}'
curl -k -X POST https://localhost:8443/v1/llm/intent -H 'Content-Type: application/json' -d '{"message":"Zara mere paas aao"}'
```

Production ZaraOS requests use the firmware envelope and JWT:

```json
{
  "protocol": "zaraos.ai.v1",
  "device_id": "zara-esp32s3-001",
  "correlation_id": "1234",
  "locale": "hi-IN",
  "timestamp_ms": 123456,
  "payload": {"text": "Zara mere paas aao"}
}
```

## ESP32 connection

1. Generate a JWT with `python scripts/provision_token.py --secret "$ZARA_JWT_SECRET" --device-id zara-esp32s3-001`.
2. Store the AI server HTTPS URL, JWT, and device ID in ZaraOS encrypted NVS through the firmware dashboard/provisioning path.
3. Install the server certificate or use a certificate chain trusted by the ESP-IDF certificate bundle.

## Tests

```bash
cd ai_server
ZARA_LOCAL_TESTING=true pytest tests
python zara_simulator.py --base-url http://localhost:8443 "Zara follow me"
```
