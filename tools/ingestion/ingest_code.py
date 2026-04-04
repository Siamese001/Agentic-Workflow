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

import chromadb
from chromadb.utils import embedding_functions

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeChunker:
    """AST-based code chunker for Python files."""

    def __init__(self):
        self.chunks = []

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
                        node, content, file_path, module_name, layer, is_async=True
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
        self, node, content: str, file_path: Path, module_name: str, layer: str, is_async: bool = False
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
            f"{file_path}:{module_name}:{node.name}:{start_line}:{func_code}".encode()
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
            },
        }

    def _create_class_chunk(
        self, node, content: str, file_path: Path, module_name: str, layer: str
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
            f"{file_path}:{module_name}:{node.name}:{start_line}:{class_code}".encode()
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
            },
        }


def ingest_code(source_dir: str, collection_name: str, mock_embeddings: bool = True, dry_run: bool = False):
    """Ingest Python code into ChromaDB."""

    # Initialize ChromaDB
    client = chromadb.PersistentClient("artifacts/chromadb")

    # Get or create collection
    try:
        collection = client.get_collection(collection_name)
        logger.info(f"Using existing collection: {collection_name}")
    except Exception:
        collection = client.create_collection(
            name=collection_name, metadata={"description": "Python source code chunks"}
        )
        logger.info(f"Created new collection: {collection_name}")

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
        all_chunks.extend(chunks)

    logger.info(f"Generated {len(all_chunks)} chunks from {len(python_files)} files")

    if dry_run:
        logger.info("DRY RUN - Not ingesting into ChromaDB")
        if all_chunks:
            logger.info(f"Preview chunk: {all_chunks[0]['metadata']['file_path']}")
        return

    # Generate embeddings
    logger.info("Generating embeddings...")

    if mock_embeddings:
        # Generate mock embeddings (1536 dimensions like OpenAI)
        embeddings = [[0.0] * 1536 for _ in all_chunks]
        logger.info(f"Generated {len(embeddings)} mock embeddings")
    else:
        # Use OpenAI embeddings
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-ada-002"
        )
        texts = [chunk["content"] for chunk in all_chunks]
        embeddings = openai_ef(texts)
        logger.info(f"Generated {len(embeddings)} OpenAI embeddings")

    # Ingest into ChromaDB
    logger.info("Ingesting into ChromaDB...")

    batch_size = 5000
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        batch_embeddings = embeddings[i : i + batch_size]

        ids = [chunk["id"] for chunk in batch]
        documents = [chunk["content"] for chunk in batch]
        metadatas = [chunk["metadata"] for chunk in batch]

        collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=batch_embeddings)

        logger.info(f"Successfully ingested batch {i // batch_size + 1}: {len(batch)} chunks")

    # Get collection stats
    stats = {
        "collection_name": collection_name,
        "total_chunks": collection.count(),
        "vector_dimensions": 1536,
        "vector_metric": "cosine",
    }

    logger.info(f"Ingestion complete: {len(all_chunks)} chunks ingested")
    logger.info(f"Collection stats: {stats}")


def main():
    parser = argparse.ArgumentParser(description="Ingest Python code into ChromaDB")
    parser.add_argument("--source-dir", required=True, help="Source directory with Python files")
    parser.add_argument("--collection-name", default="code", help="ChromaDB collection name")
    parser.add_argument("--mock-embeddings", action="store_true", default=True, help="Use mock embeddings")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't ingest)")
    parser.add_argument("--limit", type=int, help="Limit number of files to process")

    args = parser.parse_args()

    ingest_code(
        source_dir=args.source_dir,
        collection_name=args.collection_name,
        mock_embeddings=args.mock_embeddings,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
