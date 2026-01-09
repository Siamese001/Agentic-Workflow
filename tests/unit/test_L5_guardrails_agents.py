"""Unit tests for L5 Safety Guardrails agents."""
from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestAdversarialRedTeamerAgent:
    """Test suite for AdversarialRedTeamerAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.AdversarialRedTeamerAgent import AdversarialRedTeamerAgent
        assert AdversarialRedTeamerAgent is not None


class TestBiasDetectorAgent:
    """Test suite for BiasDetectorAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.BiasDetectorAgent import BiasDetectorAgent
        assert BiasDetectorAgent is not None


class TestConstitutionalReviewerAgent:
    """Test suite for ConstitutionalReviewerAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.ConstitutionalReviewerAgent import ConstitutionalReviewerAgent
        assert ConstitutionalReviewerAgent is not None


class TestCostGovernorAgent:
    """Test suite for CostGovernorAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.CostGovernorAgent import CostGovernorAgent
        assert CostGovernorAgent is not None


class TestFileCleanupAgent:
    """Test suite for FileCleanupAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.FileCleanupAgent import FileCleanupAgent
        assert FileCleanupAgent is not None


class TestHallucinationHunterAgent:
    """Test suite for HallucinationHunterAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.HallucinationHunterAgent import HallucinationHunterAgent
        assert HallucinationHunterAgent is not None


class TestMCPGuardianAgent:
    """Test suite for MCPGuardianAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.MCPGuardianAgent import MCPGuardianAgent
        assert MCPGuardianAgent is not None


class TestPIISanitizerAgent:
    """Test suite for PIISanitizerAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.PIISanitizerAgent import PIISanitizerAgent
        assert PIISanitizerAgent is not None


class TestPromptInjectionDetectorAgent:
    """Test suite for PromptInjectionDetectorAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.PromptInjectionDetectorAgent import PromptInjectionDetectorAgent
        assert PromptInjectionDetectorAgent is not None


class TestRedSentinelAgent:
    """Test suite for RedSentinelAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.RedSentinelAgent import RedSentinelAgent
        assert RedSentinelAgent is not None


class TestStructuralHealerAgent:
    """Test suite for StructuralHealerAgent."""

    def test_agent_can_be_imported(self):
        """Test agent can be imported."""
        from agentic_core.L5_safety.guardrails.StructuralHealerAgent import StructuralHealerAgent
        assert StructuralHealerAgent is not None


class TestMCPHardenedMixin:
    """Test suite for MCPHardenedMixin."""

    def test_mixin_exists(self):
        """Test MCPHardenedMixin can be imported."""
        from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
        assert MCPHardenedMixin is not None
