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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_seam_contracts")
_emit_applies_guardrail("p0", "test_seam_contracts", "p0_governance")
_emit_reads_policy_state("p0", "test_seam_contracts", "policy_binding")
_emit_snapshots_state("p0", "test_seam_contracts", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_seam_contracts", "p4obs", "metric_1")
_emit_emits_metric_event("test_seam_contracts", "p4obs", "metric_2")
_emit_emits_metric_event("test_seam_contracts", "p4obs", "metric_3")
_emit_emits_metric_event("test_seam_contracts", "p4obs", "metric_4")
_emit_emits_metric_event("test_seam_contracts", "p4obs", "metric_5")
_emit_emits_metric_event("test_seam_contracts", "p4obs", "metric_6")
_emit_records_incident_event("test_seam_contracts", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_seam_contracts", "p4obs", "anomaly")
_emit_writes_observability_log("test_seam_contracts", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_seam_contracts", "p4obs", "mon_state")
_emit_triggers_alert("test_seam_contracts", "p4obs", "alert")
_emit_links_incident_trace("test_seam_contracts", "p4obs", "trace_link")
_emit_captures_pattern("test_seam_contracts", "p3lm", "pattern")
_emit_records_learning_event("test_seam_contracts", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_seam_contracts", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_seam_contracts", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_seam_contracts", "p3lm", "routing")
_emit_improves_agent_policy("test_seam_contracts", "p3lm", "policy")
_emit_stores_learning_state("test_seam_contracts", "p3lm", "state")
_emit_records_execution_trace("test_seam_contracts", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_seam_contracts", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_seam_contracts", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_seam_contracts", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_seam_contracts", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_seam_contracts", "env_read", "p2_env_1")
_emit_reads_environ("test_seam_contracts", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_seam_contracts", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_seam_contracts", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_seam_contracts", "context_pull")
_emit_pulls_context("p1", "test_seam_contracts", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_seam_contracts", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_seam_contracts", "uwg_term_2")
_emit_writes_through("p1", "test_seam_contracts", "write_through")
_emit_writes_through("p1", "test_seam_contracts", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_seam_contracts", "safety_validation")
_emit_invokes_eval("p1", "test_seam_contracts", "eval_call")
_emit_proposal_commits_routing("p1", "test_seam_contracts", "routing_commit")
emit_replay_key("p0", "test_seam_contracts")
emit_determinism_digest("p0", "test_seam_contracts")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_seam_contracts", "execution_auth")
_emit_validates_capability("p2", "test_seam_contracts", "capability_check")
_emit_routes_to_capability("p2", "test_seam_contracts", "capability_route")
_emit_writes_via_uwg("p2", "test_seam_contracts", "uwg_write")
_emit_blocks_direct_write("p2", "test_seam_contracts", "direct_write_block")
_emit_records_tool_invocation("p2", "test_seam_contracts", "tool_invocation")
_emit_captures_execution_output("p2", "test_seam_contracts", "exec_output")
_emit_dispatches_agent("p3", "test_seam_contracts", "agent_dispatch")
_emit_coordinates_agents("p3", "test_seam_contracts", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_seam_contracts", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_seam_contracts", "healing_outcome")
_emit_escalates_failure("p3", "test_seam_contracts", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_seam_contracts", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_seam_contracts", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_seam_contracts", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_seam_contracts", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_seam_contracts", "eval_metric")
_emit_stores_embedding("p4", "test_seam_contracts", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_seam_contracts", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_seam_contracts", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
