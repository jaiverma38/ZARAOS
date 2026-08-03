# ZaraOS

Production ESP-IDF C++17 firmware architecture for an ESP32-S3-WROOM-1 robot with 16 MB flash and 8 MB PSRAM.

## Build

```bash
idf.py set-target esp32s3
idf.py build
```

## Hardware

All GPIO assignments are centralized in `components/zaraos/config/pins.h`; do not hardcode pins in drivers.

## AI integration

ZaraOS includes a secure cloud AI client in `components/ai_client`. The ESP32-S3 connects directly to an AI server over HTTPS using certificate-bundle TLS validation and JWT bearer authentication stored in encrypted NVS. The server can host Qwen2.5, Qwen3, Llama-compatible LLMs, Whisper/Whisper.cpp STT, Piper TTS, InsightFace/ArcFace, YOLO11n/YOLOv8n, and Qwen Vision-compatible services.

Firmware responsibilities remain real-time and embedded: robot control, sensors, camera/audio capture, display, MQTT/OTA, secure storage, and offline local-control behavior. Cloud AI responsibilities include LLM reasoning, intent recognition, tool calling, STT/TTS, face embedding/recognition, object detection, OCR, image understanding, and long-term memory backup.

## Features

The project is organized into independent components for audio, wake voice, camera/vision, robot motion, sensors, display, AI, persistent memory, security, network, MQTT, OTA, diagnostics, storage, and a dedicated `ai_client` communication layer. Runtime code uses ESP-IDF, FreeRTOS primitives, encrypted NVS, LittleFS partitioning, HTTPS certificate validation, JWT authentication, and OTA partitions.


## AI Server

The matching Dockerized backend lives in `ai_server/`. It provides `/v1/llm/chat`, `/v1/llm/intent`, `/v1/vision/analyze`, `/v1/faces/enroll`, `/v1/faces/recognize`, `/v1/voice/stt`, and `/v1/voice/tts` for the firmware AI client.
