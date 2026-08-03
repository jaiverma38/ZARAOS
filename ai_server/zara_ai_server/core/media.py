import base64
import io
import numpy as np
from PIL import Image

def decode_binary(payload: dict, max_bytes: int) -> bytes:
    encoded = payload.get("binary_base64", "")
    if not encoded:
        return b""
    raw = base64.b64decode(encoded, validate=True)
    if len(raw) > max_bytes:
        raise ValueError("payload too large")
    return raw

def image_from_payload(payload: dict, max_bytes: int) -> np.ndarray:
    raw = decode_binary(payload, max_bytes)
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    return np.array(image)
