"""Historical Diff Queries - Query pack for analyzing graph changes over time.

This module provides queries to compare graph snapshots and analyze
historical changes, regressions, and evolution patterns.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

import networkx as nx

from tools.graphdb.snapshot import SnapshotManager


class HistoricalQueries:
    """Historical diff query pack for ADG graph analysis."""

    def __init__(self, snapshot_manager: SnapshotManager):
        """Initialize with a snapshot manager.

        Args:
            snapshot_manager: SnapshotManager instance for loading snapshots
        """
        self.snapshot_manager = snapshot_manager

    def new_forbidden_edges(self, from_commit: str, to_commit: str) -> List[Dict[str, Any]]:
        """Find newly introduced policy violations.

        Args:
            from_commit: Source commit SHA
            to_commit: Target commit SHA

        Returns:
            List of newly introduced forbidden edges
        """
        from_graph, _ = self.snapshot_manager.load_snapshot(from_commit)
        to_graph, _ = self.snapshot_manager.load_snapshot(to_commit)

        new_violations = []

        # Find all violation edges in the new graph
        for u, v, attrs in to_graph.edges(data=True):
            if attrs.get("graph_type") == "VIOLATES":
                # Check if this violation existed in the old graph
                if not from_graph.has_edge(u, v):
                    # New violation edge
                    new_violations.append(
                        {
                            "type": "new_violation_edge",
                            "from_node": u,
                            "to_node": v,
                            "violation_type": attrs.get("properties", {}).get("violation_type"),
                            "severity": attrs.get("properties", {}).get("severity"),
                            "description": attrs.get("properties", {}).get("description"),
                            "introduced_in": to_commit,
                        }
                    )
                else:
                    # Edge existed, check if violation status changed
                    old_attrs = from_graph.edges[u, v]
                    if old_attrs.get("graph_type") != "VIOLATES":
                        # Edge became a violation
                        new_violations.append(
                            {
                                "type": "edge_became_violation",
                                "from_node": u,
                                "to_node": v,
                                "old_type": old_attrs.get("graph_type"),
                                "violation_type": attrs.get("properties", {}).get("violation_type"),
                                "severity": attrs.get("properties", {}).get("severity"),
                                "description": attrs.get("properties", {}).get("description"),
                                "introduced_in": to_commit,
                            }
                        )

        return new_violations

    def new_direct_writes(self, from_commit: str, to_commit: str) -> List[Dict[str, Any]]:
        """Find new writes that bypass gateways.

        Args:
            from_commit: Source commit SHA
            to_commit: Target commit SHA

        Returns:
            List of new direct writes bypassing gateways
        """
        from_graph, _ = self.snapshot_manager.load_snapshot(from_commit)
        to_graph, _ = self.snapshot_manager.load_snapshot(to_commit)

        new_direct_writes = []

        # Find all write edges in the new graph
        for u, v, attrs in to_graph.edges(data=True):
            if attrs.get("graph_type") in ["WRITES_TO", "WRITES_THROUGH"]:
                # Check if this is a direct write (not through gateway)
                v_attrs = to_graph.nodes[v]
                target_is_gateway = v_attrs.get("graph_type") == "Gateway"

                if not target_is_gateway and attrs.get("graph_type") == "WRITES_TO":
                    # This is a direct write
                    if not from_graph.has_edge(u, v):
                        # New direct write
                        new_direct_writes.append(
                            {
                                "type": "new_direct_write",
                                "from_node": u,
                                "to_node": v,
                                "target_type": v_attrs.get("graph_type"),
                                "line_number": attrs.get("properties", {}).get("line_number"),
                                "write_type": attrs.get("properties", {}).get("write_type"),
                                "introduced_in": to_commit,
                            }
                        )

        return new_direct_writes

    def orphaned_interfaces(self, from_commit: str, to_commit: str) -> List[Dict[str, Any]]:
        """Find interfaces that lost all dependents.

        Args:
            from_commit: Source commit SHA
            to_commit: Target commit SHA

        Returns:
            List of orphaned interfaces
        """
        from_graph, _ = self.snapshot_manager.load_snapshot(from_commit)
        to_graph, _ = self.snapshot_manager.load_snapshot(to_commit)

        orphaned_interfaces = []

        # Find all nodes that had dependents in the old graph
        for node in from_graph.nodes():
            old_dependents = list(from_graph.predecessors(node))
            new_dependents = list(to_graph.predecessors(node)) if node in to_graph else []

            if len(old_dependents) > 0 and len(new_dependents) == 0:
                # Node became orphaned
                node_attrs = from_graph.nodes[node]
                orphaned_interfaces.append(
                    {
                        "type": "orphaned_interface",
                        "node": node,
                        "node_type": node_attrs.get("graph_type"),
                        "layer": node_attrs.get("properties", {}).get("layer"),
                        "old_dependent_count": len(old_dependents),
                        "lost_in_commit": to_commit,
                        "was_removed": node not in to_graph,
                    }
                )

        return orphaned_interfaces

    def new_l2_phase_coverage_regressions(self, from_commit: str, to_commit: str) -> Dict[str, Any]:
        """Find new L2 phase coverage regressions.

        Args:
            from_commit: Source commit SHA
            to_commit: Target commit SHA

        Returns:
            Dictionary with L2 phase regression analysis
        """
        from_graph, _ = self.snapshot_manager.load_snapshot(from_commit)
        to_graph, _ = self.snapshot_manager.load_snapshot(to_commit)

        # Define expected L2 sub-phases
        expected_subphases = {
            "execution": ["execute", "run", "process"],
            "orchestration": ["orchestrate", "coordinate", "manage"],
            "validation": ["validate", "verify", "check"],
            "error_handling": ["handle", "catch", "recover"],
        }

        def analyze_l2_coverage(graph: nx.Graph) -> Dict[str, Any]:
            l2_modules = [
                node
                for node, attrs in graph.nodes(data=True)
                if attrs.get("properties", {}).get("layer") == "L2"
            ]

            phase_coverage = {phase: 0 for phase in expected_subphases}

            for module in l2_modules:
                module_attrs = graph.nodes[module]
                module_name = module_attrs.get("name", "")

                for phase, patterns in expected_subphases.items():
                    if any(pattern in module_name.lower() for pattern in patterns):
                        phase_coverage[phase] += 1
                        break

            return {
                "total_l2_modules": len(l2_modules),
                "phase_coverage": phase_coverage,
                "coverage_rate": sum(phase_coverage.values()) / len(l2_modules) if l2_modules else 0.0,
            }

        from_analysis = analyze_l2_coverage(from_graph)
        to_analysis = analyze_l2_coverage(to_graph)

        regressions = []
        for phase in expected_subphases:
            from_count = from_analysis["phase_coverage"][phase]
            to_count = to_analysis["phase_coverage"][phase]

            if to_count < from_count:
                regressions.append(
                    {
                        "phase": phase,
                        "from_count": from_count,
                        "to_count": to_count,
                        "regression": from_count - to_count,
                    }
                )

        return {
            "from_commit": from_commit,
            "to_commit": to_commit,
            "from_analysis": from_analysis,
            "to_analysis": to_analysis,
            "regressions": regressions,
            "has_regressions": len(regressions) > 0,
        }

    def new_tool_provider_call_surfaces(self, from_commit: str, to_commit: str) -> List[Dict[str, Any]]:
        """Find new tool/provider call surfaces.

        Args:
            from_commit: Source commit SHA
            to_commit: Target commit SHA

        Returns:
            List of new tool/provider call surfaces
        """
        from_graph, _ = self.snapshot_manager.load_snapshot(from_commit)
        to_graph, _ = self.snapshot_manager.load_snapshot(to_commit)

        new_call_surfaces = []

        # Find tool/provider invocation edges in new graph
        for u, v, attrs in to_graph.edges(data=True):
            if attrs.get("graph_type") in ["INVOKES_PROVIDER", "INVOKES_TOOL"]:
                v_attrs = to_graph.nodes[v]

                if v_attrs.get("graph_type") in ["Tool", "Provider"]:
                    if not from_graph.has_edge(u, v):
                        # New call surface
                        new_call_surfaces.append(
                            {
                                "type": "new_call_surface",
                                "caller": u,
                                "callee": v,
                                "callee_type": v_attrs.get("graph_type"),
                                "call_type": attrs.get("graph_type"),
                                "call_context": attrs.get("properties", {}).get("call_context"),
                                "introduced_in": to_commit,
                            }
                        )

        return new_call_surfaces

    def new_cross_layer_dependencies(self, from_commit: str, to_commit: str) -> List[Dict[str, Any]]:
        """Find new cross-layer dependencies.

        Args:
            from_commit: Source commit SHA
            to_commit: Target commit SHA

        Returns:
            List of new cross-layer dependencies
        """
        from_graph, _ = self.snapshot_manager.load_snapshot(from_commit)
        to_graph, _ = self.snapshot_manager.load_snapshot(to_commit)

        new_cross_layer_deps = []

        # Find cross-layer edges in new graph
        for u, v, attrs in to_graph.edges(data=True):
            u_attrs = to_graph.nodes[u]
            v_attrs = to_graph.nodes[v]

            u_layer = u_attrs.get("properties", {}).get("layer")
            v_layer = v_attrs.get("properties", {}).get("layer")

            if u_layer and v_layer and u_layer != v_layer:
                # This is a cross-layer dependency
                if not from_graph.has_edge(u, v):
                    # New cross-layer dependency
                    new_cross_layer_deps.append(
                        {
                            "type": "new_cross_layer_dependency",
                            "from_node": u,
                            "to_node": v,
                            "from_layer": u_layer,
                            "to_layer": v_layer,
                            "edge_type": attrs.get("graph_type"),
                            "line_number": attrs.get("properties", {}).get("line_number"),
                            "introduced_in": to_commit,
                        }
                    )

        return new_cross_layer_deps

    def regression_analysis(self, from_commit: str, to_commit: str) -> Dict[str, Any]:
        """Comprehensive regression analysis between snapshots.

        Args:
            from_commit: Source commit SHA
            to_commit: Target commit SHA

        Returns:
            Dictionary with comprehensive regression analysis
        """
        # Load snapshots
        from_graph, from_metadata = self.snapshot_manager.load_snapshot(from_commit)
        to_graph, to_metadata = self.snapshot_manager.load_snapshot(to_commit)

        # Basic metrics comparison
        metrics_comparison = {
            "nodes": {
                "from": from_graph.number_of_nodes(),
                "to": to_graph.number_of_nodes(),
                "change": to_graph.number_of_nodes() - from_graph.number_of_nodes(),
            },
            "edges": {
                "from": from_graph.number_of_edges(),
                "to": to_graph.number_of_edges(),
                "change": to_graph.number_of_edges() - from_graph.number_of_edges(),
            },
        }

        # Run all regression analyses
        new_violations = self.new_forbidden_edges(from_commit, to_commit)
        new_direct_writes = self.new_direct_writes(from_commit, to_commit)
        orphaned_interfaces = self.orphaned_interfaces(from_commit, to_commit)
        l2_regressions = self.new_l2_phase_coverage_regressions(from_commit, to_commit)
        new_call_surfaces = self.new_tool_provider_call_surfaces(from_commit, to_commit)
        new_cross_layer_deps = self.new_cross_layer_dependencies(from_commit, to_commit)

        # Calculate overall regression score
        regression_score = (
            len(new_violations) * 10
            + len(new_direct_writes) * 5
            + len(orphaned_interfaces) * 3
            + len(l2_regressions["regressions"]) * 2
            + len(new_call_surfaces) * 1
            + len(new_cross_layer_deps) * 1
        )

        # Determine regression level
        if regression_score >= 50:
            regression_level = "critical"
        elif regression_score >= 20:
            regression_level = "high"
        elif regression_score >= 10:
            regression_level = "medium"
        elif regression_score > 0:
            regression_level = "low"
        else:
            regression_level = "none"

        return {
            "from_commit": from_commit,
            "to_commit": to_commit,
            "from_timestamp": from_metadata.timestamp,
            "to_timestamp": to_metadata.timestamp,
            "metrics_comparison": metrics_comparison,
            "regression_analysis": {
                "new_violations": new_violations,
                "new_direct_writes": new_direct_writes,
                "orphaned_interfaces": orphaned_interfaces,
                "l2_regressions": l2_regressions,
                "new_call_surfaces": new_call_surfaces,
                "new_cross_layer_dependencies": new_cross_layer_deps,
            },
            "regression_score": regression_score,
            "regression_level": regression_level,
            "summary": {
                "total_issues": (
                    len(new_violations)
                    + len(new_direct_writes)
                    + len(orphaned_interfaces)
                    + len(l2_regressions["regressions"])
                    + len(new_call_surfaces)
                    + len(new_cross_layer_deps)
                ),
                "critical_issues": len(new_violations),
                "high_issues": len(new_direct_writes),
                "medium_issues": len(orphaned_interfaces),
                "low_issues": (
                    len(l2_regressions["regressions"]) + len(new_call_surfaces) + len(new_cross_layer_deps)
                ),
            },
        }
