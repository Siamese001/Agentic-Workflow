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


class EvidenceStatus:
    """C0.5 unified status (per spec §C0.5 STATUS + Final Contract §status)."""

    PASS = "pass"
    WEAK = "weak"
    WEAK_WITH_CAVEATS = "weak_with_caveats"  # post-refine partial recovery
    CONFLICTED = "conflicted"
    EMPTY = "empty"
    BLOCKED = "blocked"


class EvidenceClass:
    """C0.4 stratification classes (per spec §C0.4 STRATIFY)."""

    MUST_USE = "must_use"
    SUPPORTING = "supporting"
    CONTRADICTS = "contradicts"
    BACKGROUND = "background"
    EXCLUDED = "excluded"


class RecommendedDisposition:
    """Final Contract §recommended_disposition (per spec)."""

    PROCEED = "proceed"
    CAVEAT = "caveat"
    ABSTAIN = "abstain"
    REROUTE = "reroute"  # task became workflow-sized; recommend R5 fallback


class RefinementTactic:
    """C0.6 refinement tactic (per spec §C0.6 CHOOSE ONE TACTIC)."""

    REWRITE = "rewrite"  # same intent, better words
    BROADEN = "broaden"  # widen synonyms / source class within ACL
    NARROW = "narrow"  # add exact entity / file / time filter
    DECOMPOSE = "decompose"  # split compound support target
    GRAPH_HOP = "graph_hop"  # one bounded relation hop
    ABSTAIN = "abstain"  # cannot safely recover support


@dataclass
class RefinementDiagnostic:
    """C0.6 diagnostic record — why evidence is weak and what to do."""

    issue_type: str
    description: str
    suggested_tactic: str = RefinementTactic.ABSTAIN
    affected_chunks: list[str] = field(default_factory=list)


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
    # C0.5 unified status + C0.6 refinement state
    status: str = EvidenceStatus.PASS
    refinement_diagnostics: list[RefinementDiagnostic] = field(default_factory=list)
    refine_attempt: int = 0
    max_refine_attempts: int = 3
    # ------------------------------------------------------------------
    # Final Evidence Contract spec fields (per spec §FINAL C0 EVIDENCE CONTRACT)
    # ------------------------------------------------------------------
    cited_spans: list[dict[str, Any]] = field(default_factory=list)
    """Exact spans/line refs/section anchors per cited evidence.

    Each entry: {chunk_id, source_id, span_start, span_end, line_ref, section}.
    """
    source_ids: list[str] = field(default_factory=list)
    """Doc IDs / file paths / version IDs for all cited sources."""

    evidence_classes: dict[str, str] = field(default_factory=dict)
    """Mapping chunk_id -> EvidenceClass label (5-class stratification)."""

    contradiction_flags: list[str] = field(default_factory=list)
    """Explicit conflict descriptions (non-empty when status=CONFLICTED)."""

    unresolved_gaps: list[str] = field(default_factory=list)
    """Query aspects not covered by any retrieved chunk (alias of gaps)."""

    freshness_report: dict[str, Any] = field(default_factory=dict)
    """Per-source age vs freshness_class (from RetrievalPlan)."""

    acl_report: dict[str, Any] = field(default_factory=dict)
    """ACL clearance status per cited source."""

    lineage_manifest: dict[str, Any] = field(default_factory=dict)
    """How each evidence item was found: retrieval_mode, graph_hops, lane."""

    prompt_budget_hint: dict[str, Any] = field(default_factory=dict)
    """Packing priority for Prompt Assembly (token_estimate, must_use_count, ...)."""

    recommended_disposition: str = RecommendedDisposition.PROCEED
    """proceed / caveat / abstain / reroute (per spec §FINAL CONTRACT)."""

    budget_report: dict[str, Any] = field(
        default_factory=lambda: {
            "retrieval_passes": 1,
            "graph_hops": 0,
            "latency_used_ms": 0,
            "budget_remaining_ms": 0,
            "tokens_used": 0,
            "cost_used_usd": 0.0,
        }
    )


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
        graph_stage: Any | None = None,
    ) -> None:
        self.min_citation_confidence = min_citation_confidence
        self.must_use_threshold = must_use_threshold
        self.min_coverage_to_proceed = min_coverage_to_proceed
        self.must_use_count = must_use_count
        self._graph_stage = graph_stage  # GraphRecallStage or None (C0.6 GRAPH_HOP)
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

        # ----- C0.5 Final Evidence Contract field population -----
        status = self._compute_status(
            citations,
            support_score,
            coverage_score,
            contradiction_status,
        )
        cited_spans = self._build_cited_spans(verified_chunks, retrieved_docs)
        source_ids = self._build_source_ids(citations, retrieved_docs)
        evidence_classes = self._build_evidence_classes(verified_chunks, citations)
        contradiction_flags = self._build_contradiction_flags(verified_chunks)
        freshness_report = self._build_freshness_report(retrieved_docs)
        acl_report = self._build_acl_report(retrieved_docs)
        lineage_manifest = self._build_lineage_manifest(citations, retrieved_docs)
        prompt_budget_hint = self._build_prompt_budget_hint(verified_chunks)
        recommended_disposition = self._decide_disposition(
            status,
            contradiction_status,
            coverage_score,
        )

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
            # C0.5 unified status + Final Contract fields
            status=status,
            cited_spans=cited_spans,
            source_ids=source_ids,
            evidence_classes=evidence_classes,
            contradiction_flags=contradiction_flags,
            unresolved_gaps=list(gaps),
            freshness_report=freshness_report,
            acl_report=acl_report,
            lineage_manifest=lineage_manifest,
            prompt_budget_hint=prompt_budget_hint,
            recommended_disposition=recommended_disposition,
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

            # Prefer the real source identifier from provenance metadata;
            # fall back to citation.source (lane label) only if missing.
            real_source_id = (
                provenance.get("source_id")
                or provenance.get("file_path")
                or citation.source
            )
            chunks.append(
                VerifiedChunk(
                    chunk_id=citation.doc_id,
                    content=getattr(doc, "content", "") if doc else citation.content_snippet,
                    source_id=real_source_id,
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

    # ------------------------------------------------------------------
    # C0.5 Final Evidence Contract field builders (per spec §FINAL CONTRACT)
    # ------------------------------------------------------------------

    def _compute_status(
        self,
        citations: list[Citation],
        support_score: float,
        coverage_score: float,
        contradiction_status: str,
    ) -> str:
        """C0.5 unified status: PASS / WEAK / CONFLICTED / EMPTY / BLOCKED.

        Per spec §C0.5 STATUS:
          PASS       = enough direct support
          WEAK       = partial support, refinement may help
          CONFLICTED = credible sources disagree
          EMPTY      = no usable evidence
          BLOCKED    = source/policy/ACL prevents use (caller-set; default not BLOCKED)
        """
        if not citations:
            return EvidenceStatus.EMPTY
        if contradiction_status == ContradictionStatus.CONFLICTING:
            return EvidenceStatus.CONFLICTED
        if coverage_score < self.min_coverage_to_proceed or support_score < self.min_citation_confidence:
            return EvidenceStatus.WEAK
        return EvidenceStatus.PASS

    def _build_cited_spans(
        self,
        verified_chunks: list[VerifiedChunk],
        retrieved_docs: list[Any],
    ) -> list[dict[str, Any]]:
        """Build spec §cited_spans: exact spans/line refs/section anchors per chunk."""
        doc_map = {getattr(d, "doc_id", ""): d for d in retrieved_docs}
        spans: list[dict[str, Any]] = []
        for chunk in verified_chunks:
            doc = doc_map.get(chunk.chunk_id)
            meta = dict(getattr(doc, "metadata", {}) or {}) if doc is not None else {}
            spans.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "source_id": chunk.source_id,
                    "citation_anchor": chunk.citation_anchor,
                    "span_start": meta.get("span_start"),
                    "span_end": meta.get("span_end"),
                    "line_ref": meta.get("line_ref") or meta.get("page_number"),
                    "section": meta.get("section"),
                }
            )
        return spans

    def _build_source_ids(
        self,
        citations: list[Citation],
        retrieved_docs: list[Any] | None = None,
    ) -> list[str]:
        """Build spec §source_ids: deduped doc IDs / file paths / version IDs.

        Uses provenance metadata.source_id when available, falling back to
        citation.doc_id (which is the chunk identifier and an acceptable
        source-of-record handle).
        """
        doc_map = {
            getattr(d, "doc_id", ""): d for d in (retrieved_docs or [])
        }
        ids: list[str] = []
        for c in citations:
            doc = doc_map.get(c.doc_id)
            meta = dict(getattr(doc, "metadata", {}) or {}) if doc is not None else {}
            source_id = (
                meta.get("source_id")
                or meta.get("file_path")
                or c.doc_id
            )
            if source_id and source_id != "unknown":
                ids.append(source_id)
        # Dedupe preserving order
        return list(dict.fromkeys(ids))

    def _build_evidence_classes(
        self,
        verified_chunks: list[VerifiedChunk],
        citations: list[Citation],  # noqa: ARG002
    ) -> dict[str, str]:
        """Build spec §evidence_classes: chunk_id -> 5-class stratification label.

        Classes (per spec §C0.4 STRATIFY):
          MUST_USE / SUPPORTING / CONTRADICTS / BACKGROUND / EXCLUDED
        """
        classes: dict[str, str] = {}
        for chunk in verified_chunks:
            if chunk.contradiction_flag:
                classes[chunk.chunk_id] = EvidenceClass.CONTRADICTS
            elif chunk.is_must_use:
                classes[chunk.chunk_id] = EvidenceClass.MUST_USE
            elif chunk.support_score >= 0.5:
                classes[chunk.chunk_id] = EvidenceClass.SUPPORTING
            else:
                classes[chunk.chunk_id] = EvidenceClass.BACKGROUND
        return classes

    def _build_contradiction_flags(self, verified_chunks: list[VerifiedChunk]) -> list[str]:
        """Build spec §contradiction_flags: explicit conflict descriptions."""
        flags: list[str] = []
        for chunk in verified_chunks:
            if chunk.contradiction_flag:
                flags.append(
                    f"chunk={chunk.chunk_id} source={chunk.source_id}: contradicts another must-use chunk"
                )
        return flags

    def _build_freshness_report(self, retrieved_docs: list[Any]) -> dict[str, Any]:
        """Build spec §freshness_report: source age vs freshness_class."""
        report: dict[str, Any] = {"by_source": {}, "stale_count": 0, "fresh_count": 0}
        for doc in retrieved_docs:
            meta = dict(getattr(doc, "metadata", {}) or {})
            source_id = meta.get("source_id") or getattr(doc, "doc_id", "")
            if not source_id:
                continue
            band = meta.get("freshness_band", "unknown")
            age_days = meta.get("age_days")
            report["by_source"][source_id] = {
                "freshness_band": band,
                "age_days": age_days,
                "indexed_at": meta.get("indexed_at"),
            }
            if band in ("stale", "cold", "expired"):
                report["stale_count"] += 1
            else:
                report["fresh_count"] += 1
        return report

    def _build_acl_report(self, retrieved_docs: list[Any]) -> dict[str, Any]:
        """Build spec §acl_report: cleared sources only (per-source ACL status)."""
        report: dict[str, Any] = {"by_source": {}, "cleared_count": 0, "blocked_count": 0}
        for doc in retrieved_docs:
            meta = dict(getattr(doc, "metadata", {}) or {})
            source_id = meta.get("source_id") or getattr(doc, "doc_id", "")
            if not source_id:
                continue
            cleared = bool(meta.get("acl_cleared", True))
            report["by_source"][source_id] = {
                "cleared": cleared,
                "tenant_id": meta.get("tenant_id"),
                "allowed_principals": meta.get("allowed_principals", []),
            }
            if cleared:
                report["cleared_count"] += 1
            else:
                report["blocked_count"] += 1
        return report

    def _build_lineage_manifest(
        self,
        citations: list[Citation],
        retrieved_docs: list[Any],
    ) -> dict[str, Any]:
        """Build spec §lineage_manifest: how each evidence item was found."""
        doc_map = {getattr(d, "doc_id", ""): d for d in retrieved_docs}
        by_chunk: dict[str, dict[str, Any]] = {}
        retrieval_modes_used: set[str] = set()
        graph_hops_total = 0
        for c in citations:
            doc = doc_map.get(c.doc_id)
            meta = dict(getattr(doc, "metadata", {}) or {}) if doc is not None else {}
            mode = c.source or meta.get("retrieval_mode", "unknown")
            retrieval_modes_used.add(mode)
            graph_hops = int(meta.get("graph_hops", 0) or 0)
            graph_hops_total += graph_hops
            by_chunk[c.doc_id] = {
                "lane": mode,
                "retrieval_mode": meta.get("retrieval_mode", mode),
                "graph_hops": graph_hops,
                "plan_id": meta.get("plan_id"),
                "rank": meta.get("rank"),
                "rerank_score": meta.get("rerank_score") or c.confidence,
            }
        return {
            "by_chunk": by_chunk,
            "retrieval_modes_used": sorted(retrieval_modes_used),
            "graph_hops_total": graph_hops_total,
        }

    def _build_prompt_budget_hint(
        self,
        verified_chunks: list[VerifiedChunk],
    ) -> dict[str, Any]:
        """Build spec §prompt_budget_hint: packing priority for Prompt Assembly."""
        # Approximate token estimate (4 chars/token)
        total_chars = sum(len(c.content) for c in verified_chunks)
        token_estimate = total_chars // 4
        must_use = [c for c in verified_chunks if c.is_must_use]
        return {
            "token_estimate": token_estimate,
            "must_use_count": len(must_use),
            "must_use_token_estimate": sum(len(c.content) for c in must_use) // 4,
            "optional_count": len(verified_chunks) - len(must_use),
            "packing_order": [c.chunk_id for c in verified_chunks],  # already must-use first
        }

    def _decide_disposition(
        self,
        status: str,
        contradiction_status: str,
        coverage_score: float,
    ) -> str:
        """Build spec §recommended_disposition: proceed/caveat/abstain/reroute.

        Rules:
          PASS                                           -> PROCEED
          WEAK_WITH_CAVEATS or CONFLICTED (recoverable)  -> CAVEAT
          EMPTY or BLOCKED                               -> ABSTAIN
          WEAK with very-low coverage                    -> REROUTE (workflow-sized)
        """
        if status == EvidenceStatus.PASS:
            return RecommendedDisposition.PROCEED
        if status == EvidenceStatus.WEAK_WITH_CAVEATS:
            return RecommendedDisposition.CAVEAT
        if status == EvidenceStatus.CONFLICTED:
            return RecommendedDisposition.CAVEAT
        if status in (EvidenceStatus.EMPTY, EvidenceStatus.BLOCKED):
            return RecommendedDisposition.ABSTAIN
        if status == EvidenceStatus.WEAK:
            # Very-low coverage signals workflow-sized task
            if coverage_score < (self.min_coverage_to_proceed / 2.0):
                return RecommendedDisposition.REROUTE
            return RecommendedDisposition.CAVEAT
        # Unknown contradiction-only edge case
        if contradiction_status == ContradictionStatus.CONFLICTING:
            return RecommendedDisposition.CAVEAT
        return RecommendedDisposition.PROCEED

    # ------------------------------------------------------------------
    # C0.6 Refinement tactic executors
    # ------------------------------------------------------------------

    def execute_refinement_tactic(
        self,
        tactic: str,
        contract: EvidenceContract,
        original_plan: Any,
        query: str = "",
    ) -> dict[str, Any]:
        """Execute the chosen C0.6 refinement tactic.

        Each tactic produces a *refined RetrievalPlan* the caller re-issues
        for one bounded second pass.  GUARDS (per spec): no infinite loop
        (cap by ``max_refine_attempts``), no source escape (ACL preserved).

        Args:
            tactic: One of ``RefinementTactic`` constants.
            contract: Current weak/empty/conflicted contract.
            original_plan: ``RetrievalPlan`` from the failed first pass.
            query: Original query string (used by REWRITE/BROADEN/DECOMPOSE).

        Returns:
            Dict with keys: ``tactic``, ``refined_plan``, ``new_query``,
            ``decomposed_queries``, ``hop_results``, ``abstain``,
            ``rationale``.
        """
        # GUARD: no infinite loop
        if contract.refine_attempt >= contract.max_refine_attempts:
            return {
                "tactic": RefinementTactic.ABSTAIN,
                "refined_plan": None,
                "abstain": True,
                "rationale": (
                    f"max_refine_attempts={contract.max_refine_attempts} reached; "
                    f"forcing ABSTAIN to prevent infinite loop"
                ),
            }

        if tactic == RefinementTactic.REWRITE:
            return self._tactic_rewrite(contract, original_plan, query)
        if tactic == RefinementTactic.BROADEN:
            return self._tactic_broaden(contract, original_plan, query)
        if tactic == RefinementTactic.NARROW:
            return self._tactic_narrow(contract, original_plan, query)
        if tactic == RefinementTactic.DECOMPOSE:
            return self._tactic_decompose(contract, original_plan, query)
        if tactic == RefinementTactic.GRAPH_HOP:
            return self._tactic_graph_hop(contract, original_plan)
        if tactic == RefinementTactic.ABSTAIN:
            return {
                "tactic": RefinementTactic.ABSTAIN,
                "refined_plan": None,
                "abstain": True,
                "rationale": "Cannot safely recover support; abstaining per C0.6",
            }
        return {
            "tactic": tactic,
            "refined_plan": original_plan,
            "abstain": False,
            "rationale": f"Unknown tactic '{tactic}'; preserving original plan",
        }

    def _clone_plan_with(self, original_plan: Any, **overrides: Any) -> Any:
        """Clone a RetrievalPlan with field overrides; preserves ACL/replay.

        C0.6 GUARDS — no source escape: ACL/tenant/replay/policy fields
        are always carried forward from the original plan.
        """
        from agentic_core.knowledge.retrieval.retrieval_plan import (  # noqa: PLC0415
            RetrievalPlan,
        )

        if original_plan is None:
            return None

        new_kwargs = {
            "query_id": original_plan.query_id,
            "retrieval_mode": original_plan.retrieval_mode,
            "source_collections": list(original_plan.source_collections),
            "top_k": original_plan.top_k,
            "allowed_principals": list(original_plan.allowed_principals),
            "tenant_id": original_plan.tenant_id,
            "max_freshness_band": original_plan.max_freshness_band,
            "effective_date_window": original_plan.effective_date_window,
            "schema_version_bind": original_plan.schema_version_bind,
            "replay_key": original_plan.replay_key,
            "policy_hash": original_plan.policy_hash,
            "metadata": dict(original_plan.metadata),
        }
        # Carry forward C0.1-spec fields when present on the source plan
        # (older plans may not have them; getattr keeps backward compatibility).
        for spec_field in (
            "disallowed_sources",
            "region",
            "support_target",
            "weak_support_policy",
            "max_parent_expansion",
            "max_graph_hops",
            "max_refine_attempts",
            "slo_budget_ms",
            "token_budget",
            "latency_budget_ms",
            "cost_budget_usd",
        ):
            if hasattr(original_plan, spec_field):
                value = getattr(original_plan, spec_field)
                # Defensive copy of mutable containers
                if isinstance(value, list):
                    value = list(value)
                new_kwargs[spec_field] = value
        new_kwargs.update(overrides)
        new_kwargs["metadata"]["refinement_of"] = original_plan.plan_id
        return RetrievalPlan(**new_kwargs)

    def _tactic_rewrite(
        self,
        contract: EvidenceContract,  # noqa: ARG002
        original_plan: Any,
        query: str,
    ) -> dict[str, Any]:
        """REWRITE — same intent, better words (deterministic stop-word strip)."""
        stop = {"the", "a", "an", "of", "to", "is", "are", "what", "how", "in", "on"}
        tokens = [t for t in query.lower().split() if t not in stop]
        new_query = " ".join(tokens) if tokens else query
        return {
            "tactic": RefinementTactic.REWRITE,
            "refined_plan": self._clone_plan_with(original_plan),
            "new_query": new_query,
            "abstain": False,
            "rationale": f"Rewrote '{query}' -> '{new_query}' (stopwords removed)",
        }

    def _tactic_broaden(
        self,
        contract: EvidenceContract,  # noqa: ARG002
        original_plan: Any,
        query: str,
    ) -> dict[str, Any]:
        """BROADEN — loosen freshness one band, widen source_collections, double top_k."""
        from agentic_core.knowledge.canonical.chunk_manifest import (  # noqa: PLC0415
            FreshnessBand,
        )

        bands = FreshnessBand.ordered()
        try:
            idx = bands.index(original_plan.max_freshness_band)
            new_band = bands[min(idx + 1, len(bands) - 1)]
        except (ValueError, AttributeError):
            new_band = original_plan.max_freshness_band

        refined = self._clone_plan_with(
            original_plan,
            max_freshness_band=new_band,
            source_collections=[],
            top_k=min(original_plan.top_k * 2, 100),
        )
        return {
            "tactic": RefinementTactic.BROADEN,
            "refined_plan": refined,
            "new_query": query,
            "abstain": False,
            "rationale": (
                f"Widened freshness {original_plan.max_freshness_band}->{new_band}, "
                f"top_k {original_plan.top_k}->{refined.top_k}, "
                f"removed source_collections (ACL preserved)"
            ),
        }

    def _tactic_narrow(
        self,
        contract: EvidenceContract,
        original_plan: Any,
        query: str,
    ) -> dict[str, Any]:
        """NARROW — restrict source_collections to top must-use sources, halve top_k."""
        narrow_ids: list[str] = []
        for chunk in contract.verified_chunks[:3]:
            sid = getattr(chunk, "source_id", "") or ""
            if sid and sid != "unknown":
                narrow_ids.append(sid)

        refined = self._clone_plan_with(
            original_plan,
            source_collections=narrow_ids or list(original_plan.source_collections),
            top_k=max(original_plan.top_k // 2, 5),
        )
        return {
            "tactic": RefinementTactic.NARROW,
            "refined_plan": refined,
            "new_query": query,
            "abstain": False,
            "rationale": (
                f"Narrowed source_collections to {narrow_ids or 'unchanged'}, "
                f"top_k {original_plan.top_k}->{refined.top_k}"
            ),
        }

    def _tactic_decompose(
        self,
        contract: EvidenceContract,
        original_plan: Any,
        query: str,
    ) -> dict[str, Any]:
        """DECOMPOSE — split on conjunction/comma, produce one sub-plan per piece."""
        import re  # noqa: PLC0415

        parts = re.split(r"\s+(?:and|or)\s+|[;,]\s*", query, flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) <= 1:
            return self._tactic_broaden(contract, original_plan, query)

        sub_plans = [
            self._clone_plan_with(
                original_plan,
                top_k=max(original_plan.top_k // len(parts), 3),
            )
            for _ in parts
        ]
        return {
            "tactic": RefinementTactic.DECOMPOSE,
            "refined_plan": sub_plans[0],
            "decomposed_queries": parts,
            "decomposed_plans": sub_plans,
            "abstain": False,
            "rationale": f"Decomposed query into {len(parts)} sub-queries",
        }

    def _tactic_graph_hop(
        self,
        contract: EvidenceContract,
        original_plan: Any,
    ) -> dict[str, Any]:
        """GRAPH_HOP — execute one bounded relation hop via injected graph_stage."""
        if self._graph_stage is None:
            return {
                "tactic": RefinementTactic.GRAPH_HOP,
                "refined_plan": original_plan,
                "hop_results": [],
                "abstain": False,
                "rationale": "No graph_stage wired; graph_hop is a no-op",
            }

        hop_diags = [
            d for d in contract.refinement_diagnostics if d.suggested_tactic == RefinementTactic.GRAPH_HOP
        ]
        # If no explicit GRAPH_HOP diagnostics, hop from top must-use chunks
        target_chunk_ids: list[str] = []
        if hop_diags:
            for d in hop_diags:
                target_chunk_ids.extend(d.affected_chunks[:5])
        else:
            target_chunk_ids = [c.chunk_id for c in contract.verified_chunks[:3]]

        all_hops: list[Any] = []
        for chunk_id in target_chunk_ids:
            source_path = ""
            for c in contract.verified_chunks:
                if c.chunk_id == chunk_id:
                    source_path = c.provenance.get("source_path", "") or c.provenance.get("file_path", "")
                    break
            try:
                hops = self._graph_stage.graph_hop(
                    chunk_id=chunk_id,
                    source_path=source_path,
                    plan=original_plan,
                )
                all_hops.extend(hops)
            except (OSError, ValueError) as exc:  # guardian: allow-log-and-swallow -- graph hop failure: non-fatal; chunk skipped, contract continues with remaining hops
                log.debug("graph_hop(%s) failed: %s", chunk_id, exc)

        # Update budget report
        if all_hops:
            contract.budget_report["graph_hops"] = contract.budget_report.get("graph_hops", 0) + len(all_hops)

        return {
            "tactic": RefinementTactic.GRAPH_HOP,
            "refined_plan": original_plan,
            "hop_results": all_hops,
            "abstain": False,
            "rationale": f"Executed {len(all_hops)} graph hops",
        }


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
