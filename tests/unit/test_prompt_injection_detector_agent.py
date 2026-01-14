# tests/unit/test_prompt_injection_detector_agent.py
"""Unit tests for PromptInjectionDetectorAgent - L5 Safety."""
import pytest
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestPromptInjectionDetectorAgentImport:
    """Test suite for PromptInjectionDetectorAgent import and structure."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.PromptInjectionDetectorAgent import PromptInjectionDetectorAgent
        assert PromptInjectionDetectorAgent is not None

    def test_agent_has_required_attributes(self):
        """Test agent class has expected attributes."""
        from agentic_core.L5_safety.guardrails.PromptInjectionDetectorAgent import PromptInjectionDetectorAgent
        # Check class exists and has key methods
        assert hasattr(PromptInjectionDetectorAgent, 'run_async') or hasattr(PromptInjectionDetectorAgent, 'run')
        assert hasattr(PromptInjectionDetectorAgent, 'heal_repository')

    def test_agent_inherits_from_safety_base(self):
        """Test agent inherits from L5SafetyBaseAgent."""
        from agentic_core.L5_safety.guardrails.PromptInjectionDetectorAgent import PromptInjectionDetectorAgent
        from agentic_core.L5_safety.guardrails.L5SafetyBaseAgent import L5SafetyBaseAgent
        assert issubclass(PromptInjectionDetectorAgent, L5SafetyBaseAgent)
