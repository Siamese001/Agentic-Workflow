"""ADG Edge Builder — Graph construction and edge management.

This module provides edge building functionality for the ADG (Agentic Dependency Graph).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Edge:
    """Represents an ADG edge."""

    src_id: int
    dst_id: int
    relation_type: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str = ""


class EdgeBuilder:
    """Builds and manages ADG edges."""

    def __init__(self):
        self.edges: list[Edge] = []

    def add_edge(
        self,
        src_id: int,
        dst_id: int,
        relation_type: str,
        edge_kind: str,
        source_file: str,
        line_no: int,
        symbol: str = "",
    ) -> Edge:
        """Add a new edge to the graph.

        Args:
            src_id: Source node ID
            dst_id: Destination node ID
            relation_type: Type of relation (e.g., 'calls', 'imports')
            edge_kind: Kind of edge (e.g., 'static', 'dynamic')
            source_file: File where the edge originates
            line_no: Line number in source file
            symbol: Symbol name associated with edge

        Returns:
            The created Edge object
        """
        edge = Edge(
            src_id=src_id,
            dst_id=dst_id,
            relation_type=relation_type,
            edge_kind=edge_kind,
            source_file=source_file,
            line_no=line_no,
            symbol=symbol,
        )
        self.edges.append(edge)
        return edge

    def get_edges(self, relation_type: str | None = None) -> list[Edge]:
        """Get edges, optionally filtered by relation type.

        Args:
            relation_type: Optional filter for relation type

        Returns:
            List of matching edges
        """
        if relation_type is None:
            return self.edges.copy()
        return [e for e in self.edges if e.relation_type == relation_type]

    def build_batch(self, edge_data: list[dict[str, Any]]) -> list[Edge]:
        """Build multiple edges from raw data.

        Args:
            edge_data: List of edge data dictionaries

        Returns:
            List of created Edge objects
        """
        created = []
        for data in edge_data:
            edge = self.add_edge(
                src_id=data["src_id"],
                dst_id=data["dst_id"],
                relation_type=data["relation_type"],
                edge_kind=data.get("edge_kind", "static"),
                source_file=data.get("source_file", ""),
                line_no=data.get("line_no", 0),
                symbol=data.get("symbol", ""),
            )
            created.append(edge)
        return created
