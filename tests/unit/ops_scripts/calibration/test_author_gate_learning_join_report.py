"""Tests for author_gate_learning_join_report (W5)."""

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MOD_PATH = REPO_ROOT / "ops_scripts" / "calibration" / "author_gate_learning_join_report.py"


def _load():
    name = "author_gate_learning_join_report_t"
    spec = importlib.util.spec_from_file_location(name, MOD_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


def test_build_payload_counts_recommendation_match_and_auq(mod, tmp_path, monkeypatch):
    db = tmp_path / "ledger.sqlite"
    conn = sqlite3.connect(str(db))
    conn.executescript(
        """
        CREATE TABLE decisions (
            decision_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            decision_type TEXT NOT NULL,
            status TEXT,
            recommended_option_id TEXT,
            selected_option_id TEXT,
            override_vs_recommendation INTEGER DEFAULT 0
        );
        CREATE TABLE decision_outcomes (
            outcome_id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id TEXT NOT NULL,
            execution_completed INTEGER DEFAULT 0,
            outcome_label TEXT
        );
        CREATE TABLE ask_user_question_decisions (
            decision_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            recommended_index INTEGER,
            selected_index INTEGER,
            confidence_score REAL,
            context TEXT,
            packet_json TEXT,
            decision_type TEXT DEFAULT 'enriched_choice'
        );
        """
    )
    iso = "2026-05-10T12:00:00+00:00"
    conn.execute(
        "INSERT INTO decisions VALUES ('d1', ?, 'refactor_scope', 'resolved', 'a', 'a', 0)",
        (iso,),
    )
    conn.execute(
        "INSERT INTO decision_outcomes (decision_id, execution_completed, outcome_label) "
        "VALUES ('d1', 1, 'success')"
    )
    conn.execute(
        "INSERT INTO ask_user_question_decisions "
        "(decision_id, created_at, recommended_index, selected_index, packet_json) "
        "VALUES ('auq1', ?, 0, 0, '{}')",
        (iso,),
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(mod, "DB_PATH", db)
    monkeypatch.setattr(mod, "_DEFAULT_SLA_UNBOUND_DAYS", 9999)
    payload = mod.build_payload(days=30)
    assert payload.get("error") is None
    assert payload.get("advisory_only") is True
    assert payload.get("report_version") == "author-gate-learning-join-w4-1"
    assert payload["author_gate"]["bound_with_outcome"] == 1
    assert payload["author_gate"]["selected_equals_recommended_when_both_set"] == 1
    assert payload["author_gate"]["recommendation_match_rate"] == 1.0
    assert payload["ask_user_question"]["rows_in_window"] == 1
    assert payload["ask_user_question"]["auq_recommendation_match_rate"] == 1.0


def test_main_writes_files(mod, tmp_path, monkeypatch):
    db = tmp_path / "ledger.sqlite"
    conn = sqlite3.connect(str(db))
    conn.execute(
        "CREATE TABLE decisions (decision_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, "
        "decision_type TEXT, status TEXT, recommended_option_id TEXT, "
        "selected_option_id TEXT, override_vs_recommendation INTEGER)"
    )
    conn.execute(
        "CREATE TABLE decision_outcomes ("
        "outcome_id INTEGER PRIMARY KEY AUTOINCREMENT, decision_id TEXT NOT NULL, "
        "execution_completed INTEGER, outcome_label TEXT)"
    )
    conn.execute(
        "INSERT INTO decisions VALUES ('d1', '2026-05-10T12:00:00+00:00', "
        "'refactor_scope', 'surfaced', NULL, NULL, 0)"
    )
    conn.commit()
    conn.close()
    monkeypatch.setattr(mod, "DB_PATH", db)
    outdir = tmp_path / "out"
    monkeypatch.setattr(mod, "REPORT_DIR", outdir)

    monkeypatch.setattr(sys, "argv", ["author_gate_learning_join_report.py", "--days", "400"])
    assert mod.main() == 0
    files = list(outdir.glob("ag_learning_join_*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    assert "author_gate" in data
