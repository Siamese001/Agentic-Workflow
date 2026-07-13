from __future__ import annotations

from pathlib import Path

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
    (lane_root / "x3_disposition.json").write_text(
        '{"x3_code":"X3D_ALLOW_FINISH"}',
        encoding="utf-8",
    )
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


def test_planned_eval_outputs_do_not_pass_presence_until_emitted(tmp_path: Path) -> None:
    eval_root = tmp_path / "eval"
    planned = {
        "__eval_artifact_root__": eval_root.as_posix(),
        "__emission_complete__": False,
        "scorecard_rows": (eval_root / "scorecard_rows.jsonl").as_posix(),
        "component_scorecards": (eval_root / "apps_rg_component_scorecard.json").as_posix(),
        "coverage_matrix": (eval_root / "coverage_matrix.csv").as_posix(),
        "regression_summary": (eval_root / "regression.json").as_posix(),
    }
    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="scenario",
        x3_disposition="X3D_ALLOW_FINISH",
        output={"sections": {}},
    )

    before = build_apps_rg_microstep_evaluation(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="eval-record",
        created_at="1970-01-01T00:00:00Z",
        planned_eval_artifacts=planned,
    )
    before_package = [
        row for row in before["rows"] if row.component_id == "apps_rg.eval_package"
    ]
    assert before_package
    assert all(row.artifact_ref == "" for row in before_package)
    assert all(row.verdict in {"FAIL", "NOT_RUN"} for row in before_package)

    eval_root.mkdir()
    (eval_root / "scorecard_rows.jsonl").write_text("{}\n", encoding="utf-8")
    (eval_root / "apps_rg_component_scorecard.json").write_text("{}", encoding="utf-8")
    (eval_root / "coverage_matrix.csv").write_text("row_id\n", encoding="utf-8")
    (eval_root / "regression.json").write_text("{}", encoding="utf-8")
    planned["__emission_complete__"] = True

    after = build_apps_rg_microstep_evaluation(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="eval-record",
        created_at="1970-01-01T00:00:00Z",
        planned_eval_artifacts=planned,
    )
    after_package = [
        row for row in after["rows"] if row.component_id == "apps_rg.eval_package"
    ]
    assert all(row.verdict == "PASS" for row in after_package)
    assert all(row.artifact_ref.startswith(eval_root.as_posix()) for row in after_package)
    assert all(row.evidence_digest for row in after_package)


def test_required_rows_persist_available_source_identity_and_digests() -> None:
    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="scenario",
        x3_disposition="X3D_ALLOW_FINISH",
        output={"sections": {}},
        parent_run_id="parent-run",
        child_run_id="child-run",
        section_attempt_id="attempt-1",
        runtime_exhaust_bundle_id="exhaust-1",
        snapshot_digest="snapshot-sha",
    )

    evaluation = build_apps_rg_microstep_evaluation(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="eval-record",
        created_at="1970-01-01T00:00:00Z",
    )
    required = [row for row in evaluation["rows"] if row.required]

    assert required
    assert {row.parent_run_id for row in required} == {"parent-run"}
    assert {row.child_run_id for row in required} == {"child-run"}
    assert {row.section_attempt_id for row in required} == {"attempt-1"}
    assert {row.eval_record_id for row in required} == {"eval-record"}
    assert {row.runtime_exhaust_bundle_id for row in required} == {"exhaust-1"}
    assert {row.snapshot_digest for row in required} == {"snapshot-sha"}
    assert all(row.microstep_contract_digest for row in required)
    assert all(row.registry_digest == row.microstep_contract_digest for row in required)


def test_x3_alias_and_noncanonical_exit_fail_closed(tmp_path: Path) -> None:
    lane_root = tmp_path / "lanes" / "headline"
    lane_root.mkdir(parents=True)
    (lane_root / "x3_disposition.json").write_text(
        '{"x3_code":"X3D"}',
        encoding="utf-8",
    )
    (tmp_path / "whole_run_exit_review_packet.json").write_text(
        '{"exactly_one_x3":true,"x3_disposition":"X3D"}',
        encoding="utf-8",
    )
    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="scenario",
        x3_disposition="X3D",
        output={"sections": {}},
        run_root=str(tmp_path),
    )

    evaluation = build_apps_rg_microstep_evaluation(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="eval-record",
        created_at="1970-01-01T00:00:00Z",
    )
    x3_row = next(row for row in evaluation["rows"] if row.gate_id == "x3_disposition_earned" and row.lane_id == "headline")
    exit_row = next(row for row in evaluation["rows"] if row.gate_id == "exit_exactly_one_x3")

    assert x3_row.verdict == "FAIL"
    assert exit_row.verdict == "FAIL"
    assert x3_row.threshold == "X3D_ALLOW_FINISH"
    assert exit_row.threshold == "X3D_ALLOW_FINISH"


def test_snapshot_registry_drift_fails_required_rows() -> None:
    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="scenario",
        x3_disposition="X3D_ALLOW_FINISH",
        output={"sections": {}},
        registry_digest="stale-registry-digest",
    )

    evaluation = build_apps_rg_microstep_evaluation(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="scenario",
        snapshot=snapshot,
        run_id="eval-record",
        created_at="1970-01-01T00:00:00Z",
    )
    required = [row for row in evaluation["rows"] if row.required]

    assert required
    assert required[0].verdict == "FAIL"
    assert required[0].failure_mode == "evidence.registry_digest_mismatch"
