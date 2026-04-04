"""
V15 P2 Typed Artifacts — Determinism & Replayability Compliance Surface.

All typed artifacts required by the V15 Target State audit (Prompt v5.0 Enhanced)
that are gated by P2 (Determinism & Replayability).

Contract version: 1.0.0
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
    record_execution_trace,
)

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

record_execution_trace("determinism_types", "determinism_types_trace")


class FixConstraint(str, Enum):
    """§1.3 — Fix constraint for SurgicalManifest."""

    STRICT = "STRICT"
    RELAXED = "RELAXED"


@dataclass(frozen=True)
class SurgicalManifest:
    """§1.1/§1.3 — Exclusive execution input. All 10 fields required.

    Fields per spec:
      schema_version, correlation_id, node_id, target_layer,
      ast_snippet, serialization_canon, fix_constraint,
      manifest_hash, change_history, provenance_chain
    """

    schema_version: str
    correlation_id: str
    node_id: str
    target_layer: str
    ast_snippet: str
    serialization_canon: str
    fix_constraint: FixConstraint
    manifest_hash: str
    change_history: tuple[str, ...]
    provenance_chain: tuple[str, ...]

    def __post_init__(self) -> None:
        if not re.match("^\\d+\\.\\d+\\.\\d+$", self.schema_version):
            raise ValueError(f"SurgicalManifest: schema_version '{self.schema_version}' is not semver")
        if self.target_layer not in {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}:
            raise ValueError(f"SurgicalManifest: target_layer '{self.target_layer}' not in L0-L6")

    def verify_hash(self) -> bool:
        """§1.6 — manifest_hash must match SHA-256 of ast_snippet bytes."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "SurgicalManifest.verify_hash")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        expected = hashlib.sha256(self.ast_snippet.encode("utf-8")).hexdigest()
        return self.manifest_hash == expected


FORBIDDEN_INPUT_PATTERNS: frozenset[str] = frozenset(
    {
        "raw_file_path",
        "line_number",
        "regex_operation",
        "unified_diff",
        "free_form_text",
        "non_ssot_logic",
        "direct_tool_access",
        "unsigned_human_edit",
    }
)


@dataclass(frozen=True)
class CanonicalASTResult:
    """§1.4 — Result of deterministic AST serialization."""

    source_path: str
    canonical_form: str
    canonical_hash: str

    def verify(self) -> bool:
        """Hash must match canonical_form bytes."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "CanonicalASTResult.verify")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        expected = hashlib.sha256(self.canonical_form.encode("utf-8")).hexdigest()
        return self.canonical_hash == expected


@dataclass
class SemanticClock:
    """§13.1 — Time measured exclusively via Step ID + Vector Clock.

    No wall-clock time. Tick advances only on valid StateCommit (§13.1.1).
    """

    step_id: int = 0
    vector_clock: dict[str, int] = field(default_factory=dict)
    _committed: bool = field(default=False, repr=False, init=False)

    def prepare_commit(self, layer: str) -> None:
        """Prepare a state commit for a layer. Does NOT advance clock."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "SemanticClock.prepare_commit")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        self._committed = False
        if layer not in self.vector_clock:
            self.vector_clock[layer] = 0

    def tick(self, layer: str, state_commit_valid: bool) -> int:
        """§13.1.1 — Advance only on valid StateCommit. Fail-closed otherwise."""
        if not state_commit_valid:
            raise StateCommitInvalid(f"SemanticClock: tick rejected — invalid StateCommit for {layer}")
        self.step_id += 1
        self.vector_clock[layer] = self.vector_clock.get(layer, 0) + 1
        self._committed = True
        return self.step_id

    @property
    def current_tick(self) -> int:
        return self.step_id


class StateCommitInvalid(Exception):
    """§13.1.1 — StateCommit validation failed; clock must not advance."""


@dataclass(frozen=True)
class SemanticClockSnapshot:
    """§Phase3.2 — Immutable snapshot of SemanticClock for embedding in frozen artifacts.

    Serializes as {"tick": <int>, "vector_clock": {<layer>: <int>, ...}}.
    """

    tick: int
    vector_clock: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if self.tick < 0:
            raise ValueError(f"SemanticClockSnapshot: tick must be >= 0, got {self.tick}")

    def to_dict(self) -> dict[str, object]:
        """Deterministic serialization: sorted vector_clock keys."""
        return {"tick": self.tick, "vector_clock": dict(sorted(self.vector_clock))}

    @classmethod
    def from_clock(cls, clock: SemanticClock) -> SemanticClockSnapshot:
        """Capture a snapshot from a live SemanticClock."""
        return cls(tick=clock.step_id, vector_clock=tuple(sorted(clock.vector_clock.items())))


def validate_semantic_clock(
    semantic_clock: SemanticClockSnapshot | None, context: str = ""
) -> SemanticClockSnapshot:
    """§Phase3.2 — Hard-fail if semantic_clock is None at a determinism chokepoint."""
    if semantic_clock is None:
        raise ValueError("semantic_clock is required")
    if not isinstance(semantic_clock, SemanticClockSnapshot):
        raise TypeError(f"semantic_clock must be SemanticClockSnapshot, got {type(semantic_clock).__name__}")
    return semantic_clock


WALL_CLOCK_FORBIDDEN_CALLABLES: frozenset[str] = frozenset(
    {"datetime.utcnow", "datetime.now", "time.time", "time.monotonic", "time.perf_counter"}
)


@dataclass(frozen=True)
class BoundarySnapshotArtifact:
    """§10.2 — Snapshot of filesystem, git state, agent memory at wave start.

    Required fields: trace_id, filesystem_hash, git_state_hash,
                     agent_memory_hash, semantic_clock_tick
    """

    trace_id: str
    filesystem_hash: str
    git_state_hash: str
    agent_memory_hash: str
    semantic_clock_tick: int


@dataclass(frozen=True)
class EpisodicMemoryQueryResult:
    """§6.1 — Episodic memory must be queried before planning.

    Planning functions must accept this as a required input.
    """

    trace_id: str
    query_hash: str
    results: tuple[str, ...]
    confidence_scores: tuple[float, ...]


@dataclass(frozen=True)
class TrajectoryReuseConstraint:
    """§6.2 — Trajectory reuse requires similarity AND exact failure_reason match."""

    trace_id: str
    similarity_score: float
    similarity_threshold: float
    failure_reason: str
    candidate_failure_reason: str

    @property
    def reusable(self) -> bool:
        return (
            self.similarity_score >= self.similarity_threshold
            and self.failure_reason == self.candidate_failure_reason
        )


MEMORY_CONFIDENCE_THRESHOLD: float = 0.7


@dataclass
class KnowledgeSupervisorResult:
    """§6.6 — Knowledge Supervisor audit result for low-confidence retrievals."""

    trace_id: str
    confidence_score: float
    threshold: float = MEMORY_CONFIDENCE_THRESHOLD
    requires_retraining: bool = False

    def __post_init__(self) -> None:
        self.requires_retraining = self.confidence_score < self.threshold


@dataclass(frozen=True)
class MemoryHypostate:
    """§6.8 — Extended Trace Hypostate linked to the Semantic Clock."""

    trace_id: str
    semantic_clock_tick: int
    memory_snapshot_hash: str
    state_commit_id: str


@dataclass(frozen=True)
class EpisodicSemanticLink:
    """§6.10 — Episodic memory records outcome links used in reasoning."""

    trace_id: str
    episodic_memory_id: str
    semantic_outcome_id: str
    reasoning_context_hash: str


TRACE_BUFFER_VELOCITY_THRESHOLD: int = 10


@dataclass
class ForensicTraceBuffer:
    """§15.3 — Ephemeral buffer for high-velocity signal capture.

    Signals >= TRACE_BUFFER_VELOCITY_THRESHOLD per semantic clock tick
    must be captured here before persistence.
    """

    trace_id: str
    semantic_clock_tick: int
    velocity_threshold: int = TRACE_BUFFER_VELOCITY_THRESHOLD
    _buffer: list[dict[str, Any]] = field(default_factory=list, repr=False)

    def ingest(self, signal: dict[str, Any]) -> None:
        """Ingest a signal into the buffer."""
        self._buffer.append(signal)

    @property
    def signal_count(self) -> int:
        return len(self._buffer)

    @property
    def velocity_exceeded(self) -> bool:
        return self.signal_count >= self.velocity_threshold

    def flush(self) -> list[dict[str, Any]]:
        """Flush buffer contents for persistence. Returns copy and clears."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ForensicTraceBuffer.flush")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        contents = list(self._buffer)
        self._buffer.clear()
        return contents


@dataclass(frozen=True)
class SemanticClockAdvancementArtifact:
    """Wave 19: Semantic clock advancement artifact for replay verification.

    Captures semantic clock advancement events with L4 version binding
    and provider identification for deterministic replay.
    """

    advancement_id: str
    previous_tick: int
    new_tick: int
    advancement_reason: str
    l4_version_binding: str
    provider_id: str
    timestamp: float
    artifact_hash: str = ""

    def __post_init__(self):
        if not self.artifact_hash:
            advancement_data = {
                "advancement_id": self.advancement_id,
                "previous_tick": self.previous_tick,
                "new_tick": self.new_tick,
                "advancement_reason": self.advancement_reason,
                "l4_version_binding": self.l4_version_binding,
                "provider_id": self.provider_id,
                "timestamp": self.timestamp,
            }
            import json

            advancement_json = json.dumps(advancement_data, sort_keys=True)
            artifact_hash = hashlib.sha256(advancement_json.encode()).hexdigest()
            object.__setattr__(self, "artifact_hash", artifact_hash)


__all__ = [
    "BoundarySnapshotArtifact",
    "CanonicalASTResult",
    "EpisodicMemoryQueryResult",
    "EpisodicSemanticLink",
    "FORBIDDEN_INPUT_PATTERNS",
    "FixConstraint",
    "ForensicTraceBuffer",
    "KnowledgeSupervisorResult",
    "MEMORY_CONFIDENCE_THRESHOLD",
    "MemoryHypostate",
    "SemanticClock",
    "SemanticClockSnapshot",
    "SemanticClockAdvancementArtifact",
    "StateCommitInvalid",
    "SurgicalManifest",
    "validate_semantic_clock",
    "TRACE_BUFFER_VELOCITY_THRESHOLD",
    "TrajectoryReuseConstraint",
    "WALL_CLOCK_FORBIDDEN_CALLABLES",
]
