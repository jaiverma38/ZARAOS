import math
import wave
from io import BytesIO
import numpy as np

class LocalMemoryStore:
    def __init__(self):
        self.rows = []
        self.face_rows = []

    def add_memory(self, device_id: str, kind: str, text: str, metadata: dict) -> int:
        self.rows.append((device_id, kind, text, metadata))
        return len(self.rows)

    def save_face(self, owner_id: str, name: str, embedding: np.ndarray, metadata: dict) -> None:
        self.face_rows.append((owner_id, name, embedding, metadata))

    def faces(self):
        return [(row[0], row[1], row[2]) for row in self.face_rows]

class LocalLlmEngine:
    def chat(self, text: str, locale: str, memories: list[str] | None = None) -> str:
        if locale.startswith("hi"):
            return f"Namaste, main Zara hoon. Aapne kaha: {text}"
        return f"Hello, I am Zara. You said: {text}"

    def intent(self, text: str, locale: str) -> dict:
        lowered = text.lower()
        if "follow" in lowered or "paas" in lowered or "aao" in lowered:
            return {"intent": "robot_move", "action": "follow_user", "confidence": 0.99}
        if "stop" in lowered or "ruk" in lowered:
            return {"intent": "robot_stop", "action": "stop", "confidence": 0.99}
        return {"intent": "chat", "action": "speak", "confidence": 0.75, "text": self.chat(text, locale)}

class LocalVisionEngine:
    def analyze(self, image: np.ndarray, prompt: str) -> dict:
        brightness = float(np.mean(image)) if image.size else 0.0
        dominant = [int(x) for x in image.reshape(-1, 3).mean(axis=0)] if image.size else [0, 0, 0]
        return {"prompt": prompt, "objects": [], "persons": 0, "ocr": [], "brightness": brightness, "dominant_rgb": dominant}

class LocalFaceEngine:
    def __init__(self):
        self.embedding = [1.0] + [0.0] * 511

    def enroll(self, name: str, image: np.ndarray, role: str) -> dict:
        return {"enrolled": True, "owner_id": f"{role}-local", "owner_name": name, "embedding": self.embedding, "role": role}

    def recognize(self, image: np.ndarray) -> dict:
        return {"recognized": True, "owner_id": "owner-local", "name": "Owner", "score": 1.0}

class LocalSpeechEngine:
    def transcribe(self, audio_bytes: bytes, suffix: str = ".wav") -> dict:
        return {"text": "Hello Zara", "language": "en", "segments": []}

    def synthesize(self, text: str) -> bytes:
        sample_rate = 16000
        frames = bytearray()
        for i in range(sample_rate // 4):
            value = int(12000 * math.sin(2 * math.pi * 440 * i / sample_rate))
            frames.extend(value.to_bytes(2, "little", signed=True))
        out = BytesIO()
        with wave.open(out, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(bytes(frames))
        return out.getvalue()
