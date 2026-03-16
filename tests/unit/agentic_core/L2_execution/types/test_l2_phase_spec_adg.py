"""ADG-driven tests for L2_execution/types/l2_phase_spec.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_l2_phase_spec_adg")
_emit_applies_guardrail("p0", "test_l2_phase_spec_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_l2_phase_spec_adg", "policy_binding")
_emit_snapshots_state("p0", "test_l2_phase_spec_adg", "state_snapshot")
emit_replay_key("p0", "test_l2_phase_spec_adg")
emit_determinism_digest("p0", "test_l2_phase_spec_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
