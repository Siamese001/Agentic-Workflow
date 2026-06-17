from __future__ import annotations

import json
import time
from pathlib import Path

from apps_eval.__main__ import main
from apps_eval.contracts import EvalRequest
from apps_eval.runner.core import run_eval


def _seed_history(root: Path, count: int = 3) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for _ in range(count):
        record = run_eval(
            EvalRequest(
                suite_id="apps_rg.dev.resume_generation",
                mode="snapshot",
                deterministic_only=False,
                out_dir=str(root),
            )
        )
        records.append(
            {
                "record_id": record.record_id,
                "path": Path(record.artifact_paths["eval_record"]),
            }
        )
        time.sleep(0.01)
    return records


def _mutate_record(path: Path, *, scorecard_verdict: str, regression_verdict: str, score: float) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["scorecard"]["verdict"] = scorecard_verdict
    payload["scorecard"]["score"] = score
    payload["scorecard"]["passed_findings"] = 1 if scorecard_verdict == "pass" else 0
    payload["scorecard"]["failed_findings"] = 0 if scorecard_verdict == "pass" else 1
    payload["scorecard"]["block_failures"] = 0 if scorecard_verdict == "pass" else 1
    payload["regression"]["verdict"] = regression_verdict
    payload["regression"]["current_score"] = score
    payload["regression"]["delta"] = score - payload["regression"]["baseline_score"]
    payload["regression_flywheel"]["verdict"] = regression_verdict
    payload["regression_flywheel"]["current_score"] = score
    payload["regression_flywheel"]["delta"] = score - payload["regression_flywheel"]["baseline_score"]
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_cli_trend_dashboard_and_release_gate_pass(tmp_path: Path) -> None:
    records_root = tmp_path / "records"
    _seed_history(records_root)
    trends_root = tmp_path / "trends"

    dashboard_exit = main(
        [
            "trend-dashboard",
            "--records-root",
            str(records_root),
            "--app",
            "apps_rg",
            "--split",
            "dev",
            "--out-dir",
            str(trends_root),
        ]
    )
    assert dashboard_exit == 0

    dashboard_files = list(trends_root.rglob("trend_dashboard.json"))
    assert dashboard_files
    dashboard_payload = json.loads(dashboard_files[0].read_text(encoding="utf-8"))
    assert dashboard_payload["sample_count"] == 3
    assert dashboard_payload["suite_count"] == 1
    assert dashboard_payload["latest_scorecard_verdict"] == "pass"


def test_cli_trend_dashboard_can_emit_l6_shadow_bridge(tmp_path: Path) -> None:
    records_root = tmp_path / "records"
    _seed_history(records_root)
    trends_root = tmp_path / "trend_trends"

    dashboard_exit = main(
        [
            "trend-dashboard",
            "--records-root",
            str(records_root),
            "--app",
            "apps_rg",
            "--split",
            "dev",
            "--out-dir",
            str(trends_root),
            "--emit-l6-shadow",
        ]
    )
    assert dashboard_exit == 0

    dashboard_files = list(trends_root.rglob("trend_dashboard.json"))
    assert dashboard_files
    dashboard_payload = json.loads(dashboard_files[0].read_text(encoding="utf-8"))
    assert "l6_shadow_bridge" in dashboard_payload["artifact_paths"]

    bridge_path = Path(dashboard_payload["artifact_paths"]["l6_shadow_bridge"])
    assert bridge_path.is_file()
    bridge_payload = json.loads(bridge_path.read_text(encoding="utf-8"))
    assert bridge_payload["schema_version"] == "apps_eval.driver_l6_shadow_bridge.v1"
    assert bridge_payload["eval_id"] == dashboard_payload["trend_id"]
    assert bridge_payload["requested_action"] == "consume_completed_eval_artifacts_only"
    assert bridge_payload["current_run_mutated"] is False
    assert bridge_payload["future_run_only"] is True

    gate_exit = main(
        [
            "release-gate",
            "--records-root",
            str(records_root),
            "--app",
            "apps_rg",
            "--split",
            "dev",
            "--out-dir",
            str(trends_root),
            "--emit-l6-shadow",
        ]
    )
    assert gate_exit == 0

    gate_files = list(trends_root.rglob("release_gate.json"))
    assert gate_files
    gate_payload = json.loads(gate_files[0].read_text(encoding="utf-8"))
    assert gate_payload["status"] == "pass"
    assert gate_payload["blocking_suite_ids"] == []
    assert "l6_shadow_bridge" in gate_payload["artifact_paths"]

    bridge_path = Path(gate_payload["artifact_paths"]["l6_shadow_bridge"])
    assert bridge_path.is_file()
    bridge_payload = json.loads(bridge_path.read_text(encoding="utf-8"))
    assert bridge_payload["schema_version"] == "apps_eval.driver_l6_shadow_bridge.v1"
    assert bridge_payload["requested_action"] == "consume_completed_eval_artifacts_only"
    assert bridge_payload["current_run_mutated"] is False
    assert bridge_payload["future_run_only"] is True


def test_cli_release_gate_distinguishes_blocked_and_regression(tmp_path: Path) -> None:
    blocked_records_root = tmp_path / "blocked_records"
    blocked_records = _seed_history(blocked_records_root)
    _mutate_record(
        blocked_records[-1]["path"],
        scorecard_verdict="fail",
        regression_verdict="not_compared",
        score=0.98,
    )
    blocked_exit = main(
        [
            "release-gate",
            "--records-root",
            str(blocked_records_root),
            "--app",
            "apps_rg",
            "--split",
            "dev",
            "--out-dir",
            str(tmp_path / "blocked_trends"),
        ]
    )
    assert blocked_exit == 1
    blocked_gate_files = list((tmp_path / "blocked_trends").rglob("release_gate.json"))
    assert blocked_gate_files
    blocked_payload = json.loads(blocked_gate_files[0].read_text(encoding="utf-8"))
    assert blocked_payload["status"] == "blocked"
    assert any("latest scorecard verdict" in reason for reason in blocked_payload["reasons"])

    regression_records_root = tmp_path / "regression_records"
    regression_records = _seed_history(regression_records_root)
    _mutate_record(
        regression_records[-1]["path"],
        scorecard_verdict="pass",
        regression_verdict="regression",
        score=0.8,
    )
    regression_exit = main(
        [
            "release-gate",
            "--records-root",
            str(regression_records_root),
            "--app",
            "apps_rg",
            "--split",
            "dev",
            "--out-dir",
            str(tmp_path / "regression_trends"),
        ]
    )
    assert regression_exit == 2
    regression_gate_files = list((tmp_path / "regression_trends").rglob("release_gate.json"))
    assert regression_gate_files
    regression_payload = json.loads(regression_gate_files[0].read_text(encoding="utf-8"))
    assert regression_payload["status"] == "regression"
    assert any("latest regression verdict" in reason for reason in regression_payload["reasons"])
