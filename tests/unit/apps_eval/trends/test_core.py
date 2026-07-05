from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_eval.trends import (
    build_trend_dashboard,
    emit_release_gate,
    emit_trend_dashboard,
    evaluate_release_gate,
    render_release_gate,
    render_trend_dashboard,
)


def _record_payload(
    *,
    record_id: str,
    created_at: str,
    score: float,
    scorecard_verdict: str = "pass",
    regression_verdict: str = "not_compared",
    suite_id: str = "apps_rg.dev.resume_generation",
    app_id: str = "apps_rg",
) -> dict[str, object]:
    return {
        "record_id": record_id,
        "created_at": created_at,
        "suite_id": suite_id,
        "app_id": app_id,
        "mode": "snapshot",
        "deterministic_only": False,
        "scenario_results": [],
        "scorecard": {
            "suite_id": suite_id,
            "app_id": app_id,
            "scenario_count": 1,
            "finding_count": 1,
            "passed_findings": 1 if scorecard_verdict == "pass" else 0,
            "failed_findings": 0 if scorecard_verdict == "pass" else 1,
            "block_failures": 0 if scorecard_verdict == "pass" else 1,
            "score": score,
            "verdict": scorecard_verdict,
            "dimension_scores": {},
            "failure_mode_counts": {},
            "failure_family_counts": {},
        },
        "regression": {
            "compared": regression_verdict != "not_compared",
            "baseline_path": "",
            "baseline_digest": "",
            "current_score": score,
            "baseline_score": 1.0,
            "delta": score - 1.0,
            "verdict": regression_verdict,
        },
        "artifact_paths": {
            "eval_record": f"{record_id}/eval_record.json",
        },
        "rubric_ids": ["rubric"],
        "record_seed": {},
        "run_metadata": {
            "project_name": "agentic-workflow",
            "project_version": "1.0.0",
            "git_commit": "deadbeef",
            "python_version": "3.12.0",
            "platform": "test",
            "cwd": "C:/Git/Agentic-Workflow-FRESH",
            "runner": "apps_eval.runner.core",
            "scorer_version": "apps_eval.graders.deterministic.v2",
            "record_seed_digest": f"digest-{record_id}",
            "baseline_digest": "",
            "mode": "snapshot",
            "deterministic_only": False,
            "with_judge": False,
            "compare_baseline": False,
        },
        "fixture_provenance": [],
        "regression_flywheel": {
            "schema_version": "apps_eval.regression_flywheel.v1",
            "compared": False,
            "baseline_path": "",
            "baseline_digest": "",
            "current_score": score,
            "baseline_score": 1.0,
            "delta": score - 1.0,
            "verdict": regression_verdict,
            "current_failure_mode_counts": {},
            "current_failure_family_counts": {},
            "baseline_failure_mode_counts": {},
            "baseline_failure_family_counts": {},
            "dominant_failure_mode": "",
            "dominant_failure_family": "",
            "new_failure_modes": [],
            "recovered_failure_modes": [],
            "repeated_failure_modes": [],
            "scenario_hotspots": [],
        },
        "schema_version": "apps_eval.completed_eval.v3",
    }


def _write_record(root: Path, *, record_id: str, payload: dict[str, object]) -> Path:
    path = root / record_id / "eval_record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_build_trend_dashboard_collects_history(tmp_path: Path) -> None:
    records_root = tmp_path / "runs"
    _write_record(
        records_root,
        record_id="a",
        payload=_record_payload(record_id="a", created_at="2026-06-17T00:00:00Z", score=1.0),
    )
    _write_record(
        records_root,
        record_id="b",
        payload=_record_payload(record_id="b", created_at="2026-06-17T00:01:00Z", score=0.9),
    )

    dashboard = build_trend_dashboard(
        records_root=records_root,
        app_id="apps_rg",
        split="dev",
        window_size=2,
        history_limit=10,
    )

    assert dashboard.sample_count == 2
    assert dashboard.suite_count == 1
    assert dashboard.latest_score == pytest.approx(0.9)
    assert dashboard.suite_summaries[0].sample_count == 2
    assert dashboard.suite_summaries[0].score_delta == pytest.approx(-0.1)
    assert dashboard.suite_summaries[0].trend_direction == "degrading"
    assert dashboard.artifact_paths == {}

    markdown = render_trend_dashboard(dashboard)
    assert "## Suite Trends" in markdown
    assert "## Diagnostic Observations" in markdown
    assert "## Recent Samples" in markdown


def test_trend_dashboard_reads_diagnostic_summary_without_blocking_release(tmp_path: Path) -> None:
    records_root = tmp_path / "runs"
    payload = _record_payload(record_id="a", created_at="2026-06-17T00:00:00Z", score=1.0)
    payload["artifact_paths"]["diagnostic_summary"] = "diagnostic_summary.json"
    record_path = _write_record(records_root, record_id="a", payload=payload)
    (record_path.parent / "diagnostic_summary.json").write_text(
        json.dumps(
            {
                "suite_id": "apps_rg.dev.resume_generation",
                "app_id": "apps_rg",
                "run_id": "a",
                "observation_count": 3,
                "family_counts": {"x1d_judge_calibration": 2, "l6_shadow_non_mutation": 1},
                "verdict_counts": {"WARN": 1, "NOT_OBSERVED": 2},
                "promotion_state_counts": {"shadow": 3},
                "authority": "post_run_l6_shadow_only",
                "current_run_mutated": False,
                "future_run_only": True,
                "schema_version": "apps_eval.diagnostic_summary.v1",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    dashboard = build_trend_dashboard(records_root=records_root, app_id="apps_rg", split="dev")
    decision = evaluate_release_gate(dashboard, min_samples=1)
    blocked = evaluate_release_gate(dashboard, min_samples=1, min_diagnostic_observations=4)

    assert dashboard.diagnostic_observation_count == 3
    assert dashboard.diagnostic_family_counts["x1d_judge_calibration"] == 2
    assert dashboard.diagnostic_verdict_counts["NOT_OBSERVED"] == 2
    assert dashboard.diagnostic_not_observed_rate == pytest.approx(2 / 3)
    assert decision.status == "pass"
    assert blocked.status == "blocked"
    assert any("diagnostic observation count" in reason for reason in blocked.reasons)


def test_release_gate_distinguishes_blocked_and_regression(tmp_path: Path) -> None:
    blocked_root = tmp_path / "blocked"
    _write_record(
        blocked_root,
        record_id="a",
        payload=_record_payload(record_id="a", created_at="2026-06-17T00:00:00Z", score=1.0),
    )
    _write_record(
        blocked_root,
        record_id="b",
        payload=_record_payload(
            record_id="b",
            created_at="2026-06-17T00:01:00Z",
            score=0.98,
            scorecard_verdict="fail",
        ),
    )
    blocked_dashboard = build_trend_dashboard(records_root=blocked_root, app_id="apps_rg", split="dev")
    blocked_decision = evaluate_release_gate(blocked_dashboard)
    assert blocked_decision.status == "blocked"
    assert blocked_decision.blocking_suite_ids == ["apps_rg.dev.resume_generation"]
    assert any("latest scorecard verdict" in reason for reason in blocked_decision.reasons)
    assert "## Suite Checks" in render_release_gate(blocked_decision)

    regression_root = tmp_path / "regression"
    _write_record(
        regression_root,
        record_id="a",
        payload=_record_payload(record_id="a", created_at="2026-06-17T00:00:00Z", score=1.0),
    )
    _write_record(
        regression_root,
        record_id="b",
        payload=_record_payload(
            record_id="b",
            created_at="2026-06-17T00:01:00Z",
            score=0.8,
            scorecard_verdict="pass",
            regression_verdict="regression",
        ),
    )
    regression_dashboard = build_trend_dashboard(records_root=regression_root, app_id="apps_rg", split="dev")
    regression_decision = evaluate_release_gate(regression_dashboard)
    assert regression_decision.status == "regression"
    assert regression_decision.blocking_suite_ids == ["apps_rg.dev.resume_generation"]
    assert any("latest regression verdict" in reason for reason in regression_decision.reasons)


def test_trend_dashboard_can_emit_l6_shadow_bridge(tmp_path: Path) -> None:
    records_root = tmp_path / "trend_bridge"
    _write_record(
        records_root,
        record_id="a",
        payload=_record_payload(record_id="a", created_at="2026-06-17T00:00:00Z", score=1.0),
    )
    _write_record(
        records_root,
        record_id="b",
        payload=_record_payload(record_id="b", created_at="2026-06-17T00:01:00Z", score=0.98),
    )

    dashboard = emit_trend_dashboard(
        records_root=records_root,
        app_id="apps_rg",
        split="dev",
        out_dir=tmp_path / "trends",
        emit_l6_shadow=True,
    )

    bridge_path = Path(dashboard.artifact_paths["l6_shadow_bridge"])
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))

    assert dashboard.latest_score == pytest.approx(0.98)
    assert bridge["schema_version"] == "apps_eval.driver_l6_shadow_bridge.v1"
    assert bridge["eval_id"] == dashboard.trend_id
    assert bridge["scorecard_count"] == dashboard.suite_count
    assert bridge["requested_action"] == "consume_completed_eval_artifacts_only"
    assert bridge["current_run_mutated"] is False
    assert bridge["direct_l4_write_attempted"] is False
    assert bridge["durable_write_attempted"] is False
    assert bridge["future_run_only"] is True
    assert bridge["output_refs"]["trend_dashboard"] == dashboard.artifact_paths["trend_dashboard"]
    assert bridge["output_refs"]["trend_dashboard_report"] == dashboard.artifact_paths["trend_dashboard_report"]


def test_trend_dashboard_does_not_emit_l6_shadow_bridge_by_default(tmp_path: Path) -> None:
    records_root = tmp_path / "trend_no_bridge"
    _write_record(
        records_root,
        record_id="a",
        payload=_record_payload(record_id="a", created_at="2026-06-17T00:00:00Z", score=1.0),
    )
    _write_record(
        records_root,
        record_id="b",
        payload=_record_payload(record_id="b", created_at="2026-06-17T00:01:00Z", score=0.98),
    )

    dashboard = emit_trend_dashboard(
        records_root=records_root,
        app_id="apps_rg",
        split="dev",
        out_dir=tmp_path / "trends",
    )

    assert "l6_shadow_bridge" not in dashboard.artifact_paths
    assert not list((Path(tmp_path / "trends") / dashboard.trend_id).glob("l6_shadow_bridge.json"))


def test_release_gate_can_emit_l6_shadow_bridge(tmp_path: Path) -> None:
    records_root = tmp_path / "bridge"
    _write_record(
        records_root,
        record_id="a",
        payload=_record_payload(record_id="a", created_at="2026-06-17T00:00:00Z", score=1.0),
    )
    _write_record(
        records_root,
        record_id="b",
        payload=_record_payload(record_id="b", created_at="2026-06-17T00:01:00Z", score=0.98),
    )

    decision = emit_release_gate(
        records_root=records_root,
        app_id="apps_rg",
        split="dev",
        out_dir=tmp_path / "trends",
        emit_l6_shadow=True,
    )

    bridge_path = Path(decision.artifact_paths["l6_shadow_bridge"])
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))

    assert decision.status == "pass"
    assert bridge["schema_version"] == "apps_eval.driver_l6_shadow_bridge.v1"
    assert bridge["eval_id"] == decision.gate_id
    assert bridge["scorecard_count"] == decision.suite_count
    assert bridge["requested_action"] == "consume_completed_eval_artifacts_only"
    assert bridge["current_run_mutated"] is False
    assert bridge["direct_l4_write_attempted"] is False
    assert bridge["durable_write_attempted"] is False
    assert bridge["future_run_only"] is True
    assert bridge["output_refs"]["trend_dashboard"] == decision.trend_dashboard_path
    assert bridge["output_refs"]["release_gate"] == decision.artifact_paths["release_gate"]


def test_release_gate_does_not_emit_l6_shadow_bridge_by_default(tmp_path: Path) -> None:
    records_root = tmp_path / "no_bridge"
    _write_record(
        records_root,
        record_id="a",
        payload=_record_payload(record_id="a", created_at="2026-06-17T00:00:00Z", score=1.0),
    )
    _write_record(
        records_root,
        record_id="b",
        payload=_record_payload(record_id="b", created_at="2026-06-17T00:01:00Z", score=0.9),
    )

    decision = emit_release_gate(
        records_root=records_root,
        app_id="apps_rg",
        split="dev",
        out_dir=tmp_path / "trends",
    )

    assert "l6_shadow_bridge" not in decision.artifact_paths
    assert not list((Path(tmp_path / "trends") / decision.trend_id).glob("l6_shadow_bridge.json"))
