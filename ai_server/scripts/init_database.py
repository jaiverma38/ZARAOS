import os
import sqlite3
from pathlib import Path

def db_path() -> Path:
    url = os.environ.get("DATABASE_URL", "sqlite:///zara.db")
    if url.startswith("sqlite:///"):
        return Path(url.removeprefix("sqlite:///"))
    return Path("zara.db")

path = db_path()
path.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(path) as db:
    db.execute("CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY, device_id TEXT, kind TEXT, text TEXT, metadata TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    db.execute("CREATE TABLE IF NOT EXISTS faces(owner_id TEXT PRIMARY KEY, name TEXT, embedding BLOB, metadata TEXT, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
print(f"database ready: {path}")
