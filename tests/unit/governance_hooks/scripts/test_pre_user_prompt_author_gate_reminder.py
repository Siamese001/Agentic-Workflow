"""
Tests for pre_user_prompt_author_gate_reminder.py

Verifies:
- PATH A: prompt signal detection fires at ≥2 signals, silent at <2
- PATH B: recent violation replay emits remediation for bypass and UI violations
- REPLAY window correctly excludes stale violations
- Bypass env var suppresses all output
- Always exits 0 (never blocks)
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import types
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = REPO_ROOT / ".claude" / "governance/scripts" / "pre_user_prompt_author_gate_reminder.py"


def _load_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(
        "pre_user_prompt_author_gate_reminder", SCRIPT_PATH
    )
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


@pytest.fixture()
def mod():
    return _load_module()


class TestPromptSignalDetection:
    def test_zero_signals_no_output(self, mod, capsys):
        count = mod._count_prompt_signals("Hello, just a general question about Python.")
        assert count == 0

    def test_one_signal_below_threshold(self, mod):
        count = mod._count_prompt_signals("I want to use ask_user_question.")
        assert count == 1

    def test_two_signals_at_threshold(self, mod):
        count = mod._count_prompt_signals("Should I use ask_user_question for this author gate?")
        assert count >= 2

    def test_author_gate_packet_signal(self, mod):
        count = mod._count_prompt_signals("Emit AUTHOR_GATE_PACKET before calling ask_user_question")
        assert count >= 2

    def test_refactoring_scope_signal(self, mod):
        text = "refactoring scope for the ask_user_question options"
        assert mod._count_prompt_signals(text) >= 2

    def test_hitl_signal(self, mod):
        text = "HITL decision point with ask_user_question"
        assert mod._count_prompt_signals(text) >= 2


class TestViolationReading:
    def test_empty_violations_file(self, mod, tmp_path):
        p = tmp_path / "violations.jsonl"
        p.write_text("", encoding="utf-8")
        rows = mod._read_recent_violations(p, window_minutes=120)
        assert rows == []

    def test_missing_violations_file(self, mod, tmp_path):
        p = tmp_path / "does_not_exist.jsonl"
        rows = mod._read_recent_violations(p, window_minutes=120)
        assert rows == []

    def test_recent_violation_included(self, mod, tmp_path):
        p = tmp_path / "violations.jsonl"
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        row = {"timestamp": ts, "violation_type": "handcrafted_author_gate_detected", "severity": "advisory"}
        p.write_text(json.dumps(row) + "\n", encoding="utf-8")
        rows = mod._read_recent_violations(p, window_minutes=120)
        assert len(rows) == 1
        assert rows[0]["violation_type"] == "handcrafted_author_gate_detected"

    def test_stale_violation_excluded(self, mod, tmp_path):
        p = tmp_path / "violations.jsonl"
        old_ts = (datetime.now(timezone.utc) - timedelta(minutes=200)).isoformat(timespec="seconds")
        row = {"timestamp": old_ts, "violation_type": "handcrafted_author_gate_detected"}
        p.write_text(json.dumps(row) + "\n", encoding="utf-8")
        rows = mod._read_recent_violations(p, window_minutes=120)
        assert rows == []

    def test_malformed_json_skipped(self, mod, tmp_path):
        p = tmp_path / "violations.jsonl"
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        valid = json.dumps({"timestamp": ts, "violation_type": "missing_confidence_prefix"})
        p.write_text("not-json\n" + valid + "\n", encoding="utf-8")
        rows = mod._read_recent_violations(p, window_minutes=120)
        assert len(rows) == 1

    def test_violation_missing_timestamp_skipped(self, mod, tmp_path):
        p = tmp_path / "violations.jsonl"
        row = {"violation_type": "missing_confidence_prefix"}
        p.write_text(json.dumps(row) + "\n", encoding="utf-8")
        rows = mod._read_recent_violations(p, window_minutes=120)
        assert rows == []


class TestMainExitCode:
    def test_always_exits_zero_no_violations(self, mod, tmp_path):
        with (
            patch.object(mod, "VIOLATIONS_PATH", tmp_path / "v.jsonl"),
            patch.object(mod, "ASK_VIOLATIONS_PATH", tmp_path / "a.jsonl"),
            patch("sys.stdin", StringIO("no signals here")),
        ):
            rc = mod.main()
        assert rc == 0

    def test_always_exits_zero_with_bypass_violations(self, mod, tmp_path):
        vpath = tmp_path / "v.jsonl"
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        row = {"timestamp": ts, "violation_type": "handcrafted_author_gate_detected"}
        vpath.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with (
            patch.object(mod, "VIOLATIONS_PATH", vpath),
            patch.object(mod, "ASK_VIOLATIONS_PATH", tmp_path / "a.jsonl"),
            patch("sys.stdin", StringIO("ask_user_question author gate")),
        ):
            rc = mod.main()
        assert rc == 0

    def test_bypass_env_suppresses_all(self, mod, tmp_path):
        vpath = tmp_path / "v.jsonl"
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        row = {"timestamp": ts, "violation_type": "handcrafted_author_gate_detected"}
        vpath.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with (
            patch.dict(os.environ, {"AG_REMINDER_BYPASS": "1"}),
            patch.object(mod, "VIOLATIONS_PATH", vpath),
            patch.object(mod, "ASK_VIOLATIONS_PATH", tmp_path / "a.jsonl"),
            patch("sys.stdin", StringIO("ask_user_question author gate author-gate-packet-builder")),
            patch("sys.stderr", new_callable=StringIO) as mock_err,
        ):
            rc = mod.main()
            stderr_output = mock_err.getvalue()
        assert rc == 0
        assert "AUTHOR_GATE_PIPELINE_REMINDER" not in stderr_output
        assert "AG_REMINDER_PATH" not in stderr_output


class TestPathAFiring:
    def test_path_a_fires_on_two_signals(self, mod, tmp_path, capsys):
        with (
            patch.object(mod, "VIOLATIONS_PATH", tmp_path / "v.jsonl"),
            patch.object(mod, "ASK_VIOLATIONS_PATH", tmp_path / "a.jsonl"),
            patch("sys.stdin", StringIO("ask_user_question for this author gate decision")),
            patch("sys.stderr", new_callable=StringIO) as mock_err,
        ):
            rc = mod.main()
            stderr_output = mock_err.getvalue()
        assert rc == 0
        assert "AUTHOR_GATE_PIPELINE_REMINDER" in stderr_output
        assert "AG_REMINDER_PATH_A" in stderr_output

    def test_path_a_silent_on_one_signal(self, mod, tmp_path):
        with (
            patch.object(mod, "VIOLATIONS_PATH", tmp_path / "v.jsonl"),
            patch.object(mod, "ASK_VIOLATIONS_PATH", tmp_path / "a.jsonl"),
            patch("sys.stdin", StringIO("just ask_user_question nothing else")),
            patch("sys.stderr", new_callable=StringIO) as mock_err,
        ):
            rc = mod.main()
            stderr_output = mock_err.getvalue()
        assert rc == 0
        assert "AG_REMINDER_PATH_A" not in stderr_output


class TestPathBFiring:
    def test_bypass_violation_triggers_path_b(self, mod, tmp_path):
        vpath = tmp_path / "v.jsonl"
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        row = {"timestamp": ts, "violation_type": "handcrafted_author_gate_detected", "severity": "advisory"}
        vpath.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with (
            patch.object(mod, "VIOLATIONS_PATH", vpath),
            patch.object(mod, "ASK_VIOLATIONS_PATH", tmp_path / "a.jsonl"),
            patch("sys.stdin", StringIO("")),
            patch("sys.stderr", new_callable=StringIO) as mock_err,
        ):
            mod.main()
            stderr_output = mock_err.getvalue()
        assert "AG_REMINDER_PATH_B" in stderr_output
        assert "AUTHOR_GATE_VIOLATION_REPLAY" in stderr_output
        assert "handcrafted_author_gate_detected" in stderr_output

    def test_ask_packet_violation_triggers_path_b(self, mod, tmp_path):
        apath = tmp_path / "a.jsonl"
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        row = {"timestamp": ts, "violation_type": "ask_user_question_without_packet"}
        apath.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with (
            patch.object(mod, "VIOLATIONS_PATH", tmp_path / "v.jsonl"),
            patch.object(mod, "ASK_VIOLATIONS_PATH", apath),
            patch("sys.stdin", StringIO("")),
            patch("sys.stderr", new_callable=StringIO) as mock_err,
        ):
            mod.main()
            stderr_output = mock_err.getvalue()
        assert "AG_REMINDER_PATH_B" in stderr_output
        assert "ask_user_question_without_packet" in stderr_output

    def test_ui_violation_triggers_path_b_ui(self, mod, tmp_path):
        vpath = tmp_path / "v.jsonl"
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        row = {"timestamp": ts, "violation_type": "missing_confidence_prefix"}
        vpath.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with (
            patch.object(mod, "VIOLATIONS_PATH", vpath),
            patch.object(mod, "ASK_VIOLATIONS_PATH", tmp_path / "a.jsonl"),
            patch("sys.stdin", StringIO("")),
            patch("sys.stderr", new_callable=StringIO) as mock_err,
        ):
            mod.main()
            stderr_output = mock_err.getvalue()
        assert "AG_REMINDER_PATH_B_UI" in stderr_output
        assert "missing_confidence_prefix" in stderr_output

    def test_stale_bypass_violation_does_not_trigger(self, mod, tmp_path):
        vpath = tmp_path / "v.jsonl"
        old_ts = (datetime.now(timezone.utc) - timedelta(minutes=200)).isoformat(timespec="seconds")
        row = {"timestamp": old_ts, "violation_type": "handcrafted_author_gate_detected"}
        vpath.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with (
            patch.object(mod, "VIOLATIONS_PATH", vpath),
            patch.object(mod, "ASK_VIOLATIONS_PATH", tmp_path / "a.jsonl"),
            patch("sys.stdin", StringIO("")),
            patch("sys.stderr", new_callable=StringIO) as mock_err,
        ):
            mod.main()
            stderr_output = mock_err.getvalue()
        assert "AG_REMINDER_PATH_B" not in stderr_output

    def test_remediation_text_matches_violation_type(self, mod, tmp_path):
        vpath = tmp_path / "v.jsonl"
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        row = {"timestamp": ts, "violation_type": "description_missing_tradeoff"}
        vpath.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with (
            patch.object(mod, "VIOLATIONS_PATH", vpath),
            patch.object(mod, "ASK_VIOLATIONS_PATH", tmp_path / "a.jsonl"),
            patch("sys.stdin", StringIO("")),
            patch("sys.stderr", new_callable=StringIO) as mock_err,
        ):
            mod.main()
            stderr_output = mock_err.getvalue()
        assert "surface_description_floor" in stderr_output
        assert "key_tradeoffs" in stderr_output


class TestPipelineReminderContent:
    def test_pipeline_reminder_names_all_four_steps(self, mod):
        reminder = mod.PIPELINE_REMINDER
        assert "refactor-decision-memory" in reminder
        assert "author-gate-packet-builder" in reminder
        assert "author-gate-ui-renderer" in reminder
        assert "ask_user_question" in reminder

    def test_pipeline_reminder_names_forbidden_pattern(self, mod):
        reminder = mod.PIPELINE_REMINDER
        assert "Do not hand-build options" in reminder

    def test_pipeline_reminder_shows_format_contract(self, mod):
        reminder = mod.PIPELINE_REMINDER
        assert "OPTIONS_JSON verbatim" in reminder
        assert "author-gate-ui-renderer" in reminder
