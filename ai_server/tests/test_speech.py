def test_whisper_stt(client, sample_audio_b64):
    response = client.post("/v1/voice/stt", json={"binary_base64": sample_audio_b64})
    assert response.status_code == 200
    assert response.json()["result"]["text"]

def test_piper_tts(client):
    response = client.post("/v1/voice/tts", json={"message": "Hello"})
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["audio_format"] == "wav"
    assert result["audio_base64"]
