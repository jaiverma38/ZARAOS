from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any



@dataclass(frozen=True)
class MemoryRecord:
    id: int
    session_id: str
    role: str
    text: str


class ConversationMemory:
    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS messages ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "session_id TEXT NOT NULL, role TEXT NOT NULL, text TEXT NOT NULL, "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        self._conn.commit()
        self._embedder: Any | None = None
        self._faiss: Any | None = None
        self._index: Any | None = None
        self._index_ids: list[int] = []

    def add(self, session_id: str, role: str, text: str) -> int:
        cur = self._conn.execute(
            "INSERT INTO messages(session_id, role, text) VALUES (?, ?, ?)",
            (session_id, role, text),
        )
        self._conn.commit()
        if self._index is not None and self._embedder is not None:
            vector = self._embedder.encode([text], normalize_embeddings=True).astype("float32")
            self._index.add(vector)
            self._index_ids.append(int(cur.lastrowid))
        return int(cur.lastrowid)

    def recent(self, session_id: str, limit: int = 8) -> list[MemoryRecord]:
        rows = self._conn.execute(
            "SELECT id, session_id, role, text FROM messages "
            "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
        return [MemoryRecord(*row) for row in reversed(rows)]

    def configure_embedder(self, embedder: Any) -> None:
        self._embedder = embedder
        self.ensure_vector_index()

    def ensure_vector_index(self) -> None:
        try:
            import faiss
        except ImportError as exc:
            raise RuntimeError("faiss-cpu is required for vector memory search") from exc
        self._faiss = faiss
        if self._index is None and self._embedder is not None:
            rows = self._conn.execute("SELECT id, text FROM messages ORDER BY id").fetchall()
            dimension = int(self._embedder.get_sentence_embedding_dimension())
            self._index = faiss.IndexFlatIP(dimension)
            self._index_ids = []
            if rows:
                vectors = self._embedder.encode([row[1] for row in rows], normalize_embeddings=True).astype("float32")
                self._index.add(vectors)
                self._index_ids = [int(row[0]) for row in rows]

    def search(self, query: str, limit: int = 5) -> list[MemoryRecord]:
        if self._embedder is None:
            return []
        self.ensure_vector_index()
        if self._index is None or self._index.ntotal == 0:
            return []
        vector = self._embedder.encode([query], normalize_embeddings=True).astype("float32")
        _, indexes = self._index.search(vector, limit)
        ids = [self._index_ids[index] for index in indexes[0] if index >= 0]
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        rows = self._conn.execute(
            f"SELECT id, session_id, role, text FROM messages WHERE id IN ({placeholders})",
            ids,
        ).fetchall()
        by_id = {int(row[0]): MemoryRecord(*row) for row in rows}
        return [by_id[item_id] for item_id in ids if item_id in by_id]
