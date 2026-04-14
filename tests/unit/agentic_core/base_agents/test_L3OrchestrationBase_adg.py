"""Tests for phase-hardened L3OrchestrationBase behaviors."""

import pytest
from unittest.mock import MagicMock, patch

import agentic_core.utils.decorators_util as _dec_util
from agentic_core.base_agents.L3OrchestrationBase import L3OrchestrationBase
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


@pytest.mark.unit
class TestL3OrchestrationBaseHardening:
    """Behavioral coverage for phase-hardened L3OrchestrationBase."""

    def test_depth_at_max_returns_empty_result(self):
        """Happy: depth == max_depth returns empty result without delegating to super."""
        agent = L3OrchestrationBase()
        with patch.object(_dec_util, "_get_heal_policy_types", return_value=(MagicMock(), MagicMock())):
            result = agent.heal_repository(depth=3, max_depth=3)
        assert result["violations_found"] == 0
        assert result["errors"] == []

    def test_call_path_discarded_after_super_raises(self):
        """Failure: finally block removes agent from call_path even when super raises RuntimeError."""
        agent = L3OrchestrationBase()
        call_path = set()
        with patch.object(_dec_util, "_get_heal_policy_types", return_value=(MagicMock(), MagicMock())):
            with patch.object(SovereignBaseAgent, "heal_repository", side_effect=RuntimeError("boom")):
                agent.heal_repository(depth=0, max_depth=3, _call_path=call_path)
        assert "L3OrchestrationBase" not in call_path

    def test_cycle_detection_skips_when_already_in_call_path(self):
        """Edge: agent already in call_path returns empty result immediately."""
        agent = L3OrchestrationBase()
        with patch.object(_dec_util, "_get_heal_policy_types", return_value=(MagicMock(), MagicMock())):
            result = agent.heal_repository(depth=0, max_depth=3, _call_path={"L3OrchestrationBase"})
        assert result["violations_found"] == 0
