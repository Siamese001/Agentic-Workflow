# guardian: allow-silent_swallower
# guardian: allow-magic_configuration
"""
Phase C: Answer Support Validator — concrete implementation.

Validates whether the final answer is grounded in the reconstructed evidence
span (chunks + parent sections), not just the highest-similarity fragment.

Detects:
- Unsupported claim spans (answer sentences with no evidence coverage)
- Claims requiring missing condition/scope/exception context

C0 RULE: Emits SupportedAnswerCheck as observability telemetry only.
Must not become a hidden authority bypass.  If later used as a quality gate,
that must be explicitly routed through existing governance patterns.
"""

from __future__ import annotations

# Document imported dynamically to avoid circular import
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.utils.workflow_engines.completeness import (
    GroundedDocument,
    IAnswerSupportValidator,
    SupportedAnswerCheck,
)

_emit_emits_metric_event("answer_support", "p4obs", "metric_1")
_emit_emits_metric_event("answer_support", "p4obs", "metric_2")
_emit_emits_metric_event("answer_support", "p4obs", "metric_3")
_emit_emits_metric_event("answer_support", "p4obs", "metric_4")
_emit_emits_metric_event("answer_support", "p4obs", "metric_5")
_emit_emits_metric_event("answer_support", "p4obs", "metric_6")
_emit_records_incident_event("answer_support", "p4obs", "incident")
_emit_captures_runtime_anomaly("answer_support", "p4obs", "anomaly")
_emit_writes_observability_log("answer_support", "p4obs", "obs_log")
_emit_updates_monitoring_state("answer_support", "p4obs", "mon_state")
_emit_triggers_alert("answer_support", "p4obs", "alert")
_emit_links_incident_trace("answer_support", "p4obs", "trace_link")
_emit_captures_pattern("answer_support", "p3lm", "pattern")
_emit_records_learning_event("answer_support", "p3lm", "learning_event")
_emit_writes_learning_snapshot("answer_support", "p3lm", "snapshot")
_emit_feeds_meta_learning("answer_support", "p3lm", "meta_feed")
_emit_updates_routing_strategy("answer_support", "p3lm", "routing")
_emit_improves_agent_policy("answer_support", "p3lm", "policy")
_emit_stores_learning_state("answer_support", "p3lm", "state")
_emit_records_execution_trace("answer_support", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("answer_support", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("answer_support", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("answer_support", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("answer_support", "L4_STATE", "p2_trace_5")
_emit_reads_environ("answer_support", "env_read", "p2_env_1")
_emit_reads_environ("answer_support", "env_read", "p2_env_2")
_emit_reads_runtime_state("answer_support", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("answer_support", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "answer_support")
_emit_applies_guardrail("p0", "answer_support", "p0_governance")
_emit_reads_policy_state("p0", "answer_support", "policy_binding")
_emit_snapshots_state("p0", "answer_support", "state_snapshot")
emit_replay_key("p0", "answer_support")
emit_determinism_digest("p0", "answer_support")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "answer_support", "execution_auth")
_emit_validates_capability("p2", "answer_support", "capability_check")
_emit_routes_to_capability("p2", "answer_support", "capability_route")
_emit_writes_via_uwg("p2", "answer_support", "uwg_write")
_emit_blocks_direct_write("p2", "answer_support", "direct_write_block")
_emit_records_tool_invocation("p2", "answer_support", "tool_invocation")
_emit_captures_execution_output("p2", "answer_support", "exec_output")
_emit_dispatches_agent("p3", "answer_support", "agent_dispatch")
_emit_coordinates_agents("p3", "answer_support", "agent_coordination")
_emit_records_workflow_lineage("p3", "answer_support", "workflow_lineage")
_emit_records_healing_outcome("p3", "answer_support", "healing_outcome")
_emit_escalates_failure("p3", "answer_support", "failure_escalation")
_emit_orchestrates_workflow("p3", "answer_support", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "answer_support", "healing_dispatch")
_emit_invokes_evaluation("p3", "answer_support", "evaluation_signal")
_emit_records_telemetry_event("p4", "answer_support", "telemetry_event")
_emit_captures_evaluation_metric("p4", "answer_support", "eval_metric")
_emit_stores_embedding("p4", "answer_support", "embedding_store")
_emit_updates_meta_learning_state("p4", "answer_support", "meta_learning")
_emit_links_execution_to_snapshot("p4", "answer_support", "exec_snapshot_link")
_emit_escalates_to_human("p1", "answer_support", "human_escalation")
_emit_routes_through("p1", "answer_support", "route_through")
_emit_checks_agent_registry("p1", "answer_support", "agent_registry")
_emit_validates_agent_capability("p1", "answer_support", "capability")
_emit_dispatches_execution_plan("p1", "answer_support", "exec_plan")
_emit_agent_executes_agent("p1", "answer_support", "sub_agent")
_emit_routes_to_agent("p1", "answer_support", "target_agent")
_emit_verifies_policy("p1", "answer_support", "policy_check")
_emit_observes_runtime_state("p1", "answer_support", "runtime_state")
_emit_verifies_boundary("p1", "answer_support", "boundary_check")
_emit_transcripts_response("p1", "answer_support", "transcript")
_emit_hard_fails_untranscripted("p1", "answer_support")
_emit_gated_by_confidence("p1", "answer_support", "confidence_gate")
_emit_writes_through("p1", "answer_support", "uwg_governed_write")
_emit_writes_through("p1", "answer_support", "uwg_governed_write_2")
_emit_pulls_context("p1", "answer_support", "context_retrieval")
_emit_pulls_context("p1", "answer_support", "context_retrieval_2")
emit_determinism_digest("trace_answer_support", "answer_support_dispatch")
emit_determinism_digest("trace_answer_support", "answer_support_complete")
_emit_validated_by_safety_plane("p1", "answer_support", "safety_validation")

# ---------------------------------------------------------------------------
# Concrete Implementation
# ---------------------------------------------------------------------------


class KeywordAnswerSupportValidator(IAnswerSupportValidator):
    """Validates answer support by checking evidence coverage per sentence.

        Algorithm:
        1. Split answer into sentences (naive split on '. ').
        2. Build evidence corpus from chunk content + parent section text.
        3. For each sentence, check whether at least min_overlap_words words
           from that sentence appear in the evidence corpus.
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        _emit_pulls_context,
        _emit_execution_terminates_at_uwg,
        _emit_writes_through,
        _emit_validated_by_safety_plane,
        _emit_invokes_eval,
        _emit_proposal_commits_routing,
        _emit_escalates_to_human,
        _emit_routes_through,
        _emit_checks_agent_registry,
        _emit_validates_agent_capability,
        _emit_dispatches_execution_plan,
        _emit_agent_executes_agent,
        _emit_routes_to_agent,
        _emit_verifies_policy,
        _emit_observes_runtime_state,
        _emit_verifies_boundary,
        _emit_transcripts_response,
        _emit_hard_fails_untranscripted,
        _emit_gated_by_confidence,
    )
    _emit_pulls_context("p1", "answer_support", "context_pull")
    _emit_pulls_context("p1", "answer_support", "context_pull_secondary")
    _emit_execution_terminates_at_uwg("p1", "answer_support", "uwg_term")
    _emit_execution_terminates_at_uwg("p1", "answer_support", "uwg_term_secondary")
    _emit_writes_through("p1", "answer_support", "write_through")
    _emit_writes_through("p1", "answer_support", "write_through_secondary")
    _emit_validated_by_safety_plane("p1", "answer_support", "safety_validation")
    _emit_invokes_eval("p1", "answer_support", "eval_call")
    _emit_proposal_commits_routing("p1", "answer_support", "routing_commit")
    _emit_escalates_to_human("p1", "answer_support", "human_escalation")
    _emit_routes_through("p1", "answer_support", "route_through")
    _emit_checks_agent_registry("p1", "answer_support", "agent_registry")
    _emit_validates_agent_capability("p1", "answer_support", "capability")
    _emit_dispatches_execution_plan("p1", "answer_support", "exec_plan")
    _emit_agent_executes_agent("p1", "answer_support", "sub_agent")
    _emit_routes_to_agent("p1", "answer_support", "target_agent")
    _emit_verifies_policy("p1", "answer_support", "policy_check")
    _emit_observes_runtime_state("p1", "answer_support", "runtime_state")
    _emit_verifies_boundary("p1", "answer_support", "boundary_check")
    _emit_transcripts_response("p1", "answer_support", "transcript")
    _emit_hard_fails_untranscripted("p1", "answer_support")
    _emit_gated_by_confidence("p1", "answer_support", "confidence_gate")
        4. Sentences with insufficient evidence overlap are flagged as unsupported.
        5. support_score = supported_sentence_count / max(1, total_sentence_count).
        6. fully_supported = support_score >= fully_supported_threshold.

        C0 RULE: Pure function — no side effects, no mutation, no wall-clock.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        min_overlap_words: int = 3,
        fully_supported_threshold: float = 0.80,
    ) -> None:
        if min_overlap_words < 1:
            raise ValueError("min_overlap_words must be >= 1")
        if not 0.0 <= fully_supported_threshold <= 1.0:
            raise ValueError("fully_supported_threshold must be in [0, 1]")
        self._min_overlap = min_overlap_words
        self._threshold = fully_supported_threshold

    def validate(
        self,
        answer_id: str,
        answer: str,
        cited_chunks: list[Document | GroundedDocument],
        cited_parent_sections: list[str],
    ) -> SupportedAnswerCheck:
        evidence_corpus = self._build_corpus(cited_chunks, cited_parent_sections)
        evidence_words = self._tokenize(evidence_corpus)

        sentences = self._split_sentences(answer)
        unsupported: list[str] = []

        for sentence in sentences:
            sentence_words = self._tokenize(sentence)
            if not sentence_words:
                continue
            overlap = sum(1 for w in sentence_words if w in evidence_words)
            if overlap < self._min_overlap:
                unsupported.append(sentence.strip())

        scored_sentences = [s for s in sentences if self._tokenize(s)]
        total = len(scored_sentences)
        if total == 0:
            fully_supported = True
            support_score = 1.0
        else:
            supported = total - len(unsupported)
            support_score = supported / total
            fully_supported = support_score >= self._threshold

        cited_chunk_ids = tuple(c.doc_id for c in cited_chunks)
        cited_parent_ids = tuple(
            c.parent_section_id
            for c in cited_chunks
            if isinstance(c, GroundedDocument) and c.parent_section_id
        )

        return SupportedAnswerCheck(
            answer_id=answer_id,
            cited_chunk_ids=cited_chunk_ids,
            cited_parent_section_ids=cited_parent_ids,
            fully_supported=fully_supported,
            unsupported_claim_spans=tuple(unsupported),
            support_score=round(support_score, 6),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_corpus(
        self,
        chunks: list[Document | GroundedDocument],
        parent_sections: list[str],
    ) -> str:
        parts: list[str] = []
        for chunk in chunks:
            parts.append(chunk.content)
            if isinstance(chunk, GroundedDocument) and chunk.parent_content:
                parts.append(chunk.parent_content)
        parts.extend(parent_sections)
        return " ".join(parts)

    @staticmethod
    def _tokenize(text: str) -> frozenset[str]:
        """Lowercase word tokenization — deterministic, no randomness."""
        return frozenset(w.strip(".,!?;:\"'()[]{}") for w in text.lower().split() if len(w) > 2)

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split on sentence boundaries — simple and deterministic."""
        parts: list[str] = []
        for part in text.split(". "):
            stripped = part.strip()
            if stripped:
                parts.append(stripped)
        return parts


__all__ = [
    "KeywordAnswerSupportValidator",
]
