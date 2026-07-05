from __future__ import annotations

from pathlib import Path

from apps_eval.contracts import AppOutputSnapshot
from apps_eval.coverage import build_apps_rg_microstep_evaluation


def _row_by_gate(rows, gate_id: str):
    return next(row for row in rows if row.gate_id == gate_id)


def test_required_semantic_gate_does_not_pass_on_artifact_presence(tmp_path: Path) -> None:
    (tmp_path / "l1_plan_contract.json").write_text("{}", encoding="utf-8")
    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="scenario",
        x3_disposition="X3D_ALLOW_FINISH",
        output={"sections": {}},
        run_root=str(tmp_path),
    )

    evaluation = build_apps_rg_microstep_evaluation(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="run",
        created_at="1970-01-01T00:00:00Z",
    )

    row = _row_by_gate(evaluation["rows"], "l1_static_plan_profile_schema_bound")
    assert row.artifact_ref
    assert row.verdict == "FAIL"
    assert row.failure_mode == "microstep.l1_static_plan_profile_schema_bound"
    assert row.observed_value["schema_version"] is None
    assert row.threshold == "schema version or schema_bound true"


def test_semantic_gate_passes_when_required_fields_are_present(tmp_path: Path) -> None:
    (tmp_path / "l1_plan_contract.json").write_text(
        '{"schema_version":"apps_rg.l1_static_plan_profile.v1"}',
        encoding="utf-8",
    )
    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="scenario",
        x3_disposition="X3D_ALLOW_FINISH",
        output={"sections": {}},
        run_root=str(tmp_path),
    )

    evaluation = build_apps_rg_microstep_evaluation(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="run",
        created_at="1970-01-01T00:00:00Z",
    )

    row = _row_by_gate(evaluation["rows"], "l1_static_plan_profile_schema_bound")
    assert row.verdict == "PASS"


def test_cross_section_graph_coherence_materiality_requires_semantic_evidence(tmp_path: Path) -> None:
    (tmp_path / "cross_section_x2_gate_outputs.json").write_text("{}", encoding="utf-8")
    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="scenario",
        x3_disposition="X3D_ALLOW_FINISH",
        output={"sections": {}},
        run_root=str(tmp_path),
    )

    evaluation = build_apps_rg_microstep_evaluation(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="run",
        created_at="1970-01-01T00:00:00Z",
    )

    row = _row_by_gate(evaluation["rows"], "x2_cross_section_graph_coherence_materiality")
    assert row.artifact_ref
    assert row.verdict == "FAIL"
    assert row.observed_value["support_count"] == 0

