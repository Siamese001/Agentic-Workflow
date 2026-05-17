"""Tests for W1.3 null-bind read-only gate (tools/governance/w13_null_bind_gate.py)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from tools.governance.w13_null_bind_gate import run_audit


def _mk(tmp_path: Path) -> Path:
    db = tmp_path / "ledger.sqlite"
    conn = sqlite3.connect(str(db))
    conn.executescript(
        """
        CREATE TABLE decisions (
            decision_id TEXT PRIMARY KEY,
            decision_type TEXT NOT NULL
        );
        CREATE TABLE decision_outcomes (
            decision_id TEXT PRIMARY KEY,
            bind_confidence TEXT,
            outcome_bind_tier TEXT,
            bind_disputed INTEGER DEFAULT 0
        );
        """
    )
    for i in range(6):
        conn.execute(
            "INSERT INTO decisions VALUES (?, 'hot_type')",
            (f"d{i}",),
        )
    conn.execute(
        "INSERT INTO decision_outcomes (decision_id, bind_confidence, outcome_bind_tier) "
        "VALUES ('d0', 'high', 'strong_bind')"
    )
    for missing in ("d1", "d2", "d3", "d4", "d5"):
        conn.execute(
            "INSERT INTO decision_outcomes (decision_id, bind_confidence, outcome_bind_tier) "
            "VALUES (?, NULL, NULL)",
            (missing,),
        )
    conn.commit()
    conn.close()
    return db


def test_high_churn_null_bind_counts(tmp_path):
    db = _mk(tmp_path)
    r = run_audit(db, churn_min=5, fail_over=100, warn_over=0)
    assert r["total_decisions"] == 6
    assert r["high_churn_types"] == ["hot_type"]
    assert r["high_churn_null_bind_count"] == 5
    assert r["verdict"] == "WARN"
    assert r["advisory_only"] is True


def test_missing_ledger_pass(tmp_path):
    db = tmp_path / "nope.sqlite"
    r = run_audit(db, churn_min=5, fail_over=1, warn_over=0)
    assert r["verdict"] == "PASS"
    assert r["total_decisions"] == 0
