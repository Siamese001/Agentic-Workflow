"""Rigor-critical gates declared in lane_registry must appear in runtime X2 bundles."""

from __future__ import annotations

from apps_rg.runtime.rigor.convergence_audit import audit_missing_rigor_critical
from apps_rg.runtime.rigor.lane_registry import spec_for_lane


def test_missing_rigor_critical_gate_is_block_not_pass() -> None:
    lane = "headline"
    crit = spec_for_lane(lane).critical_gates
    assert crit
    present = {next(iter(crit))}  # deliberately incomplete
    audit = audit_missing_rigor_critical(lane=lane, present=present)
    assert audit["status"] == "BLOCK"
    assert audit["missing_rigor_critical_gates"]


def test_complete_gate_set_passes_audit() -> None:
    lane = "executive_summary"
    crit = set(spec_for_lane(lane).critical_gates)
    audit = audit_missing_rigor_critical(lane=lane, present=crit, c0_sidecar=True)
    assert audit["status"] == "PASS"
    assert audit["missing_rigor_critical_gates"] == []


def test_unknown_status_when_no_gates_emitted() -> None:
    audit = audit_missing_rigor_critical(lane="headline", present=set())
    assert audit["status"] == "BLOCK"
    assert "x2_headline" in audit["missing_rigor_critical_gates"][0] or audit["missing_rigor_critical_gates"]
