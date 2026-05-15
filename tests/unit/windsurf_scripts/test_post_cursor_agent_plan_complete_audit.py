"""
Unit tests for .windsurf/scripts/post_cursor_agent_plan_complete_audit.py

Plan: plan-complete-marker-enforcement-d2e9f1 W3.1
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / ".windsurf" / "scripts" / "post_cursor_agent_plan_complete_audit.py"

spec = importlib.util.spec_from_file_location("post_cursor_agent_plan_complete_audit", _SCRIPT)
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_payload(response_text: str) -> str:
    import json
    return json.dumps({"response_text": response_text})


_TODO_ALL_DONE = """
<tool_call>
{"name": "todo_list", "todos": [
  {"id": "1", "content": "Do X", "status": "completed", "priority": "high"},
  {"id": "2", "content": "Do Y", "status": "completed", "priority": "medium"}
]}
</tool_call>
"""

_TODO_MIXED = """
<tool_call>
{"name": "todo_list", "todos": [
  {"id": "1", "content": "Do X", "status": "completed", "priority": "high"},
  {"id": "2", "content": "Do Y", "status": "in_progress", "priority": "medium"}
]}
</tool_call>
"""

_TODO_NONE = "No todo list in this response at all."


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAllTodosCompleted:
    def test_all_done_returns_true(self):
        assert _mod._all_todos_completed(_TODO_ALL_DONE) is True

    def test_mixed_returns_false(self):
        assert _mod._all_todos_completed(_TODO_MIXED) is False

    def test_no_todos_returns_false(self):
        assert _mod._all_todos_completed(_TODO_NONE) is False

    def test_empty_string_returns_false(self):
        assert _mod._all_todos_completed("") is False

    def test_single_pending(self):
        txt = '{"todos": [{"status": "pending"}]}'
        assert _mod._all_todos_completed(txt) is False

    def test_single_completed(self):
        txt = '{"todos": [{"status": "completed"}]}'
        assert _mod._all_todos_completed(txt) is True


class TestHasPlanCompleteMarker:
    def test_line_start_marker_detected(self):
        text = "Some response.\nPLAN_COMPLETE: plan=foo-abc123\nmore text"
        assert _mod._has_plan_complete_marker(text) is True

    def test_marker_with_leading_spaces_detected(self):
        text = "  PLAN_COMPLETE: plan=foo-abc123"
        assert _mod._has_plan_complete_marker(text) is True

    def test_marker_mid_sentence_not_detected(self):
        # Not at line start — embedded in prose
        text = "The plan docs say PLAN_COMPLETE: is needed but this is mid-sentence"
        # Our regex is re.MULTILINE with ^\s* so "The plan docs say PLAN_COMPLETE:"
        # does NOT match because there are non-whitespace chars before it on that line.
        assert _mod._has_plan_complete_marker(text) is False

    def test_no_marker_returns_false(self):
        assert _mod._has_plan_complete_marker("Just some text") is False

    def test_wave_complete_is_not_plan_complete(self):
        text = "WAVE_COMPLETE: plan=foo-abc123 wave=3"
        assert _mod._has_plan_complete_marker(text) is False


class TestMainFunction:
    def test_bypass_env_var_skips_warn(self, monkeypatch, capsys):
        monkeypatch.setenv("PLAN_COMPLETE_AUDIT_BYPASS", "1")
        payload = _build_payload(_TODO_ALL_DONE)
        monkeypatch.setattr(sys, "stdin", __import__("io").StringIO(payload))
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        rc = _mod.main()
        assert rc == 0
        captured = capsys.readouterr()
        assert "WARNING" not in captured.err

    def test_all_done_no_marker_emits_warning(self, monkeypatch, capsys, tmp_path):
        monkeypatch.delenv("PLAN_COMPLETE_AUDIT_BYPASS", raising=False)
        monkeypatch.setattr(_mod, "LOG_PATH", tmp_path / "plan_complete_audit.jsonl")
        payload = _build_payload(_TODO_ALL_DONE)
        monkeypatch.setattr(sys, "stdin", __import__("io").StringIO(payload))
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        rc = _mod.main()
        assert rc == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.err

    def test_all_done_with_marker_no_warning(self, monkeypatch, capsys, tmp_path):
        monkeypatch.delenv("PLAN_COMPLETE_AUDIT_BYPASS", raising=False)
        monkeypatch.setattr(_mod, "LOG_PATH", tmp_path / "plan_complete_audit.jsonl")
        text = _TODO_ALL_DONE + "\nPLAN_COMPLETE: plan=foo-abc123\n"
        payload = _build_payload(text)
        monkeypatch.setattr(sys, "stdin", __import__("io").StringIO(payload))
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        rc = _mod.main()
        assert rc == 0
        captured = capsys.readouterr()
        assert "WARNING" not in captured.err

    def test_mixed_todos_no_warning(self, monkeypatch, capsys, tmp_path):
        monkeypatch.delenv("PLAN_COMPLETE_AUDIT_BYPASS", raising=False)
        monkeypatch.setattr(_mod, "LOG_PATH", tmp_path / "plan_complete_audit.jsonl")
        payload = _build_payload(_TODO_MIXED)
        monkeypatch.setattr(sys, "stdin", __import__("io").StringIO(payload))
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        rc = _mod.main()
        assert rc == 0
        captured = capsys.readouterr()
        assert "WARNING" not in captured.err

    def test_no_todos_no_warning(self, monkeypatch, capsys, tmp_path):
        monkeypatch.delenv("PLAN_COMPLETE_AUDIT_BYPASS", raising=False)
        monkeypatch.setattr(_mod, "LOG_PATH", tmp_path / "plan_complete_audit.jsonl")
        payload = _build_payload(_TODO_NONE)
        monkeypatch.setattr(sys, "stdin", __import__("io").StringIO(payload))
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        rc = _mod.main()
        assert rc == 0
        captured = capsys.readouterr()
        assert "WARNING" not in captured.err

    def test_empty_stdin_no_warning(self, monkeypatch, capsys, tmp_path):
        monkeypatch.delenv("PLAN_COMPLETE_AUDIT_BYPASS", raising=False)
        monkeypatch.setattr(_mod, "LOG_PATH", tmp_path / "plan_complete_audit.jsonl")
        monkeypatch.setattr(sys, "stdin", __import__("io").StringIO("  "))
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        rc = _mod.main()
        assert rc == 0
        captured = capsys.readouterr()
        assert "WARNING" not in captured.err

    def test_always_exits_zero(self, monkeypatch, tmp_path):
        monkeypatch.delenv("PLAN_COMPLETE_AUDIT_BYPASS", raising=False)
        monkeypatch.setattr(_mod, "LOG_PATH", tmp_path / "plan_complete_audit.jsonl")
        payload = _build_payload(_TODO_ALL_DONE)
        monkeypatch.setattr(sys, "stdin", __import__("io").StringIO(payload))
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        rc = _mod.main()
        assert rc == 0
