"""ADG Integration Wiring for GraphRAG - PRODUCTION IMPLEMENTATION.

Provides the integration layer between:
- ADG (Agentic Directed Graph) static edges (SQLite backend)
- GraphRAG retrieval and indexing
- ParentChildIndex (L4E) registry

Implements:
- ADG edge query interface against real SQLite database
- pulls_context edge resolution
- reads_from/writes_to edge binding
- Graph topology queries (fan-in, fan-out, impact analysis)
- Layer violation detection

Usage:
    from agentic_core.L3_orchestration.reasoning.engines.adg_integration import ADGQueryClient

    client = ADGQueryClient()
    nodes = client.get_nodes_for_file("agentic_core/L3_orchestration/engines/dag_manager.py")
    fanout = client.get_fanout_edges(node_id=12345, relation_type="calls")
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)

# Default ADG SQLite path - uses most recent indexed ADG
DEFAULT_ADG_PATH = Path("artifacts/adg/adg_indexed_03292026_1406.sqlite")


@dataclass(frozen=True)
class ADGNode:
    """ADG node representation from SQLite nodes table."""

    node_id: str
    entity_type: str
    layer: str
    file_path: str
    symbol_name: str
    confidence: float = 1.0
    precision_type: str | None = None
    type_surface: str | None = None
    enclosing_symbol: str | None = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> ADGNode:
        """Create ADGNode from SQLite row."""
        # Confidence is a string enum: 'HIGH', 'MEDIUM', 'LOW'
        confidence_map = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 0.25}
        conf_str = row["confidence"] or "HIGH"
        confidence = confidence_map.get(conf_str, 0.5)

        return cls(
            node_id=str(row["id"]),
            entity_type=row["entity_type"] or "unknown",
            layer=row["layer"] or "unknown",
            file_path=row["resolved_path"] or "",
            symbol_name=row["adg_name"] or "",
            confidence=confidence,
            precision_type=row["precision_type"],
            type_surface=row["type_surface"],
            enclosing_symbol=row["enclosing_symbol"],
        )


@dataclass(frozen=True)
class ADGEdge:
    """ADG edge representation from SQLite edges table."""

    edge_id: str
    src_id: str
    dst_id: str
    relation_type: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str
    semantic_type: str | None = None
    confidence_score: float = 1.0

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> ADGEdge:
        """Create ADGEdge from SQLite row."""
        return cls(
            edge_id=str(row["id"]),
            src_id=str(row["src_id"]),
            dst_id=str(row["dst_id"]),
            relation_type=row["relation_type"] or "unknown",
            edge_kind=row["edge_kind"] or "unknown",
            source_file=row["source_file"] or "",
            line_no=row["line_no"] or 0,
            symbol=row["symbol"] or "",
            semantic_type=row["semantic_type"],
            confidence_score=float(row["confidence_score"]) if row["confidence_score"] else 1.0,
        )


@dataclass
class ImpactAnalysisResult:
    """Result of impact analysis query."""

    root_node_id: str
    root_symbol: str
    affected_nodes: list[ADGNode]
    affected_edges: list[ADGEdge]
    max_depth: int
    total_paths: int


@dataclass
class FanAnalysisResult:
    """Result of fan-in or fan-out analysis."""

    node_id: str
    symbol_name: str
    relation_type: str
    edges: list[ADGEdge]
    total_count: int
    unique_targets: list[str]


@dataclass
class LayerViolation:
    """Represents a layer boundary violation."""

    violation_type: str  # 'gravity_violation', 'boundary_crossing', etc.
    source_layer: str
    target_layer: str
    source_file: str
    line_no: int
    symbol: str
    evidence: str


class ADGQueryClient:
    """Production client for querying ADG graph from SQLite.

    Provides interface to:
    - Query nodes by file, layer, or entity type
    - Query edges by relation type
    - Resolve pulls_context edges
    - Get graph topology (fan-in, fan-out, impact)
    - Detect layer violations
    """

    def __init__(self, adg_db_path: str | Path | None = None):
        """Initialize ADG query client.

        Args:
            adg_db_path: Path to ADG SQLite database. If None, uses default.
        """
        self.adg_db_path = Path(adg_db_path) if adg_db_path else DEFAULT_ADG_PATH
        self._cache: dict[str, Any] = {}
        self._connection: sqlite3.Connection | None = None

        if not self.adg_db_path.exists():
            Logger.warning(f"ADG database not found at {self.adg_db_path}")
            # Try to find most recent ADG
            self._discover_adg_path()

    def _discover_adg_path(self) -> None:
        """Auto-discover most recent ADG SQLite file."""
        adg_dir = Path("artifacts/adg")
        if adg_dir.exists():
            sqlite_files = sorted(
                adg_dir.glob("adg_indexed_*.sqlite"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if sqlite_files:
                self.adg_db_path = sqlite_files[0]
                Logger.info(f"Auto-discovered ADG: {self.adg_db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create SQLite connection with row factory."""
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(self.adg_db_path)
                self._connection.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                raise ConnectionError(f"Failed to connect to ADG database {self.adg_db_path}: {e}") from e
        return self._connection

    def __enter__(self) -> ADGQueryClient:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - ensure connection closes."""
        self.close()
        return None

    def get_nodes_for_file(self, file_path: str) -> list[ADGNode]:
        """Get ADG nodes for a specific file.

        Args:
            file_path: Source file path (relative to repo root)

        Returns:
            List of ADG nodes defined in the file
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Try exact match first, then partial match
        cursor.execute(
            """SELECT * FROM nodes
               WHERE resolved_path = ? OR resolved_path LIKE ?""",
            (file_path, f"%{file_path}"),
        )

        rows = cursor.fetchall()
        nodes = [ADGNode.from_row(row) for row in rows]

        Logger.debug(f"Found {len(nodes)} nodes for file: {file_path}")
        return nodes

    def get_node_by_symbol(self, symbol_name: str) -> ADGNode | None:
        """Get ADG node by its symbol name.

        Args:
            symbol_name: Full ADG name (e.g., "module.submodule.function")

        Returns:
            ADGNode if found, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM nodes WHERE adg_name = ?",
            (symbol_name,),
        )

        row = cursor.fetchone()
        return ADGNode.from_row(row) if row else None

    def get_edges_for_node(
        self,
        node_id: str,
        relation_type: str | None = None,
        direction: str = "out",
    ) -> list[ADGEdge]:
        """Get edges for a specific node.

        Args:
            node_id: Source node ID (as string)
            relation_type: Optional filter by relation type (e.g., 'calls', 'imports')
            direction: 'out' for outgoing, 'in' for incoming, 'both' for both

        Returns:
            List of ADG edges

        Raises:
            ValueError: If direction is not 'out', 'in', or 'both'
        """
        if direction not in ("out", "in", "both"):
            raise ValueError(f"Invalid direction: {direction}. Must be 'out', 'in', or 'both'")

        conn = self._get_connection()
        cursor = conn.cursor()

        node_id_int = int(node_id)

        if direction == "out":
            if relation_type:
                cursor.execute(
                    """SELECT * FROM edges
                       WHERE src_id = ? AND relation_type = ?""",
                    (node_id_int, relation_type),
                )
            else:
                cursor.execute(
                    "SELECT * FROM edges WHERE src_id = ?",
                    (node_id_int,),
                )
        elif direction == "in":
            if relation_type:
                cursor.execute(
                    """SELECT * FROM edges
                       WHERE dst_id = ? AND relation_type = ?""",
                    (node_id_int, relation_type),
                )
            else:
                cursor.execute(
                    "SELECT * FROM edges WHERE dst_id = ?",
                    (node_id_int,),
                )
        else:  # both
            if relation_type:
                cursor.execute(
                    """SELECT * FROM edges
                       WHERE (src_id = ? OR dst_id = ?) AND relation_type = ?""",
                    (node_id_int, node_id_int, relation_type),
                )
            else:
                cursor.execute(
                    """SELECT * FROM edges
                       WHERE src_id = ? OR dst_id = ?""",
                    (node_id_int, node_id_int),
                )

        rows = cursor.fetchall()
        edges = [ADGEdge.from_row(row) for row in rows]

        return edges

    def get_fanout_edges(
        self,
        node_id: str,
        relation_type: str | None = None,
        limit: int = 100,
    ) -> FanAnalysisResult:
        """Get outgoing edges (fan-out) for a node.

        Args:
            node_id: Source node ID
            relation_type: Optional relation filter
            limit: Maximum edges to return

        Returns:
            FanAnalysisResult with edges and metadata
        """
        edges = self.get_edges_for_node(node_id, relation_type, direction="out")

        # Get node symbol name
        node = self._get_node_info(node_id)

        unique_targets = list(set(e.dst_id for e in edges))

        return FanAnalysisResult(
            node_id=node_id,
            symbol_name=node.symbol_name if node else "",
            relation_type=relation_type or "all",
            edges=edges[:limit],
            total_count=len(edges),
            unique_targets=unique_targets[:limit],
        )

    def get_fanin_edges(
        self,
        node_id: str,
        relation_type: str | None = None,
        limit: int = 100,
    ) -> FanAnalysisResult:
        """Get incoming edges (fan-in) for a node.

        Args:
            node_id: Target node ID
            relation_type: Optional relation filter
            limit: Maximum edges to return

        Returns:
            FanAnalysisResult with edges and metadata
        """
        edges = self.get_edges_for_node(node_id, relation_type, direction="in")

        node = self._get_node_info(node_id)
        unique_sources = list(set(e.src_id for e in edges))

        return FanAnalysisResult(
            node_id=node_id,
            symbol_name=node.symbol_name if node else "",
            relation_type=relation_type or "all",
            edges=edges[:limit],
            total_count=len(edges),
            unique_targets=unique_sources[:limit],
        )

    def _get_node_info(self, node_id: str) -> ADGNode | None:
        """Get node info by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM nodes WHERE id = ?", (int(node_id),))
        row = cursor.fetchone()

        return ADGNode.from_row(row) if row else None

    def analyze_impact(
        self,
        root_node_id: str,
        max_depth: int = 3,
        relation_types: list[str] | None = None,
    ) -> ImpactAnalysisResult:
        """Analyze impact of a node - what depends on it (transitive fan-in).

        Args:
            root_node_id: Starting node ID
            max_depth: Maximum traversal depth (must be >= 1)
            relation_types: Optional list of relation types to follow

        Returns:
            ImpactAnalysisResult with affected nodes and paths

        Raises:
            ValueError: If max_depth < 1
        """
        if max_depth < 1:
            raise ValueError(f"max_depth must be >= 1, got {max_depth}")

        conn = self._get_connection()

        visited: set[str] = set()
        affected_nodes: list[ADGNode] = []
        affected_edges: list[ADGEdge] = []
        total_paths = 0

        # BFS traversal
        current_level: list[str] = [root_node_id]

        for depth in range(max_depth):
            next_level: list[str] = []

            for node_id in current_level:
                if node_id in visited:
                    continue
                visited.add(node_id)

                # Get node info
                node = self._get_node_info(node_id)
                if node:
                    affected_nodes.append(node)

                # Get outgoing edges (what this node affects)
                edges = self.get_edges_for_node(
                    node_id,
                    relation_type=None,
                    direction="out",
                )

                if relation_types:
                    edges = [e for e in edges if e.relation_type in relation_types]

                affected_edges.extend(edges)
                total_paths += len(edges)

                # Queue target nodes for next level
                for edge in edges:
                    if edge.dst_id not in visited:
                        next_level.append(edge.dst_id)

            current_level = next_level
            if not current_level:
                break

        root_node = self._get_node_info(root_node_id)

        return ImpactAnalysisResult(
            root_node_id=root_node_id,
            root_symbol=root_node.symbol_name if root_node else "",
            affected_nodes=affected_nodes,
            affected_edges=affected_edges,
            max_depth=depth + 1,
            total_paths=total_paths,
        )

    def detect_layer_violations(
        self,
        file_path: str | None = None,
    ) -> list[LayerViolation]:
        """Detect layer boundary violations.

        Args:
            file_path: Optional file to check. If None, checks all.

        Returns:
            List of layer violations found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        violations: list[LayerViolation] = []

        # Query for edges where src layer > dst layer (gravity violation)
        # L0 < L1 < L2 < L3 < L4 < L5 < L6
        layer_order = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]

        query = """
            SELECT e.*, src.layer as src_layer, dst.layer as dst_layer,
                   src.adg_name as src_name, dst.adg_name as dst_name
            FROM edges e
            JOIN nodes src ON e.src_id = src.id
            JOIN nodes dst ON e.dst_id = dst.id
            WHERE src.layer != 'unknown' AND dst.layer != 'unknown'
        """

        if file_path:
            query += " AND e.source_file LIKE ?"
            cursor.execute(query, (f"%{file_path}%",))
        else:
            cursor.execute(query)

        rows = cursor.fetchall()

        for row in rows:
            src_layer = row["src_layer"]
            dst_layer = row["dst_layer"]

            if src_layer not in layer_order or dst_layer not in layer_order:
                continue

            src_idx = layer_order.index(src_layer)
            dst_idx = layer_order.index(dst_layer)

            # Gravity rule: src layer must be <= dst layer
            if src_idx > dst_idx:
                violations.append(
                    LayerViolation(
                        violation_type="gravity_violation",
                        source_layer=src_layer,
                        target_layer=dst_layer,
                        source_file=row["source_file"] or "",
                        line_no=row["line_no"] or 0,
                        symbol=row["symbol"] or "",
                        evidence=f"{src_layer} (higher) imports from {dst_layer} (lower)",
                    )
                )

        return violations

    def resolve_pulls_context(
        self,
        chunk_id: str,
        context_sources: list[str],
    ) -> list[dict[str, Any]]:
        """Resolve pulls_context edges for a chunk.

        Args:
            chunk_id: Chunk identifier
            context_sources: List of context source identifiers (symbols)

        Returns:
            List of resolved context edges with metadata
        """
        _trace_id = f"pulls_context_{chunk_id}"
        _emit_records_execution_trace(_trace_id, "L4_STATE", "ADGQueryClient.resolve_pulls_context")

        resolved = []
        for source in context_sources:
            # Check if source exists in ADG
            node = self.get_node_by_symbol(source)

            _emit_pulls_context(_trace_id, chunk_id, source)
            resolved.append(
                {
                    "chunk_id": chunk_id,
                    "source": source,
                    "relation": "pulls_context",
                    "confidence": 1.0 if node else 0.5,
                    "adg_node_id": node.node_id if node else None,
                    "found_in_adg": node is not None,
                }
            )

        return resolved

    def get_graph_topology(
        self,
        edge_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get overall graph topology statistics.

        Args:
            edge_types: Optional list of edge types to filter

        Returns:
            Graph topology statistics from actual ADG
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get counts by relation type
        if edge_types:
            placeholders = ", ".join("?" * len(edge_types))
            cursor.execute(
                f"""SELECT relation_type, COUNT(*) as count
                    FROM edges
                    WHERE relation_type IN ({placeholders})
                    GROUP BY relation_type""",
                edge_types,
            )
        else:
            cursor.execute(
                """SELECT relation_type, COUNT(*) as count
                   FROM edges
                   GROUP BY relation_type
                   ORDER BY count DESC
                   LIMIT 20"""
            )

        relation_counts = {row["relation_type"]: row["count"] for row in cursor.fetchall()}

        # Get total counts
        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]

        # Get layer distribution
        cursor.execute(
            """SELECT layer, COUNT(*) as count
               FROM nodes
               WHERE layer != 'unknown'
               GROUP BY layer
               ORDER BY layer"""
        )
        layer_distribution = {row["layer"]: row["count"] for row in cursor.fetchall()}

        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "relation_type_counts": relation_counts,
            "layer_distribution": layer_distribution,
            "adg_db_path": str(self.adg_db_path),
        }

    def close(self) -> None:
        """Close database connection. Idempotent - safe to call multiple times."""
        if self._connection:
            try:
                self._connection.close()
            except sqlite3.Error:
                # Connection may already be closed
                pass
            finally:
                self._connection = None


class GraphRAGADGIntegration:
    """Integration layer between GraphRAG and ADG.

    Provides:
    - ADG edge binding during ingestion
    - ADG edge hydration during retrieval
    - pulls_context resolution
    - Graph topology awareness
    """

    def __init__(
        self,
        adg_client: ADGQueryClient | None = None,
    ):
        """Initialize GraphRAG-ADG integration.

        Args:
            adg_client: ADG query client
        """
        self.adg_client = adg_client or ADGQueryClient()

    def bind_edges_for_ingestion(
        self,
        doc_id: str,
        source_path: str,
        chunks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Bind ADG edges during document ingestion.

        Args:
            doc_id: Document identifier
            source_path: Source file path
            chunks: Document chunks

        Returns:
            Edge binding results with reads_from, writes_to, pulls_context
        """
        # Get ADG nodes for this file
        nodes = self.adg_client.get_nodes_for_file(source_path)

        # Extract entity names for binding
        entity_names = [node.symbol_name for node in nodes]

        # Query actual edges for these nodes
        reads_from = []
        writes_to = []

        for node in nodes:
            edges = self.adg_client.get_edges_for_node(node.node_id, direction="out")
            for edge in edges:
                if edge.relation_type in ("reads_from", "imports", "calls"):
                    reads_from.append(edge.symbol)
                elif edge.relation_type in ("writes_to", "exports"):
                    writes_to.append(edge.symbol)

        # Create edge binding
        binding = {
            "doc_id": doc_id,
            "source_path": source_path,
            "adg_nodes": [n.node_id for n in nodes],
            "adg_node_count": len(nodes),
            "reads_from": list(set(reads_from))[:20],  # Limit to top 20
            "writes_to": list(set(writes_to))[:20],
            "pulls_context": entity_names[:10] if len(entity_names) > 10 else entity_names,
        }

        return binding

    def hydrate_edges_for_retrieval(
        self,
        chunk_id: str,
        source_path: str,
    ) -> dict[str, Any]:
        """Hydrate ADG edges during chunk retrieval.

        Args:
            chunk_id: Chunk identifier
            source_path: Source file path

        Returns:
            Hydrated edge data from real ADG
        """
        # Get nodes for the source file
        nodes = self.adg_client.get_nodes_for_file(source_path)

        # Get edges for these nodes
        edges = []
        for node in nodes:
            node_edges = self.adg_client.get_edges_for_node(node.node_id)
            edges.extend(node_edges)

        # Resolve pulls_context edges
        context_sources = [n.symbol_name for n in nodes]
        pulls_context = self.adg_client.resolve_pulls_context(chunk_id, context_sources)

        return {
            "chunk_id": chunk_id,
            "adg_nodes": len(nodes),
            "adg_edges": len(edges),
            "pulls_context": pulls_context,
            "reads_from": [e.symbol for e in edges if e.relation_type in ("reads_from", "imports")],
            "writes_to": [e.symbol for e in edges if e.relation_type == "writes_to"],
            "calls": [e.symbol for e in edges if e.relation_type == "calls"],
        }

    def analyze_impact_for_change(
        self,
        file_path: str,
        max_depth: int = 3,
    ) -> dict[str, Any]:
        """Analyze impact of changing a file - accelerator query #1.

        Args:
            file_path: File to analyze
            max_depth: Maximum traversal depth

        Returns:
            Impact analysis with affected files and symbols
        """
        nodes = self.adg_client.get_nodes_for_file(file_path)

        all_affected: set[str] = set()
        all_edges: list[dict] = []

        for node in nodes:
            impact = self.adg_client.analyze_impact(
                node.node_id,
                max_depth=max_depth,
                relation_types=["calls", "imports", "reads_from"],
            )

            for affected in impact.affected_nodes:
                all_affected.add(affected.file_path)

            all_edges.extend(
                [
                    {
                        "src": e.src_id,
                        "dst": e.dst_id,
                        "relation": e.relation_type,
                        "symbol": e.symbol,
                    }
                    for e in impact.affected_edges
                ]
            )

        return {
            "source_file": file_path,
            "entry_points": [n.symbol_name for n in nodes],
            "affected_files": sorted(all_affected),
            "affected_file_count": len(all_affected),
            "traversal_depth": max_depth,
            "total_edges": len(all_edges),
        }

    def get_fan_analysis(
        self,
        symbol_name: str,
    ) -> dict[str, Any]:
        """Get fan-in and fan-out analysis - accelerator query #2.

        Args:
            symbol_name: Symbol to analyze (e.g., "dag_manager.DAGManager")

        Returns:
            Fan-in and fan-out statistics
        """
        node = self.adg_client.get_node_by_symbol(symbol_name)

        if not node:
            return {
                "symbol": symbol_name,
                "found": False,
                "error": "Symbol not found in ADG",
            }

        fanout = self.adg_client.get_fanout_edges(node.node_id, limit=50)
        fanin = self.adg_client.get_fanin_edges(node.node_id, limit=50)

        return {
            "symbol": symbol_name,
            "node_id": node.node_id,
            "found": True,
            "layer": node.layer,
            "file": node.file_path,
            "fan_out": {
                "total_edges": fanout.total_count,
                "unique_targets": len(fanout.unique_targets),
                "top_relations": fanout.edges[:10],
            },
            "fan_in": {
                "total_edges": fanin.total_count,
                "unique_callers": len(fanin.unique_targets),
                "top_relations": fanin.edges[:10],
            },
        }

    def get_layer_violations(
        self,
        file_path: str | None = None,
    ) -> dict[str, Any]:
        """Get layer violations - accelerator query #3.

        Args:
            file_path: Optional file to check. If None, checks all.

        Returns:
            Layer violation report
        """
        violations = self.adg_client.detect_layer_violations(file_path)

        return {
            "scope": file_path or "entire_repo",
            "violation_count": len(violations),
            "violations": [
                {
                    "type": v.violation_type,
                    "source_layer": v.source_layer,
                    "target_layer": v.target_layer,
                    "file": v.source_file,
                    "line": v.line_no,
                    "symbol": v.symbol,
                    "evidence": v.evidence,
                }
                for v in violations
            ],
        }


# Global instance
_global_adg_integration: GraphRAGADGIntegration | None = None
_global_adg_client: ADGQueryClient | None = None


def get_global_adg_client() -> ADGQueryClient:
    """Get or create global ADG client."""
    global _global_adg_client
    if _global_adg_client is None:
        _global_adg_client = ADGQueryClient()
    return _global_adg_client


def get_global_adg_integration() -> GraphRAGADGIntegration:
    """Get or create global ADG integration."""
    global _global_adg_integration
    if _global_adg_integration is None:
        _global_adg_integration = GraphRAGADGIntegration(adg_client=get_global_adg_client())
    return _global_adg_integration


__all__ = [
    "ADGNode",
    "ADGEdge",
    "ADGQueryClient",
    "GraphRAGADGIntegration",
    "ImpactAnalysisResult",
    "FanAnalysisResult",
    "LayerViolation",
    "get_global_adg_client",
    "get_global_adg_integration",
]
