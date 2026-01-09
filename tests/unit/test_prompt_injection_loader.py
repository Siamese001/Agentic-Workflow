# tests/unit/test_prompt_injection_loader.py
"""Unit tests for Prompt Injection Detection."""
from __future__ import annotations
import pytest


class TestPromptInjectionDetectorAgent:
    """Test PromptInjectionDetectorAgent imports and structure."""

    def test_agent_can_be_imported(self):
        """Test PromptInjectionDetectorAgent can be imported."""
        from agentic_core.L5_safety.guardrails.PromptInjectionDetectorAgent import PromptInjectionDetectorAgent
        assert PromptInjectionDetectorAgent is not None

    def test_agent_inherits_from_safety_base(self):
        """Test agent inherits from SafetyBaseAgent."""
        from agentic_core.L5_safety.guardrails.PromptInjectionDetectorAgent import PromptInjectionDetectorAgent
        from agentic_core.L5_safety.guardrails.SafetyBaseAgent import SafetyBaseAgent
        assert issubclass(PromptInjectionDetectorAgent, SafetyBaseAgent)


class TestInputValidationGuardrail:
    """Test InputValidationGuardrail."""

    def test_guardrail_can_be_imported(self):
        """Test InputValidationGuardrail can be imported."""
        from agentic_core.L5_safety.guardrails.InputValidationGuardrail import InputValidationGuardrail
        assert InputValidationGuardrail is not None
