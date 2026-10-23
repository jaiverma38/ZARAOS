from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from zaraos_ai.service import ZaraAiService

service = ZaraAiService()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, service.health())
        elif self.path == "/v1/models/verify":
            self._json(200, service.verify_models())
        else:
            self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        payload = self._payload()
        routes = {
            "/v1/llm/chat": lambda: service.chat(payload["session_id"], payload["text"], payload.get("owner_id")),
            "/v1/chat": lambda: service.chat(payload["session_id"], payload["text"], payload.get("owner_id")),
            "/v1/llm/intent": lambda: service.intent(payload["text"]),
            "/v1/faces/enroll": lambda: service.enroll_face(payload["image_base64"], payload.get("name", "Owner")),
            "/v1/faces/recognize": lambda: service.recognize_face(payload["image_base64"]),
            "/v1/vision/analyze": lambda: service.analyze_vision(payload["image_base64"]),
            "/v1/vision/frame": lambda: service.analyze_vision(payload["image_base64"]),
            "/v1/voice/stt": lambda: service.stt(payload["audio_base64"]),
            "/v1/voice/tts": lambda: service.tts(payload["text"]),
            "/v1/simulator/run": lambda: service.simulate(payload["audio_base64"], payload["image_base64"]),
        }
        if self.path not in routes:
            self._json(404, {"error": "not_found"})
            return
        try:
            self._json(200, routes[self.path]())
        except Exception as exc:  # noqa: BLE001 - stdlib fallback converts bad requests to JSON.
            self._json(400, {"error": str(exc)})

    def log_message(self, format: str, *args: object) -> None:
        return

    def _payload(self) -> dict:
        length = int(self.headers.get("content-length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def _json(self, status: int, body: dict) -> None:
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    print("ZaraOS AI Server listening on http://0.0.0.0:8080", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
