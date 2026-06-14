# pylint: disable=protected-access
"""Unit tests for detect_author_gate_ledger_anomalies (W4.1)."""

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
MOD_PATH = REPO_ROOT / "ops_scripts" / "ci" / "decision_ledger" / "detect_decision_ledger_anomalies.py"


def _load():
    name = "detect_author_gate_ledger_anomalies_tested"
    spec = importlib.util.spec_from_file_location(name, MOD_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture()
def tiny_ledger(tmp_path: Path, mod, monkeypatch) -> Path:
    db = tmp_path / "refactor_decision_ledger.sqlite"
    conn = sqlite3.connect(str(db))
    conn.executescript(
        """
        CREATE TABLE decisions (
            decision_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            decision_type TEXT NOT NULL DEFAULT 'refactor_scope',
            normalized_intent TEXT,
            status TEXT DEFAULT 'surfaced'
        );
        CREATE TABLE decision_outcomes (
            outcome_id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id TEXT NOT NULL,
            promote_to_pattern INTEGER DEFAULT 0,
            bound_at TEXT
        );
        """
    )
    conn.commit()
    conn.close()
    monkeypatch.setattr(mod, "REFACTOR_DECISION_LEDGER_DB", db)
    return db


def test_run_detection_future_timestamp(tiny_ledger, mod):
    conn = sqlite3.connect(str(tiny_ledger))
    conn.execute(
        "INSERT INTO decisions (decision_id, created_at, normalized_intent) "
        "VALUES ('d1', '2099-01-01T00:00:00+00:00', 'future')"
    )
    conn.commit()
    conn.close()

    payload = mod.run_detection()
    assert any(f["code"] == "FUTURE_DECISION_TIMESTAMP" for f in payload["findings"])
    assert payload["summary"]["high"] >= 1


def test_run_detection_bound_before_surfaced(tiny_ledger, mod):
    conn = sqlite3.connect(str(tiny_ledger))
    conn.execute(
        "INSERT INTO decisions (decision_id, created_at, normalized_intent) "
        "VALUES ('d1', '2026-05-01T12:00:00+00:00', 'x')"
    )
    conn.execute(
        "INSERT INTO decision_outcomes (decision_id, bound_at) VALUES ('d1', '2026-04-01T12:00:00+00:00')"
    )
    conn.commit()
    conn.close()

    payload = mod.run_detection()
    assert any(f["code"] == "BOUND_BEFORE_SURFACED" for f in payload["findings"])


def test_run_detection_duplicate_intent(tiny_ledger, mod):
    conn = sqlite3.connect(str(tiny_ledger))
    for i in range(3):
        conn.execute(
            "INSERT INTO decisions (decision_id, created_at, normalized_intent, decision_type) "
            f"VALUES ('d{i}', '2026-05-01T12:00:0{i}+00:00', 'same intent', 'refactor_scope')"
        )
    conn.commit()
    conn.close()

    payload = mod.run_detection(dup_intent_min=3)
    assert any(f["code"] == "DUPLICATE_INTENT_CLUSTER" for f in payload["findings"])
