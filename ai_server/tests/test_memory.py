from zaraos_ai.memory import ConversationMemory


def test_memory_returns_records_in_chronological_order():
    memory = ConversationMemory()
    first = memory.add("session", "user", "one")
    second = memory.add("session", "assistant", "two")

    records = memory.recent("session")

    assert [record.id for record in records] == [first, second]
    assert [record.text for record in records] == ["one", "two"]
