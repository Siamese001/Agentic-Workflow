"""SQLite-backed durable UWG ledger.

Drop-in replacement for ``InMemoryLedger`` that survives process restart and
supports cross-process hash-chain consistency. Implements ``LedgerProtocol``
from ``v6.uwg``.

Schema:
    CREATE TABLE <table> (
        seq               INTEGER PRIMARY KEY AUTOINCREMENT,
        prev_hash         TEXT NOT NULL,
        commit_request_id TEXT NOT NULL UNIQUE,
        payload_json      TEXT NOT NULL,
        hash              TEXT NOT NULL,
        created_at        INTEGER NOT NULL
    );

Concurrency: WAL journal mode for concurrent readers + a serialized writer
RLock to keep hash-chain construction atomic within a process. Cross-process
writers must coordinate externally (e.g. exclusive UWG worker).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.uwg import LedgerAppendResult


def _hash_entry(seq: int, prev: str, commit_request_id: str, payload: dict[str, Any]) -> str:
    blob = json.dumps(
        {"seq": seq, "prev": prev, "id": commit_request_id, "payload": payload},
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


class SqliteLedger:
    """SQLite implementation of ``LedgerProtocol``."""

    def __init__(self, path: str | Path, *, table: str = "uwg_ledger") -> None:
        self._path = str(path)
        if not table.isidentifier():
            raise ValueError(f"invalid table name: {table!r}")
        self._table = table
        self._mu = threading.RLock()
        self._init_schema()

    @property
    def path(self) -> str:
        return self._path

    @property
    def table(self) -> str:
        return self._table

    # ---- internal ----

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path, timeout=30.0, isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_schema(self) -> None:
        with self._mu, self._connect() as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self._table} (
                    seq               INTEGER PRIMARY KEY AUTOINCREMENT,
                    prev_hash         TEXT NOT NULL,
                    commit_request_id TEXT NOT NULL UNIQUE,
                    payload_json      TEXT NOT NULL,
                    hash              TEXT NOT NULL,
                    created_at        INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS {self._table}_id_idx ON {self._table}(commit_request_id)"
            )

    # ---- LedgerProtocol ----

    def append(
        self,
        *,
        commit_request_id: str,
        payload: dict[str, Any],
    ) -> LedgerAppendResult:
        """Append an entry. Idempotent on commit_request_id collision (returns existing)."""
        with self._mu, self._connect() as conn:
            # Idempotency: if the same commit_request_id already exists, return it.
            cur = conn.execute(
                f"SELECT seq, hash FROM {self._table} WHERE commit_request_id = ?",
                (commit_request_id,),
            )
            row = cur.fetchone()
            if row is not None:
                return LedgerAppendResult(seq=int(row[0]), hash_chain_tip=str(row[1]))

            cur = conn.execute(f"SELECT hash FROM {self._table} ORDER BY seq DESC LIMIT 1")
            head_row = cur.fetchone()
            prev_hash = head_row[0] if head_row else ""

            cur = conn.execute(f"SELECT COALESCE(MAX(seq), -1) + 1 FROM {self._table}")
            next_seq = int(cur.fetchone()[0])

            new_hash = _hash_entry(next_seq, prev_hash, commit_request_id, payload)
            payload_json = json.dumps(payload, sort_keys=True)
            now_ts = int(time.time())

            conn.execute(
                f"""
                INSERT INTO {self._table}
                (seq, prev_hash, commit_request_id, payload_json, hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (next_seq, prev_hash, commit_request_id, payload_json, new_hash, now_ts),
            )
            return LedgerAppendResult(seq=next_seq, hash_chain_tip=new_hash)

    def head_hash(self) -> str:
        with self._mu, self._connect() as conn:
            cur = conn.execute(f"SELECT hash FROM {self._table} ORDER BY seq DESC LIMIT 1")
            row = cur.fetchone()
            return str(row[0]) if row else ""

    # ---- introspection ----

    def head_seq(self) -> int:
        with self._mu, self._connect() as conn:
            cur = conn.execute(f"SELECT COALESCE(MAX(seq), -1) FROM {self._table}")
            return int(cur.fetchone()[0])

    def count(self) -> int:
        with self._mu, self._connect() as conn:
            cur = conn.execute(f"SELECT COUNT(*) FROM {self._table}")
            return int(cur.fetchone()[0])

    def entries(self) -> list[dict[str, Any]]:
        """Return all rows as dicts (sorted by seq)."""
        with self._mu, self._connect() as conn:
            cur = conn.execute(
                f"SELECT seq, prev_hash, commit_request_id, payload_json, hash, created_at "
                f"FROM {self._table} ORDER BY seq ASC"
            )
            out: list[dict[str, Any]] = []
            for seq, prev, crid, payload_json, h, created_at in cur.fetchall():
                out.append(
                    {
                        "seq": int(seq),
                        "prev_hash": str(prev),
                        "commit_request_id": str(crid),
                        "payload": json.loads(payload_json),
                        "hash": str(h),
                        "created_at": int(created_at),
                    }
                )
            return out

    def get(self, commit_request_id: str) -> dict[str, Any] | None:
        with self._mu, self._connect() as conn:
            cur = conn.execute(
                f"SELECT seq, prev_hash, commit_request_id, payload_json, hash, created_at "
                f"FROM {self._table} WHERE commit_request_id = ?",
                (commit_request_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            seq, prev, crid, payload_json, h, created_at = row
            return {
                "seq": int(seq),
                "prev_hash": str(prev),
                "commit_request_id": str(crid),
                "payload": json.loads(payload_json),
                "hash": str(h),
                "created_at": int(created_at),
            }

    # ---- audit ----

    def verify_chain(self) -> bool:
        """Replay the hash chain and verify every row's hash matches."""
        prev = ""
        for entry in self.entries():
            expected = _hash_entry(entry["seq"], prev, entry["commit_request_id"], entry["payload"])
            if expected != entry["hash"]:
                return False
            if entry["prev_hash"] != prev:
                return False
            prev = entry["hash"]
        return True


__all__ = ["SqliteLedger"]
