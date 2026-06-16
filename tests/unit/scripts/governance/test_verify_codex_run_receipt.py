"""Tests for scripts/governance/verify_codex_run_receipt.py."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import verify_codex_run_receipt as mod  # noqa: E402


def _valid_receipt() -> dict:
    return {
        "schema_version": "codex-run-receipt/v1",
        "run_id": "run-001",
        "generated_at": "2026-06-16T12:00:00-04:00",
        "repo": {
            "root": "C:/Git/Agentic-Workflow-FRESH",
            "worktree": "C:/Git/Agentic-Workflow-FRESH-worktrees/codex-primary-execution",
            "branch": "codex/codex-primary-execution",
            "head": "abc123",
            "dirty_before": False,
            "dirty_after": True,
        },
        "scope": {
            "request": "implement Codex primary execution",
            "plan_id": "codex-primary-execution-7e4c2a",
            "files_changed": ["docs/codex-primary-execution.md"],
        },
        "execution": {
            "status": "PASS",
            "commands": [
                {
                    "command": "python scripts/governance/verify_codex_primary.py",
                    "cwd": "C:/Git/Agentic-Workflow-FRESH",
                    "exit_code": 0,
                    "status": "PASS",
                }
            ],
            "fallbacks": [],
        },
        "verification": {
            "checks": [
                {
                    "name": "primary verifier",
                    "status": "PASS",
                    "evidence": "Codex primary execution verification passed",
                }
            ]
        },
    }


def test_valid_receipt_passes() -> None:
    assert mod.validate_receipt(_valid_receipt()) == []


def test_failed_execution_requires_rca() -> None:
    receipt = _valid_receipt()
    receipt["execution"]["status"] = "FAIL"

    failures = mod.validate_receipt(receipt)

    assert "rca: required when execution fails or blocks" in failures


def test_failed_check_requires_complete_rca() -> None:
    receipt = _valid_receipt()
    receipt["verification"]["checks"][0]["status"] = "FAIL"
    receipt["rca"] = {
        "symptom": "Verifier failed.",
        "root_cause": "",
        "evidence": "exit 1",
        "fix_or_next": "Patch anchors.",
        "recurrence_guard": "Unit test.",
    }

    failures = mod.validate_receipt(receipt)

    assert "rca.root_cause: expected non-empty string" in failures


def test_fallback_rows_require_substitute() -> None:
    receipt = _valid_receipt()
    receipt["execution"]["fallbacks"] = [{"route": "adg_sqlite", "reason": "not callable"}]

    failures = mod.validate_receipt(receipt)

    assert "execution.fallbacks[0].substitute: expected non-empty string" in failures
