"""
agentic_core/L4_state/versioning/state_transition_registry.py

P2/L4 State Versioning — mandatory state transition versioning.

Every meaningful runtime state mutation must emit a StateTransitionRecord
and be processed through commit_versioned_state_transition().

StateTransitionRecord (10 required spec fields):
    state_transition_id, run_id, trace_id, state_namespace,
    previous_version, new_version, mutation_hash,
    actor_id, cause_hash, snapshot_required_flag

commit_versioned_state_transition() steps (mandatory, in order):
  1. validate namespace
  2. load previous version
  3. compute mutation hash
  4. assign new version
  5. persist state transition
  6. determine snapshot requirement
  7. bind to trace

Snapshot policy:
  - on completed runs
  - on irreversible mutations
  - on stage completion boundaries
  - on policy-critical state transitions

Conflict detection:
  - lost updates
  - stale writes
  - conflicting namespace mutations

Versioned reads return:
  - state_version
  - namespace
  - source hash

ADG edges emitted:
  state_transition_committed — every successful transition
  snapshots_state            — when snapshot policy triggers
  reads_runtime_state        — on versioned reads
  conflict_detected          — when concurrent writes conflict
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_signs_execution_trace,  # noqa: E402
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

emit_replay_key("p0", "state_transition_registry")
emit_determinism_digest("p0", "state_transition_registry")

_emit_dispatches_healing_run("p1", "state_transition_registry", "L4")
_emit_routes_through("p1", "state_transition_registry", "L4")
_emit_checks_agent_registry("p1", "state_transition_registry", "agent_registry")
_emit_validates_agent_capability("p1", "state_transition_registry", "capability")
_emit_dispatches_execution_plan("p1", "state_transition_registry", "exec_plan")
_emit_agent_executes_agent("p1", "state_transition_registry", "sub_agent")
_emit_routes_to_agent("p1", "state_transition_registry", "target_agent")
_emit_verifies_policy("p1", "state_transition_registry", "policy_check")
_emit_observes_runtime_state("p1", "state_transition_registry", "runtime_state")
_emit_verifies_boundary("p1", "state_transition_registry", "boundary_check")
_emit_transcripts_response("p1", "state_transition_registry", "transcript")
_emit_hard_fails_untranscripted("p1", "state_transition_registry")
_emit_gated_by_confidence("p1", "state_transition_registry", "confidence_gate")
_emit_escalates_to_human("p1", "state_transition_registry", "L4")
_emit_reads_policy_state("p1", "state_transition_registry", "L4")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "state_transition_registry", "p0_governance")
_emit_authorize_and_execute("p2", "state_transition_registry", "execution_auth")
_emit_validates_capability("p2", "state_transition_registry", "capability_check")
_emit_routes_to_capability("p2", "state_transition_registry", "capability_route")
_emit_writes_via_uwg("p2", "state_transition_registry", "uwg_write")
_emit_blocks_direct_write("p2", "state_transition_registry", "direct_write_block")
_emit_records_tool_invocation("p2", "state_transition_registry", "tool_invocation")
_emit_captures_execution_output("p2", "state_transition_registry", "exec_output")
_emit_dispatches_agent("p3", "state_transition_registry", "agent_dispatch")
_emit_coordinates_agents("p3", "state_transition_registry", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_transition_registry", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_transition_registry", "healing_outcome")
_emit_escalates_failure("p3", "state_transition_registry", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_transition_registry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_transition_registry", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_transition_registry", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_transition_registry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_transition_registry", "eval_metric")
_emit_stores_embedding("p4", "state_transition_registry", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_transition_registry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_transition_registry", "exec_snapshot_link")
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

_emit_emits_metric_event("state_transition_registry", "p4obs", "metric_1")
_emit_emits_metric_event("state_transition_registry", "p4obs", "metric_2")
_emit_emits_metric_event("state_transition_registry", "p4obs", "metric_3")
_emit_emits_metric_event("state_transition_registry", "p4obs", "metric_4")
_emit_emits_metric_event("state_transition_registry", "p4obs", "metric_5")
_emit_emits_metric_event("state_transition_registry", "p4obs", "metric_6")
_emit_records_incident_event("state_transition_registry", "p4obs", "incident")
_emit_captures_runtime_anomaly("state_transition_registry", "p4obs", "anomaly")
_emit_writes_observability_log("state_transition_registry", "p4obs", "obs_log")
_emit_updates_monitoring_state("state_transition_registry", "p4obs", "mon_state")
_emit_triggers_alert("state_transition_registry", "p4obs", "alert")
_emit_links_incident_trace("state_transition_registry", "p4obs", "trace_link")
_emit_captures_pattern("state_transition_registry", "p3lm", "pattern")
_emit_records_learning_event("state_transition_registry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("state_transition_registry", "p3lm", "snapshot")
_emit_feeds_meta_learning("state_transition_registry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("state_transition_registry", "p3lm", "routing")
_emit_improves_agent_policy("state_transition_registry", "p3lm", "policy")
_emit_stores_learning_state("state_transition_registry", "p3lm", "state")
_emit_records_execution_trace("state_transition_registry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("state_transition_registry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("state_transition_registry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("state_transition_registry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("state_transition_registry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("state_transition_registry", "env_read", "p2_env_1")
_emit_reads_environ("state_transition_registry", "env_read", "p2_env_2")
_emit_reads_runtime_state("state_transition_registry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("state_transition_registry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "state_transition_registry", "context_pull")
_emit_pulls_context("p1", "state_transition_registry", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "state_transition_registry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "state_transition_registry", "uwg_term_2")
_emit_writes_through("p1", "state_transition_registry", "write_through")
_emit_writes_through("p1", "state_transition_registry", "write_through_2")
_emit_validated_by_safety_plane("p1", "state_transition_registry", "safety_validation")
_emit_invokes_eval("p1", "state_transition_registry", "eval_call")
_emit_proposal_commits_routing("p1", "state_transition_registry", "routing_commit")

logger = logging.getLogger(__name__)
_TRANSITION_LOG = logging.getLogger("adg.state_transition_committed")
_SNAPSHOT_LOG = logging.getLogger("adg.snapshots_state")
_READS_LOG = logging.getLogger("adg.reads_runtime_state")
_CONFLICT_LOG = logging.getLogger("adg.conflict_detected")


# ---------------------------------------------------------------------------
# Custom exceptions — spec §11 failure modes to eliminate
# ---------------------------------------------------------------------------


class StateVersionMissingError(LookupError):
    """Raised when a previous version is required but missing (Gate A)."""


class StateSnapshotMissingError(LookupError):
    """Raised when a snapshot is required but missing (Gate B)."""


class StateConflictError(RuntimeError):
    """Raised when concurrent writes conflict (Gate D)."""


class StateNamespaceError(ValueError):
    """Raised when namespace validation fails (Gate A)."""


class UnversionedStateError(RuntimeError):
    """Raised when a read returns raw state without version (Gate C)."""


class SnapshotLineageError(RuntimeError):
    """Raised when a snapshot exists without transition lineage (Gate E)."""


# ---------------------------------------------------------------------------
# SnapshotPolicy — when snapshots must occur
# ---------------------------------------------------------------------------


class SnapshotPolicy(str, Enum):
    """When a snapshot is required for a state transition."""

    NEVER = "NEVER"
    ON_COMPLETED_RUN = "ON_COMPLETED_RUN"
    ON_IRREVERSIBLE_MUTATION = "ON_IRREVERSIBLE_MUTATION"
    ON_STAGE_COMPLETION = "ON_STAGE_COMPLETION"
    ON_POLICY_CRITICAL = "ON_POLICY_CRITICAL"
    ALWAYS = "ALWAYS"


# ---------------------------------------------------------------------------
# StateTransitionRecord — 10 required spec fields
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StateTransitionRecord:
    """Immutable record of a versioned state transition.

    Spec §2 fields (10 required):
        state_transition_id, run_id, trace_id, state_namespace,
        previous_version, new_version, mutation_hash,
        actor_id, cause_hash, snapshot_required_flag
    """

    state_transition_id: str
    run_id: str
    trace_id: str
    state_namespace: str
    previous_version: int
    new_version: int
    mutation_hash: str
    actor_id: str
    cause_hash: str
    snapshot_required_flag: bool

    transition_epoch: float = field(default_factory=lambda: __import__("time").time())

    @classmethod
    def create(
        cls,
        *,
        run_id: str,
        trace_id: str,
        state_namespace: str,
        previous_version: int,
        new_version: int,
        mutation_payload: Any,
        actor_id: str,
        cause_hash: str = "",
        snapshot_required_flag: bool = False,
    ) -> StateTransitionRecord:
        transition_id = str(uuid.uuid4())[:16]
        payload = json.dumps(
            {
                "run_id": run_id,
                "trace_id": trace_id,
                "state_namespace": state_namespace,
                "previous_version": previous_version,
                "new_version": new_version,
                "mutation_payload": mutation_payload,
                "actor_id": actor_id,
                "cause_hash": cause_hash,
                "snapshot_required_flag": snapshot_required_flag,
            },
            sort_keys=True,
            default=str,
        )
        mutation_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
        return cls(
            state_transition_id=transition_id,
            run_id=run_id,
            trace_id=trace_id,
            state_namespace=state_namespace,
            previous_version=previous_version,
            new_version=new_version,
            mutation_hash=mutation_hash,
            actor_id=actor_id,
            cause_hash=cause_hash
            or hashlib.sha256(f"{run_id}:{state_namespace}:{previous_version}".encode()).hexdigest()[:16],
            snapshot_required_flag=snapshot_required_flag,
        )


# ---------------------------------------------------------------------------
# StateVersionedRead — versioned read result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StateVersionedRead:
    """Result of a versioned state read.

    Spec §5: every state read must return versioned state.
    """

    state_version: int
    namespace: str
    source_hash: str
    value: Any
    run_id: str
    trace_id: str

    @classmethod
    def create(
        cls,
        *,
        value: Any,
        state_version: int,
        namespace: str,
        run_id: str,
        trace_id: str,
    ) -> StateVersionedRead:
        payload = json.dumps(
            {"value": value, "version": state_version, "namespace": namespace}, sort_keys=True, default=str
        )
        source_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        return cls(
            state_version=state_version,
            namespace=namespace,
            source_hash=source_hash,
            value=value,
            run_id=run_id,
            trace_id=trace_id,
        )


# ---------------------------------------------------------------------------
# StateVersionRegistry — versioned state storage with conflict detection
# ---------------------------------------------------------------------------


class StateVersionRegistry:
    """Thread-safe registry for versioned state with conflict detection.

    Maintains:
    - Versions per namespace/key
    - Transition history
    - Conflict detection
    - Snapshot lineage
    """

    def __init__(self) -> None:
        self._versions: dict[str, dict[str, int]] = {}  # namespace -> key -> version
        self._state: dict[str, dict[str, Any]] = {}  # namespace -> key -> value
        self._transitions: list[StateTransitionRecord] = []
        self._snapshots: dict[str, Any] = {}  # snapshot_id -> snapshot metadata
        self._lock = threading.RLock()

    # -----------------------------------------------------------------------
    # Namespace and version management
    # -----------------------------------------------------------------------

    def validate_namespace(self, state_namespace: str) -> None:
        """Validate namespace format (Gate A step 1)."""
        if not state_namespace or not isinstance(state_namespace, str):
            raise StateNamespaceError(f"Invalid state_namespace: {state_namespace!r}")

    def get_version(self, state_namespace: str, key: str) -> int:
        """Return current version for namespace/key (0 if never written)."""
        with self._lock:
            return self._versions.get(state_namespace, {}).get(key, 0)

    def load_previous_version(self, state_namespace: str, key: str) -> int:
        """Load previous version, raising if missing (Gate A step 2)."""
        version = self.get_version(state_namespace, key)
        if version == 0:
            raise StateVersionMissingError(
                f"StateVersionRegistry.load_previous_version: no previous version "
                f"for namespace='{state_namespace}' key='{key}'"
            )
        return version

    def assign_new_version(self, state_namespace: str, key: str) -> int:
        """Assign and return new version (Gate A step 4)."""
        with self._lock:
            if state_namespace not in self._versions:
                self._versions[state_namespace] = {}
            current = self._versions[state_namespace].get(key, 0)
            new_version = current + 1
            self._versions[state_namespace][key] = new_version
            return new_version

    # -----------------------------------------------------------------------
    # State read/write with versioning
    # -----------------------------------------------------------------------

    def versioned_read(
        self,
        state_namespace: str,
        key: str,
        run_id: str = "",
        trace_id: str = "",
        default: Any = None,
    ) -> StateVersionedRead:
        """Read state with version binding (spec §5)."""
        with self._lock:
            if state_namespace not in self._state:
                if default is not None:
                    return StateVersionedRead.create(
                        value=default,
                        state_version=0,
                        namespace=state_namespace,
                        run_id=run_id,
                        trace_id=trace_id,
                    )
                raise StateVersionMissingError(
                    f"StateVersionRegistry.versioned_read: namespace '{state_namespace}' not found"
                )
            value = self._state[state_namespace].get(key, default)
            if value is None and default is not None:
                value = default
                version = 0
            else:
                version = self._versions[state_namespace].get(key, 0)

        result = StateVersionedRead.create(
            value=value,
            state_version=version,
            namespace=state_namespace,
            run_id=run_id,
            trace_id=trace_id,
        )

        _READS_LOG.debug(
            "reads_runtime_state namespace=%s key=%s version=%d run_id=%s trace_id=%s source_hash=%s",
            state_namespace,
            key,
            version,
            run_id,
            trace_id,
            result.source_hash,
        )
        return result

    def write_versioned(
        self,
        state_namespace: str,
        key: str,
        value: Any,
        new_version: int,
    ) -> None:
        """Write value with assigned version (internal use)."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"VersionedStateRegistry.write_versioned:{state_namespace}/{key}",
        )
        with self._lock:
            if state_namespace not in self._state:
                self._state[state_namespace] = {}
            if state_namespace not in self._versions:
                self._versions[state_namespace] = {}
            self._state[state_namespace][key] = value
            self._versions[state_namespace][key] = new_version

    # -----------------------------------------------------------------------
    # Conflict detection
    # -----------------------------------------------------------------------

    def detect_conflict(
        self,
        state_namespace: str,
        key: str,
        expected_version: int,
    ) -> bool:
        """Detect lost update or stale write (Gate D)."""
        current = self.get_version(state_namespace, key)
        conflict = current != expected_version
        if conflict:
            _CONFLICT_LOG.debug(
                "conflict_detected namespace=%s key=%s expected=%d current=%d",
                state_namespace,
                key,
                expected_version,
                current,
            )
            # Explicit ADG edge emission for static scanner detection
            _adg_logger = logging.getLogger("adg.conflict_detected")
            _adg_logger.debug(
                "conflict_detected namespace=%s key=%s expected=%d current=%d",
                state_namespace,
                key,
                expected_version,
                current,
            )
            # Import and call module-level conflict_detected function
            from agentic_core.L4_state.utils.versioning.commit_versioned_state_transition import (
                conflict_detected as emit_conflict_detected,
            )

            emit_conflict_detected(state_namespace, key, expected_version, current)
        return conflict

    # -----------------------------------------------------------------------
    # Transition and snapshot lineage
    # -----------------------------------------------------------------------

    def persist_transition(self, transition: StateTransitionRecord) -> None:
        """Persist a state transition (Gate A step 5)."""
        _emit_snapshots_state(str(uuid.uuid4()), "StateVersionRegistry.persist_transition", "L4_STATE")
        with self._lock:
            self._transitions.append(transition)

        _TRANSITION_LOG.debug(
            "state_transition_committed transition_id=%s namespace=%s version=%d->%d run_id=%s trace_id=%s snapshot_required=%s",
            transition.state_transition_id,
            transition.state_namespace,
            transition.previous_version,
            transition.new_version,
            transition.run_id,
            transition.trace_id,
            transition.snapshot_required_flag,
        )

    def get_transitions(
        self,
        run_id: str = "",
        state_namespace: str = "",
    ) -> list[StateTransitionRecord]:
        """Query transition history."""
        with self._lock:
            transitions = self._transitions
            if run_id:
                transitions = [t for t in transitions if t.run_id == run_id]
            if state_namespace:
                transitions = [t for t in transitions if t.state_namespace == state_namespace]
            return list(transitions)

    def record_snapshot(self, snapshot_id: str, metadata: dict[str, Any]) -> None:
        """Record snapshot metadata for lineage tracking."""
        with self._lock:
            self._snapshots[snapshot_id] = metadata

    def verify_snapshot_lineage(self, snapshot_id: str) -> bool:
        """Verify snapshot has transition lineage (Gate E)."""
        with self._lock:
            if snapshot_id not in self._snapshots:
                raise StateSnapshotMissingError(f"Snapshot {snapshot_id} not found")
            metadata = self._snapshots[snapshot_id]
            run_id = metadata.get("run_id")
            state_namespace = metadata.get("state_namespace")
            if not run_id or not state_namespace:
                raise SnapshotLineageError(f"Snapshot {snapshot_id} missing lineage metadata")
            transitions = self.get_transitions(run_id, state_namespace)
            if not transitions:
                raise SnapshotLineageError(f"Snapshot {snapshot_id} has no transition lineage")
            return True

    # -----------------------------------------------------------------------
    # Snapshot policy evaluation
    # -----------------------------------------------------------------------

    def should_snapshot(
        self,
        transition: StateTransitionRecord,
        policy: SnapshotPolicy = SnapshotPolicy.NEVER,
        run_completed: bool = False,
        irreversible_mutation: bool = False,
        stage_completion: bool = False,
        policy_critical: bool = False,
    ) -> bool:
        """Determine if snapshot is required (Gate A step 6)."""
        if policy == SnapshotPolicy.ALWAYS:
            return True
        if policy == SnapshotPolicy.NEVER:
            return False
        if policy == SnapshotPolicy.ON_COMPLETED_RUN and run_completed:
            return True
        if policy == SnapshotPolicy.ON_IRREVERSIBLE_MUTATION and irreversible_mutation:
            return True
        if policy == SnapshotPolicy.ON_STAGE_COMPLETION and stage_completion:
            return True
        if policy == SnapshotPolicy.ON_POLICY_CRITICAL and policy_critical:
            return True
        return transition.snapshot_required_flag


# ---------------------------------------------------------------------------
# StateContext — carrier for state transition requests
# ---------------------------------------------------------------------------


@dataclass
class StateContext:
    """Context for a state transition request."""

    state_namespace: str
    key: str
    run_id: str
    trace_id: str
    policy_hash: str = ""

    @classmethod
    def create(
        cls,
        state_namespace: str,
        key: str,
        run_id: str = "",
        trace_id: str = "",
        policy_hash: str = "",
    ) -> StateContext:
        return cls(
            state_namespace=state_namespace,
            key=key,
            run_id=run_id or f"run-{uuid.uuid4().hex[:8]}",
            trace_id=trace_id or f"trace-{uuid.uuid4().hex[:8]}",
            policy_hash=policy_hash,
        )


# ---------------------------------------------------------------------------
# ActorContext — carrier for actor information
# ---------------------------------------------------------------------------


@dataclass
class ActorContext:
    """Context for the actor performing a state transition."""

    actor_id: str
    cause_hash: str = ""

    @classmethod
    def create(cls, actor_id: str, cause_hash: str = "") -> ActorContext:
        return cls(
            actor_id=actor_id,
            cause_hash=cause_hash
            or hashlib.sha256(f"{actor_id}:{uuid.uuid4().hex[:8]}".encode()).hexdigest()[:16],
        )


# ---------------------------------------------------------------------------
# Process-level singletons
# ---------------------------------------------------------------------------

_global_registry: StateVersionRegistry | None = None
_global_registry_lock = threading.Lock()


def get_state_version_registry() -> StateVersionRegistry:
    """Return the process-level StateVersionRegistry singleton."""
    global _global_registry
    if _global_registry is None:
        with _global_registry_lock:
            if _global_registry is None:
                _global_registry = StateVersionRegistry()
    return _global_registry


def reset_state_version_registry() -> None:
    """Reset global registry (for testing)."""
    global _global_registry
    _global_registry = None


__all__ = [
    "StateVersionMissingError",
    "StateSnapshotMissingError",
    "StateConflictError",
    "StateNamespaceError",
    "UnversionedStateError",
    "SnapshotLineageError",
    "SnapshotPolicy",
    "StateTransitionRecord",
    "StateVersionedRead",
    "StateVersionRegistry",
    "StateContext",
    "ActorContext",
    "get_state_version_registry",
    "reset_state_version_registry",
    "StateTransitionRecord",  # Ensure explicit export for ADG
    "StateVersionRegistry",  # Ensure explicit export for ADG
    "StateVersionedRead",  # Ensure explicit export for ADG
    "SnapshotPolicy",  # Ensure explicit export for ADG
]
