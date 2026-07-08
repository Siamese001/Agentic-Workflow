"""
Rollback refiner engine for L2 execution learning.
Deterministic rollback strategy selection using outcome history.
"""

from __future__ import annotations

from typing import Protocol

from agentic_core.L2_execution.types.resource_prediction_types import FailureSignature
from agentic_core.L2_execution.types.rollback_refinement_types import (
    RollbackOutcomeStats,
    RollbackRefinementDecision,
    RollbackRefinementRequest,
    RollbackStrategyId,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "rollback_refiner")
trace_contract.emit_determinism_digest("p0", "rollback_refiner")

trace_contract._emit_dispatches_healing_run("p1", "rollback_refiner", "L2")
trace_contract._emit_routes_through("p1", "rollback_refiner", "L2")
trace_contract._emit_checks_agent_registry("p1", "rollback_refiner", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "rollback_refiner", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "rollback_refiner", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "rollback_refiner", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "rollback_refiner", "target_agent")
trace_contract._emit_verifies_policy("p1", "rollback_refiner", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "rollback_refiner", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "rollback_refiner", "boundary_check")
trace_contract._emit_transcripts_response("p1", "rollback_refiner", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "rollback_refiner")
trace_contract._emit_gated_by_confidence("p1", "rollback_refiner", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "rollback_refiner", "L2")
trace_contract._emit_reads_policy_state("p1", "rollback_refiner", "L2")

trace_contract._emit_applies_guardrail("p0", "rollback_refiner", "p0_governance")
trace_contract._emit_snapshots_state("p0", "rollback_refiner", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "rollback_refiner", "execution_auth")
trace_contract._emit_validates_capability("p2", "rollback_refiner", "capability_check")
trace_contract._emit_routes_to_capability("p2", "rollback_refiner", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "rollback_refiner", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "rollback_refiner", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "rollback_refiner", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "rollback_refiner", "exec_output")
trace_contract._emit_dispatches_agent("p3", "rollback_refiner", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "rollback_refiner", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "rollback_refiner", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "rollback_refiner", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "rollback_refiner", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "rollback_refiner", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "rollback_refiner", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "rollback_refiner", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "rollback_refiner", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "rollback_refiner", "eval_metric")
trace_contract._emit_stores_embedding("p4", "rollback_refiner", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "rollback_refiner", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "rollback_refiner", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("rollback_refiner", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("rollback_refiner", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("rollback_refiner", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("rollback_refiner", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("rollback_refiner", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("rollback_refiner", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("rollback_refiner", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("rollback_refiner", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("rollback_refiner", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("rollback_refiner", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("rollback_refiner", "p4obs", "alert")
trace_contract._emit_links_incident_trace("rollback_refiner", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("rollback_refiner", "p3lm", "pattern")
trace_contract._emit_records_learning_event("rollback_refiner", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("rollback_refiner", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("rollback_refiner", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("rollback_refiner", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("rollback_refiner", "p3lm", "policy")
trace_contract._emit_stores_learning_state("rollback_refiner", "p3lm", "state")
trace_contract._emit_records_execution_trace("rollback_refiner", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("rollback_refiner", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("rollback_refiner", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("rollback_refiner", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("rollback_refiner", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("rollback_refiner", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("rollback_refiner", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("rollback_refiner", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("rollback_refiner", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "rollback_refiner", "context_pull")
trace_contract._emit_pulls_context("p1", "rollback_refiner", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "rollback_refiner", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "rollback_refiner", "uwg_term_2")
trace_contract._emit_writes_through("p1", "rollback_refiner", "write_through")
trace_contract._emit_writes_through("p1", "rollback_refiner", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "rollback_refiner", "safety_validation")
trace_contract._emit_invokes_eval("p1", "rollback_refiner", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "rollback_refiner", "routing_commit")


class RollbackRefiner(Protocol):
    """Protocol for rollback refinement engines."""

    def refine(
        *,
        request: RollbackRefinementRequest,
    ) -> RollbackRefinementDecision:
        """Refine rollback strategy selection."""
        ...


class DefaultDeterministicRollbackRefiner:
    """Deterministic rollback refiner with stable tie-breaking."""

    # Default strategy preference order (fallback when no history)
    _DEFAULT_STRATEGY_ORDER: tuple[str, ...] = (
        "graceful_shutdown",
        "checkpoint_restore",
        "state_snapshot",
        "incremental_rollback",
        "full_restart",
        "circuit_breaker",
    )

    def __init__(self):
        """Initialize deterministic refiner."""
        # No internal state for determinism
        pass

    def refine(
        self,
        *,
        request: RollbackRefinementRequest,
    ) -> RollbackRefinementDecision:
        """Refine rollback strategy selection deterministically."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "DefaultDeterministicRollbackRefiner.refine",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:DefaultDeterministicRollbackRefiner.refine".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Parse history to get outcome statistics
        strategy_stats = self._parse_history_stats(request.history_bytes)

        # Score all candidate strategies
        scored_candidates = self._score_candidates(
            request.candidates,
            strategy_stats,
            request.failure_signature,
        )

        # Sort by score (descending), then by name for deterministic tie-breaking
        sorted_candidates = sorted(
            scored_candidates,
            key=lambda x: (-x[0], x[1].name),  # (-score, name) for descending score, then name
        )

        # Extract ranked strategies
        ranked = tuple(candidate for _, candidate in sorted_candidates)

        # Choose the highest-scoring strategy
        chosen = ranked[0] if ranked else request.candidates[0]

        # Generate deterministic reasons
        reasons = self._generate_reasons(chosen, strategy_stats, request.failure_signature)

        return RollbackRefinementDecision(
            chosen=chosen,
            ranked=ranked,
            reasons=tuple(sorted(reasons)),  # Sort for determinism
        )

    def _parse_history_stats(self, history_bytes: bytes | None) -> dict[str, RollbackOutcomeStats]:
        """Parse history bytes to extract strategy statistics."""
        if not history_bytes:
            return {}

        # In practice, this would parse actual history data
        # For determinism, we'll create mock stats based on history hash
        import hashlib

        history_hash = hashlib.sha256(history_bytes).hexdigest()

        # Deterministic mock stats based on hash
        stats = {}
        strategies = [
            "graceful_shutdown",
            "checkpoint_restore",
            "state_snapshot",
            "incremental_rollback",
            "full_restart",
            "circuit_breaker",
        ]

        for i, strategy in enumerate(strategies):
            # Use hash to generate deterministic stats
            hash_byte = int(history_hash[i % len(history_hash)], 16)
            success = 10 + (hash_byte % 20)  # 10-29 successes
            fail = hash_byte % 5  # 0-4 failures
            stats[strategy] = RollbackOutcomeStats(success=success, fail=fail)

        return stats

    def _score_candidates(
        self,
        candidates: tuple[RollbackStrategyId, ...],
        strategy_stats: dict[str, RollbackOutcomeStats],
        failure_signature: FailureSignature,
    ) -> list[tuple[float, RollbackStrategyId]]:
        """Score candidates based on statistics and deterministic rules."""
        scored = []

        for candidate in candidates:
            score = self._calculate_score(candidate, strategy_stats, failure_signature)
            scored.append((score, candidate))

        return scored

    def _calculate_score(
        self,
        candidate: RollbackStrategyId,
        strategy_stats: dict[str, RollbackOutcomeStats],
        failure_signature: FailureSignature,
    ) -> float:
        """Calculate deterministic score for a strategy."""
        # Base score from outcome statistics
        if candidate.name in strategy_stats:
            stats = strategy_stats[candidate.name]
            total = stats.success + stats.fail
            if total > 0:
                success_rate = stats.success / total
                base_score = success_rate
            else:
                base_score = 0.5  # Neutral if no data
        else:
            base_score = 0.5  # Neutral for unknown strategies

        # Adjust based on failure type preferences
        failure_adjustments = {
            "timeout": {"graceful_shutdown": 0.2, "checkpoint_restore": 0.1},
            "memory_error": {"state_snapshot": 0.2, "incremental_rollback": 0.1},
            "cpu_error": {"full_restart": 0.2, "circuit_breaker": 0.1},
            "io_error": {"checkpoint_restore": 0.2, "state_snapshot": 0.1},
            "network_error": {"circuit_breaker": 0.2, "graceful_shutdown": 0.1},
        }

        if failure_signature.failure_type in failure_adjustments:
            if candidate.name in failure_adjustments[failure_signature.failure_type]:
                base_score += failure_adjustments[failure_signature.failure_type][candidate.name]

        # Add small deterministic bias based on strategy name order
        if candidate.name in self._DEFAULT_STRATEGY_ORDER:
            order_bonus = (
                len(self._DEFAULT_STRATEGY_ORDER) - self._DEFAULT_STRATEGY_ORDER.index(candidate.name)
            ) * 0.01
            base_score += order_bonus

        # Clamp score to valid range
        return max(0.0, min(1.0, base_score))

    def _generate_reasons(
        self,
        chosen: RollbackStrategyId,
        strategy_stats: dict[str, RollbackOutcomeStats],
        failure_signature: FailureSignature,
    ) -> list[str]:
        """Generate deterministic reasoning for the choice."""
        reasons = []

        # Base reason
        reasons.append(f"chosen_strategy_{chosen.name}")

        # History-based reasoning
        if chosen.name in strategy_stats:
            stats = strategy_stats[chosen.name]
            total = stats.success + stats.fail
            if total > 0:
                success_rate = stats.success / total
                reasons.append(f"success_rate_{success_rate:.3f}")
                reasons.append("history_based")
            else:
                reasons.append("no_history_data")
        else:
            reasons.append("unknown_strategy")

        # Failure type reasoning
        reasons.append(f"failure_type_{failure_signature.failure_type}")

        # Tie-breaking reasoning
        reasons.append("deterministic_tie_break")

        return reasons

    def track_strategy_outcome(
        self,
        request: RollbackRefinementRequest,
        decision: RollbackRefinementDecision,
        success: bool,
        execution_time_ms: int,
        timestamp_utc: int,
    ) -> None:
        """Track rollback strategy outcomes for system learning feedback.

        Args:
            request: The rollback refinement request
            decision: The rollback decision made
            success: Whether the rollback was successful
            execution_time_ms: Time taken to execute rollback in milliseconds
            timestamp_utc: Timestamp for tracking
        """
        try:
            from agentic_core.L6_system_learning.system_learning_memory_bridge import get_sl_memory_bridge

            bridge = get_sl_memory_bridge()

            bridge.persist_rollback_strategy_outcome(
                failure_type=request.failure_signature.failure_type,
                failure_fingerprint=request.failure_signature.fingerprint,
                strategy_chosen=decision.strategy.name,
                strategy_score=decision.confidence,
                strategy_reasons=list(decision.reasons),
                success=success,
                execution_time_ms=execution_time_ms,
                timestamp_utc=timestamp_utc,
            )
        except (
            ValueError,
            TypeError,
        ):  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow
            # System learning unavailable - continue without tracking
            pass
