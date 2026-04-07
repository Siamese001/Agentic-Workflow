#!/usr/bin/env python3
"""
Core Knowledge Ingestion for ChromaDB Semantic Memory Layer
Wave 1 Implementation: Core Knowledge (Baseline)

Ingests code chunks, symbols, and architectural documentation into ChromaDB.
"""

import hashlib
import logging
import sqlite3
import sys
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core"))

from L4_state.client.chroma_client import SovereignChromaClient

# from L2_execution.UniversalWriteGateway import UniversalWriteGateway

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoreKnowledgeIngestion:
    """
    Ingests core knowledge artifacts into ChromaDB semantic memory layer.

    Wave 1 focuses on:
    - repo_code_chunks: Code snippets and functions
    - repo_symbols: Python symbols and classes
    - repo_arch_docs: Architectural documentation
    """

    def __init__(self, repo_root: str, adg_db_path: str, chroma_persist_dir: str = "artifacts/chromadb"):
        """
        Initialize core knowledge ingestion.

        Args:
            repo_root: Repository root directory
            adg_db_path: Path to ADG SQLite database
            chroma_persist_dir: ChromaDB persistence directory
        """
        self.repo_root = Path(repo_root)
        self.adg_db_path = Path(adg_db_path)

        # Initialize ChromaDB client
        self.chroma = SovereignChromaClient(persist_dir=chroma_persist_dir)

        # Note: UWG initialization deferred for Wave 1
        # self.uwg = UniversalWriteGateway()

        # Collection names for Wave 1
        self.collections = {
            "repo_code_chunks": "Code chunks and snippets",
            "repo_symbols": "Python symbols and classes",
            "repo_arch_docs": "Architectural documentation",
        }

    def ingest_code_chunks(self):
        """Ingest code chunks from Python files."""
        logger.info("Starting code chunks ingestion...")

        documents = []
        metadatas = []
        ids = []

        # Find all Python files in agentic_core
        python_files = list(self.repo_root.glob("agentic_core/**/*.py"))

        for file_path in python_files:
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()

                # Split into chunks (simplified - could use AST for better chunking)
                chunks = self._chunk_code(content, chunk_size=500)

                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue

                    # Create metadata
                    rel_path = str(file_path.relative_to(self.repo_root))
                    metadata = {
                        "file_path": rel_path,
                        "artifact_type": "code",
                        "layer": self._infer_layer(rel_path),
                        "subsystem": self._infer_subsystem(rel_path),
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "canonical_digest": hashlib.sha256(chunk.encode()).hexdigest()[:16],
                    }

                    documents.append(chunk)
                    metadatas.append(metadata)
                    ids.append(f"code_{rel_path.replace('/', '_')}_{i}")

            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")

        # Add to ChromaDB in batches
        if documents:
            batch_size = 1000
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]

                self.chroma.add_documents(
                    collection_name="repo_code_chunks",
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids,
                )
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch_docs)} documents")

            logger.info(f"Ingested {len(documents)} code chunks total")

        return len(documents)

    def ingest_symbols(self):
        """Ingest Python symbols from ADG database."""
        logger.info("Starting symbols ingestion...")

        if not self.adg_db_path.exists():
            logger.warning(f"ADG database not found at {self.adg_db_path}")
            return 0

        try:
            conn = sqlite3.connect(str(self.adg_db_path))
            cursor = conn.cursor()

            documents = []
            metadatas = []
            ids = []

            # Query nodes from ADG
            cursor.execute("""
                SELECT id, adg_name, entity_type, layer, identity_kind,
                       confidence, resolved_path
                FROM nodes
                WHERE entity_type IN ('class', 'function', 'module')
                ORDER BY adg_name
            """)

            for row in cursor.fetchall():
                node_id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path = row

                # Create document content
                doc_content = f"{entity_type}: {adg_name}\n"
                doc_content += f"Layer: {layer}\n"
                doc_content += f"Path: {resolved_path}\n"
                doc_content += f"Identity: {identity_kind}\n"

                # Create metadata
                metadata = {
                    "object_id": f"urn:agentic:{entity_type}:{adg_name}",
                    "artifact_type": "sym",
                    "layer": layer,
                    "entity_type": entity_type,
                    "identity_kind": identity_kind,
                    "confidence": confidence,
                    "file_path": resolved_path,
                    "symbol_name": adg_name,
                    "canonical_digest": hashlib.sha256(doc_content.encode()).hexdigest()[:16],
                }

                documents.append(doc_content)
                metadatas.append(metadata)
                ids.append(f"sym_{node_id}")

            # Add to ChromaDB in batches
            if documents:
                batch_size = 1000
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i:i+batch_size]
                    batch_metas = metadatas[i:i+batch_size]
                    batch_ids = ids[i:i+batch_size]

                    self.chroma.add_documents(
                        collection_name="repo_symbols",
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids,
                    )
                    logger.info(f"Added batch {i//batch_size + 1}: {len(batch_docs)} symbols")

                logger.info(f"Ingested {len(documents)} symbols total")

            conn.close()
            return len(documents)

        except Exception as e:
            logger.error(f"Failed to ingest symbols: {e}")
            return 0

    def ingest_arch_docs(self):
        """Ingest architectural documentation."""
        logger.info("Starting architectural documentation ingestion...")

        documents = []
        metadatas = []
        ids = []

        # Find documentation files
        doc_patterns = [
            "docs/**/*.md",
            "docs/**/*.rst",
            "agentic_core/**/*.md",
            ".windsurf/**/*.md",
        ]

        for pattern in doc_patterns:
            for file_path in self.repo_root.glob(pattern):
                if file_path.name.startswith('.'):
                    continue

                try:
                    with open(file_path, encoding='utf-8') as f:
                        content = f.read()

                    if not content.strip():
                        continue

                    # Create metadata
                    rel_path = str(file_path.relative_to(self.repo_root))
                    metadata = {
                        "file_path": rel_path,
                        "artifact_type": "doc",
                        "layer": self._infer_layer(rel_path),
                        "subsystem": "documentation",
                        "doc_type": self._infer_doc_type(rel_path),
                        "canonical_digest": hashlib.sha256(content.encode()).hexdigest()[:16],
                    }

                    documents.append(content)
                    metadatas.append(metadata)
                    ids.append(f"doc_{rel_path.replace('/', '_')}")

                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {e}")

        # Add to ChromaDB in batches
        if documents:
            batch_size = 1000
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]

                self.chroma.add_documents(
                    collection_name="repo_arch_docs",
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids,
                )
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch_docs)} documents")

            logger.info(f"Ingested {len(documents)} architectural documents total")

        return len(documents)

    def _chunk_code(self, content: str, chunk_size: int = 500) -> list[str]:
        """Split code content into chunks."""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0

        for line in lines:
            line_size = len(line)
            if current_size + line_size > chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks

    def _infer_layer(self, path: str) -> str:
        """Infer L0-L6 layer from file path."""
        if "L0_routing" in path:
            return "L0"
        elif "L1_cognition" in path:
            return "L1"
        elif "L2_execution" in path:
            return "L2"
        elif "L3_orchestration" in path:
            return "L3"
        elif "L4_state" in path:
            return "L4"
        elif "L5_safety" in path:
            return "L5"
        elif "L6_observability" in path:
            return "L6"
        else:
            return "unknown"

    def _infer_subsystem(self, path: str) -> str:
        """Infer subsystem from file path."""
        if "routing" in path.lower():
            return "routing"
        elif "cognition" in path.lower():
            return "cognition"
        elif "execution" in path.lower():
            return "execution"
        elif "orchestration" in path.lower():
            return "orchestration"
        elif "state" in path.lower():
            return "state"
        elif "safety" in path.lower():
            return "safety"
        elif "observability" in path.lower():
            return "observability"
        else:
            return "general"

    def _infer_doc_type(self, path: str) -> str:
        """Infer document type from path."""
        if "technical" in path:
            return "technical"
        elif "reports" in path:
            return "report"
        elif "rules" in path:
            return "policy"
        elif "README" in path:
            return "readme"
        else:
            return "documentation"

    def run_ingestion(self) -> dict[str, int]:
        """Run complete Wave 1 ingestion."""
        logger.info("Starting Wave 1: Core Knowledge ingestion...")

        results = {}

        # Ingest each collection
        results["repo_code_chunks"] = self.ingest_code_chunks()
        results["repo_symbols"] = self.ingest_symbols()
        results["repo_arch_docs"] = self.ingest_arch_docs()

        # Log statistics
        logger.info("Wave 1 ingestion complete:")
        for collection, count in results.items():
            stats = self.chroma.get_collection_stats(collection)
            logger.info(f"  {collection}: {count} documents ingested")

        return results


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Wave 1: Core Knowledge Ingestion")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--adg-db", help="Path to ADG SQLite database")
    parser.add_argument("--chroma-dir", default="artifacts/chromadb", help="ChromaDB persistence directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be ingested without actually doing it")
    args = parser.parse_args()

    # Find ADG database if not specified
    if not args.adg_db:
        adg_pattern = list(Path(args.repo_root).glob("artifacts/adg/adg_indexed_*.sqlite"))
        if adg_pattern:
            args.adg_db = str(adg_pattern[-1])  # Use most recent
        else:
            logger.warning("No ADG database found, symbols ingestion will be skipped")
            args.adg_db = None

    # Run ingestion
    ingestion = CoreKnowledgeIngestion(
        repo_root=args.repo_root,
        adg_db_path=args.adg_db or "",
        chroma_persist_dir=args.chroma_dir,
    )

    if args.dry_run:
        logger.info("DRY RUN: Would ingest core knowledge into ChromaDB")
        return

    results = ingestion.run_ingestion()

    # Summary
    total_docs = sum(results.values())
    logger.info(f"Wave 1 complete: {total_docs} total documents ingested")
    logger.info(f"Collections created: {list(ingestion.collections.keys())}")


if __name__ == "__main__":
    main()
