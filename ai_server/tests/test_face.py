def test_face_enroll_and_recognize(client, sample_image_b64):
    enroll = client.post("/v1/faces/enroll", json={"name": "Owner", "role": "owner", "binary_base64": sample_image_b64})
    assert enroll.status_code == 200
    assert enroll.json()["result"]["enrolled"] is True
    recog = client.post("/v1/faces/recognize", json={"binary_base64": sample_image_b64})
    assert recog.status_code == 200
    assert recog.json()["result"]["recognized"] is True
