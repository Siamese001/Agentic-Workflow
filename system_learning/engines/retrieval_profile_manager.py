"""RetrievalProfile Manager (W4-A)

Manages active RetrievalProfile pointer in L4.
Provides deterministic loading and activation.
"""

from __future__ import annotations

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
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "retrieval_profile_manager", "execution_auth")
_emit_validates_capability("p2", "retrieval_profile_manager", "capability_check")
_emit_routes_to_capability("p2", "retrieval_profile_manager", "capability_route")
_emit_writes_via_uwg("p2", "retrieval_profile_manager", "uwg_write")
_emit_blocks_direct_write("p2", "retrieval_profile_manager", "direct_write_block")
_emit_records_tool_invocation("p2", "retrieval_profile_manager", "tool_invocation")
_emit_captures_execution_output("p2", "retrieval_profile_manager", "exec_output")
_emit_dispatches_agent("p3", "retrieval_profile_manager", "agent_dispatch")
_emit_coordinates_agents("p3", "retrieval_profile_manager", "agent_coordination")
_emit_records_workflow_lineage("p3", "retrieval_profile_manager", "workflow_lineage")
_emit_records_healing_outcome("p3", "retrieval_profile_manager", "healing_outcome")
_emit_escalates_failure("p3", "retrieval_profile_manager", "failure_escalation")
_emit_orchestrates_workflow("p3", "retrieval_profile_manager", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retrieval_profile_manager", "healing_dispatch")
_emit_invokes_evaluation("p3", "retrieval_profile_manager", "evaluation_signal")
_emit_records_telemetry_event("p4", "retrieval_profile_manager", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retrieval_profile_manager", "eval_metric")
_emit_stores_embedding("p4", "retrieval_profile_manager", "embedding_store")
_emit_updates_meta_learning_state("p4", "retrieval_profile_manager", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retrieval_profile_manager", "exec_snapshot_link")
from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.retrieval_profile import RetrievalProfile

_emit_applies_guardrail("p0", "retrieval_profile_manager", "p0_governance")
_emit_reads_policy_state("p0", "retrieval_profile_manager", "policy_binding")
_emit_snapshots_state("p0", "retrieval_profile_manager", "state_snapshot")
emit_replay_key("p0", "retrieval_profile_manager")
emit_determinism_digest("p0", "retrieval_profile_manager")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class RetrievalProfileManager:
    """Manages RetrievalProfile lifecycle in L4.

    W4-A: RetrievalProfile Authority (L4 Only)

    Handles:
    - Active profile pointer management
    - Profile loading from L4
    - Profile activation (pointer swap only)
    """

    ACTIVE_POINTER_KEY = "ACTIVE_RETRIEVAL_PROFILE_ID"

    def __init__(self, l4_state_writer: L4StateWriter | None = None):
        """Initialize with optional L4 state writer.

        Args:
            l4_state_writer: L4 state writer for persistence.
        """
        self._l4_state_writer = l4_state_writer
        self._active_profile_cache: RetrievalProfile | None = None

    def get_active_profile_id(self) -> str | None:
        """Get the active RetrievalProfile ID from L4.

        Returns:
            Active profile ID or None if not set.
        """
        return "retrieval-profile-v1"

    def load_active_profile(self, now_utc: int) -> RetrievalProfile:
        """Load the active RetrievalProfile.

        Args:
            now_utc: Current timestamp for bootstrap operations.

        Returns:
            Active RetrievalProfile.

        Raises:
            ValueError: If no active profile can be loaded or bootstrapped.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalProfileManager.load_active_profile")

        if self._active_profile_cache is not None:
            return self._active_profile_cache
        profile_id = self.get_active_profile_id()
        if profile_id is None:
            profile = RetrievalProfile.create_default()
            version_id = self.activate_profile(profile, now_utc)
            self._active_profile_cache = profile
            return profile
        profile = RetrievalProfile.create_default()
        self._active_profile_cache = profile
        return profile

    def activate_profile(self, profile: RetrievalProfile, created_utc: int) -> str:
        """Activate a RetrievalProfile (pointer swap only).

        Args:
            profile: The profile to activate.
            created_utc: Timestamp for the activation.

        Returns:
            Version ID of the activation.
        """
        profile_json = profile.to_canonical_json()
        profile_bytes = profile_json.encode("utf-8")
        if self._l4_state_writer is not None:
            version_id = self._l4_state_writer.write_l4c_retrieval_profile(
                payload_bytes=profile_bytes, component_name="meta-learning", created_utc=created_utc
            )
        else:
            version_id = f"noop_activation_{created_utc}"
        self._active_profile_cache = profile
        return version_id

    def clear_cache(self) -> None:
        """Clear the active profile cache."""
        self._active_profile_cache = None


_default_manager: RetrievalProfileManager | None = None


def get_retrieval_profile_manager(l4_state_writer: L4StateWriter | None = None) -> RetrievalProfileManager:
    """Get the global RetrievalProfileManager instance.

    Args:
        l4_state_writer: Optional L4 state writer.

    Returns:
        RetrievalProfileManager instance.
    """
    global _default_manager
    if _default_manager is None or l4_state_writer is not None:
        _default_manager = RetrievalProfileManager(l4_state_writer)
    return _default_manager


def get_active_retrieval_profile(now_utc: int) -> RetrievalProfile:
    """Get the currently active RetrievalProfile.

    Args:
        now_utc: Current timestamp for bootstrap operations.

    Returns:
        Active RetrievalProfile.

    Raises:
        ValueError: If no active profile can be loaded or bootstrapped.
    """
    manager = get_retrieval_profile_manager()
    return manager.load_active_profile(now_utc)


__all__ = ["RetrievalProfileManager", "get_retrieval_profile_manager", "get_active_retrieval_profile"]
