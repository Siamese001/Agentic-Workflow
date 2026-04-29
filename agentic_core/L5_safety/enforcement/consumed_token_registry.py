"""
G07 — Capability Token Single-Use Registry (consumed-token ledger).

Per ADR-070 L5 Guardrail Family Catalog (2026-04-29).
Phase: W4 P8 W2/P8.07 — `.windsurf/plans/w4-p8-guardrail-family-e93f8a.md`

Closes the trust gap in the existing rotation logic. ``capability_token_rotation.evaluate_rotation``
already decides ``ROTATE_DUE_USAGE`` when ``single_use AND usage_count >= 1`` —
but it depends on the caller honestly tracking ``usage_count``. A faulty or
adversarial caller could replay a ``single_use`` token by claiming ``usage_count=0``.

This module owns the durable record: ``ConsumedTokenRegistry`` records
``(token_id, consumed_at, consumed_by)`` and refuses re-admission of any
already-consumed ``token_id``. The registry is the source of truth — rotation
policy reads from it via ``has_been_consumed()``.

Storage:

  - In-memory by default (test/short-lived processes)
  - Optional SQLite backing for cross-process durability

Concurrency: SQLite UPSERT with ``token_id`` as PRIMARY KEY makes consume()
race-safe across processes. In-memory backend uses a threading.Lock.

This module emits ``agentic.token.consumed`` and ``agentic.token.replay_blocked``
log records on the ``adg.G07`` logger so the OTEL bridge captures spans.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

_log = logging.getLogger("adg.G07")


@dataclass(frozen=True)
class ConsumptionRecord:
    """Immutable record of a single-use token consumption."""

    token_id: str
    consumed_at: float  # Unix epoch
    consumed_by: str  # actor_id


class TokenAlreadyConsumedError(Exception):
    """Raised when a single-use token is replayed."""


class ConsumedTokenRegistry(Protocol):
    """Protocol — the contract."""

    def consume(self, token_id: str, consumed_by: str) -> ConsumptionRecord:
        """Atomically record a single-use token's consumption.

        Raises TokenAlreadyConsumedError if token_id was previously consumed.
        Idempotency boundary: each (token_id, consumed_by) pair is unique;
        re-consume by the SAME actor is treated as replay (still raises).
        """
        ...

    def has_been_consumed(self, token_id: str) -> bool:
        """Return True if token_id appears in the consumed ledger."""
        ...


class InMemoryConsumedTokenRegistry:
    """Thread-safe in-memory registry. For tests and single-process runtimes."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._consumed: dict[str, ConsumptionRecord] = {}

    def consume(self, token_id: str, consumed_by: str) -> ConsumptionRecord:
        with self._lock:
            if token_id in self._consumed:
                _log.info(
                    "agentic.token.replay_blocked layer=L5 edge_kind=token_replay_blocked "
                    "token_id=%s already_consumed_by=%s req_ids=REQ-L5-G07-SINGLE-USE-001",
                    token_id, self._consumed[token_id].consumed_by,
                )
                raise TokenAlreadyConsumedError(
                    f"Token {token_id} was already consumed by "
                    f"{self._consumed[token_id].consumed_by} at {self._consumed[token_id].consumed_at}"
                )
            record = ConsumptionRecord(
                token_id=token_id,
                consumed_at=time.time(),
                consumed_by=consumed_by,
            )
            self._consumed[token_id] = record
            _log.info(
                "agentic.token.consumed layer=L5 edge_kind=token_consumed "
                "token_id=%s consumed_by=%s req_ids=REQ-L5-G07-SINGLE-USE-001",
                token_id, consumed_by,
            )
            return record

    def has_been_consumed(self, token_id: str) -> bool:
        with self._lock:
            return token_id in self._consumed


class SqliteConsumedTokenRegistry:
    """SQLite-backed registry for cross-process durable single-use enforcement."""

    SCHEMA = """
        CREATE TABLE IF NOT EXISTS consumed_tokens (
            token_id     TEXT PRIMARY KEY,
            consumed_at  REAL NOT NULL,
            consumed_by  TEXT NOT NULL
        )
    """

    def __init__(self, db_path: str | Path) -> None:
        self._db = Path(db_path)
        self._db.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with self._connect() as con:
            con.execute(self.SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        # isolation_level=None enables autocommit; we manage transactions explicitly via 'with'
        return sqlite3.connect(str(self._db), timeout=10.0)

    def consume(self, token_id: str, consumed_by: str) -> ConsumptionRecord:
        with self._lock, self._connect() as con:
            now = time.time()
            try:
                con.execute(
                    "INSERT INTO consumed_tokens (token_id, consumed_at, consumed_by) VALUES (?, ?, ?)",
                    (token_id, now, consumed_by),
                )
            except sqlite3.IntegrityError as exc:
                # Race with another process — fetch the winner
                row = con.execute(
                    "SELECT consumed_at, consumed_by FROM consumed_tokens WHERE token_id = ?",
                    (token_id,),
                ).fetchone()
                _log.info(
                    "agentic.token.replay_blocked layer=L5 edge_kind=token_replay_blocked "
                    "token_id=%s already_consumed_by=%s req_ids=REQ-L5-G07-SINGLE-USE-001",
                    token_id, row[1] if row else "<unknown>",
                )
                raise TokenAlreadyConsumedError(
                    f"Token {token_id} was already consumed (race lost). "
                    f"Winner: {row[1] if row else 'unknown'} at {row[0] if row else '?'}"
                ) from exc

            _log.info(
                "agentic.token.consumed layer=L5 edge_kind=token_consumed "
                "token_id=%s consumed_by=%s req_ids=REQ-L5-G07-SINGLE-USE-001",
                token_id, consumed_by,
            )
            return ConsumptionRecord(token_id=token_id, consumed_at=now, consumed_by=consumed_by)

    def has_been_consumed(self, token_id: str) -> bool:
        with self._lock, self._connect() as con:
            row = con.execute(
                "SELECT 1 FROM consumed_tokens WHERE token_id = ?",
                (token_id,),
            ).fetchone()
            return row is not None


__all__ = [
    "ConsumptionRecord",
    "TokenAlreadyConsumedError",
    "ConsumedTokenRegistry",
    "InMemoryConsumedTokenRegistry",
    "SqliteConsumedTokenRegistry",
]
