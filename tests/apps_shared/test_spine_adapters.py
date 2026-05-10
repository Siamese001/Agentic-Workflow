"""Tests for apps_shared spine adapter components."""

import pytest

from apps_shared.spine.base_spine_adapter import (
    BaseSpineAdapter,
)
from apps_shared.spine.risk_gate_adapter import (
    RiskGateAdapter,
)


class TestBaseSpineAdapter:
    """Test BaseSpineAdapter."""

    def test_adapter_import(self):
        """Test that BaseSpineAdapter can be imported."""
        assert BaseSpineAdapter is not None

    def test_adapter_class_exists(self):
        """Test that BaseSpineAdapter class exists."""
        assert callable(BaseSpineAdapter)


class TestRiskGateAdapter:
    """Test RiskGateAdapter."""

    def test_adapter_import(self):
        """Test that RiskGateAdapter can be imported."""
        assert RiskGateAdapter is not None

    def test_adapter_class_exists(self):
        """Test that RiskGateAdapter class exists."""
        assert callable(RiskGateAdapter)


class TestCIDRegistryAndExecutionCycle:
    """G4: CIDRegistry + ExecutionCycle added to agentic_core.interfaces.execution."""

    def test_cid_registry_new_cycle_happy_path(self):
        from agentic_core.interfaces.execution import CIDRegistry, ExecutionCycle

        reg = CIDRegistry()
        cycle = reg.new_cycle("tx-001")
        assert isinstance(cycle, ExecutionCycle)
        assert cycle.cid == "tx-001"
        assert cycle.attempt == 1

    def test_cid_registry_increments_attempt_on_same_cid(self):
        from agentic_core.interfaces.execution import CIDRegistry

        reg = CIDRegistry()
        reg.new_cycle("tx-001")
        cycle2 = reg.new_cycle("tx-001")
        assert cycle2.attempt == 2

    def test_cid_registry_independent_cids_dont_interfere(self):
        from agentic_core.interfaces.execution import CIDRegistry

        reg = CIDRegistry()
        c1 = reg.new_cycle("alpha")
        c2 = reg.new_cycle("beta")
        assert c1.attempt == 1
        assert c2.attempt == 1

    def test_execution_cycle_is_frozen_dataclass(self):
        from agentic_core.interfaces.execution import ExecutionCycle

        cycle = ExecutionCycle(cid="abc", attempt=1)
        with pytest.raises((AttributeError, TypeError)):
            cycle.cid = "xyz"  # type: ignore[misc]
