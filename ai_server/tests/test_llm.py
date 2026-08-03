def test_llm_chat(client):
    response = client.post("/v1/llm/chat", json={"message": "Hello Zara"})
    assert response.status_code == 200
    assert response.json()["result"]["text"]

def test_llm_intent_follow_user(client):
    response = client.post("/v1/llm/intent", json={"message": "Zara mere paas aao"})
    assert response.status_code == 200
    assert response.json()["action"] == "follow_user"
