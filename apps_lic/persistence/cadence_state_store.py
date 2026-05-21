"""SQLite-backed persistence for the 3-touch cadence state machine.

Final follow-up to W3-P9. Provides durable per-recipient
``CadenceStateRecord`` storage so HOP9 (Integration / Dispatcher) can
look up the cadence position on every send and decide whether to dispatch
the INITIAL / FOLLOWUP_1 / FOLLOWUP_2 message — or wait, or recognise
TERMINATED state.

Schema (single table, one row per (campaign_id, recipient_id) tuple):

    CREATE TABLE cadence_state (
        campaign_id              TEXT NOT NULL,
        recipient_id             TEXT NOT NULL,
        current_state            TEXT NOT NULL,
        next_action_at_utc       TEXT,         -- ISO 8601, NULL when TERMINATED
        last_sent_at_utc         TEXT,         -- ISO 8601, NULL until first send
        initial_scheduled_at_utc TEXT,
        replied                  INTEGER NOT NULL DEFAULT 0,
        send_count               INTEGER NOT NULL DEFAULT 0,
        terminated_reason        TEXT,
        PRIMARY KEY (campaign_id, recipient_id)
    );

Mirrors ``ReplyLedgerStore`` in shape — single-table, idempotent upsert,
fail-soft reads. Cross-process safety is up to the caller (Windows file
locks; POSIX advisory locking via flock if needed).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from apps_lic.types.cadence_state_types import CadenceState, CadenceStateRecord

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS cadence_state (
    campaign_id              TEXT NOT NULL,
    recipient_id             TEXT NOT NULL,
    current_state            TEXT NOT NULL,
    next_action_at_utc       TEXT,
    last_sent_at_utc         TEXT,
    initial_scheduled_at_utc TEXT,
    replied                  INTEGER NOT NULL DEFAULT 0,
    send_count               INTEGER NOT NULL DEFAULT 0,
    terminated_reason        TEXT,
    PRIMARY KEY (campaign_id, recipient_id)
);
"""

_UPSERT_SQL = """
INSERT INTO cadence_state (
    campaign_id, recipient_id, current_state, next_action_at_utc,
    last_sent_at_utc, initial_scheduled_at_utc, replied, send_count,
    terminated_reason
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(campaign_id, recipient_id) DO UPDATE SET
    current_state = excluded.current_state,
    next_action_at_utc = excluded.next_action_at_utc,
    last_sent_at_utc = excluded.last_sent_at_utc,
    initial_scheduled_at_utc = excluded.initial_scheduled_at_utc,
    replied = excluded.replied,
    send_count = excluded.send_count,
    terminated_reason = excluded.terminated_reason;
"""

_SELECT_ONE_SQL = """
SELECT campaign_id, recipient_id, current_state, next_action_at_utc,
       last_sent_at_utc, initial_scheduled_at_utc, replied, send_count,
       terminated_reason
FROM cadence_state
WHERE campaign_id = ? AND recipient_id = ?;
"""

_COUNT_SQL = "SELECT COUNT(*) FROM cadence_state;"


class CadenceStateStore:
    """SQLite store for ``CadenceStateRecord``."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    @property
    def db_path(self) -> Path:
        return self._db_path

    def save(self, record: CadenceStateRecord) -> None:
        """Upsert one cadence record."""
        row = (
            record.campaign_id,
            record.recipient_id,
            record.current_state.value,
            record.next_action_at_utc.isoformat() if record.next_action_at_utc else None,
            record.last_sent_at_utc.isoformat() if record.last_sent_at_utc else None,
            (
                record.initial_scheduled_at_utc.isoformat()
                if record.initial_scheduled_at_utc
                else None
            ),
            1 if record.replied else 0,
            int(record.send_count),
            record.terminated_reason,
        )
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(_UPSERT_SQL, row)
            conn.commit()

    def load(
        self, campaign_id: str, recipient_id: str
    ) -> Optional[CadenceStateRecord]:
        """Load one record by composite key, or None when not present."""
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.execute(_SELECT_ONE_SQL, (campaign_id, recipient_id))
            row = cur.fetchone()
        if row is None:
            return None
        (
            cid,
            rid,
            state,
            next_action,
            last_sent,
            initial_at,
            replied,
            send_count,
            terminated_reason,
        ) = row
        try:
            cadence_state = CadenceState(state)
        except ValueError:
            cadence_state = CadenceState.INITIAL
        return CadenceStateRecord(
            campaign_id=cid,
            recipient_id=rid,
            current_state=cadence_state,
            next_action_at_utc=_parse_iso(next_action),
            last_sent_at_utc=_parse_iso(last_sent),
            initial_scheduled_at_utc=_parse_iso(initial_at),
            replied=bool(replied),
            send_count=int(send_count or 0),
            terminated_reason=terminated_reason,
        )

    def load_or_create(
        self, campaign_id: str, recipient_id: str
    ) -> CadenceStateRecord:
        """Return existing record or a freshly-initialised INITIAL record."""
        existing = self.load(campaign_id, recipient_id)
        if existing is not None:
            return existing
        return CadenceStateRecord(
            campaign_id=campaign_id, recipient_id=recipient_id
        )

    def count(self) -> int:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.execute(_COUNT_SQL)
            row = cur.fetchone()
            return int(row[0]) if row else 0

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.executescript(_SCHEMA_SQL)
            conn.commit()


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None


__all__ = [
    "CadenceStateStore",
]
