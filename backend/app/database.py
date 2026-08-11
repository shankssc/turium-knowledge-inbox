"""SQLite connection and schema setup.

Uses an in-memory database by design: this is a single-user local app
with no auth, so we don't need data to survive a server restart. A
fresh `uvicorn` run always starts clean (see README for the tradeoff
and what changes for a persistent/production setup).
"""
import sqlite3
from contextlib import contextmanager
from typing import Iterator

DATABASE_URL = ":memory:"

# A single, shared connection is intentional for :memory: SQLite —
# each new connection to ":memory:" gets its own separate, empty
# database, so we can't open a fresh connection per request like
# you would with a file-backed DB. check_same_thread=False allows
# this one connection to be used across FastAPI's request threads.
_connection: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DATABASE_URL, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON")
    return _connection


SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('note', 'url')),
    source_url TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_item_id ON chunks(item_id);
"""


def init_db() -> None:
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()


@contextmanager
def get_cursor() -> Iterator[sqlite3.Cursor]:
    """Context manager that commits on success, rolls back on error."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
