"""NetworkX graph analysis scripts for ADG.

Provides advanced graph algorithms that write back to materialized views:
1. PageRank centrality analysis
2. Betweenness centrality analysis
3. Community detection (Louvain method)
4. Bridge detection (articulation points)
5. Shortest path analysis between critical nodes

All scripts load from ADG SQLite, run NetworkX algorithms, and write results
back to mv_* tables for consumption by agents and MCP tools.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import networkx as nx

# Add repo root for imports
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.generate.core import _get_latest_adg_path


def _validate_sqlite_path(sqlite_path: Path) -> Path:
    sqlite_path = sqlite_path.expanduser().resolve()
    if not sqlite_path.exists():
        raise FileNotFoundError(f"ADG SQLite not found: {sqlite_path}")
    if not sqlite_path.is_file():
        raise ValueError(f"ADG SQLite path is not a file: {sqlite_path}")
    return sqlite_path


def _connect_sqlite(sqlite_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(_validate_sqlite_path(sqlite_path)), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _snapshot_id_expr() -> str:
    return "(SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1)"


def _build_networkx_graph(sqlite_path: Path, relation_types: List[str] = None) -> nx.DiGraph:
    """Build NetworkX directed graph from ADG SQLite.

    Args:
        sqlite_path: Path to ADG SQLite file
        relation_types: List of edge types to include (default: ['imports', 'calls'])

    Returns:
        NetworkX DiGraph with nodes having layer, file_path, and symbol attributes
    """
    if relation_types is None:
        relation_types = ["imports", "calls"]

    conn = _connect_sqlite(sqlite_path)
    cur = conn.cursor()

    # Build directed graph
    G = nx.DiGraph()

    # Add nodes with attributes
    cur.execute("""
        SELECT id, resolved_path, layer, entity_type, symbol_name, symbol_type
        FROM nodes
        WHERE resolved_path IS NOT NULL
        AND entity_type IN ('module', 'symbol')
    """)

    for row in cur.fetchall():
        node_id, file_path, layer, entity_type, symbol_name, symbol_type = row
        G.add_node(
            node_id,
            file_path=file_path,
            layer=layer,
            entity_type=entity_type,
            symbol_name=symbol_name,
            symbol_type=symbol_type,
        )

    # Add edges for specified relation types
    rel_type_placeholders = ",".join(["?" for _ in relation_types])
    cur.execute(
        f"""
        SELECT src_id, dst_id, relation_type
        FROM edges
        WHERE relation_type IN ({rel_type_placeholders})
    """,
        relation_types,
    )

    for src_id, dst_id, relation_type in cur.fetchall():
        if src_id in G.nodes and dst_id in G.nodes:
            G.add_edge(src_id, dst_id, relation_type=relation_type)

    conn.close()
    return G


def analyze_pagerank(sqlite_path: Path, alpha: float = 0.85) -> Dict[int, float]:
    """Calculate PageRank centrality and write to mv_pagerank_centrality.

    Args:
        sqlite_path: Path to ADG SQLite file
        alpha: Damping factor for PageRank (default: 0.85)

    Returns:
        Dict mapping node_id -> pagerank_score
    """
    print("Building NetworkX graph for PageRank analysis...")
    G = _build_networkx_graph(sqlite_path)

    print(
        f"Calculating PageRank (alpha={alpha}) on graph with {G.number_of_nodes()} nodes, {G.number_of_edges()} edges..."
    )
    pagerank_scores = nx.pagerank(G, alpha=alpha, weight="relation_type")

    # Write results to materialized view
    conn = _connect_sqlite(sqlite_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS mv_pagerank_centrality")
    cur.execute(
        f"""
        CREATE TABLE mv_pagerank_centrality AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            node_id,
            pagerank_score,
            file_path,
            layer,
            entity_type,
            symbol_name,
            symbol_type,
            -- Percentile rank within layer
            PERCENT_RANK() OVER (PARTITION BY layer ORDER BY pagerank_score DESC) AS layer_percentile,
            -- Significance tier
            CASE
                WHEN pagerank_score > 0.01 THEN 'HIGH'
                WHEN pagerank_score > 0.005 THEN 'MEDIUM'
                WHEN pagerank_score > 0.001 THEN 'LOW'
                ELSE 'MINIMAL'
            END AS significance_tier
        FROM (
            SELECT
                n.id AS node_id,
                pr.pagerank_score,
                n.resolved_path AS file_path,
                n.layer AS layer,
                n.entity_type AS entity_type,
                n.symbol_name AS symbol_name,
                n.symbol_type AS symbol_type
            FROM nodes n
            JOIN (
                SELECT CAST(node_id AS INTEGER) AS node_id, value AS pagerank_score
                FROM json_each(?)
            ) pr ON n.id = pr.node_id
            WHERE n.resolved_path IS NOT NULL
        )
    """,
        (str(pagerank_scores).replace("'", '"'),),
    )

    conn.commit()
    conn.close()

    print(f"PageRank analysis complete. Wrote {len(pagerank_scores)} scores to mv_pagerank_centrality")
    return pagerank_scores


def analyze_betweenness(sqlite_path: Path, k: int = None) -> Dict[int, float]:
    """Calculate betweenness centrality and write to mv_betweenness_centrality.

    Args:
        sqlite_path: Path to ADG SQLite file
        k: Number of nodes to sample for approximation (None for exact)

    Returns:
        Dict mapping node_id -> betweenness_score
    """
    print("Building NetworkX graph for betweenness analysis...")
    G = _build_networkx_graph(sqlite_path)

    # Use approximation for large graphs
    if k is None and G.number_of_nodes() > 1000:
        k = min(1000, G.number_of_nodes() // 10)
        print(f"Using approximate betweenness with k={k}")

    print(f"Calculating betweenness centrality...")
    betweenness_scores = nx.betweenness_centrality(G, k=k, normalized=True)

    # Write results to materialized view
    conn = _connect_sqlite(sqlite_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS mv_betweenness_centrality")
    cur.execute(
        f"""
        CREATE TABLE mv_betweenness_centrality AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            node_id,
            betweenness_score,
            file_path,
            layer,
            entity_type,
            symbol_name,
            symbol_type,
            -- Bridge potential (high betweenness in critical layers)
            CASE
                WHEN betweenness_score > 0.1 AND layer IN ('L0', 'L3', 'L5') THEN 'CRITICAL_BRIDGE'
                WHEN betweenness_score > 0.05 THEN 'SIGNIFICANT_BRIDGE'
                WHEN betweenness_score > 0.01 THEN 'MINOR_BRIDGE'
                ELSE 'LOW_BRIDGE'
            END AS bridge_potential
        FROM (
            SELECT
                n.id AS node_id,
                bc.betweenness_score,
                n.resolved_path AS file_path,
                n.layer AS layer,
                n.entity_type AS entity_type,
                n.symbol_name AS symbol_name,
                n.symbol_type AS symbol_type
            FROM nodes n
            JOIN (
                SELECT CAST(node_id AS INTEGER) AS node_id, value AS betweenness_score
                FROM json_each(?)
            ) bc ON n.id = bc.node_id
            WHERE n.resolved_path IS NOT NULL
        )
    """,
        (str(betweenness_scores).replace("'", '"'),),
    )

    conn.commit()
    conn.close()

    print(
        f"Betweenness analysis complete. Wrote {len(betweenness_scores)} scores to mv_betweenness_centrality"
    )
    return betweenness_scores


def analyze_communities(sqlite_path: Path, resolution: float = 1.0) -> Dict[int, int]:
    """Detect communities using Louvain method and write to mv_communities.

    Args:
        sqlite_path: Path to ADG SQLite file
        resolution: Community resolution parameter (higher = more communities)

    Returns:
        Dict mapping node_id -> community_id
    """
    try:
        import community as community_louvain
    except ImportError:
        print("python-louvain not installed. Install with: pip install python-louvain")
        return {}

    print("Building NetworkX graph for community detection...")
    G = _build_networkx_graph(sqlite_path)

    # Convert to undirected for community detection
    G_undirected = G.to_undirected()

    print(f"Detecting communities with resolution={resolution}...")
    partition = community_louvain.best_partition(G_undirected, resolution=resolution)

    # Write results to materialized view
    conn = _connect_sqlite(sqlite_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS mv_communities")
    cur.execute(
        f"""
        CREATE TABLE mv_communities AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            node_id,
            community_id,
            file_path,
            layer,
            entity_type,
            symbol_name,
            symbol_type,
            -- Community size
            COUNT(*) OVER (PARTITION BY community_id) AS community_size,
            -- Community diversity (layers represented)
            COUNT(DISTINCT layer) OVER (PARTITION BY community_id) AS layer_diversity,
            -- Cross-layer community flag
            CASE WHEN COUNT(DISTINCT layer) OVER (PARTITION BY community_id) > 1 THEN 1 ELSE 0 END AS is_cross_layer
        FROM (
            SELECT
                n.id AS node_id,
                comm.community_id,
                n.resolved_path AS file_path,
                n.layer AS layer,
                n.entity_type AS entity_type,
                n.symbol_name AS symbol_name,
                n.symbol_type AS symbol_type
            FROM nodes n
            JOIN (
                SELECT CAST(node_id AS INTEGER) AS node_id, value AS community_id
                FROM json_each(?)
            ) comm ON n.id = comm.node_id
            WHERE n.resolved_path IS NOT NULL
        )
    """,
        (str(partition).replace("'", '"'),),
    )

    conn.commit()
    conn.close()

    num_communities = len(set(partition.values()))
    print(f"Community detection complete. Found {num_communities} communities, wrote to mv_communities")
    return partition


def analyze_bridges(sqlite_path: Path) -> List[int]:
    """Find articulation points (bridges) and write to mv_articulation_points.

    Args:
        sqlite_path: Path to ADG SQLite file

    Returns:
        List of node_ids that are articulation points
    """
    print("Building NetworkX graph for bridge analysis...")
    G = _build_networkx_graph(sqlite_path)

    # Convert to undirected for articulation point detection
    G_undirected = G.to_undirected()

    print(f"Finding articulation points...")
    articulation_points = list(nx.articulation_points(G_undirected))

    # Write results to materialized view
    conn = _connect_sqlite(sqlite_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS mv_articulation_points")
    cur.execute(
        f"""
        CREATE TABLE mv_articulation_points AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            node_id,
            file_path,
            layer,
            entity_type,
            symbol_name,
            symbol_type,
            -- Criticality based on layer
            CASE
                WHEN layer IN ('L0', 'L5') THEN 'CRITICAL_ARTICULATION'
                WHEN layer IN ('L3', 'L4') THEN 'IMPORTANT_ARTICULATION'
                ELSE 'MODERATE_ARTICULATION'
            END AS articulation_criticality
        FROM nodes n
        WHERE n.id IN ({",".join(["?" for _ in articulation_points])})
        AND n.resolved_path IS NOT NULL
    """,
        articulation_points,
    )

    conn.commit()
    conn.close()

    print(
        f"Bridge analysis complete. Found {len(articulation_points)} articulation points, wrote to mv_articulation_points"
    )
    return articulation_points


def run_all_analyses(sqlite_path: Path = None) -> Dict[str, Any]:
    """Run all NetworkX analyses and return summary.

    Args:
        sqlite_path: Path to ADG SQLite file (auto-detected if None)

    Returns:
        Dict with analysis results summary
    """
    if sqlite_path is None:
        sqlite_path = _get_latest_adg_path()

    if not sqlite_path:
        raise ValueError("No ADG SQLite file found")

    print(f"Running NetworkX analyses on: {sqlite_path}")

    results = {}

    # Run each analysis
    results["pagerank"] = analyze_pagerank(sqlite_path)
    results["betweenness"] = analyze_betweenness(sqlite_path)
    results["communities"] = analyze_communities(sqlite_path)
    results["articulation_points"] = analyze_bridges(sqlite_path)

    # Summary
    summary = {
        "sqlite_path": str(sqlite_path),
        "analyses_run": list(results.keys()),
        "pagerank_nodes": len(results["pagerank"]),
        "betweenness_nodes": len(results["betweenness"]),
        "communities_found": len(set(results["communities"].values())),
        "articulation_points": len(results["articulation_points"]),
        "tables_created": [
            "mv_pagerank_centrality",
            "mv_betweenness_centrality",
            "mv_communities",
            "mv_articulation_points",
        ],
    }

    print("\nNetworkX Analysis Summary:")
    for key, value in summary.items():
        if key != "sqlite_path":
            print(f"  {key}: {value}")

    return summary


if __name__ == "__main__":
    # Run all analyses on latest snapshot
    summary = run_all_analyses()
    print(f"\nAll analyses complete! Tables created for agent consumption.")
