"""C0.3 contracts — every dataclass / enum required by Phase 1 + Phase 5 of
the enhanced spec.

All structures are frozen ``dataclass`` instances with explicit
``__post_init__`` validation. The field set matches the spec line-for-line.
Field types are intentionally loose (``str | None``, ``tuple[Any, ...]``)
where the spec marks values "optional" or "object", so adapters can populate
domain-specific values without losing schema clarity.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Mapping


# ---------------------------------------------------------------------------
# enums
# ---------------------------------------------------------------------------


class AclStatus(str, Enum):
    """Spec: HydratedEvidence.acl_status enum."""

    ALLOWED = "allowed"
    CLEARED = "cleared"
    DENIED = "denied"
    UNKNOWN = "unknown"


class FreshnessStatus(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    HISTORICAL = "historical"
    UNKNOWN = "unknown"


class FreshnessClass(str, Enum):
    """Mirror of route freshness expectation, restated locally for self-contained
    C0.3 input.
    """

    LATEST = "latest"
    CURRENT = "current"
    SLOW = "slow"
    STATIC = "static"
    HISTORICAL = "historical"


class RetrievalLane(str, Enum):
    DENSE = "dense"
    SPARSE = "sparse"
    METADATA = "metadata"
    GRAPH_SEED = "graph_seed"
    CACHE = "cache"
    TRACE = "trace"
    CODE = "code"


class SupportTarget(str, Enum):
    """Spec Phase 3.4 — every support target that drives plan policy."""

    EXACT_QUOTE = "EXACT_QUOTE"
    SOURCE_SUMMARY = "SOURCE_SUMMARY"
    POLICY_CLAUSE = "POLICY_CLAUSE"
    CODE_LOCATION = "CODE_LOCATION"
    INCIDENT_EVIDENCE = "INCIDENT_EVIDENCE"
    ROOT_CAUSE_RANKING = "ROOT_CAUSE_RANKING"
    COMPARISON = "COMPARISON"
    CLAIM_CHECK = "CLAIM_CHECK"
    ARCHITECTURE_BOUNDARY = "ARCHITECTURE_BOUNDARY"
    BLAST_RADIUS = "BLAST_RADIUS"
    GOVERNANCE_DECISION = "GOVERNANCE_DECISION"


class AnchorType(str, Enum):
    """Spec: ResolvedGraphAnchor.anchor_type."""

    DOCUMENT = "document"
    SECTION = "section"
    CODE_SYMBOL = "code_symbol"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    POLICY = "policy"
    SCHEMA = "schema"
    SERVICE = "service"
    OWNER = "owner"
    TRACE = "trace"
    INCIDENT = "incident"
    TICKET = "ticket"
    ROUTE = "route"
    EVALUATION_BUNDLE = "evaluation_bundle"
    SEALED_RUN = "sealed_run"
    UNKNOWN = "unknown"


class GraphRelationType(str, Enum):
    """Default vocabulary; adapters may use any string but these are recognized
    by support-target plan policy.
    """

    DEFINES = "defines"
    REFERENCES = "references"
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    IMPORTS = "imports"
    CALLS = "calls"
    OWNS = "owns"
    OWNED_BY = "owned_by"
    DEPENDS_ON = "depends_on"
    DEPENDED_ON_BY = "depended_on_by"
    SUPERSEDES = "supersedes"
    SUPERSEDED_BY = "superseded_by"
    CONTRADICTS = "contradicts"
    DUPLICATES = "duplicates"
    IMPLEMENTS = "implements"
    IMPLEMENTED_BY = "implemented_by"
    GOVERNED_BY = "governed_by"
    GOVERNS = "governs"
    DERIVED_FROM = "derived_from"
    OBSERVED_IN = "observed_in"
    TRIGGERED_BY = "triggered_by"
    REMEDIATED_BY = "remediated_by"
    DEPLOYMENT = "deployment"
    TICKET = "ticket"
    TRACE = "trace"
    SOURCE_VERSION = "source_version"
    SOURCE_AUTHORITY = "source_authority"
    APPROVED_BY = "approved_by"
    REQUIRES = "requires"
    PROHIBITS = "prohibits"
    EXCEPTION_TO = "exception_to"
    EVIDENCE = "evidence"
    TESTED_BY = "tested_by"
    VIOLATES = "violates"
    BLOCKED_FROM = "blocked_from"
    PROJECTED_TO = "projected_to"
    USED_BY = "used_by"
    EMITS = "emits"


class RejectionReason(str, Enum):
    """Spec: RejectedGraphNeighbor.rejection_reason — closed set."""

    ACL_FAILED = "acl_failed"
    WRONG_TENANT = "wrong_tenant"
    WRONG_REGION = "wrong_region"
    BLOCKED_DATA_CLASS = "blocked_data_class"
    RELATION_TYPE_NOT_ALLOWED = "relation_type_not_allowed"
    SOURCE_CLASS_NOT_ALLOWED = "source_class_not_allowed"
    MAX_HOPS_EXCEEDED = "max_hops_exceeded"
    MAX_NODES_EXCEEDED = "max_nodes_exceeded"
    MAX_EDGES_EXCEEDED = "max_edges_exceeded"
    STALE = "stale"
    PROJECTION_STALE = "projection_stale"
    LOW_CONFIDENCE = "low_confidence"
    MISSING_LINEAGE = "missing_lineage"
    NO_CITATION_ANCHOR = "no_citation_anchor"
    INTERESTING_NOT_RELEVANT = "interesting_not_relevant"
    DUPLICATE = "duplicate"
    CYCLE_DETECTED = "cycle_detected"
    SUPPORT_TARGET_MISMATCH = "support_target_mismatch"
    INSTRUCTION_LIKE_PAYLOAD = "instruction_like_payload"
    GRAPH_SOURCE_BLOCKED = "graph_source_blocked"


class ContradictionType(str, Enum):
    """Spec Phase 5 — contradiction taxonomy."""

    VERSION = "version_contradiction"
    SOURCE = "source_contradiction"
    SCOPE = "scope_contradiction"
    TIME = "time_contradiction"
    SEMANTIC = "semantic_contradiction"
    DOCS_VS_CODE = "docs_vs_code"
    RUNTIME_VS_DESIGN = "runtime_vs_design"
    POLICY_VS_IMPLEMENTATION = "policy_vs_implementation"
    TENANT_OVERRIDE = "tenant_specific_override"


class GapType(str, Enum):
    """Spec Phase 5 — gap taxonomy."""

    MISSING_OWNER = "missing_owner"
    MISSING_CURRENT_VERSION = "missing_current_version"
    MISSING_IMPLEMENTATION_LINK = "missing_implementation_link"
    MISSING_RUNTIME_EVIDENCE = "missing_runtime_evidence"
    MISSING_POLICY_LINK = "missing_policy_link"
    MISSING_SOURCE_LINEAGE = "missing_source_lineage"
    MISSING_DEPENDENCY_CONTEXT = "missing_dependency_context"
    MISSING_CONTRADICTION_SCAN = "missing_contradiction_scan"
    MISSING_TENANT_SPECIFIC_SOURCE = "missing_tenant_specific_source"
    MISSING_GRAPH_PROJECTION = "missing_graph_projection"
    MISSING_STABLE_CITATION_ANCHOR = "missing_stable_citation_anchor"
    MISSING_EXACT_SYMBOL_RESOLUTION = "missing_exact_symbol_resolution"
    MISSING_CODE_TEST_VALIDATION = "missing_code_test_validation"
    MISSING_EVALUATION_BUNDLE = "missing_evaluation_bundle"
    MISSING_SEALED_RUN = "missing_sealed_run"


# ---------------------------------------------------------------------------
# 1. HydratedEvidence
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HydratedEvidence:
    """One normalized candidate from C0.2A — Phase 1 §1."""

    evidence_id: str
    source_id: str
    retrieval_lane: RetrievalLane | str
    acl_status: AclStatus | str

    source_type: str = ""
    source_authority_class: str | None = None
    source_version: str | None = None
    source_snapshot_id: str | None = None
    file_path_or_doc_id: str | None = None
    span_ref: str | None = None
    line_range: tuple[int, int] | None = None
    timestamp_range: tuple[str, str] | None = None

    tenant: str | None = None
    region: str | None = None
    data_class: str | None = None

    raw_score: float | None = None
    normalized_score: float | None = None
    support_target_relevance: float | None = None

    candidate_text_or_payload: str | None = None
    extracted_entities: tuple[str, ...] = field(default_factory=tuple)
    extracted_symbols: tuple[str, ...] = field(default_factory=tuple)
    extracted_dates: tuple[str, ...] = field(default_factory=tuple)
    extracted_ids: tuple[str, ...] = field(default_factory=tuple)

    parent_context_refs: tuple[str, ...] = field(default_factory=tuple)
    child_context_refs: tuple[str, ...] = field(default_factory=tuple)
    citation_anchor_status: str | None = None  # "ok" | "missing" | "weak"
    hydration_flags: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ValueError("HydratedEvidence.evidence_id is required")
        if not self.source_id:
            raise ValueError("HydratedEvidence.source_id is required")
        if not self.acl_status:
            raise ValueError("HydratedEvidence.acl_status is required")
        if not self.retrieval_lane:
            raise ValueError("HydratedEvidence.retrieval_lane is required")

    @property
    def has_citation_anchor(self) -> bool:
        return bool(self.span_ref) or self.citation_anchor_status == "ok"


# ---------------------------------------------------------------------------
# 2. GraphTraverseInput
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphTraverseInput:
    """Phase 1 §2 — bounded input contract for ``run_graph_traverse``."""

    route_id: str
    route_replay_key: str
    policy_hash: str
    blueprint_hash: str
    support_target: SupportTarget | str
    freshness_class: FreshnessClass | str

    tenant_scope: str | None = None
    acl_scope: tuple[str, ...] = field(default_factory=tuple)
    region_scope: str | None = None
    data_class_scope: tuple[str, ...] = field(default_factory=tuple)

    max_hops: int = 1
    max_nodes: int = 64
    max_edges: int = 128
    max_parent_expansion: int = 8
    max_child_expansion: int = 8
    max_relation_types: int = 16
    max_contradiction_edges: int = 16
    max_dependency_edges: int = 32
    max_lineage_edges: int = 32
    max_latency_ms: int = 5_000
    max_token_budget_for_graph_context: int = 4_000

    allowed_graph_sources: tuple[str, ...] = field(default_factory=tuple)
    disallowed_graph_sources: tuple[str, ...] = field(default_factory=tuple)
    allowed_relation_types: tuple[str, ...] = field(default_factory=tuple)
    disallowed_relation_types: tuple[str, ...] = field(default_factory=tuple)
    allowed_source_classes: tuple[str, ...] = field(default_factory=tuple)
    disallowed_source_classes: tuple[str, ...] = field(default_factory=tuple)

    confidence_threshold: float = 0.0
    require_citation_anchor: bool = False

    hydrated_candidates: tuple[HydratedEvidence, ...] = field(default_factory=tuple)
    allow_empty_candidates: bool = False

    def __post_init__(self) -> None:
        if not self.route_replay_key:
            raise ValueError("GraphTraverseInput.route_replay_key is required")
        if not self.policy_hash:
            raise ValueError("GraphTraverseInput.policy_hash is required")
        if not self.support_target:
            raise ValueError("GraphTraverseInput.support_target is required")
        if not self.blueprint_hash:
            raise ValueError("GraphTraverseInput.blueprint_hash is required")
        if self.max_hops < 0:
            raise ValueError("GraphTraverseInput.max_hops must be >= 0")
        if self.max_hops > 0:
            if self.max_nodes <= 0 or self.max_edges <= 0:
                raise ValueError(
                    "GraphTraverseInput.max_nodes/max_edges must be positive when traversal enabled"
                )
            if not self.allowed_relation_types:
                raise ValueError(
                    "GraphTraverseInput.allowed_relation_types must be explicit when max_hops > 0"
                )
        if not self.hydrated_candidates and not self.allow_empty_candidates:
            raise ValueError(
                "GraphTraverseInput.hydrated_candidates must not be empty unless allow_empty_candidates is True"
            )


# ---------------------------------------------------------------------------
# 3. ResolvedGraphAnchor / AnchorCandidateSet
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AnchorCandidate:
    """Output of ``extract_anchors`` — pre-resolution anchor request."""

    anchor_value: str
    anchor_type: AnchorType
    original_evidence_id: str
    hint_source_id: str | None = None
    hint_source_version: str | None = None
    hint_file_path: str | None = None
    confidence: float = 0.5

    def __post_init__(self) -> None:
        if not self.anchor_value:
            raise ValueError("AnchorCandidate.anchor_value is required")
        if not self.original_evidence_id:
            raise ValueError("AnchorCandidate.original_evidence_id is required")


@dataclass(frozen=True)
class AnchorCandidateSet:
    candidates: tuple[AnchorCandidate, ...]
    unresolved_anchor_candidates: tuple[AnchorCandidate, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ResolvedGraphAnchor:
    """Phase 1 §3."""

    anchor_id: str
    original_evidence_id: str
    anchor_type: AnchorType
    anchor_value: str
    resolved_node_id: str
    graph_source: str
    source_id: str
    source_version: str
    confidence: float
    resolution_reason: str
    acl_status: AclStatus | str
    tenant: str | None = None
    region: str | None = None
    data_class: str | None = None

    def __post_init__(self) -> None:
        if not self.anchor_id:
            raise ValueError("ResolvedGraphAnchor.anchor_id is required")
        if not self.resolved_node_id:
            raise ValueError("ResolvedGraphAnchor.resolved_node_id is required")
        if not self.graph_source:
            raise ValueError("ResolvedGraphAnchor.graph_source is required")
        if not self.source_id:
            raise ValueError("ResolvedGraphAnchor.source_id is required")
        if not self.resolution_reason:
            raise ValueError("ResolvedGraphAnchor.resolution_reason is required")


@dataclass(frozen=True)
class ResolvedAnchorSet:
    resolved: tuple[ResolvedGraphAnchor, ...]
    ambiguous: tuple[AnchorCandidate, ...] = field(default_factory=tuple)
    unresolved: tuple[AnchorCandidate, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# 4. GraphTraversalPlan
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphBudget:
    """Plan-level budget mirror of input bounds; never exceeds GraphTraverseInput."""

    max_hops: int
    max_nodes: int
    max_edges: int
    max_neighbors_by_anchor: int
    max_latency_ms: int
    max_token_budget_for_graph_context: int


@dataclass(frozen=True)
class GraphTraversalPlan:
    """Phase 1 §4 — deterministic plan derived from input + support target."""

    start_nodes: tuple[str, ...]
    allowed_relation_types: tuple[str, ...]
    relation_priority_order: tuple[str, ...]
    max_hops_by_relation_type: Mapping[str, int]
    max_neighbors_by_anchor: int
    contradiction_scan_enabled: bool
    supersession_scan_enabled: bool
    dependency_scan_enabled: bool
    lineage_scan_enabled: bool
    runtime_scan_enabled: bool
    definition_scan_enabled: bool
    owner_scan_enabled: bool
    source_authority_scan_enabled: bool
    graph_budget: GraphBudget
    stop_conditions: tuple[str, ...]
    replay_metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        allowed = set(self.allowed_relation_types)
        for rel in self.relation_priority_order:
            if rel not in allowed:
                raise ValueError(
                    f"GraphTraversalPlan.relation_priority_order contains '{rel}' "
                    f"which is not in allowed_relation_types"
                )


# ---------------------------------------------------------------------------
# 5. AcceptedGraphNeighbor
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AcceptedGraphNeighbor:
    """Phase 1 §5."""

    neighbor_id: str
    neighbor_type: str
    source_id: str
    source_type: str
    source_version: str
    relation_path: tuple[str, ...]
    relation_types: tuple[str, ...]
    hop_distance: int
    inclusion_reason: str
    support_contribution: str
    authority_contribution: str
    freshness_status: FreshnessStatus | str
    acl_status: AclStatus | str
    confidence: float
    lineage_refs: tuple[str, ...]
    graph_source: str
    span_ref: str | None = None
    projection_version: str | None = None
    snapshot_pointer: str | None = None
    flag_categories: tuple[str, ...] = field(default_factory=tuple)
    payload_preview: str | None = None
    is_projected: bool = True

    def __post_init__(self) -> None:
        if not self.relation_path:
            raise ValueError("AcceptedGraphNeighbor.relation_path is required")
        if not self.relation_types:
            raise ValueError("AcceptedGraphNeighbor.relation_types is required")
        if self.hop_distance < 0:
            raise ValueError("AcceptedGraphNeighbor.hop_distance must be >= 0")
        if not self.inclusion_reason:
            raise ValueError("AcceptedGraphNeighbor.inclusion_reason is required")
        if not self.graph_source:
            raise ValueError("AcceptedGraphNeighbor.graph_source is required")
        if self.is_projected:
            if not self.projection_version:
                raise ValueError(
                    "AcceptedGraphNeighbor.projection_version required when graph_source is projected"
                )
            if not self.snapshot_pointer:
                raise ValueError(
                    "AcceptedGraphNeighbor.snapshot_pointer required when graph_source is projected"
                )
        acl_value = self.acl_status.value if isinstance(self.acl_status, AclStatus) else str(self.acl_status)
        if acl_value not in {AclStatus.ALLOWED.value, AclStatus.CLEARED.value}:
            raise ValueError(f"AcceptedGraphNeighbor.acl_status must be allowed/cleared, got '{acl_value}'")


# ---------------------------------------------------------------------------
# 6. RejectedGraphNeighbor
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RejectedGraphNeighbor:
    """Phase 1 §6 — every rejection retained for audit/replay."""

    neighbor_id: str
    relation_path: tuple[str, ...]
    rejection_reason: RejectionReason | str
    failed_gate: str
    hop_distance: int
    source_id: str
    acl_status: AclStatus | str
    freshness_status: FreshnessStatus | str

    def __post_init__(self) -> None:
        if not self.failed_gate:
            raise ValueError("RejectedGraphNeighbor.failed_gate is required")
        if not self.rejection_reason:
            raise ValueError("RejectedGraphNeighbor.rejection_reason is required")
        if self.hop_distance < 0:
            raise ValueError("RejectedGraphNeighbor.hop_distance must be >= 0")


# ---------------------------------------------------------------------------
# 5b. Contradiction / Supersession / Gap captures (Phase 5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContradictionCandidate:
    conflict_type: ContradictionType | str
    source_a: str
    source_b: str
    relation_path: tuple[str, ...]
    severity: str  # "low" | "medium" | "high" | "blocker"
    confidence: float
    downstream_required_behavior: str
    note: str = ""

    def __post_init__(self) -> None:
        if not self.source_a or not self.source_b:
            raise ValueError("ContradictionCandidate requires both source_a and source_b")
        if not self.downstream_required_behavior:
            raise ValueError("ContradictionCandidate.downstream_required_behavior is required")


@dataclass(frozen=True)
class SupersessionCandidate:
    superseded_source_id: str
    superseding_source_id: str
    relation_path: tuple[str, ...]
    confidence: float
    reason: str

    def __post_init__(self) -> None:
        if not self.superseded_source_id or not self.superseding_source_id:
            raise ValueError("SupersessionCandidate requires both source ids")


@dataclass(frozen=True)
class GapFinding:
    gap_type: GapType | str
    affected_evidence_id: str
    why_it_matters: str
    severity: str
    suggested_refine_tactic: str
    can_answer_with_caveat: bool

    def __post_init__(self) -> None:
        if not self.affected_evidence_id:
            raise ValueError("GapFinding.affected_evidence_id is required")
        if not self.why_it_matters:
            raise ValueError("GapFinding.why_it_matters is required")


@dataclass(frozen=True)
class InstructionPayloadFlag:
    """Phase 6 — graph payload caught looking like instructions."""

    neighbor_id: str
    matched_markers: tuple[str, ...]
    quarantined_preview: str
    excluded_from_prompt: bool
    allowed_for_security_analysis: bool


# ---------------------------------------------------------------------------
# 7. GraphTraversalManifest
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphTraversalManifest:
    """Phase 1 §8 — replayable manifest for observability + verification."""

    graph_source: str
    graph_snapshot_id: str
    projection_version: str
    traversal_policy_hash: str
    allowed_relation_types_used: tuple[str, ...]
    blocked_relation_types_seen: tuple[str, ...]
    hops_used: int
    nodes_seen: int
    edges_seen: int
    nodes_accepted: int
    edges_accepted: int
    nodes_rejected: int
    edges_rejected: int
    latency_ms: int
    budget_remaining: Mapping[str, int]
    replay_seed: str
    manifest_hash: str

    def __post_init__(self) -> None:
        if self.hops_used < 0:
            raise ValueError("manifest.hops_used must be >= 0")
        if self.nodes_seen < 0 or self.edges_seen < 0:
            raise ValueError("manifest.nodes_seen / edges_seen must be >= 0")
        if not self.manifest_hash:
            raise ValueError("manifest.manifest_hash is required")


# Volatile fields excluded from manifest_hash so the hash is deterministic
# across runs with identical structural inputs. Phase 1 §8 contract:
# "manifest_hash must be deterministic from stable manifest fields."
_UNSTABLE_MANIFEST_FIELDS: frozenset[str] = frozenset(
    {
        "manifest_hash",
        "latency_ms",
        "budget_remaining",  # contains volatile latency_ms remaining
    }
)


def compute_manifest_hash(payload: Mapping[str, Any]) -> str:
    """Deterministic hash over stable manifest fields.

    Excludes:
      * ``manifest_hash`` itself (filled in after computation),
      * any field whose name starts with ``_`` (reserved for private/runtime),
      * ``latency_ms`` and ``budget_remaining`` (clock-dependent, vary per run).
    """
    stable = {
        k: v for k, v in payload.items() if not k.startswith("_") and k not in _UNSTABLE_MANIFEST_FIELDS
    }
    canonical = json.dumps(
        stable,
        sort_keys=True,
        default=_json_default,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _json_default(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (set, frozenset)):
        return sorted(obj)
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


# ---------------------------------------------------------------------------
# 8. GraphExpandedEvidencePool
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphExpandedEvidencePool:
    """Phase 1 §7 — output of C0.3 consumed by C0.4."""

    original_candidates: tuple[HydratedEvidence, ...]
    accepted_graph_neighbors: tuple[AcceptedGraphNeighbor, ...]
    rejected_graph_neighbors: tuple[RejectedGraphNeighbor, ...]
    entity_map: Mapping[str, tuple[str, ...]]
    symbol_map: Mapping[str, tuple[str, ...]]
    relation_map: Mapping[str, tuple[str, ...]]
    lineage_edges: tuple[AcceptedGraphNeighbor, ...]
    dependency_context: tuple[AcceptedGraphNeighbor, ...]
    ownership_context: tuple[AcceptedGraphNeighbor, ...]
    source_authority_context: tuple[AcceptedGraphNeighbor, ...]
    contradiction_candidates: tuple[ContradictionCandidate, ...]
    supersession_candidates: tuple[SupersessionCandidate, ...]
    implementation_context: tuple[AcceptedGraphNeighbor, ...]
    runtime_context: tuple[AcceptedGraphNeighbor, ...]
    prior_run_context: tuple[AcceptedGraphNeighbor, ...]
    graph_traversal_manifest: GraphTraversalManifest
    instruction_payload_flags: tuple[InstructionPayloadFlag, ...] = field(default_factory=tuple)
    gap_findings: tuple[GapFinding, ...] = field(default_factory=tuple)
    unresolved_anchors: tuple[AnchorCandidate, ...] = field(default_factory=tuple)
    ambiguous_anchors: tuple[AnchorCandidate, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        # original_candidates must be preserved unchanged — caller passes a
        # fresh tuple. We only sanity-check non-empty when accepted/rejected
        # are populated.
        if (self.accepted_graph_neighbors or self.rejected_graph_neighbors) and not self.original_candidates:
            raise ValueError("original_candidates must be preserved when traversal produced output")


__all__ = [
    "AclStatus",
    "AcceptedGraphNeighbor",
    "AnchorCandidate",
    "AnchorCandidateSet",
    "AnchorType",
    "ContradictionCandidate",
    "ContradictionType",
    "FreshnessClass",
    "FreshnessStatus",
    "GapFinding",
    "GapType",
    "GraphBudget",
    "GraphExpandedEvidencePool",
    "GraphRelationType",
    "GraphTraversalManifest",
    "GraphTraversalPlan",
    "GraphTraverseInput",
    "HydratedEvidence",
    "InstructionPayloadFlag",
    "RejectedGraphNeighbor",
    "RejectionReason",
    "ResolvedAnchorSet",
    "ResolvedGraphAnchor",
    "RetrievalLane",
    "SupersessionCandidate",
    "SupportTarget",
    "compute_manifest_hash",
]
