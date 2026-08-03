import base64
import math
import os
import wave
from io import BytesIO

os.environ.setdefault("ZARA_LOCAL_TESTING", "true")
os.environ.setdefault("ZARA_JWT_SECRET", "local-test-secret")
os.environ.setdefault("ZARA_DATA_DIR", "data/test")

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from zara_ai_server.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture(scope="session")
def sample_image_b64():
    image = Image.new("RGB", (64, 64), (20, 100, 220))
    out = BytesIO()
    image.save(out, format="JPEG")
    return base64.b64encode(out.getvalue()).decode()

@pytest.fixture(scope="session")
def sample_audio_b64():
    sample_rate = 16000
    frames = bytearray()
    for i in range(sample_rate // 4):
        value = int(8000 * math.sin(2 * math.pi * 440 * i / sample_rate))
        frames.extend(value.to_bytes(2, "little", signed=True))
    out = BytesIO()
    with wave.open(out, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(bytes(frames))
    return base64.b64encode(out.getvalue()).decode()
