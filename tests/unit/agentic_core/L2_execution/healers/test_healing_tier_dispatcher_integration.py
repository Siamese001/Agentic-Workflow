"""Tests for healing_tier_dispatcher Phase 2 integration."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
    dispatch_healing,
)
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingInput,
    HealingTier,
)
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

_emit_authorize_and_execute("p2", "test_healing_tier_dispatcher_integration", "execution_auth")
_emit_validates_capability("p2", "test_healing_tier_dispatcher_integration", "capability_check")
_emit_routes_to_capability("p2", "test_healing_tier_dispatcher_integration", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_tier_dispatcher_integration", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_tier_dispatcher_integration", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_tier_dispatcher_integration", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_tier_dispatcher_integration", "exec_output")
_emit_dispatches_agent("p3", "test_healing_tier_dispatcher_integration", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_tier_dispatcher_integration", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_tier_dispatcher_integration", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_tier_dispatcher_integration", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_tier_dispatcher_integration", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_tier_dispatcher_integration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_tier_dispatcher_integration", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_tier_dispatcher_integration", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_tier_dispatcher_integration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_tier_dispatcher_integration", "eval_metric")
_emit_stores_embedding("p4", "test_healing_tier_dispatcher_integration", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_tier_dispatcher_integration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_tier_dispatcher_integration", "exec_snapshot_link")
from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore
from system_learning.ports.meta_prior_provider import (
    NeutralMetaPriorProvider,
)
from system_learning.ports.outcome_write_back_hook import (
    DefaultOutcomeWriteBackHook,
    NullOutcomeWriteBackHook,
)

_emit_records_execution_trace("p0", "evidence", "test_healing_tier_dispatcher_integration")
_emit_applies_guardrail("p0", "test_healing_tier_dispatcher_integration", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_tier_dispatcher_integration", "policy_binding")
_emit_snapshots_state("p0", "test_healing_tier_dispatcher_integration", "state_snapshot")
emit_replay_key("p0", "test_healing_tier_dispatcher_integration")
emit_determinism_digest("p0", "test_healing_tier_dispatcher_integration")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class MockMetaPriorProvider:
    """Mock provider with configurable priors."""

    def __init__(self, priors: dict[str, float]) -> None:
        self._priors = priors

    def get_prior(self, error_signature: str) -> float:
        return self._priors.get(error_signature, 0.50)


class MockHealingProviderInvoker:
    """Mock invoker that always succeeds."""

    def invoke_local(self, healing_input, decision, config, agent_name=""):
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord

        return InvocationRecord(
            tier=decision.tier,
            method_called="invoke_local",
            model_id="",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
        )


def test_dispatch_healing_phase2_integration() -> None:
    """dispatch_healing integrates Phase 2 components."""
    store = HealingSuccessRateStore()
    meta_prior_provider = MockMetaPriorProvider({"test_sig": 0.90})
    outcome_write_back_hook = DefaultOutcomeWriteBackHook(store)

    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        meta_prior_provider=meta_prior_provider,
        outcome_write_back_hook=outcome_write_back_hook,
    )

    # Should have used meta prior in routing
    assert decision.tier in HealingTier
    assert any("historical_success_rate=0.9000" in code for code in decision.reason_codes)

    # Should have recorded outcome in store
    assert store.get_counts().get("test_sig", 0) == 1

    # Should have successful invocation record
    assert record.tier == decision.tier


def test_dispatch_healing_without_phase2_hooks() -> None:
    """dispatch_healing works without Phase 2 hooks (backward compatibility)."""
    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    # Should not raise with None hooks
    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        meta_prior_provider=None,
        outcome_write_back_hook=None,
    )

    assert decision.tier in HealingTier
    assert record.tier == decision.tier


def test_dispatch_healing_null_hooks() -> None:
    """dispatch_healing works with null hooks."""
    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        meta_prior_provider=NeutralMetaPriorProvider(),
        outcome_write_back_hook=NullOutcomeWriteBackHook(),
    )

    assert decision.tier in HealingTier
    assert record.tier == decision.tier


def test_dispatch_healing_outcome_hook_failure() -> None:
    """dispatch_healing continues even if outcome hook fails."""
    failing_hook = MagicMock()
    failing_hook.on_outcome.side_effect = Exception("Hook failed")

    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    # Should not raise despite hook failure
    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        outcome_write_back_hook=failing_hook,
    )

    assert decision.tier in HealingTier
    assert record.tier == decision.tier
    failing_hook.on_outcome.assert_called_once()


def test_dispatch_healing_invocation_failure_still_calls_hook() -> None:
    """Outcome hook is called even when invocation fails."""

    class FailingInvoker:
        def invoke_local(self, healing_input, decision, config, agent_name=""):
            raise Exception("Invocation failed")

    store = HealingSuccessRateStore()
    outcome_hook = DefaultOutcomeWriteBackHook(store)

    config = HealingTierConfig()
    invoker = FailingInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    # Should raise invocation exception but still call hook
    with pytest.raises(Exception, match="Invocation failed"):
        dispatch_healing(
            healing_input,
            config,
            invoker=invoker,
            agent_name="test-agent",
            timestamp_utc=1234567890,
            outcome_write_back_hook=outcome_hook,
        )

    # Hook should have been called with success=False and record=None
    assert store.get_counts().get("test_sig", 0) == 1
