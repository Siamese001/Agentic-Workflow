"""Test TwoPhaseGenerationNodeTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTwoPhaseGenerationNodeTypesAdg:
    """Test TwoPhaseGenerationNodeTypesAdg functionality."""

    def test_two_phase_generation_node_types_adg_imports(self):
        """Test two_phase_generation_node_types_adg module imports."""
        from agentic_core import two_phase_generation_node_types_adg
        assert two_phase_generation_node_types_adg is not None

    def test_two_phase_generation_node_types_adg_class(self):
        """Test TwoPhaseGenerationNodeTypesAdg class exists."""
        from agentic_core import TwoPhaseGenerationNodeTypesAdg
        assert TwoPhaseGenerationNodeTypesAdg is not None

    def test_two_phase_generation_node_types_adg_callable(self):
        """Test two_phase_generation_node_types_adg functions are callable."""
        from agentic_core import validate_two_phase_generation_node_types_adg
        assert callable(validate_two_phase_generation_node_types_adg)
