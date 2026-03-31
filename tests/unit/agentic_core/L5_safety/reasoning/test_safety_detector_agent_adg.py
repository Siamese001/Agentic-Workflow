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
        """Test SafetyDetectorAgent module imports as module type."""
        import types

        from agentic_core.L5_safety.reasoning import SafetyDetectorAgent as agent_module

        assert agent_module is not None
        assert isinstance(agent_module, types.ModuleType)

    def test_safety_detector_agent_adg_class(self):
        """Test SafetyDetectorAgent class exists and can be instantiated."""
        from agentic_core.L5_safety.reasoning.SafetyDetectorAgent import SafetyDetectorAgent

        assert SafetyDetectorAgent is not None
        # Test instantiation with default config
        agent = SafetyDetectorAgent()
        assert agent is not None
        assert hasattr(agent, "detect_all")
        assert hasattr(agent, "is_safe")

    def test_safety_detector_agent_adg_callable(self):
        """Test SafetyDetectorAgent methods are callable."""
        from agentic_core.L5_safety.reasoning.SafetyDetectorAgent import SafetyDetectorAgent

        agent = SafetyDetectorAgent()
        assert callable(agent.detect_all)
        assert callable(agent.detect_injection)
        assert callable(agent.is_safe)
        assert callable(agent.get_safety_score)
