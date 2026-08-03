import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_ENDPOINTS = ["/v1/llm/chat", "/v1/llm/intent", "/v1/vision/analyze", "/v1/faces/enroll", "/v1/faces/recognize", "/v1/voice/stt", "/v1/voice/tts"]

def test_ai_server_routes_match_firmware_contract():
    routes = (ROOT / "ai_server/zara_ai_server/api/routes.py").read_text()
    firmware = (ROOT / "components/ai_client/ai_client.cpp").read_text()
    for endpoint in REQUIRED_ENDPOINTS:
        assert endpoint in routes
        assert endpoint in firmware

def test_python_sources_parse():
    for path in (ROOT / "ai_server").rglob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
