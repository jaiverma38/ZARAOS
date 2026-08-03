import argparse
import base64
import json
import time
from pathlib import Path
import requests

class ZaraSimulator:
    def __init__(self, base_url: str, token: str, device_id: str, verify_tls: bool):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.device_id = device_id
        self.verify_tls = verify_tls

    def envelope(self, payload: dict) -> dict:
        return {"protocol": "zaraos.ai.v1", "device_id": self.device_id, "correlation_id": str(time.time_ns()), "locale": "hi-IN", "timestamp_ms": int(time.time() * 1000), "payload": payload}

    def post(self, path: str, payload: dict) -> dict:
        response = requests.post(self.base_url + path, json=self.envelope(payload), headers=self.headers, timeout=180, verify=self.verify_tls)
        response.raise_for_status()
        return response.json()

    def send_text_command(self, text: str) -> dict:
        return self.post("/v1/llm/intent", {"text": text})

    def send_voice_request(self, wav_path: Path) -> dict:
        return self.post("/v1/voice/stt", {"binary_base64": base64.b64encode(wav_path.read_bytes()).decode()})

    def send_image_request(self, image_path: Path, prompt: str) -> dict:
        return self.post("/v1/vision/analyze", {"prompt": prompt, "binary_base64": base64.b64encode(image_path.read_bytes()).decode()})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8443")
    parser.add_argument("--token", default="")
    parser.add_argument("--device-id", default="zara-simulator")
    parser.add_argument("--verify-tls", action="store_true")
    parser.add_argument("text", nargs="?", default="Zara follow me")
    args = parser.parse_args()
    sim = ZaraSimulator(args.base_url, args.token, args.device_id, args.verify_tls)
    print(json.dumps(sim.send_text_command(args.text), indent=2))
