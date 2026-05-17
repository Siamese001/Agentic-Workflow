"""W1 additive ledger columns (author-gate-feedback-loop-d4e8f1)."""

from __future__ import annotations

import sqlite3

from tools.refactor_decisions.ledger_w1_schema import (
    W1_SCHEMA_TAG,
    ensure_w1_feedback_loop_columns,
    w1_schema_probe,
)


def test_ensure_w1_idempotent():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """CREATE TABLE decisions (
            decision_id TEXT PRIMARY KEY,
            created_at TEXT
        )"""
    )
    conn.execute(
        """CREATE TABLE decision_outcomes (
            outcome_id INTEGER PRIMARY KEY,
            decision_id TEXT
        )"""
    )
    a1 = ensure_w1_feedback_loop_columns(conn)
    a2 = ensure_w1_feedback_loop_columns(conn)
    assert all(c.startswith("decisions.") or c.startswith("decision_outcomes.") for c in a1)
    assert a2 == []
    p = w1_schema_probe(conn)
    assert p["w1_schema_tag"] == W1_SCHEMA_TAG
    assert p["decisions_has_precedent_top_match_ids_json"] is True
    assert p["decision_outcomes_has_outcome_bind_tier"] is True
    conn.close()
