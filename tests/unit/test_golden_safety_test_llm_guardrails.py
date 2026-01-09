# tests/unit/test_golden_safety_test_llm_guardrails.py
"""Unit tests for LLM Guardrails."""
from __future__ import annotations
import pytest


class TestLLMGuardrails:
    """Test LLM guardrails module."""

    def test_mcp_hardened_mixin_importable(self):
        """Test MCPHardenedMixin can be imported."""
        from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
        assert MCPHardenedMixin is not None

    def test_cost_governor_importable(self):
        """Test CostGovernorAgent can be imported."""
        from agentic_core.L5_safety.guardrails.CostGovernorAgent import CostGovernorAgent
        assert CostGovernorAgent is not None

    def test_hallucination_hunter_importable(self):
        """Test HallucinationHunterAgent can be imported."""
        from agentic_core.L5_safety.guardrails.HallucinationHunterAgent import HallucinationHunterAgent
        assert HallucinationHunterAgent is not None
