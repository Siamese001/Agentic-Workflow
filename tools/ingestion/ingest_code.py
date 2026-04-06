#!/usr/bin/env python3
"""
Code Ingestion Script for ChromaDB
Ingests Python source code with AST-based chunking.
"""

import argparse
import ast
import hashlib
import logging
from pathlib import Path
from typing import Any

# Import SovereignChromaClient for centralized ChromaDB access
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core"))
from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient
from agentic_core.L4_state.utils.memory.bm25_store import get_bm25_store

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeChunker:
    """AST-based code chunker for Python files."""

    # Metadata schema for validation
    REQUIRED_METADATA_FIELDS = {
        "file_path", "module", "layer", "entity_type", "name",
        "line_start", "line_end", "type"
    }
    OPTIONAL_METADATA_FIELDS = {
        "args", "docstring", "methods", "adg_node_id", "embedding_model", "ingested_at"
    }

    def __init__(self):
        self.chunks = []

    @staticmethod
    def validate_metadata(metadata: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate chunk metadata against schema.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        missing_fields = CodeChunker.REQUIRED_METADATA_FIELDS - metadata.keys()
        if missing_fields:
            errors.append(f"Missing required fields: {missing_fields}")

        # Check for unknown fields
        all_known = CodeChunker.REQUIRED_METADATA_FIELDS | CodeChunker.OPTIONAL_METADATA_FIELDS
        unknown_fields = metadata.keys() - all_known
        if unknown_fields:
            errors.append(f"Unknown fields: {unknown_fields}")

        # Type checks
        if "line_start" in metadata and not isinstance(metadata["line_start"], int):
            errors.append("line_start must be int")
        if "line_end" in metadata and not isinstance(metadata["line_end"], int):
            errors.append("line_end must be int")
        if "layer" in metadata and metadata["layer"] not in ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "Unknown"]:
            errors.append(f"Invalid layer: {metadata['layer']}")
        if "entity_type" in metadata and metadata["entity_type"] not in ["function", "async_function", "class", "module"]:
            errors.append(f"Invalid entity_type: {metadata['entity_type']}")

        return (len(errors) == 0, errors)

    def chunk_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Chunk a Python file using AST."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Extract chunks
            chunks = []

            # Get module-level info
            module_name = self._get_module_name(file_path)
            layer = self._detect_layer(file_path)

            # Walk through AST nodes
            for node in ast.walk(tree):
                chunk = None

                if isinstance(node, ast.FunctionDef):
                    # Skip functions with no args
                    if not node.args.args:
                        continue
                    chunk = self._create_function_chunk(node, content, file_path, module_name, layer)
                elif isinstance(node, ast.ClassDef):
                    # Extract methods first
                    methods = []
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            methods.append(item.name)
                    # Skip classes with no methods
                    if not methods:
                        continue
                    chunk = self._create_class_chunk(node, content, file_path, module_name, layer)
                elif isinstance(node, ast.AsyncFunctionDef):
                    # Skip async functions with no args
                    if not node.args.args:
                        continue
                    chunk = self._create_function_chunk(
                        node,
                        content,
                        file_path,
                        module_name,
                        layer,
                        is_async=True,
                    )

                if chunk:
                    chunks.append(chunk)

            return chunks

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return []

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        parts = file_path.parts
        if "agentic_core" in parts:
            idx = parts.index("agentic_core")
            return ".".join(parts[idx + 1 : -1]) + "." + file_path.stem
        return str(file_path.relative_to(Path.cwd()))

    def _detect_layer(self, file_path: Path) -> str:
        """Detect architectural layer from file path."""
        path_str = str(file_path).lower()

        if "l0_" in path_str or "routing" in path_str:
            return "L0"
        elif "l1_" in path_str or "cache" in path_str:
            return "L1"
        elif "l2_" in path_str or "execution" in path_str:
            return "L2"
        elif "l3_" in path_str or "orchestration" in path_str:
            return "L3"
        elif "l4_" in path_str or "state" in path_str:
            return "L4"
        elif "l5_" in path_str or "safety" in path_str:
            return "L5"
        elif "l6_" in path_str or "governance" in path_str:
            return "L6"
        else:
            return "Unknown"

    def _create_function_chunk(
        self,
        node,
        content: str,
        file_path: Path,
        module_name: str,
        layer: str,
        is_async: bool = False,
    ) -> dict[str, Any]:
        """Create a chunk for a function."""
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)

        # Extract function source
        lines = content.split("\n")
        func_lines = lines[start_line - 1 : end_line]
        func_code = "\n".join(func_lines)

        # Create chunk ID
        chunk_id = hashlib.sha256(
            f"{file_path}:{module_name}:{node.name}:{start_line}:{func_code}".encode(),
        ).hexdigest()

        return {
            "id": chunk_id,
            "content": func_code,
            "metadata": {
                "file_path": str(file_path),
                "module": module_name,
                "layer": layer,
                "entity_type": "async_function" if is_async else "function",
                "name": node.name,
                "line_start": start_line,
                "line_end": end_line,
                "args": [arg.arg for arg in node.args.args] if node.args.args else [],
                "docstring": ast.get_docstring(node) or "",
                "type": "code",
                "adg_node_id": None,  # TODO: Populate from ADG in future wave
                "embedding_model": "fallback_hash_384",
                "ingested_at": None,  # Will be set during ingestion
            },
        }

    def _create_class_chunk(
        self,
        node,
        content: str,
        file_path: Path,
        module_name: str,
        layer: str,
    ) -> dict[str, Any]:
        """Create a chunk for a class."""
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)

        # Extract class source
        lines = content.split("\n")
        class_lines = lines[start_line - 1 : end_line]
        class_code = "\n".join(class_lines)

        # Create chunk ID
        chunk_id = hashlib.sha256(
            f"{file_path}:{module_name}:{node.name}:{start_line}:{class_code}".encode(),
        ).hexdigest()

        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)

        return {
            "id": chunk_id,
            "content": class_code,
            "metadata": {
                "file_path": str(file_path),
                "module": module_name,
                "layer": layer,
                "entity_type": "class",
                "name": node.name,
                "line_start": start_line,
                "line_end": end_line,
                "methods": methods if methods else [],
                "docstring": ast.get_docstring(node) or "",
                "type": "code",
                "adg_node_id": None,  # TODO: Populate from ADG in future wave
                "embedding_model": "fallback_hash_384",
                "ingested_at": None,  # Will be set during ingestion
            },
        }


def ingest_code(source_dir: str, collection_name: str = "repo_code_chunks", dry_run: bool = False):
    """Ingest Python code into ChromaDB using SovereignChromaClient.

    Args:
        source_dir: Source directory with Python files
        collection_name: ChromaDB collection name (default: repo_code_chunks)
        dry_run: If True, don't actually ingest (for testing)
    """
    import sqlite3
    from datetime import datetime

    # Initialize SovereignChromaClient
    chroma_client = SovereignChromaClient(persist_dir="artifacts/chromadb")

    logger.info(f"Using collection: {collection_name}")

    # Query ADG for node IDs (future wave - placeholder)
    # TODO: Query ADG SQLite to get node_id for each file
    adg_db_path = "artifacts/adg/adg_indexed_04062026_1246.sqlite"
    adg_node_map = {}
    if Path(adg_db_path).exists():
        try:
            conn = sqlite3.connect(adg_db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT id, resolved_path FROM nodes WHERE resolved_path LIKE ?", (f"%{source_dir}%",),
            )
            for row in cur.fetchall():
                adg_node_map[row["resolved_path"]] = row["id"]
            conn.close()
            logger.info(f"Loaded {len(adg_node_map)} ADG node mappings")
        except Exception as e:
            logger.warning(f"Could not load ADG node mappings: {e}")

    # Find Python files
    source_path = Path(source_dir)
    python_files = []

    for py_file in source_path.rglob("*.py"):
        # Skip unwanted directories
        if any(skip in str(py_file) for skip in ["__pycache__", ".pytest_cache", ".mypy_cache", "_compat"]):
            continue

        # Skip test files
        if "test" in py_file.name.lower():
            continue

        python_files.append(py_file)

    logger.info(f"Found {len(python_files)} Python files")

    # Chunk files
    chunker = CodeChunker()
    all_chunks = []

    for py_file in python_files:
        logger.info(f"Processing: {py_file}")
        chunks = chunker.chunk_file(py_file)
        # Add ADG node ID if available
        file_path_str = str(py_file)
        adg_node_id = adg_node_map.get(file_path_str)
        valid_chunks = []
        for chunk in chunks:
            chunk["metadata"]["adg_node_id"] = adg_node_id
            chunk["metadata"]["ingested_at"] = datetime.now().isoformat()
            # Validate metadata
            is_valid, errors = CodeChunker.validate_metadata(chunk["metadata"])
            if not is_valid:
                logger.warning(f"Metadata validation failed for {chunk['id']}: {errors}")
                continue
            valid_chunks.append(chunk)
        all_chunks.extend(valid_chunks)

    logger.info(f"Generated {len(all_chunks)} chunks from {len(python_files)} files")

    # ADG sync validation: verify node_id mapping coverage
    chunks_with_adg_id = sum(1 for c in all_chunks if c["metadata"].get("adg_node_id") is not None)
    coverage_pct = (chunks_with_adg_id / len(all_chunks) * 100) if all_chunks else 0
    logger.info(f"ADG node ID coverage: {chunks_with_adg_id}/{len(all_chunks)} ({coverage_pct:.1f}%)")
    if coverage_pct < 50:
        logger.warning(f"Low ADG node ID coverage ({coverage_pct:.1f}%). Consider regenerating ADG.")

    if dry_run:
        logger.info("DRY RUN - Not ingesting into ChromaDB")
        if all_chunks:
            logger.info(f"Preview chunk: {all_chunks[0]['metadata']['file_path']}")
            logger.info(f"Metadata sample: {all_chunks[0]['metadata']}")
        return

    # Ingest into ChromaDB using SovereignChromaClient
    logger.info("Ingesting into ChromaDB...")

    batch_size = 5000
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]

        ids = [chunk["id"] for chunk in batch]
        documents = [chunk["content"] for chunk in batch]
        metadatas = [chunk["metadata"] for chunk in batch]

        chroma_client.add_documents(
            collection_name=collection_name,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info(f"Successfully ingested batch {i // batch_size + 1}: {len(batch)} chunks")

    # Get collection stats
    stats = chroma_client.get_collection_stats(collection_name)
    stats["total_chunks"] = len(all_chunks)
    stats["vector_dimensions"] = 384  # SovereignChromaClient uses 384-dim fallback

    logger.info(f"Ingestion complete: {len(all_chunks)} chunks ingested")
    logger.info(f"Collection stats: {stats}")

    # Populate BM25 index during ingestion (not lazy rebuild)
    logger.info("Populating BM25 index...")
    bm25_store = get_bm25_store()
    bm25_docs = [
        {"id": chunk["id"], "text": chunk["content"], "metadata": chunk["metadata"]}
        for chunk in all_chunks
    ]
    bm25_store.add_documents(bm25_docs)
    logger.info(f"BM25 index populated with {len(bm25_docs)} documents")


def main():
    parser = argparse.ArgumentParser(description="Ingest Python code into ChromaDB")
    parser.add_argument("--source-dir", required=True, help="Source directory with Python files")
    parser.add_argument(
        "--collection-name",
        default="repo_code_chunks",
        help="ChromaDB collection name (default: repo_code_chunks)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't ingest)")

    args = parser.parse_args()

    ingest_code(
        source_dir=args.source_dir,
        collection_name=args.collection_name,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
