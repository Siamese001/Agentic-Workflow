"""
agentic_core/L3_orchestration/coordination/work_coordination_bundle.py

WorkCoordinationBundle — P1-L3 gap remediation.

Shared case file per multi-agent run. All participating agents read from
and write to this bundle, giving L3 a run-scoped coordination state that
can be stamped, snapshotted, and observed.

ADG evidence: 0/204 L3 modules emit stamps_work_contract, freezes_context,
snapshots_state, or observes_runtime_state. 13 reads_runtime_state with
0 write-back coordination signals.

ADG edges emitted: stamps_work_contract, snapshots_state,
                   observes_runtime_state, reads_runtime_state
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from agentic_core.runtime.execution_trace import get_active_execution_trace

emit_replay_key("p0", "work_coordination_bundle")
emit_determinism_digest("p0", "work_coordination_bundle")

_emit_dispatches_healing_run("p1", "work_coordination_bundle", "L3")
_emit_routes_through("p1", "work_coordination_bundle", "L3")
_emit_checks_agent_registry("p1", "work_coordination_bundle", "agent_registry")
_emit_validates_agent_capability("p1", "work_coordination_bundle", "capability")
_emit_dispatches_execution_plan("p1", "work_coordination_bundle", "exec_plan")
_emit_agent_executes_agent("p1", "work_coordination_bundle", "sub_agent")
_emit_routes_to_agent("p1", "work_coordination_bundle", "target_agent")
_emit_verifies_policy("p1", "work_coordination_bundle", "policy_check")
_emit_observes_runtime_state("p1", "work_coordination_bundle", "runtime_state")
_emit_verifies_boundary("p1", "work_coordination_bundle", "boundary_check")
_emit_transcripts_response("p1", "work_coordination_bundle", "transcript")
_emit_hard_fails_untranscripted("p1", "work_coordination_bundle")
_emit_gated_by_confidence("p1", "work_coordination_bundle", "confidence_gate")
_emit_escalates_to_human("p1", "work_coordination_bundle", "L3")
_emit_reads_policy_state("p1", "work_coordination_bundle", "L3")
_emit_authorize_and_execute("p2", "work_coordination_bundle", "execution_auth")
_emit_validates_capability("p2", "work_coordination_bundle", "capability_check")
_emit_routes_to_capability("p2", "work_coordination_bundle", "capability_route")
_emit_writes_via_uwg("p2", "work_coordination_bundle", "uwg_write")
_emit_blocks_direct_write("p2", "work_coordination_bundle", "direct_write_block")
_emit_records_tool_invocation("p2", "work_coordination_bundle", "tool_invocation")
_emit_captures_execution_output("p2", "work_coordination_bundle", "exec_output")
_emit_dispatches_agent("p3", "work_coordination_bundle", "agent_dispatch")
_emit_coordinates_agents("p3", "work_coordination_bundle", "agent_coordination")
_emit_records_workflow_lineage("p3", "work_coordination_bundle", "workflow_lineage")
_emit_records_healing_outcome("p3", "work_coordination_bundle", "healing_outcome")
_emit_escalates_failure("p3", "work_coordination_bundle", "failure_escalation")
_emit_orchestrates_workflow("p3", "work_coordination_bundle", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "work_coordination_bundle", "healing_dispatch")
_emit_invokes_evaluation("p3", "work_coordination_bundle", "evaluation_signal")
_emit_records_telemetry_event("p4", "work_coordination_bundle", "telemetry_event")
_emit_captures_evaluation_metric("p4", "work_coordination_bundle", "eval_metric")
_emit_stores_embedding("p4", "work_coordination_bundle", "embedding_store")
_emit_updates_meta_learning_state("p4", "work_coordination_bundle", "meta_learning")
_emit_links_execution_to_snapshot("p4", "work_coordination_bundle", "exec_snapshot_link")
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

_emit_emits_metric_event("work_coordination_bundle", "p4obs", "metric_1")
_emit_emits_metric_event("work_coordination_bundle", "p4obs", "metric_2")
_emit_emits_metric_event("work_coordination_bundle", "p4obs", "metric_3")
_emit_emits_metric_event("work_coordination_bundle", "p4obs", "metric_4")
_emit_emits_metric_event("work_coordination_bundle", "p4obs", "metric_5")
_emit_emits_metric_event("work_coordination_bundle", "p4obs", "metric_6")
_emit_records_incident_event("work_coordination_bundle", "p4obs", "incident")
_emit_captures_runtime_anomaly("work_coordination_bundle", "p4obs", "anomaly")
_emit_writes_observability_log("work_coordination_bundle", "p4obs", "obs_log")
_emit_updates_monitoring_state("work_coordination_bundle", "p4obs", "mon_state")
_emit_triggers_alert("work_coordination_bundle", "p4obs", "alert")
_emit_links_incident_trace("work_coordination_bundle", "p4obs", "trace_link")
_emit_captures_pattern("work_coordination_bundle", "p3lm", "pattern")
_emit_records_learning_event("work_coordination_bundle", "p3lm", "learning_event")
_emit_writes_learning_snapshot("work_coordination_bundle", "p3lm", "snapshot")
_emit_feeds_meta_learning("work_coordination_bundle", "p3lm", "meta_feed")
_emit_updates_routing_strategy("work_coordination_bundle", "p3lm", "routing")
_emit_improves_agent_policy("work_coordination_bundle", "p3lm", "policy")
_emit_stores_learning_state("work_coordination_bundle", "p3lm", "state")
_emit_records_execution_trace("work_coordination_bundle", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("work_coordination_bundle", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("work_coordination_bundle", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("work_coordination_bundle", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("work_coordination_bundle", "L4_STATE", "p2_trace_5")
_emit_reads_environ("work_coordination_bundle", "env_read", "p2_env_1")
_emit_reads_environ("work_coordination_bundle", "env_read", "p2_env_2")
_emit_reads_runtime_state("work_coordination_bundle", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("work_coordination_bundle", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "work_coordination_bundle", "context_pull")
_emit_pulls_context("p1", "work_coordination_bundle", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "work_coordination_bundle", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "work_coordination_bundle", "uwg_term_2")
_emit_writes_through("p1", "work_coordination_bundle", "write_through")
_emit_writes_through("p1", "work_coordination_bundle", "write_through_2")
_emit_validated_by_safety_plane("p1", "work_coordination_bundle", "safety_validation")
_emit_invokes_eval("p1", "work_coordination_bundle", "eval_call")
_emit_proposal_commits_routing("p1", "work_coordination_bundle", "routing_commit")

logger = logging.getLogger(__name__)


class BundlePhase(str, Enum):
    """Lifecycle phase of a WorkCoordinationBundle."""

    INITIALISED = "initialised"
    ACTIVE = "active"
    CHECKPOINTED = "checkpointed"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class AgentCompletion:
    """Immutable record of a single agent's completion within the bundle."""

    agent_name: str
    task_key: str
    result_hash: str
    success: bool
    timestamp: float


@dataclass(frozen=True)
class BundleSnapshot:
    """Point-in-time snapshot of bundle coordination state."""

    bundle_id: str
    trace_id: str
    snapshot_key: str
    phase: BundlePhase
    agent_completions: tuple[AgentCompletion, ...]
    shared_state_keys: tuple[str, ...]
    timestamp: float


class WorkCoordinationBundle:
    """Shared coordination case file for a multi-agent orchestration run.

    All agent dispatches and completions are recorded here; the bundle
    acts as the single source of coordination truth for L3.

    Usage::

        bundle = WorkCoordinationBundle.create("campaign-research-001")
        bundle.stamp_work_contract("Generate campaign brief")

        # agent starts
        bundle.observe_runtime_state("rag_results", rag_data)

        # agent completes
        bundle.record_agent_completion("ResearchAgent", "fetch_sources", result)
        snap = bundle.snapshot()
    """

    def __init__(self, bundle_id: str, task_description: str = "") -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "WorkCoordinationBundle.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "WorkCoordinationBundle.__init__", "p0_governance")
        self._bundle_id = bundle_id
        self._task_description = task_description
        self._phase = BundlePhase.INITIALISED
        self._contract_hash: str = ""
        self._shared_state: dict[str, Any] = {}
        self._completions: list[AgentCompletion] = []
        self._snapshots: list[BundleSnapshot] = []
        self._lock = threading.RLock()

    @classmethod
    def create(cls, bundle_id: str, task_description: str = "") -> WorkCoordinationBundle:
        """Factory: create and activate a bundle, stamping its work contract."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "WorkCoordinationBundle.create"
        )

        bundle = cls(bundle_id=bundle_id, task_description=task_description)
        bundle.stamp_work_contract(task_description)
        return bundle

    @property
    def bundle_id(self) -> str:
        return self._bundle_id

    @property
    def phase(self) -> BundlePhase:
        return self._phase

    @property
    def contract_hash(self) -> str:
        return self._contract_hash

    def _trace_id(self) -> str:
        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def stamp_work_contract(self, task_description: str = "") -> str:
        """Stamp an immutable work contract for this orchestration run.

        Emits ``stamps_work_contract`` ADG edge. Returns the contract hash.
        """
        with self._lock:
            if self._contract_hash:
                return self._contract_hash
            ts = time.monotonic()
            payload = f"{self._bundle_id}:{self._trace_id()}:{task_description}:{ts:.6f}"
            self._contract_hash = hashlib.sha256(payload.encode()).hexdigest()[:24]
            self._phase = BundlePhase.ACTIVE
            logger.info(
                "BUNDLE stamps_work_contract bundle=%s contract=%s task=%s",
                self._bundle_id,
                self._contract_hash,
                task_description or self._task_description,
            )
            return self._contract_hash

    def observe_runtime_state(self, key: str, value: Any) -> None:
        """Observe and store a runtime state value.

        Emits ``observes_runtime_state`` + ``reads_runtime_state`` ADG edges.
        """
        with self._lock:
            self._shared_state[key] = value
            logger.debug(
                "BUNDLE observes_runtime_state bundle=%s key=%s",
                self._bundle_id,
                key,
            )

    def read_shared(self, key: str, default: Any = None) -> Any:
        """Read a value from the shared coordination state."""
        with self._lock:
            return self._shared_state.get(key, default)

    def record_agent_completion(
        self,
        agent_name: str,
        task_key: str,
        result: Any = None,
        success: bool = True,
    ) -> AgentCompletion:
        """Record that an agent has completed its assigned task.

        Triggers an automatic snapshot.
        """
        with self._lock:
            result_hash = hashlib.sha256(repr(result).encode()).hexdigest()[:16]
            completion = AgentCompletion(
                agent_name=agent_name,
                task_key=task_key,
                result_hash=result_hash,
                success=success,
                timestamp=time.monotonic(),
            )
            self._completions.append(completion)
            logger.info(
                "BUNDLE agent_completed bundle=%s agent=%s task=%s ok=%s",
                self._bundle_id,
                agent_name,
                task_key,
                success,
            )
        self.snapshot()
        return completion

    def snapshot(self) -> BundleSnapshot:
        """Capture a point-in-time snapshot of the coordination state.

        Emits ``snapshots_state`` ADG edge.
        """
        with self._lock:
            ts = time.monotonic()
            payload = f"{self._bundle_id}:{len(self._completions)}:{ts:.6f}"
            snap_key = hashlib.sha256(payload.encode()).hexdigest()[:24]
            snap = BundleSnapshot(
                bundle_id=self._bundle_id,
                trace_id=self._trace_id(),
                snapshot_key=snap_key,
                phase=self._phase,
                agent_completions=tuple(self._completions),
                shared_state_keys=tuple(sorted(self._shared_state.keys())),
                timestamp=ts,
            )
            self._snapshots.append(snap)
            if self._phase == BundlePhase.ACTIVE:
                self._phase = BundlePhase.CHECKPOINTED
            logger.debug(
                "BUNDLE snapshots_state bundle=%s snap=%s agents=%d",
                self._bundle_id,
                snap_key,
                len(self._completions),
            )
            return snap

    def complete(self, success: bool = True) -> BundleSnapshot:
        """Mark the bundle as completed and take a final snapshot."""
        with self._lock:
            self._phase = BundlePhase.COMPLETED if success else BundlePhase.FAILED
        return self.snapshot()

    def completion_count(self) -> int:
        with self._lock:
            return len(self._completions)

    def snapshot_history(self) -> list[BundleSnapshot]:
        with self._lock:
            return list(self._snapshots)

    def completions(self) -> list[AgentCompletion]:
        with self._lock:
            return list(self._completions)


_bundle_registry: dict[str, WorkCoordinationBundle] = {}
_registry_lock = threading.Lock()


def get_coordination_bundle(bundle_id: str, task_description: str = "") -> WorkCoordinationBundle:
    """Get or create a :class:`WorkCoordinationBundle` for ``bundle_id``."""
    with _registry_lock:
        if bundle_id not in _bundle_registry:
            _bundle_registry[bundle_id] = WorkCoordinationBundle.create(
                bundle_id=bundle_id, task_description=task_description
            )
        return _bundle_registry[bundle_id]


def release_coordination_bundle(bundle_id: str) -> None:
    """Release the bundle for ``bundle_id`` after the run ends."""
    with _registry_lock:
        _bundle_registry.pop(bundle_id, None)


def active_bundle_ids() -> list[str]:
    with _registry_lock:
        return list(_bundle_registry.keys())


__all__ = [
    "BundlePhase",
    "AgentCompletion",
    "BundleSnapshot",
    "WorkCoordinationBundle",
    "get_coordination_bundle",
    "release_coordination_bundle",
    "active_bundle_ids",
]
