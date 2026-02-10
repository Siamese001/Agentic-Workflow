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
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

Logger = logging.getLogger(__name__)

# Critical DNA keys that must NEVER be pruned
CRITICAL_DNA_KEYS: frozenset[str] = frozenset(
    {
        "original_goal",
        "dataset",
        "mission_params",
        "task_dna",
        "mission_id",
        "user_intent",
    },
)

# Default configuration
DEFAULT_MAX_CONTEXT_SIZE = 1024 * 1024  # 1MB
DEFAULT_PRUNE_RATIO = 0.3  # Prune 30% when triggered
# guardian: allow-magic-config
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
        self.max_context_size = max_context_size
        self.prune_ratio = min(max(prune_ratio, 0.1), 0.9)  # Clamp to 10-90%
        self.min_entries_to_keep = min_entries_to_keep
        self.critical_keys = critical_keys or CRITICAL_DNA_KEYS
        self.strategy = strategy
        self._metrics = PruningMetrics()
        self._access_timestamps: dict[str, str] = {}
        self._priority_scores: dict[str, int] = {}

        Logger.info(
            f"[ContextPruning] Initialized with strategy={strategy}, "
            f"max_size={max_context_size}, prune_ratio={prune_ratio}",
        )

    def should_prune(self, context: dict[str, Any]) -> bool:
        """
        Check if context should be pruned based on size.

        Args:
            context: Context dictionary to check

        Returns:
            True if pruning should be triggered
        """
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

        # Identify keys to preserve (critical DNA)
        preserved_keys = self._identify_preserved_keys(context)

        # Identify prunable keys
        prunable_keys = [k for k in context.keys() if k not in preserved_keys]

        # Score and sort keys for pruning
        scored_keys = self._score_keys_for_pruning(context, prunable_keys)

        # Prune until target size reached
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

        # Update metrics
        bytes_freed = initial_size - current_size
        self._metrics.total_prunes += 1
        self._metrics.bytes_pruned += bytes_freed
        self._metrics.entries_pruned += len(pruned_keys)
        self._metrics.dna_preservations += len(preserved_keys)
        self._metrics.last_prune_timestamp = datetime.now().isoformat()

        Logger.info(
            f"[ContextPruning] Pruned {len(pruned_keys)} entries, "
            f"freed {bytes_freed} bytes, preserved {len(preserved_keys)} DNA keys",
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
            # Check if key is critical
            if key in self.critical_keys:
                preserved.add(key)
            # Check if key starts with underscore (internal metadata)
            elif key.startswith("_"):
                preserved.add(key)
            # Check if key contains 'dna' or 'goal' (DNA indicators)
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

        # Sort by score ascending (lowest scores pruned first)
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
        score = 50.0  # Base score

        if self.strategy == "lru":
            # LRU: Older access = lower score
            access_time = self._access_timestamps.get(key)
            if access_time:
                # More recent = higher score
                score += 25.0
            else:
                score -= 25.0

        elif self.strategy == "priority":
            # Priority: Use explicit priority scores
            priority = self._priority_scores.get(key, 50)
            score = float(priority)

        elif self.strategy == "size":
            # Size: Larger entries = lower score (prune first)
            entry_size = self._estimate_entry_size(value)
            # Normalize to 0-50 range (larger = lower score)
            size_penalty = min(entry_size / 10000, 50)
            score -= size_penalty

        else:  # hybrid
            # Combine all factors
            # Access recency
            if key in self._access_timestamps:
                score += 15.0

            # Priority
            priority = self._priority_scores.get(key, 50)
            score += (priority - 50) * 0.3

            # Size penalty
            entry_size = self._estimate_entry_size(value)
            size_penalty = min(entry_size / 20000, 25)
            score -= size_penalty

            # Key name heuristics
            if any(hint in key.lower() for hint in ["result", "output", "response"]):
                score += 10.0  # Results are often important
            if any(hint in key.lower() for hint in ["temp", "cache", "debug"]):
                score -= 20.0  # Temporary data is less important

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
        # guardian: allow-magic-config
        base_limit: int = 50,
        # guardian: allow-magic-config
        max_limit: int = 200,
        # guardian: allow-magic-config
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

        # Scale depth limit based on complexity
        if complexity_score < 0.3:
            # Low complexity - use base limit
            limit = self.base_limit
        elif complexity_score < 0.5:
            # Medium-low complexity - slight increase
            limit = int(self.base_limit * 1.25)
        elif complexity_score < 0.7:
            # Medium complexity - moderate increase
            limit = int(self.base_limit * 1.5)
        elif complexity_score < 0.85:
            # Medium-high complexity - significant increase
            limit = int(self.base_limit * 2.0)
        else:
            # High complexity - maximum increase
            limit = int(self.base_limit * 3.0)

        # Clamp to allowed range
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

        # Factor 1: Context size
        context_size = sys.getsizeof(str(context))
        size_score = min(context_size / (500 * 1024), 1.0)  # Normalize to 500KB
        score += size_score
        factors += 1

        # Factor 2: Successor chain length
        successor_chain = context.get("successor_chain", [])
        if isinstance(successor_chain, list):
            chain_score = min(len(successor_chain) / 20, 1.0)  # Normalize to 20
            score += chain_score
            factors += 1

        # Factor 3: Accumulated context depth
        acc_context = context.get("accumulated_context", {})
        if isinstance(acc_context, dict):
            depth_score = min(len(acc_context) / 50, 1.0)  # Normalize to 50 keys
            score += depth_score
            factors += 1

        # Factor 4: Error rate from metrics
        if metrics:
            error_count = metrics.get("errors", 0)
            total_ops = metrics.get("total_spawns", 1)
            error_rate = error_count / max(total_ops, 1)
            error_score = min(error_rate * 2, 1.0)  # 50% error rate = 1.0
            score += error_score
            factors += 1

        # Factor 5: Mission parameters complexity
        mission_params = context.get("mission_params", {})
        if isinstance(mission_params, dict):
            param_score = min(len(mission_params) / 10, 1.0)
            score += param_score
            factors += 1

        # Calculate average complexity
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
        # Only extend if near limit and success rate is high
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
            extension = int(current_limit * 0.5)  # 50% extension
        elif success_rate >= 0.9:
            extension = int(current_limit * 0.25)  # 25% extension
        else:
            extension = int(current_limit * 0.1)  # 10% extension

        # Ensure we don't exceed max
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
            "avg_complexity": (
                sum(self._complexity_history) / len(self._complexity_history)
                if self._complexity_history
                else 0.0
            ),
            "depth_history_length": len(self._depth_history),
            "avg_calculated_depth": (
                sum(self._depth_history) / len(self._depth_history)
                if self._depth_history
                else self.base_limit
            ),
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
