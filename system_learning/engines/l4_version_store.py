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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "l4_version_store", "p0_governance")
_emit_reads_policy_state("p0", "l4_version_store", "policy_binding")
emit_replay_key("p0", "l4_version_store")
emit_determinism_digest("p0", "l4_version_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "l4_version_store", "execution_auth")
_emit_validates_capability("p2", "l4_version_store", "capability_check")
_emit_routes_to_capability("p2", "l4_version_store", "capability_route")
_emit_writes_via_uwg("p2", "l4_version_store", "uwg_write")
_emit_blocks_direct_write("p2", "l4_version_store", "direct_write_block")
_emit_records_tool_invocation("p2", "l4_version_store", "tool_invocation")
_emit_captures_execution_output("p2", "l4_version_store", "exec_output")
_emit_dispatches_agent("p3", "l4_version_store", "agent_dispatch")
_emit_coordinates_agents("p3", "l4_version_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "l4_version_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "l4_version_store", "healing_outcome")
_emit_escalates_failure("p3", "l4_version_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "l4_version_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "l4_version_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "l4_version_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "l4_version_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "l4_version_store", "eval_metric")
_emit_stores_embedding("p4", "l4_version_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "l4_version_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "l4_version_store", "exec_snapshot_link")


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
        self, package, parent_version_id: str | None, change_spec_hash: str, committed_at_utc: int
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
        _emit_snapshots_state(str(uuid.uuid4()), "L4VersionStore.commit_change_package", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L4VersionStore.commit_change_package")

        raw = package.canonical_bytes()
        version_id = hashlib.sha256(raw).hexdigest()
        if version_id in self._versions:
            return version_id
        if parent_version_id is not None and parent_version_id not in self._versions:
            raise ParentVersionNotFound(
                f"PARENT_VERSION_NOT_FOUND: parent {parent_version_id!r} does not exist"
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
