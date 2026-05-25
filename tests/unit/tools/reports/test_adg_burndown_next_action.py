"""W2 — burndown report includes Next action section."""

from __future__ import annotations

import json
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
