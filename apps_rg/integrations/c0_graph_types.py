"""apps_rg-owned graph adapter protocol and value objects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol, runtime_checkable


class AclStatus(str, Enum):
    ALLOWED = "allowed"
    CLEARED = "cleared"
    DENIED = "denied"
    UNKNOWN = "unknown"


class FreshnessStatus(str, Enum):
    FRESH = "fresh"
    CURRENT = "current"
    STALE = "stale"
    HISTORICAL = "historical"
    UNKNOWN = "unknown"


class AnchorType(str, Enum):
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


@dataclass(frozen=True)
class AnchorCandidate:
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
class ResolvedGraphAnchor:
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


@dataclass(frozen=True)
class GraphNeighbor:
    node_id: str
    node_type: str
    source_id: str
    source_type: str
    source_version: str
    relation_type: str
    relation_path: tuple[str, ...]
    hop_distance: int
    tenant: str | None = None
    region: str | None = None
    data_class: str | None = None
    acl_status: AclStatus | str = AclStatus.UNKNOWN
    freshness_status: FreshnessStatus | str = FreshnessStatus.UNKNOWN
    candidate_text_or_payload: str = ""

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("GraphNeighbor.node_id is required")
        if not self.relation_type:
            raise ValueError("GraphNeighbor.relation_type is required")
        if self.hop_distance < 0:
            raise ValueError("GraphNeighbor.hop_distance must be >= 0")


@dataclass(frozen=True)
class GraphRelationPath:
    start_node_id: str
    end_node_id: str
    relations: tuple[str, ...]
    nodes: tuple[str, ...]


@dataclass(frozen=True)
class ProjectionManifest:
    graph_source: str
    projection_version: str
    snapshot_pointer: str
    snapshot_built_at: str
    canonical_source_hash: str
    is_stale: bool = False
    stale_reason: str = ""


@dataclass(frozen=True)
class GraphAdapterHealth:
    healthy: bool
    backend: str
    latency_p50_ms: float
    latency_p95_ms: float
    last_error: str = ""


@dataclass(frozen=True)
class AmbiguousAnchorResolution:
    candidate: AnchorCandidate
    candidates: tuple[ResolvedGraphAnchor, ...]


@dataclass(frozen=True)
class UnresolvedAnchorResolution:
    candidate: AnchorCandidate
    reason: str


@runtime_checkable
class GraphTraversalAdapter(Protocol):
    def resolve_anchor(
        self,
        anchor_candidate: AnchorCandidate,
        scope: Mapping[str, object],
    ) -> ResolvedGraphAnchor | AmbiguousAnchorResolution | UnresolvedAnchorResolution: ...

    def get_neighbors(
        self,
        node_id: str,
        relation_types: tuple[str, ...],
        scope: Mapping[str, object],
        limit: int,
    ) -> tuple[GraphNeighbor, ...]: ...

    def get_relation_path(
        self,
        start_node_id: str,
        neighbor_node_id: str,
    ) -> GraphRelationPath: ...

    def get_projection_manifest(self) -> ProjectionManifest: ...

    def health_check(self) -> GraphAdapterHealth: ...


__all__ = [
    "AclStatus",
    "AmbiguousAnchorResolution",
    "AnchorCandidate",
    "AnchorType",
    "FreshnessStatus",
    "GraphAdapterHealth",
    "GraphNeighbor",
    "GraphRelationPath",
    "GraphTraversalAdapter",
    "ProjectionManifest",
    "ResolvedGraphAnchor",
    "UnresolvedAnchorResolution",
]
