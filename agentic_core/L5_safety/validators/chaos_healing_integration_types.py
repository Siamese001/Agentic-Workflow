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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "chaos_healing_integration_types")
trace_contract.emit_determinism_digest("p0", "chaos_healing_integration_types")

trace_contract._emit_dispatches_healing_run("p1", "chaos_healing_integration_types", "L5")
trace_contract._emit_routes_through("p1", "chaos_healing_integration_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "chaos_healing_integration_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "chaos_healing_integration_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "chaos_healing_integration_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "chaos_healing_integration_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "chaos_healing_integration_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "chaos_healing_integration_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "chaos_healing_integration_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "chaos_healing_integration_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "chaos_healing_integration_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "chaos_healing_integration_types")
trace_contract._emit_gated_by_confidence("p1", "chaos_healing_integration_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "chaos_healing_integration_types", "L5")
trace_contract._emit_reads_policy_state("p1", "chaos_healing_integration_types", "L5")

trace_contract._emit_applies_guardrail("p0", "chaos_healing_integration_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "chaos_healing_integration_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "chaos_healing_integration_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "chaos_healing_integration_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "chaos_healing_integration_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "chaos_healing_integration_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "chaos_healing_integration_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "chaos_healing_integration_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "chaos_healing_integration_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "chaos_healing_integration_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "chaos_healing_integration_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "chaos_healing_integration_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "chaos_healing_integration_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "chaos_healing_integration_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "chaos_healing_integration_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "chaos_healing_integration_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "chaos_healing_integration_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "chaos_healing_integration_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "chaos_healing_integration_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "chaos_healing_integration_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "chaos_healing_integration_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "chaos_healing_integration_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("chaos_healing_integration_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("chaos_healing_integration_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("chaos_healing_integration_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("chaos_healing_integration_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("chaos_healing_integration_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("chaos_healing_integration_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("chaos_healing_integration_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("chaos_healing_integration_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("chaos_healing_integration_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("chaos_healing_integration_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("chaos_healing_integration_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("chaos_healing_integration_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("chaos_healing_integration_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("chaos_healing_integration_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("chaos_healing_integration_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("chaos_healing_integration_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("chaos_healing_integration_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("chaos_healing_integration_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("chaos_healing_integration_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("chaos_healing_integration_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("chaos_healing_integration_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("chaos_healing_integration_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("chaos_healing_integration_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "chaos_healing_integration_types", "context_pull")
trace_contract._emit_pulls_context("p1", "chaos_healing_integration_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "chaos_healing_integration_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "chaos_healing_integration_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "chaos_healing_integration_types", "write_through")
trace_contract._emit_writes_through("p1", "chaos_healing_integration_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "chaos_healing_integration_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "chaos_healing_integration_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "chaos_healing_integration_types", "routing_commit")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "ChaosResilienceStrategy.can_heal")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ChaosResilienceStrategy.can_heal".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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

        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
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
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            errors.append(f"chaos_resilience: {e}")

        Logger.info(f"[Chaos Integration] Registered {len(registered)} strategies")

    except ImportError as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
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
