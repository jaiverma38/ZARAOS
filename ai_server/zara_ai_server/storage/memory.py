import json
import sqlite3
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class MemoryStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.db_path = data_dir / "zara_memory.sqlite3"
        self.index_path = data_dir / "zara_memory.faiss"
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.index = faiss.IndexFlatIP(384)
        self._init_db()
        self._load_index()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY, device_id TEXT, kind TEXT, text TEXT, metadata TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
            db.execute("CREATE TABLE IF NOT EXISTS faces(owner_id TEXT PRIMARY KEY, name TEXT, embedding BLOB, metadata TEXT, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)")

    def _load_index(self) -> None:
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))

    def add_memory(self, device_id: str, kind: str, text: str, metadata: dict) -> int:
        vector = self.embedder.encode([text], normalize_embeddings=True).astype("float32")
        self.index.add(vector)
        faiss.write_index(self.index, str(self.index_path))
        with sqlite3.connect(self.db_path) as db:
            cur = db.execute("INSERT INTO memories(device_id, kind, text, metadata) VALUES(?,?,?,?)", (device_id, kind, text, json.dumps(metadata)))
            return int(cur.lastrowid)

    def save_face(self, owner_id: str, name: str, embedding: np.ndarray, metadata: dict) -> None:
        blob = embedding.astype("float32").tobytes()
        with sqlite3.connect(self.db_path) as db:
            db.execute("REPLACE INTO faces(owner_id, name, embedding, metadata) VALUES(?,?,?,?)", (owner_id, name, blob, json.dumps(metadata)))

    def faces(self) -> list[tuple[str, str, np.ndarray]]:
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT owner_id, name, embedding FROM faces").fetchall()
        return [(row[0], row[1], np.frombuffer(row[2], dtype="float32")) for row in rows]
