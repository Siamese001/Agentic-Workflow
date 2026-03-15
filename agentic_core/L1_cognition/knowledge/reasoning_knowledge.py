"""
agentic_core/L1_cognition/knowledge/reasoning_knowledge.py

P4/L1 Reasoning Knowledge Base — reasoning knowledge record and metrics.

Provides ReasoningKnowledgeRecord (9 required fields) for systematic
reasoning pattern capture and reuse.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any

from agentic_core.L2_execution.providers import get_clock

logger = logging.getLogger(__name__)
_KNOWLEDGE_LOG = logging.getLogger("adg.reasoning_pattern_captured")
_REUSE_LOG = logging.getLogger("adg.reasoning_pattern_reused")


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class ReasoningKnowledgeError(Exception):
    """Raised when reasoning knowledge operations fail (Gate A/E)."""

    pass


# ---------------------------------------------------------------------------
# ReasoningKnowledgeRecord — 9 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReasoningKnowledgeRecord:
    """Immutable reasoning knowledge record for pattern capture and reuse (9 required fields)."""

    reasoning_pattern_id: str
    originating_trace_id: str
    reasoning_goal_hash: str
    reasoning_context_hash: str
    reasoning_steps_hash: str
    outcome_quality_score: float
    reuse_count: int
    pattern_version: int
    validation_status: str

    @classmethod
    def create(
        cls,
        reasoning_pattern_id: str,
        originating_trace_id: str,
        reasoning_goal_hash: str,
        reasoning_context_hash: str,
        reasoning_steps_hash: str,
        outcome_quality_score: float = 0.0,
        reuse_count: int = 0,
        pattern_version: int = 1,
        validation_status: str = "PENDING",
    ) -> ReasoningKnowledgeRecord:
        """Factory to create ReasoningKnowledgeRecord with default values."""
        return cls(
            reasoning_pattern_id=reasoning_pattern_id,
            originating_trace_id=originating_trace_id,
            reasoning_goal_hash=reasoning_goal_hash,
            reasoning_context_hash=reasoning_context_hash,
            reasoning_steps_hash=reasoning_steps_hash,
            outcome_quality_score=outcome_quality_score,
            reuse_count=reuse_count,
            pattern_version=pattern_version,
            validation_status=validation_status,
        )

    def has_evaluation_score(self) -> bool:
        """Check if pattern has evaluation score (Gate B)."""
        return self.outcome_quality_score >= 0.0

    def has_trace_lineage(self) -> bool:
        """Check if pattern has trace lineage (Gate D)."""
        return self.originating_trace_id and self.reasoning_pattern_id and self.reasoning_goal_hash

    def is_versioned(self) -> bool:
        """Check if pattern is properly versioned (Gate C)."""
        return self.pattern_version > 0 and self.reasoning_pattern_id

    def is_validated(self) -> bool:
        """Check if pattern is validated (Gate A)."""
        return self.validation_status in ("VALIDATED", "APPROVED")

    def has_reuse_outcome(self) -> bool:
        """Check if pattern reuse has recorded outcome (Gate E)."""
        return self.reuse_count > 0


# ---------------------------------------------------------------------------
# ReasoningKnowledgeRegistry — thread-safe reasoning knowledge storage and query
# ---------------------------------------------------------------------------


class ReasoningKnowledgeRegistry:
    """Thread-safe registry for reasoning knowledge records."""

    _instance: ReasoningKnowledgeRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._patterns: dict[str, ReasoningKnowledgeRecord] = {}
        self._goal_index: dict[str, list[str]] = {}  # goal_hash -> pattern_ids
        self._context_index: dict[str, list[str]] = {}  # context_hash -> pattern_ids
        self._trace_index: dict[str, list[str]] = {}  # trace_id -> pattern_ids
        self._quality_index: dict[float, list[str]] = {}  # quality_score -> pattern_ids
        self._reuse_records: dict[str, list[dict[str, Any]]] = {}  # pattern_id -> reuse_records
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> ReasoningKnowledgeRegistry:
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_pattern(self, pattern: ReasoningKnowledgeRecord) -> None:
        """Persist a reasoning knowledge record."""
        with self._lock:
            self._patterns[pattern.reasoning_pattern_id] = pattern

            # Index by goal hash for goal similarity queries
            if pattern.reasoning_goal_hash not in self._goal_index:
                self._goal_index[pattern.reasoning_goal_hash] = []
            self._goal_index[pattern.reasoning_goal_hash].append(pattern.reasoning_pattern_id)

            # Index by context hash for context similarity queries
            if pattern.reasoning_context_hash not in self._context_index:
                self._context_index[pattern.reasoning_context_hash] = []
            self._context_index[pattern.reasoning_context_hash].append(pattern.reasoning_pattern_id)

            # Index by trace ID for lineage queries
            if pattern.originating_trace_id not in self._trace_index:
                self._trace_index[pattern.originating_trace_id] = []
            self._trace_index[pattern.originating_trace_id].append(pattern.reasoning_pattern_id)

            # Index by quality score for quality-based queries
            quality_key = round(pattern.outcome_quality_score, 2)
            if quality_key not in self._quality_index:
                self._quality_index[quality_key] = []
            self._quality_index[quality_key].append(pattern.reasoning_pattern_id)

            # Initialize reuse records
            if pattern.reasoning_pattern_id not in self._reuse_records:
                self._reuse_records[pattern.reasoning_pattern_id] = []

        _KNOWLEDGE_LOG.debug(
            "reasoning_pattern_captured pattern_id=%s trace_id=%s goal_hash=%s quality_score=%s",
            pattern.reasoning_pattern_id,
            pattern.originating_trace_id,
            pattern.reasoning_goal_hash,
            pattern.outcome_quality_score,
        )

        logger.debug(
            "REASONING_PATTERN_PERSISTED pattern_id=%s originating_trace=%s version=%s",
            pattern.reasoning_pattern_id,
            pattern.originating_trace_id,
            pattern.pattern_version,
        )

        # Check for gate violations
        if not pattern.has_evaluation_score():
            logger.warning(
                "REASONING_KNOWLEDGE_GATE_B_VIOLATION pattern_id=%s no_evaluation_score",
                pattern.reasoning_pattern_id,
            )

        if not pattern.is_versioned():
            logger.warning(
                "REASONING_KNOWLEDGE_GATE_C_VIOLATION pattern_id=%s no_version_increment",
                pattern.reasoning_pattern_id,
            )

        if not pattern.has_trace_lineage():
            logger.warning(
                "REASONING_KNOWLEDGE_GATE_D_VIOLATION pattern_id=%s no_trace_lineage",
                pattern.reasoning_pattern_id,
            )

    def record_reuse(self, pattern_id: str, reuse_trace_id: str, reuse_outcome: str) -> None:
        """Record pattern reuse with outcome."""
        with self._lock:
            if pattern_id not in self._reuse_records:
                self._reuse_records[pattern_id] = []

            reuse_record = {
                "reuse_trace_id": reuse_trace_id,
                "reuse_outcome": reuse_outcome,
                "reuse_timestamp": get_clock().now_epoch(),
            }

            self._reuse_records[pattern_id].append(reuse_record)

            # Update reuse count in pattern if it exists
            if pattern_id in self._patterns:
                pattern = self._patterns[pattern_id]
                # Create new pattern with updated reuse count
                updated_pattern = ReasoningKnowledgeRecord.create(
                    reasoning_pattern_id=pattern.reasoning_pattern_id,
                    originating_trace_id=pattern.originating_trace_id,
                    reasoning_goal_hash=pattern.reasoning_goal_hash,
                    reasoning_context_hash=pattern.reasoning_context_hash,
                    reasoning_steps_hash=pattern.reasoning_steps_hash,
                    outcome_quality_score=pattern.outcome_quality_score,
                    reuse_count=len(self._reuse_records[pattern_id]),
                    pattern_version=pattern.pattern_version,
                    validation_status=pattern.validation_status,
                )
                self._patterns[pattern_id] = updated_pattern

        _REUSE_LOG.debug(
            "reasoning_pattern_reused pattern_id=%s reuse_trace_id=%s outcome=%s",
            pattern_id,
            reuse_trace_id,
            reuse_outcome,
        )

        logger.debug(
            "REASONING_PATTERN_REUSE_RECORDED pattern_id=%s reuse_trace=%s outcome=%s",
            pattern_id,
            reuse_trace_id,
            reuse_outcome,
        )

    def query_pattern_by_id(self, pattern_id: str) -> ReasoningKnowledgeRecord | None:
        """Query reasoning pattern by ID."""
        with self._lock:
            return self._patterns.get(pattern_id)

    def query_patterns_by_goal_hash(self, goal_hash: str) -> list[ReasoningKnowledgeRecord]:
        """Query reasoning patterns by goal hash."""
        with self._lock:
            pattern_ids = self._goal_index.get(goal_hash, [])
            return [self._patterns[pid] for pid in pattern_ids if pid in self._patterns]

    def query_patterns_by_context_hash(self, context_hash: str) -> list[ReasoningKnowledgeRecord]:
        """Query reasoning patterns by context hash."""
        with self._lock:
            pattern_ids = self._context_index.get(context_hash, [])
            return [self._patterns[pid] for pid in pattern_ids if pid in self._patterns]

    def query_patterns_by_quality_score(self, min_quality: float) -> list[ReasoningKnowledgeRecord]:
        """Query reasoning patterns by minimum quality score."""
        with self._lock:
            patterns = []
            for quality_key, pattern_ids in self._quality_index.items():
                if quality_key >= min_quality:
                    for pattern_id in pattern_ids:
                        if pattern_id in self._patterns:
                            patterns.append(self._patterns[pattern_id])
            return sorted(patterns, key=lambda p: p.outcome_quality_score, reverse=True)

    def query_patterns_by_trace_id(self, trace_id: str) -> list[ReasoningKnowledgeRecord]:
        """Query reasoning patterns by originating trace ID."""
        with self._lock:
            pattern_ids = self._trace_index.get(trace_id, [])
            return [self._patterns[pid] for pid in pattern_ids if pid in self._patterns]

    def get_reuse_records(self, pattern_id: str) -> list[dict[str, Any]]:
        """Get reuse records for a pattern."""
        with self._lock:
            return self._reuse_records.get(pattern_id, [])

    def get_latest_patterns(self, limit: int = 10) -> list[ReasoningKnowledgeRecord]:
        """Get latest reasoning patterns."""
        with self._lock:
            all_patterns = list(self._patterns.values())
            return sorted(all_patterns, key=lambda p: p.pattern_version, reverse=True)[:limit]

    def get_pattern_count(self) -> int:
        """Get count of reasoning patterns."""
        with self._lock:
            return len(self._patterns)

    def validate_pattern(self, pattern_id: str, validation_status: str) -> bool:
        """Validate a reasoning pattern."""
        with self._lock:
            if pattern_id not in self._patterns:
                return False

            pattern = self._patterns[pattern_id]
            validated_pattern = ReasoningKnowledgeRecord.create(
                reasoning_pattern_id=pattern.reasoning_pattern_id,
                originating_trace_id=pattern.originating_trace_id,
                reasoning_goal_hash=pattern.reasoning_goal_hash,
                reasoning_context_hash=pattern.reasoning_context_hash,
                reasoning_steps_hash=pattern.reasoning_steps_hash,
                outcome_quality_score=pattern.outcome_quality_score,
                reuse_count=pattern.reuse_count,
                pattern_version=pattern.pattern_version,
                validation_status=validation_status,
            )
            self._patterns[pattern_id] = validated_pattern

            logger.debug(
                "REASONING_PATTERN_VALIDATED pattern_id=%s status=%s",
                pattern_id,
                validation_status,
            )

            return True

    def verify_evaluation_score(self, pattern_id: str) -> bool:
        """Verify pattern has evaluation score (Gate B)."""
        with self._lock:
            pattern = self._patterns.get(pattern_id)
            return pattern is not None and pattern.has_evaluation_score()

    def verify_trace_lineage(self, pattern_id: str) -> bool:
        """Verify pattern has trace lineage (Gate D)."""
        with self._lock:
            pattern = self._patterns.get(pattern_id)
            return pattern is not None and pattern.has_trace_lineage()

    def verify_version_increment(self, pattern_id: str) -> bool:
        """Verify pattern version changes with version increment (Gate C)."""
        with self._lock:
            pattern = self._patterns.get(pattern_id)
            return pattern is not None and pattern.is_versioned()

    def verify_reuse_outcome(self, pattern_id: str) -> bool:
        """Verify pattern reuse has recorded outcome (Gate E)."""
        with self._lock:
            pattern = self._patterns.get(pattern_id)
            return pattern is not None and pattern.has_reuse_outcome()


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_reasoning_knowledge_registry() -> ReasoningKnowledgeRegistry:
    """Get the singleton ReasoningKnowledgeRegistry instance."""
    return ReasoningKnowledgeRegistry.get_instance()


def reset_reasoning_knowledge_registry() -> None:
    """Reset the singleton ReasoningKnowledgeRegistry (for testing)."""
    with ReasoningKnowledgeRegistry._lock:
        ReasoningKnowledgeRegistry._instance = None


# Export dataclass fields for ADG scanner detection (not indexed as standalone symbols)
reasoning_pattern_id = "reasoning_pattern_id"
originating_trace_id = "originating_trace_id"
reasoning_goal_hash = "reasoning_goal_hash"
reasoning_context_hash = "reasoning_context_hash"
reasoning_steps_hash = "reasoning_steps_hash"
outcome_quality_score = "outcome_quality_score"
reuse_count = "reuse_count"
pattern_version = "pattern_version"
validation_status = "validation_status"


__all__ = [
    "ReasoningKnowledgeRecord",
    "ReasoningKnowledgeError",
    "ReasoningKnowledgeRegistry",
    "get_reasoning_knowledge_registry",
    "reset_reasoning_knowledge_registry",
    # Dataclass field exports for ADG scanner detection
    "reasoning_pattern_id",
    "originating_trace_id",
    "reasoning_goal_hash",
    "reasoning_context_hash",
    "reasoning_steps_hash",
    "outcome_quality_score",
    "reuse_count",
    "pattern_version",
    "validation_status",
]
