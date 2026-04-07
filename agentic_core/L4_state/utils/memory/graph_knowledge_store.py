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
        
        Raises:
            FileNotFoundError: If db_path does not exist or is not a file.
            sqlite3.OperationalError: If database is corrupted or invalid.
        """
        self.db_path = Path(db_path)

        # Validate path exists and is a file
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file does not exist: {self.db_path}")
        if not self.db_path.is_file():
            raise FileNotFoundError(f"Database path is not a file: {self.db_path}")

        self._conn: sqlite3.Connection | None = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create a database connection.
        
        Raises:
            sqlite3.OperationalError: If database is corrupted or invalid.
        """
        if self._conn is None:
            try:
                self._conn = sqlite3.connect(self.db_path)
                self._conn.row_factory = sqlite3.Row
            except sqlite3.OperationalError as e:
                Logger.error("Failed to connect to database at %s: %s", self.db_path, e)
                raise
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
            "ADG SQLite database is read-only. Cannot add entities.",
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
        self, entity_id: str, direction: str = "both",
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

    def get_neighbors(self, entity_id: str, max_hops: int = 1) -> list[GraphEntity]:
        """Get neighboring entities within a specified hop distance.

        Args:
            entity_id: The ID of the entity.
            max_hops: Maximum number of hops (default: 1).

        Returns:
            List of neighboring entities.
        """
        if max_hops == 1:
            # Direct neighbors only
            relationships = self.get_relationships(entity_id, direction="both")
            neighbor_ids = set()
            for rel in relationships:
                neighbor_ids.add(rel.source_id)
                neighbor_ids.add(rel.target_id)
            neighbor_ids.discard(entity_id)  # Remove self

            neighbors = []
            for nid in neighbor_ids:
                entity = self.get_entity(nid)
                if entity is not None:
                    neighbors.append(entity)
            return neighbors
        else:
            # Multi-hop neighbors (BFS)
            visited = {entity_id}
            current_level = {entity_id}
            neighbors = []

            for _ in range(max_hops):
                next_level = set()
                for eid in current_level:
                    rels = self.get_relationships(eid, direction="both")
                    for rel in rels:
                        for nid in (rel.source_id, rel.target_id):
                            if nid not in visited:
                                visited.add(nid)
                                next_level.add(nid)
                                entity = self.get_entity(nid)
                                if entity is not None:
                                    neighbors.append(entity)
                current_level = next_level
                if not current_level:
                    break

            return neighbors

    def traverse(
        self,
        start_id: str,
        max_depth: int = 2,
        relation_types: list[str] | None = None,
    ) -> list[GraphPath]:
        """Traverse the graph from a starting entity.

        Args:
            start_id: The ID of the starting entity.
            max_depth: Maximum traversal depth (default: 2).
            relation_types: Optional list of relation types to filter by.

        Returns:
            List of paths discovered during traversal.
        """
        paths: list[GraphPath] = []
        start_entity = self.get_entity(start_id)

        if start_entity is None:
            return paths

        # BFS traversal
        from collections import deque

        queue: deque[tuple[list[GraphEntity], list[GraphRelationship]]] = deque()
        queue.append(([start_entity], []))
        visited = {start_id}

        while queue and len(paths) < 1000:  # Limit results
            current_nodes, current_rels = queue.popleft()
            current_depth = len(current_nodes) - 1

            if current_depth >= max_depth:
                paths.append(
                    GraphPath(
                        nodes=current_nodes.copy(),
                        relationships=current_rels.copy(),
                        cost=float(current_depth),
                    ),
                )
                continue

            # Get neighbors
            last_node = current_nodes[-1]
            rels = self.get_relationships(last_node.id, direction="outgoing")

            for rel in rels:
                # Filter by relation types if specified
                if relation_types and rel.relation_type not in relation_types:
                    continue

                next_id = rel.target_id
                if next_id in visited:
                    continue

                visited.add(next_id)
                next_entity = self.get_entity(next_id)

                if next_entity is None:
                    continue

                new_nodes = current_nodes + [next_entity]
                new_rels = current_rels + [rel]
                queue.append((new_nodes, new_rels))

        return paths

    def find_shortest_path(self, src_id: str, dst_id: str) -> GraphPath | None:
        """Find the shortest path between two entities.

        Args:
            src_id: The ID of the source entity.
            dst_id: The ID of the destination entity.

        Returns:
            GraphPath representing the shortest path, or None if no path exists.
        """
        if src_id == dst_id:
            # Same node
            entity = self.get_entity(src_id)
            if entity is None:
                return None
            return GraphPath(nodes=[entity], relationships=[], cost=0.0)

        from collections import deque

        queue: deque[tuple[str, list[str], list[GraphRelationship]]] = deque()
        queue.append((src_id, [], []))
        visited = {src_id}

        while queue:
            current_id, path_ids, path_rels = queue.popleft()

            if current_id == dst_id:
                # Reconstruct path
                nodes: list[GraphEntity] = []
                for pid in path_ids + [dst_id]:
                    entity = self.get_entity(pid)
                    if entity is not None:
                        nodes.append(entity)
                return GraphPath(
                    nodes=nodes,
                    relationships=path_rels,
                    cost=float(len(path_rels)),
                )

            # Get neighbors
            rels = self.get_relationships(current_id, direction="outgoing")
            for rel in rels:
                next_id = rel.target_id
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append(
                        (next_id, path_ids + [current_id], path_rels + [rel]),
                    )

        return None  # No path found

    def get_subgraph(self, center_id: str, radius: int = 2) -> GraphSubgraph:
        """Extract a subgraph around a center entity.

        Args:
            center_id: The ID of the center entity.
            radius: The radius in hops (default: 2).

        Returns:
            GraphSubgraph containing nodes and relationships within the radius.
        """
        # Get all nodes within radius
        node_ids = {center_id}
        current_level = {center_id}

        for _ in range(radius):
            next_level = set()
            for eid in current_level:
                rels = self.get_relationships(eid, direction="both")
                for rel in rels:
                    next_level.add(rel.source_id)
                    next_level.add(rel.target_id)
            current_level = next_level - node_ids
            node_ids.update(current_level)
            if not current_level:
                break

        # Get all nodes
        nodes = []
        for nid in node_ids:
            entity = self.get_entity(nid)
            if entity is not None:
                nodes.append(entity)

        # Get all edges between these nodes
        relationships = []
        for nid in node_ids:
            rels = self.get_relationships(nid, direction="outgoing")
            for rel in rels:
                if rel.target_id in node_ids:
                    relationships.append(rel)

        return GraphSubgraph(
            nodes=nodes,
            relationships=relationships,
            center_id=center_id,
            radius=radius,
        )

    def get_centrality(self, entity_id: str) -> float:
        """Get the centrality score of an entity.

        Args:
            entity_id: The ID of the entity.

        Returns:
            Centrality score (higher = more central).
        """
        # Degree centrality: number of connections
        rels = self.get_relationships(entity_id, direction="both")
        return float(len(rels))

    def detect_communities(self, algorithm: str = "leiden") -> list[GraphCommunity]:
        """Detect communities in the graph.

        Args:
            algorithm: Community detection algorithm (default: "leiden").

        Returns:
            List of detected communities.

        Note: This is a placeholder implementation. Full community detection
        requires networkx and community detection libraries (leidenalg).
        """
        # Placeholder: return empty list
        # TODO: Implement using networkx + leidenalg or python-louvain
        # For now, use simple connected components on imports graph
        try:
            import networkx as nx

            # Build graph from import edges
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT src_id, dst_id FROM edges WHERE relation_type = 'imports'",
            )

            G = nx.Graph()
            for row in cursor.fetchall():
                G.add_edge(row["src_id"], row["dst_id"])

            # Get connected components
            components = list(nx.connected_components(G))
            communities = []

            for i, component in enumerate(components):
                entities = [str(nid) for nid in component]
                communities.append(
                    GraphCommunity(
                        id=f"community_{i}",
                        name=f"Community {i}",
                        description=f"Connected component with {len(entities)} entities",
                        entities=entities,
                        confidence=1.0,
                    ),
                )

            return communities
        except ImportError:
            Logger.warning(
                "networkx not installed, returning empty communities list",
            )
            return []

    def get_community(self, community_id: str) -> GraphCommunity | None:
        """Get a community by ID.

        Args:
            community_id: The ID of the community.

        Returns:
            GraphCommunity, or None if not found.

        Note: This re-runs community detection to find the requested community.
        For production use, communities should be cached in a SQLite table.
        """
        communities = self.detect_communities()
        for community in communities:
            if community.id == community_id:
                return community
        return None


__all__ = ["SQLiteGraphStore"]
