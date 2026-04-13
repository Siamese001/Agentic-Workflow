"""Evidence Contract Builder.

Citation slip compilation, provenance verification, and precise context packet generation.

Architecture reference:
  - C5_Retrieval_Prompt_Assembly.md §C0.3 Evidence Shaping / §C0.4 Evidence Contract
  - 00C_index_materialization_runtime_handoff.md §Anchors (provenance, citations)

Changes from initial version:
  - VerifiedChunk dataclass: granular per-chunk evidence with must_use flag,
    contradiction_flag, citation_anchor, and support_score.
  - EvidenceContract extended: coverage_score, gaps, contradiction_status,
    abstain_recommended, next_action_hint, replay_metadata.
  - Must-use / optional chunk classification per C0.4.
  - Contradiction detection across must-use chunks.
  - Abstain path: when coverage is below threshold or conflict is severe.
  - replay_key / policy_hash propagated from RecallResult metadata.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from tqdm import tqdm

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclass
class Citation:
    """Individual citation anchor.

    Attributes
    ----------
    doc_id : str
        Chunk identifier.
    content_snippet : str
        First 200 characters of the chunk's raw text.
    source : str
        Retrieval source label (``"dense"``, ``"sparse"``, ``"both"``).
    confidence : float
        Rerank score for this citation.
    citation_anchor : str
        Short reference label used in the prompt (``"[1]"``, ``"[2]"`` …).
    page_number : int | None
        Page number from provenance metadata when available.
    section : str | None
        Section/heading from provenance metadata when available.
    """

    doc_id: str
    content_snippet: str
    source: str
    confidence: float
    citation_anchor: str = ""
    page_number: int | None = None
    section: str | None = None


@dataclass
class VerifiedChunk:
    """Granular per-chunk evidence record (C0.4).

    Attributes
    ----------
    chunk_id : str
        Canonical chunk identifier.
    content : str
        Raw text payload.
    source_id : str
        Source label (doc, URL, collection name …).
    citation_anchor : str
        Inline reference label for the prompt envelope.
    support_score : float
        Chunk-level relevance / support to the query.
    is_must_use : bool
        True when this chunk carries critical evidence that MUST appear in
        the prompt; False = optional (included if token budget permits).
    contradiction_flag : bool
        True when this chunk contradicts another must-use chunk.
    provenance : dict
        Arbitrary provenance metadata from canonical store.
    """

    chunk_id: str
    content: str
    source_id: str
    citation_anchor: str
    support_score: float
    is_must_use: bool = True
    contradiction_flag: bool = False
    provenance: dict[str, Any] = field(default_factory=dict)


class ContradictionStatus:
    """Constants for contradiction_status field on EvidenceContract."""

    NONE = "none"
    PARTIAL = "partial"  # conflicting signals but not fatal
    CONFLICTING = "conflicting"  # must-use chunks directly contradict each other


class NextActionHint:
    """Constants for next_action_hint field on EvidenceContract."""

    PROCEED = "proceed"
    REFINE = "refine"  # query could be improved
    ABSTAIN = "abstain"  # evidence too weak; do not generate


@dataclass
class EvidenceContract:
    """Full C0.4 evidence contract.

    Produced by ``EvidenceContractBuilder.build_contract()`` and consumed by
    the Prompt Assembly stage.

    Attributes
    ----------
    query_id : str
        Identifier of the originating query.
    verified_chunks : list[VerifiedChunk]
        Verified, ranked chunk records (must-use first, then optional).
    citations : list[Citation]
        Flat citation list for backward compatibility with assemblers.
    context_packet : str
        Pre-formatted context block for direct LLM injection (legacy path).
    support_score : float
        Aggregate evidence strength (0–1).
    coverage_score : float
        Fraction of the query's key aspects covered by retrieved chunks (0–1).
    gaps : list[str]
        Query aspects not covered by any retrieved chunk.
    contradiction_status : str
        One of ``ContradictionStatus`` constants.
    abstain_recommended : bool
        True when evidence is too weak or conflicting for safe generation.
    next_action_hint : str
        One of ``NextActionHint`` constants.
    provenance_verified : bool
        True when all must-use chunks have verifiable canonical provenance.
    replay_metadata : dict
        replay_key, policy_hash, plan_id propagated from retrieval results.
    metadata : dict
        Build-time diagnostics (citation_count, avg_confidence …).
    """

    query_id: str
    verified_chunks: list[VerifiedChunk] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    context_packet: str = ""
    support_score: float = 0.0
    coverage_score: float = 0.0
    gaps: list[str] = field(default_factory=list)
    contradiction_status: str = ContradictionStatus.NONE
    abstain_recommended: bool = False
    next_action_hint: str = NextActionHint.PROCEED
    provenance_verified: bool = False
    replay_metadata: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# EvidenceContractBuilder
# ---------------------------------------------------------------------------


class EvidenceContractBuilder:
    """Builds full C0.4 evidence contracts with verified chunks and provenance.

    The EvidenceContractBuilder compiles citation slips, classifies chunks as
    must-use or optional, detects contradictions, computes coverage, and
    triggers the abstain path when evidence quality is insufficient.

    Args:
        min_citation_confidence: Minimum rerank score to include a chunk.
        must_use_threshold: Chunks with score >= this are classified must-use.
        min_coverage_to_proceed: Coverage below this → abstain recommended.
        must_use_count: Expected number of must-use chunks for full coverage.
    """

    def __init__(
        self,
        min_citation_confidence: float = 0.7,
        must_use_threshold: float = 0.80,
        min_coverage_to_proceed: float = 0.3,
        must_use_count: int = 3,
    ) -> None:
        self.min_citation_confidence = min_citation_confidence
        self.must_use_threshold = must_use_threshold
        self.min_coverage_to_proceed = min_coverage_to_proceed
        self.must_use_count = must_use_count
        log.info("EvidenceContractBuilder initialized")

    def build_contract(
        self,
        query_id: str,
        query: str,
        retrieved_docs: list[Any],
        query_aspects: list[str] | None = None,
    ) -> EvidenceContract:
        """Build C0.4 evidence contract from retrieved/ranked documents.

        Args:
            query_id: Query identifier.
            query: Original query string.
            retrieved_docs: ``RecallResult`` / reranked document objects.
            query_aspects: Optional list of key query aspects for coverage scoring.
                When ``None``, coverage is estimated from doc count alone.

        Returns:
            Full ``EvidenceContract``.
        """
        trace_id = f"evidence_{query_id}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L1_REASONING,
            "EvidenceContractBuilder.build_contract",
        )

        # Extract replay metadata from the first doc that carries it
        replay_metadata = self._extract_replay_metadata(retrieved_docs)

        # Build citations (confidence-filtered)
        citations: list[Citation] = []
        for idx, doc in enumerate(retrieved_docs):
            citation = self._create_citation(doc, idx + 1)
            if citation.confidence >= self.min_citation_confidence:
                citations.append(citation)

        # Build VerifiedChunk list (must-use first, then optional)
        verified_chunks = self._build_verified_chunks(citations, retrieved_docs)

        # Provenance check (all must-use sources are known)
        provenance_verified = self._verify_provenance(citations)

        # Aggregate support score
        support_score = self._calculate_support(citations)

        # Coverage score and gap detection
        coverage_score, gaps = self._calculate_coverage(query, citations, query_aspects)

        # Contradiction detection
        contradiction_status = self._detect_contradictions(verified_chunks)

        # Abstain decision
        abstain_recommended = (
            coverage_score < self.min_coverage_to_proceed
            or contradiction_status == ContradictionStatus.CONFLICTING
        )
        next_action_hint = self._decide_next_action(abstain_recommended, coverage_score, contradiction_status)

        # Build legacy context packet
        context_packet = self._generate_context_packet(query, citations)

        contract = EvidenceContract(
            query_id=query_id,
            verified_chunks=verified_chunks,
            citations=citations,
            context_packet=context_packet,
            support_score=support_score,
            coverage_score=coverage_score,
            gaps=gaps,
            contradiction_status=contradiction_status,
            abstain_recommended=abstain_recommended,
            next_action_hint=next_action_hint,
            provenance_verified=provenance_verified,
            replay_metadata=replay_metadata,
            metadata={
                "citation_count": len(citations),
                "must_use_count": sum(1 for c in verified_chunks if c.is_must_use),
                "optional_count": sum(1 for c in verified_chunks if not c.is_must_use),
                "avg_confidence": (
                    sum(c.confidence for c in citations) / len(citations) if citations else 0.0
                ),
            },
        )

        _emit_records_telemetry_event(
            trace_id,
            "evidence_contract",
            f"q{query_id}_cit{len(citations)}_cov{coverage_score:.2f}_abstain{abstain_recommended}",
        )

        log.debug(
            "Evidence contract [query=%s]: citations=%d support=%.2f "
            "coverage=%.2f contradiction=%s abstain=%s",
            query_id,
            len(citations),
            support_score,
            coverage_score,
            contradiction_status,
            abstain_recommended,
        )
        return contract

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_replay_metadata(self, docs: list[Any]) -> dict[str, Any]:
        """Pull replay_key / policy_hash / plan_id from the first doc that has them."""
        for doc in docs:
            meta = getattr(doc, "metadata", {}) or {}
            if "replay_key" in meta or "policy_hash" in meta:
                return {
                    "replay_key": meta.get("replay_key", ""),
                    "policy_hash": meta.get("policy_hash", ""),
                    "plan_id": meta.get("plan_id", ""),
                }
        return {}

    def _create_citation(self, doc: Any, index: int) -> Citation:
        """Create a ``Citation`` from a recall / rerank result."""
        return Citation(
            doc_id=getattr(doc, "doc_id", "unknown"),
            content_snippet=getattr(doc, "content", "")[:200],
            source=getattr(doc, "source", "unknown"),
            confidence=float(getattr(doc, "rerank_score", getattr(doc, "score", 0.5))),
            citation_anchor=f"[{index}]",
            page_number=getattr(doc, "metadata", {}).get("page_number"),
            section=getattr(doc, "metadata", {}).get("section"),
        )

    def _build_verified_chunks(
        self,
        citations: list[Citation],
        docs: list[Any],
    ) -> list[VerifiedChunk]:
        """Build VerifiedChunk list with must_use classification."""
        chunks: list[VerifiedChunk] = []
        doc_map = {getattr(d, "doc_id", ""): d for d in docs}

        for citation in tqdm(citations, desc="Building verified chunks", unit="chunk", leave=False):
            doc = doc_map.get(citation.doc_id)
            support = citation.confidence
            is_must_use = support >= self.must_use_threshold
            provenance = {}
            if doc is not None:
                provenance = dict(getattr(doc, "metadata", {}) or {})

            chunks.append(
                VerifiedChunk(
                    chunk_id=citation.doc_id,
                    content=getattr(doc, "content", "") if doc else citation.content_snippet,
                    source_id=citation.source,
                    citation_anchor=citation.citation_anchor,
                    support_score=support,
                    is_must_use=is_must_use,
                    provenance=provenance,
                )
            )

        # Sort: must-use first (descending score), then optional
        chunks.sort(key=lambda c: (not c.is_must_use, -c.support_score))
        return chunks

    def _verify_provenance(self, citations: list[Citation]) -> bool:
        """True when all citations have a known (non-"unknown") source."""
        return bool(citations) and all(c.source != "unknown" for c in citations)

    def _calculate_support(self, citations: list[Citation]) -> float:
        """Aggregate support score: avg confidence * coverage factor."""
        if not citations:
            return 0.0
        avg_conf = sum(c.confidence for c in citations) / len(citations)
        coverage_factor = min(len(citations) / max(self.must_use_count, 1), 1.0)
        return avg_conf * coverage_factor

    def _calculate_coverage(
        self,
        query: str,
        citations: list[Citation],
        query_aspects: list[str] | None,
    ) -> tuple[float, list[str]]:
        """Estimate coverage score and identify gaps.

        When ``query_aspects`` are provided, each aspect is checked against
        citation snippets.  Without aspects, coverage is estimated from the
        count of citations relative to ``must_use_count``.
        """
        if not citations:
            return 0.0, []

        if not query_aspects:
            coverage = min(len(citations) / max(self.must_use_count, 1), 1.0)
            return coverage, []

        covered: list[str] = []
        gaps: list[str] = []
        combined_text = " ".join(c.content_snippet.lower() for c in citations)

        for aspect in query_aspects:
            if aspect.lower() in combined_text:
                covered.append(aspect)
            else:
                gaps.append(aspect)

        coverage = len(covered) / len(query_aspects) if query_aspects else 1.0
        return coverage, gaps

    def _detect_contradictions(
        self,
        chunks: list[VerifiedChunk],
    ) -> str:
        """Detect contradictions among must-use chunks.

        Uses token-level negation heuristic: if a must-use chunk contains
        strong negation tokens (not, never, false, incorrect, wrong) while
        another must-use chunk asserts similar terms positively, flag partial
        or conflicting contradiction status.
        """
        must_use = [c for c in chunks if c.is_must_use]
        if len(must_use) < 2:
            return ContradictionStatus.NONE

        negation_tokens = {"not", "never", "false", "incorrect", "wrong", "no"}
        affirm_chunks: list[set[str]] = []
        negate_chunks: list[set[str]] = []

        for chunk in must_use:
            tokens = set(chunk.content.lower().split())
            neg_tokens = tokens & negation_tokens
            if neg_tokens:
                negate_chunks.append(tokens - negation_tokens)
            else:
                affirm_chunks.append(tokens)

        if not (affirm_chunks and negate_chunks):
            return ContradictionStatus.NONE

        # Check overlap between affirmed terms and negated terms
        for aff in tqdm(affirm_chunks, desc="Checking contradictions", unit="pair", leave=False):
            for neg in tqdm(negate_chunks, desc="Neg scan", unit="neg", leave=False):
                overlap = aff & neg
                significant = overlap - {"the", "a", "is", "in", "of", "and", "to"}
                if len(significant) >= 3:
                    # Mark the involved chunks as contradictory
                    for chunk in must_use:
                        tokens = set(chunk.content.lower().split())
                        if tokens & significant:
                            chunk.contradiction_flag = True
                    return ContradictionStatus.CONFLICTING
                if len(significant) >= 1:
                    return ContradictionStatus.PARTIAL

        return ContradictionStatus.NONE

    def _decide_next_action(
        self,
        abstain: bool,
        coverage: float,
        contradiction: str,
    ) -> str:
        if abstain and contradiction == ContradictionStatus.CONFLICTING:
            return NextActionHint.ABSTAIN
        if abstain and coverage < self.min_coverage_to_proceed:
            return NextActionHint.REFINE
        return NextActionHint.PROCEED

    def _generate_context_packet(self, query: str, citations: list[Citation]) -> str:
        """Generate legacy context packet for direct LLM injection."""
        parts = [f"Query: {query}\n", "Relevant Context:\n"]
        for i, c in enumerate(citations, 1):
            parts.append(f"[{i}] Source: {c.source} (ID: {c.doc_id})\nContent: {c.content_snippet}\n")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_global_builder: EvidenceContractBuilder | None = None


def get_evidence_contract_builder() -> EvidenceContractBuilder:
    """Get or create the global builder."""
    global _global_builder
    if _global_builder is None:
        _global_builder = EvidenceContractBuilder()
    return _global_builder
