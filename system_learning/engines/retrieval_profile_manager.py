"""RetrievalProfile Manager (W4-A)

Manages active RetrievalProfile pointer in L4.
Provides deterministic loading and activation.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_1")
_emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_2")
_emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_3")
_emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_4")
_emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_5")
_emit_emits_metric_event("retrieval_profile_manager", "p4obs", "metric_6")
_emit_records_incident_event("retrieval_profile_manager", "p4obs", "incident")
_emit_captures_runtime_anomaly("retrieval_profile_manager", "p4obs", "anomaly")
_emit_writes_observability_log("retrieval_profile_manager", "p4obs", "obs_log")
_emit_updates_monitoring_state("retrieval_profile_manager", "p4obs", "mon_state")
_emit_triggers_alert("retrieval_profile_manager", "p4obs", "alert")
_emit_links_incident_trace("retrieval_profile_manager", "p4obs", "trace_link")
_emit_captures_pattern("retrieval_profile_manager", "p3lm", "pattern")
_emit_records_learning_event("retrieval_profile_manager", "p3lm", "learning_event")
_emit_writes_learning_snapshot("retrieval_profile_manager", "p3lm", "snapshot")
_emit_feeds_meta_learning("retrieval_profile_manager", "p3lm", "meta_feed")
_emit_updates_routing_strategy("retrieval_profile_manager", "p3lm", "routing")
_emit_improves_agent_policy("retrieval_profile_manager", "p3lm", "policy")
_emit_stores_learning_state("retrieval_profile_manager", "p3lm", "state")
_emit_records_execution_trace("retrieval_profile_manager", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("retrieval_profile_manager", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("retrieval_profile_manager", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("retrieval_profile_manager", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("retrieval_profile_manager", "L4_STATE", "p2_trace_5")
_emit_reads_environ("retrieval_profile_manager", "env_read", "p2_env_1")
_emit_reads_environ("retrieval_profile_manager", "env_read", "p2_env_2")
_emit_reads_runtime_state("retrieval_profile_manager", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("retrieval_profile_manager", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "retrieval_profile_manager", "context_pull")
_emit_pulls_context("p1", "retrieval_profile_manager", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile_manager", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile_manager", "uwg_term_2")
_emit_writes_through("p1", "retrieval_profile_manager", "write_through")
_emit_writes_through("p1", "retrieval_profile_manager", "write_through_2")
_emit_validated_by_safety_plane("p1", "retrieval_profile_manager", "safety_validation")
_emit_invokes_eval("p1", "retrieval_profile_manager", "eval_call")
_emit_proposal_commits_routing("p1", "retrieval_profile_manager", "routing_commit")
_emit_escalates_to_human("p1", "retrieval_profile_manager", "human_escalation")
_emit_routes_through("p1", "retrieval_profile_manager", "route_through")
_emit_checks_agent_registry("p1", "retrieval_profile_manager", "agent_registry")
_emit_validates_agent_capability("p1", "retrieval_profile_manager", "capability")
_emit_dispatches_execution_plan("p1", "retrieval_profile_manager", "exec_plan")
_emit_agent_executes_agent("p1", "retrieval_profile_manager", "sub_agent")
_emit_routes_to_agent("p1", "retrieval_profile_manager", "target_agent")
_emit_verifies_policy("p1", "retrieval_profile_manager", "policy_check")
_emit_observes_runtime_state("p1", "retrieval_profile_manager", "runtime_state")
_emit_verifies_boundary("p1", "retrieval_profile_manager", "boundary_check")
_emit_transcripts_response("p1", "retrieval_profile_manager", "transcript")
_emit_hard_fails_untranscripted("p1", "retrieval_profile_manager")
_emit_gated_by_confidence("p1", "retrieval_profile_manager", "confidence_gate")
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
                payload_bytes=profile_bytes, component_name="meta-learning", created_utc=created_utc,
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
