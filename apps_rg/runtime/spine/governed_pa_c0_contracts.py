"""apps_rg-owned C0 prompt-assembly bridge contracts.

These are the narrow data shapes needed by ``governed_pa_compose`` when it
builds inputs for prompt governance. They preserve the attribute surface read by
``agentic_core.prompt_governance.assemble_prompt`` without importing concrete
L0/C0 retrieval internals from apps_rg.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class FreshnessClass(str, Enum):
    STATIC = "static"
    SLOW = "slow"
    CURRENT = "current"
    LATEST = "latest"


class SupportTarget(str, Enum):
    EXACT_QUOTE = "EXACT_QUOTE"
    SOURCE_SUMMARY = "SOURCE_SUMMARY"
    POLICY_CLAUSE = "POLICY_CLAUSE"
    CODE_LOCATION = "CODE_LOCATION"
    INCIDENT_EVIDENCE = "INCIDENT_EVIDENCE"
    ROOT_CAUSE_RANKING = "ROOT_CAUSE_RANKING"
    COMPARISON = "COMPARISON"
    CLAIM_CHECK = "CLAIM_CHECK"


class SourceClass(str, Enum):
    DOCS = "docs"
    CODE = "code"
    LOGS = "logs"
    TICKETS = "tickets"
    TABLES = "tables"
    POLICY = "policy"
    PRIOR_ARTIFACTS = "prior_artifacts"


class RetrievalLane(str, Enum):
    DENSE = "dense"
    SPARSE = "sparse"
    METADATA = "metadata"
    GRAPH_SEED = "graph_seed"
    CACHE = "cache"
    TRACE = "trace"
    CODE = "code"


class SupportStatus(str, Enum):
    PASS = "PASS"
    WEAK = "WEAK"
    WEAK_WITH_CAVEATS = "WEAK_WITH_CAVEATS"
    CONFLICTED = "CONFLICTED"
    EMPTY = "EMPTY"
    BLOCKED = "BLOCKED"


class ChunkBoundaryRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class HydrationManifest:
    source_id: str
    file_path: str = ""
    section: str = ""
    line_range: tuple[int, int] = (0, 0)

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("HydrationManifest.source_id required")
        a, b = self.line_range
        if a < 0 or b < 0 or b < a:
            raise ValueError(f"invalid line_range {self.line_range}")


@dataclass(frozen=True)
class CandidateChunk:
    chunk_id: str
    source_class: SourceClass
    text: str
    manifest: HydrationManifest
    found_by_lanes: tuple[RetrievalLane, ...] = ()

    def __post_init__(self) -> None:
        if not self.chunk_id.strip():
            raise ValueError("CandidateChunk.chunk_id required")
        if self.text == "":
            raise ValueError("CandidateChunk.text must not be empty")
        if not self.found_by_lanes:
            raise ValueError(f"CandidateChunk {self.chunk_id!r} missing lane provenance")


@dataclass(frozen=True)
class QualityFlags:
    span_resolves: bool
    source_version_current: bool
    acl_clear: bool
    parent_context_available: bool
    citation_anchor_stable: bool
    chunk_boundary_risk: ChunkBoundaryRisk = ChunkBoundaryRisk.LOW


@dataclass(frozen=True)
class HydratedChunk:
    candidate: CandidateChunk
    canonical_source_path: str
    section_hierarchy: tuple[str, ...]
    chunk_version: str
    citation_anchor_candidates: tuple[str, ...]
    quality: QualityFlags

    def __post_init__(self) -> None:
        if not self.canonical_source_path.strip():
            raise ValueError("canonical_source_path required")
        if not self.chunk_version.strip():
            raise ValueError("chunk_version required")


@dataclass(frozen=True)
class FinalEvidenceContract:
    contract_id: str
    route_id: str
    route_replay_key: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    status: SupportStatus = SupportStatus.EMPTY
    support_score: float = 0.0
    must_use: tuple[HydratedChunk, ...] = ()
    supporting: tuple[HydratedChunk, ...] = ()
    lineage: tuple[object, ...] = ()
    blocked_reason: str = ""

    def __post_init__(self) -> None:
        if not (0.0 <= self.support_score <= 1.0):
            raise ValueError(f"support_score={self.support_score} must be in [0,1]")
        if not isinstance(self.status, SupportStatus):
            raise TypeError("status must be SupportStatus")


@dataclass(frozen=True)
class RouteContract:
    route_id: str
    grounding_required: bool
    execution_form: str
    freshness_class: FreshnessClass
    support_target: SupportTarget
    tenant_scope: str
    route_replay_key: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    hmac_sig: str = ""
    app_id: str = ""
    task_class: str = ""
    l5_certification_ref: str = ""

    def __post_init__(self) -> None:
        if self.execution_form not in ("SINGLE_STEP", "MANAGED_WORKFLOW_STEP"):
            raise ValueError(f"invalid execution_form: {self.execution_form}")


@dataclass(frozen=True)
class L1PlanContract:
    task_spec: str
    query_spec: str
    grounding_required: bool = True
    user_task_text: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.task_spec, str):
            raise TypeError("task_spec must be str")
        if not isinstance(self.query_spec, str):
            raise TypeError("query_spec must be str")


__all__ = [
    "CandidateChunk",
    "ChunkBoundaryRisk",
    "FinalEvidenceContract",
    "FreshnessClass",
    "HydratedChunk",
    "HydrationManifest",
    "L1PlanContract",
    "QualityFlags",
    "RetrievalLane",
    "RouteContract",
    "SourceClass",
    "SupportStatus",
    "SupportTarget",
]
