"""Runtime write path applies rigor convergence BLOCK for missing critical gates."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.sections.section_x2_gate_outputs import write_section_x2_gate_outputs


def test_write_section_x2_injects_block_for_missing_rigor_critical(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "headline_run"
    artifact_dir.mkdir(parents=True)
    write_section_x2_gate_outputs(artifact_dir, "headline", [])
    raw = json.loads((artifact_dir / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    assert raw.get("rigor_convergence_status") == "BLOCK"
    audit = raw.get("rigor_convergence_audit") or {}
    assert audit.get("status") == "BLOCK"
    assert audit.get("missing_rigor_critical_gates")
    gate_ids = {g["gate_id"] for g in raw.get("gates", [])}
    assert any(g.get("rigor_convergence") for g in raw.get("gates", []))
    assert "x2_headline_exactly_one_line" in gate_ids or audit["missing_rigor_critical_gates"]
