"""Unit tests for tools.refactor_decisions.rebind_outcomes_from_git."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.refactor_decisions import rebind_outcomes_from_git as mod


def _bootstrap_ledger(db: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db))
    conn.execute(
        """
        CREATE TABLE decision_outcomes (
            outcome_id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id TEXT,
            execution_completed INTEGER DEFAULT 1,
            tests_passed INTEGER DEFAULT 0,
            regression_found INTEGER DEFAULT 0,
            rollback_required INTEGER DEFAULT 0,
            promote_to_pattern INTEGER DEFAULT 0,
            commit_shas_json TEXT,
            files_written_json TEXT DEFAULT '[]',
            tests_run_json TEXT DEFAULT '[]',
            latency_to_outcome_s INTEGER DEFAULT 0,
            pattern_promotion_eligible INTEGER DEFAULT 0,
            outcome_label TEXT DEFAULT 'undecided',
            bound_at TEXT,
            outcome_notes TEXT
        )
        """
    )
    conn.commit()
    return conn


def _insert(conn: sqlite3.Connection, decision_id: str, sha: str, label: str = "undecided") -> None:
    conn.execute(
        "INSERT INTO decision_outcomes (decision_id, commit_shas_json, outcome_label) VALUES (?, ?, ?)",
        (decision_id, json.dumps([sha]), label),
    )
    conn.commit()


def test_rollback_detection(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap_ledger(db)
    _insert(conn, "dec_1", "abc1234")
    conn.close()
    with (
        patch.object(mod, "_commit_exists", return_value=True),
        patch.object(
            mod,
            "_git",
            return_value=(0, 'def5678 Revert "abc1234 — broken commit"\n'),
        ),
    ):
        c = mod.rebind(db, max_walk=30, dry_run=False)
    assert c["updated_rollback"] == 1
    conn = sqlite3.connect(str(db))
    label = conn.execute("SELECT outcome_label FROM decision_outcomes").fetchone()[0]
    rb = conn.execute("SELECT rollback_required FROM decision_outcomes").fetchone()[0]
    assert label == "rollback"
    assert rb == 1


def test_regression_detection(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap_ledger(db)
    _insert(conn, "dec_2", "aaa1111")
    conn.close()
    with (
        patch.object(mod, "_commit_exists", return_value=True),
        patch.object(
            mod,
            "_git",
            return_value=(0, "bbb222 fix regression in foo\n"),
        ),
    ):
        c = mod.rebind(db, max_walk=30, dry_run=False)
    assert c["updated_regression"] == 1


def test_success_detection_clean_window(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap_ledger(db)
    _insert(conn, "dec_3", "ccc3333")
    conn.close()
    log = "\n".join(f"sha{i} feature: add thing {i}" for i in range(6)) + "\n"
    with (
        patch.object(mod, "_commit_exists", return_value=True),
        patch.object(mod, "_git", return_value=(0, log)),
    ):
        c = mod.rebind(db, max_walk=30, dry_run=False)
    assert c["updated_success"] == 1


def test_idempotent_skips_already_labeled(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap_ledger(db)
    _insert(conn, "dec_4", "ddd4444", label="success")
    conn.close()
    c = mod.rebind(db, max_walk=30, dry_run=False)
    assert c["scanned"] == 0


def test_dry_run_does_not_write(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap_ledger(db)
    _insert(conn, "dec_5", "eee5555")
    conn.close()
    with (
        patch.object(mod, "_commit_exists", return_value=True),
        patch.object(
            mod,
            "_git",
            return_value=(0, 'fff Revert "eee5555 broken"\n'),
        ),
    ):
        mod.rebind(db, max_walk=30, dry_run=True)
    conn = sqlite3.connect(str(db))
    label = conn.execute("SELECT outcome_label FROM decision_outcomes").fetchone()[0]
    assert label == "undecided"


def test_skipped_no_sha(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap_ledger(db)
    conn.execute(
        "INSERT INTO decision_outcomes (decision_id, commit_shas_json) VALUES (?, ?)",
        ("dec_6", "[]"),
    )
    conn.commit()
    conn.close()
    c = mod.rebind(db, max_walk=30, dry_run=False)
    assert c["skipped_no_sha"] == 1


def test_missing_db_returns_zero_counters(tmp_path: Path) -> None:
    db = tmp_path / "missing.sqlite"
    c = mod.rebind(db, max_walk=30, dry_run=False)
    assert c["scanned"] == 0
