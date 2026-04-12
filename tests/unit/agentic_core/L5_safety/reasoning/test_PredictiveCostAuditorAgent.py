"""Test Predictivecostauditoragent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPredictivecostauditoragent:
    """Test Predictivecostauditoragent functionality."""

    def test_PredictiveCostAuditorAgent_imports(self):
        """Test PredictiveCostAuditorAgent module imports."""
        from agentic_core import PredictiveCostAuditorAgent

        assert PredictiveCostAuditorAgent is not None

    def test_PredictiveCostAuditorAgent_class(self):
        """Test Predictivecostauditoragent class exists."""
        from agentic_core import Predictivecostauditoragent

        assert Predictivecostauditoragent is not None

    def test_PredictiveCostAuditorAgent_callable(self):
        """Test PredictiveCostAuditorAgent functions are callable."""
        from agentic_core import validate_PredictiveCostAuditorAgent

        assert callable(validate_PredictiveCostAuditorAgent)
