"""Final Evidence Contract — AG-RGGOV-W6 Core Contract + AG-4 carrier repair.

Canonical dataclasses for C0 evidence collection output.

AG-4 (plan ``ag4-evidence-contract-carrier-repair-d2f9a3``) extends both
``EvidenceItem`` and ``FinalEvidenceContract`` with the carrier fields needed
to prove groundedness, faithfulness, citation, ACL, freshness, lineage,
contradiction status, support status, replay, audit, and Exit-side
verdicts WITHOUT generating new embeddings or mutating ChromaDB.

All AG-4 additions are *additive with safe defaults* so the 50+ pre-existing
tests that construct these contracts compile and pass without change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from agentic_core.runtime.contracts.posture import RuntimePosture, POSTURE_READ_ONLY

from agentic_core.runtime.contracts.origin import Origin, OriginTaggedContent


# ---------------------------------------------------------------------------
# AG-4 status sentinels — string-valued so they serialise cleanly to JSON.
# UNKNOWN must NEVER be treated as PASS by any downstream gate (Exit X1).
# NOT_APPLICABLE MUST be accompanied by a non-empty reason.
# ---------------------------------------------------------------------------

#: Sentinel: a status field whose value has not been computed.  Downstream
#: evaluators MUST NOT treat this as PASS.  Pair with a populated
#: ``*_unknown_reason`` field where applicable.
STATUS_UNKNOWN = "UNKNOWN"

#: Sentinel: a status field that does not apply to this evidence item or
#: contract instance.  MUST be accompanied by a non-empty reason field.
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"

#: Sentinel: support_status value indicating evidence is empty / missing.
#: MUST NOT silently become PASS.
SUPPORT_STATUS_EMPTY = "EMPTY"

#: Sentinel: support_status value indicating evidence is BLOCKED by ACL or
#: policy.  MUST NOT silently become PASS.
SUPPORT_STATUS_BLOCKED = "BLOCKED"

#: Sentinel: support_status value indicating internal contradiction.
#: MUST NOT silently become PASS.
SUPPORT_STATUS_CONFLICTED = "CONFLICTED"

#: Sentinel: support_status value indicating support is below threshold but
#: not zero.  MUST NOT silently become PASS.
SUPPORT_STATUS_WEAK = "WEAK"

#: Sentinel: support_status value indicating evidence meets the support
#: target.  Only this value (and ``PARTIAL``) may be treated as PASS by
#: downstream gates.
SUPPORT_STATUS_PASS = "PASS"

#: Sentinel: support_status value indicating partial support that meets the
#: contract's partial-support target.
SUPPORT_STATUS_PARTIAL = "PARTIAL"

#: Sentinel: per the AG-4 invariant, retrieved evidence is data-only — never
#: an instruction.  Every ``EvidenceItem`` produced by C0 MUST carry this
#: literal in ``allowed_prompt_slot``.
ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY = "C0_EVIDENCE_DATA_ONLY"

#: Set of support_status values that downstream gates MAY treat as PASS.
#: Any value not in this set (including UNKNOWN, EMPTY, BLOCKED, CONFLICTED,
#: WEAK, NOT_APPLICABLE) MUST NOT pass.
SUPPORT_STATUS_PASSING_VALUES = frozenset({
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_PARTIAL,
})


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    """Single evidence item with full AG-4 carrier shape.

    Pre-AG-4 callers continue to work — every new field has a safe default
    (empty string, 0.0, ``UNKNOWN``, or empty tuple).  Callers populating
    new fields MUST use real values or explicit sentinel constants
    (``STATUS_UNKNOWN`` / ``STATUS_NOT_APPLICABLE``); fabrication is
    forbidden by the AG-4 plan.
    """

    # ---- Pre-AG-4 fields (unchanged shape) ----
    source: str
    content: str
    content_type: str = "text"  # text, json, html, etc.
    retrieval_timestamp: str = ""
    confidence_score: float = 0.0
    # W3 P3.2: origin/data-boundary tagging (concern #6, D7=Origin enum)
    origin: Origin = Origin.RETRIEVED_DATA

    # ---- AG-4 W1: identity + provenance ----
    #: Stable id for this evidence item across replays.  Empty = not yet
    #: minted.  Recommended shape: ``"<run_id>:<source_id>:<chunk_digest>"``.
    evidence_id: str = ""
    #: Stable id for the origin source (collection name, URL, file path, …).
    source_id: str = ""
    #: Coarse classification of the source (``chromadb_collection`` |
    #: ``app_payload_inline`` | ``tavily_web`` | ``tool_output`` |
    #: ``user_intent`` | ``human_review`` | …).
    source_type: str = ""
    #: Version pin on the source (commit SHA, ingest run id, doc revision, …).
    source_version: str = ""
    #: Opaque pointer to the original location (URL, S3 key, file:line range).
    source_uri_or_ref: str = ""
    #: Authority that owns / can vouch for the source (team, system, person).
    source_owner_or_authority: str = ""

    # ---- AG-4 W1: span + citation ----
    #: The exact span retrieved (line range / paragraph / token range).
    #: Empty when the evidence is the full source.
    retrieved_span: str = ""
    #: Anchor that can be cited externally.  MUST be present for any evidence
    #: that may leave the system in an answer.  Empty = no external citation
    #: possible (downstream gates may FAIL grounding).
    citation_anchor: str = ""
    #: Deterministic digest of the retrieved chunk (e.g. SHA-256 of
    #: normalized content).  MUST be reproducible for replay.
    chunk_digest: str = ""

    # ---- AG-4 W1: retrieval scores ----
    #: Pointer to the dense embedding used to retrieve this item.  REQUIRED
    #: when ``retrieval_method`` includes ``dense``.  Empty otherwise.
    fact_vec_ref: str = ""
    #: Dense-retrieval score.  REQUIRED when ``retrieval_method`` includes
    #: ``dense``.  ``-1.0`` indicates explicit unknown; ``0.0`` indicates a
    #: real zero score.
    dense_score: float = 0.0
    #: Lexical/sparse-retrieval score.  REQUIRED when ``retrieval_method``
    #: includes ``sparse`` (BM25, TF-IDF, regex).
    bm25_score: float = 0.0
    #: Score derived from metadata-only filters (date, ACL bucket, etc.).
    metadata_score: float = 0.0
    #: Pointer to the run-time query embedding ref used to retrieve this item.
    query_vec_ref: str = ""

    # ---- AG-4 W1: trust + safety ----
    #: Coarse freshness class: ``FRESH`` | ``STALE`` | ``EXPIRED`` |
    #: ``UNKNOWN`` | ``NOT_APPLICABLE``.
    freshness_status: str = STATUS_UNKNOWN
    #: ACL outcome: ``ALLOWED`` | ``DENIED`` | ``REDACTED`` | ``UNKNOWN`` |
    #: ``NOT_APPLICABLE``.
    acl_status: str = STATUS_UNKNOWN
    #: Trust label tied to ``origin`` (``USER`` | ``RETRIEVED`` |
    #: ``TOOL`` | ``MODEL`` | ``HUMAN_REVIEWED`` | ``SYSTEM``).
    origin_trust_label: str = ""
    #: Authority class (``PRIMARY`` | ``SECONDARY`` | ``TERTIARY`` |
    #: ``ANECDOTAL`` | ``UNKNOWN``).
    authority_class: str = STATUS_UNKNOWN
    #: Contradiction status (``NONE`` | ``WITH_OTHER_EVIDENCE`` |
    #: ``WITH_SOURCE_AUTHORITY`` | ``UNKNOWN`` | ``NOT_APPLICABLE``).
    contradiction_status: str = STATUS_UNKNOWN
    #: Stratum / lane the evidence comes from (``CANONICAL`` | ``REPO`` |
    #: ``EXTERNAL_AUTHORITY`` | ``EXTERNAL_RAW`` | ``RUNTIME`` | …).
    stratum: str = ""

    # ---- AG-4 W1: prompt-slot binding (AG-4 invariant) ----
    #: Slot label that PA MUST honour when packing this item into a prompt.
    #: For C0-retrieved evidence this MUST equal
    #: ``C0_EVIDENCE_DATA_ONLY`` — i.e. retrieved text is data, never
    #: instruction.  PA-side enforcement: see
    #: ``agentic_core.prompt_governance.*`` checks.
    allowed_prompt_slot: str = ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY

    # ---- AG-4 W1: support outcome ----
    #: Numeric support score for this single item (NOT the contract-level
    #: aggregate).  ``0.0`` when not computed.
    support_score: float = 0.0
    #: Per-item support disposition.  Sentinels: ``PASS``, ``PARTIAL``,
    #: ``WEAK``, ``EMPTY``, ``BLOCKED``, ``CONFLICTED``, ``UNKNOWN``,
    #: ``NOT_APPLICABLE``.  Only ``PASS``/``PARTIAL`` may be treated as
    #: support by downstream gates.
    support_status: str = STATUS_UNKNOWN

    # ---- AG-4 W1: retrieval audit ----
    #: Comma-separated retrieval methods exercised: ``dense`` | ``sparse`` |
    #: ``metadata`` | ``graph`` | ``inline`` | ``cache_exact`` |
    #: ``cache_semantic``.  Empty = unknown.
    retrieval_method: str = ""
    #: Pointer to the retrieval-run record (run_id, span ref, …) so an
    #: auditor can reconstruct the retrieval that produced this item.
    retrieval_run_ref: str = ""
    #: Pointer to a graph-expansion record when ``retrieval_method`` includes
    #: ``graph``.  Empty otherwise.
    graph_ref: str = ""
    #: Deterministic digest of this entire ``EvidenceItem`` (computed by
    #: producer; stable across replays).  Used by FEC's
    #: ``final_evidence_digest`` aggregator.
    evidence_digest: str = ""

    # ---- AG-4 W1: explicit reasons for sentinel status fields ----
    #: Reason populated when a status field equals ``UNKNOWN``.  Empty
    #: string allowed only when no status field is UNKNOWN on this item.
    unknown_reason: str = ""
    #: Reason populated when a status field equals ``NOT_APPLICABLE``.
    #: MUST be non-empty if any status field on this item is NOT_APPLICABLE.
    not_applicable_reason: str = ""

    # ------------------------------------------------------------------
    # AG-4 invariants — reject silent NOT_APPLICABLE without a reason.
    # ``UNKNOWN`` is permitted without a reason (the producer may not yet
    # have computed it) but MUST NEVER be treated as PASS.  Enforcement:
    # downstream gate logic, not __post_init__ — we only block the most
    # dangerous shape (NOT_APPLICABLE without reason) here.
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        # Detect any *_status field equal to NOT_APPLICABLE without reason.
        na_fields = [
            name for name in (
                "freshness_status",
                "acl_status",
                "authority_class",
                "contradiction_status",
                "support_status",
            )
            if getattr(self, name) == STATUS_NOT_APPLICABLE
        ]
        if na_fields and not self.not_applicable_reason:
            raise ValueError(
                "EvidenceItem: fields "
                f"{na_fields} set to NOT_APPLICABLE but not_applicable_reason "
                "is empty. AG-4 invariant: NOT_APPLICABLE requires a reason."
            )


@dataclass(frozen=True, slots=True)
class FinalEvidenceContract:
    """C0 evidence collection output contract.

    Contains collected evidence and sufficiency assessment.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Evidence content
    evidence_items: tuple[EvidenceItem, ...] = field(default_factory=tuple)
    retrieval_sources: tuple[str, ...] = field(default_factory=tuple)

    # Sufficiency assessment
    support_target_met: bool = False
    support_target_partial: bool = False
    evidence_sufficiency_score: float = 0.0

    # Identity extension
    tenant_id: str = ""  # W1: threaded from RouteContract.tenant_id (D6)

    # Metadata
    evidence_collection_timestamp: str = ""
    schema_version: str = "W6.0"  # W5 P5.1: renamed from contract_version (D8)

    # Digest for downstream referencing
    compilation_hash: str = ""
    # W4: observability + audit linkage (concern #9, D12=default-empty tuples)
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    # W5 P5.2: HMAC-SHA256 integrity signature (D9, default-empty = unsigned)
    signature: str = ""
    # W6 P6.2: risk/side-effect posture (concern #7)
    posture: RuntimePosture = field(default_factory=lambda: POSTURE_READ_ONLY)
    # W6 P6.3: gate verdict refs (concern #3)
    gate_verdict_refs: tuple[str, ...] = field(default_factory=tuple)
    # W7 P7.1: replay/determinism (concern #4; D11=default-empty)
    replay_key: str = ""
    snapshot_refs: tuple[str, ...] = field(default_factory=tuple)
    l5_certification_ref: str = ""

    # ====================================================================
    # AG-4 W2: carrier fields for full retrieval lineage + safety verdicts.
    # All additive with safe defaults (empty tuples / strings / UNKNOWN).
    # No mutation of pre-AG-4 field shapes.
    # ====================================================================

    #: Pointer to the upstream RouteContract that authorised this retrieval.
    route_contract_ref: str = ""
    #: Pointer to the retrieval plan (lanes invoked, fallbacks, timing).
    retrieval_plan_ref: str = ""
    #: Pointer to the run-time query embedding ref (if dense retrieval).
    query_vec_ref: str = ""
    #: Refs to dense-search receipts (1 per dense lane invocation).
    dense_search_refs: tuple[str, ...] = field(default_factory=tuple)
    #: Refs to sparse/lexical-search receipts (1 per sparse lane).
    sparse_search_refs: tuple[str, ...] = field(default_factory=tuple)
    #: Refs to metadata-filter receipts (1 per filter applied).
    metadata_filter_refs: tuple[str, ...] = field(default_factory=tuple)
    #: Refs to graph-expansion receipts (when graph retrieval was used).
    graph_expansion_refs: tuple[str, ...] = field(default_factory=tuple)

    #: Stratification of evidence_items by stratum / lane / authority.
    #: Tuple of ``(stratum_label, evidence_id_tuple)`` rows for opaque
    #: serialisation.
    evidence_strata: tuple[tuple[str, tuple[str, ...]], ...] = field(default_factory=tuple)
    #: Map from evidence_id -> citation_anchor.  Materialised separately
    #: so Exit-side citation gates don't have to walk evidence_items.
    citation_map: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    #: Map from evidence_id -> source_id for fast lineage lookup.
    source_lineage_map: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    #: Map from source_id -> source_version pin.
    source_version_map: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    #: ACL verification receipts (one per source_id verified).  Each ref
    #: points to an audit row capturing principal + scope + outcome.
    acl_verification_receipts: tuple[str, ...] = field(default_factory=tuple)
    #: Freshness receipts (one per source_id freshness check).
    freshness_receipts: tuple[str, ...] = field(default_factory=tuple)

    #: Aggregate contradiction report ref (single document summarising
    #: per-item contradiction_status across all evidence_items).  Empty
    #: when no contradiction surface was computed.
    contradiction_report: str = ""

    #: Aggregate support disposition for the contract as a whole.
    #: Sentinels: ``PASS``, ``PARTIAL``, ``WEAK``, ``EMPTY``, ``BLOCKED``,
    #: ``CONFLICTED``, ``UNKNOWN``, ``NOT_APPLICABLE``.  Distinct from
    #: pre-AG-4 boolean ``support_target_met`` (which remains for
    #: backwards compatibility).
    support_status: str = STATUS_UNKNOWN
    #: Map from support-dimension label -> score (e.g. coverage, quality,
    #: independence).  Tuple shape for opaque serialisation.
    support_score_profile: tuple[tuple[str, float], ...] = field(default_factory=tuple)

    #: Refs to evidence rows that were retrieved but excluded from
    #: ``evidence_items`` (e.g. ACL-redacted, dedup-collapsed, low-score).
    excluded_evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    #: Refs to source_ids that were BLOCKED (ACL deny, policy block,
    #: invalid_for_normative_use).  MUST NOT silently become PASS.
    blocked_source_refs: tuple[str, ...] = field(default_factory=tuple)
    #: Refs to weak-support refinement attempts (re-query with broader
    #: scope, lane fallback, etc.).  Empty when no refinement was tried.
    weak_support_refinement_attempts: tuple[str, ...] = field(default_factory=tuple)

    #: Deterministic digest of the full evidence bundle (including all
    #: items + ordering + scores).  Stable across replays for the same
    #: query+route+snapshot.
    final_evidence_digest: str = ""

    #: Reason populated when ``support_status`` equals ``UNKNOWN``.
    unknown_reason: str = ""
    #: Reason populated when ``support_status`` equals ``NOT_APPLICABLE``.
    not_applicable_reason: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"FinalEvidenceContract: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
        # AG-4 invariant: NOT_APPLICABLE requires reason.
        if self.support_status == STATUS_NOT_APPLICABLE and not self.not_applicable_reason:
            raise ValueError(
                "FinalEvidenceContract: support_status=NOT_APPLICABLE but "
                "not_applicable_reason is empty. AG-4 invariant: "
                "NOT_APPLICABLE requires a reason."
            )

    # ------------------------------------------------------------------
    # AG-4 helpers — small read-only utilities downstream gates may use.
    # ------------------------------------------------------------------

    def support_status_is_passing(self) -> bool:
        """Return True iff ``support_status`` is one of the PASS values.

        AG-4 invariant: ``UNKNOWN``, ``EMPTY``, ``BLOCKED``, ``CONFLICTED``,
        ``WEAK``, ``NOT_APPLICABLE`` MUST NOT pass.
        """
        return self.support_status in SUPPORT_STATUS_PASSING_VALUES

    def has_blocked_sources(self) -> bool:
        """Return True if any source was BLOCKED — Exit MUST consider this."""
        return bool(self.blocked_source_refs)

    def has_contradictions(self) -> bool:
        """Return True if a contradiction report is present."""
        return bool(self.contradiction_report)


__all__ = [
    "EvidenceItem",
    "FinalEvidenceContract",
    "STATUS_UNKNOWN",
    "STATUS_NOT_APPLICABLE",
    "SUPPORT_STATUS_EMPTY",
    "SUPPORT_STATUS_BLOCKED",
    "SUPPORT_STATUS_CONFLICTED",
    "SUPPORT_STATUS_WEAK",
    "SUPPORT_STATUS_PASS",
    "SUPPORT_STATUS_PARTIAL",
    "SUPPORT_STATUS_PASSING_VALUES",
    "ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY",
]
