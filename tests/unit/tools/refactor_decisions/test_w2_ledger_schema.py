"""W2 decision_signals additive schema."""

from __future__ import annotations

import sqlite3

from tools.refactor_decisions.ledger_w2_schema import (
    W2_SCHEMA_TAG,
    ensure_w2_decision_signal_columns,
    w2_schema_probe,
)


def test_ensure_w2_idempotent():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """CREATE TABLE decision_signals (
            signal_id INTEGER PRIMARY KEY,
            decision_id TEXT,
            option_id TEXT,
            signal_name TEXT,
            signal_value REAL,
            signal_weight REAL,
            signal_source TEXT
        )"""
    )
    a1 = ensure_w2_decision_signal_columns(conn)
    a2 = ensure_w2_decision_signal_columns(conn)
    assert a1
    assert a2 == []
    p = w2_schema_probe(conn)
    assert p["w2_schema_tag"] == W2_SCHEMA_TAG
    assert p["decision_signals_has_source_ref"] is True
    conn.close()
