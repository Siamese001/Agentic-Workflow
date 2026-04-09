"""Blast-Radius Queries - Query pack for impact analysis and dependency exploration.

This module provides queries to analyze blast radius, impact of changes,
and dependency relationships in the ADG graph.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

import networkx as nx


class BlastRadiusQueries:
    """Blast-radius query pack for ADG graph analysis."""

    def __init__(self, graph: nx.Graph):
        """Initialize with a NetworkX graph.

        Args:
            graph: NetworkX graph with ADG projection
        """
        self.graph = graph

    def transitive_dependents(self, node_id: str, max_depth: int = 10) -> Dict[str, Any]:
        """Find all nodes that depend on the given node.

        Args:
            node_id: Starting node ID
            max_depth: Maximum depth to explore

        Returns:
            Dictionary with dependent nodes and paths
        """
        if node_id not in self.graph:
            raise ValueError(f"Node {node_id} not found in graph")

        # Use reverse graph to find dependents
        reverse_graph = self.graph.reverse()

        # Find all reachable nodes from the target in reverse
        try:
            # Use BFS to limit depth
            dependents = {}
            visited = set()
            queue = [(node_id, 0, [node_id])]

            while queue:
                current, depth, path = queue.pop(0)

                if depth >= max_depth or current in visited:
                    continue

                visited.add(current)

                if depth > 0:  # Don't include the starting node
                    dependents[current] = {
                        "depth": depth,
                        "path": path.copy(),
                        "node_type": self.graph.nodes[current].get("graph_type"),
                        "layer": self.graph.nodes[current].get("properties", {}).get("layer"),
                    }

                # Add neighbors to queue
                for neighbor in reverse_graph.neighbors(current):
                    if neighbor not in visited:
                        new_path = path + [neighbor]
                        queue.append((neighbor, depth + 1, new_path))

            return {
                "source_node": node_id,
                "total_dependents": len(dependents),
                "max_depth_explored": max_depth,
                "dependents": dependents,
                "layers_affected": set(dep["layer"] for dep in dependents.values() if dep["layer"]),
            }

        except (nx.NetworkXError, ValueError, RuntimeError) as e:
            raise RuntimeError(f"Failed to compute transitive dependents: {e}")

    def shortest_illegal_path(self, source: str, sink: str) -> Dict[str, Any]:
        """Find shortest path that violates policies.

        Args:
            source: Source node ID
            sink: Sink node ID

        Returns:
            Dictionary with illegal path analysis
        """
        if source not in self.graph or sink not in self.graph:
            raise ValueError(f"Source or sink node not found in graph")

        # Find all paths between source and sink
        try:
            paths = list(nx.all_simple_paths(self.graph, source, sink, cutoff=5))
        except nx.NetworkXNoPath:
            return {
                "source": source,
                "sink": sink,
                "paths_found": 0,
                "illegal_paths": [],
                "shortest_legal_path": None,
            }

        illegal_paths = []
        legal_paths = []

        for path in paths:
            path_edges = []
            is_illegal = False
            violations = []

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_attrs = self.graph.edges[u, v]
                path_edges.append(
                    {
                        "from": u,
                        "to": v,
                        "edge_type": edge_attrs.get("graph_type"),
                        "properties": edge_attrs.get("properties", {}),
                    }
                )

                # Check for illegal patterns
                u_attrs = self.graph.nodes[u]
                v_attrs = self.graph.nodes[v]

                u_layer = u_attrs.get("properties", {}).get("layer")
                v_layer = v_attrs.get("properties", {}).get("layer")

                # Check layer violations
                if u_layer and v_layer:
                    layer_hierarchy = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
                    u_level = layer_hierarchy.get(u_layer)
                    v_level = layer_hierarchy.get(v_layer)

                    if u_level is not None and v_level is not None:
                        if edge_attrs.get("graph_type") == "IMPORTS" and v_level > u_level:
                            is_illegal = True
                            violations.append(f"Gravity import violation: {u_layer} -> {v_layer}")

                        # Check forbidden transitions
                        forbidden = {
                            ("L6", "L2"): "Infrastructure -> Execution",
                            ("L5", "L2"): "Safety -> Execution",
                            ("L4", "L0"): "State -> Routing",
                        }
                        transition = (u_layer, v_layer)
                        if transition in forbidden:
                            is_illegal = True
                            violations.append(f"Forbidden transition: {forbidden[transition]}")

            path_info = {
                "path": path,
                "edges": path_edges,
                "length": len(path) - 1,
                "violations": violations,
            }

            if is_illegal:
                illegal_paths.append(path_info)
            else:
                legal_paths.append(path_info)

        # Find shortest paths
        shortest_illegal = min(illegal_paths, key=lambda x: x["length"]) if illegal_paths else None
        shortest_legal = min(legal_paths, key=lambda x: x["length"]) if legal_paths else None

        return {
            "source": source,
            "sink": sink,
            "paths_found": len(paths),
            "illegal_paths": illegal_paths,
            "legal_paths": legal_paths,
            "shortest_illegal_path": shortest_illegal,
            "shortest_legal_path": shortest_legal,
            "has_illegal_path": len(illegal_paths) > 0,
        }

    def bypass_paths(self, gateway: str) -> List[Dict[str, Any]]:
        """Find paths that bypass approved gateways.

        Args:
            gateway: Gateway node ID

        Returns:
            List of bypass paths
        """
        if gateway not in self.graph:
            raise ValueError(f"Gateway {gateway} not found in graph")

        gateway_attrs = self.graph.nodes[gateway]
        if gateway_attrs.get("graph_type") != "Gateway":
            raise ValueError(f"Node {gateway} is not a gateway")

        bypass_paths = []

        # Find all nodes that write through the gateway
        writes_through = [
            (u, v)
            for u, v in self.graph.edges(gateway)
            if self.graph.edges[u, v].get("graph_type") == "WRITES_THROUGH"
        ]

        for source, target in writes_through:
            # Find alternative paths from source to target that don't use the gateway
            try:
                # Remove gateway temporarily and find paths
                temp_graph = self.graph.copy()
                temp_graph.remove_node(gateway)

                if temp_graph.has_node(source) and temp_graph.has_node(target):
                    try:
                        alt_paths = list(nx.all_simple_paths(temp_graph, source, target, cutoff=5))

                        for alt_path in alt_paths:
                            path_edges = []
                            for i in range(len(alt_path) - 1):
                                u, v = alt_path[i], alt_path[i + 1]
                                edge_attrs = self.graph.edges[u, v]
                                path_edges.append(
                                    {
                                        "from": u,
                                        "to": v,
                                        "edge_type": edge_attrs.get("graph_type"),
                                    }
                                )

                            bypass_paths.append(
                                {
                                    "source": source,
                                    "target": target,
                                    "gateway": gateway,
                                    "bypass_path": alt_path,
                                    "path_edges": path_edges,
                                    "path_length": len(alt_path) - 1,
                                    "risk_level": "high" if len(alt_path) <= 3 else "medium",
                                }
                            )
                    except nx.NetworkXNoPath:
                        pass  # No alternative paths, which is good

            except (nx.NetworkXError, ValueError) as e:
                print(f"Warning: Error analyzing bypass for {gateway}: {e}")

        return bypass_paths

    def impact_analysis(self, removed_node: str) -> Dict[str, Any]:
        """Analyze impact of removing a node.

        Args:
            removed_node: Node ID to analyze removal for

        Returns:
            Dictionary with impact analysis
        """
        if removed_node not in self.graph:
            raise ValueError(f"Node {removed_node} not found in graph")

        # Create graph without the node
        temp_graph = self.graph.copy()
        temp_graph.remove_node(removed_node)

        # Analyze connectivity changes
        original_components = list(nx.connected_components(self.graph))
        new_components = list(nx.connected_components(temp_graph))

        # Find nodes that become isolated
        isolated_nodes = [node for node in temp_graph.nodes() if temp_graph.degree(node) == 0]

        # Find broken dependencies
        broken_dependencies = []
        for neighbor in self.graph.neighbors(removed_node):
            neighbor_attrs = self.graph.nodes[neighbor]
            edge_attrs = self.graph.edges[removed_node, neighbor]

            broken_dependencies.append(
                {
                    "affected_node": neighbor,
                    "edge_type": edge_attrs.get("graph_type"),
                    "relationship": edge_attrs.get("properties", {}),
                    "node_type": neighbor_attrs.get("graph_type"),
                    "layer": neighbor_attrs.get("properties", {}).get("layer"),
                }
            )

        # Calculate impact metrics
        impact_score = 0
        impact_factors = {
            "high_degree": self.graph.degree(removed_node) * 2,
            "broken_dependencies": len(broken_dependencies) * 3,
            "isolated_nodes": len(isolated_nodes) * 5,
            "component_fragmentation": abs(len(new_components) - len(original_components)) * 4,
        }

        impact_score = sum(impact_factors.values())

        # Determine impact level
        if impact_score >= 20:
            impact_level = "critical"
        elif impact_score >= 10:
            impact_level = "high"
        elif impact_score >= 5:
            impact_level = "medium"
        else:
            impact_level = "low"

        return {
            "removed_node": removed_node,
            "node_type": self.graph.nodes[removed_node].get("graph_type"),
            "impact_score": impact_score,
            "impact_level": impact_level,
            "impact_factors": impact_factors,
            "original_degree": self.graph.degree(removed_node),
            "broken_dependencies": broken_dependencies,
            "isolated_nodes": isolated_nodes,
            "connectivity_change": {
                "original_components": len(original_components),
                "new_components": len(new_components),
                "fragmentation": len(new_components) - len(original_components),
            },
        }

    def high_fan_in_out_hubs(self, min_connections: int = 10) -> Dict[str, Any]:
        """Find high fan-in/fan-out hubs with policy context.

        Args:
            min_connections: Minimum number of connections to be considered a hub

        Returns:
            Dictionary with hub analysis
        """
        hubs = {
            "fan_in": [],
            "fan_out": [],
            "bidirectional": [],
        }

        # Calculate fan-in and fan-out for each node
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node) if self.graph.is_directed() else self.graph.degree(node)
            out_degree = self.graph.out_degree(node) if self.graph.is_directed() else 0

            node_attrs = self.graph.nodes[node]

            hub_info = {
                "node": node,
                "node_type": node_attrs.get("graph_type"),
                "layer": node_attrs.get("properties", {}).get("layer"),
                "fan_in": in_degree,
                "fan_out": out_degree,
                "total_connections": in_degree + out_degree,
            }

            # Check bidirectional hub
            if in_degree >= min_connections and out_degree >= min_connections:
                hubs["bidirectional"].append(hub_info)
            elif in_degree >= min_connections:
                hubs["fan_in"].append(hub_info)
            elif out_degree >= min_connections:
                hubs["fan_out"].append(hub_info)

        # Sort by connection count
        for hub_type in hubs:
            hubs[hub_type].sort(key=lambda x: x["total_connections"], reverse=True)

        # Analyze policy context for top hubs
        top_hubs = hubs["bidirectional"][:5] + hubs["fan_in"][:5] + hubs["fan_out"][:5]

        for hub in top_hubs:
            node = hub["node"]

            # Check if hub is protected by policies
            incoming_edges = list(self.graph.in_edges(node, data=True))
            policy_protections = [
                attrs.get("graph_type")
                for _, _, attrs in incoming_edges
                if attrs.get("graph_type") in ["APPLIES_GUARDRAIL", "VALIDATES", "VERIFIES_POLICY"]
            ]

            hub["policy_protections"] = policy_protections
            hub["is_protected"] = len(policy_protections) > 0

            # Check for violations involving the hub
            violations = []
            for u, v, attrs in self.graph.edges(node, data=True):
                if attrs.get("graph_type") == "VIOLATES":
                    violations.append(
                        {
                            "target": v,
                            "violation_type": attrs.get("properties", {}).get("violation_type"),
                        }
                    )

            hub["violations"] = violations
            hub["has_violations"] = len(violations) > 0

        return {
            "min_connections_threshold": min_connections,
            "total_hubs": {
                "fan_in": len(hubs["fan_in"]),
                "fan_out": len(hubs["fan_out"]),
                "bidirectional": len(hubs["bidirectional"]),
            },
            "hubs": hubs,
        }

    def affected_neighborhoods(self, edge_additions: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Analyze components newly affected by edge additions between snapshots.

        Args:
            edge_additions: List of (source, target) tuples for new edges

        Returns:
            Dictionary with neighborhood analysis
        """
        affected_areas = []

        for source, target in edge_additions:
            if source not in self.graph or target not in self.graph:
                continue

            # Find the neighborhood around the new edge
            source_neighbors = set(self.graph.neighbors(source))
            target_neighbors = set(self.graph.neighbors(target))

            # Combined neighborhood
            neighborhood = {source, target} | source_neighbors | target_neighbors

            # Analyze the neighborhood
            neighborhood_subgraph = self.graph.subgraph(neighborhood)

            # Count different types of nodes and edges in neighborhood
            node_types = {}
            for node in neighborhood:
                node_type = self.graph.nodes[node].get("graph_type", "Unknown")
                node_types[node_type] = node_types.get(node_type, 0) + 1

            edge_types = {}
            for u, v, attrs in neighborhood_subgraph.edges(data=True):
                edge_type = attrs.get("graph_type", "Unknown")
                edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

            # Check for policy violations in neighborhood
            violations = []
            for u, v, attrs in neighborhood_subgraph.edges(data=True):
                if attrs.get("graph_type") == "VIOLATES":
                    violations.append(
                        {
                            "edge": (u, v),
                            "violation_type": attrs.get("properties", {}).get("violation_type"),
                        }
                    )

            affected_areas.append(
                {
                    "new_edge": (source, target),
                    "neighborhood_size": len(neighborhood),
                    "node_types": node_types,
                    "edge_types": edge_types,
                    "violations": violations,
                    "risk_level": "high" if len(violations) > 0 else "medium",
                }
            )

        # Sort by risk level and neighborhood size
        affected_areas.sort(key=lambda x: (x["risk_level"], x["neighborhood_size"]), reverse=True)

        return {
            "edge_additions_analyzed": len(edge_additions),
            "affected_areas": affected_areas,
            "total_violations": sum(len(area["violations"]) for area in affected_areas),
        }
