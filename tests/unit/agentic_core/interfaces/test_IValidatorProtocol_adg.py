"""Behavioral tests for IValidatorProtocol.py: _run_agent helper, get_integration_status."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.unit
class TestRunAgentHelper:
    # --- happy path ---

    def test_run_agent_returns_act_result(self):
        from agentic_core.interfaces.IValidatorProtocol import _run_agent

        async def _fake_act():
            return {"result": "ok"}

        agent = MagicMock()
        agent.act = _fake_act
        result = _run_agent(agent)
        assert result == {"result": "ok"}

    # --- failure path ---

    def test_run_agent_closes_loop_on_exception(self):
        from agentic_core.interfaces.IValidatorProtocol import _run_agent

        async def _raise():
            raise ValueError("boom")

        agent = MagicMock()
        agent.act = _raise
        with pytest.raises(ValueError, match="boom"):
            _run_agent(agent)

    # --- edge case ---

    def test_run_agent_returns_dict(self):
        from agentic_core.interfaces.IValidatorProtocol import _run_agent

        async def _empty():
            return {}

        agent = MagicMock()
        agent.act = _empty
        result = _run_agent(agent)
        assert isinstance(result, dict)


@pytest.mark.unit
class TestGetIntegrationStatus:
    # --- happy path ---

    def test_keys_include_validator_flags(self):
        from agentic_core.interfaces.IValidatorProtocol import get_integration_status

        status = get_integration_status()
        for key in (
            "adversarial_validator_initialized",
            "boundary_validator_initialized",
            "validators_available",
        ):
            assert key in status, f"Missing key: {key}"

    # --- edge case ---

    def test_validators_available_is_list_of_strings(self):
        from agentic_core.interfaces.IValidatorProtocol import get_integration_status

        status = get_integration_status()
        available = status["validators_available"]
        assert isinstance(available, list)
        assert all(isinstance(v, str) for v in available)

    def test_initialized_flags_are_bool(self):
        from agentic_core.interfaces.IValidatorProtocol import get_integration_status

        status = get_integration_status()
        assert isinstance(status["adversarial_validator_initialized"], bool)
        assert isinstance(status["boundary_validator_initialized"], bool)


@pytest.mark.unit
class TestAdversarialValidatorUnavailable:
    """G5: validate returns agent_unavailable when agent cannot be imported."""

    def test_validate_agent_unavailable(self):
        from agentic_core.interfaces.IValidatorProtocol import AdversarialValidator

        v = AdversarialValidator()
        v._initialized = True
        v._agent = None
        result = v.validate("test content", {})
        assert result["valid"] is True
        assert result["errors"] == []
        assert result["threat_assessment"]["status"] == "agent_unavailable"

    def test_validate_agent_unavailable_returns_dict(self):
        from agentic_core.interfaces.IValidatorProtocol import AdversarialValidator

        v = AdversarialValidator()
        v._initialized = True
        v._agent = None
        assert isinstance(v.validate("x", {}), dict)


@pytest.mark.unit
class TestBoundaryValidatorUnavailable:
    """G6: validate returns safe fallback when agent cannot be imported."""

    def test_validate_agent_unavailable(self):
        from agentic_core.interfaces.IValidatorProtocol import BoundaryValidator

        v = BoundaryValidator()
        v._initialized = True
        v._agent = None
        result = v.validate("test content", {})
        assert result["valid"] is True
        assert result["errors"] == []
        assert result["recommendations"] == []

    def test_validate_agent_unavailable_returns_dict(self):
        from agentic_core.interfaces.IValidatorProtocol import BoundaryValidator

        v = BoundaryValidator()
        v._initialized = True
        v._agent = None
        assert isinstance(v.validate("x", {}), dict)
