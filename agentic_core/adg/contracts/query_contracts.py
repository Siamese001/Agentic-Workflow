"""ADG Query Contracts — Structured contracts for graph queries.

Defines dataclasses for:
- Snapshot metadata with lineage verification
- Node and edge representations
- Query results and finding packets

These contracts ensure type-safe, reproducible queries across SQLite and Redis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EntityType(Enum):
    """ADG entity types."""
    MODULE = "module"
    SYMBOL = "symbol"
    CLASS = "class"
    FUNCTION = "function"
    PACKAGE = "package"


class RelationType(Enum):
    """ADG relation types for edges."""
    IMPORTS = "imports"
    EXPORTS = "exports"
    CALLS = "calls"
    READS_FROM = "reads_from"
    WRITES_TO = "writes_to"
    FLOWS_TO = "flows_to"
    CONTROLS_FLOW = "controls_flow"


class EdgeKind(Enum):
    """ADG edge kinds."""
    DIRECT = "direct"
    FROM_IMPORT = "from_import"
    CONDITIONAL = "conditional"


class FindingSeverity(Enum):
    """Severity levels for invariant findings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SnapshotMetadata:
    """Snapshot metadata with lineage verification.

    Attributes:
        snapshot_id: Unique snapshot identifier (e.g., "04022026_2140")
        timestamp: ISO timestamp of snapshot creation
        node_count: Total nodes in snapshot
        edge_count: Total edges in snapshot
        sqlite_path: Path to authoritative SQLite file
        sqlite_digest: SHA256 digest of SQLite file
        redis_digest: SHA256 digest of Redis materialization (if available)
        projection_coherent: Whether Redis matches SQLite
    """
    snapshot_id: str
    timestamp: str
    node_count: int
    edge_count: int
    sqlite_path: str
    sqlite_digest: str
    redis_digest: str | None = None
    projection_coherent: bool = False

    def is_authoritative(self) -> bool:
        """Check if this snapshot has verified coherence."""
        return self.projection_coherent and self.redis_digest == self.sqlite_digest


@dataclass(frozen=True)
class Node:
    """ADG node representation.

    Attributes:
        id: Numeric node ID
        adg_name: Fully qualified ADG name
        entity_type: Type of entity (module, symbol, etc.)
        layer: Architectural layer (L0, L1, L2, L3, L4, L5, L6, L_APP)
        file_path: Source file path (if applicable)
        identity_kind: Kind of identity (repo_module, external_module, etc.)
        confidence: Confidence level (HIGH, MEDIUM, LOW)
    """
    id: int
    adg_name: str
    entity_type: str
    layer: str | None = None
    file_path: str | None = None
    identity_kind: str | None = None
    confidence: str = "HIGH"


@dataclass(frozen=True)
class Edge:
    """ADG edge representation.

    Attributes:
        id: Numeric edge ID
        src_id: Source node ID
        dst_id: Destination node ID
        relation_type: Type of relation (imports, calls, etc.)
        edge_kind: Kind of edge (direct, from_import, etc.)
        symbol: Symbol name for the edge (e.g., module name being imported)
        source_file: File where edge originates
        line_no: Line number in source file
        semantic_type: Semantic classification
        confidence_score: Confidence 0.0-1.0
    """
    id: int
    src_id: int
    dst_id: int
    relation_type: str
    edge_kind: str = "direct"
    symbol: str | None = None
    source_file: str | None = None
    line_no: int | None = None
    semantic_type: str | None = None
    confidence_score: float = 1.0


@dataclass(frozen=True)
class ImportEdge(Edge):
    """Specialized edge for import relations with resolution status."""

    @property
    def is_resolved(self) -> bool:
        """Check if import resolves to a module entity."""
        # Import is unresolved if dst node is not a module
        # This will be checked by the query service
        return False  # Placeholder, actual check in service


@dataclass(frozen=True)
class QueryResult:
    """Generic query result wrapper.

    Attributes:
        success: Whether query succeeded
        data: Query result data
        error: Error message if failed
        snapshot_id: Snapshot used for query
        cache_hit: Whether result came from Redis cache
    """
    success: bool
    data: Any | None = None
    error: str | None = None
    snapshot_id: str | None = None
    cache_hit: bool = False


@dataclass(frozen=True)
class NodeQueryResult(QueryResult):
    """Result for node queries."""
    data: Node | None = None


@dataclass(frozen=True)
class EdgeQueryResult(QueryResult):
    """Result for edge queries."""
    data: list[Edge] = field(default_factory=list)


@dataclass(frozen=True)
class UnresolvedImport:
    """Record of an unresolved import.

    Attributes:
        edge_id: Edge ID
        src_module: Source module ADG name
        src_file: Source file path
        line_no: Line number
        symbol: Symbol being imported
        dst_id: Destination node ID
        dst_entity_type: Actual entity type of destination (usually "symbol")
        reason: Why import is unresolved
    """
    edge_id: int
    src_module: str
    src_file: str
    line_no: int
    symbol: str
    dst_id: int
    dst_entity_type: str
    reason: str = "destination_not_module"


@dataclass
class FindingPacket:
    """Structured finding packet for invariant violations.

    Separates graph facts from policy findings. Reproducible from
    (facts + policy pack).

    Attributes:
        finding_id: Unique finding identifier
        finding_type: Classification (unresolved_import, boundary_violation, etc.)
        severity: Severity level
        scope: Affected scope (module, layer, etc.)
        facts: Graph facts (nodes, edges, entity types)
        policy_pack: Policy applied to derive finding
        description: Human-readable description
        remediation: Suggested remediation
        snapshot_id: Snapshot where finding was detected
    """
    finding_id: str
    finding_type: str
    severity: FindingSeverity
    scope: str
    facts: dict[str, Any] = field(default_factory=dict)
    policy_pack: str = "default"
    description: str = ""
    remediation: str | None = None
    snapshot_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "finding_id": self.finding_id,
            "finding_type": self.finding_type,
            "severity": self.severity.value,
            "scope": self.scope,
            "facts": self.facts,
            "policy_pack": self.policy_pack,
            "description": self.description,
            "remediation": self.remediation,
            "snapshot_id": self.snapshot_id,
        }


@dataclass
class InvariantResult:
    """Result from invariant check run.

    Attributes:
        invariant_name: Name of invariant checked
        passed: Whether invariant passed
        findings: List of finding packets
        checked_count: Number of items checked
        duration_ms: Check duration in milliseconds
        snapshot_id: Snapshot checked
    """
    invariant_name: str
    passed: bool
    findings: list[FindingPacket] = field(default_factory=list)
    checked_count: int = 0
    duration_ms: float = 0.0
    snapshot_id: str | None = None

    @property
    def has_violations(self) -> bool:
        """Check if any HIGH or CRITICAL violations exist."""
        return any(
            f.severity in (FindingSeverity.HIGH, FindingSeverity.CRITICAL)
            for f in self.findings
        )


__all__ = [
    "EntityType",
    "RelationType",
    "EdgeKind",
    "FindingSeverity",
    "SnapshotMetadata",
    "Node",
    "Edge",
    "ImportEdge",
    "QueryResult",
    "NodeQueryResult",
    "EdgeQueryResult",
    "UnresolvedImport",
    "FindingPacket",
    "InvariantResult",
]
