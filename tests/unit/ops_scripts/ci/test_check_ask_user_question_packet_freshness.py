"""Tests for ops_scripts/ci/author_gate/check_ask_user_question_packet_freshness.py.

Plan: author-gate-four-req-enforcement-c4d2a8 W2.P4.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE_PATH = (
    REPO_ROOT
    / "ops_scripts"
    / "ci"
    / "author_gate"
    / "check_ask_user_question_packet_freshness.py"
)


def _load(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gate():
    return _load("check_ask_user_question_packet_freshness", GATE_PATH)


def _row(ts: datetime, **extra: Any) -> dict[str, Any]:
    return {"ts": ts.isoformat(timespec="seconds"), **extra}


# ------------------------------ evaluate() pure-function tests ------------------------------


def test_empty_rows_returns_empty(gate):
    assert gate.evaluate([], window_days=7) == []


def test_recent_unresolved_row_is_returned(gate):
    rows = [_row(datetime.now(timezone.utc), severity="critical", reason="vacuum")]
    assert gate.evaluate(rows, window_days=7) == rows


def test_aged_row_is_dropped(gate):
    rows = [
        _row(
            datetime.now(timezone.utc) - timedelta(days=30),
            severity="critical",
            reason="old",
        )
    ]
    assert gate.evaluate(rows, window_days=7) == []


def test_resolved_row_is_skipped(gate):
    rows = [
        _row(
            datetime.now(timezone.utc),
            severity="critical",
            reason="vacuum",
            resolved=True,
        )
    ]
    assert gate.evaluate(rows, window_days=7) == []


def test_bypass_row_is_skipped(gate):
    rows = [_row(datetime.now(timezone.utc), reason="bypass")]
    assert gate.evaluate(rows, window_days=7) == []


def test_malformed_timestamp_treated_as_recent(gate):
    rows = [{"ts": "not-a-timestamp", "severity": "high", "reason": "weird"}]
    assert gate.evaluate(rows, window_days=7) == rows


def test_mixed_rows_filtered_correctly(gate):
    now = datetime.now(timezone.utc)
    rows = [
        _row(now, severity="high", reason="recent_unresolved"),
        _row(now, severity="high", reason="recent_resolved", resolved=True),
        _row(now - timedelta(days=10), severity="high", reason="aged"),
        _row(now, reason="bypass"),
    ]
    out = gate.evaluate(rows, window_days=7)
    assert len(out) == 1
    assert out[0]["reason"] == "recent_unresolved"


# ------------------------------ main() integration ------------------------------


def test_main_returns_zero_when_log_missing(gate, tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "VIOLATIONS_LOG", tmp_path / "missing.jsonl")
    assert gate.main() == 0


def test_main_returns_zero_when_log_empty(gate, tmp_path, monkeypatch):
    log = tmp_path / "empty.jsonl"
    log.write_text("", encoding="utf-8")
    monkeypatch.setattr(gate, "VIOLATIONS_LOG", log)
    assert gate.main() == 0


def test_main_returns_one_on_recent_unresolved(gate, tmp_path, monkeypatch, capsys):
    log = tmp_path / "violations.jsonl"
    row = _row(datetime.now(timezone.utc), severity="critical", reason="vacuum")
    log.write_text(json.dumps(row) + "\n", encoding="utf-8")
    monkeypatch.setattr(gate, "VIOLATIONS_LOG", log)
    assert gate.main() == 1
    err = capsys.readouterr().err
    assert "unresolved vacuum-closure violations" in err


def test_main_bypass_returns_zero(gate, tmp_path, monkeypatch):
    log = tmp_path / "violations.jsonl"
    row = _row(datetime.now(timezone.utc), severity="critical", reason="vacuum")
    log.write_text(json.dumps(row) + "\n", encoding="utf-8")
    monkeypatch.setattr(gate, "VIOLATIONS_LOG", log)
    monkeypatch.setenv("ASK_PACKET_AUDIT_FRESHNESS_BYPASS", "1")
    assert gate.main() == 0
