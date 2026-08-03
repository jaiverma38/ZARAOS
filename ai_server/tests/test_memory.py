from zara_ai_server.services.runtime import memory_store

def test_memory_store_adds_conversation():
    memory_id = memory_store().add_memory("test-device", "conversation", "hello zara", {"test": True})
    assert memory_id > 0
