"""
G06 SQLite-backed durable PermissionLadder.

Sibling to InMemoryPermissionLadder for cross-process / restart-survival
deployments. Schema mirrors the in-memory grant store; a UNIQUE index on
(agent_id, target_resource) enforces overwrite-on-grant semantics via UPSERT.

Race-safety: SQLite serializes WAL writes, so concurrent grant() calls land
in well-defined order. check() reads via plain SELECT and reconstructs a
PermissionGrant tuple. No bespoke locking on top of SQLite is required.

Schema:

    CREATE TABLE IF NOT EXISTS permission_grants (
        agent_id TEXT NOT NULL,
        target_resource TEXT NOT NULL,
        rung INTEGER NOT NULL,
        granted_by TEXT NOT NULL,
        expires_at_iso TEXT NOT NULL,
        PRIMARY KEY (agent_id, target_resource)
    );
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from agentic_core.L5_safety.permissions import (
    PermissionGrant,
    PermissionLadder,
    PermissionRung,
    PermissionVerdict,
    _now_iso,
)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS permission_grants (
    agent_id TEXT NOT NULL,
    target_resource TEXT NOT NULL,
    rung INTEGER NOT NULL,
    granted_by TEXT NOT NULL,
    expires_at_iso TEXT NOT NULL,
    PRIMARY KEY (agent_id, target_resource)
);
"""


class SqlitePermissionLadder:
    """Durable PermissionLadder backed by a SQLite file.

    Use for multi-process deployments where grants must survive restart.
    For single-process in-memory use, prefer InMemoryPermissionLadder
    (faster, no I/O).
    """

    def __init__(self, db_path: str | Path) -> None:
        self._path = str(db_path)
        # Single connection guarded by a lock — sqlite3 connections are
        # not safe across threads by default; this lock makes them safe
        # without paying for check_same_thread=False reentrance hazards.
        self._lock = threading.Lock()
        self._con = sqlite3.connect(self._path, check_same_thread=False, timeout=30)
        self._con.execute("PRAGMA journal_mode=WAL")
        self._con.execute("PRAGMA synchronous=NORMAL")
        self._con.executescript(_SCHEMA)
        self._con.commit()

    def grant(self, grant: PermissionGrant) -> None:
        with self._lock:
            self._con.execute(
                """
                INSERT INTO permission_grants
                    (agent_id, target_resource, rung, granted_by, expires_at_iso)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(agent_id, target_resource) DO UPDATE SET
                    rung = excluded.rung,
                    granted_by = excluded.granted_by,
                    expires_at_iso = excluded.expires_at_iso
                """,
                (
                    grant.agent_id,
                    grant.target_resource,
                    int(grant.rung),
                    grant.granted_by,
                    grant.expires_at_iso,
                ),
            )
            self._con.commit()

    def revoke(self, agent_id: str, target_resource: str) -> bool:
        with self._lock:
            cur = self._con.execute(
                "DELETE FROM permission_grants WHERE agent_id=? AND target_resource=?",
                (agent_id, target_resource),
            )
            self._con.commit()
            return cur.rowcount > 0

    def check(
        self,
        agent_id: str,
        target: str,
        requested: PermissionRung,
    ) -> PermissionVerdict:
        with self._lock:
            row = self._con.execute(
                """
                SELECT rung, granted_by, expires_at_iso
                FROM permission_grants
                WHERE agent_id=? AND target_resource=?
                """,
                (agent_id, target),
            ).fetchone()

        if row is None:
            return PermissionVerdict(
                allowed=False, held_rung=None, requested_rung=requested,
                reason="no grant exists for (agent, target)",
            )
        rung_int, _granted_by, expires = row
        held = PermissionRung(rung_int)
        if expires <= _now_iso():
            return PermissionVerdict(
                allowed=False, held_rung=held, requested_rung=requested,
                reason=f"grant expired at {expires}",
            )
        if held >= requested:
            return PermissionVerdict(
                allowed=True, held_rung=held, requested_rung=requested,
                reason=f"held {held.name} \u2265 requested {requested.name}",
            )
        return PermissionVerdict(
            allowed=False, held_rung=held, requested_rung=requested,
            reason=f"held {held.name} < requested {requested.name}",
        )

    def close(self) -> None:
        with self._lock:
            self._con.close()


def sqlite_ladder(db_path: str | Path) -> SqlitePermissionLadder:
    """Factory for a durable SQLite-backed permission ladder.

    Returns the concrete type (not the Protocol) because callers typically
    need ``grant``/``revoke`` in addition to the Protocol's ``check``.
    """
    return SqlitePermissionLadder(db_path)


__all__ = ["SqlitePermissionLadder", "sqlite_ladder"]
