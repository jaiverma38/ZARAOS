import cv2
import numpy as np
from paddleocr import PaddleOCR
from ultralytics import YOLO

class VisionEngine:
    def __init__(self, model_name: str = "yolo11n.pt"):
        self.detector = YOLO(model_name)
        self.ocr = PaddleOCR(use_angle_cls=True, lang="en")

    def analyze(self, image: np.ndarray, prompt: str) -> dict:
        detections = []
        result = self.detector.predict(image, verbose=False)[0]
        names = result.names
        for box in result.boxes:
            cls = int(box.cls[0])
            xyxy = [float(x) for x in box.xyxy[0].tolist()]
            detections.append({"label": names.get(cls, str(cls)), "confidence": float(box.conf[0]), "box": xyxy})
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        brightness = float(np.mean(gray))
        dominant = image.reshape(-1, 3).mean(axis=0).astype(int).tolist()
        ocr_rows = self.ocr.ocr(image, cls=True)
        texts = []
        for row in ocr_rows or []:
            for item in row or []:
                texts.append({"text": item[1][0], "confidence": float(item[1][1])})
        people = [d for d in detections if d["label"] == "person"]
        return {"prompt": prompt, "objects": detections, "persons": len(people), "ocr": texts, "brightness": brightness, "dominant_rgb": dominant}
