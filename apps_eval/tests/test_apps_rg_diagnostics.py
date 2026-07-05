from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_eval.contracts import (
    AppOutputSnapshot,
    DiagnosticObservationV1,
    DiagnosticSourceArtifactRef,
    EvalRequest,
    ScorecardRow,
)
from apps_eval.diagnostics import build_apps_rg_diagnostics
from apps_eval.runner.core import run_eval


def _source() -> DiagnosticSourceArtifactRef:
    return DiagnosticSourceArtifactRef(
        artifact_role="fixture_snapshot",
        artifact_ref="snapshot.json",
        artifact_digest="abc123",
    )


def _scorecard_row(
    *,
    lane_id: str,
    stage_id: str,
    gate_id: str,
    artifact_role: str,
    artifact_ref: str,
    verdict: str = "PASS",
    failure_mode: str = "",
) -> ScorecardRow:
    return ScorecardRow(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        app_id="apps_rg",
        row_id=f"{lane_id}-{gate_id}",
        microstep_id=f"{lane_id}.{stage_id}.row",
        stage_id=stage_id,
        component_id="apps_rg.generated_lane",
        subcomponent_id=f"lane_{stage_id.lower()}",
        verdict=verdict,
        score=1.0 if verdict == "PASS" else 0.0,
        severity="BLOCK",
        run_id="run",
        lane_id=lane_id,
        gate_id=gate_id,
        artifact_role=artifact_role,
        artifact_ref=artifact_ref,
        evidence_ref=artifact_ref,
        evidence_digest=f"digest-{lane_id}-{gate_id}",
        failure_mode=failure_mode,
    )


def test_diagnostic_observation_rejects_missing_source_ref() -> None:
    with pytest.raises(ValueError, match="artifact_ref"):
        DiagnosticSourceArtifactRef(
            artifact_role="fixture_snapshot",
            artifact_ref="",
            artifact_digest="abc123",
        )


def test_diagnostic_observation_rejects_duplicate_overlap_and_blocking() -> None:
    kwargs = dict(
        diagnostic_id="diag",
        diagnostic_family="graph_traversal",
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        app_id="apps_rg",
        run_id="run",
        lane_id="",
        stage_id="C0",
        depends_on_microstep_id="C0.evidence_manifest.present",
        source_artifact_refs=[_source()],
        diagnostic_verdict="WARN",
    )
    with pytest.raises(ValueError, match="duplicate"):
        DiagnosticObservationV1(**kwargs, existing_row_overlap="duplicates")
    with pytest.raises(ValueError, match="blocking"):
        DiagnosticObservationV1(**kwargs, promotion_state="blocking")
    with pytest.raises(ValueError, match="authority"):
        DiagnosticObservationV1(**kwargs, authority="current_run_mutator")


def test_apps_rg_diagnostics_are_shadow_only_and_cover_requested_families(tmp_path: Path) -> None:
    graph = {
        "binding_metrics": {
            "sqlite_ranked_candidate_count": 4,
            "sqlite_selected_skill_count": 2,
            "rejected_sibling_skill_count": 1,
            "direct_support_count": 2,
            "adjacent_only_count": 0,
            "metric_bucket_counts": {"growth": 1},
            "skill_family_counts": {"platform": 1},
        },
        "rejection_receipts": [{"reason": "repeated_metric_penalty"}],
    }
    (tmp_path / "native_c03_final_evidence.json").write_text(json.dumps(graph), encoding="utf-8")
    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="scenario",
        x3_disposition="X3D_ALLOW_FINISH",
        output={"sections": {}},
        run_root=str(tmp_path),
        claims=[{"source_ids": ["fact-1"]}],
        artifacts=["generated_resume.json"],
        provenance={"resolved_inputs": {"manual_brief_ref": "brief.md"}, "evidence_refs": ["fact-1"]},
        raw_artifact_refs=["native_c03_final_evidence.json"],
    )

    diagnostics = build_apps_rg_diagnostics(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="run",
        scorecard_rows=[],
        snapshot_ref="snapshot.json",
        snapshot_digest="digest",
    )
    rows = diagnostics["rows"]
    families = {row.diagnostic_family for row in rows}

    assert families == {
        "briefing_to_graph",
        "e4_heal_opportunity",
        "graph_traversal",
        "l0_routing_cache",
        "l1_planning_rigor",
        "l2_failure_retry",
        "retrieval_quality",
        "x1d_judge_calibration",
    }
    assert all(row.authority == "post_run_l6_shadow_only" for row in rows)
    assert all(row.promotion_state == "shadow" for row in rows)
    assert all(row.source_artifact_refs[0].artifact_digest for row in rows)
    assert diagnostics["summary"].future_run_only is True


def test_apps_rg_diagnostics_emit_lane_scoped_x1d_rows(tmp_path: Path) -> None:
    good = tmp_path / "headline_x1d.json"
    bad = tmp_path / "skills_x1d.json"
    good.write_text('{"overall":"PASS"}', encoding="utf-8")
    bad.write_text('{"provider_unavailable":true}', encoding="utf-8")
    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="scenario",
        x3_disposition="X3D_ALLOW_FINISH",
        output={"sections": {}},
    )

    diagnostics = build_apps_rg_diagnostics(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="run",
        scorecard_rows=[
            _scorecard_row(
                lane_id="headline",
                stage_id="X1D",
                gate_id="x1d_judge_result_pass",
                artifact_role="lane_x1d_llm_judge_outputs",
                artifact_ref=good.as_posix(),
            ),
            _scorecard_row(
                lane_id="skills",
                stage_id="X1D",
                gate_id="x1d_judge_result_pass",
                artifact_role="lane_x1d_llm_judge_outputs",
                artifact_ref=bad.as_posix(),
                verdict="FAIL",
                failure_mode="microstep.x1d_judge_result_pass",
            ),
        ],
        snapshot_ref="snapshot.json",
        snapshot_digest="digest",
    )

    x1d_rows = [row for row in diagnostics["rows"] if row.diagnostic_family == "x1d_judge_calibration"]
    assert {row.lane_id for row in x1d_rows} == {"headline", "skills"}
    assert {row.observed_value["x1d_category"] for row in x1d_rows} == {
        "MODEL_BACKED_PASS",
        "PROVIDER_UNAVAILABLE",
    }
    assert diagnostics["summary"].lane_counts == {"headline": 5, "skills": 5}
    assert diagnostics["summary"].stage_counts["X1D"] == 2


def test_apps_rg_eval_emits_diagnostic_artifacts_without_changing_scorecard(tmp_path: Path) -> None:
    record = run_eval(
        EvalRequest(
            suite_id="apps_rg.dev.resume_generation",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(tmp_path),
        )
    )

    assert len(record.scorecard.scorecard_rows) == 134 * record.scorecard.scenario_count
    diagnostic_rows = Path(record.artifact_paths["diagnostic_rows"])
    diagnostic_summary = Path(record.artifact_paths["diagnostic_summary"])
    assert diagnostic_rows.is_file()
    assert diagnostic_summary.is_file()
    rows = [json.loads(line) for line in diagnostic_rows.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(diagnostic_summary.read_text(encoding="utf-8"))
    assert rows
    assert summary["authority"] == "post_run_l6_shadow_only"
    assert summary["current_run_mutated"] is False
    assert summary["future_run_only"] is True
    assert "stage_counts" in summary
    assert "lane_counts" in summary
