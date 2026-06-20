"""Regression tests for ``stop_task_audit`` Stop-hook proof enforcement.

Incident (2026-06-11): ``stop_task_audit`` used advisory ``warn()`` for PASS-without-proof
violations, letting misleading PASS claims through. Hardened to ``block()`` (exit 2) and
``ARTIFACTS`` was added to ``PROOF_WORDS`` in ``claude_hook_common``.
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
SCRIPT = HOOKS_DIR / "stop_task_audit.py"


def _run_stop_audit(payload: dict) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["STOP_TASK_AUDIT_WORKTREE_HYGIENE_BYPASS"] = "1"
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(HOOKS_DIR),
        check=False,
        env=env,
    )


class TestStopTaskAudit:
    def test_empty_payload_allowed(self) -> None:
        result = _run_stop_audit({})
        assert result.returncode == 0

    def test_plain_prose_without_repo_work_cues_allowed(self) -> None:
        result = _run_stop_audit({"response": "Here is a short answer with no repo-work cues."})
        assert result.returncode == 0

    def test_full_pass_proof_allowed(self) -> None:
        text = (
            "STATUS: PASS\n"
            "FILES_CHANGED: apps_rg/foo.py\n"
            "COMMANDS_RUN: pytest tests/unit/foo.py\n"
            "TESTS_GATES: 12 passed\n"
            "ARTIFACTS: artifacts/governance/proof.json\n"
        )
        result = _run_stop_audit({"response": text})
        assert result.returncode == 0

    def test_pass_missing_artifacts_blocked(self) -> None:
        text = (
            "STATUS: PASS\n"
            "FILES_CHANGED: apps_rg/foo.py\n"
            "COMMANDS_RUN: pytest tests/unit/foo.py\n"
            "TESTS_GATES: 12 passed\n"
        )
        result = _run_stop_audit({"response": text})
        assert result.returncode == 2
        assert "ARTIFACTS" in result.stdout + result.stderr

    def test_bare_pass_without_proof_sections_blocked(self) -> None:
        result = _run_stop_audit({"response": "STATUS: PASS\nShipped the fix."})
        assert result.returncode == 2
        combined = result.stdout + result.stderr
        assert "proof sections" in combined.lower() or "ARTIFACTS" in combined

    def test_repo_work_without_status_blocked(self) -> None:
        text = (
            "IMPLEMENTED the lane fix.\n"
            "FILES_CHANGED: apps_rg/runtime/foo.py\n"
            "TESTS PASS on the scoped target.\n"
        )
        result = _run_stop_audit({"response": text})
        assert result.returncode == 2
        assert "STATUS" in result.stdout + result.stderr

    def test_speculative_pass_language_blocked(self) -> None:
        for phrase in ("SHOULD PASS", "LIKELY PASS"):
            result = _run_stop_audit(
                {
                    "response": (
                        "STATUS: PARTIAL\n"
                        "COMMANDS_RUN:\n- pytest -> in progress\n"
                        "ARTIFACTS:\n- NONE\n"
                        f"Verdict: {phrase} once wired."
                    )
                }
            )
            assert result.returncode == 2, phrase
            assert "Speculative" in result.stdout + result.stderr

    def test_partial_status_without_full_pass_proof_allowed(self) -> None:
        text = "STATUS: PARTIAL\nFILES_CHANGED: apps_rg/foo.py\nStill missing integration proof."
        result = _run_stop_audit({"response": text})
        assert result.returncode == 0
