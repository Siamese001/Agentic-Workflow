"""ADG-driven tests for L2_execution/types/l2_phase_spec.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.l2_phase_spec import PhaseSpec


class TestPhaseSpec:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PhaseSpec)

    def test_is_frozen(self):
        spec = PhaseSpec(name="pre_audit")
        with pytest.raises((AttributeError, TypeError)):
            spec.name = "discovery"

    def test_creates_with_name(self):
        spec = PhaseSpec(name="pre_audit")
        assert spec.name == "pre_audit"

    def test_all_canonical_phases_creatable(self):
        phases = [
            "pre_audit", "discovery", "reconciliation",
            "alignment", "arch_validation", "healing", "certification",
        ]
        for phase in phases:
            spec = PhaseSpec(name=phase)
            assert spec.name == phase
