# tests/unit/test_golden_safety_test_safety_properties.py
"""Unit tests for Safety Properties."""
from __future__ import annotations
import pytest


class TestSafetyProperties:
    """Test safety properties module."""

    def test_l5_safety_module_exists(self):
        """Test L5 safety module exists."""
        import agentic_core.L5_safety
        assert agentic_core.L5_safety is not None

    def test_safety_base_agent_importable(self):
        """Test L5SafetyBaseAgent can be imported."""
        from agentic_core.L5_safety.guardrails.L5SafetyBaseAgent import L5SafetyBaseAgent
        assert L5SafetyBaseAgent is not None

    def test_bias_detector_importable(self):
        """Test BiasDetectorAgent can be imported."""
        from agentic_core.L5_safety.guardrails.BiasDetectorAgent import BiasDetectorAgent
        assert BiasDetectorAgent is not None

    def test_pii_sanitizer_importable(self):
        """Test PIISanitizerAgent can be imported."""
        from agentic_core.L5_safety.guardrails.PIISanitizerAgent import PIISanitizerAgent
        assert PIISanitizerAgent is not None
