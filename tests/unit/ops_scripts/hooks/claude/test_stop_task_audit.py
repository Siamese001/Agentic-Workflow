"""Tests for the live Stop hook ``stop_task_audit.py``.

Commit f96f7a3735 flipped advisory warns to hard blocks and added ARTIFACTS to
PROOF_WORDS — these cases guard that contract.
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
HOOK = HOOKS_DIR / "stop_task_audit.py"


def _run_stop(payload: dict) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(HOOKS_DIR)}
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )


_FULL_PASS = (
    "STATUS: PASS\n"
    "FILES_CHANGED:\n- [foo.py](foo.py)\n"
    "COMMANDS_RUN:\n- python -m pytest -> exit 0\n"
    "TESTS_GATES:\n- pytest 6 passed\n"
    "ARTIFACTS:\n- [receipt.json](artifacts/receipt.json)\n"
)


class TestStopTaskAudit:
    def test_allow_empty_payload(self) -> None:
        proc = _run_stop({})
        assert proc.returncode == 0

    def test_allow_plain_prose_without_repo_work_cues(self) -> None:
        proc = _run_stop({"response": "Here is a short answer with no repo-work markers."})
        assert proc.returncode == 0

    def test_allow_full_pass_with_all_proof_sections(self) -> None:
        proc = _run_stop({"response": _FULL_PASS})
        assert proc.returncode == 0

    def test_block_pass_missing_artifacts(self) -> None:
        text = (
            "STATUS: PASS\n"
            "FILES_CHANGED:\n- [foo.py](foo.py)\n"
            "COMMANDS_RUN:\n- pytest -> exit 0\n"
            "TESTS_GATES:\n- pytest 3 passed\n"
        )
        proc = _run_stop({"response": text})
        assert proc.returncode == 2
        assert "ARTIFACTS" in proc.stdout

    def test_block_repo_work_without_status(self) -> None:
        text = "FILES_CHANGED:\n- [foo.py](foo.py)\nImplemented the fix."
        proc = _run_stop({"response": text})
        assert proc.returncode == 2
        assert "STATUS" in proc.stdout

    def test_block_speculative_pass_language(self) -> None:
        proc = _run_stop({"response": "This SHOULD PASS once CI is green."})
        assert proc.returncode == 2
        assert "Speculative" in proc.stdout

    def test_block_likely_pass_language(self) -> None:
        proc = _run_stop({"response": "LIKELY PASS after the next retry."})
        assert proc.returncode == 2
