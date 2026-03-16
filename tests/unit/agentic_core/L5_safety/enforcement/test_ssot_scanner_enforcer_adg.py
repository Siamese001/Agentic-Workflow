"""ADG-driven tests for L5_safety/enforcement/ssot_scanner_enforcer.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_ssot_scanner_enforcer_adg")
_emit_applies_guardrail("p0", "test_ssot_scanner_enforcer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_ssot_scanner_enforcer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_ssot_scanner_enforcer_adg", "state_snapshot")
emit_replay_key("p0", "test_ssot_scanner_enforcer_adg")
emit_determinism_digest("p0", "test_ssot_scanner_enforcer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.ssot_scanner_enforcer import AgentMetadata


class TestAgentMetadata:
    def _make(self, layer="L1_cognition", assigned_layer="L1_cognition"):
        from pathlib import Path
        return AgentMetadata(
            file_path=Path("agentic_core/L1_cognition/reasoning/FooAgent.py"),
            relative_path="agentic_core/L1_cognition/reasoning/FooAgent.py",
            class_name="FooAgent",
            layer=layer,
            assigned_layer=assigned_layer,
            base_classes=["SovereignBaseAgent"],
            signals=set(),
        )

    def test_creates(self):
        m = self._make()
        assert m.class_name == "FooAgent"

    def test_compliant_when_layers_match(self):
        m = self._make("L1_cognition", "L1_cognition")
        assert m.is_compliant is True

    def test_not_compliant_when_layers_mismatch(self):
        m = self._make("L0_routing", "L1_cognition")
        assert m.is_compliant is False

    def test_no_gravity_violation_for_app_layer(self):
        m = self._make("APP", "L2_execution")
        assert m.has_gravity_violation is False

    def test_gravity_violation_when_layers_mismatch(self):
        m = self._make("L0_routing", "L5_safety")
        assert m.has_gravity_violation is True

    def test_base_classes_list(self):
        m = self._make()
        assert isinstance(m.base_classes, list)
