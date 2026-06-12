"""W1 / G4 regression: integrated whole-run exit code must not mask failure as success.

Plan: apps-rg-e2e-gap-remediation-7e2d9c (W1 — fail-loud / exit codes).

The masking bug: the whole-run failure path delegated its process exit code to
``exit_code_for_executive_summary_artifact``. For an ``X3_BLOCK`` exec-summary artifact with
no temperature fault / token-budget receipt / judge soft-fail, that helper returns
``EXIT_SUCCESS`` — so an all-lanes-blocked run (AIG + Brown) exited 0 despite producing no
resume. ``exit_code_from_whole_run_result`` fixes this: success requires
``exit_status == "success"`` AND ``outcome_authorized``; every other state is non-zero.

Runs in product mode (no APPS_RG_TEST_HARNESS); imports only the pure exit-code helper.
"""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.cli_exit_codes import (
    EXIT_GENERIC_FAILURE,
    EXIT_JUDGE_REVIEW_REQUIRED,
    EXIT_SUCCESS,
    EXIT_TOKEN_BUDGET_BLOCKED,
    exit_code_from_whole_run_result,
)


def _write_exec_summary_artifact(root: Path, x3_code: str) -> str:
    """Create a whole-run artifact_dir with an exec-summary lane disposition; return its str path."""
    es_dir = root / "lanes" / "executive_summary"
    es_dir.mkdir(parents=True, exist_ok=True)
    (es_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": x3_code}), encoding="utf-8"
    )
    return str(root)


def test_all_lanes_blocked_whole_run_is_nonzero(tmp_path: Path) -> None:
    """The frozen AIG/Brown signature: every lane X3_BLOCK, status error -> must NOT be 0."""
    artifact_dir = _write_exec_summary_artifact(tmp_path, "X3_BLOCK")
    result = {
        "exit_status": "error",
        "outcome_authorized": False,
        "artifact_dir": artifact_dir,
        "x3_disposition": "X3_BLOCK",
    }
    rc = exit_code_from_whole_run_result(result)
    assert rc != EXIT_SUCCESS, "all-lanes-blocked whole run must not exit 0 (G4)"
    assert rc == EXIT_GENERIC_FAILURE


def test_success_authorized_is_zero() -> None:
    result = {"exit_status": "success", "outcome_authorized": True}
    assert exit_code_from_whole_run_result(result) == EXIT_SUCCESS


def test_success_but_unauthorized_is_nonzero() -> None:
    result = {"exit_status": "success", "outcome_authorized": False}
    assert exit_code_from_whole_run_result(result) == EXIT_GENERIC_FAILURE


def test_non_dict_result_is_generic_failure() -> None:
    assert exit_code_from_whole_run_result(None) == EXIT_GENERIC_FAILURE
    assert exit_code_from_whole_run_result("error") == EXIT_GENERIC_FAILURE


def test_token_budget_message_maps_to_blocked() -> None:
    result = {
        "exit_status": "error",
        "outcome_authorized": False,
        "token_budget_operator_message": "TOKEN_BUDGET_EXCEEDED_FIRST_PASS_95PCT",
    }
    assert exit_code_from_whole_run_result(result) == EXIT_TOKEN_BUDGET_BLOCKED


def test_exec_summary_soft_fail_artifact_refines_to_review(tmp_path: Path) -> None:
    """A genuine judge soft-fail on the exec-summary artifact still refines to code 4."""
    artifact_dir = _write_exec_summary_artifact(tmp_path, "X3_REVIEW_JUDGE_SOFT_FAIL")
    result = {
        "exit_status": "error",
        "outcome_authorized": False,
        "artifact_dir": artifact_dir,
    }
    assert exit_code_from_whole_run_result(result) == EXIT_JUDGE_REVIEW_REQUIRED


def test_judge_soft_fail_disposition_without_artifact(tmp_path: Path) -> None:
    result = {
        "exit_status": "error",
        "outcome_authorized": False,
        "x3_disposition": "X3_REVIEW_JUDGE_SOFT_FAIL",
    }
    assert exit_code_from_whole_run_result(result) == EXIT_JUDGE_REVIEW_REQUIRED
