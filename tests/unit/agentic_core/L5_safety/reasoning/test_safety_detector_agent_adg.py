"""Test SafetyDetectorAgentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSafetyDetectorAgentAdg:
    """Test SafetyDetectorAgentAdg functionality."""

    def test_safety_detector_agent_adg_imports(self):
        """Test safety_detector_agent_adg module imports."""
        from agentic_core import safety_detector_agent_adg
        assert safety_detector_agent_adg is not None

    def test_safety_detector_agent_adg_class(self):
        """Test SafetyDetectorAgentAdg class exists."""
        from agentic_core import SafetyDetectorAgentAdg
        assert SafetyDetectorAgentAdg is not None

    def test_safety_detector_agent_adg_callable(self):
        """Test safety_detector_agent_adg functions are callable."""
        from agentic_core import validate_safety_detector_agent_adg
        assert callable(validate_safety_detector_agent_adg)
