"""Analyst Investigation Workflows - Query pack for architectural analysis.

This module provides analyst-friendly workflows for subgraph extraction,
violation explanation, and architectural investigation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

import networkx as nx


class AnalystQueries:
    """Analyst investigation query pack for ADG graph analysis."""

    def __init__(self, graph: nx.Graph):
        """Initialize with a NetworkX graph.

        Args:
            graph: NetworkX graph with ADG projection
        """
        self.graph = graph

    def extract_subgraph_by_layer(self, layer: str) -> Dict[str, Any]:
        """Extract subgraph by layer.

        Args:
            layer: Layer name (e.g., "L0", "L1", etc.)

        Returns:
            Dictionary with layer subgraph analysis
        """
        # Find all nodes in the specified layer
        layer_nodes = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("properties", {}).get("layer") == layer
        ]

        if not layer_nodes:
            return {
                "layer": layer,
                "node_count": 0,
                "edge_count": 0,
                "subgraph": None,
                "analysis": {"error": f"No nodes found in layer {layer}"},
            }

        # Extract subgraph
        subgraph = self.graph.subgraph(layer_nodes)

        # Analyze the subgraph
        node_types = {}
        for node, attrs in subgraph.nodes(data=True):
            node_type = attrs.get("graph_type", "Unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1

        edge_types = {}
        for u, v, attrs in subgraph.edges(data=True):
            edge_type = attrs.get("graph_type", "Unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

        # Find key metrics
        try:
            density = nx.density(subgraph)
        except (nx.NetworkXError, ZeroDivisionError):
            density = 0.0

        # Find connected components
        try:
            components = list(nx.connected_components(subgraph))
            num_components = len(components)
            largest_component_size = max(len(comp) for comp in components) if components else 0
        except nx.NetworkXError:
            num_components = 0
            largest_component_size = 0

        return {
            "layer": layer,
            "node_count": subgraph.number_of_nodes(),
            "edge_count": subgraph.number_of_edges(),
            "subgraph": subgraph,
            "node_types": node_types,
            "edge_types": edge_types,
            "density": density,
            "connected_components": num_components,
            "largest_component_size": largest_component_size,
            "is_fully_connected": num_components == 1,
        }

    def extract_subgraph_by_agent(self, agent_name: str) -> Dict[str, Any]:
        """Extract subgraph by agent.

        Args:
            agent_name: Agent name or partial name

        Returns:
            Dictionary with agent subgraph analysis
        """
        # Find agent nodes matching the name
        agent_nodes = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("graph_type") == "Agent" and agent_name.lower() in attrs.get("name", "").lower()
        ]

        if not agent_nodes:
            return {
                "agent_name": agent_name,
                "node_count": 0,
                "edge_count": 0,
                "subgraph": None,
                "analysis": {"error": f"No agents found matching '{agent_name}'"},
            }

        # Include the agent and its immediate neighborhood
        neighborhood_nodes = set(agent_nodes)
        for agent in agent_nodes:
            neighborhood_nodes.update(self.graph.neighbors(agent))
            # Also include neighbors of neighbors for context
            for neighbor in self.graph.neighbors(agent):
                neighborhood_nodes.update(self.graph.neighbors(neighbor))

        # Extract subgraph
        subgraph = self.graph.subgraph(neighborhood_nodes)

        # Analyze the subgraph
        agent_analysis = []
        for agent in agent_nodes:
            agent_attrs = self.graph.nodes[agent]

            # Find agent's capabilities
            capability_edges = [
                (u, v, attrs)
                for u, v, attrs in self.graph.edges(agent, data=True)
                if attrs.get("graph_type") == "HAS_CAPABILITY"
            ]

            # Find agent's tools
            tool_edges = [
                (u, v, attrs)
                for u, v, attrs in self.graph.edges(agent, data=True)
                if attrs.get("graph_type") == "INVOKES_TOOL"
            ]

            # Find agent's providers
            provider_edges = [
                (u, v, attrs)
                for u, v, attrs in self.graph.edges(agent, data=True)
                if attrs.get("graph_type") == "INVOKES_PROVIDER"
            ]

            agent_analysis.append(
                {
                    "agent_id": agent,
                    "agent_name": agent_attrs.get("name"),
                    "capabilities": len(capability_edges),
                    "tools": len(tool_edges),
                    "providers": len(provider_edges),
                    "total_connections": self.graph.degree(agent),
                }
            )

        return {
            "agent_name": agent_name,
            "matching_agents": agent_nodes,
            "node_count": subgraph.number_of_nodes(),
            "edge_count": subgraph.number_of_edges(),
            "subgraph": subgraph,
            "agent_analysis": agent_analysis,
        }

    def extract_subgraph_by_gateway(self, gateway_name: str) -> Dict[str, Any]:
        """Extract subgraph by gateway.

        Args:
            gateway_name: Gateway name or partial name

        Returns:
            Dictionary with gateway subgraph analysis
        """
        # Find gateway nodes matching the name
        gateway_nodes = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("graph_type") == "Gateway" and gateway_name.lower() in attrs.get("name", "").lower()
        ]

        if not gateway_nodes:
            return {
                "gateway_name": gateway_name,
                "node_count": 0,
                "edge_count": 0,
                "subgraph": None,
                "analysis": {"error": f"No gateways found matching '{gateway_name}'"},
            }

        # For each gateway, analyze its usage patterns
        gateway_analysis = []
        all_related_nodes = set(gateway_nodes)

        for gateway in gateway_nodes:
            gateway_attrs = self.graph.nodes[gateway]

            # Find writes through gateway
            writes_through = [
                (u, v, attrs)
                for u, v, attrs in self.graph.edges(gateway, data=True)
                if attrs.get("graph_type") == "WRITES_THROUGH"
            ]

            # Find reads from gateway
            reads_from = [
                (u, v, attrs)
                for u, v, attrs in self.graph.edges(gateway, data=True)
                if attrs.get("graph_type") == "READS_FROM"
            ]

            # Find routes through gateway
            routes_through = [
                (u, v, attrs)
                for u, v, attrs in self.graph.edges(gateway, data=True)
                if attrs.get("graph_type") == "ROUTES_THROUGH"
            ]

            # Collect related nodes
            for u, v, _ in writes_through + reads_from + routes_through:
                all_related_nodes.add(u)
                all_related_nodes.add(v)

            # Check for bypass violations
            bypass_violations = []
            for u, v, attrs in self.graph.edges(data=True):
                if attrs.get("graph_type") == "BYPASSES":
                    v_attrs = self.graph.nodes[v]
                    if (
                        v_attrs.get("graph_type") == "Gateway"
                        and gateway_name.lower() in v_attrs.get("name", "").lower()
                    ):
                        bypass_violations.append((u, v, attrs))

            gateway_analysis.append(
                {
                    "gateway_id": gateway,
                    "gateway_name": gateway_attrs.get("name"),
                    "writes_through": len(writes_through),
                    "reads_from": len(reads_from),
                    "routes_through": len(routes_through),
                    "bypass_violations": len(bypass_violations),
                    "total_connections": self.graph.degree(gateway),
                }
            )

        # Extract subgraph with all related nodes
        subgraph = self.graph.subgraph(all_related_nodes)

        return {
            "gateway_name": gateway_name,
            "matching_gateways": gateway_nodes,
            "node_count": subgraph.number_of_nodes(),
            "edge_count": subgraph.number_of_edges(),
            "subgraph": subgraph,
            "gateway_analysis": gateway_analysis,
        }

    def extract_subgraph_by_provider(self, provider_name: str) -> Dict[str, Any]:
        """Extract subgraph by provider.

        Args:
            provider_name: Provider name or partial name

        Returns:
            Dictionary with provider subgraph analysis
        """
        # Find provider nodes matching the name
        provider_nodes = [
            node
            for node, attrs in self.graph.nodes(data=True)
            if attrs.get("graph_type") == "Provider"
            and provider_name.lower() in attrs.get("name", "").lower()
        ]

        if not provider_nodes:
            return {
                "provider_name": provider_name,
                "node_count": 0,
                "edge_count": 0,
                "subgraph": None,
                "analysis": {"error": f"No providers found matching '{provider_name}'"},
            }

        # Analyze provider usage patterns
        provider_analysis = []
        all_related_nodes = set(provider_nodes)

        for provider in provider_nodes:
            provider_attrs = self.graph.nodes[provider]

            # Find agents that invoke this provider
            invokers = [
                (u, v, attrs)
                for u, v, attrs in self.graph.edges(data=True)
                if v == provider and attrs.get("graph_type") == "INVOKES_PROVIDER"
            ]

            # Find provider's capabilities
            capabilities = [
                (u, v, attrs)
                for u, v, attrs in self.graph.edges(provider, data=True)
                if attrs.get("graph_type") == "HAS_CAPABILITY"
            ]

            # Collect related nodes
            for u, v, _ in invokers + capabilities:
                all_related_nodes.add(u)
                all_related_nodes.add(v)

            # Analyze invoker types
            invoker_types = {}
            for u, v, _ in invokers:
                u_attrs = self.graph.nodes[u]
                invoker_type = u_attrs.get("graph_type", "Unknown")
                invoker_types[invoker_type] = invoker_types.get(invoker_type, 0) + 1

            provider_analysis.append(
                {
                    "provider_id": provider,
                    "provider_name": provider_attrs.get("name"),
                    "interface": provider_attrs.get("properties", {}).get("interface"),
                    "invokers": len(invokers),
                    "capabilities": len(capabilities),
                    "invoker_types": invoker_types,
                    "total_connections": self.graph.degree(provider),
                }
            )

        # Extract subgraph with all related nodes
        subgraph = self.graph.subgraph(all_related_nodes)

        return {
            "provider_name": provider_name,
            "matching_providers": provider_nodes,
            "node_count": subgraph.number_of_nodes(),
            "edge_count": subgraph.number_of_edges(),
            "subgraph": subgraph,
            "provider_analysis": provider_analysis,
        }

    def violation_explanation_paths(self, violation_node: str) -> Dict[str, Any]:
        """Generate explanation paths for violations.

        Args:
            violation_node: Node ID with violations

        Returns:
            Dictionary with violation explanation paths
        """
        if violation_node not in self.graph:
            raise ValueError(f"Node {violation_node} not found in graph")

        # Find all violation edges connected to this node
        violation_edges = [
            (u, v, attrs)
            for u, v, attrs in self.graph.edges(violation_node, data=True)
            if attrs.get("graph_type") == "VIOLATES"
        ]

        if not violation_edges:
            return {
                "violation_node": violation_node,
                "violation_count": 0,
                "explanation_paths": [],
                "analysis": {"message": "No violations found for this node"},
            }

        explanation_paths = []

        for u, v, attrs in violation_edges:
            violation_type = attrs.get("properties", {}).get("violation_type", "Unknown")
            severity = attrs.get("properties", {}).get("severity", "medium")
            description = attrs.get("properties", {}).get("description", "")

            # Trace the violation path
            path_analysis = self._trace_violation_path(u, v, attrs)

            explanation_paths.append(
                {
                    "violation_edge": (u, v),
                    "violation_type": violation_type,
                    "severity": severity,
                    "description": description,
                    "path_analysis": path_analysis,
                }
            )

        return {
            "violation_node": violation_node,
            "violation_count": len(violation_edges),
            "explanation_paths": explanation_paths,
            "node_info": self.graph.nodes[violation_node],
        }

    def _trace_violation_path(self, u: str, v: str, edge_attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Trace and analyze a violation path.

        Args:
            u: Source node
            v: Target node
            edge_attrs: Edge attributes

        Returns:
            Dictionary with path analysis
        """
        u_attrs = self.graph.nodes[u]
        v_attrs = self.graph.nodes[v]

        # Get layer information
        u_layer = u_attrs.get("properties", {}).get("layer")
        v_layer = v_attrs.get("properties", {}).get("layer")

        # Get node types
        u_type = u_attrs.get("graph_type")
        v_type = v_attrs.get("graph_type")

        # Analyze the violation context
        context = {
            "source": {
                "node": u,
                "name": u_attrs.get("name"),
                "type": u_type,
                "layer": u_layer,
            },
            "target": {
                "node": v,
                "name": v_attrs.get("name"),
                "type": v_type,
                "layer": v_layer,
            },
            "edge": {
                "type": edge_attrs.get("graph_type"),
                "properties": edge_attrs.get("properties", {}),
            },
        }

        # Add specific analysis based on violation type
        violation_type = edge_attrs.get("properties", {}).get("violation_type")
        if violation_type == "gravity_import":
            context["analysis"] = {
                "type": "Layer Gravity Violation",
                "issue": f"Import from {u_layer} to {v_layer} violates architectural gravity",
                "recommendation": "Consider moving the dependency to a lower layer or using a gateway",
            }
        elif violation_type == "forbidden_transition":
            context["analysis"] = {
                "type": "Forbidden Layer Transition",
                "issue": f"Direct dependency from {u_layer} to {v_layer} is not allowed",
                "recommendation": "Use an intermediate layer or approved gateway pattern",
            }
        else:
            context["analysis"] = {
                "type": "General Violation",
                "issue": f"Violation of type: {violation_type}",
                "recommendation": "Review architectural guidelines for this violation type",
            }

        return context

    def top_changed_neighborhoods(
        self, from_graph: nx.Graph, to_graph: nx.Graph, top_n: int = 10
    ) -> Dict[str, Any]:
        """Find top changed neighborhoods between two runs.

        Args:
            from_graph: Previous graph snapshot
            to_graph: Current graph snapshot
            top_n: Number of top neighborhoods to return

        Returns:
            Dictionary with top changed neighborhoods
        """
        # Find all nodes that exist in both graphs
        common_nodes = set(from_graph.nodes()) & set(to_graph.nodes())

        neighborhood_changes = []

        for node in common_nodes:
            # Get neighborhoods in both graphs
            from_neighbors = set(from_graph.neighbors(node))
            to_neighbors = set(to_graph.neighbors(node))

            # Calculate changes
            added_neighbors = to_neighbors - from_neighbors
            removed_neighbors = from_neighbors - to_neighbors
            common_neighbors = from_neighbors & to_neighbors

            # Calculate change score
            change_score = len(added_neighbors) + len(removed_neighbors)

            if change_score > 0:
                # Analyze the types of changes
                added_types = {}
                for neighbor in added_neighbors:
                    neighbor_type = to_graph.nodes[neighbor].get("graph_type", "Unknown")
                    added_types[neighbor_type] = added_types.get(neighbor_type, 0) + 1

                removed_types = {}
                for neighbor in removed_neighbors:
                    neighbor_type = from_graph.nodes[neighbor].get("graph_type", "Unknown")
                    removed_types[neighbor_type] = removed_types.get(neighbor_type, 0) + 1

                neighborhood_changes.append(
                    {
                        "node": node,
                        "node_name": to_graph.nodes[node].get("name"),
                        "node_type": to_graph.nodes[node].get("graph_type"),
                        "change_score": change_score,
                        "added_neighbors": {
                            "count": len(added_neighbors),
                            "nodes": list(added_neighbors),
                            "types": added_types,
                        },
                        "removed_neighbors": {
                            "count": len(removed_neighbors),
                            "nodes": list(removed_neighbors),
                            "types": removed_types,
                        },
                        "common_neighbors": {
                            "count": len(common_neighbors),
                            "nodes": list(common_neighbors),
                        },
                    }
                )

        # Sort by change score and return top N
        neighborhood_changes.sort(key=lambda x: x["change_score"], reverse=True)
        top_changes = neighborhood_changes[:top_n]

        return {
            "total_nodes_analyzed": len(common_nodes),
            "nodes_with_changes": len(neighborhood_changes),
            "top_neighborhoods": top_changes,
            "summary": {
                "highest_change_score": top_changes[0]["change_score"] if top_changes else 0,
                "average_change_score": sum(c["change_score"] for c in neighborhood_changes)
                / len(neighborhood_changes)
                if neighborhood_changes
                else 0,
            },
        }
