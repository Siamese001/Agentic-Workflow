"""Mandatory ADG JSON review template."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from tools.generate.core.helpers import _write_text_artifact
from tools.reports.adg_review_template import (
    build_review_template,
    emit_mandatory_adg_review_template,
    render_inline_review_template,
    validate_review_template,
)
from tools.reports.adg_decision_synthesis import artifact_consistency_status


def _write_gate_results(path: Path) -> None:
    _write_text_artifact(
        path,
        json.dumps(
            {
                "timestamp": "2026-06-13T17:29:49+00:00",
                "overall_exit_code": 0,
                "summary": {
                    "block_pass": 1,
                    "block_fail": 0,
                    "ratchet_pass": 3,
                    "ratchet_regressed": 0,
                    "warn": 0,
                },
                "gates": [
                    {
                        "gate_id": "G_REACH_l0_reachability",
                        "band": "P0",
                        "enforcement": "ratchet",
                        "classification": "pass",
                        "violation_count": 2792,
                        "baseline_count": 2792,
                    },
                    {
                        "gate_id": "S2_uwg_bypass_ratchet",
                        "band": "P0",
                        "enforcement": "ratchet",
                        "classification": "pass",
                        "violation_count": 1583,
                        "baseline_count": 1583,
                    },
                    {
                        "gate_id": "L2_lpg_drift_ratchet",
                        "band": "P0",
                        "enforcement": "ratchet",
                        "classification": "pass",
                        "violation_count": 1,
                        "baseline_count": 1,
                    },
                    {
                        "gate_id": "1_critical_path_integrity",
                        "band": "P0",
                        "enforcement": "block",
                        "classification": "pass",
                        "violation_count": 0,
                    },
                    {
                        "gate_id": "3_write_sovereignty",
                        "band": "P0",
                        "enforcement": "block",
                        "classification": "pass",
                        "status": "warn",
                        "owner": "adg_gates",
                        "exit_code": 0,
                        "violation_count": 848,
                    },
                    {
                        "gate_id": "B2_layer_skip_ratchet",
                        "band": "P1",
                        "enforcement": "ratchet",
                        "classification": "pass",
                        "violation_count": 900,
                        "baseline_count": 900,
                    },
                ],
            }
        ),
    )


def _write_burndown(path: Path) -> None:
    _write_text_artifact(
        path,
        json.dumps(
            {
                "schema_version": "2.2",
                "p0_clean": False,
                "p1_no_ratchet": True,
                "summary": {
                    "P0": {
                        "label": "layer_violations",
                        "gross": 46,
                        "guardian": 41,
                        "net": 5,
                        "diff": 41,
                    },
                    "P1": {
                        "label": "anti_patterns_high",
                        "gross": 10,
                        "guardian": 6,
                        "net": 4,
                        "diff": 6,
                    }
                },
                "provenance": {"counting_mode": "violations_plus_exempted_edge_inference"},
            }
        ),
    )


def _write_action_queue(path: Path) -> None:
    _write_text_artifact(
        path,
        json.dumps(
            {
                "emit_status": "ok",
                "provenance": {"degraded": False},
                "actions": [
                    {
                        "rank": 1,
                        "verdict_cluster": "GRAPHDB",
                        "action_kind": "test_hotspot_gap",
                        "file_path": "apps_rg/runtime/sections/executive_summary_lane.py",
                        "ordering_reason": "mv_hotspot_coverage_risk_priority",
                        "signal": "Test hotspot gap from mv_hotspot_coverage_risk",
                    }
                ],
            }
        ),
    )


def _write_hotspot_sqlite(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
        con.execute(
            """
            CREATE TABLE mv_hotspot_coverage_risk (
                file TEXT,
                layer TEXT,
                priority_band TEXT,
                risk_band TEXT,
                coverage_band TEXT,
                criticality_score REAL,
                combined_risk_score REAL,
                fan_in INTEGER,
                fan_out INTEGER,
                violation_count INTEGER,
                coverage_pct REAL
            )
            """
        )
        con.executemany(
            "INSERT INTO mv_hotspot_coverage_risk VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    "apps_rg/runtime/sections/executive_summary_lane.py",
                    "L_APP",
                    "P1_URGENT",
                    "CRITICAL",
                    "ABSENT",
                    9.5,
                    8.2,
                    42,
                    11,
                    3,
                    -1.0,
                ),
                (
                    "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
                    "L5",
                    "P2_GAP",
                    "HIGH",
                    "LOW",
                    7.0,
                    6.5,
                    21,
                    8,
                    1,
                    12.5,
                ),
            ],
        )
        con.commit()
    finally:
        con.close()


def test_inline_bypass_flag_is_declared_in_env_example() -> None:
    env_example = Path(".env.example").read_text(encoding="utf-8")

    assert "ADG_REVIEW_TEMPLATE_INLINE_BYPASS=" in env_example


def test_review_template_names_tracked_records_and_separates_guardian_math(tmp_path: Path) -> None:
    gate = tmp_path / "adg_gate_results_test.json"
    burndown = tmp_path / "adg_burndown_table.json"
    queue = tmp_path / "adg_action_queue_06132026_1324.json"
    _write_gate_results(gate)
    _write_burndown(burndown)
    _write_action_queue(queue)

    doc = build_review_template(
        gate_results_path=gate,
        burndown_path=burndown,
        action_queue_path=queue,
        run_id="06132026_1324",
    )

    p0 = doc["operator_summary"]["band_status"][0]
    assert p0["tracked_record_label"] == "4 gates / 5,224 tracked records"
    assert p0["ratchet_burn_down"] == "`G_REACH` 2,792; `S2_UWG` 1,583; `L2_LPG` 1"
    assert p0["cleanup_backlog"] == "`write_sovereignty` 848"
    assert p0["open_non_ratchet_work"] == "`write_sovereignty` 848"
    assert p0["read_it_as"] == "green; ratchet burn-down/open work remains"
    assert "guardian exemptions" in doc["terminology"]["not_counted_as"]
    assert "open_non_ratchet_work" in doc["terminology"]
    assert doc["severity_inventory"][0]["formula"] == "net = gross - guardian"
    assert doc["severity_inventory"][0]["net"] == 5
    assert doc["graphdb_mv_positioning"]["graphdb_actions_present"] is True
    assert [row["label"] for row in doc["p0_action_plan"]["rows"]] == [
        "G_REACH",
        "S2_UWG",
        "L2_LPG",
        "write_sovereignty",
    ]
    assert doc["p0_action_plan"]["rows"][0]["work_type"] == "Burn down ratchet"
    assert doc["p0_action_plan"]["rows"][0]["why_this_priority"].startswith("Largest P0 ratchet")
    assert doc["p0_action_plan"]["rows"][3]["work_type"] == "Open non-ratchet work"
    assert doc["p0_action_plan"]["comments"]
    assert "testing_hotspot_overlay" not in doc
    assert doc["priority_execution_plan"]["title"] == "Priority Execution Plan"
    assert doc["priority_execution_plan"]["rows"]
    synthesis = doc["decision_synthesis"]
    assert synthesis["band_counts"]["P0"]["ratchet_floor_records"] == 4376
    assert synthesis["band_counts"]["P0"]["open_non_ratchet_records"] == 848
    assert synthesis["band_counts"]["P0"]["clear_gates"] == 1
    assert synthesis["after_green_plan"]["rows"][0]["work"] == "burn_down_ratchet_floor"
    assert synthesis["artifact_consistency"]["status"] == "ok"
    assert "Testing Gap Risk" in doc["priority_execution_plan"]["rows"][0]["testing_mv_action"]
    attack_rows = doc["adg_attack_order"]["rows"]
    assert [row["work_class"] for row in attack_rows[:4]] == [
        "Burn down ratchets",
        "Burn down ratchets",
        "Open non-ratchet work",
        "Severity audit",
    ]
    assert attack_rows[0]["band"] == "P0"
    assert attack_rows[1]["band"] == "P1"
    assert attack_rows[2]["target"] == "`write_sovereignty` 848"
    assert "P-band outranks raw size" in attack_rows[0]["why_this_priority"]
    high_signal = doc["high_signal_review"]
    assert high_signal["headline"] == "Green for enforcement; burn-down work remains."
    assert any(
        "P0 open non-ratchet work is separate from P0 ratchets: `write_sovereignty` 848."
        in line
        for line in high_signal["what_this_means"]
    )
    assert (
        high_signal["p0_relationships"]["cleanup_relation_to_ratchets"]
        == "Separate open work. These records do not add to, subtract from, or change the ratchet-floor count."
    )
    assert high_signal["p0_relationships"]["non_ratchet_cleanup_records"] == 848
    assert high_signal["p0_relationships"]["open_non_ratchet_work_records"] == 848
    assert "checklist" not in doc["review_template"]
    assert validate_review_template(doc) == []

    broken = dict(doc)
    broken.pop("decision_synthesis")
    assert "missing top-level field: decision_synthesis" in validate_review_template(broken)


def test_artifact_consistency_reports_fail_open_and_fail_closed() -> None:
    refs = [
        {"artifact_key": "gate_results", "required": True, "exists": False},
        {"artifact_key": "burndown", "required": True, "exists": True},
        {"artifact_key": "action_queue", "required": False, "exists": True},
    ]

    fail_closed = artifact_consistency_status(required_artifacts=refs, fail_closed=True)
    fail_open = artifact_consistency_status(required_artifacts=refs, fail_closed=False)

    assert fail_closed["status"] == "fail_closed"
    assert fail_open["status"] == "fail_open"
    assert fail_closed["missing_required"] == ["gate_results"]
    assert fail_closed["required_count"] == 2
    assert fail_closed["present_required_count"] == 1
    assert fail_closed["optional_present_count"] == 1


def test_review_template_renders_executive_graphdb_testing_gap_brief(tmp_path: Path) -> None:
    gate = tmp_path / "adg_gate_results_test.json"
    burndown = tmp_path / "adg_burndown_table.json"
    queue = tmp_path / "adg_action_queue_06132026_1324.json"
    sqlite_path = tmp_path / "adg_indexed_test.sqlite"
    out = tmp_path / "adg_review_template_06132026_1324.json"
    _write_gate_results(gate)
    _write_burndown(burndown)
    _write_action_queue(queue)
    _write_hotspot_sqlite(sqlite_path)

    gate_doc = json.loads(gate.read_text(encoding="utf-8"))
    gate_doc["overall_exit_code"] = 1
    gate_doc["snapshot_path"] = str(sqlite_path)
    for gate_row in gate_doc["gates"]:
        if gate_row["gate_id"] == "B2_layer_skip_ratchet":
            gate_row["classification"] = "regressed"
            gate_row["violation_count"] = 901
            gate_row["baseline_count"] = 900
    gate.write_text(json.dumps(gate_doc), encoding="utf-8")

    doc = build_review_template(
        gate_results_path=gate,
        burndown_path=burndown,
        action_queue_path=queue,
        run_id="06132026_1324",
    )
    inline = render_inline_review_template(doc, output_path=out)

    assert validate_review_template(doc) == []
    assert doc["executive_decision_brief"]["decision"] == "Fund a narrow unblock-and-test slice now."
    testing = doc["graphdb_mv_analyst_summary"]["testing_gap_summary"]
    assert testing["status"] == "present"
    assert testing["counts"]["p1_urgent"] == 1
    assert testing["counts"]["coverage_absent"] == 1
    assert testing["top_files"][0]["file"] == "apps_rg/runtime/sections/executive_summary_lane.py"
    mv_inventory = doc["graphdb_mv_analyst_summary"]["mv_inventory"]
    hotspot = next(row for row in mv_inventory if row["mv_name"] == "mv_hotspot_coverage_risk")
    assert hotspot["routing_status"] == "action_driver"
    assert hotspot["priority"] == "next"
    assert "### BCG Review Brief" in inline
    assert "Maintain SVP engineer-level repo standards" in inline
    assert "### Executive Decision Brief" in inline
    assert "### Testing Gap Risk" in inline
    assert "Fund a narrow unblock-and-test slice now." in inline
    assert "### Priority Execution Plan" in inline
    assert doc["priority_execution_plan"]["rows"][0]["priority_work"].startswith("Fix P1 red gates first")
    assert "Testing implication" in inline
    assert "If this work touches a Testing Gap Risk file or caller" in inline
    assert "What to do:" not in inline
    assert "Do This Next" not in inline
    assert "`apps_rg/runtime/sections/executive_summary_lane.py`" in inline


def test_emit_mandatory_review_template_writes_timestamped_json_and_yaml(tmp_path: Path) -> None:
    gate = tmp_path / "adg_gate_results_test.json"
    burndown = tmp_path / "adg_burndown_table.json"
    queue = tmp_path / "adg_action_queue_06132026_1324.json"
    _write_gate_results(gate)
    _write_burndown(burndown)
    _write_action_queue(queue)

    rc, out = emit_mandatory_adg_review_template(
        adg_artifacts_dir=tmp_path,
        ts="06132026_1324",
        gate_results=gate,
        burndown=burndown,
        action_queue=queue,
        write_latest=False,
        print_inline=False,
        fail_closed=True,
    )

    assert rc == 0
    assert out == tmp_path / "adg_review_template_06132026_1324.json"
    yaml_out = tmp_path / "adg_review_template_06132026_1324.yaml"
    assert yaml_out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["artifact_kind"] == "adg_run_review_template"
    assert data["run_id"] == "06132026_1324"
    assert data["operator_summary"]["tracked_records"] == 6124
    yaml_text = yaml_out.read_text(encoding="utf-8")
    assert "high_signal_review:" in yaml_text
    assert "priority_execution_plan:" in yaml_text
    assert "Testing Gap Risk" in yaml_text
    assert "adg_attack_order:" in yaml_text
    assert "p0_action_plan:" in yaml_text
    assert "testing_hotspot_overlay:" not in yaml_text
    assert "checklist:" not in yaml_text
    assert "Largest P0 ratchet floor" in yaml_text


def test_inline_review_template_renders_chat_summary(tmp_path: Path) -> None:
    gate = tmp_path / "adg_gate_results_test.json"
    burndown = tmp_path / "adg_burndown_table.json"
    queue = tmp_path / "adg_action_queue_06132026_1324.json"
    out = tmp_path / "adg_review_template_06132026_1324.json"
    _write_gate_results(gate)
    _write_burndown(burndown)
    _write_action_queue(queue)

    doc = build_review_template(
        gate_results_path=gate,
        burndown_path=burndown,
        action_queue_path=queue,
        run_id="06132026_1324",
    )
    inline = render_inline_review_template(doc, output_path=out)

    assert "## ADG Review" in inline
    assert "adg_review_template_06132026_1324.json" in inline
    assert "adg_review_template_06132026_1324.yaml" in inline
    assert "### BCG Review Brief" in inline
    assert "### What This Means" in inline
    assert "P0 open non-ratchet work is separate from P0 ratchets: `write_sovereignty` 848." in inline
    assert "Do it after ratchets unless an item is tiny or high-leverage." in inline
    assert "### ADG Heuristic Attack Order" in inline
    assert "| 1 | Burn down ratchets: `G_REACH` 2,792; `S2_UWG` 1,583; `L2_LPG` 1 | P0 | 4,376 |" in inline
    assert "| 2 | Burn down ratchets: `B2_layer_skip` 900 | P1 | 900 |" in inline
    assert "| 3 | Open non-ratchet work: `write_sovereignty` 848 | P0 | 848 |" in inline
    assert "Non-exempt severity rows are included for review, but they do not populate Fix now unless a gate is failing." in inline
    assert "### P0 Action Plan" in inline
    assert "| # | Work | Gate | Records | Why this priority | Next step |" in inline
    assert "| 1 | Burn down ratchet | `G_REACH` | 2,792 | Largest P0 ratchet floor" in inline
    assert "| 2 | Burn down ratchet | `S2_UWG` | 1,583 | Next-largest P0 ratchet floor" in inline
    assert "| 3 | Burn down ratchet | `L2_LPG` | 1 | Small P0 ratchet" in inline
    assert "| 4 | Open non-ratchet work | `write_sovereignty` | 848 | Real open P0 work" in inline
    assert "Comments:" in inline
    assert "Open non-ratchet work is still real work; it is second because it does not lower the P0 ratchet floor." in inline
    assert "### Priority Execution Plan" in inline
    assert "`apps_rg/runtime/sections/executive_summary_lane.py`" in inline
    assert "### Testing Hotspot Overlay" not in inline
    assert "Do This Next" not in inline
    assert "Burn down P0 ratchet `G_REACH` (2,792)" in inline
    assert "Burn down P0 ratchet `S2_UWG` (1,583)" in inline
    assert "If this work touches a Testing Gap Risk file or caller" in inline
    assert "Close P0 open non-ratchet work `write_sovereignty` (848)" in inline
    assert "| Band | Fix now | 1) Burn down ratchets | 2) Open non-ratchet work | Work order |" in inline
    assert "### Exception Audit" in inline
    assert "| P0 | 46 | 41 | 5 |" in inline
    assert "### Ranked Queue" in inline
    assert "`apps_rg/runtime/sections/executive_summary_lane.py`" in inline
    assert "### Review Checklist" not in inline


def test_emit_mandatory_review_template_prints_inline_by_default(
    tmp_path: Path,
    capsys,
) -> None:
    gate = tmp_path / "adg_gate_results_test.json"
    burndown = tmp_path / "adg_burndown_table.json"
    queue = tmp_path / "adg_action_queue_06132026_1324.json"
    _write_gate_results(gate)
    _write_burndown(burndown)
    _write_action_queue(queue)

    rc, out = emit_mandatory_adg_review_template(
        adg_artifacts_dir=tmp_path,
        ts="06132026_1324",
        gate_results=gate,
        burndown=burndown,
        action_queue=queue,
        write_latest=False,
        fail_closed=True,
    )

    captured = capsys.readouterr()
    assert rc == 0
    assert out is not None and out.is_file()
    assert "## ADG Review" in captured.out
    assert "### BCG Review Brief" in captured.out
    assert "### What This Means" in captured.out
    assert "### Priority Execution Plan" in captured.out
    assert "Do This Next" not in captured.out
    assert "inline markdown emitted" in captured.err
