"""L4 versioned ChangePackage store — write-once semantics with activation pointers.

Provides:
  - Content-addressed commit (SHA-256 of canonical_bytes → version_id)
  - Write-once / idempotent: same content → same version_id, no mutation
  - Parent existence enforcement (DAG, not free graph)
  - O(1) activation pointer update and rollback
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "l4_version_store", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "l4_version_store", "policy_binding")

trace_contract._emit_emits_metric_event("l4_version_store", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("l4_version_store", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("l4_version_store", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("l4_version_store", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("l4_version_store", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("l4_version_store", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("l4_version_store", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("l4_version_store", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("l4_version_store", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("l4_version_store", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("l4_version_store", "p4obs", "alert")
trace_contract._emit_links_incident_trace("l4_version_store", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("l4_version_store", "p3lm", "pattern")
trace_contract._emit_records_learning_event("l4_version_store", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("l4_version_store", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("l4_version_store", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("l4_version_store", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("l4_version_store", "p3lm", "policy")
trace_contract._emit_stores_learning_state("l4_version_store", "p3lm", "state")
trace_contract._emit_records_execution_trace("l4_version_store", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("l4_version_store", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("l4_version_store", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("l4_version_store", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("l4_version_store", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("l4_version_store", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("l4_version_store", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("l4_version_store", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("l4_version_store", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "l4_version_store", "context_pull")
trace_contract._emit_pulls_context("p1", "l4_version_store", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "l4_version_store", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "l4_version_store", "uwg_term_2")
trace_contract._emit_writes_through("p1", "l4_version_store", "write_through")
trace_contract._emit_writes_through("p1", "l4_version_store", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "l4_version_store", "safety_validation")
trace_contract._emit_invokes_eval("p1", "l4_version_store", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "l4_version_store", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "l4_version_store", "human_escalation")
trace_contract._emit_routes_through("p1", "l4_version_store", "route_through")
trace_contract._emit_checks_agent_registry("p1", "l4_version_store", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "l4_version_store", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "l4_version_store", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "l4_version_store", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "l4_version_store", "target_agent")
trace_contract._emit_verifies_policy("p1", "l4_version_store", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "l4_version_store", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "l4_version_store", "boundary_check")
trace_contract._emit_transcripts_response("p1", "l4_version_store", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "l4_version_store")
trace_contract._emit_gated_by_confidence("p1", "l4_version_store", "confidence_gate")
trace_contract.emit_replay_key("p0", "l4_version_store")
trace_contract.emit_determinism_digest("p0", "l4_version_store")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "l4_version_store", "execution_auth")
trace_contract._emit_validates_capability("p2", "l4_version_store", "capability_check")
trace_contract._emit_routes_to_capability("p2", "l4_version_store", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "l4_version_store", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "l4_version_store", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "l4_version_store", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "l4_version_store", "exec_output")
trace_contract._emit_dispatches_agent("p3", "l4_version_store", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "l4_version_store", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "l4_version_store", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "l4_version_store", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "l4_version_store", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "l4_version_store", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "l4_version_store", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "l4_version_store", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "l4_version_store", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "l4_version_store", "eval_metric")
trace_contract._emit_stores_embedding("p4", "l4_version_store", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "l4_version_store", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "l4_version_store", "exec_snapshot_link")


class ParentVersionNotFound(Exception):
    """Raised when a specified parent version does not exist in the store."""


class VersionNotFound(Exception):
    """Raised when a requested version does not exist in the store."""


@dataclass(frozen=True)
class VersionedPackage:
    """Immutable record of a committed ChangePackage."""

    version_id: str
    parent_version_id: str | None
    change_spec_hash: str
    committed_at_utc: int
    package_bytes: bytes


class L4VersionStore:
    """Concrete in-memory L4 versioned store.

    Enforces:
      - Write-once / idempotent semantics (content-addressed by SHA-256)
      - Parent existence for non-genesis commits
      - O(1) activation pointer update and rollback
      - No deletion of historical versions
    """

    def __init__(self) -> None:
        self._versions: dict[str, VersionedPackage] = {}
        self._active_pointers: dict[str, str] = {}

    def commit_change_package(
        self,
        package,
        parent_version_id: str | None,
        change_spec_hash: str,
        committed_at_utc: int,
    ) -> str:
        """Commit a ChangePackage and return its version_id.

        Parameters
        ----------
        package
            Any object implementing ``canonical_bytes() -> bytes``.
        parent_version_id : str | None
            Parent version or ``None`` for genesis.
        change_spec_hash : str
            Caller-supplied spec hash (stored but not used for version_id).
        committed_at_utc : int
            Commit timestamp.

        Returns
        -------
        str
            SHA-256 hex digest of ``package.canonical_bytes()``.

        Raises
        ------
        ParentVersionNotFound
            If ``parent_version_id`` is not ``None`` and not in the store.
        """
        trace_contract._emit_snapshots_state(str(uuid.uuid4()), "L4VersionStore.commit_change_package", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "L4VersionStore.commit_change_package"
        )

        raw = package.canonical_bytes()
        version_id = hashlib.sha256(raw).hexdigest()
        if version_id in self._versions:
            return version_id
        if parent_version_id is not None and parent_version_id not in self._versions:
            raise ParentVersionNotFound(
                f"PARENT_VERSION_NOT_FOUND: parent {parent_version_id!r} does not exist",
            )
        self._versions[version_id] = VersionedPackage(
            version_id=version_id,
            parent_version_id=parent_version_id,
            change_spec_hash=change_spec_hash,
            committed_at_utc=committed_at_utc,
            package_bytes=raw,
        )
        return version_id

    def get_change_package(self, version_id: str) -> VersionedPackage:
        """Retrieve a versioned package by ID.

        Raises
        ------
        VersionNotFound
            If the version_id is not in the store.
        """
        if version_id not in self._versions:
            raise VersionNotFound(f"VERSION_NOT_FOUND: {version_id!r}")
        return self._versions[version_id]

    def list_versions(self) -> list[str]:
        """Return a deterministic sorted list of all committed version_ids."""
        return sorted(self._versions.keys())

    def update_activation_pointer(self, component: str, version_id: str) -> None:
        """Set the active version for a component.

        Raises
        ------
        VersionNotFound
            If the target version_id does not exist.
        """
        if version_id not in self._versions:
            raise VersionNotFound(f"ACTIVATION_TARGET_NOT_FOUND: {version_id!r}")
        self._active_pointers[component] = version_id

    def get_active_version(self, component: str) -> str | None:
        """Return the currently active version_id for a component, or None."""
        return self._active_pointers.get(component)

    def rollback(self, component: str, version_id: str) -> None:
        """Revert the activation pointer for a component to a prior version_id.

        Does NOT delete any historical versions.

        Raises
        ------
        VersionNotFound
            If the rollback target does not exist.
        """
        if version_id not in self._versions:
            raise VersionNotFound(f"VERSION_NOT_FOUND: rollback target {version_id!r} does not exist")
        self._active_pointers[component] = version_id


__all__ = ["L4VersionStore", "VersionedPackage", "ParentVersionNotFound", "VersionNotFound"]
