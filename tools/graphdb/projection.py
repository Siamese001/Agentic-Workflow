"""GraphDB Projection - Core graph projection logic from ADG SQLite to NetworkX.

This module handles the conversion of canonical ADG SQLite artifacts into
NetworkX graph projections with proper node/edge typing and metadata.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

import networkx as nx

from tools.graphdb.schema import (
    EDGE_TYPE_MAPPING,
    NODE_TYPE_MAPPING,
    get_edge_properties,
    get_node_properties,
    validate_edge_type,
    validate_node_type,
)


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
        """Validate that the SQLite file has the expected ADG schema."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Check for required tables
                required_tables = ["entities", "relations", "metadata"]
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = {row[0] for row in cursor.fetchall()}

                missing_tables = required_tables - existing_tables
                if missing_tables:
                    raise ValueError(f"ADG SQLite missing required tables: {missing_tables}")

                # Check entity table structure
                cursor.execute("PRAGMA table_info(entities)")
                entity_columns = {row[1] for row in cursor.fetchall()}
                required_entity_columns = {"id", "type", "name", "properties"}
                missing_entity_columns = required_entity_columns - entity_columns
                if missing_entity_columns:
                    raise ValueError(f"ADG SQLite entities table missing columns: {missing_entity_columns}")

                # Check relation table structure
                cursor.execute("PRAGMA table_info(relations)")
                relation_columns = {row[1] for row in cursor.fetchall()}
                required_relation_columns = {"id", "from_id", "to_id", "type", "properties"}
                missing_relation_columns = required_relation_columns - relation_columns
                if missing_relation_columns:
                    raise ValueError(
                        f"ADG SQLite relations table missing columns: {missing_relation_columns}"
                    )

        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to validate ADG SQLite schema: {e}")

    def project_graph(self) -> nx.Graph:
        """Project the entire ADG into a NetworkX graph.

        Returns:
            NetworkX graph with all entities and relations
        """
        graph = nx.Graph()

        # Load entities as nodes
        self._add_entities_to_graph(graph)

        # Load relations as edges
        self._add_relations_to_graph(graph)

        return graph

    def _add_entities_to_graph(self, graph: nx.Graph) -> None:
        """Add ADG entities as graph nodes."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, type, name, properties FROM entities")

                for row in cursor.fetchall():
                    entity_id, entity_type, name, properties_json = row

                    # Validate and map entity type
                    try:
                        graph_type = validate_node_type(entity_type)
                    except ValueError:
                        # Skip unknown entity types with warning
                        print(f"Warning: Unknown entity type '{entity_type}', skipping entity {entity_id}")
                        continue

                    # Parse properties
                    properties = {}
                    if properties_json:
                        try:
                            import json

                            properties = json.loads(properties_json)
                        except json.JSONDecodeError:
                            print(f"Warning: Invalid JSON in properties for entity {entity_id}")

                    # Create node with all required properties
                    node_attrs = {
                        "adg_id": entity_id,
                        "adg_type": entity_type,
                        "graph_type": graph_type,
                        "name": name,
                        "properties": properties,
                    }

                    # Add type-specific properties
                    type_specific_props = get_node_properties(entity_type)
                    for prop in type_specific_props:
                        if prop in properties:
                            node_attrs[prop] = properties[prop]

                    graph.add_node(entity_id, **node_attrs)

        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to load entities from ADG SQLite: {e}")

    def _add_relations_to_graph(self, graph: nx.Graph) -> None:
        """Add ADG relations as graph edges."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, from_id, to_id, type, properties FROM relations")

                for row in cursor.fetchall():
                    relation_id, from_id, to_id, relation_type, properties_json = row

                    # Skip if either endpoint doesn't exist in graph
                    if from_id not in graph or to_id not in graph:
                        continue

                    # Validate and map relation type
                    try:
                        graph_type = validate_edge_type(relation_type)
                    except ValueError:
                        # Skip unknown relation types with warning
                        print(
                            f"Warning: Unknown relation type '{relation_type}', skipping relation {relation_id}"
                        )
                        continue

                    # Parse properties
                    properties = {}
                    if properties_json:
                        try:
                            import json

                            properties = json.loads(properties_json)
                        except json.JSONDecodeError:
                            print(f"Warning: Invalid JSON in properties for relation {relation_id}")

                    # Create edge with all required properties
                    edge_attrs = {
                        "adg_id": relation_id,
                        "adg_type": relation_type,
                        "graph_type": graph_type,
                        "properties": properties,
                    }

                    # Add type-specific properties
                    type_specific_props = get_edge_properties(relation_type)
                    for prop in type_specific_props:
                        if prop in properties:
                            edge_attrs[prop] = properties[prop]

                    graph.add_edge(from_id, to_id, **edge_attrs)

        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to load relations from ADG SQLite: {e}")

    def project_subgraph(
        self,
        entity_types: List[str] | None = None,
        relation_types: List[str] | None = None,
        layer_filter: str | None = None,
    ) -> nx.Graph:
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
            for u, v, attrs in graph.edges(data=True):
                if attrs.get("adg_type") in relation_types:
                    edges_to_keep.append((u, v))
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
        node_type_counts = {}
        for _, attrs in graph.nodes(data=True):
            node_type = attrs.get("graph_type", "Unknown")
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1

        edge_type_counts = {}
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
                avg_clustering = nx.average_clustering(graph)
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

        # Check for edges without required attributes
        required_edge_attrs = ["adg_id", "adg_type", "graph_type"]
        for u, v, attrs in graph.edges(data=True):
            missing_attrs = [attr for attr in required_edge_attrs if attr not in attrs]
            if missing_attrs:
                warnings.append(f"Edge {u}-{v} missing attributes: {missing_attrs}")

        # Check for self-loops (may be valid depending on relation type)
        self_loops = list(nx.selfloop_edges(graph))
        if self_loops:
            warnings.append(f"Found {len(self_loops)} self-loop edges")

        return warnings
