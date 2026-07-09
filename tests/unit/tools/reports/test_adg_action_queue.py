"""W1.3 negative tests for ADG action queue (plan adg-action-dispatch-c9e4a2)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from tools.reports.adg_action_queue import (
    build_action_queue,
    extract_notion_fix_rows,
    validate_action_queue,
)
from tools.reports.gate_signal_catalog import display_verdict


def _gate(
    gate_id: str,
    *,
    band: str = "P0",
    enforcement: str = "block",
    classification: str = "blocked",
    violation_count: int = 1,
    baseline_count: int | None = None,
) -> dict:
    status = "fail" if classification == "blocked" else "pass"
    if classification == "regressed":
        status = "fail"
    return {
        "gate_id": gate_id,
        "band": band,
        "enforcement": enforcement,
        "classification": classification,
        "violation_count": violation_count,
        "baseline_count": baseline_count,
        "status": status,
    }


def _write_gate_results(path: Path, gates: list[dict], ts: str = "2026-05-25T12:00:00+00:00") -> None:
    path.write_text(
        json.dumps(
            {
                "timestamp": ts,
                "overall_exit_code": 1,
                "gates": gates,
            }
        ),
        encoding="utf-8",
    )


def _write_burndown(path: Path) -> None:
    path.write_text(
        json.dumps({"schema_version": "2.2", "summary": {"P0": {}}, "bands": {}}),
        encoding="utf-8",
    )


def _write_p0_wave_plan(path: Path, issue_kind: str = "l0_reachability_orphan") -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "plan_required": True,
                "top_files": [
                    {
                        "source_file": "agentic_core/L1_cognition/reachable.py",
                        "issue_count": 1,
                        "issue_kinds": [issue_kind],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_track_never_in_actions(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    _write_gate_results(
        gate,
        [
            _gate("10_infra_wiring", classification="blocked", violation_count=2),
            _gate(
                "G_REACH_l0_reachability",
                enforcement="ratchet",
                classification="pass",
                violation_count=2792,
                baseline_count=2792,
            ),
        ],
    )
    _write_burndown(burndown)
    doc = build_action_queue(gate_results_path=gate, burndown_path=burndown, max_actions=10)
    assert all(a.get("verdict_cluster") != "TRACK" for a in doc["actions"])
    blocker = doc["actions"][0]
    assert blocker["verdict_cluster"] == "FIX"
    assert blocker["impact_severity"] == "critical"
    assert blocker["enforcement_effect"] == "blocker"
    assert blocker["work_priority"] == "P0"
    assert blocker["queue_section"] == "open_blockers"
    assert display_verdict({"classification": "pass", "violation_count": 2792, "enforcement": "ratchet"}) == "TRACK"


def test_p0_wave_does_not_promote_ratchet_floor(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    p0_wave = tmp_path / "p0_wave.json"
    _write_gate_results(
        gate,
        [
            _gate(
                "G_REACH_l0_reachability",
                enforcement="ratchet",
                classification="pass",
                violation_count=1495,
                baseline_count=1495,
            )
        ],
    )
    _write_burndown(burndown)
    _write_p0_wave_plan(p0_wave)

    doc = build_action_queue(
        gate_results_path=gate,
        burndown_path=burndown,
        p0_wave_plan_path=p0_wave,
    )

    assert doc["summary"]["track_count"] == 1
    assert all(a.get("verdict_cluster") != "CANDIDATE_BLOCKER_TRIAGE" for a in doc["actions"])


def test_p0_wave_promotes_ratchet_regression(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    p0_wave = tmp_path / "p0_wave.json"
    _write_gate_results(
        gate,
        [
            _gate(
                "G_REACH_l0_reachability",
                enforcement="ratchet",
                classification="regressed",
                violation_count=1496,
                baseline_count=1495,
            )
        ],
    )
    _write_burndown(burndown)
    _write_p0_wave_plan(p0_wave)

    doc = build_action_queue(
        gate_results_path=gate,
        burndown_path=burndown,
        p0_wave_plan_path=p0_wave,
    )

    candidate_actions = [a for a in doc["actions"] if a.get("verdict_cluster") == "CANDIDATE_BLOCKER_TRIAGE"]
    assert len(candidate_actions) == 1
    assert candidate_actions[0]["file_path"] == "agentic_core/L1_cognition/reachable.py"
    assert candidate_actions[0]["impact_severity"] == "critical"
    assert candidate_actions[0]["enforcement_effect"] == "inventory"
    assert candidate_actions[0]["work_priority"] == "triage"
    assert candidate_actions[0]["queue_section"] == "candidate_blockers"


def test_p0_wave_promotes_non_ratchet_structural_issue(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    p0_wave = tmp_path / "p0_wave.json"
    _write_gate_results(gate, [])
    _write_burndown(burndown)
    _write_p0_wave_plan(p0_wave, issue_kind="dynamic_exec")

    doc = build_action_queue(
        gate_results_path=gate,
        burndown_path=burndown,
        p0_wave_plan_path=p0_wave,
    )

    assert any(a.get("verdict_cluster") == "CANDIDATE_BLOCKER_TRIAGE" for a in doc["actions"])
    assert all(
        a.get("work_priority") != "P0"
        for a in doc["actions"]
        if a.get("verdict_cluster") == "CANDIDATE_BLOCKER_TRIAGE"
    )


def test_track_never_in_notion_payload(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    _write_gate_results(
        gate,
        [
            _gate("10_infra_wiring", classification="blocked", violation_count=2),
            _gate(
                "3_write_sovereignty",
                classification="pass",
                violation_count=848,
            ),
        ],
    )
    _write_burndown(burndown)
    doc = build_action_queue(gate_results_path=gate, burndown_path=burndown)
    notion_rows = extract_notion_fix_rows(doc)
    assert notion_rows
    assert all("TRACK" not in r.get("gate_id", "") for r in notion_rows)


def test_refactor_does_not_outrank_fix(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    accel = tmp_path / "accel.json"
    _write_gate_results(
        gate,
        [
            _gate("10_infra_wiring", classification="blocked", violation_count=2),
            _gate(
                "O_tool_call_parity_ratchet",
                band="P1",
                enforcement="ratchet",
                classification="regressed",
                violation_count=316,
                baseline_count=315,
            ),
        ],
    )
    _write_burndown(burndown)
    accel.write_text(
        json.dumps(
            {
                "timestamp": "2026-05-25T12:00:00+00:00",
                "candidates": [
                    {"file_path": "agentic_core/foo.py", "impacted_tests": ["tests/unit/test_foo.py"]},
                ],
            }
        ),
        encoding="utf-8",
    )
    doc = build_action_queue(
        gate_results_path=gate,
        burndown_path=burndown,
        refactor_accelerator_path=accel,
        max_actions=10,
    )
    fix_ranks = [a["rank"] for a in doc["actions"] if a["verdict_cluster"] == "FIX"]
    refactor_ranks = [a["rank"] for a in doc["actions"] if a["verdict_cluster"] == "REFACTOR"]
    assert fix_ranks
    assert refactor_ranks
    assert max(fix_ranks) < min(refactor_ranks)


def test_refactor_accelerator_accepts_resolved_path(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    accel = tmp_path / "accel.json"
    _write_gate_results(gate, [])
    _write_burndown(burndown)
    accel.write_text(
        json.dumps(
            {
                "timestamp": "2026-05-25T12:00:00+00:00",
                "candidates": [
                    {
                        "adg_name": "ADG::Symbol::agentic_core.foo.bar",
                        "resolved_path": "agentic_core/foo.py",
                        "score": 0.42,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    doc = build_action_queue(
        gate_results_path=gate,
        burndown_path=burndown,
        refactor_accelerator_path=accel,
        max_actions=10,
    )

    refactor = next(a for a in doc["actions"] if a["verdict_cluster"] == "REFACTOR")
    assert refactor["file_path"] == "agentic_core/foo.py"
    assert refactor["symbol"] == "ADG::Symbol::agentic_core.foo.bar"


def test_hotspot_coverage_mv_becomes_graphdb_action(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    sqlite_path = tmp_path / "adg.sqlite"
    _write_gate_results(gate, [])
    _write_burndown(burndown)

    con = sqlite3.connect(sqlite_path)
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
        con.execute(
            "INSERT INTO mv_hotspot_coverage_risk VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "agentic_core/L5_safety/contracts/registry.py",
                "L5",
                "P1_URGENT",
                "CRITICAL",
                "ABSENT",
                810.0,
                822.0,
                12,
                4,
                0,
                -1.0,
            ),
        )
        con.commit()
    finally:
        con.close()

    doc = build_action_queue(
        gate_results_path=gate,
        burndown_path=burndown,
        sqlite_snapshot_path=sqlite_path,
        max_actions=10,
    )

    action = doc["actions"][0]
    assert action["verdict_cluster"] == "GRAPHDB"
    assert action["action_kind"] == "test_hotspot_gap"
    assert action["file_path"] == "agentic_core/L5_safety/contracts/registry.py"
    assert "mv_hotspot_coverage_risk" in action["signal"]
    assert validate_action_queue(doc) == []


def test_missing_accelerator_fix_only_degraded(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    _write_gate_results(
        gate,
        [_gate("1_critical_path_integrity", classification="blocked", violation_count=1)],
    )
    _write_burndown(burndown)
    doc = build_action_queue(
        gate_results_path=gate,
        burndown_path=burndown,
        refactor_accelerator_path=None,
    )
    assert doc["emit_status"] == "degraded"
    assert doc["provenance"]["degraded"] is True
    assert all(a["verdict_cluster"] == "FIX" for a in doc["actions"])


def test_cap_preserves_rank1_fix(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    gates = [
        _gate("1_critical_path_integrity", classification="blocked", violation_count=1),
    ]
    for i in range(14):
        gates.append(
            _gate(
                f"REGR_gate_{i}",
                band="P1",
                enforcement="ratchet",
                classification="regressed",
                violation_count=100 + i,
                baseline_count=100,
            )
        )
    _write_gate_results(gate, gates)
    _write_burndown(burndown)
    doc = build_action_queue(gate_results_path=gate, burndown_path=burndown, max_actions=10)
    assert doc["actions"][0]["gate_id"] == "1_critical_path_integrity"
    assert len(doc["actions"]) == 10


def test_stale_failure_clusters_rejected(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    clusters = tmp_path / "clusters.json"
    active = "2026-05-25T12:00:00+00:00"
    _write_gate_results(gate, [_gate("10_infra_wiring", classification="blocked")], ts=active)
    _write_burndown(burndown)
    clusters.write_text(
        json.dumps({"timestamp": "2020-01-01T00:00:00+00:00", "top_clusters": [{"id": "c1"}]}),
        encoding="utf-8",
    )
    doc = build_action_queue(
        gate_results_path=gate,
        burndown_path=burndown,
        failure_clusters_path=clusters,
    )
    cluster_input = next(
        i for i in doc["provenance"]["inputs"] if i["artifact_key"] == "failure_clusters"
    )
    assert cluster_input["status"] in {"stale", "rejected"}
    assert len(doc["actions"]) == 1


def test_schema_validation(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    _write_gate_results(
        gate,
        [
            _gate("10_infra_wiring", classification="blocked", violation_count=2),
            _gate(
                "O_tool_call_parity_ratchet",
                band="P1",
                enforcement="ratchet",
                classification="regressed",
                violation_count=316,
                baseline_count=315,
            ),
        ],
    )
    _write_burndown(burndown)
    doc = build_action_queue(gate_results_path=gate, burndown_path=burndown)
    errors = validate_action_queue(doc)
    assert errors == [], errors
