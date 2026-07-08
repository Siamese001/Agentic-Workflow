from __future__ import annotations

import json
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


def test_current_integrated_receipts_satisfy_global_semantic_gates(tmp_path: Path) -> None:
    receipts = {
        "l1_plan_contract.json": {
            "payload": {
                "route_id": "apps_rg.resume_generation_v1",
                "task_spec": "intake.user_chat",
                "query_spec": "user_query",
            }
        },
        "route_contract.json": {
            "payload": {
                "route_contract_id": "route-1",
                "route_id": "apps_rg.resume_generation_v1",
                "execution_form": "R4_SINGLE_ACTION",
            }
        },
        "c0_bypass_receipt.json": {
            "payload": {
                "c0_required": False,
                "c0_bypass_reason": "BYPASS_PRELOADED_CONTEXT",
                "deterministic_digest": "sha256:abc",
            }
        },
        "prompt_assembly_bypass_receipt.json": {
            "payload": {
                "prompt_assembly_required": False,
                "prompt_assembly_bypass_reason": "NO_MODEL_EXECUTION_REQUIRED",
                "deterministic_digest": "sha256:def",
            }
        },
    }
    for name, payload in receipts.items():
        (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")
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

    for gate_id in (
        "l1_static_plan_profile_schema_bound",
        "l0_dispatch_profile_canonical",
        "c0_evidence_materiality_present",
        "pa_prompt_boundary_evidence_as_data",
    ):
        assert _row_by_gate(evaluation["rows"], gate_id).verdict == "PASS"


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


def test_cross_section_graph_coherence_warn_with_material_support_passes_materiality(tmp_path: Path) -> None:
    (tmp_path / "cross_section_x2_gate_outputs.json").write_text(
        json.dumps(
            {
                "all_pass": True,
                "failed_gate_ids": [],
                "gates": [
                    {
                        "gate_id": "x2_cross_section_graph_coherence",
                        "verdict": "WARN",
                        "pass": False,
                        "observed": {
                            "status": "WARN",
                            "active_section_ids": ["headline", "executive_summary"],
                            "unique_graph_skill_node_ids": ["skill_a", "skill_b"],
                            "unique_role_episode_bundle_ids": ["reb_a"],
                        },
                    }
                ],
            }
        ),
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

    row = _row_by_gate(evaluation["rows"], "x2_cross_section_graph_coherence_materiality")
    assert row.verdict == "PASS"
    assert row.observed_value["support_count"] > 0

