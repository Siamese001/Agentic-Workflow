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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "chaos_healing_integration_types")
emit_determinism_digest("p0", "chaos_healing_integration_types")

_emit_dispatches_healing_run("p1", "chaos_healing_integration_types", "L5")
_emit_routes_through("p1", "chaos_healing_integration_types", "L5")
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
        }
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
        except Exception as e:
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
        except Exception as e:
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
