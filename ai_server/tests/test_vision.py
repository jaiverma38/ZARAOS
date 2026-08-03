def test_yolo_and_ocr_vision_endpoint(client, sample_image_b64):
    response = client.post("/v1/vision/analyze", json={"prompt": "what do you see", "binary_base64": sample_image_b64})
    assert response.status_code == 200
    result = response.json()["result"]
    assert "objects" in result
    assert "ocr" in result
    assert "brightness" in result
