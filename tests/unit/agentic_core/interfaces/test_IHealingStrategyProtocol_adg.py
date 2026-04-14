"""Behavioral tests for IHealingStrategyProtocol.py: _run_agent helper, get_integration_status."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.mark.unit
class TestRunAgentHelperHealing:
    # --- happy path ---

    def test_run_agent_returns_act_result(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import _run_agent

        async def _fake_act():
            return {"scenarios_tested": 2}

        agent = MagicMock()
        agent.act = _fake_act
        result = _run_agent(agent)
        assert result == {"scenarios_tested": 2}

    # --- failure path ---

    def test_run_agent_propagates_exception(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import _run_agent

        async def _fail():
            raise RuntimeError("agent failed")

        agent = MagicMock()
        agent.act = _fail
        with pytest.raises(RuntimeError, match="agent failed"):
            _run_agent(agent)

    # --- edge case ---

    def test_run_agent_returns_empty_dict(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import _run_agent

        async def _empty():
            return {}

        agent = MagicMock()
        agent.act = _empty
        assert _run_agent(agent) == {}


@pytest.mark.unit
class TestChaosResilienceStrategyCanHeal:
    """G3: can_heal supported/unsupported type."""

    def test_supported_type_returns_true(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        assert strategy.can_heal({"type": "resilience_check"}) is True

    def test_unsupported_type_returns_false(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        assert strategy.can_heal({"type": "nonexistent_violation"}) is False

    def test_missing_type_key_returns_false(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        assert strategy.can_heal({}) is False


@pytest.mark.unit
class TestChaosResilienceStrategyHealUnavailable:
    """G4: heal returns agent_unavailable when agent cannot be imported."""

    def test_heal_returns_agent_unavailable(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import ChaosResilienceStrategy

        strategy = ChaosResilienceStrategy()
        strategy._initialized = True
        strategy._agent = None
        result = strategy.heal({"type": "resilience_check"}, {})
        assert result["success"] is True
        assert result["status"] == "agent_unavailable"
        assert result["scenarios_tested"] == 0
        assert result["resilience_score"] == 1.0


@pytest.mark.unit
class TestGetIntegrationStatusHealingAdg:
    # --- happy path ---

    def test_supported_violations_is_nonempty_list(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import get_integration_status

        status = get_integration_status()
        assert isinstance(status["supported_violations"], list)
        assert len(status["supported_violations"]) > 0

    # --- failure path (key contract) ---

    def test_strategies_available_is_list_of_strings(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import get_integration_status

        status = get_integration_status()
        available = status["strategies_available"]
        assert isinstance(available, list)
        assert all(isinstance(s, str) for s in available)

    # --- edge case ---

    def test_chaos_strategy_initialized_is_bool(self):
        from agentic_core.interfaces.IHealingStrategyProtocol import get_integration_status

        status = get_integration_status()
        assert isinstance(status["chaos_strategy_initialized"], bool)
