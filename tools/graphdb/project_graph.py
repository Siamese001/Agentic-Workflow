"""GraphDB Projection Entry Point - Main orchestration for graph projection.

This module provides the main entry point for projecting ADG SQLite artifacts
into NetworkX graphs with full metadata management.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import networkx as nx

from tools.graphdb.projection import GraphProjector
from tools.graphdb.schema import NODE_TYPE_MAPPING, EDGE_TYPE_MAPPING
from tools.graphdb.snapshot import SnapshotManager, SnapshotMetadata


def get_git_info(repo_root: Path) -> tuple[str, str]:
    """Get Git commit SHA and repo state hash.

    Args:
        repo_root: Repository root directory

    Returns:
        Tuple of (commit_sha, repo_state_hash)
    """
    try:
        # Get commit SHA
        commit_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=10,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        commit_sha = ""

    try:
        # Get repo state hash (tree hash)
        repo_state_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD^{tree}"],
            cwd=repo_root,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=10,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        repo_state_hash = ""

    return commit_sha, repo_state_hash


def get_scanner_digest() -> str:
    """Calculate digest of scanner code for reproducibility tracking."""
    scanner_dir = Path(__file__).parent.parent / "agentic_core" / "adg" / "extraction"
    if not scanner_dir.exists():
        return ""

    hasher = hashlib.sha256()
    try:
        for py_file in scanner_dir.rglob("*.py"):
            with open(py_file, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return ""


def generate_run_id() -> str:
    """Generate a unique run identifier."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"graphdb_{timestamp}"


def project_graph(
    sqlite_path: Path,
    output_dir: Path,
    run_id: Optional[str] = None,
) -> tuple[nx.Graph, SnapshotMetadata]:
    """Project ADG SQLite to NetworkX graph with full metadata.

    Args:
        sqlite_path: Path to ADG SQLite file
        output_dir: Output directory for projections
        run_id: Optional run identifier (auto-generated if None)

    Returns:
        Tuple of (graph, metadata)
    """
    # Initialize components
    projector = GraphProjector(sqlite_path)
    snapshot_manager = SnapshotManager(output_dir)

    # Generate run ID if not provided
    if run_id is None:
        run_id = generate_run_id()

    # Get Git information
    repo_root = Path(__file__).parent.parent.parent
    commit_sha, repo_state_hash = get_git_info(repo_root)

    # Get scanner information
    scanner_digest = get_scanner_digest()
    scanner_version = "0.1.0"  # TODO: Get from actual scanner version

    # Get schema version
    schema_version = "1.0"  # TODO: Get from ADG schema

    # Generate timestamp
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Project the graph
    print(f"[GraphDB] Projecting graph from {sqlite_path}")
    graph = projector.project_graph()

    print(f"[GraphDB] Projected {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

    # Validate projection
    warnings = projector.validate_projection(graph)
    if warnings:
        print("[GraphDB] Validation warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    # Create metadata
    metadata = snapshot_manager.create_metadata(
        commit_sha=commit_sha,
        repo_state_hash=repo_state_hash,
        schema_version=schema_version,
        scanner_digest=scanner_digest,
        sqlite_path=sqlite_path,
        run_id=run_id,
        timestamp=timestamp,
        scanner_version=scanner_version,
        graph=graph,
    )

    # Save snapshot
    saved_path = snapshot_manager.save_snapshot(graph, metadata)
    print(f"[GraphDB] Saved snapshot to {saved_path}")

    # Cleanup old snapshots
    deleted = snapshot_manager.cleanup_old_snapshots(keep_count=30)
    if deleted:
        print(f"[GraphDB] Cleaned up {len(deleted)} old snapshots")

    return graph, metadata


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Project ADG SQLite artifacts to NetworkX graphs")
    parser.add_argument(
        "sqlite_path",
        type=Path,
        help="Path to ADG SQLite file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/graphdb"),
        help="Output directory for graph projections",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        help="Run identifier (auto-generated if not provided)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print graph statistics",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the SQLite file, don't project",
    )

    args = parser.parse_args()

    # Validate input
    if not args.sqlite_path.exists():
        print(f"Error: SQLite file not found: {args.sqlite_path}", file=sys.stderr)
        return 1

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        if args.validate_only:
            # Just validate the SQLite file
            projector = GraphProjector(args.sqlite_path)
            stats = projector.get_graph_statistics()
            print("SQLite file validation passed")
            print(f"Estimated graph size: {stats['total_nodes']} nodes, {stats['total_edges']} edges")
            return 0

        # Project the graph
        graph, metadata = project_graph(
            sqlite_path=args.sqlite_path,
            output_dir=args.output_dir,
            run_id=args.run_id,
        )

        # Print statistics if requested
        if args.stats:
            projector = GraphProjector(args.sqlite_path)
            stats = projector.get_graph_statistics()

            print("\n=== Graph Statistics ===")
            print(f"Total nodes: {stats['total_nodes']}")
            print(f"Total edges: {stats['total_edges']}")
            print(f"Density: {stats['density']:.4f}")
            print(f"Average clustering: {stats['average_clustering']:.4f}")
            print(f"Connected components: {stats['num_connected_components']}")
            print(f"Largest component size: {stats['largest_component_size']}")

            print("\n=== Node Types ===")
            for node_type, count in sorted(stats["node_type_counts"].items()):
                print(f"{node_type}: {count}")

            print("\n=== Edge Types ===")
            for edge_type, count in sorted(stats["edge_type_counts"].items()):
                print(f"{edge_type}: {count}")

        print(f"\n=== Projection Complete ===")
        print(f"Commit: {metadata.commit_sha}")
        print(f"Run ID: {metadata.run_id}")
        print(f"Timestamp: {metadata.timestamp}")
        print(f"Nodes: {metadata.node_count}")
        print(f"Edges: {metadata.edge_count}")

        return 0

    except (FileNotFoundError, RuntimeError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
