import pytest

from zaraos_ai.service import ModelUnavailable, ZaraAiService


def test_real_inference_reports_unavailable_when_model_runtime_is_missing():
    service = ZaraAiService()

    with pytest.raises(ModelUnavailable):
        service.chat("s1", "hello")


def test_model_verification_reports_real_runtime_statuses():
    result = ZaraAiService().verify_models()

    assert set(result["models"]) == {
        "qwen2.5",
        "whisper",
        "piper",
        "yolo11n",
        "paddleocr",
        "insightface",
        "sentence_transformers",
        "faiss",
    }
    assert all("status" in item for item in result["models"].values())
