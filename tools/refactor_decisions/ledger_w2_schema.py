"""W2 additive schema (plan author-gate-feedback-loop-d4e8f1).

Idempotent ``ALTER TABLE`` helpers for ``decision_signals`` audit columns.
"""

from __future__ import annotations

import sqlite3
from typing import Any

W2_SCHEMA_TAG = "ag-feedback-w2-signal-columns-20260517"

_W2_SIGNAL_COLUMNS: tuple[tuple[str, str], ...] = (
    ("source_ref", "TEXT"),
    ("policy_version", "TEXT"),
    ("created_at", "TEXT"),
)


def ensure_w2_decision_signal_columns(conn: sqlite3.Connection) -> list[str]:
    """Add W2 columns on ``decision_signals`` if missing. Returns ``table.column`` added."""
    added: list[str] = []
    cols = {r[1] for r in conn.execute("PRAGMA table_info(decision_signals)").fetchall()}
    for name, sql_type in _W2_SIGNAL_COLUMNS:
        if name not in cols:
            conn.execute(f'ALTER TABLE decision_signals ADD COLUMN "{name}" {sql_type}')
            added.append(f"decision_signals.{name}")
            cols.add(name)
    return added


def w2_schema_probe(conn: sqlite3.Connection) -> dict[str, Any]:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(decision_signals)").fetchall()}
    return {
        "w2_schema_tag": W2_SCHEMA_TAG,
        "decision_signals_has_source_ref": "source_ref" in cols,
        "decision_signals_has_policy_version": "policy_version" in cols,
        "decision_signals_has_created_at": "created_at" in cols,
    }
