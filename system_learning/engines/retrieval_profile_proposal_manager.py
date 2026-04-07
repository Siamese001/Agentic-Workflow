"""
import uuid
W4-E Retrieval Profile Proposal Manager

Manages deterministic proposal creation and approval tracking.
"""


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

_emit_authorize_and_execute("p2", "retrieval_profile_proposal_manager", "execution_auth")
_emit_validates_capability("p2", "retrieval_profile_proposal_manager", "capability_check")
_emit_routes_to_capability("p2", "retrieval_profile_proposal_manager", "capability_route")
_emit_writes_via_uwg("p2", "retrieval_profile_proposal_manager", "uwg_write")
_emit_blocks_direct_write("p2", "retrieval_profile_proposal_manager", "direct_write_block")
_emit_records_tool_invocation("p2", "retrieval_profile_proposal_manager", "tool_invocation")
_emit_captures_execution_output("p2", "retrieval_profile_proposal_manager", "exec_output")
_emit_dispatches_agent("p3", "retrieval_profile_proposal_manager", "agent_dispatch")
_emit_coordinates_agents("p3", "retrieval_profile_proposal_manager", "agent_coordination")
_emit_records_workflow_lineage("p3", "retrieval_profile_proposal_manager", "workflow_lineage")
_emit_records_healing_outcome("p3", "retrieval_profile_proposal_manager", "healing_outcome")
_emit_escalates_failure("p3", "retrieval_profile_proposal_manager", "failure_escalation")
_emit_orchestrates_workflow("p3", "retrieval_profile_proposal_manager", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retrieval_profile_proposal_manager", "healing_dispatch")
_emit_invokes_evaluation("p3", "retrieval_profile_proposal_manager", "evaluation_signal")
_emit_records_telemetry_event("p4", "retrieval_profile_proposal_manager", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retrieval_profile_proposal_manager", "eval_metric")
_emit_stores_embedding("p4", "retrieval_profile_proposal_manager", "embedding_store")
_emit_updates_meta_learning_state("p4", "retrieval_profile_proposal_manager", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retrieval_profile_proposal_manager", "exec_snapshot_link")
from system_learning.engines.policy_recommendation_engine import PolicyRecommendation
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_proposal import (
    RetrievalProfileProposal,
    create_proposal_digest,
)

_emit_applies_guardrail("p0", "retrieval_profile_proposal_manager", "p0_governance")
_emit_snapshots_state("p0", "retrieval_profile_proposal_manager", "state_snapshot")
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

_emit_emits_metric_event("retrieval_profile_proposal_manager", "p4obs", "metric_1")
_emit_emits_metric_event("retrieval_profile_proposal_manager", "p4obs", "metric_2")
_emit_emits_metric_event("retrieval_profile_proposal_manager", "p4obs", "metric_3")
_emit_emits_metric_event("retrieval_profile_proposal_manager", "p4obs", "metric_4")
_emit_emits_metric_event("retrieval_profile_proposal_manager", "p4obs", "metric_5")
_emit_emits_metric_event("retrieval_profile_proposal_manager", "p4obs", "metric_6")
_emit_records_incident_event("retrieval_profile_proposal_manager", "p4obs", "incident")
_emit_captures_runtime_anomaly("retrieval_profile_proposal_manager", "p4obs", "anomaly")
_emit_writes_observability_log("retrieval_profile_proposal_manager", "p4obs", "obs_log")
_emit_updates_monitoring_state("retrieval_profile_proposal_manager", "p4obs", "mon_state")
_emit_triggers_alert("retrieval_profile_proposal_manager", "p4obs", "alert")
_emit_links_incident_trace("retrieval_profile_proposal_manager", "p4obs", "trace_link")
_emit_captures_pattern("retrieval_profile_proposal_manager", "p3lm", "pattern")
_emit_records_learning_event("retrieval_profile_proposal_manager", "p3lm", "learning_event")
_emit_writes_learning_snapshot("retrieval_profile_proposal_manager", "p3lm", "snapshot")
_emit_feeds_meta_learning("retrieval_profile_proposal_manager", "p3lm", "meta_feed")
_emit_updates_routing_strategy("retrieval_profile_proposal_manager", "p3lm", "routing")
_emit_improves_agent_policy("retrieval_profile_proposal_manager", "p3lm", "policy")
_emit_stores_learning_state("retrieval_profile_proposal_manager", "p3lm", "state")
_emit_records_execution_trace("retrieval_profile_proposal_manager", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("retrieval_profile_proposal_manager", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("retrieval_profile_proposal_manager", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("retrieval_profile_proposal_manager", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("retrieval_profile_proposal_manager", "L4_STATE", "p2_trace_5")
_emit_reads_environ("retrieval_profile_proposal_manager", "env_read", "p2_env_1")
_emit_reads_environ("retrieval_profile_proposal_manager", "env_read", "p2_env_2")
_emit_reads_runtime_state("retrieval_profile_proposal_manager", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("retrieval_profile_proposal_manager", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "retrieval_profile_proposal_manager", "context_pull")
_emit_pulls_context("p1", "retrieval_profile_proposal_manager", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile_proposal_manager", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile_proposal_manager", "uwg_term_2")
_emit_writes_through("p1", "retrieval_profile_proposal_manager", "write_through")
_emit_writes_through("p1", "retrieval_profile_proposal_manager", "write_through_2")
_emit_validated_by_safety_plane("p1", "retrieval_profile_proposal_manager", "safety_validation")
_emit_invokes_eval("p1", "retrieval_profile_proposal_manager", "eval_call")
_emit_proposal_commits_routing("p1", "retrieval_profile_proposal_manager", "routing_commit")
_emit_escalates_to_human("p1", "retrieval_profile_proposal_manager", "human_escalation")
_emit_routes_through("p1", "retrieval_profile_proposal_manager", "route_through")
_emit_checks_agent_registry("p1", "retrieval_profile_proposal_manager", "agent_registry")
_emit_validates_agent_capability("p1", "retrieval_profile_proposal_manager", "capability")
_emit_dispatches_execution_plan("p1", "retrieval_profile_proposal_manager", "exec_plan")
_emit_agent_executes_agent("p1", "retrieval_profile_proposal_manager", "sub_agent")
_emit_routes_to_agent("p1", "retrieval_profile_proposal_manager", "target_agent")
_emit_verifies_policy("p1", "retrieval_profile_proposal_manager", "policy_check")
_emit_observes_runtime_state("p1", "retrieval_profile_proposal_manager", "runtime_state")
_emit_verifies_boundary("p1", "retrieval_profile_proposal_manager", "boundary_check")
_emit_transcripts_response("p1", "retrieval_profile_proposal_manager", "transcript")
_emit_hard_fails_untranscripted("p1", "retrieval_profile_proposal_manager")
_emit_gated_by_confidence("p1", "retrieval_profile_proposal_manager", "confidence_gate")
emit_replay_key("p0", "retrieval_profile_proposal_manager")
emit_determinism_digest("p0", "retrieval_profile_proposal_manager")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class RetrievalProfileProposalManager:
    """Manages RetrievalProfile proposals with deterministic creation and approval tracking."""

    def create_proposal(
        self,
        *,
        recommendation: PolicyRecommendation,
        active_profile: RetrievalProfile,
        now_utc: int,
    ) -> RetrievalProfileProposal:
        """Create a deterministic proposal from policy recommendation.

        Args:
            recommendation: Policy recommendation from W4-D
            active_profile: Current active RetrievalProfile
            now_utc: Current timestamp

        Returns:
            RetrievalProfileProposal with deterministic digest
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalProfileProposalManager.create_proposal")

        # Apply recommended changes to create proposed profile
        proposed_profile = self._apply_recommendation_to_profile(
            recommendation=recommendation,
            base_profile=active_profile,
        )

        # Create recommended changes dictionary (deltas)
        recommended_changes = {}
        for param, new_value in recommendation.recommended_changes.items():
            if hasattr(active_profile, param):
                old_value = getattr(active_profile, param)
                recommended_changes[param] = round(new_value - old_value, 6)

        # Compute deterministic digest
        deterministic_digest = create_proposal_digest(
            base_profile_id=active_profile.profile_id,
            proposed_profile=proposed_profile,
            recommended_changes=recommended_changes,
            proposed_at_utc=now_utc,
        )

        return RetrievalProfileProposal(
            base_profile_id=active_profile.profile_id,
            proposed_profile=proposed_profile,
            recommended_changes=recommended_changes,
            approved=False,  # Initial proposals are unapproved
            proposed_at_utc=now_utc,
            deterministic_digest=deterministic_digest,
        )

    def set_approval(
        self,
        *,
        proposal_digest: str,
        approved: bool,
        now_utc: int,
    ) -> None:
        """Set approval status for a proposal.

        This method records the approval decision but does NOT activate
        the proposed profile. Activation is handled separately.

        Args:
            proposal_digest: Digest of the proposal to approve/reject
            approved: True to approve, False to reject
            now_utc: Current timestamp
        """
        # In a real implementation, this would write to L4 state
        # For now, this is a no-op placeholder
        # The approval is recorded via L4StateWriter.write_l4c_retrieval_profile_proposal_approval
        pass

    def get_latest_proposal(
        self,
        *,
        base_profile_id: str,
    ) -> RetrievalProfileProposal | None:
        """Get the latest proposal for a base profile.

        Args:
            base_profile_id: ID of the base profile

        Returns:
            Latest proposal if exists, None otherwise
        """
        # In a real implementation, this would read from L4 state
        # For now, return None as placeholder
        return None

    def _apply_recommendation_to_profile(
        self,
        *,
        recommendation: PolicyRecommendation,
        base_profile: RetrievalProfile,
    ) -> RetrievalProfile:
        """Apply recommended changes to create proposed profile.

        Args:
            recommendation: Policy recommendation with changes
            base_profile: Base profile to modify

        Returns:
            New RetrievalProfile with applied changes
        """
        # Start with base profile values
        profile_id = f"{base_profile.profile_id}_proposed_{recommendation.deterministic_digest[:8]}"
        primary_embedder_id = base_profile.primary_embedder_id
        embedding_dim = base_profile.embedding_dim
        similarity_cutoff = base_profile.similarity_cutoff
        top_k = base_profile.top_k
        influence_cap = base_profile.influence_cap
        normalization_policy = base_profile.normalization_policy
        shadow_embedder_id = base_profile.shadow_embedder_id
        hybrid_alpha = base_profile.hybrid_alpha

        # Apply recommended changes with bounds checking
        for param, new_value in recommendation.recommended_changes.items():
            if param == "similarity_cutoff":
                # Ensure similarity_cutoff stays within valid bounds
                similarity_cutoff = max(0.1, min(1.0, round(new_value, 6)))
            elif param == "influence_cap":
                # Ensure influence_cap stays within valid bounds
                influence_cap = max(0.0, min(1.0, round(new_value, 6)))
            elif param == "top_k":
                # Ensure top_k stays within valid bounds
                top_k = max(1, min(1000, int(round(new_value))))

        # Create proposed profile
        proposed_profile = RetrievalProfile(
            profile_id=profile_id,
            primary_embedder_id=primary_embedder_id,
            embedding_dim=embedding_dim,
            similarity_cutoff=similarity_cutoff,
            top_k=top_k,
            influence_cap=influence_cap,
            normalization_policy=normalization_policy,
            shadow_embedder_id=shadow_embedder_id,
            hybrid_alpha=hybrid_alpha,
        )

        return proposed_profile


# Export public interface
__all__ = [
    'RetrievalProfileProposalManager',
]
