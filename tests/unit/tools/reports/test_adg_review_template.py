"""Mandatory ADG JSON review template."""

from __future__ import annotations

import json
from pathlib import Path

from tools.generate.core.helpers import _write_text_artifact
from tools.reports.adg_review_template import (
    build_review_template,
    emit_mandatory_adg_review_template,
    render_inline_review_template,
    validate_review_template,
)


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
                    "ratchet_pass": 1,
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
    assert p0["tracked_record_label"] == "2 gates / 3,640 tracked records"
    assert p0["ratchet_burn_down"] == "`G_REACH` 2,792"
    assert p0["cleanup_backlog"] == "`write_sovereignty` 848"
    assert p0["open_non_ratchet_work"] == "`write_sovereignty` 848"
    assert p0["read_it_as"] == "green; ratchet burn-down/open work remains"
    assert "guardian exemptions" in doc["terminology"]["not_counted_as"]
    assert "open_non_ratchet_work" in doc["terminology"]
    assert doc["severity_inventory"][0]["formula"] == "net = gross - guardian"
    assert doc["severity_inventory"][0]["net"] == 5
    assert doc["graphdb_mv_positioning"]["graphdb_actions_present"] is True
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
    assert doc["review_template"]["checklist"]
    assert validate_review_template(doc) == []


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
    assert data["operator_summary"]["tracked_records"] == 3640
    yaml_text = yaml_out.read_text(encoding="utf-8")
    assert "high_signal_review:" in yaml_text
    assert "P0 open non-ratchet work is separate from P0 ratchets" in yaml_text


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
    assert "### What This Means" in inline
    assert "P0 open non-ratchet work is separate from P0 ratchets: `write_sovereignty` 848." in inline
    assert "Do it after ratchets unless an item is tiny or high-leverage." in inline
    assert "### Do This Next" in inline
    assert "1. Burn down P0 ratchets first: `G_REACH` 2,792." in inline
    assert "2. Close P0 open non-ratchet work after ratchets: `write_sovereignty` 848." in inline
    assert "| Band | Fix now | 1) Burn down ratchets | 2) Open non-ratchet work | Work order |" in inline
    assert "### Exception Audit" in inline
    assert "| P0 | 46 | 41 | 5 |" in inline
    assert "### Ranked Queue" in inline
    assert "`apps_rg/runtime/sections/executive_summary_lane.py`" in inline


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
    assert "### What This Means" in captured.out
    assert "### Do This Next" in captured.out
    assert "inline markdown emitted" in captured.err
