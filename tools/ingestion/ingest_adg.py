#!/usr/bin/env python3
"""
ADG Graph Ingestion for ChromaDB Semantic Memory Layer
Wave 2 Implementation: Structural & Test Intelligence

Ingests ADG graph relationships and structural patterns into ChromaDB.
"""

import hashlib
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core"))

from L4_state.client.chroma_client import SovereignChromaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ADGGraphIngestion:
    """
    Ingests ADG graph structural knowledge into ChromaDB semantic memory layer.

    Wave 2 focuses on:
    - repo_adg_graph: Graph relationships and structural patterns
    """

    def __init__(self, repo_root: str, adg_db_path: str, chroma_persist_dir: str = "artifacts/chromadb"):
        """
        Initialize ADG graph ingestion.

        Args:
            repo_root: Repository root directory
            adg_db_path: Path to ADG SQLite database
            chroma_persist_dir: ChromaDB persistence directory
        """
        self.repo_root = Path(repo_root)
        self.adg_db_path = Path(adg_db_path)

        # Initialize ChromaDB client
        self.chroma = SovereignChromaClient(persist_dir=chroma_persist_dir)

        logger.info("ADG graph ingestion initialized")

    def ingest_graph_relationships(self) -> int:
        """Ingest ADG graph relationships as natural language descriptions."""
        logger.info("Starting ADG graph relationships ingestion...")

        if not self.adg_db_path.exists():
            logger.warning(f"ADG database not found at {self.adg_db_path}")
            return 0

        try:
            conn = sqlite3.connect(str(self.adg_db_path))
            cursor = conn.cursor()

            documents = []
            metadatas = []
            ids = []

            # Query edges with node information
            cursor.execute("""
                SELECT
                    e.id as edge_id,
                    e.relation_type,
                    e.edge_kind,
                    e.source_file,
                    e.line_no,
                    e.symbol,
                    n1.adg_name as src_name,
                    n1.entity_type as src_type,
                    n1.layer as src_layer,
                    n2.adg_name as dst_name,
                    n2.entity_type as dst_type,
                    n2.layer as dst_layer
                FROM edges e
                JOIN nodes n1 ON e.src_id = n1.id
                JOIN nodes n2 ON e.dst_id = n2.id
                ORDER BY e.relation_type, n1.layer, n2.layer
            """)

            for row in cursor.fetchall():
                (
                    edge_id,
                    relation_type,
                    edge_kind,
                    source_file,
                    line_no,
                    symbol,
                    src_name,
                    src_type,
                    src_layer,
                    dst_name,
                    dst_type,
                    dst_layer,
                ) = row

                # Create natural language description
                doc_content = self._create_relationship_description(
                    src_name,
                    src_type,
                    src_layer,
                    relation_type,
                    edge_kind,
                    dst_name,
                    dst_type,
                    dst_layer,
                    source_file,
                    line_no,
                    symbol,
                )

                # Create metadata
                metadata = {
                    "object_id": f"urn:agentic:edge:{edge_id}",
                    "artifact_type": "edge",
                    "relation_type": relation_type,
                    "edge_kind": edge_kind,
                    "src_name": src_name,
                    "src_type": src_type,
                    "src_layer": src_layer,
                    "dst_name": dst_name,
                    "dst_type": dst_type,
                    "dst_layer": dst_layer,
                    "source_file": source_file,
                    "line_no": line_no,
                    "symbol": symbol,
                    "canonical_digest": hashlib.sha256(doc_content.encode()).hexdigest()[:16],
                }

                documents.append(doc_content)
                metadatas.append(metadata)
                ids.append(f"edge_{edge_id}")

            # Add to ChromaDB in batches
            if documents:
                batch_size = 1000
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i : i + batch_size]
                    batch_metas = metadatas[i : i + batch_size]
                    batch_ids = ids[i : i + batch_size]

                    self.chroma.add_documents(
                        collection_name="repo_adg_graph",
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids,
                    )
                    logger.info(f"Added batch {i // batch_size + 1}: {len(batch_docs)} relationships")

                logger.info(f"Ingested {len(documents)} ADG relationships total")

            conn.close()
            return len(documents)

        except Exception as e:
            logger.error(f"Failed to ingest ADG relationships: {e}")
            return 0

    def ingest_structural_patterns(self) -> int:
        """Ingest structural patterns and architectural insights."""
        logger.info("Starting structural patterns ingestion...")

        if not self.adg_db_path.exists():
            logger.warning(f"ADG database not found at {self.adg_db_path}")
            return 0

        try:
            conn = sqlite3.connect(str(self.adg_db_path))
            cursor = conn.cursor()

            documents = []
            metadatas = []
            ids = []

            # Pattern 1: Layer coupling analysis
            layer_coupling = self._analyze_layer_coupling(cursor)
            for pattern_desc, metadata in layer_coupling:
                documents.append(pattern_desc)
                metadatas.append(metadata)
                ids.append(f"pattern_coupling_{len(documents)}")

            # Pattern 2: Hub nodes (high connectivity)
            hub_nodes = self._analyze_hub_nodes(cursor)
            for pattern_desc, metadata in hub_nodes:
                documents.append(pattern_desc)
                metadatas.append(metadata)
                ids.append(f"pattern_hub_{len(documents)}")

            # Pattern 3: Critical paths
            critical_paths = self._analyze_critical_paths(cursor)
            for pattern_desc, metadata in critical_paths:
                documents.append(pattern_desc)
                metadatas.append(metadata)
                ids.append(f"pattern_critical_{len(documents)}")

            # Add to ChromaDB in batches
            if documents:
                batch_size = 500
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i : i + batch_size]
                    batch_metas = metadatas[i : i + batch_size]
                    batch_ids = ids[i : i + batch_size]

                    self.chroma.add_documents(
                        collection_name="repo_adg_graph",
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids,
                    )
                    logger.info(f"Added pattern batch {i // batch_size + 1}: {len(batch_docs)} patterns")

                logger.info(f"Ingested {len(documents)} structural patterns total")

            conn.close()
            return len(documents)

        except Exception as e:
            logger.error(f"Failed to ingest structural patterns: {e}")
            return 0

    def _create_relationship_description(
        self,
        src_name: str,
        src_type: str,
        src_layer: str,
        relation_type: str,
        edge_kind: str,
        dst_name: str,
        dst_type: str,
        dst_layer: str,
        source_file: str,
        line_no: int,
        symbol: str,
    ) -> str:
        """Create natural language description of a relationship."""

        # Map relation types to natural language
        relation_verbs = {
            "calls": "calls",
            "imports": "imports",
            "extends": "extends",
            "implements": "implements",
            "writes_to": "writes to",
            "reads_from": "reads from",
            "routes_to": "routes to",
            "validates": "validates",
            "authorizes": "authorizes",
            "orchestrates": "orchestrates",
        }

        verb = relation_verbs.get(relation_type, relation_type)

        description = f"{src_type} '{src_name}' ({src_layer}) {verb} {dst_type} '{dst_name}' ({dst_layer})"

        if source_file and line_no:
            description += f" in {source_file}:{line_no}"

        if symbol:
            description += f" via symbol '{symbol}'"

        if edge_kind:
            description += f" [{edge_kind}]"

        return description

    def _analyze_layer_coupling(self, cursor: sqlite3.Cursor) -> list[tuple[str, dict[str, Any]]]:
        """Analyze coupling between layers."""
        patterns = []

        # Query inter-layer relationships
        cursor.execute("""
            SELECT
                n1.layer as src_layer,
                n2.layer as dst_layer,
                COUNT(*) as edge_count,
                GROUP_CONCAT(DISTINCT e.relation_type) as relation_types
            FROM edges e
            JOIN nodes n1 ON e.src_id = n1.id
            JOIN nodes n2 ON e.dst_id = n2.id
            WHERE n1.layer != n2.layer
            GROUP BY n1.layer, n2.layer
            HAVING edge_count > 10
            ORDER BY edge_count DESC
        """)

        for row in cursor.fetchall():
            src_layer, dst_layer, edge_count, relation_types = row

            pattern_desc = (
                f"Layer {src_layer} is strongly coupled to Layer {dst_layer} with {edge_count} edges"
            )
            pattern_desc += f" using relations: {relation_types}"

            metadata = {
                "object_id": f"urn:agentic:pattern:layer_coupling:{src_layer}_{dst_layer}",
                "artifact_type": "pattern",
                "pattern_type": "layer_coupling",
                "src_layer": src_layer,
                "dst_layer": dst_layer,
                "edge_count": edge_count,
                "relation_types": relation_types.split(","),
                "canonical_digest": hashlib.sha256(pattern_desc.encode()).hexdigest()[:16],
            }

            patterns.append((pattern_desc, metadata))

        return patterns

    def _analyze_hub_nodes(self, cursor: sqlite3.Cursor) -> list[tuple[str, dict[str, Any]]]:
        """Identify hub nodes with high connectivity."""
        patterns = []

        # Find nodes with high out-degree
        cursor.execute("""
            SELECT
                n.adg_name,
                n.entity_type,
                n.layer,
                COUNT(*) as out_degree,
                GROUP_CONCAT(DISTINCT e.relation_type) as relation_types
            FROM edges e
            JOIN nodes n ON e.src_id = n.id
            GROUP BY n.id
            HAVING out_degree > 50
            ORDER BY out_degree DESC
            LIMIT 20
        """)

        for row in cursor.fetchall():
            name, entity_type, layer, out_degree, relation_types = row

            pattern_desc = (
                f"Hub node: {entity_type} '{name}' in {layer} has {out_degree} outgoing connections"
            )
            pattern_desc += f" using relations: {relation_types}"

            metadata = {
                "object_id": f"urn:agentic:pattern:hub:{name}",
                "artifact_type": "pattern",
                "pattern_type": "hub_node",
                "node_name": name,
                "entity_type": entity_type,
                "layer": layer,
                "out_degree": out_degree,
                "relation_types": relation_types.split(","),
                "canonical_digest": hashlib.sha256(pattern_desc.encode()).hexdigest()[:16],
            }

            patterns.append((pattern_desc, metadata))

        return patterns

    def _analyze_critical_paths(self, cursor: sqlite3.Cursor) -> list[tuple[str, dict[str, Any]]]:
        """Identify critical architectural paths."""
        patterns = []

        # Find paths from L0 to L6
        cursor.execute("""
            SELECT DISTINCT
                n1.adg_name as src_name,
                n1.entity_type as src_type,
                n1.layer as src_layer,
                n2.adg_name as dst_name,
                n2.entity_type as dst_type,
                n2.layer as dst_layer,
                e.relation_type
            FROM edges e
            JOIN nodes n1 ON e.src_id = n1.id
            JOIN nodes n2 ON e.dst_id = n2.id
            WHERE n1.layer = 'L0' AND n2.layer = 'L6'
               OR n1.layer = 'L6' AND n2.layer = 'L0'
            LIMIT 50
        """)

        for row in cursor.fetchall():
            src_name, src_type, src_layer, dst_name, dst_type, dst_layer, relation_type = row

            pattern_desc = f"Critical path: {src_type} '{src_name}' ({src_layer}) {relation_type} {dst_type} '{dst_name}' ({dst_layer})"

            metadata = {
                "object_id": f"urn:agentic:pattern:critical_path:{src_name}_{dst_name}",
                "artifact_type": "pattern",
                "pattern_type": "critical_path",
                "src_name": src_name,
                "src_type": src_type,
                "src_layer": src_layer,
                "dst_name": dst_name,
                "dst_type": dst_type,
                "dst_layer": dst_layer,
                "relation_type": relation_type,
                "canonical_digest": hashlib.sha256(pattern_desc.encode()).hexdigest()[:16],
            }

            patterns.append((pattern_desc, metadata))

        return patterns

    def run_ingestion(self) -> dict[str, int]:
        """Run complete Wave 2 ADG ingestion."""
        logger.info("Starting Wave 2: ADG Graph ingestion...")

        results = {}

        # Ingest relationships and patterns
        results["relationships"] = self.ingest_graph_relationships()
        results["patterns"] = self.ingest_structural_patterns()

        # Log statistics
        logger.info("Wave 2 ADG ingestion complete:")
        for category, count in results.items():
            logger.info(f"  {category}: {count} items")

        stats = self.chroma.get_collection_stats("repo_adg_graph")
        logger.info(f"Collection 'repo_adg_graph': {stats['document_count']} total documents")

        return results


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Wave 2: ADG Graph Ingestion")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--adg-db", help="Path to ADG SQLite database")
    parser.add_argument("--chroma-dir", default="artifacts/chromadb", help="ChromaDB persistence directory")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be ingested without actually doing it"
    )
    args = parser.parse_args()

    # Find ADG database if not specified
    if not args.adg_db:
        adg_pattern = list(Path(args.repo_root).glob("artifacts/adg/adg_indexed_*.sqlite"))
        if adg_pattern:
            args.adg_db = str(adg_pattern[-1])  # Use most recent
        else:
            logger.error("No ADG database found")
            sys.exit(1)

    # Run ingestion
    ingestion = ADGGraphIngestion(
        repo_root=args.repo_root,
        adg_db_path=args.adg_db,
        chroma_persist_dir=args.chroma_dir,
    )

    if args.dry_run:
        logger.info("DRY RUN: Would ingest ADG graph into ChromaDB")
        return

    results = ingestion.run_ingestion()

    # Summary
    total_items = sum(results.values())
    logger.info(f"Wave 2 complete: {total_items} total ADG items ingested")


if __name__ == "__main__":
    main()
