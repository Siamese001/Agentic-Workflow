"""C0 Context Engine — closed vocabularies + dataclasses.

Spec: ``docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md``
Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W6.5
   (C0 spec hardening follow-up — implements every named constant in the spec.)

This module is the single source of truth for C0 enums and dataclasses. Other
modules in the package consume these types only — never re-define vocabularies
inline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Final


# ---------------------------------------------------------------------------
# C0.5 SUPPORT STATUS — six values per spec.
# ---------------------------------------------------------------------------


class SupportStatus(Enum):
    PASS = "PASS"
    WEAK = "WEAK"
    WEAK_WITH_CAVEATS = "WEAK_WITH_CAVEATS"
    CONFLICTED = "CONFLICTED"
    EMPTY = "EMPTY"
    BLOCKED = "BLOCKED"


# ---------------------------------------------------------------------------
# C0.1 SUPPORT TARGET TYPES — eight values per spec.
# ---------------------------------------------------------------------------


class SupportTarget(Enum):
    EXACT_QUOTE = "EXACT_QUOTE"
    SOURCE_SUMMARY = "SOURCE_SUMMARY"
    POLICY_CLAUSE = "POLICY_CLAUSE"
    CODE_LOCATION = "CODE_LOCATION"
    INCIDENT_EVIDENCE = "INCIDENT_EVIDENCE"
    ROOT_CAUSE_RANKING = "ROOT_CAUSE_RANKING"
    COMPARISON = "COMPARISON"
    CLAIM_CHECK = "CLAIM_CHECK"


# ---------------------------------------------------------------------------
# C0.1 SOURCE CLASSES — seven values per spec.
# ---------------------------------------------------------------------------


SOURCE_CLASSES: Final[frozenset[str]] = frozenset(
    {"docs", "code", "logs", "tickets", "tables", "policy", "prior_artifacts"},
)


# ---------------------------------------------------------------------------
# C0.1 RETRIEVAL MODES — six values per spec.
# ---------------------------------------------------------------------------


RETRIEVAL_MODES: Final[frozenset[str]] = frozenset(
    {"dense", "sparse", "metadata", "graph", "cache", "hybrid"},
)


# ---------------------------------------------------------------------------
# C0.1 BOUNDS — nine named bound parameters per spec.
# ---------------------------------------------------------------------------


BOUND_PARAMS: Final[tuple[str, ...]] = (
    "max_k",
    "max_parent_expansion",
    "max_child_expansion",
    "max_graph_hops",
    "max_refine_attempts",
    "max_token_context",
    "max_source_classes",
    "max_latency_ms",
    "max_cost_tier",
)


# ---------------------------------------------------------------------------
# C0.4 STRATIFY — seven evidence classes per spec.
# ---------------------------------------------------------------------------


class EvidenceClass(Enum):
    MUST_USE = "MUST_USE"
    SUPPORTING = "SUPPORTING"
    CONTRADICTS = "CONTRADICTS"
    BACKGROUND = "BACKGROUND"
    DEFINITIONS = "DEFINITIONS"
    LINEAGE = "LINEAGE"
    EXCLUDED = "EXCLUDED"


# ---------------------------------------------------------------------------
# C0.4A CONTRADICTION TYPES — eight values per spec.
# ---------------------------------------------------------------------------


class ContradictionType(Enum):
    VERSION = "version"
    SOURCE = "source"
    SCOPE = "scope"
    TIME = "time"
    SEMANTIC = "semantic"
    CODE = "code"
    RUNTIME = "runtime"
    POLICY = "policy"


# ---------------------------------------------------------------------------
# C0.4A GAP TYPES — nine values per spec.
# ---------------------------------------------------------------------------


class GapType(Enum):
    MISSING_DIRECT_SUPPORT = "missing_direct_support"
    MISSING_EXACT_QUOTE = "missing_exact_quote"
    MISSING_CURRENT_VERSION = "missing_current_version"
    MISSING_OWNER_AUTHORITY = "missing_owner_authority"
    MISSING_SOURCE_DIVERSITY = "missing_source_diversity"
    MISSING_VALIDATION = "missing_validation"
    MISSING_CITATION_ANCHOR = "missing_citation_anchor"
    MISSING_TIME_RANGE = "missing_time_range"
    MISSING_TENANT_ACL_PROOF = "missing_tenant_acl_proof"


# ---------------------------------------------------------------------------
# C0.5 SCORE DIMENSIONS — eleven dimensions per spec.
# ---------------------------------------------------------------------------


SCORE_DIMENSIONS: Final[tuple[str, ...]] = (
    "direct_support_score",
    "coverage_score",
    "source_authority_score",
    "freshness_score",
    "contradiction_risk",
    "unsupported_inference_risk",
    "citation_stability_score",
    "lineage_quality_score",
    "source_diversity_score",
    "exactness_score",
    "ACL_confidence",
)


# ---------------------------------------------------------------------------
# C0.5 / FINAL CONTRACT RECOMMENDED DISPOSITION — six values per spec.
# ---------------------------------------------------------------------------


class RecommendedDisposition(Enum):
    PROCEED = "proceed"
    PROCEED_WITH_CAVEAT = "proceed_with_caveat"
    ABSTAIN = "abstain"
    FALLBACK_R5 = "fallback_R5"
    REROUTE = "reroute"
    HUMAN_REVIEW = "human_review"


# ---------------------------------------------------------------------------
# C0.6 REFINE TACTICS — eight allowed tactics per spec.
# ---------------------------------------------------------------------------


class RefineTactic(Enum):
    REWRITE = "REWRITE"
    BROADEN = "BROADEN"
    NARROW = "NARROW"
    DECOMPOSE = "DECOMPOSE"
    GRAPH_HOP = "GRAPH_HOP"
    HYBRIDIZE = "HYBRIDIZE"
    FRESHEN = "FRESHEN"
    ABSTAIN = "ABSTAIN"


# C0.6 DISALLOWED refinements — strings rather than enum because they describe
# behaviors that the system must reject, not choose.
DISALLOWED_REFINEMENTS: Final[frozenset[str]] = frozenset(
    {
        "change_user_task",
        "change_route",
        "expand_tenant_acl_region",
        "ignore_contradictions",
        "invent_source_authority",
        "convert_read_to_action",
        "modify_durable_memory",
    },
)


# ---------------------------------------------------------------------------
# C0 quality-gate identifiers — eleven gates per spec (G0..G10).
# ---------------------------------------------------------------------------


QUALITY_GATES: Final[tuple[str, ...]] = (
    "C0.G0_Scope",
    "C0.G1_ACL",
    "C0.G2_Fresh",
    "C0.G3_Exact",
    "C0.G4_Dense",
    "C0.G5_Graph",
    "C0.G6_Cite",
    "C0.G7_Conflict",
    "C0.G8_Cover",
    "C0.G9_Budget",
    "C0.G10_Inject",
)


# ---------------------------------------------------------------------------
# C0 invariants — twelve invariants per spec (I1..I12).
# ---------------------------------------------------------------------------


INVARIANTS: Final[tuple[str, ...]] = tuple(f"C0.I{i}" for i in range(1, 13))


# ---------------------------------------------------------------------------
# Failure modes per spec — fourteen named failure modes the engine prevents.
# ---------------------------------------------------------------------------


FAILURE_MODES: Final[tuple[str, ...]] = (
    "dense_only_hallucination",
    "wrong_tenant_evidence",
    "stale_policy_answer",
    "quote_distortion",
    "hidden_contradiction",
    "graph_scope_creep",
    "cache_poisoning",
    "prompt_injection_via_retrieved_text",
    "fake_confidence",
    "lost_lineage",
    "overstuffed_context",
    "unsupported_synthesis",
    "docs_vs_code_mismatch",
    "runtime_vs_design_mismatch",
)


# ---------------------------------------------------------------------------
# Dataclasses.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class L1C0Advisory:
    """W2 c0-policy-rectification-f7b2a9 — L1 advisory grounding analysis.

    L1 may declare semantic grounding need, but L0 is the authority that
    freezes the C0 policy into RouteContract.c0_policy. This dataclass
    represents L1's advisory opinion only; it does not authorize C0 runtime.
    """

    # Advisory signal from L1 reasoning
    grounding_required: bool
    """L1 opinion: does the task require grounded evidence?"""

    support_expectation: str = ""
    """What kind of support L1 expects (e.g., 'policy_clause', 'source_summary')."""

    support_target: SupportTarget = SupportTarget.SOURCE_SUMMARY
    """Target type for evidence retrieval."""

    grounding_reason_codes: tuple[str, ...] = ()
    """Why L1 believes grounding is/isn't required (traceability)."""

    confidence: float = 0.85
    """L1 confidence in the grounding assessment [0.0, 1.0]."""


@dataclass(frozen=True)
class RouteContractView:
    """The subset of L0 RouteContract fields C0 needs."""

    route_id: str
    grounding_required: bool
    execution_form: str
    freshness_class: str
    support_target: SupportTarget
    tenant_scope: str
    acl: tuple[str, ...]
    region: str
    data_class: str
    max_k: int
    max_hops: int
    max_parent_expansion: int
    max_refine_attempts: int
    max_latency_ms: int
    token_budget: int
    allowed_sources: frozenset[str]
    disallowed_sources: frozenset[str]
    fallback_policy: str
    route_replay_key: str
    policy_hash: str
    blueprint_hash: str


@dataclass(frozen=True)
class C0PreflightStatus:
    """C0.0 output — eligibility decision."""

    eligible: bool
    blocked_reason: str
    allowed_source_classes: frozenset[str]
    evidence_standard: str
    budget_floor_tokens: int


@dataclass(frozen=True)
class RetrievalPlan:
    """C0.1 output — bounded plan, no fetch yet."""

    source_classes: frozenset[str]
    allowed_sources: frozenset[str]
    disallowed_sources: frozenset[str]
    retrieval_modes: frozenset[str]
    support_target: SupportTarget
    freshness_rule: str
    evidence_standard: str
    bounds: dict[str, int]
    cache_policy: str
    weak_support_policy: str
    replay_metadata: dict[str, str]


@dataclass(frozen=True)
class EvidenceItem:
    """One retrieved + verified evidence row."""

    evidence_id: str
    source_id: str
    source_class: str
    span_ref: str
    quote_or_summary: str
    retrieval_lane: str
    authority_score: float
    freshness_status: str
    acl_status: str
    token_cost: int
    evidence_class: EvidenceClass = EvidenceClass.SUPPORTING


@dataclass(frozen=True)
class ContradictionFlag:
    contradiction_type: ContradictionType
    source_a: str
    source_b: str
    severity: float
    summary: str


@dataclass(frozen=True)
class UnresolvedGap:
    gap_type: GapType
    severity: float
    impact_on_answer: str
    suggested_next_step: str


@dataclass(frozen=True)
class ScoreBreakdown:
    """11-dimension score map. Every dimension in [0, 1]."""

    direct_support_score: float = 0.0
    coverage_score: float = 0.0
    source_authority_score: float = 0.0
    freshness_score: float = 0.0
    contradiction_risk: float = 0.0
    unsupported_inference_risk: float = 0.0
    citation_stability_score: float = 0.0
    lineage_quality_score: float = 0.0
    source_diversity_score: float = 0.0
    exactness_score: float = 0.0
    ACL_confidence: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {dim: getattr(self, dim) for dim in SCORE_DIMENSIONS}  # guardian: allow-hallucinated-tool-name -- getattr is Python stdlib; reads score dimension attrs by name


@dataclass(frozen=True)
class FinalEvidenceContract:
    """The output Prompt Assembly consumes."""

    contract_id: str
    route_id: str
    route_replay_key: str
    policy_hash: str
    blueprint_hash: str
    status: SupportStatus
    support_score: float
    score_breakdown: ScoreBreakdown
    evidence: tuple[EvidenceItem, ...]
    contradiction_flags: tuple[ContradictionFlag, ...]
    unresolved_gaps: tuple[UnresolvedGap, ...]
    recommended_disposition: RecommendedDisposition
    refine_attempts: int = 0
    extras: dict[str, str] = field(default_factory=dict)


__all__ = [
    "BOUND_PARAMS",
    "C0PreflightStatus",
    "L1C0Advisory",
    "ContradictionFlag",
    "ContradictionType",
    "DISALLOWED_REFINEMENTS",
    "EvidenceClass",
    "EvidenceItem",
    "FAILURE_MODES",
    "FinalEvidenceContract",
    "GapType",
    "INVARIANTS",
    "QUALITY_GATES",
    "RETRIEVAL_MODES",
    "RecommendedDisposition",
    "RefineTactic",
    "RetrievalPlan",
    "RouteContractView",
    "SCORE_DIMENSIONS",
    "SOURCE_CLASSES",
    "ScoreBreakdown",
    "SupportStatus",
    "SupportTarget",
    "UnresolvedGap",
]
