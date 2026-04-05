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
