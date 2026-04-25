"""Durable SQLite-backed ``PassKStore`` — ADR-054.

Interface-compatible with the in-memory ``PassKStore`` in
``consistency.py``. Callers see the same ``record`` / ``check`` /
``history`` / ``clear`` methods and the same ``ConsistencyCheck`` type.

Why this exists:

- The in-memory store loses all history on process restart. That is
  unacceptable for commit-path gating — a restart becomes a silent
  circumvention of X1G.
- SQLite gives durability with zero external dependency, WAL-mode
  concurrency, and process-local file paths that survive restarts.
- Callers that want cross-host sharing should plug in Redis or a
  managed DB — both are straightforward given the interface.

Schema (one table):

    CREATE TABLE passk_trials (
        trajectory_class TEXT NOT NULL,
        rubric_version   TEXT NOT NULL,
        agent_version    TEXT NOT NULL,
        policy_version   TEXT NOT NULL,
        run_id           TEXT NOT NULL,
        passed           INTEGER NOT NULL,  -- 0/1
        timestamp        REAL NOT NULL,
        inserted_at      REAL NOT NULL DEFAULT (strftime('%s','now')),
        PRIMARY KEY (trajectory_class, rubric_version, agent_version,
                     policy_version, inserted_at, run_id)
    );
    CREATE INDEX idx_bucket_recent
        ON passk_trials (trajectory_class, rubric_version,
                         agent_version, policy_version, inserted_at DESC);

H8 fail-mode: any backend read/write failure propagates as
``RuntimeError`` so the calling pipeline routes to X3B with
``CONSISTENCY_HISTORY_UNAVAILABLE`` — never falls back to "assume pass".
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Iterable

from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    ConsistencyCheck,
    TrialRecord,
)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS passk_trials (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    trajectory_class TEXT NOT NULL,
    rubric_version   TEXT NOT NULL,
    agent_version    TEXT NOT NULL,
    policy_version   TEXT NOT NULL,
    run_id           TEXT NOT NULL,
    passed           INTEGER NOT NULL,
    timestamp        REAL NOT NULL,
    inserted_at      REAL NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_bucket_recent
    ON passk_trials (trajectory_class, rubric_version,
                     agent_version, policy_version, id DESC);
"""


class SqlitePassKStore:
    """Durable ``PassKStore`` backed by a local SQLite file.

    Thread-safe via a ``threading.Lock`` around write operations. SQLite
    in WAL mode allows concurrent reads; the lock serializes writes to
    avoid ``database is locked`` under bursty workloads.

    Signature-compatible with ``consistency.PassKStore`` so callers can
    swap implementations transparently.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        # check_same_thread=False because we serialize ourselves via _lock;
        # connection is reused across the process to avoid per-call open cost.
        self._conn = sqlite3.connect(
            str(self._path),
            check_same_thread=False,
            isolation_level=None,  # autocommit; explicit BEGIN for batches
            timeout=30.0,
        )
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL;")
            self._conn.execute("PRAGMA synchronous=NORMAL;")
            self._conn.execute("PRAGMA foreign_keys=ON;")
            self._conn.executescript(_SCHEMA)

    # ------------------------------------------------------------------ #
    # PassKStore interface
    # ------------------------------------------------------------------ #

    def record(
        self,
        key: BucketKey,
        trial: TrialRecord,
        *,
        max_retained: int = 100,
    ) -> None:
        """Append a trial, then prune beyond ``max_retained`` newest rows."""
        if max_retained <= 0:
            raise ValueError("max_retained must be > 0")
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO passk_trials "
                    "(trajectory_class, rubric_version, agent_version, "
                    "policy_version, run_id, passed, timestamp) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        key.trajectory_class,
                        key.rubric_version,
                        key.agent_version,
                        key.policy_version,
                        trial.run_id,
                        1 if trial.passed else 0,
                        float(trial.timestamp),
                    ),
                )
                # Prune older rows beyond the retention cap. Keeps the
                # newest ``max_retained`` by id DESC (autoincrement
                # preserves insertion order, finer-grained than
                # second-resolution inserted_at).
                self._conn.execute(
                    "DELETE FROM passk_trials "
                    "WHERE trajectory_class=? AND rubric_version=? "
                    "  AND agent_version=? AND policy_version=? "
                    "  AND id NOT IN ("
                    "    SELECT id FROM passk_trials "
                    "    WHERE trajectory_class=? AND rubric_version=? "
                    "      AND agent_version=? AND policy_version=? "
                    "    ORDER BY id DESC "
                    "    LIMIT ?"
                    "  )",
                    (
                        key.trajectory_class,
                        key.rubric_version,
                        key.agent_version,
                        key.policy_version,
                        key.trajectory_class,
                        key.rubric_version,
                        key.agent_version,
                        key.policy_version,
                        max_retained,
                    ),
                )
            except sqlite3.Error as exc:
                raise RuntimeError(f"SqlitePassKStore.record failed for {key}: {exc}") from exc

    def check(
        self,
        key: BucketKey,
        *,
        k: int,
        theta: float,
    ) -> ConsistencyCheck:
        """Compute ``pass^k`` over the most recent k trials."""
        if k <= 0:
            raise ValueError("k must be > 0")
        if not 0.0 <= theta <= 1.0:
            raise ValueError("theta must be in [0, 1]")

        try:
            cur = self._conn.execute(
                "SELECT passed FROM passk_trials "
                "WHERE trajectory_class=? AND rubric_version=? "
                "  AND agent_version=? AND policy_version=? "
                "ORDER BY id DESC "
                "LIMIT ?",
                (
                    key.trajectory_class,
                    key.rubric_version,
                    key.agent_version,
                    key.policy_version,
                    k,
                ),
            )
            rows = cur.fetchall()
        except sqlite3.Error as exc:
            # H8: read failure MUST propagate; caller routes to X3B with
            # CONSISTENCY_HISTORY_UNAVAILABLE. Never silently "pass".
            raise RuntimeError(f"SqlitePassKStore.check read failed for {key}: {exc}") from exc

        if len(rows) < k:
            return ConsistencyCheck(
                passed=False,
                pass_k=None,
                k=k,
                theta=theta,
                has_history=False,
                history_size=len(rows),
                reason="INSUFFICIENT_HISTORY",
            )

        successes = sum(1 for (p,) in rows if p)
        pass_k = successes / k
        passed = pass_k >= theta
        return ConsistencyCheck(
            passed=passed,
            pass_k=pass_k,
            k=k,
            theta=theta,
            has_history=True,
            history_size=len(rows),
            reason="" if passed else "CONSISTENCY_FAIL",
        )

    def history(self, key: BucketKey) -> tuple[TrialRecord, ...]:
        """Return bucket records in chronological order (oldest first)."""
        try:
            cur = self._conn.execute(
                "SELECT run_id, passed, timestamp FROM passk_trials "
                "WHERE trajectory_class=? AND rubric_version=? "
                "  AND agent_version=? AND policy_version=? "
                "ORDER BY id ASC",
                (
                    key.trajectory_class,
                    key.rubric_version,
                    key.agent_version,
                    key.policy_version,
                ),
            )
            rows = cur.fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError(f"SqlitePassKStore.history failed for {key}: {exc}") from exc
        return tuple(TrialRecord(run_id=r, passed=bool(p), timestamp=float(t)) for (r, p, t) in rows)

    def clear(self, key: BucketKey) -> None:
        """Explicit bucket reset."""
        with self._lock:
            try:
                self._conn.execute(
                    "DELETE FROM passk_trials "
                    "WHERE trajectory_class=? AND rubric_version=? "
                    "  AND agent_version=? AND policy_version=?",
                    (
                        key.trajectory_class,
                        key.rubric_version,
                        key.agent_version,
                        key.policy_version,
                    ),
                )
            except sqlite3.Error as exc:
                raise RuntimeError(f"SqlitePassKStore.clear failed for {key}: {exc}") from exc

    # ------------------------------------------------------------------ #
    # Maintenance surface
    # ------------------------------------------------------------------ #

    def close(self) -> None:
        """Close the backing connection. Idempotent."""
        with self._lock:
            try:
                self._conn.close()
            except sqlite3.Error:  # guardian: allow-silent-swallow -- close() must be idempotent
                pass

    def all_buckets(self) -> Iterable[BucketKey]:
        """Yield every bucket present in the store (admin / debugging)."""
        try:
            cur = self._conn.execute(
                "SELECT DISTINCT trajectory_class, rubric_version, "
                "agent_version, policy_version FROM passk_trials"
            )
            for row in cur.fetchall():
                yield BucketKey(
                    trajectory_class=row[0],
                    rubric_version=row[1],
                    agent_version=row[2],
                    policy_version=row[3],
                )
        except sqlite3.Error as exc:
            raise RuntimeError(f"SqlitePassKStore.all_buckets failed: {exc}") from exc

    def __enter__(self) -> "SqlitePassKStore":
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()


__all__ = ["SqlitePassKStore"]
