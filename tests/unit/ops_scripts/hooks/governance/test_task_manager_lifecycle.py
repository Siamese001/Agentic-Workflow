"""
Focused lifecycle invariant tests for task_manager MCP hardening.

Covers:
  post_mcp_audit.py  — lifecycle state signal handlers
  pre_write_gate.py  — pre-execution lifecycle enforcement
  pre_prompt_classifier.py — continuation-turn preservation + open-task warning

All tests use mocks/fakes — no real filesystem MCP, no real Node.js, no real task_manager.
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

# Resolve script paths relative to this test file's location.
_SCRIPTS = Path(__file__).resolve().parents[5] / ".codex" / "governance/scripts"
sys.path.insert(0, str(_SCRIPTS))

import post_mcp_audit as _audit_module
import pre_prompt_classifier as _classifier_module
import pre_write_gate as _write_gate_module
from post_mcp_audit import _mark_task_created, _mark_task_decomposed, _mark_task_started
from pre_write_gate import check_task_exists


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_state(tmp_path: Path, **fields) -> Path:
    """Write a session_state.json under tmp_path and return its path."""
    state_file = tmp_path / "session_state.json"
    state_file.write_text(json.dumps(fields), encoding="utf-8")
    return state_file


def _read_state(state_file: Path) -> dict[str, object]:
    result: dict[str, object] = json.loads(state_file.read_text(encoding="utf-8"))
    return result


# ---------------------------------------------------------------------------
# post_mcp_audit — lifecycle state signals
# ---------------------------------------------------------------------------


class TestMarkTaskCreated:
    def test_sets_task_created_true(self, tmp_path):
        state_file = _make_state(tmp_path, current_tier="T2", task_created=False)
        with patch.object(_audit_module, "session_state", state_file):
            _mark_task_created()
        assert _read_state(state_file)["task_created"] is True

    def test_creates_file_if_missing(self, tmp_path):
        state_file = tmp_path / "session_state.json"
        with patch.object(_audit_module, "session_state", state_file):
            _mark_task_created()
        assert _read_state(state_file)["task_created"] is True


class TestMarkTaskStarted:
    def test_sets_task_started_true(self, tmp_path):
        state_file = _make_state(
            tmp_path,
            current_tier="T2",
            task_created=True,
            task_started=False,
            update_task_count=0,
            lessons_captured=False,
        )
        with patch.object(_audit_module, "session_state", state_file):
            _mark_task_started()
        s = _read_state(state_file)
        assert s["task_started"] is True

    def test_increments_update_task_count(self, tmp_path):
        state_file = _make_state(tmp_path, task_started=False, update_task_count=0, lessons_captured=False)
        with patch.object(_audit_module, "session_state", state_file):
            _mark_task_started()
        assert _read_state(state_file)["update_task_count"] == 1

    def test_second_update_sets_lessons_captured(self, tmp_path):
        state_file = _make_state(tmp_path, task_started=True, update_task_count=1, lessons_captured=False)
        with patch.object(_audit_module, "session_state", state_file):
            _mark_task_started()
        s = _read_state(state_file)
        assert s["update_task_count"] == 2
        assert s["lessons_captured"] is True

    def test_first_update_does_not_set_lessons_captured(self, tmp_path):
        state_file = _make_state(tmp_path, task_started=False, update_task_count=0, lessons_captured=False)
        with patch.object(_audit_module, "session_state", state_file):
            _mark_task_started()
        assert _read_state(state_file)["lessons_captured"] is False


class TestMarkTaskDecomposed:
    def test_sets_task_decomposed_true(self, tmp_path):
        state_file = _make_state(tmp_path, current_tier="T3", task_decomposed=False)
        with patch.object(_audit_module, "session_state", state_file):
            _mark_task_decomposed()
        assert _read_state(state_file)["task_decomposed"] is True

    def test_creates_file_if_missing(self, tmp_path):
        state_file = tmp_path / "session_state.json"
        with patch.object(_audit_module, "session_state", state_file):
            _mark_task_decomposed()
        assert _read_state(state_file)["task_decomposed"] is True


# ---------------------------------------------------------------------------
# pre_write_gate — lifecycle enforcement
# ---------------------------------------------------------------------------


class TestCheckTaskExistsLifecycle:
    """check_task_exists enforces the three-step pre-execution lifecycle gate."""

    def test_t2_blocked_without_task_created(self, tmp_path):
        state_file = _make_state(
            tmp_path, current_tier="T2", task_created=False, task_started=False, task_decomposed=False
        )
        with patch.object(_write_gate_module, "session_state", state_file):
            result = check_task_exists("/repo/foo.py")
        assert result is not None
        assert "create_task" in result

    def test_t2_blocked_without_task_started(self, tmp_path):
        state_file = _make_state(
            tmp_path, current_tier="T2", task_created=True, task_started=False, task_decomposed=False
        )
        with patch.object(_write_gate_module, "session_state", state_file):
            result = check_task_exists("/repo/foo.py")
        assert result is not None
        assert "update_task" in result

    def test_t3_blocked_without_task_decomposed(self, tmp_path):
        state_file = _make_state(
            tmp_path, current_tier="T3", task_created=True, task_started=True, task_decomposed=False
        )
        with patch.object(_write_gate_module, "session_state", state_file):
            result = check_task_exists("/repo/foo.py")
        assert result is not None
        assert "decompose_task" in result

    def test_t2_allowed_with_valid_prestart(self, tmp_path):
        state_file = _make_state(
            tmp_path, current_tier="T2", task_created=True, task_started=True, task_decomposed=False
        )
        with patch.object(_write_gate_module, "session_state", state_file):
            result = check_task_exists("/repo/foo.py")
        assert result is None

    def test_t3_allowed_with_full_prestart(self, tmp_path):
        state_file = _make_state(
            tmp_path, current_tier="T3", task_created=True, task_started=True, task_decomposed=True
        )
        with patch.object(_write_gate_module, "session_state", state_file):
            result = check_task_exists("/repo/foo.py")
        assert result is None

    def test_t1_always_allowed(self, tmp_path):
        state_file = _make_state(
            tmp_path, current_tier="T1", task_created=False, task_started=False, task_decomposed=False
        )
        with patch.object(_write_gate_module, "session_state", state_file):
            result = check_task_exists("/repo/foo.py")
        assert result is None

    def test_non_py_file_always_allowed(self, tmp_path):
        state_file = _make_state(
            tmp_path, current_tier="T3", task_created=False, task_started=False, task_decomposed=False
        )
        with patch.object(_write_gate_module, "session_state", state_file):
            result = check_task_exists("/repo/config.yaml")
        assert result is None

    def test_fail_open_on_missing_state_file(self, tmp_path):
        missing = tmp_path / "no_such_file.json"
        with patch.object(_write_gate_module, "session_state", missing):
            result = check_task_exists("/repo/foo.py")
        assert result is None

    def test_check_order_task_created_before_decomposed(self, tmp_path):
        """When task_created is false, the error must mention create_task, not decompose_task."""
        state_file = _make_state(
            tmp_path, current_tier="T3", task_created=False, task_started=False, task_decomposed=False
        )
        with patch.object(_write_gate_module, "session_state", state_file):
            result = check_task_exists("/repo/foo.py")
        assert "create_task" in result
        assert "decompose_task" not in result


# ---------------------------------------------------------------------------
# pre_prompt_classifier — continuation-turn preservation + open-task warning
# ---------------------------------------------------------------------------


class TestWriteSessionStatePreservation:
    """_write_session_state preserves lifecycle fields on T2/T3 continuation turns."""

    def test_t1_prompt_fully_resets_lifecycle_fields(self, tmp_path):
        state_file = _make_state(
            tmp_path,
            current_tier="T3",
            task_created=True,
            task_started=True,
            task_decomposed=True,
            update_task_count=1,
            lessons_captured=False,
        )
        with patch.object(_classifier_module, "session_state", state_file):
            _classifier_module._write_session_state("T1")
        s = _read_state(state_file)
        assert s["task_created"] is False
        assert s["task_started"] is False
        assert s["task_decomposed"] is False
        assert s["update_task_count"] == 0
        assert s["lessons_captured"] is False

    def test_t0_prompt_fully_resets_lifecycle_fields(self, tmp_path):
        state_file = _make_state(
            tmp_path,
            current_tier="T3",
            task_created=True,
            task_started=True,
            task_decomposed=True,
            update_task_count=2,
            lessons_captured=True,
        )
        with patch.object(_classifier_module, "session_state", state_file):
            _classifier_module._write_session_state("T0")
        s = _read_state(state_file)
        assert s["task_created"] is False
        assert s["update_task_count"] == 0

    def test_t2_continuation_preserves_lifecycle_fields(self, tmp_path):
        state_file = _make_state(
            tmp_path,
            current_tier="T2",
            task_created=True,
            task_started=True,
            task_decomposed=False,
            update_task_count=1,
            lessons_captured=False,
        )
        with patch.object(_classifier_module, "session_state", state_file):
            _classifier_module._write_session_state("T2")
        s = _read_state(state_file)
        assert s["task_created"] is True
        assert s["task_started"] is True
        assert s["update_task_count"] == 1

    def test_t3_continuation_preserves_lifecycle_fields(self, tmp_path):
        state_file = _make_state(
            tmp_path,
            current_tier="T3",
            task_created=True,
            task_started=True,
            task_decomposed=True,
            update_task_count=1,
            lessons_captured=False,
        )
        with patch.object(_classifier_module, "session_state", state_file):
            _classifier_module._write_session_state("T3")
        s = _read_state(state_file)
        assert s["task_created"] is True
        assert s["task_decomposed"] is True
        assert s["update_task_count"] == 1

    def test_t2_with_no_prior_state_defaults_to_false(self, tmp_path):
        missing = tmp_path / "no_state.json"
        with patch.object(_classifier_module, "session_state", missing):
            _classifier_module._write_session_state("T2")
        s = _read_state(missing)
        assert s["task_created"] is False
        assert s["update_task_count"] == 0


class TestWarnOpenTask:
    """_warn_open_task emits advisory to stderr when prior task is unclosed."""

    def test_warns_when_task_open_and_count_less_than_2(self, tmp_path, capsys):
        state_file = _make_state(tmp_path, task_created=True, update_task_count=1)
        with patch.object(_classifier_module, "session_state", state_file):
            _classifier_module._warn_open_task("T2")
        captured = capsys.readouterr()
        assert "prior T2/T3 task was not closed" in captured.err

    def test_no_warn_when_task_closed(self, tmp_path, capsys):
        state_file = _make_state(tmp_path, task_created=True, update_task_count=2)
        with patch.object(_classifier_module, "session_state", state_file):
            _classifier_module._warn_open_task("T2")
        captured = capsys.readouterr()
        assert "not closed" not in captured.err

    def test_no_warn_when_no_task_created(self, tmp_path, capsys):
        state_file = _make_state(tmp_path, task_created=False, update_task_count=0)
        with patch.object(_classifier_module, "session_state", state_file):
            _classifier_module._warn_open_task("T3")
        captured = capsys.readouterr()
        assert "not closed" not in captured.err

    def test_no_warn_when_state_file_missing(self, tmp_path, capsys):
        missing = tmp_path / "no_state.json"
        with patch.object(_classifier_module, "session_state", missing):
            _classifier_module._warn_open_task("T2")
        captured = capsys.readouterr()
        assert "not closed" not in captured.err
