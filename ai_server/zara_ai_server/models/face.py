import uuid
import cv2
import insightface
import numpy as np
from zara_ai_server.storage.memory import MemoryStore

class FaceEngine:
    def __init__(self, memory: MemoryStore, model_name: str = "buffalo_l"):
        self.memory = memory
        self.app = insightface.app.FaceAnalysis(name=model_name, providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def _largest_face(self, image: np.ndarray):
        faces = self.app.get(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        if not faces:
            return None
        return max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))

    def enroll(self, name: str, image: np.ndarray, role: str) -> dict:
        face = self._largest_face(image)
        if face is None:
            return {"enrolled": False, "reason": "no_face"}
        owner_id = f"{role}-{uuid.uuid4().hex[:12]}"
        embedding = face.normed_embedding.astype("float32")
        self.memory.save_face(owner_id, name, embedding, {"role": role})
        return {"enrolled": True, "owner_id": owner_id, "owner_name": name, "embedding": embedding.tolist(), "role": role}

    def recognize(self, image: np.ndarray) -> dict:
        face = self._largest_face(image)
        if face is None:
            return {"recognized": False, "reason": "no_face"}
        probe = face.normed_embedding.astype("float32")
        best = None
        for owner_id, name, embedding in self.memory.faces():
            score = float(np.dot(probe, embedding) / (np.linalg.norm(probe) * np.linalg.norm(embedding)))
            if best is None or score > best["score"]:
                best = {"owner_id": owner_id, "name": name, "score": score}
        if best and best["score"] >= 0.38:
            best["recognized"] = True
            return best
        return {"recognized": False, "reason": "unknown", "score": best["score"] if best else 0.0}
