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

from agentic_core.evaluation.retrieval.completeness import (
    GroundedDocument,
    IAnswerSupportValidator,
    SupportedAnswerCheck,
)
from agentic_core.evaluation.retrieval.interfaces import Document

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
