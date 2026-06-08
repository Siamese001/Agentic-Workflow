"""W0 unit tests for the apps_rg E2E run summarizer.

Hermetic: builds synthetic run dirs in ``tmp_path`` (the real RCA artifact tree is
git-ignored). Verifies the three-state classification that corrects the
``integrated_lane_evidence_status.json`` conflation (apps_rg AIG E2E remediation, E2E-05).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_tool():
    spec = importlib.util.spec_from_file_location(
        "summarize_e2e_run", REPO_ROOT / "tools" / "apps_rg" / "summarize_e2e_run.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


sumr = _load_tool()


def _write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


# --------------------------------------------------------------- classification


def test_classify_executed_x3_block():
    assert (
        sumr.classify_lane_state({"x3_disposition": "X3_BLOCK", "exit_status": "error"})
        == "EXECUTED_X3_BLOCK"
    )


def test_classify_executed_x3_allow():
    assert sumr.classify_lane_state({"x3_disposition": "X3_ALLOW"}) == "EXECUTED_X3_ALLOW"


def test_classify_pre_run_blocked_on_own_exception():
    dr = {"fault": "exception", "error": "'RustBindingsAPI' object has no attribute 'bindings'"}
    assert sumr.classify_lane_state(dr) == "PRE_RUN_BLOCKED"


def test_classify_missing_on_prior_abort():
    dr = {"prior_abort": "dispatch_exception:ibm_bullets:RustBindingsAPI", "exit_status": "error"}
    assert sumr.classify_lane_state(dr) == "MISSING_NOT_ATTEMPTED"


def test_x3_disposition_takes_precedence_over_error():
    # competencies: executed to X3_BLOCK AND carries exit_status=error -> EXECUTED wins.
    dr = {"x3_disposition": "X3_BLOCK", "exit_status": "error", "execution_status": "failed"}
    assert sumr.classify_lane_state(dr) == "EXECUTED_X3_BLOCK"


# --------------------------------------------------------------- full-run summary


def test_summarize_full_run_three_states(tmp_path):
    sections = tmp_path / "modular_r4" / "sections"
    _write(tmp_path / "integrated_lane_evidence_status.json", {"missing_lanes": []})
    _write(
        sections / "competencies" / "integrated_lane_pre_run_failure.json",
        {
            "status": "PRE_RUN_BLOCKED",
            "blocker": "LANE_DISPATCH_EXIT_ERROR",
            "dispatch_result": {"x3_disposition": "X3_BLOCK", "exit_status": "error", "run_id": "competencies_x"},
        },
    )
    _write(
        sections / "ibm_bullets" / "integrated_lane_pre_run_failure.json",
        {
            "status": "PRE_RUN_BLOCKED",
            "blocker": "exception",
            "dispatch_result": {"fault": "exception", "error": "'RustBindingsAPI' object has no attribute 'bindings'"},
        },
    )
    _write(
        sections / "ey_bullets" / "integrated_lane_pre_run_failure.json",
        {
            "status": "PRE_RUN_BLOCKED",
            "blocker": "LANE_DISPATCH_EXIT_ERROR",
            "dispatch_result": {"prior_abort": "dispatch_exception:ibm_bullets:RustBindingsAPI", "exit_status": "error"},
        },
    )

    summary = sumr.summarize(tmp_path)
    assert summary["mode"] == "full"
    states = {r["lane"]: r["state"] for r in summary["lanes"]}
    assert states["competencies"] == "EXECUTED_X3_BLOCK"
    assert states["ibm_bullets"] == "PRE_RUN_BLOCKED"
    assert states["ey_bullets"] == "MISSING_NOT_ATTEMPTED"
    # The three states are distinct (the bug being fixed collapsed them to one).
    assert len(set(states.values())) == 3

    md = sumr.render(summary)
    assert "EXECUTED_X3_BLOCK" in md
    assert "PRE_RUN_BLOCKED" in md
    assert "MISSING_NOT_ATTEMPTED" in md


# --------------------------------------------------------------- section summary


def test_summarize_section_run(tmp_path):
    d = tmp_path / "section_unify_bullets_external"
    d.mkdir()
    _write(
        d / "provider_response.json",
        {"provider_requested": "external_claude", "model": "claude-sonnet-4-6", "runtime_generation_status": "REAL_LLM"},
    )
    _write(
        d / "exit_disposition_receipt.json",
        {
            "section_id": "unify_bullets",
            "x3_code": "X3_BLOCK",
            "x3_disposition": {
                "x3_code": "X3_BLOCK",
                "x2_failed_gates": ["a", "b", "c"],
                "x1d_evaluator_mode": "MODEL_BACKED",
                "decisive_judge_failures": ["anthropic_claude"],
                "pass": False,
            },
        },
    )
    _write(
        d / "cli_section_execution_report.json",
        {"x3_code": "X3_BLOCK", "product_authorized": False, "x2_product_quality_status": "FAIL"},
    )

    summary = sumr.summarize(d)
    assert summary["mode"] == "section"
    rec = summary["lanes"][0]
    assert rec["lane"] == "unify_bullets"
    assert rec["provider"] == "external_claude"
    assert rec["model"] == "claude-sonnet-4-6"
    assert rec["runtime_generation_status"] == "REAL_LLM"
    assert rec["x2_failed"] == 3
    assert rec["x3"] == "X3_BLOCK"
    assert rec["authorized"] is False
    assert rec["state"] == "EXECUTED_X3_BLOCK"
