"""W2 — burndown report includes Next action section."""

from __future__ import annotations

import json
import os
from pathlib import Path

from tools.reports.adg_burndown_report import render


def test_burndown_includes_next_action_section(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    queue_dir = tmp_path / "artifacts" / "adg"
    queue_dir.mkdir(parents=True)
    (queue_dir / "adg_action_queue_test.json").write_text(
        json.dumps(
            {
                "emit_status": "degraded",
                "provenance": {"degraded": True, "degradation_reasons": ["refactor_accelerator missing"]},
                "summary": {"fix_count": 2, "track_count": 1, "actions_emitted": 2},
                "actions": [
                    {
                        "rank": 1,
                        "verdict_cluster": "FIX",
                        "gate_id": "10_infra_wiring",
                        "ordering_reason": "fix_block_p0",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    gate.write_text(
        json.dumps(
            {
                "timestamp": "2026-05-25T12:00:00+00:00",
                "overall_exit_code": 1,
                "gates": [
                    {
                        "gate_id": "10_infra_wiring",
                        "band": "P0",
                        "enforcement": "block",
                        "classification": "blocked",
                        "violation_count": 2,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    burndown.write_text(json.dumps({"schema_version": "2.2", "summary": {}}), encoding="utf-8")

    import tools.reports.adg_burndown_report as mod

    old_artifacts = mod.ARTIFACTS
    mod.ARTIFACTS = queue_dir
    try:
        md = render(gate, burndown)
    finally:
        mod.ARTIFACTS = old_artifacts

    assert "## Next action" in md
    assert "emit_status" in md
    assert "degraded" in md
    assert "adg_action_queue_test.json" in md


def test_burndown_prefers_current_snapshot_action_queue(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    queue_dir = tmp_path / "artifacts" / "adg"
    queue_dir.mkdir(parents=True)

    active_ts = "2026-05-25T12:00:00+00:00"
    matching = queue_dir / "adg_action_queue_current.json"
    stale = queue_dir / "adg_action_queue_stale.json"
    matching.write_text(
        json.dumps(
            {
                "emit_status": "ok",
                "provenance": {"active_snapshot_ts": active_ts, "degraded": False},
                "summary": {"fix_count": 2, "track_count": 1, "actions_emitted": 1},
                "actions": [{"rank": 1, "verdict_cluster": "FIX", "gate_id": "10_infra_wiring"}],
            }
        ),
        encoding="utf-8",
    )
    stale.write_text(
        json.dumps(
            {
                "emit_status": "ok",
                "provenance": {"active_snapshot_ts": "2026-05-24T12:00:00+00:00", "degraded": False},
                "summary": {"fix_count": 99, "track_count": 99, "actions_emitted": 1},
                "actions": [{"rank": 1, "verdict_cluster": "FIX", "gate_id": "stale_gate"}],
            }
        ),
        encoding="utf-8",
    )
    os.utime(stale, (matching.stat().st_mtime + 10, matching.stat().st_mtime + 10))

    gate.write_text(
        json.dumps(
            {
                "timestamp": active_ts,
                "overall_exit_code": 1,
                "gates": [
                    {
                        "gate_id": "10_infra_wiring",
                        "band": "P0",
                        "enforcement": "block",
                        "classification": "blocked",
                        "violation_count": 2,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    burndown.write_text(json.dumps({"schema_version": "2.2", "summary": {}}), encoding="utf-8")

    import tools.reports.adg_burndown_report as mod

    old_artifacts = mod.ARTIFACTS
    mod.ARTIFACTS = queue_dir
    try:
        md = render(gate, burndown)
    finally:
        mod.ARTIFACTS = old_artifacts

    assert "adg_action_queue_current.json" in md
    assert "adg_action_queue_stale.json" not in md
    assert "stale_gate" not in md


def test_burndown_next_action_renders_graphdb_lane(tmp_path: Path) -> None:
    gate = tmp_path / "gates.json"
    burndown = tmp_path / "burndown.json"
    queue_dir = tmp_path / "artifacts" / "adg"
    queue_dir.mkdir(parents=True)
    active_ts = "2026-05-25T12:00:00+00:00"
    (queue_dir / "adg_action_queue_current.json").write_text(
        json.dumps(
            {
                "emit_status": "ok",
                "provenance": {"active_snapshot_ts": active_ts, "degraded": False},
                "summary": {"fix_count": 0, "track_count": 0, "actions_emitted": 1},
                "actions": [
                    {
                        "rank": 1,
                        "verdict_cluster": "GRAPHDB",
                        "action_kind": "test_hotspot_gap",
                        "source_id": "agentic_core/foo.py",
                        "ordering_reason": "mv_hotspot_coverage_risk_priority",
                        "signal": "Test hotspot gap from mv_hotspot_coverage_risk; priority=P1_URGENT",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    gate.write_text(
        json.dumps({"timestamp": active_ts, "overall_exit_code": 0, "gates": []}),
        encoding="utf-8",
    )
    burndown.write_text(json.dumps({"schema_version": "2.2", "summary": {}}), encoding="utf-8")

    import tools.reports.adg_burndown_report as mod

    old_artifacts = mod.ARTIFACTS
    mod.ARTIFACTS = queue_dir
    try:
        md = render(gate, burndown)
    finally:
        mod.ARTIFACTS = old_artifacts

    assert "| 1 | GRAPHDB | test_hotspot_gap | `agentic_core/foo.py` |" in md
    assert "mv_hotspot_coverage_risk_priority" in md
