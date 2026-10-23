from __future__ import annotations

import base64
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


from .memory import ConversationMemory

SUPPORTED_LLM_MODELS = {"qwen2.5", "qwen3", "llama-compatible"}
DEFAULT_LLM_MODEL = "qwen2.5"
DEFAULT_MODEL_IDS = {
    "qwen2.5": "Qwen/Qwen2.5-0.5B-Instruct",
    "qwen3": "Qwen/Qwen3-0.6B",
    "llama-compatible": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "sentence_transformers": "sentence-transformers/all-MiniLM-L6-v2",
    "whisper": "base",
    "yolo11n": "yolo11n.pt",
    "insightface": "buffalo_l",
}


class ModelUnavailable(RuntimeError):
    """Raised when a required real model runtime or weight is unavailable."""


class ZaraAiService:
    def __init__(self, memory: ConversationMemory | None = None) -> None:
        self.memory = memory or ConversationMemory(os.getenv("ZARAOS_MEMORY_DB", ":memory:"))
        self._llm: tuple[Any, Any] | None = None
        self._whisper: Any | None = None
        self._yolo: Any | None = None
        self._ocr: Any | None = None
        self._face: Any | None = None
        self._embedder: Any | None = None
        self._faiss_index: Any | None = None
        self._owner_embedding: list[float] | None = None
        self._owner_name = "Owner"

    def health(self) -> dict[str, Any]:
        components = {name: self._component_status(name) for name in (
            "llm", "whisper", "piper", "yolo11n", "paddleocr", "insightface", "sentence_transformers", "faiss", "memory"
        )}
        status = "ready" if all(value == "ready" for value in components.values()) else "degraded"
        return {"status": status, "components": components}

    def chat(self, session_id: str, text: str, owner_id: str | None = None) -> dict[str, Any]:
        del owner_id
        tokenizer, model = self._load_llm()
        self.memory.add(session_id, "user", text)
        context = "\n".join(f"{item.role}: {item.text}" for item in self.memory.recent(session_id))
        prompt = f"You are ZaraOS, an embodied robot assistant.\n{context}\nuser: {text}\nassistant:"
        inputs = tokenizer(prompt, return_tensors="pt")
        generated = model.generate(**inputs, max_new_tokens=int(os.getenv("ZARAOS_LLM_MAX_NEW_TOKENS", "128")))
        answer = tokenizer.decode(generated[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True).strip()
        self.memory.add(session_id, "assistant", answer)
        memories = self.memory.search(text)
        return {
            "text": answer,
            "model": self._llm_model_name(),
            "memory_refs": [str(item.id) for item in memories],
            "robot_command": self.intent(answer).get("robot_command"),
        }

    def intent(self, text: str) -> dict[str, Any]:
        tokenizer, model = self._load_llm()
        prompt = (
            "Extract a ZaraOS robot intent as compact JSON with keys name, confidence, "
            "and robot_command {linear_mps, angular_rps, duration_ms} or null. Text: "
            f"{text}"
        )
        inputs = tokenizer(prompt, return_tensors="pt")
        generated = model.generate(**inputs, max_new_tokens=96)
        decoded = tokenizer.decode(generated[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True).strip()
        return {"name": "llm_intent", "text": decoded, "confidence": 1.0, "robot_command": None}

    def enroll_face(self, image_base64: str, name: str = "Owner") -> dict[str, Any]:
        faces = self._face_embeddings(image_base64)
        if not faces:
            raise ModelUnavailable("InsightFace buffalo_l did not detect a face to enroll")
        self._owner_embedding = faces[0]
        self._owner_name = name or "Owner"
        return {"id": "owner", "name": self._owner_name, "owner": True, "confidence": 1.0}

    def recognize_face(self, image_base64: str) -> dict[str, Any]:
        if self._owner_embedding is None:
            enrolled = self.enroll_face(image_base64)
            return {"owner_enrolled": True, "faces": [enrolled], "objects": [], "ocr_text": []}
        faces = []
        for embedding in self._face_embeddings(image_base64):
            score = self._cosine(self._owner_embedding, embedding)
            if score >= float(os.getenv("ZARAOS_FACE_THRESHOLD", "0.35")):
                faces.append({"id": "owner", "name": self._owner_name, "owner": True, "confidence": max(0.0, min(1.0, score))})
        return {"owner_enrolled": False, "faces": faces, "objects": [], "ocr_text": []}

    def analyze_vision(self, image_base64: str) -> dict[str, Any]:
        image = self._decode_image(image_base64)
        objects = self._detect_objects(image)
        ocr_text = self._read_ocr(image)
        faces = self.recognize_face(image_base64)
        return {**faces, "objects": objects, "ocr_text": ocr_text}

    def stt(self, audio_base64: str) -> dict[str, Any]:
        model = self._load_whisper()
        audio = base64.b64decode(audio_base64.encode("ascii"), validate=True)
        with tempfile.NamedTemporaryFile(suffix=".wav") as wav:
            wav.write(audio)
            wav.flush()
            result = model.transcribe(wav.name)
        return {"text": result.get("text", "").strip(), "engine": "whisper", "status": "ready"}

    def tts(self, text: str) -> dict[str, Any]:
        piper_bin = os.getenv("ZARAOS_PIPER_BIN", "piper")
        voice = os.getenv("ZARAOS_PIPER_VOICE")
        if not voice:
            raise ModelUnavailable("ZARAOS_PIPER_VOICE must point to a Piper .onnx voice model")
        with tempfile.NamedTemporaryFile(suffix=".wav") as wav:
            cmd = [piper_bin, "--model", voice, "--output_file", wav.name]
            subprocess.run(cmd, input=text.encode("utf-8"), check=True)
            encoded = base64.b64encode(Path(wav.name).read_bytes()).decode("ascii")
        return {"audio_base64": encoded, "engine": "piper", "sample_rate": 22050, "status": "ready"}

    def verify_models(self) -> dict[str, Any]:
        checks = {
            "qwen2.5": lambda: self._load_llm("qwen2.5"),
            "whisper": self._load_whisper,
            "piper": self._verify_piper,
            "yolo11n": self._load_yolo,
            "paddleocr": self._load_ocr,
            "insightface": self._load_face,
            "sentence_transformers": self._load_embedder,
            "faiss": self.memory.ensure_vector_index,
        }
        results = {}
        for name, check in checks.items():
            try:
                check()
                results[name] = {"installed": True, "status": "ready"}
            except Exception as exc:  # noqa: BLE001 - endpoint reports each model validation failure.
                results[name] = {"installed": False, "status": "unavailable", "detail": str(exc)}
        return {"models": results}

    def simulate(self, audio_base64: str, image_base64: str) -> dict[str, Any]:
        voice = self.stt(audio_base64)
        llm = self.chat("simulator", voice["text"])
        intent = self.intent(llm["text"])
        vision = self.analyze_vision(image_base64)
        return {"voice": voice, "llm": llm, "intent": intent, "vision": vision, "robot": intent.get("robot_command")}

    def _llm_model_name(self) -> str:
        key = os.getenv("ZARAOS_LLM_MODEL", DEFAULT_LLM_MODEL).lower()
        if key not in SUPPORTED_LLM_MODELS:
            key = DEFAULT_LLM_MODEL
        return os.getenv("ZARAOS_LLM_MODEL_ID", DEFAULT_MODEL_IDS[key])

    def _load_llm(self, family: str | None = None) -> tuple[Any, Any]:
        if self._llm is not None and family is None:
            return self._llm
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise ModelUnavailable("transformers is required for Qwen/Llama inference") from exc
        model_id = os.getenv("ZARAOS_LLM_MODEL_ID", DEFAULT_MODEL_IDS[family or os.getenv("ZARAOS_LLM_MODEL", DEFAULT_LLM_MODEL).lower()])
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
        self._llm = (tokenizer, model)
        return self._llm

    def _load_whisper(self) -> Any:
        if self._whisper is None:
            try:
                import whisper
            except ImportError as exc:
                raise ModelUnavailable("openai-whisper is required for STT") from exc
            self._whisper = whisper.load_model(os.getenv("ZARAOS_WHISPER_MODEL", DEFAULT_MODEL_IDS["whisper"]))
        return self._whisper

    def _verify_piper(self) -> None:
        if not os.getenv("ZARAOS_PIPER_VOICE"):
            raise ModelUnavailable("ZARAOS_PIPER_VOICE must point to a Piper .onnx voice model")
        subprocess.run([os.getenv("ZARAOS_PIPER_BIN", "piper"), "--help"], check=True, stdout=subprocess.DEVNULL)

    def _load_yolo(self) -> Any:
        if self._yolo is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:
                raise ModelUnavailable("ultralytics is required for YOLO11n inference") from exc
            self._yolo = YOLO(os.getenv("ZARAOS_YOLO_MODEL", DEFAULT_MODEL_IDS["yolo11n"]))
        return self._yolo

    def _load_ocr(self) -> Any:
        if self._ocr is None:
            try:
                from paddleocr import PaddleOCR
            except ImportError as exc:
                raise ModelUnavailable("paddleocr is required for OCR inference") from exc
            self._ocr = PaddleOCR(use_angle_cls=True, lang=os.getenv("ZARAOS_OCR_LANG", "en"))
        return self._ocr

    def _load_face(self) -> Any:
        if self._face is None:
            try:
                from insightface.app import FaceAnalysis
            except ImportError as exc:
                raise ModelUnavailable("insightface is required for buffalo_l face recognition") from exc
            app = FaceAnalysis(name=os.getenv("ZARAOS_INSIGHTFACE_MODEL", DEFAULT_MODEL_IDS["insightface"]))
            app.prepare(ctx_id=int(os.getenv("ZARAOS_FACE_CTX_ID", "-1")))
            self._face = app
        return self._face

    def _load_embedder(self) -> Any:
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise ModelUnavailable("sentence-transformers is required for semantic memory") from exc
            self._embedder = SentenceTransformer(os.getenv("ZARAOS_EMBEDDING_MODEL", DEFAULT_MODEL_IDS["sentence_transformers"]))
            self.memory.configure_embedder(self._embedder)
        return self._embedder

    def _component_status(self, name: str) -> str:
        if name == "memory":
            return "ready"
        return "ready" if self.verify_models()["models"].get(name, {}).get("status") == "ready" else "unavailable"

    def _decode_image(self, image_base64: str) -> Any:
        try:
            import cv2
            import numpy as np
        except ImportError as exc:
            raise ModelUnavailable("opencv-python is required to decode vision images") from exc
        data = np.frombuffer(base64.b64decode(image_base64.encode("ascii"), validate=True), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("image_base64 is not a decodable image")
        return image

    def _detect_objects(self, image: Any) -> list[dict[str, Any]]:
        yolo = self._load_yolo()
        detections = []
        for result in yolo(image):
            names = result.names
            for box in result.boxes:
                cls = int(box.cls[0])
                detections.append({"label": names[cls], "confidence": float(box.conf[0]), "box": [float(v) for v in box.xyxy[0].tolist()]})
        return detections

    def _read_ocr(self, image: Any) -> list[str]:
        ocr = self._load_ocr()
        results = ocr.ocr(image, cls=True)
        lines: list[str] = []
        for page in results or []:
            for item in page or []:
                if len(item) >= 2:
                    lines.append(str(item[1][0]))
        return lines

    def _face_embeddings(self, image_base64: str) -> list[list[float]]:
        image = self._decode_image(image_base64)
        app = self._load_face()
        faces = app.get(image)
        return [[float(value) for value in face.embedding] for face in faces]

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = sum(a * a for a in left) ** 0.5
        right_norm = sum(b * b for b in right) ** 0.5
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return max(0.0, min(1.0, dot / (left_norm * right_norm)))
