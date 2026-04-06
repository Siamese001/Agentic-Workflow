"""Graph Knowledge Store.

SQLite-based implementation of the knowledge graph store
with FTS5 search and graph traversal capabilities.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from agentic_core.L4_state.types.graph_store_types import (
    GraphCommunity,
    GraphEntity,
    GraphPath,
    GraphRelationship,
    GraphSubgraph,
    IGraphStore,
)

Logger = logging.getLogger(__name__)


class SQLiteGraphStore(IGraphStore):
    """SQLite-based implementation of IGraphStore.

    Uses ADG SQLite database as the underlying graph store.
    Maps ADG nodes/edges to GraphEntity/GraphRelationship.
    """

    def __init__(self, db_path: str | Path) -> None:
        """Initialize the graph store.

        Args:
            db_path: Path to the ADG SQLite database.
        """
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create a database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> SQLiteGraphStore:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def _row_to_entity(self, row: sqlite3.Row) -> GraphEntity:
        """Convert ADG node row to GraphEntity."""
        return GraphEntity(
            id=str(row["id"]),
            name=row["adg_name"] or "",
            entity_type=row["entity_type"] or "unknown",
            description="",  # ADG doesn't have description
            confidence=self._parse_confidence(row["confidence"]),
            metadata={
                "layer": row["layer"] or "",
                "file_path": row["resolved_path"] or "",
                "identity_kind": row["identity_kind"] or "",
                "precision_type": row["precision_type"] or "",
                "type_surface": row["type_surface"] or "",
                "enclosing_symbol": row["enclosing_symbol"] or "",
            },
        )

    def _parse_confidence(self, confidence: str | None) -> float:
        """Parse ADG confidence string to float."""
        if confidence is None:
            return 1.0
        confidence_map = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 0.25}
        return confidence_map.get(confidence, 0.5)

    def add_entity(self, entity: GraphEntity) -> None:
        """Add an entity to the graph store.

        Note: ADG is read-only. This method is provided for interface
        compatibility but will raise NotImplementedError.
        """
        raise NotImplementedError(
            "ADG SQLite database is read-only. Cannot add entities."
        )

    def get_entity(self, entity_id: str) -> GraphEntity | None:
        """Get an entity by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nodes WHERE id = ?", (int(entity_id),))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entity(row)

    def search_entities(self, query: str, limit: int = 10) -> list[GraphEntity]:
        """Search for entities.

        Uses LIKE query on adg_name and resolved_path columns.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        pattern = f"%{query}%"
        cursor.execute(
            """
            SELECT * FROM nodes
            WHERE adg_name LIKE ? OR resolved_path LIKE ?
            LIMIT ?
            """,
            (pattern, pattern, limit),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def _row_to_relationship(self, row: sqlite3.Row) -> GraphRelationship:
        """Convert ADG edge row to GraphRelationship."""
        return GraphRelationship(
            source_id=str(row["src_id"]),
            target_id=str(row["dst_id"]),
            relation_type=row["relation_type"] or "unknown",
            edge_kind=row["edge_kind"] or "",
            confidence=float(row["confidence_score"] or 1.0),
            metadata={
                "source_file": row["source_file"] or "",
                "line_no": int(row["line_no"] or 0),
                "symbol": row["symbol"] or "",
                "semantic_type": row["semantic_type"] or "",
            },
        )

    def get_relationships(
        self, entity_id: str, direction: str = "both"
    ) -> list[GraphRelationship]:
        """Get relationships for an entity.

        Args:
            entity_id: The ID of the entity.
            direction: "outgoing", "incoming", or "both" (default: "both").

        Returns:
            List of relationships connected to the entity.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if direction == "outgoing":
            cursor.execute(
                "SELECT * FROM edges WHERE src_id = ?",
                (int(entity_id),),
            )
        elif direction == "incoming":
            cursor.execute(
                "SELECT * FROM edges WHERE dst_id = ?",
                (int(entity_id),),
            )
        else:  # both
            cursor.execute(
                "SELECT * FROM edges WHERE src_id = ? OR dst_id = ?",
                (int(entity_id), int(entity_id)),
            )

        return [self._row_to_relationship(row) for row in cursor.fetchall()]


__all__ = ["SQLiteGraphStore"]
