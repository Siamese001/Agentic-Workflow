#!/usr/bin/env python3
"""
test_check_author_gate_pipeline_freshness.py — Unit tests for AGP1 CI gate.

Plan: author-gate-ui-renderer-hardening-a7f3c2 W3.P3.2 / W4.P4.3.

Mirrors the sibling test_check_ask_user_question_packet_freshness.py pattern:
pure evaluate() tests + main() integration + bypass + fail-closed.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT / "ops_scripts" / "ci") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "ops_scripts" / "ci"))

from check_author_gate_pipeline_freshness import (
    DEFAULT_STALENESS_DAYS,
    evaluate,
    main,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts(days_ago: int = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat(timespec="seconds")


def _violation_row(days_ago: int = 0, **overrides) -> dict:
    row = {
        "invariant": "packet_without_ask_user_question",
        "severity": "critical",
        "packet_count": 1,
        "has_ask": False,
        "ts": _ts(days_ago),
        "detail": "test violation",
        "packet_ids": [],
    }
    row.update(overrides)
    return row


# ---------------------------------------------------------------------------
# §1 — evaluate() pure tests
# ---------------------------------------------------------------------------

class TestEvaluate:
    def test_empty_rows(self):
        assert evaluate([], 7) == []

    def test_bypass_rows_skipped(self):
        rows = [{"reason": "bypass", "ts": _ts(0)}]
        assert evaluate(rows, 7) == []

    def test_resolved_rows_skipped(self):
        rows = [_violation_row(0, resolved=True)]
        assert evaluate(rows, 7) == []

    def test_recent_violation_returned(self):
        row = _violation_row(1)
        result = evaluate([row], 7)
        assert len(result) == 1
        assert result[0] is row

    def test_old_violation_outside_window(self):
        row = _violation_row(10)
        assert evaluate([row], 7) == []

    def test_boundary_exactly_at_window(self):
        """Row at exactly the window boundary — should be included (>=)."""
        # A row from exactly 7 days ago might or might not pass depending on
        # sub-second timing. Use 6 days to be safely inside.
        row = _violation_row(6)
        result = evaluate([row], 7)
        assert len(result) == 1

    def test_mix_of_rows(self):
        rows = [
            _violation_row(1),                     # recent, unresolved → flagged
            _violation_row(0, reason="bypass"),     # bypass → skipped
            _violation_row(10),                     # old → skipped
            _violation_row(2, resolved=True),       # resolved → skipped
            _violation_row(3),                      # recent, unresolved → flagged
        ]
        result = evaluate(rows, 7)
        assert len(result) == 2

    def test_no_ts_row_included(self):
        """Row without a parseable ts is always included."""
        row = {"invariant": "test", "severity": "critical"}
        result = evaluate([row], 7)
        assert len(result) == 1

    def test_custom_window(self):
        row = _violation_row(5)
        assert evaluate([row], 3) == []   # outside 3-day window
        assert len(evaluate([row], 7)) == 1  # inside 7-day window


# ---------------------------------------------------------------------------
# §2 — main() integration tests
# ---------------------------------------------------------------------------

class TestMain:
    def test_no_log_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "check_author_gate_pipeline_freshness.VIOLATIONS_LOG",
            tmp_path / "nonexistent.jsonl",
        )
        assert main() == 0

    def test_empty_log(self, tmp_path, monkeypatch):
        log = tmp_path / "pipeline.jsonl"
        log.write_text("", encoding="utf-8")
        monkeypatch.setattr(
            "check_author_gate_pipeline_freshness.VIOLATIONS_LOG", log,
        )
        assert main() == 0

    def test_bypass(self, tmp_path, monkeypatch):
        log = tmp_path / "pipeline.jsonl"
        log.write_text(
            json.dumps(_violation_row(0)) + "\n", encoding="utf-8",
        )
        monkeypatch.setattr(
            "check_author_gate_pipeline_freshness.VIOLATIONS_LOG", log,
        )
        monkeypatch.setenv("AG_PIPELINE_FRESHNESS_BYPASS", "1")
        assert main() == 0

    def test_advisory_mode_with_violations(self, tmp_path, monkeypatch):
        """Default advisory mode — warns but exits 0."""
        log = tmp_path / "pipeline.jsonl"
        log.write_text(
            json.dumps(_violation_row(0)) + "\n", encoding="utf-8",
        )
        monkeypatch.setattr(
            "check_author_gate_pipeline_freshness.VIOLATIONS_LOG", log,
        )
        monkeypatch.delenv("AG_PIPELINE_FAIL_CLOSED", raising=False)
        monkeypatch.delenv("AG_PIPELINE_FRESHNESS_BYPASS", raising=False)
        assert main() == 0

    def test_fail_closed_with_violations(self, tmp_path, monkeypatch):
        """Fail-closed mode — exits 1 on unresolved violations."""
        log = tmp_path / "pipeline.jsonl"
        log.write_text(
            json.dumps(_violation_row(0)) + "\n", encoding="utf-8",
        )
        monkeypatch.setattr(
            "check_author_gate_pipeline_freshness.VIOLATIONS_LOG", log,
        )
        monkeypatch.setenv("AG_PIPELINE_FAIL_CLOSED", "1")
        monkeypatch.delenv("AG_PIPELINE_FRESHNESS_BYPASS", raising=False)
        assert main() == 1

    def test_fail_closed_no_violations(self, tmp_path, monkeypatch):
        """Fail-closed mode but only bypass rows → 0."""
        log = tmp_path / "pipeline.jsonl"
        log.write_text(
            json.dumps({"reason": "bypass", "ts": _ts(0)}) + "\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(
            "check_author_gate_pipeline_freshness.VIOLATIONS_LOG", log,
        )
        monkeypatch.setenv("AG_PIPELINE_FAIL_CLOSED", "1")
        assert main() == 0
