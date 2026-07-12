from __future__ import annotations

from agentic_core.L6_observability.shadow_eval.longitudinal_patterns import (
    synthesize_longitudinal_patterns,
)


def _gap(run_id: str) -> dict[str, object]:
    return {
        "run_id": run_id,
        "observed_at": f"2026-07-{run_id[-1]}T00:00:00Z",
        "app_id": "apps_rg",
        "lane_id": "headline",
        "microstep_id": "headline.X2.gates.pass",
        "failure_mode": "quality.gate_failure",
        "artifact_role": "lane_x2_gate_outputs",
        "policy_version": "v1",
        "shadow_classification": "QUALITY_GAP",
        "observed_status": "DRIFT",
    }


def test_same_run_duplicates_do_not_create_longitudinal_pattern() -> None:
    result = synthesize_longitudinal_patterns([_gap("run-1"), _gap("run-1")])
    assert result["pattern_count"] == 0
    assert result["proposal_count"] == 0


def test_distinct_completed_runs_create_inert_future_proposal() -> None:
    result = synthesize_longitudinal_patterns([_gap("run-1"), _gap("run-2")])
    assert result["pattern_count"] == 1
    pattern = result["patterns"][0]
    assert pattern["distinct_run_count"] == 2
    proposal = result["proposals"][0]
    assert proposal["requires_gauntlet"] is True
    assert proposal["uwg_required_for_activation"] is True
    assert proposal["current_run_effect"] == "none"
    assert proposal["future_run_only"] is True
