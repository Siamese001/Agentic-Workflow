from __future__ import annotations

from apps_eval.contracts import AppOutputSnapshot
from apps_eval.coverage import build_apps_rg_microstep_evaluation, load_apps_rg_contracts


def test_apps_rg_microstep_contract_expands_all_lane_rows() -> None:
    contracts = load_apps_rg_contracts()
    lanes = contracts["lane_contract"]["generated_lanes"]
    assert len(lanes) == 11

    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="scenario",
        x3_disposition="X3D_ALLOW_FINISH",
        output={"sections": {}},
    )
    evaluation = build_apps_rg_microstep_evaluation(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="run",
        created_at="1970-01-01T00:00:00Z",
        planned_eval_artifacts={
            "scorecard_rows": "scorecard_rows.jsonl",
            "component_scorecards": "apps_rg_component_scorecard.json",
            "coverage_matrix": "coverage_matrix.csv",
            "regression_summary": "regression.json",
        },
    )

    rows = [row.to_dict() for row in evaluation["rows"]]
    assert len(rows) == 136
    for lane in lanes:
        lane_rows = [row for row in rows if row["lane_id"] == lane]
        assert len(lane_rows) == 10
        assert {row["stage_id"] for row in lane_rows} == {"L2", "X2", "X1D", "X3", "L6"}
        assert {row["gate_id"] for row in lane_rows} >= {
            "x2_gates_pass",
            "x1d_judge_result_pass",
            "x3_disposition_earned",
            "l6_shadow_package_non_mutating",
        }

    coverage = evaluation["coverage_summary"].to_dict()
    assert coverage["release_blocked"] is True
    assert coverage["coverage_complete"] is False
    assert coverage["missing_required_artifacts"] > 0
    assert any(row["verdict"] == "FAIL" for row in rows)
    assert any(row["verdict"] == "NOT_RUN" for row in rows)


def test_apps_rg_microstep_rows_pass_when_required_lane_artifacts_resolve(tmp_path) -> None:
    lane_root = tmp_path / "lanes" / "headline"
    lane_root.mkdir(parents=True)
    (lane_root / "l2_output.json").write_text('{"runtime_generation_status":"REAL_LLM"}', encoding="utf-8")
    (lane_root / "runtime_payload.json").write_text('{"proof_pool_metadata":{}}', encoding="utf-8")
    (lane_root / "x2_gate_outputs.json").write_text('{"gates":[{"gate_id":"g","pass":true}]}', encoding="utf-8")
    (lane_root / "x1d_llm_judge_outputs.json").write_text(
        '{"judges":[{"provider_key":"gemini_pro","pass":true}]}',
        encoding="utf-8",
    )
    (lane_root / "x3_disposition.json").write_text('{"x3_code":"X3_ALLOW"}', encoding="utf-8")
    (lane_root / "l6_shadow_eval_package.json").write_text(
        '{"offline_only":true,"current_run_mutated":false}',
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
    headline_rows = [row for row in evaluation["rows"] if row.lane_id == "headline"]

    assert headline_rows
    assert all(row.verdict == "PASS" for row in headline_rows)


def test_apps_rg_microstep_consumes_trace_reconciliation_when_present(tmp_path) -> None:
    (tmp_path / "trace_reconciliation.json").write_text(
        '{"schema_version":"apps_rg.trace_reconciliation.v1","trace_verdict":"TRACE_UNAVAILABLE",'
        '"otel_snapshot_available":false,"summary":{"fail_count":0,"warn_count":2}}',
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

    rows = [row for row in evaluation["rows"] if row.artifact_role == "trace_reconciliation"]
    assert {row.gate_id for row in rows} == {
        "trace_reconciliation_present",
        "trace_reconciliation_consumed",
    }
    assert {row.verdict for row in rows} == {"PASS", "WARN"}
