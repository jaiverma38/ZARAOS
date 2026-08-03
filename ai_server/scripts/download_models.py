import os
from pathlib import Path
import whisper
from huggingface_hub import snapshot_download
from sentence_transformers import SentenceTransformer
from ultralytics import YOLO
from paddleocr import PaddleOCR
import insightface

llm_model = os.environ.get("ZARA_LLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
face_model = os.environ.get("FACE_MODEL", "buffalo_l")
vision_model = os.environ.get("VISION_MODEL", "yolo11n.pt")
whisper_model = os.environ.get("WHISPER_MODEL", "base")
piper_dir = Path(os.environ.get("PIPER_MODEL_PATH", "models/piper"))
piper_dir.mkdir(parents=True, exist_ok=True)

snapshot_download(llm_model)
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
YOLO(vision_model)
PaddleOCR(use_angle_cls=True, lang="en")
app = insightface.app.FaceAnalysis(name=face_model, providers=["CPUExecutionProvider"])
app.prepare(ctx_id=0, det_size=(640, 640))
whisper.load_model(whisper_model)
print("AI models downloaded and load-checked. Place Piper .onnx voice files in", piper_dir)
