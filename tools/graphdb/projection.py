"""GraphDB Projection - Core graph projection logic from ADG SQLite to NetworkX.

This module handles the conversion of canonical ADG SQLite artifacts into
NetworkX graph projections with proper node/edge typing and metadata.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

import networkx as nx

from .schema import (
    EDGE_TYPE_MAPPING,
    NODE_TYPE_MAPPING,
    get_edge_properties,
    get_node_properties,
    validate_edge_type,
    validate_node_type,
)
from tqdm import tqdm


class GraphProjector:
    """Projects ADG SQLite data into NetworkX graphs."""

    def __init__(self, sqlite_path: Path):
        """Initialize the projector.

        Args:
            sqlite_path: Path to the canonical ADG SQLite file
        """
        self.sqlite_path = Path(sqlite_path)
        if not self.sqlite_path.exists():
            raise FileNotFoundError(f"ADG SQLite file not found: {sqlite_path}")

        # Validate SQLite file structure
        self._validate_sqlite_schema()

    def _validate_sqlite_schema(self) -> None:
        """Validate that the SQLite file has the canonical ADG schema.

        The canonical ADG (``tools/generate/generate_full_adg.py``) writes the
        tables ``nodes`` / ``edges`` / ``meta``. This projection adapts those
        to the GraphDB-internal ``entities`` / ``relations`` / ``metadata``
        vocabulary at read time.
        """
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                required_tables = ["nodes", "edges", "meta"]
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = {row[0] for row in cursor.fetchall()}

                missing_tables = [t for t in required_tables if t not in existing_tables]
                if missing_tables:
                    raise ValueError(
                        f"ADG SQLite missing required canonical tables: {missing_tables}",
                    )

                cursor.execute("PRAGMA table_info(nodes)")
                node_columns = {row[1] for row in cursor.fetchall()}
                required_node_columns = {
                    "id", "entity_type", "adg_name", "layer",
                    "resolved_path", "span_line", "enclosing_symbol",
                    "identity_kind", "confidence",
                }
                missing_node_columns = required_node_columns - node_columns
                if missing_node_columns:
                    raise ValueError(
                        f"ADG SQLite nodes table missing columns: {missing_node_columns}",
                    )

                cursor.execute("PRAGMA table_info(edges)")
                edge_columns = {row[1] for row in cursor.fetchall()}
                required_edge_columns = {
                    "id", "src_id", "dst_id", "relation_type", "edge_kind",
                    "source_file", "line_no", "symbol", "semantic_type",
                    "confidence_score",
                }
                missing_edge_columns = required_edge_columns - edge_columns
                if missing_edge_columns:
                    raise ValueError(
                        f"ADG SQLite edges table missing columns: {missing_edge_columns}",
                    )

        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to validate ADG SQLite schema: {e}") from e

    def project_graph(self) -> nx.MultiDiGraph:
        """Project the entire ADG into a NetworkX graph.

        Returns:
            NetworkX graph with all entities and relations
        """
        graph = nx.MultiDiGraph()

        # Load entities as nodes
        self._add_entities_to_graph(graph)

        # Load relations as edges
        self._add_relations_to_graph(graph)

        return graph

    def _add_entities_to_graph(self, graph: nx.MultiDiGraph) -> None:
        """Add every canonical node, preserving unmapped types explicitly."""
        unmapped_types: Dict[str, int] = {}
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, entity_type, adg_name, layer, resolved_path, "
                    "span_line, enclosing_symbol, identity_kind, confidence "
                    "FROM nodes ORDER BY id",
                )
                for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                    (
                        entity_id, entity_type, name, layer, resolved_path,
                        span_line, enclosing_symbol, identity_kind, confidence,
                    ) = row
                    try:
                        graph_type = validate_node_type(entity_type or "")
                    except ValueError:
                        unmapped_types[entity_type or "<null>"] = (
                            unmapped_types.get(entity_type or "<null>", 0) + 1
                        )
                        graph_type = "UnmappedNode"
                        mapping_status = "unmapped"
                    else:
                        mapping_status = "mapped"

                    properties: Dict[str, Any] = {
                        "layer": layer,
                        "file_path": resolved_path,
                        "line_number": span_line,
                        "enclosing_symbol": enclosing_symbol,
                        "identity_kind": identity_kind,
                        "confidence": confidence,
                    }
                    properties = {
                        key: value for key, value in properties.items()
                        if value is not None
                    }
                    node_attrs: Dict[str, Any] = {
                        "adg_id": entity_id,
                        "adg_type": entity_type,
                        "graph_type": graph_type,
                        "name": name,
                        "properties": properties,
                        "mapping_status": mapping_status,
                    }
                    if mapping_status == "mapped":
                        for prop in get_node_properties(entity_type):
                            if prop in properties:
                                node_attrs[prop] = properties[prop]
                    graph.add_node(entity_id, **node_attrs)
        except sqlite3.Error as exc:
            raise RuntimeError(
                f"Failed to load entities from ADG SQLite: {exc}"
            ) from exc

        if unmapped_types:
            top = sorted(
                unmapped_types.items(), key=lambda item: item[1], reverse=True
            )[:5]
            print(
                f"[GraphDB] Preserved {sum(unmapped_types.values())} nodes with "
                f"unmapped entity_type as UnmappedNode (top: {top})",
            )

    def _add_relations_to_graph(self, graph: nx.MultiDiGraph) -> None:
        """Add every canonical edge, preserving direction and multiplicity."""
        unmapped_types: Dict[str, int] = {}
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, src_id, dst_id, relation_type, edge_kind, "
                    "source_file, line_no, symbol, semantic_type, "
                    "confidence_score FROM edges ORDER BY id",
                )
                for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                    (
                        relation_id, from_id, to_id, relation_type, edge_kind,
                        source_file, line_no, symbol, semantic_type,
                        confidence_score,
                    ) = row
                    if from_id not in graph or to_id not in graph:
                        raise RuntimeError(
                            "Canonical edge references an absent projected node: "
                            f"edge_id={relation_id!r}, src_id={from_id!r}, "
                            f"dst_id={to_id!r}"
                        )
                    try:
                        graph_type = validate_edge_type(relation_type or "")
                    except ValueError:
                        unmapped_types[relation_type or "<null>"] = (
                            unmapped_types.get(relation_type or "<null>", 0) + 1
                        )
                        graph_type = "UNMAPPED_RELATION"
                        mapping_status = "unmapped"
                    else:
                        mapping_status = "mapped"

                    properties: Dict[str, Any] = {
                        "edge_kind": edge_kind,
                        "source_file": source_file,
                        "line_number": line_no,
                        "symbol": symbol,
                        "semantic_type": semantic_type,
                        "confidence_score": confidence_score,
                    }
                    properties = {
                        key: value for key, value in properties.items()
                        if value is not None
                    }
                    edge_attrs: Dict[str, Any] = {
                        "adg_id": relation_id,
                        "adg_type": relation_type,
                        "graph_type": graph_type,
                        "properties": properties,
                        "mapping_status": mapping_status,
                    }
                    if mapping_status == "mapped":
                        for prop in get_edge_properties(relation_type):
                            if prop in properties:
                                edge_attrs[prop] = properties[prop]
                    graph.add_edge(
                        from_id, to_id, key=relation_id, **edge_attrs
                    )
        except sqlite3.Error as exc:
            raise RuntimeError(
                f"Failed to load relations from ADG SQLite: {exc}"
            ) from exc

        if unmapped_types:
            top = sorted(
                unmapped_types.items(), key=lambda item: item[1], reverse=True
            )[:5]
            print(
                f"[GraphDB] Preserved {sum(unmapped_types.values())} edges with "
                f"unmapped relation_type as UNMAPPED_RELATION (top: {top})",
            )

    def project_subgraph(
        self,
        entity_types: List[str] | None = None,
        relation_types: List[str] | None = None,
        layer_filter: str | None = None,
    ) -> nx.MultiDiGraph:
        """Project a filtered subgraph.

        Args:
            entity_types: List of entity types to include (None = all)
            relation_types: List of relation types to include (None = all)
            layer_filter: Filter entities by layer (None = no filter)

        Returns:
            Filtered NetworkX graph
        """
        # Start with full projection
        graph = self.project_graph()

        # Filter by entity types
        if entity_types is not None:
            nodes_to_keep = []
            for node, attrs in graph.nodes(data=True):
                if attrs.get("adg_type") in entity_types:
                    nodes_to_keep.append(node)
            graph = graph.subgraph(nodes_to_keep).copy()

        # Filter by relation types
        if relation_types is not None:
            edges_to_keep = []
            for u, v, edge_key, attrs in graph.edges(keys=True, data=True):
                if attrs.get("adg_type") in relation_types:
                    edges_to_keep.append((u, v, edge_key))
            graph = graph.edge_subgraph(edges_to_keep).copy()

        # Filter by layer
        if layer_filter is not None:
            nodes_to_keep = []
            for node, attrs in graph.nodes(data=True):
                node_layer = attrs.get("properties", {}).get("layer")
                if node_layer == layer_filter:
                    nodes_to_keep.append(node)
            graph = graph.subgraph(nodes_to_keep).copy()

        return graph

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the projected graph.

        Returns:
            Dictionary with graph statistics
        """
        graph = self.project_graph()

        # Count nodes and edges by type
        node_type_counts: Dict[str, int] = {}
        for _, attrs in graph.nodes(data=True):
            node_type = attrs.get("graph_type", "Unknown")
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1

        edge_type_counts: Dict[str, int] = {}
        for _, _, attrs in graph.edges(data=True):
            edge_type = attrs.get("graph_type", "Unknown")
            edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1

        # Calculate basic graph metrics
        try:
            density = nx.density(graph)
        except (nx.NetworkXError, ZeroDivisionError):
            density = 0.0

        try:
            # For large graphs, use approximation
            if graph.number_of_nodes() > 10000:
                avg_clustering = 0.0  # Skip for performance
            else:
                # Clustering has no MultiDiGraph definition. Compute the legacy
                # statistic on an explicit undirected endpoint-presence view.
                clustering_graph = nx.Graph(graph.to_undirected())
                avg_clustering = nx.average_clustering(clustering_graph)
        except (nx.NetworkXError, ZeroDivisionError):
            avg_clustering = 0.0

        # Find connected components
        try:
            if graph.is_directed():
                components = list(nx.weakly_connected_components(graph))
            else:
                components = list(nx.connected_components(graph))
            num_components = len(components)
            largest_component_size = max(len(comp) for comp in components) if components else 0
        except nx.NetworkXError:
            num_components = 0
            largest_component_size = 0

        return {
            "total_nodes": graph.number_of_nodes(),
            "total_edges": graph.number_of_edges(),
            "node_type_counts": node_type_counts,
            "edge_type_counts": edge_type_counts,
            "density": density,
            "average_clustering": avg_clustering,
            "num_connected_components": num_components,
            "largest_component_size": largest_component_size,
            "is_directed": graph.is_directed(),
        }

    def validate_projection(self, graph: nx.Graph) -> List[str]:
        """Validate a projected graph for correctness.

        Args:
            graph: NetworkX graph to validate

        Returns:
            List of validation warnings/errors
        """
        warnings = []

        # Check for empty graph
        if graph.number_of_nodes() == 0:
            warnings.append("Graph has no nodes")
            return warnings

        # Check for isolated nodes
        isolated_nodes = list(nx.isolates(graph))
        if isolated_nodes:
            warnings.append(f"Found {len(isolated_nodes)} isolated nodes")

        # Check for nodes without required attributes
        required_node_attrs = ["adg_id", "adg_type", "graph_type", "name"]
        for node, attrs in graph.nodes(data=True):
            missing_attrs = [attr for attr in required_node_attrs if attr not in attrs]
            if missing_attrs:
                warnings.append(f"Node {node} missing attributes: {missing_attrs}")

        # Check for edges without required attributes.
        required_edge_attrs = ["adg_id", "adg_type", "graph_type"]
        if graph.is_multigraph():
            edge_rows = graph.edges(keys=True, data=True)
        else:
            edge_rows = (
                (u, v, None, attrs)
                for u, v, attrs in graph.edges(data=True)
            )
        for u, v, edge_key, attrs in edge_rows:
            missing_attrs = [
                attr for attr in required_edge_attrs if attr not in attrs
            ]
            if missing_attrs:
                warnings.append(
                    f"Edge {u}-{v} key={edge_key!r} missing attributes: "
                    f"{missing_attrs}"
                )

        # Check for self-loops (may be valid depending on relation type)
        self_loops = list(nx.selfloop_edges(graph))
        if self_loops:
            warnings.append(f"Found {len(self_loops)} self-loop edges")

        return warnings
