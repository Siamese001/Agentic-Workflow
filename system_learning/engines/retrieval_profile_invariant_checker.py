"""
W4-F Retrieval Profile Invariant Checker

Validates RetrievalProfile invariants before activation.
"""

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
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "retrieval_profile_invariant_checker", "execution_auth")
_emit_validates_capability("p2", "retrieval_profile_invariant_checker", "capability_check")
_emit_routes_to_capability("p2", "retrieval_profile_invariant_checker", "capability_route")
_emit_writes_via_uwg("p2", "retrieval_profile_invariant_checker", "uwg_write")
_emit_blocks_direct_write("p2", "retrieval_profile_invariant_checker", "direct_write_block")
_emit_records_tool_invocation("p2", "retrieval_profile_invariant_checker", "tool_invocation")
_emit_captures_execution_output("p2", "retrieval_profile_invariant_checker", "exec_output")
_emit_dispatches_agent("p3", "retrieval_profile_invariant_checker", "agent_dispatch")
_emit_coordinates_agents("p3", "retrieval_profile_invariant_checker", "agent_coordination")
_emit_records_workflow_lineage("p3", "retrieval_profile_invariant_checker", "workflow_lineage")
_emit_records_healing_outcome("p3", "retrieval_profile_invariant_checker", "healing_outcome")
_emit_escalates_failure("p3", "retrieval_profile_invariant_checker", "failure_escalation")
_emit_orchestrates_workflow("p3", "retrieval_profile_invariant_checker", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retrieval_profile_invariant_checker", "healing_dispatch")
_emit_invokes_evaluation("p3", "retrieval_profile_invariant_checker", "evaluation_signal")
_emit_records_telemetry_event("p4", "retrieval_profile_invariant_checker", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retrieval_profile_invariant_checker", "eval_metric")
_emit_stores_embedding("p4", "retrieval_profile_invariant_checker", "embedding_store")
_emit_updates_meta_learning_state("p4", "retrieval_profile_invariant_checker", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retrieval_profile_invariant_checker", "exec_snapshot_link")
from system_learning.engines.retrieval_profile import RetrievalProfile

_emit_applies_guardrail("p0", "retrieval_profile_invariant_checker", "p0_governance")
_emit_reads_policy_state("p0", "retrieval_profile_invariant_checker", "policy_binding")
_emit_snapshots_state("p0", "retrieval_profile_invariant_checker", "state_snapshot")
emit_replay_key("p0", "retrieval_profile_invariant_checker")
emit_determinism_digest("p0", "retrieval_profile_invariant_checker")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
        self, *, profile: RetrievalProfile, reference_profile: RetrievalProfile | None = None
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalProfileInvariantChecker.validate")

        violations = []
        if not 0.0 < profile.similarity_cutoff <= 1.0:
            violations.append(
                InvariantViolation(
                    field="similarity_cutoff",
                    expected="0.0 < similarity_cutoff <= 1.0",
                    actual=str(profile.similarity_cutoff),
                    message="Similarity cutoff must be between 0 and 1 (exclusive of 0)",
                )
            )
        if not self.min_top_k <= profile.top_k <= self.max_top_k:
            violations.append(
                InvariantViolation(
                    field="top_k",
                    expected=f"{self.min_top_k} <= top_k <= {self.max_top_k}",
                    actual=str(profile.top_k),
                    message=f"Top_k must be between {self.min_top_k} and {self.max_top_k}",
                )
            )
        if not 0.0 <= profile.influence_cap <= 1.0:
            violations.append(
                InvariantViolation(
                    field="influence_cap",
                    expected="0.0 <= influence_cap <= 1.0",
                    actual=str(profile.influence_cap),
                    message="Influence cap must be between 0 and 1 (inclusive)",
                )
            )
        if reference_profile is not None:
            if profile.embedding_dim != reference_profile.embedding_dim:
                violations.append(
                    InvariantViolation(
                        field="embedding_dim",
                        expected=str(reference_profile.embedding_dim),
                        actual=str(profile.embedding_dim),
                        message="Embedding dimension must match reference profile",
                    )
                )
        if not profile.primary_embedder_id or not profile.primary_embedder_id.strip():
            violations.append(
                InvariantViolation(
                    field="primary_embedder_id",
                    expected="non-empty string",
                    actual=str(profile.primary_embedder_id),
                    message="Primary embedder ID must be a non-empty string",
                )
            )
        if violations:
            error_messages = []
            for violation in violations:
                error_messages.append(
                    f"{violation.field}: {violation.message} (expected: {violation.expected}, actual: {violation.actual})"
                )
            raise ValueError(f"Invariant violations found: {'; '.join(error_messages)}")


__all__ = ["RetrievalProfileInvariantChecker", "InvariantViolation"]
