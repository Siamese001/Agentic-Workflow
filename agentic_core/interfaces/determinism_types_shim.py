"""
agentic_core/interfaces/determinism_types.py

Re-export shim: exposes determinism types through the allowed
agentic_core.interfaces path so that system_learning (and any other
downstream consumer) does not need to reach into the L0_routing layer
directly.

system_learning MUST import from here, not from
agentic_core.L0_routing.types.determinism_types.
"""
from agentic_core.L0_routing.types.determinism_types import (
    FORBIDDEN_INPUT_PATTERNS,
    MEMORY_CONFIDENCE_THRESHOLD,
    TRACE_BUFFER_VELOCITY_THRESHOLD,
    WALL_CLOCK_FORBIDDEN_CALLABLES,
    BoundarySnapshotArtifact,
    CanonicalASTResult,
    EpisodicMemoryQueryResult,
    EpisodicSemanticLink,
    FixConstraint,
    ForensicTraceBuffer,
    KnowledgeSupervisorResult,
    MemoryHypostate,
    SemanticClock,
    SemanticClockSnapshot,
    StateCommitInvalid,
    SurgicalManifest,
    TrajectoryReuseConstraint,
    validate_semantic_clock,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("determinism_types", "determinism_types_digest")
record_execution_trace("determinism_types", "determinism_types_trace")


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
    "StateCommitInvalid",
    "SurgicalManifest",
    "TRACE_BUFFER_VELOCITY_THRESHOLD",
    "TrajectoryReuseConstraint",
    "validate_semantic_clock",
    "WALL_CLOCK_FORBIDDEN_CALLABLES",
]
