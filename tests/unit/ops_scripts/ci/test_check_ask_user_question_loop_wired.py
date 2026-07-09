"""Tests for check_ask_user_question_loop_wired — the loop-wiring health check.

Plan: askq-confidence-meta-learning-loop-c4e7a1 (W3.1). Asserts the gate recognises the wired
loop on this branch (hook registered + files present + ledger writable) and that fail-closed mode
flips the exit code when a seam is missing.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_ask_user_question_loop_wired.py"
_spec = importlib.util.spec_from_file_location("check_ask_user_question_loop_wired", _GATE_PATH)
assert _spec and _spec.loader
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def test_all_seams_wired_on_this_branch():
    results = {name: ok for name, ok, _ in gate.run_checks()}
    # On the feat branch every seam is present.
    assert results["pre_tool_use_hook_registered"] is True
    assert results["post_tool_use_hook_registered"] is True
    assert results["shape_hook_exists"] is True
    assert results["capture_hook_exists"] is True
    assert results["capture_ssot_exists"] is True
    assert results["calibration_helper_exists"] is True
    assert results["ledger_writable"] is True


def test_main_passes_when_wired():
    assert gate.main() == 0


def test_post_hook_detection_reads_settings():
    # The detector must match request_user_input PostToolUse -> after_ask_user_question.py.
    assert gate._post_hook_registered() is True


def test_pre_hook_detection_reads_settings():
    # The detector must match request_user_input PreToolUse -> before_ask_user_question.py.
    assert gate._pre_hook_registered() is True


def test_fail_closed_flips_exit_on_missing_seam(monkeypatch):
    monkeypatch.setattr(gate, "_pre_hook_registered", lambda: False)
    monkeypatch.setenv("ASKQ_LOOP_WIRED_FAIL_CLOSED", "1")
    assert gate.main() == 1


def test_advisory_default_stays_zero_on_missing_seam(monkeypatch):
    monkeypatch.setattr(gate, "_pre_hook_registered", lambda: False)
    monkeypatch.delenv("ASKQ_LOOP_WIRED_FAIL_CLOSED", raising=False)
    assert gate.main() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
