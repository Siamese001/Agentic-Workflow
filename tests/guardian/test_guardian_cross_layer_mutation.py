"""Test GuardianCrossLayerMutation functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianCrossLayerMutation:
    """Test GuardianCrossLayerMutation functionality."""

    def test_guardian_cross_layer_mutation_imports(self):
        """Test guardian_cross_layer_mutation module imports."""
        from agentic_core import guardian_cross_layer_mutation
        assert guardian_cross_layer_mutation is not None

    def test_guardian_cross_layer_mutation_class(self):
        """Test GuardianCrossLayerMutation class exists."""
        from agentic_core import GuardianCrossLayerMutation
        assert GuardianCrossLayerMutation is not None

    def test_guardian_cross_layer_mutation_callable(self):
        """Test guardian_cross_layer_mutation functions are callable."""
        from agentic_core import validate_guardian_cross_layer_mutation
        assert callable(validate_guardian_cross_layer_mutation)
