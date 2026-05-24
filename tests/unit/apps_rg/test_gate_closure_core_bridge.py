"""W2.2: apps_rg gate-closure map exports to core GateClosureMap."""

from __future__ import annotations

from apps_rg.runtime.judges.executive_summary_x1d_gate_closure_map import (
    EXECUTIVE_SUMMARY_GATE_CLOSURE_MAP,
    RECONCILIATION_POLICY_VERSION,
    core_gate_closure_map,
)


def test_core_gate_closure_map_non_empty() -> None:
    cmap = core_gate_closure_map()
    assert len(cmap.rules) == len(EXECUTIVE_SUMMARY_GATE_CLOSURE_MAP)
    assert cmap.version == RECONCILIATION_POLICY_VERSION


def test_core_map_gate_ids_match_ssot() -> None:
    apps_ids = {r.gate_id for r in EXECUTIVE_SUMMARY_GATE_CLOSURE_MAP}
    core_ids = {r.gate_id for r in core_gate_closure_map().rules}
    assert apps_ids == core_ids
