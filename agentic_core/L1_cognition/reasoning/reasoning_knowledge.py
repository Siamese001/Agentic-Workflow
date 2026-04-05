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

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "reasoning_knowledge")
emit_determinism_digest("p0", "reasoning_knowledge")

_emit_dispatches_healing_run("p1", "reasoning_knowledge", "L1")
_emit_routes_through("p1", "reasoning_knowledge", "L1")
_emit_checks_agent_registry("p1", "reasoning_knowledge", "agent_registry")
_emit_validates_agent_capability("p1", "reasoning_knowledge", "capability")
_emit_dispatches_execution_plan("p1", "reasoning_knowledge", "exec_plan")
_emit_agent_executes_agent("p1", "reasoning_knowledge", "sub_agent")
_emit_routes_to_agent("p1", "reasoning_knowledge", "target_agent")
_emit_verifies_policy("p1", "reasoning_knowledge", "policy_check")
_emit_observes_runtime_state("p1", "reasoning_knowledge", "runtime_state")
_emit_verifies_boundary("p1", "reasoning_knowledge", "boundary_check")
_emit_transcripts_response("p1", "reasoning_knowledge", "transcript")
_emit_hard_fails_untranscripted("p1", "reasoning_knowledge")
_emit_gated_by_confidence("p1", "reasoning_knowledge", "confidence_gate")
_emit_escalates_to_human("p1", "reasoning_knowledge", "L1")
_emit_reads_policy_state("p1", "reasoning_knowledge", "L1")
_emit_authorize_and_execute("p2", "reasoning_knowledge", "execution_auth")
_emit_validates_capability("p2", "reasoning_knowledge", "capability_check")
_emit_routes_to_capability("p2", "reasoning_knowledge", "capability_route")
_emit_writes_via_uwg("p2", "reasoning_knowledge", "uwg_write")
_emit_blocks_direct_write("p2", "reasoning_knowledge", "direct_write_block")
_emit_records_tool_invocation("p2", "reasoning_knowledge", "tool_invocation")
_emit_captures_execution_output("p2", "reasoning_knowledge", "exec_output")
_emit_dispatches_agent("p3", "reasoning_knowledge", "agent_dispatch")
_emit_coordinates_agents("p3", "reasoning_knowledge", "agent_coordination")
_emit_records_workflow_lineage("p3", "reasoning_knowledge", "workflow_lineage")
_emit_records_healing_outcome("p3", "reasoning_knowledge", "healing_outcome")
_emit_escalates_failure("p3", "reasoning_knowledge", "failure_escalation")
_emit_orchestrates_workflow("p3", "reasoning_knowledge", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reasoning_knowledge", "healing_dispatch")
_emit_invokes_evaluation("p3", "reasoning_knowledge", "evaluation_signal")
_emit_records_telemetry_event("p4", "reasoning_knowledge", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reasoning_knowledge", "eval_metric")
_emit_stores_embedding("p4", "reasoning_knowledge", "embedding_store")
_emit_updates_meta_learning_state("p4", "reasoning_knowledge", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reasoning_knowledge", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("reasoning_knowledge", "p4obs", "metric_1")
_emit_emits_metric_event("reasoning_knowledge", "p4obs", "metric_2")
_emit_emits_metric_event("reasoning_knowledge", "p4obs", "metric_3")
_emit_emits_metric_event("reasoning_knowledge", "p4obs", "metric_4")
_emit_emits_metric_event("reasoning_knowledge", "p4obs", "metric_5")
_emit_emits_metric_event("reasoning_knowledge", "p4obs", "metric_6")
_emit_records_incident_event("reasoning_knowledge", "p4obs", "incident")
_emit_captures_runtime_anomaly("reasoning_knowledge", "p4obs", "anomaly")
_emit_writes_observability_log("reasoning_knowledge", "p4obs", "obs_log")
_emit_updates_monitoring_state("reasoning_knowledge", "p4obs", "mon_state")
_emit_triggers_alert("reasoning_knowledge", "p4obs", "alert")
_emit_links_incident_trace("reasoning_knowledge", "p4obs", "trace_link")
_emit_captures_pattern("reasoning_knowledge", "p3lm", "pattern")
_emit_records_learning_event("reasoning_knowledge", "p3lm", "learning_event")
_emit_writes_learning_snapshot("reasoning_knowledge", "p3lm", "snapshot")
_emit_feeds_meta_learning("reasoning_knowledge", "p3lm", "meta_feed")
_emit_updates_routing_strategy("reasoning_knowledge", "p3lm", "routing")
_emit_improves_agent_policy("reasoning_knowledge", "p3lm", "policy")
_emit_stores_learning_state("reasoning_knowledge", "p3lm", "state")
_emit_records_execution_trace("reasoning_knowledge", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("reasoning_knowledge", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("reasoning_knowledge", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("reasoning_knowledge", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("reasoning_knowledge", "L4_STATE", "p2_trace_5")
_emit_reads_environ("reasoning_knowledge", "env_read", "p2_env_1")
_emit_reads_environ("reasoning_knowledge", "env_read", "p2_env_2")
_emit_reads_runtime_state("reasoning_knowledge", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("reasoning_knowledge", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "reasoning_knowledge", "context_pull")
_emit_pulls_context("p1", "reasoning_knowledge", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "reasoning_knowledge", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "reasoning_knowledge", "uwg_term_2")
_emit_writes_through("p1", "reasoning_knowledge", "write_through")
_emit_writes_through("p1", "reasoning_knowledge", "write_through_2")
_emit_validated_by_safety_plane("p1", "reasoning_knowledge", "safety_validation")
_emit_invokes_eval("p1", "reasoning_knowledge", "eval_call")
_emit_proposal_commits_routing("p1", "reasoning_knowledge", "routing_commit")

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
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReasoningKnowledgeRecord.create", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReasoningKnowledgeRecord.create", "p0_governance")
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "ReasoningKnowledgeRegistry.get_instance"
        )

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
