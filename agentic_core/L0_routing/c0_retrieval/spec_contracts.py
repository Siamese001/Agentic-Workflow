"""C0.1-C0.5 spec-grade typed contracts (additive).

Spec sources:
- ``docs/reference/03_L0_Routing/C0 - Context Engine/C0.1_Retrieval_Plan_detailed.md``
- ``docs/reference/03_L0_Routing/C0 - Context Engine/C0.2_Evidence_Fetch_detailed.md``
- ``docs/reference/03_L0_Routing/C0 - Context Engine/C0.4_Shape_Rerank_Stratify_detailed.md``
- ``docs/reference/03_L0_Routing/C0 - Context Engine/C0.5_Final_Evidence_Contract_detailed.md``

This module is **additive**: it provides the spec-canonical typed dataclasses
that the existing modules (``plan.py``, ``candidate_pool.py``, ``shape.py``,
``final_contract.py``) do not surface as their own dataclass types.

All existing tests + dispatcher continue to use the existing types. The
contracts here are for callers that consume the spec-grade interface
(integration adapters, replay verifiers, OTEL emitters).

No I/O, no MCP calls. Pure data + validation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Mapping

from .verdicts import (
    GraphRelation,
    RetrievalLane,
    SourceClass,
    SupportTarget,
)


# ===========================================================================
# C0.1 — RetrievalPlan adjuncts
# ===========================================================================

class CitationPrecision(str, Enum):
    """C0.1 SupportTargetProfile.required_citation_precision."""

    SPAN_EXACT = "span_exact"
    SECTION = "section"
    DOCUMENT = "document"
    NONE = "none"


class SourceAuthorityClass(str, Enum):
    """C0.1 SupportTargetProfile.required_source_authority."""

    AUTHORITATIVE = "authoritative"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    INFORMATIONAL = "informational"


class UnsupportedInferencePolicy(str, Enum):
    """C0.1 SupportTargetProfile.unsupported_inference_policy."""

    REJECT = "reject"
    CAVEAT = "caveat"
    ALLOW_WITH_FLAG = "allow_with_flag"


@dataclass(frozen=True)
class SupportTargetProfile:
    """C0.1 PHASE 1 #2 — defines the evidence standard for a support target.

    All 14 fields from the spec are present. Required-* booleans drive
    downstream lane selection in C0.2 and verification in C0.5.
    """

    support_target_id: str
    support_target_type: SupportTarget
    required_citation_precision: CitationPrecision = CitationPrecision.SECTION
    required_source_authority: SourceAuthorityClass = SourceAuthorityClass.PRIMARY
    required_freshness: str = "current"  # FreshnessClass label as string
    requires_sparse_support: bool = False
    requires_dense_support: bool = True
    requires_metadata_filter: bool = True
    requires_graph_context: bool = False
    requires_contradiction_scan: bool = False
    requires_source_parity: bool = False
    min_independent_sources: int = 1
    direct_quote_required: bool = False
    exact_symbol_required: bool = False
    exact_date_required: bool = False
    unsupported_inference_policy: UnsupportedInferencePolicy = (
        UnsupportedInferencePolicy.CAVEAT
    )

    def __post_init__(self) -> None:
        if not self.support_target_id:
            raise ValueError("support_target_id required")
        if self.min_independent_sources < 1:
            raise ValueError("min_independent_sources must be >= 1")
        # Spec rule: EXACT_QUOTE requires direct_quote_required + sparse support
        # to ensure stable citation anchors (C0 Context Engine I.4-I.5).
        if self.support_target_type is SupportTarget.EXACT_QUOTE:
            if not self.direct_quote_required:
                raise ValueError(
                    "SupportTarget.EXACT_QUOTE requires direct_quote_required=True"
                )
            if not self.requires_sparse_support:
                raise ValueError(
                    "SupportTarget.EXACT_QUOTE requires requires_sparse_support=True"
                )
        if self.support_target_type is SupportTarget.POLICY_CLAUSE:
            if self.required_citation_precision is CitationPrecision.NONE:
                raise ValueError(
                    "SupportTarget.POLICY_CLAUSE requires citation precision "
                    ">= section"
                )
        if self.support_target_type is SupportTarget.CODE_LOCATION:
            if not self.exact_symbol_required:
                raise ValueError(
                    "SupportTarget.CODE_LOCATION requires exact_symbol_required=True"
                )


class SourceDecision(str, Enum):
    """C0.1 SourceClassDecision.decision."""

    INCLUDE = "include"
    EXCLUDE = "exclude"
    REQUIRED = "required"
    OPTIONAL = "optional"


@dataclass(frozen=True)
class SourceClassDecision:
    """C0.1 PHASE 1 #3 — per-source-class decision with full audit fields."""

    source_class: SourceClass
    decision: SourceDecision
    reason_codes: tuple[str, ...] = ()
    allowed_sources: tuple[str, ...] = ()
    disallowed_sources: tuple[str, ...] = ()
    acl_scope: str = ""
    freshness_rule: str = ""
    source_authority_floor: SourceAuthorityClass = SourceAuthorityClass.SECONDARY
    metadata_filters: Mapping[str, str] = field(default_factory=dict)
    risk_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.decision is SourceDecision.EXCLUDE and not self.reason_codes:
            raise ValueError(
                "SourceClassDecision.EXCLUDE requires reason_codes "
                "(spec C0.1.3 — record excluded source classes and reasons)"
            )


class LaneFailureBehavior(str, Enum):
    """C0.1 RetrievalModePlan.failure_behavior."""

    SKIP_LANE = "skip_lane"
    PROPAGATE = "propagate"
    DEGRADE = "degrade"


@dataclass(frozen=True)
class RetrievalModePlan:
    """C0.1 PHASE 1 #4 — per-lane plan with full audit fields."""

    lane_id: str
    lane_type: RetrievalLane
    enabled: bool
    query_input_ref: str = ""
    filters: Mapping[str, str] = field(default_factory=dict)
    top_k: int = 10
    score_floor: float = 0.0
    exactness_required: bool = False
    freshness_rule: str = ""
    budget_slice: float = 0.0
    timeout_ms: int = 5000
    expected_output_contract: str = "RetrievalLaneResult"
    failure_behavior: LaneFailureBehavior = LaneFailureBehavior.SKIP_LANE

    def __post_init__(self) -> None:
        if not self.lane_id:
            raise ValueError("lane_id required")
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive")
        if not 0.0 <= self.score_floor <= 1.0:
            raise ValueError("score_floor must be in [0,1]")
        if not 0.0 <= self.budget_slice <= 1.0:
            raise ValueError("budget_slice must be in [0,1]")
        # Spec lane rules (C0.1 PHASE 1 #4):
        # - graph_seed only prepares anchors; not a fetch lane.
        if (
            self.lane_type is RetrievalLane.GRAPH_SEED
            and self.exactness_required
        ):
            raise ValueError(
                "graph_seed lane cannot have exactness_required=True "
                "(spec C0.1 PHASE 1 #4 lane rules)"
            )


# ===========================================================================
# C0.2 — RetrievalLaneResult
# ===========================================================================

@dataclass(frozen=True)
class RawHit:
    """C0.2 PHASE 1 #2 raw_hit fields."""

    raw_hit_id: str
    source_id: str
    source_type: SourceClass
    source_version: str = ""
    source_snapshot_id: str = ""
    file_path_or_doc_id: str = ""
    span_ref: str = ""
    line_range: tuple[int, int] | None = None
    timestamp_range: tuple[str, str] | None = None
    row_key: str = ""
    section_heading: str = ""
    raw_payload_ref: str = ""
    raw_text_preview: str = ""
    raw_score: float = 0.0
    retrieval_lane: RetrievalLane = RetrievalLane.DENSE
    adapter_metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.raw_hit_id:
            raise ValueError("raw_hit_id required")
        if not self.source_id:
            raise ValueError("source_id required")
        if self.line_range is not None:
            lo, hi = self.line_range
            if lo < 0 or hi < lo:
                raise ValueError(f"invalid line_range {self.line_range!r}")


class LaneTimeoutStatus(str, Enum):
    OK = "ok"
    PARTIAL = "partial"
    TIMED_OUT = "timed_out"


@dataclass(frozen=True)
class RetrievalLaneResult:
    """C0.2 PHASE 1 #2 — single-lane execution receipt.

    Replay-stable: same plan + same source snapshot -> same lane_manifest_hash.
    """

    lane_id: str
    lane_type: RetrievalLane
    query_ref: str
    adapter_id: str
    adapter_version: str
    source_class: SourceClass
    raw_hits: tuple[RawHit, ...] = ()
    raw_score_map: Mapping[str, float] = field(default_factory=dict)
    normalized_score_map: Mapping[str, float] = field(default_factory=dict)
    filter_report: Mapping[str, str] = field(default_factory=dict)
    timeout_status: LaneTimeoutStatus = LaneTimeoutStatus.OK
    error_status: str = ""
    latency_ms: int = 0
    budget_used: float = 0.0
    lane_manifest_hash: str = ""

    def __post_init__(self) -> None:
        if not self.lane_id:
            raise ValueError("lane_id required")
        if not self.adapter_id:
            raise ValueError("adapter_id required")
        if self.latency_ms < 0:
            raise ValueError("latency_ms must be >= 0")
        if self.budget_used < 0:
            raise ValueError("budget_used must be >= 0")

    def compute_manifest_hash(self) -> str:
        """Deterministic per-lane manifest hash for replay."""
        payload = {
            "lane_id": self.lane_id,
            "lane_type": self.lane_type.value,
            "adapter_id": self.adapter_id,
            "adapter_version": self.adapter_version,
            "source_class": self.source_class.value,
            "raw_hit_ids": tuple(h.raw_hit_id for h in self.raw_hits),
            "timeout_status": self.timeout_status.value,
            "error_status": self.error_status,
        }
        raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.blake2b(raw, digest_size=12).hexdigest()


# ===========================================================================
# C0.4 — EvidenceFingerprint + ExcludedEvidenceItem
# ===========================================================================

@dataclass(frozen=True)
class EvidenceFingerprint:
    """C0.4 PHASE 1 #2 — stable dedupe identity.

    Two hydrated chunks share a fingerprint when they describe the same
    underlying span across different retrieval lanes / graph relations.
    """

    source_id: str
    source_version: str = ""
    span_ref: str = ""
    line_range: tuple[int, int] | None = None
    timestamp_range: tuple[str, str] | None = None
    content_hash: str = ""
    normalized_text_hash: str = ""
    retrieval_lane_set: tuple[RetrievalLane, ...] = ()
    graph_relation_refs: tuple[GraphRelation, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_id:
            raise ValueError("source_id required")

    @property
    def fingerprint_key(self) -> str:
        """Stable identity key for dedupe — independent of retrieval lane."""
        parts = [
            self.source_id,
            self.source_version,
            self.span_ref,
            f"{self.line_range[0]}:{self.line_range[1]}" if self.line_range else "",
            self.content_hash or self.normalized_text_hash,
        ]
        raw = "|".join(parts).encode("utf-8")
        return hashlib.blake2b(raw, digest_size=8).hexdigest()


class ExclusionReason(str, Enum):
    """C0.4 ExcludedEvidenceItem.exclusion_reason — canonical codes."""

    ACL_BLOCKED = "acl_blocked"
    STALE = "stale"
    LOW_RELEVANCE = "low_relevance"
    DUPLICATE = "duplicate"
    NO_CITATION_ANCHOR = "no_citation_anchor"
    SOURCE_MISMATCH = "source_mismatch"
    TENANT_MISMATCH = "tenant_mismatch"
    REGION_MISMATCH = "region_mismatch"
    DATA_CLASS_BLOCKED = "data_class_blocked"
    BUDGET_PRUNE = "budget_prune"
    POLICY_VIOLATION = "policy_violation"
    INSTRUCTION_LIKE_PAYLOAD = "instruction_like_payload"


@dataclass(frozen=True)
class ExcludedEvidenceItem:
    """C0.4 PHASE 1 #4 — explicit exclusion record with full audit fields."""

    excluded_evidence_id: str
    original_evidence_ref: str
    exclusion_reason: ExclusionReason
    failed_gate: str = ""
    source_id: str = ""
    retrieval_lane: RetrievalLane | None = None
    score_snapshot: Mapping[str, float] = field(default_factory=dict)
    acl_status: str = ""
    freshness_status: str = ""
    lineage_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.excluded_evidence_id:
            raise ValueError("excluded_evidence_id required")
        if not self.original_evidence_ref:
            raise ValueError("original_evidence_ref required")


# ===========================================================================
# C0.5 — CitationSupportMap + SupportScoreBreakdown + EvidenceGapReport
# ===========================================================================

@dataclass(frozen=True)
class CitationSupportMap:
    """C0.5 PHASE 1 #2 — explicit per-claim citation coverage."""

    claim_target_id: str
    support_target_type: SupportTarget
    required_support_level: str  # "direct" | "corroborating" | "context-only"
    supporting_evidence_refs: tuple[str, ...] = ()
    direct_span_refs: tuple[str, ...] = ()
    indirect_context_refs: tuple[str, ...] = ()
    contradiction_refs: tuple[str, ...] = ()
    citation_precision_score: float = 0.0
    citation_recall_score: float = 0.0
    citation_anchor_status: str = "missing"
    unsupported_material_claim_risk: bool = False
    quote_eligibility: bool = False
    source_version_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.claim_target_id:
            raise ValueError("claim_target_id required")
        if not 0.0 <= self.citation_precision_score <= 1.0:
            raise ValueError("citation_precision_score must be in [0,1]")
        if not 0.0 <= self.citation_recall_score <= 1.0:
            raise ValueError("citation_recall_score must be in [0,1]")
        if (
            self.support_target_type is SupportTarget.EXACT_QUOTE
            and self.quote_eligibility
            and not self.direct_span_refs
        ):
            raise ValueError(
                "EXACT_QUOTE quote_eligibility=True requires direct_span_refs "
                "(spec C0.5 PHASE 1 #2 — exact quotes require stable source span)"
            )


@dataclass(frozen=True)
class SupportScoreBreakdownV2:
    """C0.5 PHASE 1 #3 — full 12-field score breakdown.

    Distinct from the existing ``evidence_contract.ScoreBreakdown``: that one
    is the back-compatible runtime view; this one is the spec-grade form
    used by replay manifests and OTEL emitters.
    """

    support_score: float
    directness_score: float = 0.0
    coverage_score: float = 0.0
    citation_score: float = 0.0
    freshness_score: float = 0.0
    authority_score: float = 0.0
    contradiction_penalty: float = 0.0
    lineage_score: float = 0.0
    exactness_score: float = 0.0
    source_parity_score: float = 0.0
    confidence_band: str = "medium"  # "low" | "medium" | "high"
    scoring_reason_codes: tuple[str, ...] = ()
    threshold_profile_ref: str = ""

    def __post_init__(self) -> None:
        # All scalar scores must be in [0,1]; contradiction_penalty is the
        # only one that is a magnitude (>= 0).
        bounded = [
            ("support_score", self.support_score),
            ("directness_score", self.directness_score),
            ("coverage_score", self.coverage_score),
            ("citation_score", self.citation_score),
            ("freshness_score", self.freshness_score),
            ("authority_score", self.authority_score),
            ("lineage_score", self.lineage_score),
            ("exactness_score", self.exactness_score),
            ("source_parity_score", self.source_parity_score),
        ]
        for name, val in bounded:
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name}={val} must be in [0,1]")
        if self.contradiction_penalty < 0.0:
            raise ValueError("contradiction_penalty must be >= 0")
        if self.confidence_band not in ("low", "medium", "high"):
            raise ValueError(
                f"confidence_band must be low|medium|high, got {self.confidence_band!r}"
            )


@dataclass(frozen=True)
class EvidenceGapReportV2:
    """C0.5 PHASE 1 #4 — full 11-field gap report.

    Distinct from existing ``UnresolvedGapOut`` (which is per-gap); this one
    is the aggregate gap report referenced by C0.6 for diagnosis.
    """

    missing_source_classes: tuple[SourceClass, ...] = ()
    missing_exact_terms: tuple[str, ...] = ()
    missing_citation_anchors: tuple[str, ...] = ()
    missing_versions: tuple[str, ...] = ()
    weak_lineage_refs: tuple[str, ...] = ()
    stale_sources: tuple[str, ...] = ()
    contradiction_refs: tuple[str, ...] = ()
    unresolved_scope_gaps: tuple[str, ...] = ()
    blocked_source_classes: tuple[SourceClass, ...] = ()
    insufficient_budget_notes: tuple[str, ...] = ()
    recommended_refinement_targets: tuple[str, ...] = ()

    @property
    def is_empty(self) -> bool:
        return not any(
            (
                self.missing_source_classes,
                self.missing_exact_terms,
                self.missing_citation_anchors,
                self.missing_versions,
                self.weak_lineage_refs,
                self.stale_sources,
                self.contradiction_refs,
                self.unresolved_scope_gaps,
                self.blocked_source_classes,
                self.insufficient_budget_notes,
                self.recommended_refinement_targets,
            )
        )


# ===========================================================================
# Hashing/replay helpers (cross-stage).
# ===========================================================================

def compute_profile_hash(profile: SupportTargetProfile) -> str:
    """Deterministic hash for SupportTargetProfile (replay key)."""
    raw = json.dumps(asdict(profile), sort_keys=True, default=str).encode("utf-8")
    return hashlib.blake2b(raw, digest_size=12).hexdigest()


def compute_pool_manifest_hash(
    *,
    plan_hash: str,
    raw_hit_ids: tuple[str, ...],
    lane_manifest_hashes: tuple[str, ...],
) -> str:
    """C0.2 pool_manifest_hash — deterministic over plan + sorted hits + lanes."""
    payload = {
        "plan_hash": plan_hash,
        "raw_hit_ids": sorted(raw_hit_ids),
        "lane_manifest_hashes": sorted(lane_manifest_hashes),
    }
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.blake2b(raw, digest_size=16).hexdigest()


__all__ = [
    "CitationPrecision",
    "CitationSupportMap",
    "EvidenceFingerprint",
    "EvidenceGapReportV2",
    "ExcludedEvidenceItem",
    "ExclusionReason",
    "LaneFailureBehavior",
    "LaneTimeoutStatus",
    "RawHit",
    "RetrievalLaneResult",
    "RetrievalModePlan",
    "SourceAuthorityClass",
    "SourceClassDecision",
    "SourceDecision",
    "SupportScoreBreakdownV2",
    "SupportTargetProfile",
    "UnsupportedInferencePolicy",
    "compute_pool_manifest_hash",
    "compute_profile_hash",
]
