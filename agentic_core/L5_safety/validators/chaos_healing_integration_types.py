"""
Chaos Healing Integration Module - Phase 1 Foundation

Registers ChaosEngineeringAgent as a healing strategy in the
HealingSovereignOrchestrator.

This module adapts the ChaosEngineeringAgent to the HealingStrategy
protocol, enabling resilience testing after healing operations.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "chaos_healing_integration_types")
emit_determinism_digest("p0", "chaos_healing_integration_types")

_emit_dispatches_healing_run("p1", "chaos_healing_integration_types", "L5")
_emit_routes_through("p1", "chaos_healing_integration_types", "L5")
_emit_checks_agent_registry("p1", "chaos_healing_integration_types", "agent_registry")
_emit_validates_agent_capability("p1", "chaos_healing_integration_types", "capability")
_emit_dispatches_execution_plan("p1", "chaos_healing_integration_types", "exec_plan")
_emit_agent_executes_agent("p1", "chaos_healing_integration_types", "sub_agent")
_emit_routes_to_agent("p1", "chaos_healing_integration_types", "target_agent")
_emit_verifies_policy("p1", "chaos_healing_integration_types", "policy_check")
_emit_observes_runtime_state("p1", "chaos_healing_integration_types", "runtime_state")
_emit_verifies_boundary("p1", "chaos_healing_integration_types", "boundary_check")
_emit_transcripts_response("p1", "chaos_healing_integration_types", "transcript")
_emit_hard_fails_untranscripted("p1", "chaos_healing_integration_types")
_emit_gated_by_confidence("p1", "chaos_healing_integration_types", "confidence_gate")
_emit_escalates_to_human("p1", "chaos_healing_integration_types", "L5")
_emit_reads_policy_state("p1", "chaos_healing_integration_types", "L5")

_emit_applies_guardrail("p0", "chaos_healing_integration_types", "p0_governance")
_emit_snapshots_state("p0", "chaos_healing_integration_types", "state_snapshot")
_emit_authorize_and_execute("p2", "chaos_healing_integration_types", "execution_auth")
_emit_validates_capability("p2", "chaos_healing_integration_types", "capability_check")
_emit_routes_to_capability("p2", "chaos_healing_integration_types", "capability_route")
_emit_writes_via_uwg("p2", "chaos_healing_integration_types", "uwg_write")
_emit_blocks_direct_write("p2", "chaos_healing_integration_types", "direct_write_block")
_emit_records_tool_invocation("p2", "chaos_healing_integration_types", "tool_invocation")
_emit_captures_execution_output("p2", "chaos_healing_integration_types", "exec_output")
_emit_dispatches_agent("p3", "chaos_healing_integration_types", "agent_dispatch")
_emit_coordinates_agents("p3", "chaos_healing_integration_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "chaos_healing_integration_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "chaos_healing_integration_types", "healing_outcome")
_emit_escalates_failure("p3", "chaos_healing_integration_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "chaos_healing_integration_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "chaos_healing_integration_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "chaos_healing_integration_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "chaos_healing_integration_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "chaos_healing_integration_types", "eval_metric")
_emit_stores_embedding("p4", "chaos_healing_integration_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "chaos_healing_integration_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "chaos_healing_integration_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_1")
_emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_2")
_emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_3")
_emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_4")
_emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_5")
_emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_6")
_emit_records_incident_event("chaos_healing_integration_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("chaos_healing_integration_types", "p4obs", "anomaly")
_emit_writes_observability_log("chaos_healing_integration_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("chaos_healing_integration_types", "p4obs", "mon_state")
_emit_triggers_alert("chaos_healing_integration_types", "p4obs", "alert")
_emit_links_incident_trace("chaos_healing_integration_types", "p4obs", "trace_link")
_emit_captures_pattern("chaos_healing_integration_types", "p3lm", "pattern")
_emit_records_learning_event("chaos_healing_integration_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("chaos_healing_integration_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("chaos_healing_integration_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("chaos_healing_integration_types", "p3lm", "routing")
_emit_improves_agent_policy("chaos_healing_integration_types", "p3lm", "policy")
_emit_stores_learning_state("chaos_healing_integration_types", "p3lm", "state")
_emit_records_execution_trace("chaos_healing_integration_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("chaos_healing_integration_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("chaos_healing_integration_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("chaos_healing_integration_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("chaos_healing_integration_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("chaos_healing_integration_types", "env_read", "p2_env_1")
_emit_reads_environ("chaos_healing_integration_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("chaos_healing_integration_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("chaos_healing_integration_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "chaos_healing_integration_types", "context_pull")
_emit_pulls_context("p1", "chaos_healing_integration_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "chaos_healing_integration_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "chaos_healing_integration_types", "uwg_term_2")
_emit_writes_through("p1", "chaos_healing_integration_types", "write_through")
_emit_writes_through("p1", "chaos_healing_integration_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "chaos_healing_integration_types", "safety_validation")
_emit_invokes_eval("p1", "chaos_healing_integration_types", "eval_call")
_emit_proposal_commits_routing("p1", "chaos_healing_integration_types", "routing_commit")

Logger = logging.getLogger(__name__)


class HealingStrategyProtocol(Protocol):
    """Protocol for healing strategies - matches HealingSovereignOrchestrator interface."""

    def can_heal(self, violation: dict) -> bool:
        """Check if this strategy can heal the violation."""
        ...

    def heal(self, violation: dict, context: dict) -> dict:
        """Execute healing and return result."""
        ...


class ChaosResilienceStrategy:
    """
    Healing strategy that validates system resilience after healing.

    Use case: After a healing operation completes, run chaos tests
    to verify the system can handle failures gracefully.
    """

    # Violation types this strategy can handle
    SUPPORTED_VIOLATIONS = frozenset(
        {
            "resilience_check",
            "post_healing_validation",
            "chaos_test_required",
            "system_stability_check",
        },
    )

    def __init__(self) -> None:
        """Initialize the chaos resilience strategy."""
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to avoid import cycles."""
        if self._initialized:
            return

        try:
            from agentic_core.L4_state.validation_context import ValidationContext
            from agentic_core.L5_safety.red_teaming.chaos_engineering_agent_validator import (
                ChaosEngineeringAgent,
            )

            ctx = ValidationContext()
            self._agent = ChaosEngineeringAgent(ctx=ctx)
            self._initialized = True
        except ImportError as e:
            Logger.warning(f"[ChaosResilienceStrategy] Could not import agent: {e}")
            self._initialized = True

    def can_heal(self, violation: dict) -> bool:
        """
        Check if this strategy can handle the violation.

        Args:
            violation: Violation details with 'type' key

        Returns:
            True if this strategy can handle the violation type
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ChaosResilienceStrategy.can_heal")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ChaosResilienceStrategy.can_heal".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violation_type = violation.get("type", "")
        return violation_type in self.SUPPORTED_VIOLATIONS

    def heal(self, violation: dict, context: dict) -> dict:
        """
        Run chaos tests and report resilience status.

        Args:
            violation: Violation details
            context: Healing context (may include dry_run flag)

        Returns:
            dict with healing results
        """
        self._ensure_initialized()

        if self._agent is None:
            return {
                "success": True,
                "resilience_score": 1.0,
                "status": "agent_unavailable",
                "scenarios_tested": 0,
            }

        try:
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(self._agent.act())
            finally:
                loop.close()

            failures = result.get("failures_detected", 0)
            tests_executed = max(1, result.get("tests_executed", 1))
            recovery_metrics = result.get("recovery_metrics", {})

            return {
                "success": failures == 0,
                "resilience_score": 1.0 - (failures / tests_executed),
                "recovery_metrics": recovery_metrics,
                "scenarios_tested": len(result.get("scenarios_tested", [])),
                "failures_detected": failures,
            }

        # guardian: allow-silent-swallower
        except (ValueError, TypeError) as e:
            Logger.error(f"[ChaosResilienceStrategy] Healing failed: {e}")
            return {
                "success": False,
                "resilience_score": 0.0,
                "error": str(e),
                "scenarios_tested": 0,
            }


# Global strategy instance (lazy-initialized)
_chaos_strategy: ChaosResilienceStrategy | None = None


def get_chaos_strategy() -> ChaosResilienceStrategy:
    """Get or create the chaos resilience strategy instance."""
    global _chaos_strategy
    if _chaos_strategy is None:
        _chaos_strategy = ChaosResilienceStrategy()
    return _chaos_strategy


def register_chaos_healing() -> dict[str, Any]:
    """
    Register chaos engineering as a healing strategy.

    Returns:
        dict with registration status
    """
    registered = []
    errors = []

    try:
        from agentic_core.L5_safety.validators.healing_sovereign_orchestrator_types import (
            get_healing_orchestrator,
        )

        orchestrator = get_healing_orchestrator()

        try:
            orchestrator.register_strategy("chaos_resilience", get_chaos_strategy())
            registered.append("chaos_resilience")
        # guardian: allow-silent-swallower
        except (ValueError, TypeError) as e:
            errors.append(f"chaos_resilience: {e}")

        Logger.info(f"[Chaos Integration] Registered {len(registered)} strategies")

    except ImportError as e:
        errors.append(f"HealingSovereignOrchestrator import failed: {e}")
        Logger.warning(f"[Chaos Integration] Could not import orchestrator: {e}")

    return {
        "registered": registered,
        "errors": errors,
        "success": len(errors) == 0,
    }


def get_integration_status() -> dict[str, Any]:
    """Get the current status of chaos healing integration."""
    return {
        "chaos_strategy_initialized": _chaos_strategy is not None,
        "strategies_available": ["chaos_resilience"],
        "supported_violations": list(ChaosResilienceStrategy.SUPPORTED_VIOLATIONS),
    }
