"""C0 Context Engine / Ref Desk — bounded read-only evidence engine.

Spec: docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md

Hard law: retrieve + verify support, never generate the answer.
Pipeline: PreFlight → Plan → Fetch → Hydrate → GraphTraverse → Shape →
ContradictionGap → EvidenceContract → (RefineLoop?) → FinalEvidenceContract.

Public API surface re-exported here is the stable contract for callers
(L0 routing, Prompt Assembly bridge, audit/replay tooling).
"""

from __future__ import annotations

# Stage 0 — verdicts (enums, invariants)
from .verdicts import (
    BlockedReason,
    C0Gate,
    ContradictionType,
    EvidenceClass,
    FailureMode,
    FreshnessClass,
    GapType,
    GraphRelation,
    RecommendedDisposition,
    RefineTactic,
    RetrievalLane,
    RetrievalMode,
    SourceClass,
    SupportStatus,
    SupportTarget,
    CORE_INVARIANTS,
    EXACTNESS_REQUIRED,
)

# Stage 0 — input contracts
from .route_contract import L1PlanContract, RouteContract

# C0.0 — preflight
from .preflight import C0PreflightStatus, EvidenceStandard, run_preflight

# C0.1 — retrieval plan
from .plan import (
    Budgets,
    CachePolicy,
    DenseQuerySpec,
    GraphBounds,
    MetadataFilters,
    RetrievalPlan,
    SparseQuerySpec,
    build_retrieval_plan,
)

# C0.2 — candidate evidence pool
from .candidate_pool import (
    CandidateChunk,
    CandidateEvidencePool,
    HydrationManifest,
    RetrievalScores,
)

# C0.2A — hydration / span normalization
from .hydration import (
    ChunkBoundaryRisk,
    HydratedEvidencePool,
    QualityFlags,
    normalize_pool,
)

# C0.3 — graph traverse
from .graph_traverse import (
    GraphExpandedEvidencePool,
    GraphHop,
    GraphTraverseResult,
    expand_graph,
)

# C0.4 — shape / rerank / stratify
from .shape import (
    CompressionManifest,
    RerankSignal,
    ShapedEvidenceSet,
    StratifiedBucket,
    shape_pool,
)

# C0.4A — contradiction / gap
from .contradiction_gap import (
    ConflictGapReport,
    ContradictionFlag,
    GapFlag,
    scan_conflicts_and_gaps,
)

# C0.5 — evidence contract (verification + scoring)
from .evidence_contract import (
    EvidenceContract,
    ScoreBreakdown,
    verify_and_score,
)

# C0.6 — refine loop
from .refine_loop import (
    RefineDiagnostic,
    RefinedEvidenceContract,
    detect_compound_target,
    plan_refinement,
)

# Typed evidence projections (spec lines 1041-1080)
from .evidence_projections import (
    BackgroundEvidence,
    ContradictsEvidence,
    DefinitionEntry,
    ExcludedEntry,
    MustUseEvidence,
    SupportingEvidence,
    estimate_token_cost,
)

# Final
from .final_contract import (
    BudgetReport,
    FinalEvidenceContract,
    FreshnessReport,
    AclReport,
    PromptBudgetHint,
    ReplayMetadata,
    compute_source_manifest_hash,
    seal_final_contract,
)

# Quality gates G0–G10
from .gates import (
    GateOutcome,
    GateReport,
    run_all_gates,
    G0_scope,
    G1_acl,
    G2_fresh,
    G3_exact,
    G4_dense,
    G5_graph,
    G6_cite,
    G7_conflict,
    G8_cover,
    G9_budget,
    G10_inject,
)

# Failure-mode preventers (14)
from .failure_modes import (
    FailureModeReport,
    detect_all_failure_modes,
)

# Observability + injection guards
from .events import C0Event, C0EventRecord, C0_METRIC_NAMES, FORBIDDEN_EVENT_FIELDS
from .injection import detect_injection_markers, neutralize_for_audit

# Dispatcher — wires the pipeline
from .dispatcher import C0Dispatcher, C0Result, FetcherFn, run_c0

__all__ = [
    # enums + invariants
    "BlockedReason", "C0Gate", "ContradictionType", "EvidenceClass",
    "FailureMode", "FreshnessClass", "GapType", "GraphRelation",
    "RecommendedDisposition", "RefineTactic", "RetrievalLane",
    "RetrievalMode", "SourceClass", "SupportStatus", "SupportTarget",
    "CORE_INVARIANTS", "EXACTNESS_REQUIRED",
    # input contracts
    "L1PlanContract", "RouteContract",
    # preflight
    "C0PreflightStatus", "EvidenceStandard", "run_preflight",
    # plan
    "Budgets", "CachePolicy", "DenseQuerySpec", "GraphBounds",
    "MetadataFilters", "RetrievalPlan", "SparseQuerySpec",
    "build_retrieval_plan",
    # candidate pool
    "CandidateChunk", "CandidateEvidencePool", "HydrationManifest",
    "RetrievalScores",
    # hydration
    "ChunkBoundaryRisk", "HydratedEvidencePool", "QualityFlags",
    "normalize_pool",
    # graph
    "GraphExpandedEvidencePool", "GraphHop", "GraphTraverseResult",
    "expand_graph",
    # shape
    "CompressionManifest", "RerankSignal", "ShapedEvidenceSet",
    "StratifiedBucket", "shape_pool",
    # contradiction
    "ConflictGapReport", "ContradictionFlag", "GapFlag",
    "scan_conflicts_and_gaps",
    # contract
    "EvidenceContract", "ScoreBreakdown", "verify_and_score",
    # refine
    "RefineDiagnostic", "RefinedEvidenceContract",
    "detect_compound_target", "plan_refinement",
    # typed projections
    "BackgroundEvidence", "ContradictsEvidence", "DefinitionEntry",
    "ExcludedEntry", "MustUseEvidence", "SupportingEvidence",
    "estimate_token_cost",
    # final
    "BudgetReport", "FinalEvidenceContract", "FreshnessReport",
    "AclReport", "PromptBudgetHint", "ReplayMetadata",
    "compute_source_manifest_hash", "seal_final_contract",
    # gates
    "GateOutcome", "GateReport", "run_all_gates",
    "G0_scope", "G1_acl", "G2_fresh", "G3_exact", "G4_dense",
    "G5_graph", "G6_cite", "G7_conflict", "G8_cover", "G9_budget",
    "G10_inject",
    # failure modes
    "FailureModeReport", "detect_all_failure_modes",
    # events + injection
    "C0Event", "C0EventRecord", "C0_METRIC_NAMES", "FORBIDDEN_EVENT_FIELDS",
    "detect_injection_markers", "neutralize_for_audit",
    # dispatcher
    "C0Dispatcher", "C0Result", "FetcherFn", "run_c0",
    # C0.6 spec-grade weak-support refinement (additive)
    "AttemptStatus", "BroadenDimension", "C06Gate",
    "DecompositionPlan", "FORBIDDEN_OUTPUT_TOKENS",
    "NoMoreRefinementReport", "PrimaryGapType",
    "QueryRewritePlan", "ReentryTarget", "RefinementAttemptLedger",
    "RefinementStrategy", "ScopeBroadenPlan", "SubQuerySpec",
    "WeakSupportDiagnosis", "WeakSupportRefinementInput",
    "bridge_tactic_to_strategy", "build_no_more_refinement_report",
    "build_otel_attributes", "compute_ledger_hash",
    "compute_reentry_input_hash", "diagnose_from_contract",
    "is_eligible_for_refinement", "run_gates", "seal_ledger",
    # C0.1-C0.5 spec-grade typed contracts (additive)
    "CitationPrecision", "CitationSupportMap",
    "EvidenceFingerprint", "EvidenceGapReportV2",
    "ExcludedEvidenceItem", "ExclusionReason",
    "LaneFailureBehavior", "LaneTimeoutStatus",
    "RawHit", "RetrievalLaneResult", "RetrievalModePlan",
    "SourceAuthorityClass", "SourceClassDecision", "SourceDecision",
    "SupportScoreBreakdownV2", "SupportTargetProfile",
    "UnsupportedInferencePolicy",
    "compute_pool_manifest_hash", "compute_profile_hash",
]


# C0.6 spec-grade weak-support refinement (additive surface) ----------------
from .weak_support_refinement import (  # noqa: E402
    AttemptStatus,
    BroadenDimension,
    C06Gate,
    DecompositionPlan,
    FORBIDDEN_OUTPUT_TOKENS,
    NoMoreRefinementReport,
    PrimaryGapType,
    QueryRewritePlan,
    ReentryTarget,
    RefinementAttemptLedger,
    RefinementStrategy,
    ScopeBroadenPlan,
    SubQuerySpec,
    WeakSupportDiagnosis,
    WeakSupportRefinementInput,
    bridge_tactic_to_strategy,
    build_no_more_refinement_report,
    build_otel_attributes,
    compute_ledger_hash,
    compute_reentry_input_hash,
    diagnose_from_contract,
    is_eligible_for_refinement,
    run_gates,
    seal_ledger,
)

# C0.1-C0.5 spec-grade typed contracts (additive surface) -------------------
from .spec_contracts import (  # noqa: E402
    CitationPrecision,
    CitationSupportMap,
    EvidenceFingerprint,
    EvidenceGapReportV2,
    ExcludedEvidenceItem,
    ExclusionReason,
    LaneFailureBehavior,
    LaneTimeoutStatus,
    RawHit,
    RetrievalLaneResult,
    RetrievalModePlan,
    SourceAuthorityClass,
    SourceClassDecision,
    SourceDecision,
    SupportScoreBreakdownV2,
    SupportTargetProfile,
    UnsupportedInferencePolicy,
    compute_pool_manifest_hash,
    compute_profile_hash,
)
