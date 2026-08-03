# Zara AI Server Deployment

`ai_server/` contains the runnable backend that pairs with `components/ai_client` in the firmware.

```mermaid
graph LR
  esp[ESP32-S3 ZaraOS] -->|HTTPS JWT TLS| api[FastAPI AI Server]
  api --> llm[Qwen2.5/Qwen3/Llama]
  api --> face[InsightFace ArcFace buffalo_l]
  api --> yolo[YOLO11n]
  api --> ocr[PaddleOCR]
  api --> stt[Whisper]
  api --> tts[Piper]
  api --> mem[SQLite + FAISS]
```

## Fresh machine workflow

1. `cd ai_server && cp .env.example .env`
2. `./setup.sh`
3. `./run.sh`
4. `ZARA_LOCAL_TESTING=true pytest tests`
5. `python zara_simulator.py --base-url http://localhost:8443 "Zara follow me"`

The ESP32 keeps hard real-time responsibilities. The backend performs heavy AI inference and returns JSON commands that match the firmware parser.
