"""ADG-driven tests for L5_safety/enforcement/ssot_scanner_enforcer.py — fan_in=1."""
from __future__ import annotations

import pytest

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
