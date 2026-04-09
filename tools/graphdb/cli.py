"""GraphDB CLI - Command-line interface for graph projection and queries.

This module provides the main CLI interface for the GraphDB enhancement,
including projection, query execution, and analysis commands.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

import networkx as nx

from .project_graph import project_graph
from .projection import GraphProjector
from .queries.analyst import AnalystQueries
from .queries.blast_radius import BlastRadiusQueries
from .queries.historical import HistoricalQueries
from .queries.structural import StructuralQueries
from .snapshot import SnapshotManager


def cmd_project(args: argparse.Namespace) -> int:
    """Handle project command."""
    try:
        graph, _metadata = project_graph(
            sqlite_path=args.sqlite,
            output_dir=args.output_dir,
            run_id=args.run_id,
        )

        print(f"✓ Projection complete: {_metadata.node_count} nodes, {_metadata.edge_count} edges")
        print(f"  Commit: {_metadata.commit_sha}")
        print(f"  Run ID: {_metadata.run_id}")

        return 0
    except (FileNotFoundError, RuntimeError, ValueError) as e:
        print(f"✗ Projection failed: {e}", file=sys.stderr)
        return 1


def cmd_query(args: argparse.Namespace) -> int:
    """Handle query command."""
    try:
        # Load the graph
        if args.snapshot:
            # Load from snapshot
            snapshot_manager = SnapshotManager(args.output_dir)
            graph, _metadata = snapshot_manager.load_snapshot(args.snapshot)
        else:
            # Project from SQLite
            graph, _metadata = project_graph(
                sqlite_path=args.sqlite,
                output_dir=args.output_dir,
                run_id=args.run_id,
            )

        # Initialize query packs
        structural = StructuralQueries(graph)
        blast_radius = BlastRadiusQueries(graph)
        analyst = AnalystQueries(graph)

        results: Dict[str, Any] = {}

        # Execute requested queries
        if args.query_type == "structural":
            if args.gravity_violations:
                results["gravity_violations"] = structural.gravity_import_violations()
            if args.illegal_reach:
                results["illegal_layer_reach"] = structural.illegal_layer_reach()
            if args.l2_conformance:
                results["l2_lifecycle_conformance"] = structural.l2_lifecycle_conformance()
            if args.uwg_conformance:
                results["uwg_durable_write_conformance"] = structural.uwg_durable_write_conformance()
            if args.chokepoint_conformance:
                results["capability_tool_provider_chokepoint_conformance"] = (
                    structural.capability_tool_provider_chokepoint_conformance()
                )
            if args.spine_completeness:
                results["agentic_spine_completeness"] = structural.agentic_spine_completeness()
            if args.role_purity:
                results["l0_l1_l6_role_purity"] = structural.l0_l1_l6_role_purity()
            if args.grounding_separation:
                results["grounding_contract_separation"] = structural.grounding_contract_separation()
            if args.trace_coverage:
                results["trace_replay_eval_coverage"] = structural.trace_replay_eval_coverage()

        elif args.query_type == "blast-radius":
            if args.transitive_dependents:
                if not args.node:
                    print("✗ --node required for transitive dependents query", file=sys.stderr)
                    return 1
                results["transitive_dependents"] = blast_radius.transitive_dependents(
                    args.node, max_depth=args.max_depth
                )
            if args.illegal_path:
                if not args.source or not args.target:
                    print("✗ --source and --target required for illegal path query", file=sys.stderr)
                    return 1
                results["shortest_illegal_path"] = blast_radius.shortest_illegal_path(
                    args.source, args.target
                )
            if args.bypass_paths:
                if not args.gateway:
                    print("✗ --gateway required for bypass paths query", file=sys.stderr)
                    return 1
                results["bypass_paths"] = blast_radius.bypass_paths(args.gateway)
            if args.impact_analysis:
                if not args.node:
                    print("✗ --node required for impact analysis query", file=sys.stderr)
                    return 1
                results["impact_analysis"] = blast_radius.impact_analysis(args.node)
            if args.hubs:
                results["high_fan_in_out_hubs"] = blast_radius.high_fan_in_out_hubs(
                    min_connections=args.min_connections
                )

        elif args.query_type == "analyst":
            if args.layer:
                results["layer_subgraph"] = analyst.extract_subgraph_by_layer(args.layer)
            if args.agent:
                results["agent_subgraph"] = analyst.extract_subgraph_by_agent(args.agent)
            if args.gateway:
                results["gateway_subgraph"] = analyst.extract_subgraph_by_gateway(args.gateway)
            if args.provider:
                results["provider_subgraph"] = analyst.extract_subgraph_by_provider(args.provider)
            if args.violation_explanation:
                if not args.node:
                    print("✗ --node required for violation explanation query", file=sys.stderr)
                    return 1
                results["violation_explanation"] = analyst.violation_explanation_paths(args.node)

        # Output results
        if args.output_format == "json":
            print(json.dumps(results, indent=2))
        else:
            # Pretty print results
            for query_name, result in results.items():
                print(f"\n=== {query_name} ===")
                if isinstance(result, list):
                    print(f"Found {len(result)} items")
                    for item in result[:5]:  # Show first 5 items
                        print(f"  - {item}")
                    if len(result) > 5:
                        print(f"  ... and {len(result) - 5} more")
                elif isinstance(result, dict):
                    for key, value in result.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"  {result}")

        return 0
    except (FileNotFoundError, RuntimeError, ValueError) as e:
        print(f"✗ Query failed: {e}", file=sys.stderr)
        return 1


def cmd_diff(args: argparse.Namespace) -> int:
    """Handle diff command."""
    try:
        snapshot_manager = SnapshotManager(args.output_dir)

        if not snapshot_manager.snapshot_exists(args.from_commit) or not snapshot_manager.snapshot_exists(
            args.to_commit
        ):
            print("✗ One or both snapshots not found", file=sys.stderr)
            return 1

        historical = HistoricalQueries(snapshot_manager)

        results: Dict[str, Any] = {}
        if args.new_violations:
            results["new_forbidden_edges"] = historical.new_forbidden_edges(args.from_commit, args.to_commit)
        if args.new_writes:
            results["new_direct_writes"] = historical.new_direct_writes(args.from_commit, args.to_commit)
        if args.orphaned_interfaces:
            results["orphaned_interfaces"] = historical.orphaned_interfaces(args.from_commit, args.to_commit)
        if args.l2_regressions:
            results["l2_regressions"] = historical.new_l2_phase_coverage_regressions(
                args.from_commit, args.to_commit
            )
        if args.new_call_surfaces:
            results["new_call_surfaces"] = historical.new_tool_provider_call_surfaces(
                args.from_commit, args.to_commit
            )
        if args.new_cross_layer:
            results["new_cross_layer_dependencies"] = historical.new_cross_layer_dependencies(
                args.from_commit, args.to_commit
            )
        if args.full_regression:
            results["full_regression_analysis"] = historical.regression_analysis(
                args.from_commit, args.to_commit
            )

        # Output results
        if args.output_format == "json":
            print(json.dumps(results, indent=2))
        else:
            # Pretty print results
            for query_name, result in results.items():
                print(f"\n=== {query_name} ===")
                if isinstance(result, list):
                    print(f"Found {len(result)} items")
                    for item in result[:5]:  # Show first 5 items
                        print(f"  - {item}")
                    if len(result) > 5:
                        print(f"  ... and {len(result) - 5} more")
                elif isinstance(result, dict):
                    for key, value in result.items():
                        if key == "summary":
                            print(f"  {key}:")
                            for subkey, subvalue in value.items():
                                print(f"    {subkey}: {subvalue}")
                        else:
                            print(f"  {key}: {value}")
                else:
                    print(f"  {result}")

        return 0
    except (FileNotFoundError, RuntimeError, ValueError) as e:
        print(f"✗ Diff failed: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Handle list command."""
    try:
        snapshot_manager = SnapshotManager(args.output_dir)
        snapshots = snapshot_manager.list_snapshots()

        if not snapshots:
            print("No snapshots found")
            return 0

        print(f"Found {len(snapshots)} snapshots:")
        print(f"{'Commit SHA':<12} {'Timestamp':<20} {'Run ID':<20} {'Nodes':<8} {'Edges':<8}")
        print("-" * 76)

        for commit_sha, info in sorted(snapshots.items(), key=lambda x: x[1]["timestamp"], reverse=True):
            timestamp = info["timestamp"][:19]  # Remove microseconds and Z
            run_id = info["run_id"][:18]  # Truncate if too long
            nodes = info["node_count"]
            edges = info["edge_count"]
            print(f"{commit_sha[:12]:<12} {timestamp:<20} {run_id:<20} {nodes:<8} {edges:<8}")

        return 0
    except (FileNotFoundError, RuntimeError) as e:
        print(f"✗ List failed: {e}", file=sys.stderr)
        return 1


def cmd_stats(args: argparse.Namespace) -> int:
    """Handle stats command."""
    try:
        if args.snapshot:
            # Load from snapshot
            snapshot_manager = SnapshotManager(args.output_dir)
            graph, metadata = snapshot_manager.load_snapshot(args.snapshot)
        else:
            # Project from SQLite
            projector = GraphProjector(args.sqlite)
            stats = projector.get_graph_statistics()

            print("=== ADG SQLite Statistics ===")
            print(f"Estimated nodes: {stats['total_nodes']}")
            print(f"Estimated edges: {stats['total_edges']}")
            print(f"Density: {stats['density']:.4f}")
            return 0

        # Full graph statistics
        print(f"=== Graph Statistics for {metadata.commit_sha[:8]} ===")
        print(f"Nodes: {graph.number_of_nodes()}")
        print(f"Edges: {graph.number_of_edges()}")
        print(f"Density: {nx.density(graph):.4f}")

        # Node type distribution
        node_types: Dict[str, int] = {}
        for _, attrs in graph.nodes(data=True):
            node_type = attrs.get("graph_type", "Unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1

        print(f"\nNode Types ({len(node_types)} types):")
        for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {node_type}: {count}")

        # Edge type distribution
        edge_types: Dict[str, int] = {}
        for _, _, attrs in graph.edges(data=True):
            edge_type = attrs.get("graph_type", "Unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

        print(f"\nEdge Types ({len(edge_types)} types):")
        for edge_type, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {edge_type}: {count}")

        return 0
    except (FileNotFoundError, RuntimeError, ValueError) as e:
        print(f"✗ Stats failed: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="GraphDB Enhancement - ADG Graph Projection and Analysis")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/graphdb"),
        help="Output directory for graph projections",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format for query results",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Project command
    project_parser = subparsers.add_parser("project", help="Project ADG to graph")
    project_parser.add_argument("sqlite", type=Path, help="ADG SQLite file")
    project_parser.add_argument("--run-id", type=str, help="Run identifier")

    # Query command
    query_parser = subparsers.add_parser("query", help="Run graph queries")
    query_parser.add_argument("sqlite", type=Path, help="ADG SQLite file")
    query_parser.add_argument("--snapshot", type=str, help="Load from snapshot instead of SQLite")
    query_parser.add_argument("--run-id", type=str, help="Run identifier")
    query_parser.add_argument(
        "query_type", choices=["structural", "blast-radius", "analyst"], help="Query type"
    )

    # Structural query options
    query_parser.add_argument("--gravity-violations", action="store_true")
    query_parser.add_argument("--illegal-reach", action="store_true")
    query_parser.add_argument("--l2-conformance", action="store_true")
    query_parser.add_argument("--uwg-conformance", action="store_true")
    query_parser.add_argument("--chokepoint-conformance", action="store_true")
    query_parser.add_argument("--spine-completeness", action="store_true")
    query_parser.add_argument("--role-purity", action="store_true")
    query_parser.add_argument("--grounding-separation", action="store_true")
    query_parser.add_argument("--trace-coverage", action="store_true")

    # Blast-radius query options
    query_parser.add_argument("--transitive-dependents", action="store_true")
    query_parser.add_argument("--illegal-path", action="store_true")
    query_parser.add_argument("--bypass-paths", action="store_true")
    query_parser.add_argument("--impact-analysis", action="store_true")
    query_parser.add_argument("--hubs", action="store_true")
    query_parser.add_argument("--node", type=str, help="Node ID for node-specific queries")
    query_parser.add_argument("--source", type=str, help="Source node for path queries")
    query_parser.add_argument("--target", type=str, help="Target node for path queries")
    query_parser.add_argument("--gateway", type=str, help="Gateway node for gateway queries")
    query_parser.add_argument("--max-depth", type=int, default=10, help="Max depth for dependency analysis")
    query_parser.add_argument(
        "--min-connections", type=int, default=10, help="Min connections for hub analysis"
    )

    # Analyst query options
    query_parser.add_argument("--layer", type=str, help="Layer name for layer subgraph")
    query_parser.add_argument("--agent", type=str, help="Agent name for agent subgraph")
    query_parser.add_argument("--gateway-subgraph", type=str, help="Gateway name for gateway subgraph")
    query_parser.add_argument("--provider", type=str, help="Provider name for provider subgraph")
    query_parser.add_argument("--violation-explanation", action="store_true")

    # Diff command
    diff_parser = subparsers.add_parser("diff", help="Compare snapshots")
    diff_parser.add_argument("from_commit", type=str, help="Source commit SHA")
    diff_parser.add_argument("to_commit", type=str, help="Target commit SHA")
    diff_parser.add_argument("--new-violations", action="store_true")
    diff_parser.add_argument("--new-writes", action="store_true")
    diff_parser.add_argument("--orphaned-interfaces", action="store_true")
    diff_parser.add_argument("--l2-regressions", action="store_true")
    diff_parser.add_argument("--new-call-surfaces", action="store_true")
    diff_parser.add_argument("--new-cross-layer", action="store_true")
    diff_parser.add_argument("--full-regression", action="store_true")

    # List command
    list_parser = subparsers.add_parser("list", help="List snapshots")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show graph statistics")
    stats_parser.add_argument("sqlite", type=Path, nargs="?", help="ADG SQLite file")
    stats_parser.add_argument("--snapshot", type=str, help="Load from snapshot instead of SQLite")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate command handler
    if args.command == "project":
        return cmd_project(args)
    elif args.command == "query":
        return cmd_query(args)
    elif args.command == "diff":
        return cmd_diff(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "stats":
        return cmd_stats(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
