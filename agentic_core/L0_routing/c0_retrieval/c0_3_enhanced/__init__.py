"""C0.3 GRAPH TRAVERSE — enhanced runtime per
``docs/reference/03_L0_Routing/C0 - Context Engine/C0.3_Graph_RAG_detailed.md``.

This subpackage implements the WINDSURF IMPLEMENTATION CONTRACT for C0.3 as a
read-only, bounded graph expansion stage that:

* receives hydrated candidates,
* resolves anchors against a graph adapter,
* walks the projection within a deterministic plan,
* applies 15 gates (ACL, tenant, region, data class, freshness, relation
  allowlist, source class, hop budget, support relevance, confidence,
  lineage, citation, contradiction-preserve, cycle, projection currency),
* preserves contradictions and supersession candidates,
* quarantines instruction-like payloads,
* emits a deterministic ``GraphTraversalManifest``,
* and never opens a SQLite connection in the runtime path.

The legacy ``graph_traverse.expand_graph`` implementation is preserved for
back-compat; this package is the enhanced surface used by the new spec.
"""

from __future__ import annotations

from .contracts import (
    AclStatus,
    AcceptedGraphNeighbor,
    AnchorCandidate,
    AnchorCandidateSet,
    AnchorType,
    ContradictionCandidate,
    ContradictionType,
    FreshnessClass,
    FreshnessStatus,
    GapFinding,
    GapType,
    GraphBudget,
    GraphExpandedEvidencePool,
    GraphRelationType,
    GraphTraversalManifest,
    GraphTraversalPlan,
    GraphTraverseInput,
    HydratedEvidence,
    InstructionPayloadFlag,
    RejectedGraphNeighbor,
    RejectionReason,
    ResolvedAnchorSet,
    ResolvedGraphAnchor,
    RetrievalLane,
    SupersessionCandidate,
    SupportTarget,
    compute_manifest_hash,
)
from .adapter import (
    GraphAdapterHealth,
    GraphNeighbor,
    GraphRelationPath,
    GraphTraversalAdapter,
    InMemoryGraphAdapter,
    ProjectionManifest,
)
from .gates import (
    GATE_FUNCTIONS,
    GateDecision,
    GateName,
    apply_all_gates,
)
from .pipeline import run_graph_traverse
from .plan import build_traversal_plan
from .security import detect_instruction_payload, quarantine_neighbor_payload
from .substrate import (
    SubstrateViolation,
    assert_no_direct_sqlite_traversal,
    sqlite_substrate_guard,
)
from .otel import C0GraphSpan, GraphSpanRecorder, NullSpanRecorder

__all__ = [
    "AcceptedGraphNeighbor",
    "AnchorCandidateSet",
    "AnchorType",
    "ContradictionCandidate",
    "ContradictionType",
    "GapFinding",
    "GapType",
    "GraphExpandedEvidencePool",
    "GraphTraversalManifest",
    "GraphTraversalPlan",
    "GraphTraverseInput",
    "HydratedEvidence",
    "InstructionPayloadFlag",
    "RejectedGraphNeighbor",
    "RejectionReason",
    "ResolvedGraphAnchor",
    "SupersessionCandidate",
    "compute_manifest_hash",
    "GraphAdapterHealth",
    "GraphNeighbor",
    "GraphRelationPath",
    "GraphTraversalAdapter",
    "InMemoryGraphAdapter",
    "ProjectionManifest",
    "GATE_FUNCTIONS",
    "GateDecision",
    "GateName",
    "apply_all_gates",
    "run_graph_traverse",
    "build_traversal_plan",
    "detect_instruction_payload",
    "quarantine_neighbor_payload",
    "SubstrateViolation",
    "assert_no_direct_sqlite_traversal",
    "sqlite_substrate_guard",
    "C0GraphSpan",
    "GraphSpanRecorder",
    "NullSpanRecorder",
]
