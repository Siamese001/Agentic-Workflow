"""Regression tests for stop_task_audit.py (PASS proof contract enforcement).

Commit f96f7a3735 flipped warn→block and added ARTIFACTS to PROOF_WORDS.
These tests lock that behavior so misleading PASS claims cannot slip through.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"
HOOK_PATH = HOOKS_DIR / "stop_task_audit.py"

_BLOCK = 2
_ALLOW = 0


def _run_stop(payload: dict) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(HOOKS_DIR)}
    return subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )


def _full_proof_response() -> str:
    return (
        "STATUS: PASS\n"
        "FILES_CHANGED: tests/foo.py\n"
        "COMMANDS_RUN: pytest tests/foo.py\n"
        "TESTS_GATES: 3 passed\n"
        "ARTIFACTS: artifacts/governance/foo.json\n"
        "Implemented the fix."
    )


class TestStopTaskAudit:
    def test_plain_prose_allowed(self) -> None:
        result = _run_stop({"response": "Thanks for the question — no repo work here."})
        assert result.returncode == _ALLOW

    def test_full_pass_proof_allowed(self) -> None:
        result = _run_stop({"response": _full_proof_response()})
        assert result.returncode == _ALLOW

    def test_pass_missing_artifacts_blocked(self) -> None:
        text = (
            "STATUS: PASS\n"
            "FILES_CHANGED: tests/foo.py\n"
            "COMMANDS_RUN: pytest tests/foo.py\n"
            "TESTS_GATES: 3 passed\n"
        )
        result = _run_stop({"response": text})
        assert result.returncode == _BLOCK
        assert "ARTIFACTS" in result.stdout

    def test_bare_pass_without_proof_blocked(self) -> None:
        result = _run_stop({"response": "STATUS: PASS — all done."})
        assert result.returncode == _BLOCK
        assert "proof sections" in result.stdout

    def test_repo_work_without_status_blocked(self) -> None:
        result = _run_stop(
            {"response": "FILES_CHANGED: apps_rg/foo.py\nCOMMANDS_RUN: pytest\nImplemented the patch."}
        )
        assert result.returncode == _BLOCK
        assert "missing STATUS" in result.stdout

    def test_speculative_pass_language_blocked(self) -> None:
        result = _run_stop({"response": "This SHOULD PASS once CI runs."})
        assert result.returncode == _BLOCK
        assert "Speculative pass language" in result.stdout

    def test_likely_pass_language_blocked(self) -> None:
        result = _run_stop({"response": "LIKELY PASS after the gate finishes."})
        assert result.returncode == _BLOCK

    def test_empty_payload_allowed(self) -> None:
        result = _run_stop({})
        assert result.returncode == _ALLOW
