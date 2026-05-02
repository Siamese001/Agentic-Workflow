"""SQLite-backed persistence for the reply-signal feedback ledger.

Follow-up to W4-P10 (apps_lic LinkedIn response-rate plan, Notion page
35327693-f55c-81e2-9b58-debeeb48bb35). Mirrors the intelligence-ledger
family pattern (ADR-050) — a thin store with idempotent upsert,
fail-soft reads, and lattice-fingerprint drift detection.

Schema (single table, single ledger per file):

    CREATE TABLE reply_feedback_ledger (
        cell_id              TEXT PRIMARY KEY,
        sends                INTEGER NOT NULL DEFAULT 0,
        replies              INTEGER NOT NULL DEFAULT 0,
        last_updated_utc     TEXT,                     -- ISO 8601
        lattice_fingerprint  TEXT NOT NULL
    );

The store is deliberately schema-thin. Per-event audit trail (one row
per send/reply event) is OUT OF SCOPE — that belongs in a dedicated
event log, not in the posterior projection. The Beta posterior IS the
projection; rebuilding it from events would require replay machinery
that the engine does not need.

Drift detection: every row carries the lattice_fingerprint at write
time. Reads warn (not raise) if the persisted fingerprint differs from
the current ``LATTICE_FINGERPRINT`` — drift means a cell was added or
removed and prior posteriors may not be apples-to-apples comparable.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from apps_lic.config.outreach_experiment_cells import (
    LATTICE_FINGERPRINT,
    is_valid_cell_id,
)
from apps_lic.engines.reply_signal_feedback_engine import (
    CellPosterior,
    ReplyFeedbackLedger,
)

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS reply_feedback_ledger (
    cell_id              TEXT PRIMARY KEY,
    sends                INTEGER NOT NULL DEFAULT 0,
    replies              INTEGER NOT NULL DEFAULT 0,
    last_updated_utc     TEXT,
    lattice_fingerprint  TEXT NOT NULL
);
"""

_UPSERT_SQL = """
INSERT INTO reply_feedback_ledger
    (cell_id, sends, replies, last_updated_utc, lattice_fingerprint)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(cell_id) DO UPDATE SET
    sends = excluded.sends,
    replies = excluded.replies,
    last_updated_utc = excluded.last_updated_utc,
    lattice_fingerprint = excluded.lattice_fingerprint;
"""

_SELECT_ALL_SQL = """
SELECT cell_id, sends, replies, last_updated_utc, lattice_fingerprint
FROM reply_feedback_ledger;
"""


class LatticeFingerprintDrift(UserWarning):
    """Emitted when the persisted lattice fingerprint disagrees with current."""


class ReplyLedgerStore:
    """SQLite store for ``ReplyFeedbackLedger``.

    Thread-unsafe by default — callers MUST serialise writes per file.
    The intended use is a single writer per campaign / per host.
    """

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    @property
    def db_path(self) -> Path:
        return self._db_path

    def save(self, ledger: ReplyFeedbackLedger) -> int:
        """Upsert every posterior in ``ledger`` to the SQLite file.

        Returns the number of rows written (== ``len(ledger.posteriors)``).
        Idempotent — running twice with the same ledger yields the same
        on-disk state.
        """
        rows: list[tuple[str, int, int, Optional[str], str]] = []
        for cell_id, posterior in ledger.posteriors.items():
            if not is_valid_cell_id(cell_id):
                # Defensive: a poisoned ledger should not persist invalid cells.
                continue
            ts = (
                posterior.last_updated_utc.isoformat()
                if posterior.last_updated_utc is not None
                else None
            )
            rows.append(
                (
                    cell_id,
                    int(posterior.sends),
                    int(posterior.replies),
                    ts,
                    ledger.lattice_fingerprint,
                )
            )
        if not rows:
            return 0
        with sqlite3.connect(self._db_path) as conn:
            conn.executemany(_UPSERT_SQL, rows)
            conn.commit()
        return len(rows)

    def load(self) -> ReplyFeedbackLedger:
        """Reconstruct a ``ReplyFeedbackLedger`` from disk.

        Returns an empty ledger (with current ``LATTICE_FINGERPRINT``)
        when the database is empty or missing. Warns via
        :class:`LatticeFingerprintDrift` when persisted fingerprints
        disagree with the current lattice — but loads the data anyway
        so callers can decide whether to trust prior posteriors.
        """
        ledger = ReplyFeedbackLedger()
        try:
            with sqlite3.connect(self._db_path) as conn:
                cur = conn.execute(_SELECT_ALL_SQL)
                rows = cur.fetchall()
        except sqlite3.DatabaseError:
            return ledger
        seen_fingerprints: set[str] = set()
        for cell_id, sends, replies, ts, fingerprint in rows:
            if not is_valid_cell_id(cell_id):
                # Skip rows that no longer correspond to live lattice cells.
                continue
            seen_fingerprints.add(fingerprint)
            last_updated: Optional[datetime] = None
            if ts:
                try:
                    last_updated = datetime.fromisoformat(ts)
                except ValueError:
                    last_updated = None
            ledger.posteriors[cell_id] = CellPosterior(
                cell_id=cell_id,
                sends=int(sends),
                replies=int(replies),
                last_updated_utc=last_updated,
            )
        if seen_fingerprints and LATTICE_FINGERPRINT not in seen_fingerprints:
            import warnings

            warnings.warn(
                (
                    f"Reply ledger fingerprint drift: persisted={sorted(seen_fingerprints)} "
                    f"current={LATTICE_FINGERPRINT}. Posterior comparability degraded."
                ),
                LatticeFingerprintDrift,
                stacklevel=2,
            )
        # Adopt the most recent persisted fingerprint when present, so
        # subsequent saves preserve the historical chain. New ledgers
        # default to current LATTICE_FINGERPRINT via the dataclass factory.
        if seen_fingerprints:
            ledger.lattice_fingerprint = next(iter(seen_fingerprints))
        return ledger

    def cell_count(self) -> int:
        """Return the number of cells currently stored on disk."""
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM reply_feedback_ledger;")
            row = cur.fetchone()
            return int(row[0]) if row else 0

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.executescript(_SCHEMA_SQL)
            conn.commit()


__all__ = [
    "LatticeFingerprintDrift",
    "ReplyLedgerStore",
]
