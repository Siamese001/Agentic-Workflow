"""
agentic_core/L4_state/authority/run_scoped_state_ledger.py

RunScopedStateLedger — per-run audit ledger for P0/L4 state authority closure.

Records every state interaction (reads, observations, mutations, snapshots,
version vectors, conflict events) bound to a single run_id + trace_id.

This module is the explicit per-run ledger required by the P0/L4 addendum:
  §3  — Run-Scoped State Ledger
  §4  — Versioned State Transitions
  §5  — Snapshot Enforcement
  §6  — State Observation Expansion

All persistent state mutations must route through RunStateAuthority.commit(),
which automatically creates a StateMutationRecord and emits writes_through.

ADG edges emitted (via structured log):
  observes_runtime_state  — every explicit observation entry
  snapshots_state         — every snapshot entry
  writes_through          — every committed mutation (via RunStateAuthority)
  reads_runtime_state     — every read entry
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.L2_execution.providers import get_clock
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
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
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

_log = logging.getLogger(__name__)
_OBSERVE_LOG = logging.getLogger("adg.observes_runtime_state")
_SNAPSHOT_LOG = logging.getLogger("adg.snapshots_state")
_READS_LOG = logging.getLogger("adg.reads_runtime_state")


# ---------------------------------------------------------------------------
# Ledger entry types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReadEntry:
    """Record of a single state read."""

    run_id: str
    trace_id: str
    key: str
    state_version: int
    epoch: float


@dataclass(frozen=True)
class ObservationEntry:
    """Record of an explicit state observation signal."""

    run_id: str
    trace_id: str
    context: str
    stage: str
    actor_id: str
    epoch: float


@dataclass(frozen=True)
class MutationEntry:
    """Record of a committed state mutation."""

    run_id: str
    trace_id: str
    key: str
    previous_state_version: int
    new_state_version: int
    mutation_hash: str
    actor_id: str
    policy_hash: str
    reason_code: str
    epoch: float


@dataclass(frozen=True)
class SnapshotEntry:
    """Record of a state snapshot."""

    run_id: str
    trace_id: str
    label: str
    snapshot_hash: str
    mutation_count: int
    final_state_version: int
    epoch: float


@dataclass(frozen=True)
class ConflictEntry:
    """Record of a detected state conflict."""

    run_id: str
    trace_id: str
    key: str
    expected_version: int
    actual_version: int
    resolved: bool
    epoch: float


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------


class RunScopedStateLedger:
    """Per-run append-only ledger for all state interactions.

    Bind one ledger per run_id. All state reads, observations, mutations,
    snapshots, and conflicts are recorded here for audit and CI gate closure.

    Usage::

        ledger = RunScopedStateLedger(run_id="run-001", trace_id="trace-abc")
        ledger.record_observation("orchestration_stage", stage="plan_start", actor_id="mission_runner")
        ledger.record_mutation("phase", prev_version=0, new_version=1,
                               mutation_hash="abc", actor_id="mission_runner")
        snap = ledger.record_snapshot("run_complete", mutation_count=3)
    """

    def __init__(self, run_id: str, trace_id: str = "") -> None:
        self._run_id = run_id
        self._trace_id = trace_id
        self._reads: list[ReadEntry] = []
        self._observations: list[ObservationEntry] = []
        self._mutations: list[MutationEntry] = []
        self._snapshots: list[SnapshotEntry] = []
        self._conflicts: list[ConflictEntry] = []
        self._lock = threading.RLock()

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def trace_id(self) -> str:
        return self._trace_id

    def record_read(self, key: str, state_version: int) -> ReadEntry:
        """Record a state read and emit reads_runtime_state."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "RunScopedStateLedger.record_read")

        entry = ReadEntry(
            run_id=self._run_id,
            trace_id=self._trace_id,
            key=key,
            state_version=state_version,
            epoch=get_clock().now_epoch(),
        )
        with self._lock:
            self._reads.append(entry)
        _READS_LOG.debug(
            "reads_runtime_state key=%s version=%d run_id=%s",
            key,
            state_version,
            self._run_id,
        )
        return entry

    def record_observation(
        self,
        context: str,
        stage: str = "",
        actor_id: str = "",
    ) -> ObservationEntry:
        """Record an explicit state observation and emit observes_runtime_state."""
        entry = ObservationEntry(
            run_id=self._run_id,
            trace_id=self._trace_id,
            context=context,
            stage=stage,
            actor_id=actor_id,
            epoch=get_clock().now_epoch(),
        )
        with self._lock:
            self._observations.append(entry)
        _OBSERVE_LOG.debug(
            "observes_runtime_state context=%s stage=%s actor=%s run_id=%s",
            context,
            stage,
            actor_id,
            self._run_id,
        )
        return entry

    def record_mutation(
        self,
        key: str,
        previous_state_version: int,
        new_state_version: int,
        mutation_hash: str,
        actor_id: str = "",
        policy_hash: str = "",
        reason_code: str = "",
    ) -> MutationEntry:
        """Record a committed state mutation."""
        entry = MutationEntry(
            run_id=self._run_id,
            trace_id=self._trace_id,
            key=key,
            previous_state_version=previous_state_version,
            new_state_version=new_state_version,
            mutation_hash=mutation_hash,
            actor_id=actor_id,
            policy_hash=policy_hash,
            reason_code=reason_code,
            epoch=get_clock().now_epoch(),
        )
        with self._lock:
            self._mutations.append(entry)
        return entry

    def record_snapshot(
        self,
        label: str,
        state: dict[str, Any] | None = None,
        mutation_count: int | None = None,
        final_state_version: int = 0,
    ) -> SnapshotEntry:
        """Record a state snapshot and emit snapshots_state."""
        _emit_snapshots_state(str(uuid.uuid4()), "RunScopedStateLedger.record_snapshot", "L4_STATE")
        if state is None:
            state = {}
        if mutation_count is None:
            with self._lock:
                mutation_count = len(self._mutations)
        payload = json.dumps(
            {
                "run_id": self._run_id,
                "label": label,
                "state_keys": sorted(state.keys()),
                "final_version": final_state_version,
            },
            sort_keys=True,
        )
        snapshot_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
        entry = SnapshotEntry(
            run_id=self._run_id,
            trace_id=self._trace_id,
            label=label,
            snapshot_hash=snapshot_hash,
            mutation_count=mutation_count,
            final_state_version=final_state_version,
            epoch=get_clock().now_epoch(),
        )
        with self._lock:
            self._snapshots.append(entry)
        _SNAPSHOT_LOG.debug(
            "snapshots_state run_id=%s label=%s hash=%s mutations=%d",
            self._run_id,
            label,
            snapshot_hash,
            mutation_count,
        )
        return entry

    def record_conflict(
        self,
        key: str,
        expected_version: int,
        actual_version: int,
        resolved: bool = False,
    ) -> ConflictEntry:
        """Record a detected version conflict event."""
        entry = ConflictEntry(
            run_id=self._run_id,
            trace_id=self._trace_id,
            key=key,
            expected_version=expected_version,
            actual_version=actual_version,
            resolved=resolved,
            epoch=get_clock().now_epoch(),
        )
        with self._lock:
            self._conflicts.append(entry)
        _log.warning(
            "STATE_CONFLICT key=%s expected=%d actual=%d resolved=%s run_id=%s",
            key,
            expected_version,
            actual_version,
            resolved,
            self._run_id,
        )
        return entry

    # ── Accessors ──────────────────────────────────────────────────────────

    def reads(self) -> list[ReadEntry]:
        with self._lock:
            return list(self._reads)

    def observations(self) -> list[ObservationEntry]:
        with self._lock:
            return list(self._observations)

    def mutations(self) -> list[MutationEntry]:
        with self._lock:
            return list(self._mutations)

    def snapshots(self) -> list[SnapshotEntry]:
        with self._lock:
            return list(self._snapshots)

    def conflicts(self) -> list[ConflictEntry]:
        with self._lock:
            return list(self._conflicts)

    def summary(self) -> dict[str, Any]:
        """Return ledger summary for CI gate and monitoring."""
        with self._lock:
            return {
                "run_id": self._run_id,
                "trace_id": self._trace_id,
                "reads": len(self._reads),
                "observations": len(self._observations),
                "mutations": len(self._mutations),
                "snapshots": len(self._snapshots),
                "conflicts": len(self._conflicts),
            }


# ---------------------------------------------------------------------------
# Process-level registry
# ---------------------------------------------------------------------------

_registry: dict[str, RunScopedStateLedger] = {}
_registry_lock = threading.Lock()


def get_state_ledger(run_id: str, trace_id: str = "") -> RunScopedStateLedger:
    """Get or create a RunScopedStateLedger for ``run_id``."""
    _emit_writes_through(str(uuid.uuid4()), "Module.get_state_ledger", "L4_STATE")
    with _registry_lock:
        if run_id not in _registry:
            _registry[run_id] = RunScopedStateLedger(run_id=run_id, trace_id=trace_id)
        return _registry[run_id]


def release_state_ledger(run_id: str) -> None:
    """Release the ledger for ``run_id`` after run completion."""
    with _registry_lock:
        _registry.pop(run_id, None)


def active_ledger_run_ids() -> list[str]:
    """Return all currently active ledger run IDs."""
    with _registry_lock:
        return list(_registry.keys())


__all__ = [
    "ReadEntry",
    "ObservationEntry",
    "MutationEntry",
    "SnapshotEntry",
    "ConflictEntry",
    "RunScopedStateLedger",
    "get_state_ledger",
    "release_state_ledger",
    "active_ledger_run_ids",
]
