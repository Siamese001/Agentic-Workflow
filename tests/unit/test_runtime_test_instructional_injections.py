# tests/unit/test_runtime_test_instructional_injections.py
"""Unit tests for Instructional Injections Runtime."""
from __future__ import annotations
import pytest


class TestInstructionalInjections:
    """Test instructional injection detection."""

    def test_l5_safety_module_exists(self):
        """Test L5 safety module exists."""
        import agentic_core.L5_safety
        assert agentic_core.L5_safety is not None

    def test_guardrails_module_exists(self):
        """Test guardrails module exists."""
        import agentic_core.L5_safety.guardrails
        assert agentic_core.L5_safety.guardrails is not None

    def test_prompt_injection_detector_importable(self):
        """Test PromptInjectionDetectorAgent can be imported."""
        from agentic_core.L5_safety.guardrails.PromptInjectionDetectorAgent import PromptInjectionDetectorAgent
        assert PromptInjectionDetectorAgent is not None
