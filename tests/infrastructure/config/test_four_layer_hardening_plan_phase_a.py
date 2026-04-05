"""Test FourLayerHardeningPlanPhaseA functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFourLayerHardeningPlanPhaseA:
    """Test FourLayerHardeningPlanPhaseA functionality."""

    def test_four_layer_hardening_imports(self):
        """Test four layer hardening module imports."""
        from infrastructure import four_layer_hardening
        assert four_layer_hardening is not None

    def test_four_layer_hardening_plan(self):
        """Test four layer hardening plan exists."""
        from infrastructure.four_layer_hardening import FourLayerHardeningPlan
        assert FourLayerHardeningPlan is not None

    def test_four_layer_hardening_validate(self):
        """Test four layer hardening validate function."""
        from infrastructure.four_layer_hardening import validate_phase_a
        assert callable(validate_phase_a)
