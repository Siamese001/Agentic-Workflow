"""W1 additive schema (plan author-gate-feedback-loop-d4e8f1).

Idempotent ``ALTER TABLE`` helpers for capture-time precedent metadata and
outcome bind tier. Safe to re-run.
"""

from __future__ import annotations

import sqlite3
from typing import Any

# Bump when lookup ranking / digest inputs change materially.
W1_SCHEMA_TAG = "ag-feedback-w1-columns-20260517"

_W1_DECISION_COLUMNS: tuple[tuple[str, str], ...] = (
    ("precedent_top_match_ids_json", "TEXT"),
    ("precedent_lookup_query_digest", "TEXT"),
    ("precedent_lookup_policy_version", "TEXT"),
    ("precedent_capture_utc", "TEXT"),
)

_W1_OUTCOME_COLUMNS: tuple[tuple[str, str], ...] = (("outcome_bind_tier", "TEXT"),)


def ensure_w1_feedback_loop_columns(conn: sqlite3.Connection) -> list[str]:
    """Add W1 columns if missing. Returns list of ``table.column`` added."""
    added: list[str] = []
    cols = {r[1] for r in conn.execute("PRAGMA table_info(decisions)").fetchall()}
    for name, sql_type in _W1_DECISION_COLUMNS:
        if name not in cols:
            conn.execute(f'ALTER TABLE decisions ADD COLUMN "{name}" {sql_type}')
            added.append(f"decisions.{name}")
            cols.add(name)
    ocols = {r[1] for r in conn.execute("PRAGMA table_info(decision_outcomes)").fetchall()}
    for name, sql_type in _W1_OUTCOME_COLUMNS:
        if name not in ocols:
            conn.execute(f'ALTER TABLE decision_outcomes ADD COLUMN "{name}" {sql_type}')
            added.append(f"decision_outcomes.{name}")
            ocols.add(name)
    return added


def w1_schema_probe(conn: sqlite3.Connection) -> dict[str, Any]:
    """Return bool flags for tests / migration verification."""
    dcols = {r[1] for r in conn.execute("PRAGMA table_info(decisions)").fetchall()}
    ocols = {r[1] for r in conn.execute("PRAGMA table_info(decision_outcomes)").fetchall()}
    return {
        "w1_schema_tag": W1_SCHEMA_TAG,
        "decisions_has_precedent_top_match_ids_json": "precedent_top_match_ids_json" in dcols,
        "decisions_has_precedent_lookup_query_digest": "precedent_lookup_query_digest" in dcols,
        "decisions_has_precedent_lookup_policy_version": "precedent_lookup_policy_version" in dcols,
        "decisions_has_precedent_capture_utc": "precedent_capture_utc" in dcols,
        "decision_outcomes_has_outcome_bind_tier": "outcome_bind_tier" in ocols,
    }
