"""
NetworkX-based graph analysis for ADG.

Provides advanced graph algorithms including centrality measures,
community detection, and path analysis using NetworkX.
"""

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import logging
import sqlite3
import networkx as nx
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class NetworkXAnalyzer:
    """NetworkX-based graph analyzer for ADG."""

    def __init__(self, sqlite_path: str):
        """
        Initialize NetworkX analyzer.

        Args:
            sqlite_path: Path to ADG SQLite database
        """
        self.sqlite_path = Path(sqlite_path)
        if not self.sqlite_path.exists():
            raise ValueError(f"SQLite database not found: {sqlite_path}")

        self.conn = sqlite3.connect(str(self.sqlite_path))
        self.conn.row_factory = sqlite3.Row
        self.graph = None
        self._load_graph()

    def _load_graph(self):
        """Load ADG data into NetworkX graph."""
        try:
            self.graph = nx.DiGraph()

            # Load nodes
            cursor = self.conn.execute("SELECT * FROM nodes")
            for row in cursor:
                node_id = row["id"]
                attributes = {
                    "adg_name": row["adg_name"],
                    "layer": row["layer"],
                    "node_type": row["node_type"],
                    "file_path": row["file_path"],
                }
                self.graph.add_node(node_id, **attributes)

            # Load edges
            cursor = self.conn.execute("SELECT * FROM edges")
            for row in cursor:
                src_id = row["src_id"]
                tgt_id = row["tgt_id"]
                relation_type = row["relation_type"]

                self.graph.add_edge(src_id, tgt_id, relation_type=relation_type)

            logger.info(
                f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges"
            )

        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            raise

    def analyze_pagerank(self, writeback: bool = False) -> List[Tuple[str, float]]:
        """
        Analyze PageRank centrality.

        Args:
            writeback: Whether to write results back to SQLite

        Returns:
            List of (node_name, pagerank_score) tuples
        """
        try:
            pagerank_scores = nx.pagerank(self.graph)

            # Convert to (name, score) format
            results = []
            for node_id, score in pagerank_scores.items():
                node_name = self.graph.nodes[node_id].get("adg_name", f"node_{node_id}")
                results.append((node_name, score))

            # Sort by score (descending)
            results.sort(key=lambda x: x[1], reverse=True)

            if writeback:
                self._writeback_pagerank(pagerank_scores)

            return results

        except Exception as e:
            logger.error(f"Failed to analyze PageRank: {e}")
            return []

    def analyze_betweenness_centrality(self, writeback: bool = False) -> List[Tuple[str, float]]:
        """
        Analyze betweenness centrality.

        Args:
            writeback: Whether to write results back to SQLite

        Returns:
            List of (node_name, betweenness_score) tuples
        """
        try:
            betweenness_scores = nx.betweenness_centrality(self.graph)

            # Convert to (name, score) format
            results = []
            for node_id, score in betweenness_scores.items():
                node_name = self.graph.nodes[node_id].get("adg_name", f"node_{node_id}")
                results.append((node_name, score))

            # Sort by score (descending)
            results.sort(key=lambda x: x[1], reverse=True)

            if writeback:
                self._writeback_betweenness(betweenness_scores)

            return results

        except Exception as e:
            logger.error(f"Failed to analyze betweenness centrality: {e}")
            return []

    def detect_communities(self, writeback: bool = False) -> Dict[str, int]:
        """
        Detect communities using Louvain method.

        Args:
            writeback: Whether to write results back to SQLite

        Returns:
            Dictionary mapping node_name to community_id
        """
        try:
            # Convert to undirected graph for community detection
            undirected_graph = self.graph.to_undirected()

            # Use greedy modularity communities (simpler than Louvain)
            communities = nx.community.greedy_modularity_communities(undirected_graph)

            # Convert to node_name -> community_id mapping
            results = {}
            for community_id, community_nodes in enumerate(communities):
                for node_id in community_nodes:
                    node_name = self.graph.nodes[node_id].get("adg_name", f"node_{node_id}")
                    results[node_name] = community_id

            if writeback:
                self._writeback_communities(results)

            return results

        except Exception as e:
            logger.error(f"Failed to detect communities: {e}")
            return {}

    def analyze_closeness_centrality(self, writeback: bool = False) -> List[Tuple[str, float]]:
        """
        Analyze closeness centrality.

        Args:
            writeback: Whether to write results back to SQLite

        Returns:
            List of (node_name, closeness_score) tuples
        """
        try:
            # Only analyze the largest connected component
            largest_cc = max(nx.weakly_connected_components(self.graph), key=len)
            subgraph = self.graph.subgraph(largest_cc)

            closeness_scores = nx.closeness_centrality(subgraph)

            # Convert to (name, score) format
            results = []
            for node_id, score in closeness_scores.items():
                node_name = self.graph.nodes[node_id].get("adg_name", f"node_{node_id}")
                results.append((node_name, score))

            # Sort by score (descending)
            results.sort(key=lambda x: x[1], reverse=True)

            if writeback:
                self._writeback_closeness(closeness_scores)

            return results

        except Exception as e:
            logger.error(f"Failed to analyze closeness centrality: {e}")
            return []

    def find_bridges(self) -> List[Tuple[str, str]]:
        """
        Find bridge edges in the graph.

        Returns:
            List of (source_name, target_name) tuples
        """
        try:
            bridges = nx.bridges(self.graph.to_undirected())

            results = []
            for src_id, tgt_id in bridges:
                src_name = self.graph.nodes[src_id].get("adg_name", f"node_{src_id}")
                tgt_name = self.graph.nodes[tgt_id].get("adg_name", f"node_{tgt_id}")
                results.append((src_name, tgt_name))

            return results

        except Exception as e:
            logger.error(f"Failed to find bridges: {e}")
            return []

    def analyze_layer_connectivity(self) -> Dict[str, Dict[str, int]]:
        """
        Analyze connectivity between layers.

        Returns:
            Dictionary mapping layer_pair to edge_count
        """
        try:
            layer_edges = {}

            for src_id, tgt_id, data in self.graph.edges(data=True):
                src_layer = self.graph.nodes[src_id].get("layer", "unknown")
                tgt_layer = self.graph.nodes[tgt_id].get("layer", "unknown")

                if src_layer != tgt_layer:
                    pair = f"{src_layer}->{tgt_layer}"
                    layer_edges[pair] = layer_edges.get(pair, 0) + 1

            return layer_edges

        except Exception as e:
            logger.error(f"Failed to analyze layer connectivity: {e}")
            return {}

    def get_strongly_connected_components(self) -> List[List[str]]:
        """
        Get strongly connected components.

        Returns:
            List of components, each as a list of node names
        """
        try:
            sccs = nx.strongly_connected_components(self.graph)

            results = []
            for scc in sccs:
                component = []
                for node_id in scc:
                    node_name = self.graph.nodes[node_id].get("adg_name", f"node_{node_id}")
                    component.append(node_name)
                results.append(component)

            # Sort by size (descending)
            results.sort(key=len, reverse=True)

            return results

        except Exception as e:
            logger.error(f"Failed to get strongly connected components: {e}")
            return []

    def _writeback_pagerank(self, pagerank_scores: Dict[int, float]):
        """Write PageRank scores back to SQLite."""
        try:
            # Create table if it doesn't exist
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS mv_pagerank_scores (
                    node_id INTEGER PRIMARY KEY,
                    adg_name TEXT,
                    pagerank_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Clear existing data
            self.conn.execute("DELETE FROM mv_pagerank_scores")

            # Insert new data
            for node_id, score in pagerank_scores.items():
                node_name = self.graph.nodes[node_id].get("adg_name", f"node_{node_id}")
                self.conn.execute(
                    "INSERT INTO mv_pagerank_scores (node_id, adg_name, pagerank_score) VALUES (?, ?, ?)",
                    (node_id, node_name, score),
                )

            self.conn.commit()
            logger.info("PageRank scores written back to SQLite")

        except Exception as e:
            logger.error(f"Failed to write back PageRank scores: {e}")

    def _writeback_betweenness(self, betweenness_scores: Dict[int, float]):
        """Write betweenness scores back to SQLite."""
        try:
            # Create table if it doesn't exist
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS mv_betweenness_scores (
                    node_id INTEGER PRIMARY KEY,
                    adg_name TEXT,
                    betweenness_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Clear existing data
            self.conn.execute("DELETE FROM mv_betweenness_scores")

            # Insert new data
            for node_id, score in betweenness_scores.items():
                node_name = self.graph.nodes[node_id].get("adg_name", f"node_{node_id}")
                self.conn.execute(
                    "INSERT INTO mv_betweenness_scores (node_id, adg_name, betweenness_score) VALUES (?, ?, ?)",
                    (node_id, node_name, score),
                )

            self.conn.commit()
            logger.info("Betweenness scores written back to SQLite")

        except Exception as e:
            logger.error(f"Failed to write back betweenness scores: {e}")

    def _writeback_communities(self, communities: Dict[str, int]):
        """Write community assignments back to SQLite."""
        try:
            # Create table if it doesn't exist
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS mv_community_assignments (
                    adg_name TEXT PRIMARY KEY,
                    community_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Clear existing data
            self.conn.execute("DELETE FROM mv_community_assignments")

            # Insert new data
            for node_name, community_id in communities.items():
                self.conn.execute(
                    "INSERT INTO mv_community_assignments (adg_name, community_id) VALUES (?, ?)",
                    (node_name, community_id),
                )

            self.conn.commit()
            logger.info("Community assignments written back to SQLite")

        except Exception as e:
            logger.error(f"Failed to write back community assignments: {e}")

    def _writeback_closeness(self, closeness_scores: Dict[int, float]):
        """Write closeness scores back to SQLite."""
        try:
            # Create table if it doesn't exist
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS mv_closeness_scores (
                    node_id INTEGER PRIMARY KEY,
                    adg_name TEXT,
                    closeness_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Clear existing data
            self.conn.execute("DELETE FROM mv_closeness_scores")

            # Insert new data
            for node_id, score in closeness_scores.items():
                node_name = self.graph.nodes[node_id].get("adg_name", f"node_{node_id}")
                self.conn.execute(
                    "INSERT INTO mv_closeness_scores (node_id, adg_name, closeness_score) VALUES (?, ?, ?)",
                    (node_id, node_name, score),
                )

            self.conn.commit()
            logger.info("Closeness scores written back to SQLite")

        except Exception as e:
            logger.error(f"Failed to write back closeness scores: {e}")

    def get_graph_summary(self) -> Dict[str, Any]:
        """Get summary statistics about the graph."""
        try:
            n_nodes = self.graph.number_of_nodes()
            n_edges = self.graph.number_of_edges()
            summary: Dict[str, Any] = {
                "nodes": n_nodes,
                "edges": n_edges,
            }
            if n_nodes == 0:
                summary.update(
                    {
                        "density": 0.0,
                        "is_strongly_connected": False,
                        "is_weakly_connected": False,
                        "number_of_strongly_connected_components": 0,
                        "number_of_weakly_connected_components": 0,
                        "layer_distribution": {},
                    }
                )
                return summary
            summary.update(
                {
                    "density": nx.density(self.graph),
                    "is_strongly_connected": nx.is_strongly_connected(self.graph),
                    "is_weakly_connected": nx.is_weakly_connected(self.graph),
                    "number_of_strongly_connected_components": nx.number_strongly_connected_components(
                        self.graph
                    ),
                    "number_of_weakly_connected_components": nx.number_weakly_connected_components(
                        self.graph
                    ),
                }
            )

            # Add layer distribution
            layers = {}
            for node_data in self.graph.nodes.values():
                layer = node_data.get("layer", "unknown")
                layers[layer] = layers.get(layer, 0) + 1
            summary["layer_distribution"] = layers

            return summary

        except Exception as e:
            logger.error(f"Failed to get graph summary: {e}")
            return {}

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("NetworkX analyzer connection closed")


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python networkx_analysis.py <sqlite_path> [analysis_type]")
        print("Available analysis types: pagerank, betweenness, communities, closeness, summary")
        sys.exit(1)

    sqlite_path = sys.argv[1]
    analysis_type = sys.argv[2] if len(sys.argv) > 2 else "summary"

    try:
        analyzer = NetworkXAnalyzer(sqlite_path)

        if analysis_type == "pagerank":
            results = analyzer.analyze_pagerank()
            print(json.dumps(results, indent=2))
        elif analysis_type == "betweenness":
            results = analyzer.analyze_betweenness_centrality()
            print(json.dumps(results, indent=2))
        elif analysis_type == "communities":
            results = analyzer.detect_communities()
            print(json.dumps(results, indent=2))
        elif analysis_type == "closeness":
            results = analyzer.analyze_closeness_centrality()
            print(json.dumps(results, indent=2))
        elif analysis_type == "summary":
            results = analyzer.get_graph_summary()
            print(json.dumps(results, indent=2))
        else:
            print(f"Unknown analysis type: {analysis_type}")
            sys.exit(1)

        analyzer.close()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
