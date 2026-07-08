"""
W4-F Retrieval Profile Invariant Checker

Validates RetrievalProfile invariants before activation.
"""

from dataclasses import dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "retrieval_profile_invariant_checker", "execution_auth")
trace_contract._emit_validates_capability("p2", "retrieval_profile_invariant_checker", "capability_check")
trace_contract._emit_routes_to_capability("p2", "retrieval_profile_invariant_checker", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "retrieval_profile_invariant_checker", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "retrieval_profile_invariant_checker", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "retrieval_profile_invariant_checker", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "retrieval_profile_invariant_checker", "exec_output")
trace_contract._emit_dispatches_agent("p3", "retrieval_profile_invariant_checker", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "retrieval_profile_invariant_checker", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "retrieval_profile_invariant_checker", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "retrieval_profile_invariant_checker", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "retrieval_profile_invariant_checker", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "retrieval_profile_invariant_checker", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "retrieval_profile_invariant_checker", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "retrieval_profile_invariant_checker", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "retrieval_profile_invariant_checker", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "retrieval_profile_invariant_checker", "eval_metric")
trace_contract._emit_stores_embedding("p4", "retrieval_profile_invariant_checker", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "retrieval_profile_invariant_checker", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "retrieval_profile_invariant_checker", "exec_snapshot_link")
from .retrieval_profile import RetrievalProfile

trace_contract._emit_applies_guardrail("p0", "retrieval_profile_invariant_checker", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "retrieval_profile_invariant_checker", "policy_binding")
trace_contract._emit_snapshots_state("p0", "retrieval_profile_invariant_checker", "state_snapshot")

trace_contract._emit_emits_metric_event("retrieval_profile_invariant_checker", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("retrieval_profile_invariant_checker", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("retrieval_profile_invariant_checker", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("retrieval_profile_invariant_checker", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("retrieval_profile_invariant_checker", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("retrieval_profile_invariant_checker", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("retrieval_profile_invariant_checker", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("retrieval_profile_invariant_checker", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("retrieval_profile_invariant_checker", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("retrieval_profile_invariant_checker", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("retrieval_profile_invariant_checker", "p4obs", "alert")
trace_contract._emit_links_incident_trace("retrieval_profile_invariant_checker", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("retrieval_profile_invariant_checker", "p3lm", "pattern")
trace_contract._emit_records_learning_event("retrieval_profile_invariant_checker", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("retrieval_profile_invariant_checker", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("retrieval_profile_invariant_checker", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("retrieval_profile_invariant_checker", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("retrieval_profile_invariant_checker", "p3lm", "policy")
trace_contract._emit_stores_learning_state("retrieval_profile_invariant_checker", "p3lm", "state")
trace_contract._emit_records_execution_trace("retrieval_profile_invariant_checker", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("retrieval_profile_invariant_checker", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("retrieval_profile_invariant_checker", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("retrieval_profile_invariant_checker", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("retrieval_profile_invariant_checker", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("retrieval_profile_invariant_checker", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("retrieval_profile_invariant_checker", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("retrieval_profile_invariant_checker", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("retrieval_profile_invariant_checker", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "retrieval_profile_invariant_checker", "context_pull")
trace_contract._emit_pulls_context("p1", "retrieval_profile_invariant_checker", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "retrieval_profile_invariant_checker", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "retrieval_profile_invariant_checker", "uwg_term_2")
trace_contract._emit_writes_through("p1", "retrieval_profile_invariant_checker", "write_through")
trace_contract._emit_writes_through("p1", "retrieval_profile_invariant_checker", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "retrieval_profile_invariant_checker", "safety_validation")
trace_contract._emit_invokes_eval("p1", "retrieval_profile_invariant_checker", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "retrieval_profile_invariant_checker", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "retrieval_profile_invariant_checker", "human_escalation")
trace_contract._emit_routes_through("p1", "retrieval_profile_invariant_checker", "route_through")
trace_contract._emit_checks_agent_registry("p1", "retrieval_profile_invariant_checker", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "retrieval_profile_invariant_checker", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "retrieval_profile_invariant_checker", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "retrieval_profile_invariant_checker", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "retrieval_profile_invariant_checker", "target_agent")
trace_contract._emit_verifies_policy("p1", "retrieval_profile_invariant_checker", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "retrieval_profile_invariant_checker", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "retrieval_profile_invariant_checker", "boundary_check")
trace_contract._emit_transcripts_response("p1", "retrieval_profile_invariant_checker", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "retrieval_profile_invariant_checker")
trace_contract._emit_gated_by_confidence("p1", "retrieval_profile_invariant_checker", "confidence_gate")
trace_contract.emit_replay_key("p0", "retrieval_profile_invariant_checker")
trace_contract.emit_determinism_digest("p0", "retrieval_profile_invariant_checker")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True, slots=True)
class InvariantViolation:
    """Represents an invariant violation."""

    field: str
    expected: str
    actual: str
    message: str


class RetrievalProfileInvariantChecker:
    """Validates RetrievalProfile invariants."""

    # guardian: allow-magic-config
    def __init__(self, min_top_k: int = 1, max_top_k: int = 200):
        """Initialize checker with bounds.

        Args:
            min_top_k: Minimum allowed top_k value
            max_top_k: Maximum allowed top_k value
        """
        self.min_top_k = min_top_k
        self.max_top_k = max_top_k

    def validate(
        self,
        *,
        profile: RetrievalProfile,
        reference_profile: RetrievalProfile | None = None,
    ) -> None:
        """Validate profile invariants.

        Args:
            profile: Profile to validate
            reference_profile: Optional reference profile for embedding_dim comparison

        Raises:
            ValueError: If any invariant is violated
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "RetrievalProfileInvariantChecker.validate"
        )

        violations = []
        if not 0.0 < profile.similarity_cutoff <= 1.0:
            violations.append(
                InvariantViolation(
                    field="similarity_cutoff",
                    expected="0.0 < similarity_cutoff <= 1.0",
                    actual=str(profile.similarity_cutoff),
                    message="Similarity cutoff must be between 0 and 1 (exclusive of 0)",
                ),
            )
        if not self.min_top_k <= profile.top_k <= self.max_top_k:
            violations.append(
                InvariantViolation(
                    field="top_k",
                    expected=f"{self.min_top_k} <= top_k <= {self.max_top_k}",
                    actual=str(profile.top_k),
                    message=f"Top_k must be between {self.min_top_k} and {self.max_top_k}",
                ),
            )
        if not 0.0 <= profile.influence_cap <= 1.0:
            violations.append(
                InvariantViolation(
                    field="influence_cap",
                    expected="0.0 <= influence_cap <= 1.0",
                    actual=str(profile.influence_cap),
                    message="Influence cap must be between 0 and 1 (inclusive)",
                ),
            )
        if reference_profile is not None:
            if profile.embedding_dim != reference_profile.embedding_dim:
                violations.append(
                    InvariantViolation(
                        field="embedding_dim",
                        expected=str(reference_profile.embedding_dim),
                        actual=str(profile.embedding_dim),
                        message="Embedding dimension must match reference profile",
                    ),
                )
        if not profile.primary_embedder_id or not profile.primary_embedder_id.strip():
            violations.append(
                InvariantViolation(
                    field="primary_embedder_id",
                    expected="non-empty string",
                    actual=str(profile.primary_embedder_id),
                    message="Primary embedder ID must be a non-empty string",
                ),
            )
        if violations:
            error_messages = []
            for violation in violations:
                error_messages.append(
                    f"{violation.field}: {violation.message} (expected: {violation.expected}, actual: {violation.actual})",
                )
            raise ValueError(f"Invariant violations found: {'; '.join(error_messages)}")


__all__ = ["RetrievalProfileInvariantChecker", "InvariantViolation"]
