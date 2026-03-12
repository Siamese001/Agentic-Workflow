"""ADG-driven tests for apps_shared/reasoning/BaseDispatchAgent.py and BaseProactiveAgent.py — fan_in=2.

Contract tests: ExecutionResult, BaseDispatchAgent init, BaseProactiveAgent init.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_shared.reasoning.BaseDispatchAgent import (
    BaseDispatchAgent,
    ExecutionResult,
    _DEFAULT_TIMEOUT_S,
    _MAX_SAFE_TIMEOUT_S,
    _MIN_SAFE_TIMEOUT_S,
)
from apps_shared.reasoning.BaseProactiveAgent import BaseProactiveAgent


class TestExecutionResult:
    def test_creates_success(self):
        r = ExecutionResult(SUCCESS=True, OUTPUT="done", ERROR=None)
        assert r.SUCCESS is True
        assert r.OUTPUT == "done"

    def test_creates_failure(self):
        r = ExecutionResult(SUCCESS=False, ERROR="timeout")
        assert r.SUCCESS is False
        assert r.ERROR == "timeout"

    def test_default_duration_ms(self):
        r = ExecutionResult(SUCCESS=True)
        assert r.duration_ms == 0.0

    def test_is_named_tuple(self):
        r = ExecutionResult(SUCCESS=True)
        assert isinstance(r, tuple)


class TestTimeoutConstants:
    def test_default_timeout_positive(self):
        assert _DEFAULT_TIMEOUT_S > 0

    def test_max_timeout_greater_than_min(self):
        assert _MAX_SAFE_TIMEOUT_S > _MIN_SAFE_TIMEOUT_S

    def test_min_timeout_at_least_1(self):
        assert _MIN_SAFE_TIMEOUT_S >= 1.0


class TestBaseDispatchAgentInit:
    def test_creates_without_args(self):
        agent = BaseDispatchAgent()
        assert agent is not None

    def test_config_dict_defaults_empty(self):
        agent = BaseDispatchAgent()
        assert agent.config_dict == {}

    def test_timeout_set_from_config(self):
        agent = BaseDispatchAgent(config_dict={"timeout": 60.0})
        assert agent.TIMEOUT == 60.0

    def test_timeout_defaults_to_default_timeout(self):
        agent = BaseDispatchAgent()
        assert agent.TIMEOUT == _DEFAULT_TIMEOUT_S

    def test_has_perform_action(self):
        assert hasattr(BaseDispatchAgent, "_perform_action")

    def test_has_heal_domain_config(self):
        assert hasattr(BaseDispatchAgent, "_heal_domain_config")


class TestBaseProactiveAgentInit:
    def test_importable(self):
        assert callable(BaseProactiveAgent)

    def test_is_sovereign_base_agent(self):
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        assert issubclass(BaseProactiveAgent, SovereignBaseAgent)

    def test_has_execute_method(self):
        assert hasattr(BaseProactiveAgent, "execute")

    def test_has_get_handoff_kwargs(self):
        assert hasattr(BaseProactiveAgent, "_get_handoff_kwargs")
