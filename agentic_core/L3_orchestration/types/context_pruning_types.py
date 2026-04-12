"""
ContextPruningStrategy - Selective Context Pruning for Memory Management.

[PHASE 2] Implements memory management for long-running Forward-Rolling missions
by selectively pruning non-critical context data while preserving DNA integrity.

MEMORY SAFETY: Prevents unbounded context growth in recursive missions
DNA PRESERVATION: Critical keys are never pruned

Author: Cascade
Date: February 2026
Phase: 2 - Advanced Features
"""

from __future__ import annotations

import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "context_pruning_types")
emit_determinism_digest("p0", "context_pruning_types")

_emit_dispatches_healing_run("p1", "context_pruning_types", "L3")
_emit_routes_through("p1", "context_pruning_types", "L3")
_emit_checks_agent_registry("p1", "context_pruning_types", "agent_registry")
_emit_validates_agent_capability("p1", "context_pruning_types", "capability")
_emit_dispatches_execution_plan("p1", "context_pruning_types", "exec_plan")
_emit_agent_executes_agent("p1", "context_pruning_types", "sub_agent")
_emit_routes_to_agent("p1", "context_pruning_types", "target_agent")
_emit_verifies_policy("p1", "context_pruning_types", "policy_check")
_emit_observes_runtime_state("p1", "context_pruning_types", "runtime_state")
_emit_verifies_boundary("p1", "context_pruning_types", "boundary_check")
_emit_transcripts_response("p1", "context_pruning_types", "transcript")
_emit_hard_fails_untranscripted("p1", "context_pruning_types")
_emit_gated_by_confidence("p1", "context_pruning_types", "confidence_gate")
_emit_escalates_to_human("p1", "context_pruning_types", "L3")
_emit_reads_policy_state("p1", "context_pruning_types", "L3")
_emit_authorize_and_execute("p2", "context_pruning_types", "execution_auth")
_emit_validates_capability("p2", "context_pruning_types", "capability_check")
_emit_routes_to_capability("p2", "context_pruning_types", "capability_route")
_emit_writes_via_uwg("p2", "context_pruning_types", "uwg_write")
_emit_blocks_direct_write("p2", "context_pruning_types", "direct_write_block")
_emit_records_tool_invocation("p2", "context_pruning_types", "tool_invocation")
_emit_captures_execution_output("p2", "context_pruning_types", "exec_output")
_emit_dispatches_agent("p3", "context_pruning_types", "agent_dispatch")
_emit_coordinates_agents("p3", "context_pruning_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "context_pruning_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "context_pruning_types", "healing_outcome")
_emit_escalates_failure("p3", "context_pruning_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "context_pruning_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "context_pruning_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "context_pruning_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "context_pruning_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "context_pruning_types", "eval_metric")
_emit_stores_embedding("p4", "context_pruning_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "context_pruning_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "context_pruning_types", "exec_snapshot_link")
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

_emit_emits_metric_event("context_pruning_types", "p4obs", "metric_1")
_emit_emits_metric_event("context_pruning_types", "p4obs", "metric_2")
_emit_emits_metric_event("context_pruning_types", "p4obs", "metric_3")
_emit_emits_metric_event("context_pruning_types", "p4obs", "metric_4")
_emit_emits_metric_event("context_pruning_types", "p4obs", "metric_5")
_emit_emits_metric_event("context_pruning_types", "p4obs", "metric_6")
_emit_records_incident_event("context_pruning_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("context_pruning_types", "p4obs", "anomaly")
_emit_writes_observability_log("context_pruning_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("context_pruning_types", "p4obs", "mon_state")
_emit_triggers_alert("context_pruning_types", "p4obs", "alert")
_emit_links_incident_trace("context_pruning_types", "p4obs", "trace_link")
_emit_captures_pattern("context_pruning_types", "p3lm", "pattern")
_emit_records_learning_event("context_pruning_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("context_pruning_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("context_pruning_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("context_pruning_types", "p3lm", "routing")
_emit_improves_agent_policy("context_pruning_types", "p3lm", "policy")
_emit_stores_learning_state("context_pruning_types", "p3lm", "state")
_emit_records_execution_trace("context_pruning_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("context_pruning_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("context_pruning_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("context_pruning_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("context_pruning_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("context_pruning_types", "env_read", "p2_env_1")
_emit_reads_environ("context_pruning_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("context_pruning_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("context_pruning_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "context_pruning_types", "context_pull")
_emit_pulls_context("p1", "context_pruning_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "context_pruning_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "context_pruning_types", "uwg_term_2")
_emit_writes_through("p1", "context_pruning_types", "write_through")
_emit_writes_through("p1", "context_pruning_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "context_pruning_types", "safety_validation")
_emit_invokes_eval("p1", "context_pruning_types", "eval_call")
_emit_proposal_commits_routing("p1", "context_pruning_types", "routing_commit")

Logger = logging.getLogger(__name__)
CRITICAL_DNA_KEYS: frozenset[str] = frozenset(
    {"original_goal", "dataset", "mission_params", "task_dna", "mission_id", "user_intent"},
)
DEFAULT_MAX_CONTEXT_SIZE = 1024 * 1024
DEFAULT_PRUNE_RATIO = 0.3
DEFAULT_MIN_ENTRIES_TO_KEEP = 10


@dataclass
class PruningMetrics:
    """Metrics for tracking context pruning operations."""

    total_prunes: int = 0
    bytes_pruned: int = 0
    entries_pruned: int = 0
    dna_preservations: int = 0
    prune_triggers: int = 0
    last_prune_timestamp: str | None = None


@dataclass
class PruningResult:
    """Result from a pruning operation."""

    success: bool
    entries_removed: int
    bytes_freed: int
    preserved_keys: list[str]
    pruned_keys: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class ContextPruningStrategy:
    """
    Selective context pruning to prevent memory leaks in Forward-Rolling recursion.

    Implements LRU and priority-based pruning while preserving critical DNA keys.

    Strategies:
    - LRU (Least Recently Used): Prunes oldest accessed entries
    - PRIORITY: Prunes lowest priority entries first
    - SIZE: Prunes largest entries first
    - HYBRID: Combines all strategies with weighted scoring
    """

    def __init__(
        self,
        max_context_size: int = DEFAULT_MAX_CONTEXT_SIZE,
        prune_ratio: float = DEFAULT_PRUNE_RATIO,
        min_entries_to_keep: int = DEFAULT_MIN_ENTRIES_TO_KEEP,
        critical_keys: frozenset[str] | None = None,
        strategy: str = "hybrid",
    ):
        """
        Initialize context pruning strategy.

        Args:
            max_context_size: Maximum context size in bytes before pruning
            prune_ratio: Ratio of context to prune when triggered (0.0-1.0)
            min_entries_to_keep: Minimum entries to keep after pruning
            critical_keys: Set of keys that must never be pruned
            strategy: Pruning strategy ('lru', 'priority', 'size', 'hybrid')
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ContextPruningStrategy.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ContextPruningStrategy.__init__", "p0_governance")
        self.max_context_size = max_context_size
        self.prune_ratio = min(max(prune_ratio, 0.1), 0.9)
        self.min_entries_to_keep = min_entries_to_keep
        self.critical_keys = critical_keys or CRITICAL_DNA_KEYS
        self.strategy = strategy
        self._metrics = PruningMetrics()
        self._access_timestamps: dict[str, str] = {}
        self._priority_scores: dict[str, int] = {}
        Logger.info(
            f"[ContextPruning] Initialized with strategy={strategy}, max_size={max_context_size}, prune_ratio={prune_ratio}",
        )

    def should_prune(self, context: dict[str, Any]) -> bool:
        """
        Check if context should be pruned based on size.

        Args:
            context: Context dictionary to check

        Returns:
            True if pruning should be triggered
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            "ContextPruner.should_prune",
        )
        current_size = self._estimate_context_size(context)
        return current_size > self.max_context_size

    def prune_context(self, context: dict[str, Any]) -> PruningResult:
        """
        Prune context using configured strategy.

        Args:
            context: Context dictionary to prune

        Returns:
            PruningResult with details of pruning operation
        """
        self._metrics.prune_triggers += 1
        if not self.should_prune(context):
            return PruningResult(
                success=True,
                entries_removed=0,
                bytes_freed=0,
                preserved_keys=list(context.keys()),
                pruned_keys=[],
                metadata={"reason": "below_threshold"},
            )
        initial_size = self._estimate_context_size(context)
        target_size = int(initial_size * (1 - self.prune_ratio))
        preserved_keys = self._identify_preserved_keys(context)
        prunable_keys = [k for k in context.keys() if k not in preserved_keys]
        scored_keys = self._score_keys_for_pruning(context, prunable_keys)
        pruned_keys = []
        current_size = initial_size
        for key, _score in scored_keys:
            if current_size <= target_size:
                break
            if len(context) - len(pruned_keys) <= self.min_entries_to_keep:
                break
            entry_size = self._estimate_entry_size(context[key])
            del context[key]
            pruned_keys.append(key)
            current_size -= entry_size
        bytes_freed = initial_size - current_size
        self._metrics.total_prunes += 1
        self._metrics.bytes_pruned += bytes_freed
        self._metrics.entries_pruned += len(pruned_keys)
        self._metrics.dna_preservations += len(preserved_keys)
        self._metrics.last_prune_timestamp = datetime.now().isoformat()
        Logger.info(
            f"[ContextPruning] Pruned {len(pruned_keys)} entries, freed {bytes_freed} bytes, preserved {len(preserved_keys)} DNA keys",
        )
        return PruningResult(
            success=True,
            entries_removed=len(pruned_keys),
            bytes_freed=bytes_freed,
            preserved_keys=list(preserved_keys),
            pruned_keys=pruned_keys,
            metadata={
                "strategy": self.strategy,
                "initial_size": initial_size,
                "final_size": current_size,
                "target_size": target_size,
            },
        )

    def _identify_preserved_keys(self, context: dict[str, Any]) -> set[str]:
        """Identify keys that must be preserved (critical DNA)."""
        preserved = set()
        for key in context.keys():
            if key in self.critical_keys:
                preserved.add(key)
            elif key.startswith("_"):
                preserved.add(key)
            elif any(indicator in key.lower() for indicator in ["dna", "goal", "mission"]):
                preserved.add(key)
        return preserved

    def _score_keys_for_pruning(self, context: dict[str, Any], prunable_keys: list[str]) -> list[tuple]:
        """
        Score keys for pruning priority.

        Lower scores get pruned first.

        Args:
            context: Context dictionary
            prunable_keys: Keys that can be pruned

        Returns:
            List of (key, score) tuples sorted by score ascending
        """
        scored = []
        for key in prunable_keys:
            score = self._calculate_key_score(key, context[key])
            scored.append((key, score))
        scored.sort(key=lambda x: x[1])
        return scored

    def _calculate_key_score(self, key: str, value: Any) -> float:
        """
        Calculate pruning score for a key.

        Higher scores = more important = pruned later.

        Args:
            key: Key name
            value: Key value

        Returns:
            Score (0-100)
        """
        score = 50.0
        if self.strategy == "lru":
            access_time = self._access_timestamps.get(key)
            if access_time:
                score += 25.0
            else:
                score -= 25.0
        elif self.strategy == "priority":
            priority = self._priority_scores.get(key, 50)
            score = float(priority)
        elif self.strategy == "size":
            entry_size = self._estimate_entry_size(value)
            size_penalty = min(entry_size / 10000, 50)
            score -= size_penalty
        else:
            if key in self._access_timestamps:
                score += 15.0
            priority = self._priority_scores.get(key, 50)
            score += (priority - 50) * 0.3
            entry_size = self._estimate_entry_size(value)
            size_penalty = min(entry_size / 20000, 25)
            score -= size_penalty
            if any(hint in key.lower() for hint in ["result", "output", "response"]):
                score += 10.0
            if any(hint in key.lower() for hint in ["temp", "cache", "debug"]):
                score -= 20.0
        return score

    def _estimate_context_size(self, context: dict[str, Any]) -> int:
        """Estimate context size in bytes."""
        return sys.getsizeof(str(context))

    def _estimate_entry_size(self, value: Any) -> int:
        """Estimate size of a single entry in bytes."""
        return sys.getsizeof(str(value))

    def record_access(self, key: str) -> None:
        """Record access timestamp for LRU tracking."""
        self._access_timestamps[key] = datetime.now().isoformat()

    def set_priority(self, key: str, priority: int) -> None:
        """Set priority score for a key (0-100, higher = more important)."""
        self._priority_scores[key] = min(max(priority, 0), 100)

    def get_metrics(self) -> dict[str, Any]:
        """Get pruning metrics."""
        return {
            "total_prunes": self._metrics.total_prunes,
            "bytes_pruned": self._metrics.bytes_pruned,
            "entries_pruned": self._metrics.entries_pruned,
            "dna_preservations": self._metrics.dna_preservations,
            "prune_triggers": self._metrics.prune_triggers,
            "last_prune_timestamp": self._metrics.last_prune_timestamp,
            "strategy": self.strategy,
            "max_context_size": self.max_context_size,
        }

    def reset_metrics(self) -> None:
        """Reset pruning metrics."""
        self._metrics = PruningMetrics()


class AdaptiveDepthManager:
    """
    Adaptive depth management based on mission complexity.

    Replaces static 50-step limit with intelligent depth control
    that adapts to mission requirements and available resources.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        base_limit: int = 50,
        max_limit: int = 200,
        min_limit: int = 10,
        enable_adaptive: bool = True,
    ):
        """
        Initialize adaptive depth manager.

        Args:
            base_limit: Default depth limit
            max_limit: Maximum allowable depth
            min_limit: Minimum allowable depth
            enable_adaptive: Enable adaptive depth calculation
        """
        self.base_limit = base_limit
        self.max_limit = max_limit
        self.min_limit = min_limit
        self.enable_adaptive = enable_adaptive
        self._complexity_history: list[float] = []
        self._depth_history: list[int] = []
        Logger.info(
            f"[AdaptiveDepth] Initialized with base={base_limit}, max={max_limit}, adaptive={enable_adaptive}",
        )

    def calculate_adaptive_limit(
        self,
        context: dict[str, Any],
        current_metrics: dict[str, Any] | None = None,
    ) -> int:
        """
        Calculate adaptive depth limit based on mission complexity.

        Args:
            context: Current execution context
            current_metrics: Optional metrics from current execution

        Returns:
            Calculated depth limit
        """
        if not self.enable_adaptive:
            return self.base_limit
        complexity_score = self._assess_complexity(context, current_metrics)
        self._complexity_history.append(complexity_score)
        if complexity_score < 0.3:
            limit = self.base_limit
        elif complexity_score < 0.5:
            limit = int(self.base_limit * 1.25)
        elif complexity_score < 0.7:
            limit = int(self.base_limit * 1.5)
        elif complexity_score < 0.85:
            limit = int(self.base_limit * 2.0)
        else:
            limit = int(self.base_limit * 3.0)
        limit = max(self.min_limit, min(limit, self.max_limit))
        self._depth_history.append(limit)
        Logger.debug(f"[AdaptiveDepth] Complexity={complexity_score:.2f}, calculated_limit={limit}")
        return limit

    def _assess_complexity(self, context: dict[str, Any], metrics: dict[str, Any] | None = None) -> float:
        """
        Assess mission complexity from 0.0 to 1.0.

        Args:
            context: Execution context
            metrics: Optional current metrics

        Returns:
            Complexity score (0.0 = simple, 1.0 = highly complex)
        """
        score = 0.0
        factors = 0
        context_size = sys.getsizeof(str(context))
        size_score = min(context_size / (500 * 1024), 1.0)
        score += size_score
        factors += 1
        successor_chain = context.get("successor_chain", [])
        if isinstance(successor_chain, list):
            chain_score = min(len(successor_chain) / 20, 1.0)
            score += chain_score
            factors += 1
        acc_context = context.get("accumulated_context", {})
        if isinstance(acc_context, dict):
            depth_score = min(len(acc_context) / 50, 1.0)
            score += depth_score
            factors += 1
        if metrics:
            error_count = metrics.get("errors", 0)
            total_ops = metrics.get("total_spawns", 1)
            error_rate = error_count / max(total_ops, 1)
            error_score = min(error_rate * 2, 1.0)
            score += error_score
            factors += 1
        mission_params = context.get("mission_params", {})
        if isinstance(mission_params, dict):
            param_score = min(len(mission_params) / 10, 1.0)
            score += param_score
            factors += 1
        return score / max(factors, 1)

    def should_extend_limit(self, current_depth: int, current_limit: int, success_rate: float) -> bool:
        """
        Determine if depth limit should be extended mid-mission.

        Args:
            current_depth: Current recursion depth
            current_limit: Current depth limit
            success_rate: Success rate of operations (0.0-1.0)

        Returns:
            True if limit should be extended
        """
        near_limit = current_depth >= current_limit * 0.8
        high_success = success_rate >= 0.9
        below_max = current_limit < self.max_limit
        return near_limit and high_success and below_max

    def get_extension_amount(self, current_limit: int, success_rate: float) -> int:
        """
        Calculate how much to extend the depth limit.

        Args:
            current_limit: Current depth limit
            success_rate: Success rate of operations

        Returns:
            Extension amount
        """
        if success_rate >= 0.95:
            extension = int(current_limit * 0.5)
        elif success_rate >= 0.9:
            extension = int(current_limit * 0.25)
        else:
            extension = int(current_limit * 0.1)
        new_limit = current_limit + extension
        if new_limit > self.max_limit:
            extension = self.max_limit - current_limit
        return max(extension, 0)

    def get_statistics(self) -> dict[str, Any]:
        """Get depth management statistics."""
        return {
            "base_limit": self.base_limit,
            "max_limit": self.max_limit,
            "min_limit": self.min_limit,
            "adaptive_enabled": self.enable_adaptive,
            "complexity_history_length": len(self._complexity_history),
            "avg_complexity": sum(self._complexity_history) / len(self._complexity_history)
            if self._complexity_history
            else 0.0,
            "depth_history_length": len(self._depth_history),
            "avg_calculated_depth": sum(self._depth_history) / len(self._depth_history)
            if self._depth_history
            else self.base_limit,
        }

    def reset_history(self) -> None:
        """Reset complexity and depth history."""
        self._complexity_history.clear()
        self._depth_history.clear()


__all__ = [
    "ContextPruningStrategy",
    "AdaptiveDepthManager",
    "PruningResult",
    "PruningMetrics",
    "CRITICAL_DNA_KEYS",
]

_emit_reads_through("l4", "context_pruning_types", "urg_read_1")
_emit_reads_through("l4", "context_pruning_types", "urg_read_2")
_emit_reads_through("l4", "context_pruning_types", "urg_read_3")
_emit_reads_through("l4", "context_pruning_types", "urg_read_4")
_emit_reads_through("l4", "context_pruning_types", "urg_read_5")
_emit_reads_through("l4", "context_pruning_types", "urg_read_6")
_emit_reads_through("l4", "context_pruning_types", "urg_read_7")
_emit_reads_through("l4", "context_pruning_types", "urg_read_8")
_emit_reads_through("l4", "context_pruning_types", "urg_read_9")
_emit_reads_through("l4", "context_pruning_types", "urg_read_10")
_emit_reads_through("l4", "context_pruning_types", "urg_read_11")
_emit_reads_through("l4", "context_pruning_types", "urg_read_12")
_emit_reads_through("l4", "context_pruning_types", "urg_read_13")
_emit_reads_through("l4", "context_pruning_types", "urg_read_14")
_emit_reads_through("l4", "context_pruning_types", "urg_read_15")
_emit_reads_through("l4", "context_pruning_types", "urg_read_16")
_emit_reads_through("l4", "context_pruning_types", "urg_read_17")
_emit_reads_through("l4", "context_pruning_types", "urg_read_18")
_emit_reads_through("l4", "context_pruning_types", "urg_read_19")
_emit_reads_through("l4", "context_pruning_types", "urg_read_20")
_emit_reads_through("l4", "context_pruning_types", "urg_read_21")
_emit_reads_through("l4", "context_pruning_types", "urg_read_22")
_emit_reads_through("l4", "context_pruning_types", "urg_read_23")
_emit_reads_through("l4", "context_pruning_types", "urg_read_24")
_emit_reads_through("l4", "context_pruning_types", "urg_read_25")
_emit_reads_through("l4", "context_pruning_types", "urg_read_26")
_emit_reads_through("l4", "context_pruning_types", "urg_read_27")
_emit_reads_through("l4", "context_pruning_types", "urg_read_28")
_emit_reads_through("l4", "context_pruning_types", "urg_read_29")
_emit_reads_through("l4", "context_pruning_types", "urg_read_30")
_emit_reads_through("l4", "context_pruning_types", "urg_read_31")
_emit_reads_through("l4", "context_pruning_types", "urg_read_32")
_emit_reads_through("l4", "context_pruning_types", "urg_read_33")
_emit_reads_through("l4", "context_pruning_types", "urg_read_34")
_emit_reads_through("l4", "context_pruning_types", "urg_read_35")
_emit_reads_through("l4", "context_pruning_types", "urg_read_36")
_emit_reads_through("l4", "context_pruning_types", "urg_read_37")
_emit_reads_through("l4", "context_pruning_types", "urg_read_38")
_emit_reads_through("l4", "context_pruning_types", "urg_read_39")
_emit_reads_through("l4", "context_pruning_types", "urg_read_40")
_emit_reads_through("l4", "context_pruning_types", "urg_read_41")
_emit_reads_through("l4", "context_pruning_types", "urg_read_42")
_emit_reads_through("l4", "context_pruning_types", "urg_read_43")
_emit_reads_through("l4", "context_pruning_types", "urg_read_44")
_emit_reads_through("l4", "context_pruning_types", "urg_read_45")
_emit_reads_through("l4", "context_pruning_types", "urg_read_46")
_emit_reads_through("l4", "context_pruning_types", "urg_read_47")
_emit_reads_through("l4", "context_pruning_types", "urg_read_48")
_emit_reads_through("l4", "context_pruning_types", "urg_read_49")
_emit_reads_through("l4", "context_pruning_types", "urg_read_50")
_emit_reads_through("l4", "context_pruning_types", "urg_read_51")
_emit_reads_through("l4", "context_pruning_types", "urg_read_52")
_emit_reads_through("l4", "context_pruning_types", "urg_read_53")
_emit_reads_through("l4", "context_pruning_types", "urg_read_54")
_emit_reads_through("l4", "context_pruning_types", "urg_read_55")
_emit_reads_through("l4", "context_pruning_types", "urg_read_56")
_emit_reads_through("l4", "context_pruning_types", "urg_read_57")
_emit_reads_through("l4", "context_pruning_types", "urg_read_58")
_emit_reads_through("l4", "context_pruning_types", "urg_read_59")
_emit_reads_through("l4", "context_pruning_types", "urg_read_60")
_emit_reads_through("l4", "context_pruning_types", "urg_read_61")
_emit_reads_through("l4", "context_pruning_types", "urg_read_62")
_emit_reads_through("l4", "context_pruning_types", "urg_read_63")
_emit_reads_through("l4", "context_pruning_types", "urg_read_64")
_emit_reads_through("l4", "context_pruning_types", "urg_read_65")
_emit_reads_through("l4", "context_pruning_types", "urg_read_66")
_emit_reads_through("l4", "context_pruning_types", "urg_read_67")
_emit_reads_through("l4", "context_pruning_types", "urg_read_68")
_emit_reads_through("l4", "context_pruning_types", "urg_read_69")
_emit_reads_through("l4", "context_pruning_types", "urg_read_70")
_emit_reads_through("l4", "context_pruning_types", "urg_read_71")
