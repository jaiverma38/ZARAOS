# ZaraOS AI Server

FastAPI service that fronts ZaraOS cloud/edge AI capabilities for ESP32 firmware integration.

## Current scope

- Health endpoint with per-pipeline readiness.
- Chat and intent endpoints backed by real Qwen/Llama-compatible `transformers` inference.
- Whisper STT, Piper TTS, YOLO11n object detection, PaddleOCR text extraction, InsightFace buffalo_l face recognition, SentenceTransformers embeddings, and FAISS memory search loaders.
- Vision endpoints that require real image decoding and model inference; missing runtimes are reported as errors rather than mocked.

## Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[test]
uvicorn zaraos_ai.app:app --host 0.0.0.0 --port 8080
```

## Test

```bash
pip install -e .[test]
pytest
```

## API contracts

- `POST /v1/llm/chat`
- `POST /v1/llm/intent`
- `POST /v1/faces/enroll`
- `POST /v1/faces/recognize`
- `POST /v1/vision/analyze`
- `POST /v1/voice/stt`
- `POST /v1/voice/tts`
- `POST /v1/simulator/run`
- `GET /v1/models/verify`

When FastAPI is unavailable, `python main.py` starts a standard-library HTTP server exposing the same core JSON endpoints. The server still calls the real model integration layer and does not fabricate inference results.
