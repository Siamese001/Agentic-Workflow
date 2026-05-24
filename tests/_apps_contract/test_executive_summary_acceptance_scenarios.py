"""Acceptance scenarios: frozen L2 + judge scores → lane done policy (exit, regen, flags).

Guards against design drift where X2 PASS + soft-fail judges regress to exit 1 or
hide regen/rescore artifact semantics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from apps_rg.runtime.cli_section_execution_report import (
    build_section_cli_execution_report_payload,
    section_lane_process_exit_code,
)
from apps_rg.runtime.sections.executive_summary_lane_done_policy import (
    compute_executive_summary_lane_done_policy,
)
from tests._apps_contract.executive_summary_acceptance_fixtures import ACCEPTANCE_SCENARIOS


def _persist_scenario_artifacts(tmp_path: Path, scenario: dict[str, Any]) -> Path:
    sid = str(scenario["scenario_id"])
    rd = tmp_path / sid
    rd.mkdir()
    l2 = scenario["l2_output"]
    x3 = scenario["x3_disposition"]
    manifest = dict(scenario.get("manifest") or {})
    manifest.setdefault("section_id", "executive_summary")
    manifest.setdefault(
        "runtime_generation_status",
        l2.get("runtime_generation_status", "REAL_LLM"),
    )
    (rd / "l2_output.json").write_text(json.dumps(l2), encoding="utf-8")
    (rd / "x3_disposition.json").write_text(json.dumps(x3), encoding="utf-8")
    (rd / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (rd / "x1d_llm_judge_outputs.json").write_text(
        json.dumps({"judges": scenario["x1d_judges"]}),
        encoding="utf-8",
    )
    return rd


def _assert_lane_done_matches_written_done(scenario: dict[str, Any]) -> None:
    expected = scenario["expected"]
    policy = compute_executive_summary_lane_done_policy(
        l2_output=scenario["l2_output"],
        x3_disposition=scenario["x3_disposition"],
        x1d_judges=scenario["x1d_judges"],
        manifest=scenario.get("manifest"),
        judge_regen_enabled=True,
    )
    sid = scenario["scenario_id"]

    assert policy.draft_ready is expected["draft_ready"], sid
    assert policy.certified is expected["certified"], sid
    assert policy.process_exit_code == expected["process_exit_code"], sid
    assert policy.operator_status == expected["operator_status"], sid
    assert policy.disposition_tier == expected["disposition_tier"], sid
    assert policy.proof_eligible is expected["proof_eligible"], sid
    assert policy.judge_regen_triggered is expected["judge_regen_triggered"], sid
    assert policy.judge_regen_trigger_mode == expected.get("judge_regen_trigger_mode"), sid
    assert policy.judge_regen_skip_reason == expected.get("judge_regen_skip_reason"), sid
    assert policy.soft_judge_only_rescore_eligible is expected["soft_judge_only_rescore_eligible"], sid

    flags = policy.artifact_flags
    assert flags["runtime_generation_status"] == "REAL_LLM", sid
    assert flags["product_quality_status"] == "PASS", sid
    assert flags["x3_code"] == scenario["x3_disposition"]["x3_code"], sid
    assert flags["model_backed_pass_count"] == expected.get("model_backed_pass_count", 2 if "two_pass" in sid else 3), sid
    assert flags["soft_fail_count"] == (1 if "two_pass_one_soft" in sid else 0), sid
    assert flags["judge_regen_enabled"] is True, sid
    assert flags["post_x2_judge_refresh_rescore_only"] is False, sid


@pytest.mark.parametrize("scenario", ACCEPTANCE_SCENARIOS, ids=[s["scenario_id"] for s in ACCEPTANCE_SCENARIOS])
def test_acceptance_scenario_lane_done_policy(scenario: dict[str, Any]) -> None:
    _assert_lane_done_matches_written_done(scenario)


@pytest.mark.parametrize("scenario", ACCEPTANCE_SCENARIOS, ids=[s["scenario_id"] for s in ACCEPTANCE_SCENARIOS])
def test_acceptance_scenario_cli_exit_and_report_flags(
    tmp_path: Path,
    scenario: dict[str, Any],
) -> None:
    rd = _persist_scenario_artifacts(tmp_path, scenario)
    expected = scenario["expected"]
    sid = scenario["scenario_id"]

    result = {
        "exit_status": "error" if expected["process_exit_code"] else "success",
        "outcome_authorized": bool(scenario["x3_disposition"].get("pass")),
        "artifact_dir": str(rd),
        "fault": "",
    }
    exit_code = section_lane_process_exit_code(
        result=result,
        allow_non_allow_exit_zero_effective=False,
        section_id="executive_summary",
    )
    assert exit_code == expected["process_exit_code"], sid

    payload = build_section_cli_execution_report_payload(
        result=result,
        lane_provider_resolution_source=None,
        allow_non_allow_exit_zero_effective=False,
        process_exit_code=exit_code,
    )
    assert payload["operator_status"] == expected["operator_status"], sid
    assert payload["draft_ready"] is expected["draft_ready"], sid
    assert payload["certified"] is expected["certified"], sid
    assert payload["process_exit_code"] == expected["process_exit_code"], sid
    assert payload["expected_nonzero_exit"] is (expected["process_exit_code"] != 0), sid


def test_acceptance_regression_exit_one_on_x2_pass_soft_fail_only() -> None:
    """Anti-regression: shippable draft must not exit 1 when only judges soft-fail."""
    scenario = next(s for s in ACCEPTANCE_SCENARIOS if s["scenario_id"] == "two_pass_one_soft_shippable_draft")
    policy = compute_executive_summary_lane_done_policy(
        l2_output=scenario["l2_output"],
        x3_disposition=scenario["x3_disposition"],
        x1d_judges=scenario["x1d_judges"],
        manifest=scenario.get("manifest"),
    )
    assert policy.process_exit_code == 0
    assert policy.draft_ready is True
    assert policy.certified is False
