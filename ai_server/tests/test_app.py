import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from zaraos_ai.app import create_app


def test_health_reports_model_readiness():
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["components"]["memory"] == "ready"


def test_model_verification_endpoint_reports_required_models():
    client = TestClient(create_app())
    response = client.get("/v1/models/verify")
    assert response.status_code == 200
    body = response.json()
    assert "qwen2.5" in body["models"]
    assert "insightface" in body["models"]
