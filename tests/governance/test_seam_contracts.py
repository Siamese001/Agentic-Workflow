"""
Phase 3B Wave 1.2/1.3 — Seam contract compatibility and Protocol unit tests.

Verifies:
- T1: seam contract modules re-export the same symbols as the original paths
- T2: HealingAgentProtocol is satisfied by real agents; fakes can be injected
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# T1 — Import parity tests
# ---------------------------------------------------------------------------


class TestForwardRollingContractImportParity:
    def test_execution_mode_importable(self):
        from agentic_core.seams.contracts.forward_rolling import ExecutionMode

        assert ExecutionMode is not None

    def test_forward_rolling_config_importable(self):
        from agentic_core.seams.contracts.forward_rolling import ForwardRollingConfig

        assert ForwardRollingConfig is not None

    def test_rollout_stage_importable(self):
        from agentic_core.seams.contracts.forward_rolling import RolloutStage

        assert RolloutStage is not None

    def test_health_status_importable(self):
        from agentic_core.seams.contracts.forward_rolling import HealthStatus

        assert HealthStatus is not None

    def test_contract_symbols_match_originals(self):
        from agentic_core.L3_orchestration.types.forward_rolling_types import (
            ExecutionMode as OriginalMode,
        )
        from agentic_core.seams.contracts.forward_rolling import (
            ExecutionMode as ContractMode,
        )

        assert ContractMode is OriginalMode


class TestActivationContractImportParity:
    def test_assert_activation_allowed_importable(self):
        from agentic_core.seams.contracts.activation import assert_activation_allowed

        assert callable(assert_activation_allowed)

    def test_contract_symbol_matches_original(self):
        from agentic_core.L5_safety.enforcement.activation_gate import (
            assert_activation_allowed as original_fn,
        )
        from agentic_core.seams.contracts.activation import (
            assert_activation_allowed as contract_fn,
        )

        assert contract_fn is original_fn


class TestMcpContractImportParity:
    def test_mcp_connection_manager_importable(self):
        from agentic_core.seams.contracts.mcp import MCPConnectionManager

        assert MCPConnectionManager is not None

    def test_mcp_connection_manager_is_protocol(self):
        from typing import Protocol

        from agentic_core.seams.contracts.mcp import MCPConnectionManager

        assert issubclass(MCPConnectionManager, Protocol)


# ---------------------------------------------------------------------------
# T2 — Protocol unit tests
# ---------------------------------------------------------------------------


class TestSafetyAgentProtocolDefaultWiring:
    def test_safety_agent_factory_instantiates(self):
        from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

        factory = SafetyAgentFactory(project_root=Path.cwd())
        assert factory is not None

    def test_unknown_agent_returns_none(self):
        from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

        factory = SafetyAgentFactory(project_root=Path.cwd())
        result = factory.get("NonExistentAgent")
        assert result is None

    def test_healing_agent_protocol_is_runtime_checkable(self):
        from agentic_core.seams.contracts.safety_agents import HealingAgentProtocol

        class FakeAgent:
            def heal_repository(
                self,
                dry_run: bool = True,
                execute: bool = False,
                **kwargs: Any,
            ) -> dict[str, Any]:
                return {"errors": 0}

        assert isinstance(FakeAgent(), HealingAgentProtocol)

    def test_object_without_heal_repository_fails_protocol(self):
        from agentic_core.seams.contracts.safety_agents import HealingAgentProtocol

        class NotAnAgent:
            pass

        assert not isinstance(NotAnAgent(), HealingAgentProtocol)


class TestSafetyAgentProtocolFakeInjection:
    def test_safety_strategy_accepts_injected_factory(self):
        from agentic_core.L3_orchestration.enforcement.safety_strategy import (
            SafetyStrategy,
        )
        from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

        fake_factory = MagicMock(spec=SafetyAgentFactory)
        fake_agent = MagicMock()
        fake_agent.heal_repository.return_value = {"errors": 0}
        fake_factory.get.return_value = fake_agent

        strategy = SafetyStrategy(_agent_factory=fake_factory)
        agent = strategy._get_agent("HygieneGuardianAgent")

        fake_factory.get.assert_called_once_with("HygieneGuardianAgent")
        assert agent is fake_agent

    def test_safety_strategy_default_factory_created_when_none(self):
        from agentic_core.L3_orchestration.enforcement.safety_strategy import (
            SafetyStrategy,
        )
        from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

        strategy = SafetyStrategy()
        assert isinstance(strategy._agent_factory, SafetyAgentFactory)


class TestNervousSystemAgentProtocolDefaultWiring:
    def test_safety_agent_factory_used_in_nervous_system(self):
        from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

        factory = SafetyAgentFactory(project_root=Path.cwd())
        assert factory is not None

    def test_nervous_system_agent_protocol_fake_injection(self):
        from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

        fake_factory = MagicMock(spec=SafetyAgentFactory)
        fake_factory.get.return_value = None
        fake_factory.get_legacy_import_healer_factory.return_value = None

        result = fake_factory.get("GovernanceAgent")
        assert result is None
        fake_factory.get.assert_called_once_with("GovernanceAgent")
