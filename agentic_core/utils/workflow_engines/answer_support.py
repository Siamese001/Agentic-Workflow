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
