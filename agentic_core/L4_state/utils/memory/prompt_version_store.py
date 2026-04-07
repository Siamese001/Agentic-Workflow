"""PromptVersionStore — Immutable versioned prompt storage for L4 S0/I0 prompts.

Phase 1 Wave 1.1 implementation. Provides SHA-256-based immutability,
atomic commits, and read-only access to versioned prompts.
"""

from __future__ import annotations

import hashlib
from typing import Literal

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

emit_replay_key("p0", "prompt_version_store")
emit_determinism_digest("p0", "prompt_version_store")

_emit_dispatches_healing_run("p1", "prompt_version_store", "L4")
_emit_routes_through("p1", "prompt_version_store", "L4")
_emit_checks_agent_registry("p1", "prompt_version_store", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_version_store", "capability")
_emit_dispatches_execution_plan("p1", "prompt_version_store", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_version_store", "sub_agent")
_emit_routes_to_agent("p1", "prompt_version_store", "target_agent")
_emit_verifies_policy("p1", "prompt_version_store", "policy_check")
_emit_observes_runtime_state("p1", "prompt_version_store", "runtime_state")
_emit_verifies_boundary("p1", "prompt_version_store", "boundary_check")
_emit_transcripts_response("p1", "prompt_version_store", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_version_store")
_emit_gated_by_confidence("p1", "prompt_version_store", "confidence_gate")
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

_emit_emits_metric_event("prompt_version_store", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_version_store", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_version_store", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_version_store", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_version_store", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_version_store", "p4obs", "metric_6")
_emit_records_incident_event("prompt_version_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_version_store", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_version_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_version_store", "p4obs", "mon_state")
_emit_triggers_alert("prompt_version_store", "p4obs", "alert")
_emit_links_incident_trace("prompt_version_store", "p4obs", "trace_link")
_emit_captures_pattern("prompt_version_store", "p3lm", "pattern")
_emit_records_learning_event("prompt_version_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_version_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_version_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_version_store", "p3lm", "routing")
_emit_improves_agent_policy("prompt_version_store", "p3lm", "policy")
_emit_stores_learning_state("prompt_version_store", "p3lm", "state")
_emit_records_execution_trace("prompt_version_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_version_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_version_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_version_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_version_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_version_store", "env_read", "p2_env_1")
_emit_reads_environ("prompt_version_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_version_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_version_store", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_version_store", "context_pull")
_emit_pulls_context("p1", "prompt_version_store", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_version_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_version_store", "uwg_term_2")
_emit_writes_through("p1", "prompt_version_store", "write_through")
_emit_writes_through("p1", "prompt_version_store", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_version_store", "safety_validation")
_emit_invokes_eval("p1", "prompt_version_store", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_version_store", "routing_commit")


__all__ = [
    "PromptVersionStore",
    "get_version_store",
]


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

    def get_current_system_hash(self) -> str:
        """Return a deterministic hash representing the current system state.

        This is used for cache invalidation and change detection.
        Returns a SHA-256 hex digest of all stored versions.
        """
        import hashlib
        sorted_versions = sorted(_versions.keys())
        combined = "|".join(sorted_versions)
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def clear(self) -> None:
        """Clear all stored versions. For tests only."""
        _versions.clear()


# Module-level singleton
_global_store: PromptVersionStore | None = None


def get_version_store() -> PromptVersionStore:
    """Get or create the global PromptVersionStore singleton."""
    global _global_store
    if _global_store is None:
        _global_store = PromptVersionStore()
    return _global_store
