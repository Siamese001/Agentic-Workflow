"""tools.ledgers.writer — Thread-safe idempotent ledger row writer.

Shared by every post-hook that emits intelligence events. Contract:

    w = writer_for("tool_routing")
    event_id = w.append(
        event_kind="retrieval_tool_choice",
        repo_area=".cursor/scripts/pre_prompt_classifier.py",
        prediction={"chosen_tool": "mcp1_adg_edge_fanin", "query_features": {...}},
        outcome=None,           # may be bound later via bind_outcome()
        latency_ms=12,
        metadata={"session_id": "...", "adg_snapshot_id": "..."},
    )

Guarantees:
    - Idempotent on event_id (SHA-256 of kind + ts + repo_area + prediction_json).
    - Fail-soft: on sqlite3.Error or JSON serialization error, logs to stderr
      and returns empty string instead of raising — callers never crash the
      parent hook chain.
    - Honors LEDGER_WRITER_BYPASS env var: if set (global) or if set to the
      ledger name, becomes a no-op.
    - Stdlib only: sqlite3, hashlib, json, threading, os, datetime.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.ledgers.schema_registry import LedgerSpec, get

# Global lock table keyed by db_path; every writer shares the lock for its DB
# to serialize concurrent hook writes within a single process.
_DB_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_LOCK = threading.Lock()


def _lock_for(db_path: Path) -> threading.Lock:
    key = str(db_path)
    with _LOCKS_LOCK:
        lock = _DB_LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _DB_LOCKS[key] = lock
        return lock


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _stable_json(obj: Any) -> str:
    """Deterministic JSON dump for hashing. None → empty string."""
    if obj is None:
        return ""
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    except (TypeError, ValueError) as exc:
        return json.dumps({"_serialize_error": str(exc)})


def _compute_event_id(kind: str, ts: str, repo_area: str, prediction_json: str) -> str:
    raw = f"{kind}\x00{ts}\x00{repo_area or ''}\x00{prediction_json}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _bypass_active(ledger_name: str) -> bool:
    bypass = os.environ.get("LEDGER_WRITER_BYPASS", "").strip().lower()
    if not bypass:
        return False
    if bypass in ("1", "true", "all", "*"):
        return True
    return ledger_name.lower() in {token.strip() for token in bypass.split(",")}


class LedgerWriter:
    """Thread-safe writer for one ledger. Fail-soft on every error path."""

    def __init__(self, spec: LedgerSpec) -> None:
        self.spec = spec
        self.db_path = spec.db_path
        self._lock = _lock_for(self.db_path)

    # ------------------------------------------------------------------ #
    def append(
        self,
        *,
        event_kind: str,
        repo_area: str = "",
        prediction: Any = None,
        outcome: Any = None,
        score_band: str | None = None,
        score_numeric: float | None = None,
        latency_ms: int | None = None,
        metadata: Any = None,
        session_id: str = "",
        branch: str = "",
        commit_sha: str = "",
        adg_snapshot_id: str = "",
        ts_utc: str | None = None,
    ) -> str:
        """Append an event row. Returns event_id (empty string if bypassed/failed)."""
        if _bypass_active(self.spec.name):
            return ""

        ts = ts_utc or _iso_now()
        prediction_json = _stable_json(prediction)
        outcome_json = _stable_json(outcome) if outcome is not None else ""
        metadata_json = _stable_json(metadata) if metadata is not None else ""
        event_id = _compute_event_id(event_kind, ts, repo_area, prediction_json)

        status = "bound" if outcome is not None else "predicted"
        bound_at = ts if outcome is not None else None

        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with self._lock:
                conn = sqlite3.connect(str(self.db_path), timeout=5)
                try:
                    conn.execute("PRAGMA busy_timeout=3000")
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO events (
                            event_id, event_kind, ts_utc, repo_area, session_id,
                            branch, commit_sha, adg_snapshot_id,
                            prediction_json, outcome_json,
                            score_band, score_numeric, latency_ms, metadata_json,
                            status, bound_at
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            event_id,
                            event_kind,
                            ts,
                            repo_area or "",
                            session_id or "",
                            branch or "",
                            commit_sha or "",
                            adg_snapshot_id or "",
                            prediction_json,
                            outcome_json or None,
                            score_band,
                            score_numeric,
                            latency_ms,
                            metadata_json or None,
                            status,
                            bound_at,
                        ),
                    )
                    conn.commit()
                finally:
                    conn.close()
            return event_id
        except sqlite3.Error as exc:
            print(
                f"[ledger.writer] {self.spec.name} append failed: {exc}",
                file=sys.stderr,
            )
            return ""

    # ------------------------------------------------------------------ #
    def bind_outcome(
        self,
        event_id: str,
        *,
        outcome: Any,
        score_band: str | None = None,
        score_numeric: float | None = None,
        latency_ms: int | None = None,
    ) -> bool:
        """Attach a late-arriving outcome to a previously-predicted row.

        Returns True on success; False on bypass or failure (fail-soft).
        """
        if _bypass_active(self.spec.name) or not event_id:
            return False

        outcome_json = _stable_json(outcome)
        bound_at = _iso_now()

        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path), timeout=5)
                try:
                    cur = conn.execute(
                        """
                        UPDATE events
                           SET outcome_json = ?,
                               score_band = COALESCE(?, score_band),
                               score_numeric = COALESCE(?, score_numeric),
                               latency_ms = COALESCE(?, latency_ms),
                               status = 'bound',
                               bound_at = ?
                         WHERE event_id = ? AND status != 'calibrated'
                        """,
                        (outcome_json, score_band, score_numeric, latency_ms, bound_at, event_id),
                    )
                    conn.commit()
                    return cur.rowcount > 0
                finally:
                    conn.close()
        except sqlite3.Error as exc:
            print(
                f"[ledger.writer] {self.spec.name} bind_outcome failed: {exc}",
                file=sys.stderr,
            )
            return False

    # ------------------------------------------------------------------ #
    def add_scope(
        self,
        event_id: str,
        *,
        file_path: str = "",
        symbol_name: str = "",
        symbol_kind: str = "",
        layer: str = "",
        tags: str = "",
    ) -> bool:
        """Record a file/symbol touched by an event. Idempotent by (event_id,file_path,symbol)."""
        if _bypass_active(self.spec.name) or not event_id:
            return False
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path), timeout=5)
                try:
                    conn.execute(
                        """
                        INSERT INTO event_scope
                            (event_id, file_path, symbol_name, symbol_kind, layer, tags)
                        VALUES (?,?,?,?,?,?)
                        """,
                        (
                            event_id,
                            file_path or "",
                            symbol_name or "",
                            symbol_kind or "",
                            layer or "",
                            tags or "",
                        ),
                    )
                    conn.commit()
                    return True
                finally:
                    conn.close()
        except sqlite3.Error as exc:
            print(
                f"[ledger.writer] {self.spec.name} add_scope failed: {exc}",
                file=sys.stderr,
            )
            return False


# Cache writers so threading locks are reused within a process.
_WRITERS: dict[str, LedgerWriter] = {}


def writer_for(ledger_name: str) -> LedgerWriter:
    """Return a shared LedgerWriter for the named ledger."""
    cached = _WRITERS.get(ledger_name)
    if cached is None:
        cached = LedgerWriter(get(ledger_name))
        _WRITERS[ledger_name] = cached
    return cached
