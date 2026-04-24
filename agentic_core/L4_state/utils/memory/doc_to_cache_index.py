"""G5 Document-fingerprint CDC invalidation — inverse index.

When a source document changes, invalidate only the cached queries that
referenced it — O(queries that touched the document), not O(cache size).

Standalone SQLite table; thread-safe via reentrant module lock; fails soft.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

_LOCK = threading.RLock()
_CONN: sqlite3.Connection | None = None
_DEFAULT_PATH = Path("artifacts/gptcache/doc_to_cache.db")


def _get_conn(db_path: Path | None = None) -> sqlite3.Connection | None:
    """Return a lazily-initialized SQLite connection. Returns None on failure."""
    global _CONN  # noqa: PLW0603
    with _LOCK:
        if _CONN is not None:
            return _CONN
        path = db_path or _DEFAULT_PATH
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(path), check_same_thread=False)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS l2_doc_to_cache (
                    doc_id TEXT NOT NULL,
                    cache_id TEXT NOT NULL,
                    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (doc_id, cache_id)
                )
                """,
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_doc_to_cache_doc ON l2_doc_to_cache(doc_id)",
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_doc_to_cache_cache ON l2_doc_to_cache(cache_id)",
            )
            conn.commit()
            _CONN = conn
            return conn
        except (sqlite3.Error, OSError) as exc:
            _LOGGER.warning("doc_to_cache_index init failed: %s", exc)
            return None


def register_cache_row(cache_id: str, evidence_ids: list[str]) -> int:
    """Record that *cache_id* was grounded on *evidence_ids*. Idempotent."""
    if not cache_id or not evidence_ids:
        return 0
    conn = _get_conn()
    if conn is None:
        return 0
    rows = [(str(eid), cache_id) for eid in evidence_ids if eid]
    if not rows:
        return 0
    with _LOCK:
        try:
            conn.executemany(
                "INSERT OR IGNORE INTO l2_doc_to_cache (doc_id, cache_id) VALUES (?, ?)",
                rows,
            )
            conn.commit()
            return len(rows)
        except sqlite3.Error as exc:
            _LOGGER.warning("doc_to_cache_index register failed: %s", exc)
            return 0


def cache_ids_for_document(doc_id: str) -> list[str]:
    """Return the cache ids that cited *doc_id* (empty on miss / DB error)."""
    if not doc_id:
        return []
    conn = _get_conn()
    if conn is None:
        return []
    with _LOCK:
        try:
            cur = conn.execute(
                "SELECT cache_id FROM l2_doc_to_cache WHERE doc_id = ?",
                (doc_id,),
            )
            return [row[0] for row in cur.fetchall()]
        except sqlite3.Error as exc:
            _LOGGER.warning("doc_to_cache_index lookup failed: %s", exc)
            return []


def forget_cache_row(cache_id: str) -> int:
    """Drop all inverse-index rows that reference *cache_id*."""
    if not cache_id:
        return 0
    conn = _get_conn()
    if conn is None:
        return 0
    with _LOCK:
        try:
            cur = conn.execute(
                "DELETE FROM l2_doc_to_cache WHERE cache_id = ?",
                (cache_id,),
            )
            conn.commit()
            return cur.rowcount
        except sqlite3.Error as exc:
            _LOGGER.warning("doc_to_cache_index forget failed: %s", exc)
            return 0


def reset_for_tests() -> None:
    """Test-only: close + clear the module-level connection."""
    global _CONN  # noqa: PLW0603
    with _LOCK:
        if _CONN is not None:
            try:
                _CONN.close()
            except sqlite3.Error:
                pass
            _CONN = None


__all__ = [
    "cache_ids_for_document",
    "forget_cache_row",
    "register_cache_row",
    "reset_for_tests",
]
