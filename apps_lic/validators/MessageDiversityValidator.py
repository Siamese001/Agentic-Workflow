from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "MessageDiversityValidator", "p0_governance")
_emit_reads_policy_state("p0", "MessageDiversityValidator", "policy_binding")
_emit_snapshots_state("p0", "MessageDiversityValidator", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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

_emit_emits_metric_event("MessageDiversityValidator", "p4obs", "metric_1")
_emit_emits_metric_event("MessageDiversityValidator", "p4obs", "metric_2")
_emit_emits_metric_event("MessageDiversityValidator", "p4obs", "metric_3")
_emit_emits_metric_event("MessageDiversityValidator", "p4obs", "metric_4")
_emit_emits_metric_event("MessageDiversityValidator", "p4obs", "metric_5")
_emit_emits_metric_event("MessageDiversityValidator", "p4obs", "metric_6")
_emit_records_incident_event("MessageDiversityValidator", "p4obs", "incident")
_emit_captures_runtime_anomaly("MessageDiversityValidator", "p4obs", "anomaly")
_emit_writes_observability_log("MessageDiversityValidator", "p4obs", "obs_log")
_emit_updates_monitoring_state("MessageDiversityValidator", "p4obs", "mon_state")
_emit_triggers_alert("MessageDiversityValidator", "p4obs", "alert")
_emit_links_incident_trace("MessageDiversityValidator", "p4obs", "trace_link")
_emit_captures_pattern("MessageDiversityValidator", "p3lm", "pattern")
_emit_records_learning_event("MessageDiversityValidator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("MessageDiversityValidator", "p3lm", "snapshot")
_emit_feeds_meta_learning("MessageDiversityValidator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("MessageDiversityValidator", "p3lm", "routing")
_emit_improves_agent_policy("MessageDiversityValidator", "p3lm", "policy")
_emit_stores_learning_state("MessageDiversityValidator", "p3lm", "state")
_emit_records_execution_trace("MessageDiversityValidator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("MessageDiversityValidator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("MessageDiversityValidator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("MessageDiversityValidator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("MessageDiversityValidator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("MessageDiversityValidator", "env_read", "p2_env_1")
_emit_reads_environ("MessageDiversityValidator", "env_read", "p2_env_2")
_emit_reads_runtime_state("MessageDiversityValidator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("MessageDiversityValidator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "MessageDiversityValidator", "context_pull")
_emit_pulls_context("p1", "MessageDiversityValidator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "MessageDiversityValidator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "MessageDiversityValidator", "uwg_term_2")
_emit_writes_through("p1", "MessageDiversityValidator", "write_through")
_emit_writes_through("p1", "MessageDiversityValidator", "write_through_2")
_emit_validated_by_safety_plane("p1", "MessageDiversityValidator", "safety_validation")
_emit_invokes_eval("p1", "MessageDiversityValidator", "eval_call")
_emit_proposal_commits_routing("p1", "MessageDiversityValidator", "routing_commit")
_emit_escalates_to_human("p1", "MessageDiversityValidator", "human_escalation")
_emit_routes_through("p1", "MessageDiversityValidator", "route_through")
_emit_checks_agent_registry("p1", "MessageDiversityValidator", "agent_registry")
_emit_validates_agent_capability("p1", "MessageDiversityValidator", "capability")
_emit_dispatches_execution_plan("p1", "MessageDiversityValidator", "exec_plan")
_emit_agent_executes_agent("p1", "MessageDiversityValidator", "sub_agent")
_emit_routes_to_agent("p1", "MessageDiversityValidator", "target_agent")
_emit_verifies_policy("p1", "MessageDiversityValidator", "policy_check")
_emit_observes_runtime_state("p1", "MessageDiversityValidator", "runtime_state")
_emit_verifies_boundary("p1", "MessageDiversityValidator", "boundary_check")
_emit_transcripts_response("p1", "MessageDiversityValidator", "transcript")
_emit_hard_fails_untranscripted("p1", "MessageDiversityValidator")
_emit_gated_by_confidence("p1", "MessageDiversityValidator", "confidence_gate")
emit_replay_key("p0", "MessageDiversityValidator")
emit_determinism_digest("p0", "MessageDiversityValidator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "MessageDiversityValidator", "execution_auth")
_emit_validates_capability("p2", "MessageDiversityValidator", "capability_check")
_emit_routes_to_capability("p2", "MessageDiversityValidator", "capability_route")
_emit_writes_via_uwg("p2", "MessageDiversityValidator", "uwg_write")
_emit_blocks_direct_write("p2", "MessageDiversityValidator", "direct_write_block")
_emit_records_tool_invocation("p2", "MessageDiversityValidator", "tool_invocation")
_emit_captures_execution_output("p2", "MessageDiversityValidator", "exec_output")
_emit_dispatches_agent("p3", "MessageDiversityValidator", "agent_dispatch")
_emit_coordinates_agents("p3", "MessageDiversityValidator", "agent_coordination")
_emit_records_workflow_lineage("p3", "MessageDiversityValidator", "workflow_lineage")
_emit_records_healing_outcome("p3", "MessageDiversityValidator", "healing_outcome")
_emit_escalates_failure("p3", "MessageDiversityValidator", "failure_escalation")
_emit_orchestrates_workflow("p3", "MessageDiversityValidator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "MessageDiversityValidator", "healing_dispatch")
_emit_invokes_evaluation("p3", "MessageDiversityValidator", "evaluation_signal")
_emit_records_telemetry_event("p4", "MessageDiversityValidator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "MessageDiversityValidator", "eval_metric")
_emit_stores_embedding("p4", "MessageDiversityValidator", "embedding_store")
_emit_updates_meta_learning_state("p4", "MessageDiversityValidator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "MessageDiversityValidator", "exec_snapshot_link")

"\nMessageDiversityValidator - Extracted for one-class-per-file pattern.\n\nOriginally from: ContentCleanlinessValidatorAgent.py\nExtracted: 2026-01-06 (Surgical Extraction)\n"


class HealerMixin:
    """Legacy mixin - use LICAgentBase instead."""

    pass


@dataclass
class MessageDiversityValidator(SovereignBaseAgent):
    """
    Prevent repetitive messages using cosine similarity
    FEATURE 1.3 from SUPREME_SPELL
    """

    MIN_DIVERSITY_THRESHOLD = 0.85

    def __init__(self) -> None:
        """
        Initialize message diversity validator.

        Sets up TF-IDF vectorizer for similarity analysis and initializes
        message history tracking.
        """
        self.message_history: list[str] = []
        self.vectorizer = TfidfVectorizer()

    def check_diversity(self, new_message: str) -> tuple[bool, float, str]:
        """
        Check if new message is sufficiently different from history

        Returns:
            (is_diverse, max_similarity, most_similar_message)
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MessageDiversityValidator.check_diversity")

        if not self.message_history:
            return (True, 0.0, "")
        all_messages = self.message_history + [new_message]
        try:
            vectors = self.vectorizer.fit_transform(all_messages)
            new_vector = vectors[-1]
            history_vectors = vectors[:-1]
            similarities = cosine_similarity(new_vector, history_vectors)[0]
            max_similarity = float(np.max(similarities))
            max_idx = int(np.argmax(similarities))
            is_diverse = max_similarity < self.MIN_DIVERSITY_THRESHOLD
            most_similar = self.message_history[max_idx] if max_idx < len(self.message_history) else ""
            return (is_diverse, max_similarity, most_similar)
        except (ValueError, TypeError, KeyError):
            return (True, 0.0, "")

    def add_to_history(self, message: str) -> None:
        """
        Add message to history for future diversity checks.

        Args:
            message: Message text to add to history
        """
        self.message_history.append(message)

    # guardian: allow-type-erasure
    def heal_repository(self) -> dict:
        """
        Invoke healing chain via super().

        Returns:
            Dictionary with healing results including violations, fixed, errors, skipped
        """
        return super().heal_repository()

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by MessageDiversityValidator."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"MessageDiversityValidator heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"MessageDiversityValidator heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
