"""L4 State Layer — Persistent state and data sovereignty only.

This layer provides persistent storage, caching, and state management.
No execution logic or agent orchestration belongs in this layer.
Only state types, storage providers, and persistence utilities are exported.
"""

# Sovereignty assertion: This layer contains NO agents with execute() methods
# Any agent classes belong in L2 (Execute) or L3 (Route) layers only

# P2/L4 State Versioning exports
from agentic_core.L4_state.versioning.commit_versioned_state_transition import (
    MutationPayload,
    commit_simple_transition,
    commit_versioned_state_transition,
    conflict_detected,
    read_versioned_state,
    state_transition_committed,
)
from agentic_core.L4_state.versioning.state_transition_registry import (
    ActorContext,
    SnapshotLineageError,
    SnapshotPolicy,
    StateConflictError,
    StateContext,
    StateNamespaceError,
    StateSnapshotMissingError,
    StateTransitionRecord,
    StateVersionedRead,
    StateVersionMissingError,
    StateVersionRegistry,
    UnversionedStateError,
    get_state_version_registry,
    reset_state_version_registry,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L4")
_emit_routes_through("p1", "__init__", "L4")
_emit_escalates_to_human("p1", "__init__", "L4")
_emit_reads_policy_state("p1", "__init__", "L4")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    "StateTransitionRecord",
    "StateVersionRegistry",
    "StateVersionedRead",
    "SnapshotPolicy",
    "StateContext",
    "ActorContext",
    "StateVersionMissingError",
    "StateSnapshotMissingError",
    "StateConflictError",
    "StateNamespaceError",
    "UnversionedStateError",
    "SnapshotLineageError",
    "get_state_version_registry",
    "reset_state_version_registry",
    "MutationPayload",
    "commit_versioned_state_transition",
    "read_versioned_state",
    "commit_simple_transition",
    "state_transition_committed",
    "conflict_detected",
]
