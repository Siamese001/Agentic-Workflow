"""Test GuardianAggregation functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianAggregation:
    """Test GuardianAggregation functionality."""

    def test_guardian_aggregation_imports(self):
        """Test guardian_aggregation module imports."""
        from agentic_core import guardian_aggregation
        assert guardian_aggregation is not None

    def test_guardian_aggregation_class(self):
        """Test GuardianAggregation class exists."""
        from agentic_core import GuardianAggregation
        assert GuardianAggregation is not None

    def test_guardian_aggregation_callable(self):
        """Test guardian_aggregation functions are callable."""
        from agentic_core import validate_guardian_aggregation
        assert callable(validate_guardian_aggregation)
