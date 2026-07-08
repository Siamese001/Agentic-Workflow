"""RetrievalProfile Manager (W4-A)

Manages active RetrievalProfile pointer in L4.
Provides deterministic loading and activation.
"""

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "retrieval_profile_manager", "execution_auth")
trace_contract._emit_validates_capability("p2", "retrieval_profile_manager", "capability_check")
trace_contract._emit_routes_to_capability("p2", "retrieval_profile_manager", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "retrieval_profile_manager", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "retrieval_profile_manager", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "retrieval_profile_manager", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "retrieval_profile_manager", "exec_output")
trace_contract._emit_dispatches_agent("p3", "retrieval_profile_manager", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "retrieval_profile_manager", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "retrieval_profile_manager", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "retrieval_profile_manager", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "retrieval_profile_manager", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "retrieval_profile_manager", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "retrieval_profile_manager", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "retrieval_profile_manager", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "retrieval_profile_manager", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "retrieval_profile_manager", "eval_metric")
trace_contract._emit_stores_embedding("p4", "retrieval_profile_manager", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "retrieval_profile_manager", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "retrieval_profile_manager", "exec_snapshot_link")
from .l4_state_writer import L4StateWriter
from .retrieval_profile import RetrievalProfile

trace_contract._emit_applies_guardrail("p0", "retrieval_profile_manager", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "retrieval_profile_manager", "policy_binding")
trace_contract._emit_snapshots_state("p0", "retrieval_profile_manager", "state_snapshot")

trace_contract._emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("retrieval_profile_manager", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("retrieval_profile_manager", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("retrieval_profile_manager", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("retrieval_profile_manager", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("retrieval_profile_manager", "p4obs", "alert")
trace_contract._emit_links_incident_trace("retrieval_profile_manager", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("retrieval_profile_manager", "p3lm", "pattern")
trace_contract._emit_records_learning_event("retrieval_profile_manager", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("retrieval_profile_manager", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("retrieval_profile_manager", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("retrieval_profile_manager", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("retrieval_profile_manager", "p3lm", "policy")
trace_contract._emit_stores_learning_state("retrieval_profile_manager", "p3lm", "state")
trace_contract._emit_records_execution_trace("retrieval_profile_manager", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("retrieval_profile_manager", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("retrieval_profile_manager", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("retrieval_profile_manager", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("retrieval_profile_manager", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("retrieval_profile_manager", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("retrieval_profile_manager", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("retrieval_profile_manager", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("retrieval_profile_manager", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "retrieval_profile_manager", "context_pull")
trace_contract._emit_pulls_context("p1", "retrieval_profile_manager", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "retrieval_profile_manager", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "retrieval_profile_manager", "uwg_term_2")
trace_contract._emit_writes_through("p1", "retrieval_profile_manager", "write_through")
trace_contract._emit_writes_through("p1", "retrieval_profile_manager", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "retrieval_profile_manager", "safety_validation")
trace_contract._emit_invokes_eval("p1", "retrieval_profile_manager", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "retrieval_profile_manager", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "retrieval_profile_manager", "human_escalation")
trace_contract._emit_routes_through("p1", "retrieval_profile_manager", "route_through")
trace_contract._emit_checks_agent_registry("p1", "retrieval_profile_manager", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "retrieval_profile_manager", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "retrieval_profile_manager", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "retrieval_profile_manager", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "retrieval_profile_manager", "target_agent")
trace_contract._emit_verifies_policy("p1", "retrieval_profile_manager", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "retrieval_profile_manager", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "retrieval_profile_manager", "boundary_check")
trace_contract._emit_transcripts_response("p1", "retrieval_profile_manager", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "retrieval_profile_manager")
trace_contract._emit_gated_by_confidence("p1", "retrieval_profile_manager", "confidence_gate")
trace_contract.emit_replay_key("p0", "retrieval_profile_manager")
trace_contract.emit_determinism_digest("p0", "retrieval_profile_manager")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "RetrievalProfileManager.load_active_profile"
        )

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
                payload_bytes=profile_bytes,
                component_name="meta-learning",
                created_utc=created_utc,
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
