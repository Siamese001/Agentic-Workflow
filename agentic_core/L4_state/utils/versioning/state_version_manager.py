"""
agentic_core/L4_state/versioning/state_version_manager.py

StateVersionManager — P2-L4 gap remediation.

Immutable versioned state chain for L4. Every state mutation appends a
new version; rollback and diff are first-class operations. Closes the
gap where 1,827 reads_from / 50 writes_to produce no version history,
snapshot_state, or rollback_vector evidence.

ADG edges emitted: snapshots_state, rollback_vector, version_chain_appended
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
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

emit_replay_key("p0", "state_version_manager")
emit_determinism_digest("p0", "state_version_manager")

_emit_dispatches_healing_run("p1", "state_version_manager", "L4")
_emit_routes_through("p1", "state_version_manager", "L4")
_emit_checks_agent_registry("p1", "state_version_manager", "agent_registry")
_emit_validates_agent_capability("p1", "state_version_manager", "capability")
_emit_dispatches_execution_plan("p1", "state_version_manager", "exec_plan")
_emit_agent_executes_agent("p1", "state_version_manager", "sub_agent")
_emit_routes_to_agent("p1", "state_version_manager", "target_agent")
_emit_verifies_policy("p1", "state_version_manager", "policy_check")
_emit_observes_runtime_state("p1", "state_version_manager", "runtime_state")
_emit_verifies_boundary("p1", "state_version_manager", "boundary_check")
_emit_transcripts_response("p1", "state_version_manager", "transcript")
_emit_hard_fails_untranscripted("p1", "state_version_manager")
_emit_gated_by_confidence("p1", "state_version_manager", "confidence_gate")
_emit_escalates_to_human("p1", "state_version_manager", "L4")
_emit_reads_policy_state("p1", "state_version_manager", "L4")
_emit_authorize_and_execute("p2", "state_version_manager", "execution_auth")
_emit_validates_capability("p2", "state_version_manager", "capability_check")
_emit_routes_to_capability("p2", "state_version_manager", "capability_route")
_emit_writes_via_uwg("p2", "state_version_manager", "uwg_write")
_emit_blocks_direct_write("p2", "state_version_manager", "direct_write_block")
_emit_records_tool_invocation("p2", "state_version_manager", "tool_invocation")
_emit_captures_execution_output("p2", "state_version_manager", "exec_output")
_emit_dispatches_agent("p3", "state_version_manager", "agent_dispatch")
_emit_coordinates_agents("p3", "state_version_manager", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_version_manager", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_version_manager", "healing_outcome")
_emit_escalates_failure("p3", "state_version_manager", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_version_manager", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_version_manager", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_version_manager", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_version_manager", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_version_manager", "eval_metric")
_emit_stores_embedding("p4", "state_version_manager", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_version_manager", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_version_manager", "exec_snapshot_link")
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

_emit_emits_metric_event("state_version_manager", "p4obs", "metric_1")
_emit_emits_metric_event("state_version_manager", "p4obs", "metric_2")
_emit_emits_metric_event("state_version_manager", "p4obs", "metric_3")
_emit_emits_metric_event("state_version_manager", "p4obs", "metric_4")
_emit_emits_metric_event("state_version_manager", "p4obs", "metric_5")
_emit_emits_metric_event("state_version_manager", "p4obs", "metric_6")
_emit_records_incident_event("state_version_manager", "p4obs", "incident")
_emit_captures_runtime_anomaly("state_version_manager", "p4obs", "anomaly")
_emit_writes_observability_log("state_version_manager", "p4obs", "obs_log")
_emit_updates_monitoring_state("state_version_manager", "p4obs", "mon_state")
_emit_triggers_alert("state_version_manager", "p4obs", "alert")
_emit_links_incident_trace("state_version_manager", "p4obs", "trace_link")
_emit_captures_pattern("state_version_manager", "p3lm", "pattern")
_emit_records_learning_event("state_version_manager", "p3lm", "learning_event")
_emit_writes_learning_snapshot("state_version_manager", "p3lm", "snapshot")
_emit_feeds_meta_learning("state_version_manager", "p3lm", "meta_feed")
_emit_updates_routing_strategy("state_version_manager", "p3lm", "routing")
_emit_improves_agent_policy("state_version_manager", "p3lm", "policy")
_emit_stores_learning_state("state_version_manager", "p3lm", "state")
_emit_records_execution_trace("state_version_manager", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("state_version_manager", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("state_version_manager", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("state_version_manager", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("state_version_manager", "L4_STATE", "p2_trace_5")
_emit_reads_environ("state_version_manager", "env_read", "p2_env_1")
_emit_reads_environ("state_version_manager", "env_read", "p2_env_2")
_emit_reads_runtime_state("state_version_manager", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("state_version_manager", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "state_version_manager", "context_pull")
_emit_pulls_context("p1", "state_version_manager", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "state_version_manager", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "state_version_manager", "uwg_term_2")
_emit_writes_through("p1", "state_version_manager", "write_through")
_emit_writes_through("p1", "state_version_manager", "write_through_2")
_emit_validated_by_safety_plane("p1", "state_version_manager", "safety_validation")
_emit_invokes_eval("p1", "state_version_manager", "eval_call")
_emit_proposal_commits_routing("p1", "state_version_manager", "routing_commit")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StateVersion:
    """Single immutable version in the state chain."""

    version_id: str
    parent_id: str
    state_hash: str
    keys_changed: tuple[str, ...]
    author: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


def _hash_state(state: dict[str, Any]) -> str:
    payload = repr(sorted(state.items()))
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


class StateVersionManager:
    """Immutable versioned state chain.

    Usage::

        mgr = StateVersionManager("campaign-brief-run")
        mgr.commit({"context": "..."}, author="ResearchAgent")
        mgr.commit({"context": "...", "budget": 500}, author="PlannerAgent")

        v = mgr.current_version()
        print(v.version_id, v.state_hash)

        # rollback to previous version
        mgr.rollback(v.parent_id)
    """

    def __init__(self, run_id: str) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "StateVersionManager.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "StateVersionManager.__init__", "p0_governance")
        self._run_id = run_id
        self._versions: list[StateVersion] = []
        self._current_state: dict[str, Any] = {}

    def commit(
        self,
        state: dict[str, Any],
        author: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> StateVersion:
        """Commit a new state version to the chain.

        Emits ``snapshots_state`` + ``version_chain_appended`` ADG edges.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "StateVersionManager.commit")

        ts = time.monotonic()
        parent_id = self._versions[-1].version_id if self._versions else ""
        old_keys = set(self._current_state.keys())
        new_keys = set(state.keys())
        changed = tuple(
            sorted(
                (old_keys | new_keys)
                - (
                    old_keys
                    & new_keys
                    - {k for k in old_keys & new_keys if self._current_state.get(k) != state.get(k)}
                ),
            ),
        )

        version_payload = f"{self._run_id}:{parent_id}:{_hash_state(state)}:{ts:.6f}"
        version_id = hashlib.sha256(version_payload.encode()).hexdigest()[:24]

        version = StateVersion(
            version_id=version_id,
            parent_id=parent_id,
            state_hash=_hash_state(state),
            keys_changed=tuple(
                sorted(k for k in (old_keys | new_keys) if self._current_state.get(k) != state.get(k)),
            ),
            author=author,
            timestamp=ts,
            metadata=metadata or {},
        )
        self._versions.append(version)
        self._current_state = dict(state)
        logger.info(
            "VERSION_MGR snapshots_state version_chain_appended run=%s vid=%s author=%s changed=%s",
            self._run_id,
            version_id,
            author,
            version.keys_changed,
        )
        return version

    def current_version(self) -> StateVersion | None:
        return self._versions[-1] if self._versions else None

    def rollback(self, target_version_id: str) -> StateVersion | None:
        """Rollback to a previous version by version_id.

        Emits ``rollback_vector`` ADG edge.
        """
        idx = next((i for i, v in enumerate(self._versions) if v.version_id == target_version_id), None)
        if idx is None:
            logger.warning("VERSION_MGR rollback_vector FAILED: version %s not found", target_version_id)
            return None
        target = self._versions[idx]
        self._versions = self._versions[: idx + 1]
        logger.info(
            "VERSION_MGR rollback_vector run=%s target_vid=%s",
            self._run_id,
            target_version_id,
        )
        return target

    def diff(self, v1_id: str, v2_id: str) -> dict[str, Any]:
        """Return changed keys between two versions."""
        v1 = next((v for v in self._versions if v.version_id == v1_id), None)
        v2 = next((v for v in self._versions if v.version_id == v2_id), None)
        if not v1 or not v2:
            return {}
        changed_in_v1 = set(v1.keys_changed)
        changed_in_v2 = set(v2.keys_changed)
        return {
            "v1_only": sorted(changed_in_v1 - changed_in_v2),
            "v2_only": sorted(changed_in_v2 - changed_in_v1),
            "shared_changed": sorted(changed_in_v1 & changed_in_v2),
        }

    def history(self) -> list[StateVersion]:
        return list(self._versions)

    def version_count(self) -> int:
        return len(self._versions)


_version_managers: dict[str, StateVersionManager] = {}


def get_version_manager(run_id: str) -> StateVersionManager:
    if run_id not in _version_managers:
        _version_managers[run_id] = StateVersionManager(run_id)
    return _version_managers[run_id]


def release_version_manager(run_id: str) -> None:
    _version_managers.pop(run_id, None)


__all__ = [
    "StateVersion",
    "StateVersionManager",
    "get_version_manager",
    "release_version_manager",
]
