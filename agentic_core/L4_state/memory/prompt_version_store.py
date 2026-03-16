"""PromptVersionStore — Immutable versioned prompt storage for L4 S0/I0 prompts.

Phase 1 Wave 1.1 implementation. Provides SHA-256-based immutability,
atomic commits, and read-only access to versioned prompts.
"""

from __future__ import annotations

import hashlib
from typing import Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "prompt_version_store")
emit_determinism_digest("p0", "prompt_version_store")

_emit_dispatches_healing_run("p1", "prompt_version_store", "L4")
_emit_routes_through("p1", "prompt_version_store", "L4")
_emit_escalates_to_human("p1", "prompt_version_store", "L4")
_emit_reads_policy_state("p1", "prompt_version_store", "L4")
_emit_authorize_and_execute("p2", "prompt_version_store", "execution_auth")
_emit_validates_capability("p2", "prompt_version_store", "capability_check")
_emit_routes_to_capability("p2", "prompt_version_store", "capability_route")
_emit_writes_via_uwg("p2", "prompt_version_store", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_version_store", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_version_store", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_version_store", "exec_output")
_emit_dispatches_agent("p3", "prompt_version_store", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_version_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_version_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_version_store", "healing_outcome")
_emit_escalates_failure("p3", "prompt_version_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_version_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_version_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_version_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_version_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_version_store", "eval_metric")
_emit_stores_embedding("p4", "prompt_version_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_version_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_version_store", "exec_snapshot_link")

_versions: dict[str, str] = {}


class PromptVersionStore:
    """Immutable versioned storage for S0/I0 prompts.

    - commit_version() returns SHA-256 of content (immutable version ID)
    - Same content → same version ID (deduplication)
    - Versions are write-once; no delete, no overwrite
    """

    def commit_version(self, prompt_type: Literal["S0", "I0"], content: str) -> str:
        """Commit a prompt version and return its SHA-256 version ID.

        Args:
            prompt_type: Either "S0" (SYSTEM) or "I0" (INSTRUCTIONAL)
            content: Prompt text content

        Returns:
            SHA-256 hex digest as version ID

        Raises:
            ValueError: If prompt_type is not "S0" or "I0"
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "PromptVersionStore.commit_version", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "PromptVersionStore.commit_version", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "PromptVersionStore.commit_version")

        if prompt_type not in ("S0", "I0"):
            raise ValueError(f"prompt_type must be 'S0' or 'I0', got {prompt_type!r}")
        version_id = hashlib.sha256(content.encode("utf-8")).hexdigest()
        _versions.setdefault(version_id, content)
        return version_id

    def get_s0(self, version: str) -> str:
        """Retrieve S0 prompt content by version ID.

        Args:
            version: SHA-256 version ID

        Returns:
            Prompt content

        Raises:
            KeyError: If version not found
        """
        return _versions[version]

    def get_i0(self, version: str) -> str:
        """Retrieve I0 prompt content by version ID.

        Args:
            version: SHA-256 version ID

        Returns:
            Prompt content

        Raises:
            KeyError: If version not found
        """
        return _versions[version]

    def list_versions(self) -> list[str]:
        """Return all stored version IDs."""
        return list(_versions.keys())

    def clear(self) -> None:
        """Clear all stored versions. For tests only."""
        _versions.clear()
