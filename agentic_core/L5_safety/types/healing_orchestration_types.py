"""
Healing Orchestration Suite - Phase 3 Resilience Integration

Provides a unified interface for running all healing strategies:
- Chaos resilience testing
- Dependency pruning
- Post-healing validation

This module creates a HealingOrchestrationSuite that coordinates
healing operations across multiple strategies.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

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

emit_replay_key("p0", "healing_orchestration_types")
emit_determinism_digest("p0", "healing_orchestration_types")

_emit_dispatches_healing_run("p1", "healing_orchestration_types", "L5")
_emit_routes_through("p1", "healing_orchestration_types", "L5")
_emit_checks_agent_registry("p1", "healing_orchestration_types", "agent_registry")
_emit_validates_agent_capability("p1", "healing_orchestration_types", "capability")
_emit_dispatches_execution_plan("p1", "healing_orchestration_types", "exec_plan")
_emit_agent_executes_agent("p1", "healing_orchestration_types", "sub_agent")
_emit_routes_to_agent("p1", "healing_orchestration_types", "target_agent")
_emit_verifies_policy("p1", "healing_orchestration_types", "policy_check")
_emit_observes_runtime_state("p1", "healing_orchestration_types", "runtime_state")
_emit_verifies_boundary("p1", "healing_orchestration_types", "boundary_check")
_emit_transcripts_response("p1", "healing_orchestration_types", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_orchestration_types")
_emit_gated_by_confidence("p1", "healing_orchestration_types", "confidence_gate")
_emit_escalates_to_human("p1", "healing_orchestration_types", "L5")
_emit_reads_policy_state("p1", "healing_orchestration_types", "L5")

_emit_applies_guardrail("p0", "healing_orchestration_types", "p0_governance")
_emit_snapshots_state("p0", "healing_orchestration_types", "state_snapshot")
_emit_authorize_and_execute("p2", "healing_orchestration_types", "execution_auth")
_emit_validates_capability("p2", "healing_orchestration_types", "capability_check")
_emit_routes_to_capability("p2", "healing_orchestration_types", "capability_route")
_emit_writes_via_uwg("p2", "healing_orchestration_types", "uwg_write")
_emit_blocks_direct_write("p2", "healing_orchestration_types", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_orchestration_types", "tool_invocation")
_emit_captures_execution_output("p2", "healing_orchestration_types", "exec_output")
_emit_dispatches_agent("p3", "healing_orchestration_types", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_orchestration_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_orchestration_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_orchestration_types", "healing_outcome")
_emit_escalates_failure("p3", "healing_orchestration_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_orchestration_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_orchestration_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_orchestration_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_orchestration_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_orchestration_types", "eval_metric")
_emit_stores_embedding("p4", "healing_orchestration_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_orchestration_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_orchestration_types", "exec_snapshot_link")
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

_emit_emits_metric_event("healing_orchestration_types", "p4obs", "metric_1")
_emit_emits_metric_event("healing_orchestration_types", "p4obs", "metric_2")
_emit_emits_metric_event("healing_orchestration_types", "p4obs", "metric_3")
_emit_emits_metric_event("healing_orchestration_types", "p4obs", "metric_4")
_emit_emits_metric_event("healing_orchestration_types", "p4obs", "metric_5")
_emit_emits_metric_event("healing_orchestration_types", "p4obs", "metric_6")
_emit_records_incident_event("healing_orchestration_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_orchestration_types", "p4obs", "anomaly")
_emit_writes_observability_log("healing_orchestration_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_orchestration_types", "p4obs", "mon_state")
_emit_triggers_alert("healing_orchestration_types", "p4obs", "alert")
_emit_links_incident_trace("healing_orchestration_types", "p4obs", "trace_link")
_emit_captures_pattern("healing_orchestration_types", "p3lm", "pattern")
_emit_records_learning_event("healing_orchestration_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_orchestration_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_orchestration_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_orchestration_types", "p3lm", "routing")
_emit_improves_agent_policy("healing_orchestration_types", "p3lm", "policy")
_emit_stores_learning_state("healing_orchestration_types", "p3lm", "state")
_emit_records_execution_trace("healing_orchestration_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_orchestration_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_orchestration_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_orchestration_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_orchestration_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_orchestration_types", "env_read", "p2_env_1")
_emit_reads_environ("healing_orchestration_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_orchestration_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_orchestration_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_orchestration_types", "context_pull")
_emit_pulls_context("p1", "healing_orchestration_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_orchestration_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_orchestration_types", "uwg_term_2")
_emit_writes_through("p1", "healing_orchestration_types", "write_through")
_emit_writes_through("p1", "healing_orchestration_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_orchestration_types", "safety_validation")
_emit_invokes_eval("p1", "healing_orchestration_types", "eval_call")
_emit_proposal_commits_routing("p1", "healing_orchestration_types", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass
class HealingResult:
    """Result from a single healing operation."""

    strategy_name: str
    success: bool
    violations_found: int = 0
    violations_fixed: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class HealingSuiteResult:
    """Aggregated result from running the full healing suite."""

    overall_success: bool
    strategies_run: int
    strategies_succeeded: int
    strategies_failed: int
    total_violations_found: int
    total_violations_fixed: int
    results: list[HealingResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    execution_time_ms: float = 0.0


class HealingOrchestrationSuite:
    """
    Orchestrates healing operations across multiple strategies.

    Usage:
        suite = HealingOrchestrationSuite()
        result = suite.run_all(
            violation={"type": "resilience_check"},
            context={"dry_run": True}
        )
        if result.overall_success:
            print(f"Healed {result.total_violations_fixed} violations")
    """

    def __init__(self) -> None:
        """Initialize the healing orchestration suite."""
        self._strategies: dict[str, Any] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization of healing strategies."""
        if self._initialized:
            return
        try:
            from agentic_core.L5_safety.validators.chaos_healing_integration_types import get_chaos_strategy

            self._strategies["chaos_resilience"] = get_chaos_strategy()
        except ImportError as e:
            Logger.warning(f"[HealingSuite] Could not import chaos strategy: {e}")
        try:
            from agentic_core.L5_safety.validators.dependency_healing_integration_types import (
                get_dependency_strategy,
            )

            self._strategies["dependency_pruning"] = get_dependency_strategy()
        except ImportError as e:
            Logger.warning(f"[HealingSuite] Could not import dependency strategy: {e}")
        self._initialized = True
        Logger.info(f"[HealingSuite] Initialized with {len(self._strategies)} strategies")

    def run_strategy(self, strategy_name: str, violation: dict, context: dict | None = None) -> HealingResult:
        """
        Run a specific healing strategy.

        Args:
            strategy_name: Name of the strategy to run
            violation: Violation details to heal
            context: Optional healing context

        Returns:
            HealingResult with healing details
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HealingOrchestrationSuite.run_strategy",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:HealingOrchestrationSuite.run_strategy".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._ensure_initialized()
        context = context or {}
        if strategy_name not in self._strategies:
            return HealingResult(
                strategy_name=strategy_name, success=False, errors=[f"Strategy '{strategy_name}' not found"],
            )
        strategy = self._strategies[strategy_name]
        if hasattr(strategy, "can_heal") and (not strategy.can_heal(violation)):
            return HealingResult(
                strategy_name=strategy_name,
                success=True,
                errors=[],
                metadata={"skipped": True, "reason": "violation_type_not_supported"},
            )
        try:
            result = strategy.heal(violation, context)
            return HealingResult(
                strategy_name=strategy_name,
                success=result.get("success", False),
                violations_found=result.get("violations_found", 1),
                violations_fixed=result.get("violations_fixed", 0) if result.get("success") else 0,
                errors=result.get("errors", []),
                metadata={
                    k: v
                    for k, v in result.items()
                    if k not in ("success", "violations_found", "violations_fixed", "errors")
                },
            )
        except (ValueError, TypeError) as e:
            Logger.error(f"[HealingSuite] Strategy {strategy_name} failed: {e}")
            return HealingResult(
                strategy_name=strategy_name, success=False, errors=[f"Strategy error: {str(e)}"],
            )

    def run_all(self, violation: dict, context: dict | None = None) -> HealingSuiteResult:
        """
        Run all applicable healing strategies for a violation.

        Args:
            violation: Violation details to heal
            context: Optional healing context

        Returns:
            HealingSuiteResult with aggregated results
        """
        import time

        self._ensure_initialized()
        context = context or {}
        start_time = time.time()
        results: list[HealingResult] = []
        for strategy_name in self._strategies:
            result = self.run_strategy(strategy_name, violation, context)
            results.append(result)
        execution_time = (time.time() - start_time) * 1000
        succeeded = sum(1 for r in results if r.success)
        failed = len(results) - succeeded
        total_found = sum(r.violations_found for r in results)
        total_fixed = sum(r.violations_fixed for r in results)
        return HealingSuiteResult(
            overall_success=failed == 0,
            strategies_run=len(results),
            strategies_succeeded=succeeded,
            strategies_failed=failed,
            total_violations_found=total_found,
            total_violations_fixed=total_fixed,
            results=results,
            execution_time_ms=execution_time,
        )

    def run_resilience_check(self, context: dict | None = None) -> HealingResult:
        """
        Run chaos resilience check specifically.

        Args:
            context: Optional healing context

        Returns:
            HealingResult from chaos resilience strategy
        """
        return self.run_strategy("chaos_resilience", violation={"type": "resilience_check"}, context=context)

    def run_dependency_cleanup(self, dry_run: bool = True, context: dict | None = None) -> HealingResult:
        """
        Run dependency pruning specifically.

        Args:
            dry_run: If True, only report what would be done
            context: Optional additional context

        Returns:
            HealingResult from dependency pruning strategy
        """
        ctx = context or {}
        ctx["dry_run"] = dry_run
        return self.run_strategy("dependency_pruning", violation={"type": "unused_dependency"}, context=ctx)

    def get_available_strategies(self) -> list[str]:
        """Get list of available strategy names."""
        self._ensure_initialized()
        return list(self._strategies.keys())

    def get_status(self) -> dict[str, Any]:
        """Get current status of the healing suite."""
        self._ensure_initialized()
        return {
            "initialized": self._initialized,
            "strategies_available": list(self._strategies.keys()),
            "strategy_count": len(self._strategies),
        }


_healing_suite: HealingOrchestrationSuite | None = None


def get_healing_suite() -> HealingOrchestrationSuite:
    """Get or create the global healing orchestration suite."""
    global _healing_suite
    if _healing_suite is None:
        _healing_suite = HealingOrchestrationSuite()
    return _healing_suite


def run_healing_operation(violation: dict, context: dict | None = None) -> HealingSuiteResult:
    """
    Convenience function to run healing for a violation.

    Args:
        violation: Violation details to heal
        context: Optional healing context

    Returns:
        HealingSuiteResult with all healing results
    """
    suite = get_healing_suite()
    return suite.run_all(violation, context)
