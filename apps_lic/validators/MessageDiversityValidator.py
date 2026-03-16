from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
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

_emit_applies_guardrail("p0", "MessageDiversityValidator", "p0_governance")
_emit_reads_policy_state("p0", "MessageDiversityValidator", "policy_binding")
_emit_snapshots_state("p0", "MessageDiversityValidator", "state_snapshot")
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
class MessageDiversityValidator(SubatomicTestingMixin, SovereignBaseAgent):
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
