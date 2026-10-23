# ZaraOS Build Report

## Firmware

- Command: `idf.py fullclean && idf.py build`
- Status: Pending environment setup
- Detail: ESP-IDF is not installed in this container, so `idf.py` is unavailable and firmware compilation must be run in an ESP-IDF-enabled environment.

## AI Server

- Command: `python3 ai_server/main.py`
- Status: Pass for server startup
- Detail: The HTTP server starts and exposes real-inference endpoints. Endpoints now require actual model runtimes and return errors instead of placeholder inference when dependencies or weights are missing.

## Dependency and model installation

- Command: `python3 -m pip install --user -e 'ai_server[test,ai]'`
- Status: Blocked by environment
- Detail: The configured package index/network tunnel returned `403 Forbidden`, preventing installation or automatic model downloads for Qwen2.5, Whisper, Piper, YOLO11n, PaddleOCR, InsightFace buffalo_l, SentenceTransformers, and FAISS.
