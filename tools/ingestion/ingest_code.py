#!/usr/bin/env python3
"""
Code Ingestion Script for ChromaDB
Ingests Python source code with AST-based chunking.
"""

import argparse
import ast
import hashlib
import logging
import sqlite3

# Import SovereignChromaClient for centralized ChromaDB access
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core"))
from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient
from agentic_core.L4_state.utils.memory.bm25_store import get_bm25_store
from tools.ingestion.contextual_chunk_builder import (
    ContextualChunkBuilder,
    ContextualizationRequest,
    prepend_context,
)

# Setup logging (needed by ADGNodeResolver below)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ADGNodeResolver:
    """Resolve ingest chunks to ADG node ids for cross-index joinability.

    Builds a single in-memory index keyed by ``(resolved_path_basename, adg_name)``
    from the ADG SQLite snapshot so per-chunk lookup is O(1). If the ADG db is
    missing or unreadable the resolver degrades gracefully to returning ``None``
    — this keeps ingestion resilient to snapshot regeneration windows.

    Wave E plan: ``.windsurf/plans/wave-e-adg-card-projection-2df148.md`` (µW6).
    """

    def __init__(self, adg_db_path: str | Path | None):
        self._by_path_name: dict[tuple[str, str], int] = {}
        self._by_name: dict[str, int] = {}
        self._loaded = False
        self._path = Path(adg_db_path) if adg_db_path else None
        if self._path is not None:
            self._load()

    def _load(self) -> None:
        assert self._path is not None
        if not self._path.exists():
            logger.warning("ADGNodeResolver: snapshot not found at %s; node_id resolution disabled", self._path)
            return
        try:
            uri = f"file:{self._path.as_posix()}?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=10.0)
        except sqlite3.Error as exc:
            logger.warning("ADGNodeResolver: cannot open ADG (%s); node_id resolution disabled", exc)
            return
        try:
            cur = conn.execute(
                "SELECT id, adg_name, resolved_path FROM nodes"
                " WHERE adg_name IS NOT NULL AND adg_name != ''"
            )
            # ADG ``adg_name`` uses qualified forms like
            # ``ADG::Symbol::pkg.sub.module.ClassName`` or
            # ``ADG::Module::path/to/file.py``. Chunks emitted from ingest_code
            # know only the terminal symbol name, so we index by the tail
            # after the final ``.`` or ``::`` and keep the (file_basename, tail)
            # pair as primary key.
            for node_id, adg_name, resolved_path in cur:
                name_str = str(adg_name)
                tail = name_str.rsplit(".", 1)[-1].rsplit("::", 1)[-1]
                if tail and tail not in self._by_name:
                    self._by_name[tail] = node_id
                if resolved_path and tail:
                    key = (Path(str(resolved_path)).name, tail)
                    self._by_path_name.setdefault(key, node_id)
            self._loaded = True
            logger.info(
                "ADGNodeResolver: indexed %d (path,name) pairs from %s",
                len(self._by_path_name),
                self._path.name,
            )
        finally:
            conn.close()

    def resolve(self, file_path: Path, name: str) -> int | None:
        """Return the ADG node id for ``name`` in ``file_path``, if known."""

        if not self._loaded:
            return None
        key = (file_path.name, name)
        node_id = self._by_path_name.get(key)
        if node_id is not None:
            return node_id
        # Fallback: exact adg_name match anywhere (looser; only used when the
        # file-scoped lookup misses — e.g. renamed or moved files). None is
        # preferable to a wrong id, so we only fall back when unambiguous.
        return self._by_name.get(name)


class CodeChunker:
    """AST-based code chunker for Python files."""

    # Metadata schema for validation
    REQUIRED_METADATA_FIELDS = {
        "file_path",
        "module",
        "layer",
        "entity_type",
        "name",
        "line_start",
        "line_end",
        "type",
    }
    OPTIONAL_METADATA_FIELDS = {
        "args",
        "docstring",
        "methods",
        "adg_node_id",
        "embedding_model",
        "ingested_at",
        "parent_id",
        # Anthropic Contextual Retrieval: narrative context prepended to the
        # chunk content. Populated by _apply_contextualization when --contextualize
        # is passed to the ingest CLI.
        "chunk_context",
    }

    def __init__(self, adg_resolver: ADGNodeResolver | None = None):
        self.chunks = []
        self.parent_child_map = {}  # chunk_id -> parent_chunk_id
        # Optional ADG resolver — when present, function/class chunks carry
        # the ADG node id so retrieval can join chunk metadata against the
        # semantic card indexes emitted by project_adg_cards.py.
        self.adg_resolver = adg_resolver

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
        if "layer" in metadata and metadata["layer"] not in [
            "L0",
            "L1",
            "L2",
            "L3",
            "L4",
            "L5",
            "L6",
            "Unknown",
        ]:
            errors.append(f"Invalid layer: {metadata['layer']}")
        if "entity_type" in metadata and metadata["entity_type"] not in [
            "function",
            "async_function",
            "class",
            "module",
        ]:
            errors.append(f"Invalid entity_type: {metadata['entity_type']}")

        return (len(errors) == 0, errors)

    def chunk_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Chunk a Python file using AST."""
        self.parent_child_map = {}  # Reset for each file
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

            # Track class chunks for parent-child relationships
            class_chunks = {}  # class_name -> (chunk_id, methods_set)

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
                    class_chunks[node.name] = (chunk["id"], set(methods))
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
                    # Track parent-child: if function is a method, set parent class
                    if chunk["metadata"]["entity_type"] in ["function", "async_function"]:
                        func_name = chunk["metadata"]["name"]
                        for class_id, methods_set in class_chunks.values():
                            if func_name in methods_set:
                                self.parent_child_map[chunk["id"]] = class_id
                                chunk["metadata"]["parent_id"] = class_id
                                break

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
                "adg_node_id": self.adg_resolver.resolve(file_path, node.name)
                if self.adg_resolver is not None
                else None,
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
                "adg_node_id": self.adg_resolver.resolve(file_path, node.name)
                if self.adg_resolver is not None
                else None,
                "embedding_model": "fallback_hash_384",
                "ingested_at": None,  # Will be set during ingestion
            },
        }


def _apply_contextualization(
    all_chunks: list[dict[str, Any]],
    *,
    builder: ContextualChunkBuilder | None = None,
) -> int:
    """Enrich chunks in-place with Anthropic-style narrative context.

    For each chunk, reads the full source file, generates a 50-100 token
    contextual sentence (via the injected builder — gateway-backed when an
    Anthropic adapter is provided, heuristic fallback otherwise), prepends
    the context to ``chunk["content"]``, and writes it back onto the chunk
    metadata under ``chunk_context``.

    Files are read at most ONCE across all their chunks via an in-memory
    cache keyed by file_path.

    Returns the number of chunks enriched with a non-empty context.
    """
    builder = builder or ContextualChunkBuilder()
    file_cache: dict[str, str] = {}
    enriched = 0
    for chunk in all_chunks:
        metadata = chunk.get("metadata", {}) or {}
        file_path = metadata.get("file_path")
        if not file_path:
            continue
        if file_path not in file_cache:
            try:
                file_cache[file_path] = Path(file_path).read_text(encoding="utf-8", errors="replace")
            except (OSError, ValueError) as exc:
                logger.warning("Skip contextualization for %s: %s", file_path, exc)
                file_cache[file_path] = ""
        document = file_cache[file_path]
        if not document:
            continue
        request = ContextualizationRequest(
            document=document,
            chunk=chunk.get("content", ""),
            metadata=metadata,
        )
        result = builder.build(request)
        if not result.context:
            continue
        metadata["chunk_context"] = result.context
        chunk["content"] = prepend_context(chunk.get("content", ""), result.context)
        chunk["metadata"] = metadata
        enriched += 1
    return enriched


def ingest_code(
    source_dir: str,
    collection_name: str = "repo_code_chunks",
    dry_run: bool = False,
    contextualize: bool = False,
):
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
                "SELECT id, resolved_path FROM nodes WHERE resolved_path LIKE ?",
                (f"%{source_dir}%",),
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

    # Anthropic Contextual Retrieval enrichment (opt-in).
    # When enabled, generates a 50-100 token narrative context per chunk and
    # prepends it to the chunk content + records it in metadata.chunk_context.
    # Uses heuristic fallback when no Anthropic gateway is wired (offline-safe).
    if contextualize:
        logger.info("Contextualizing chunks (Anthropic-style narrative context)...")
        enriched = _apply_contextualization(all_chunks)
        logger.info(f"Contextualized {enriched}/{len(all_chunks)} chunks")

    # Log parent-child relationship statistics
    total_parent_child = sum(1 for c in all_chunks if c["metadata"].get("parent_id") is not None)
    if total_parent_child > 0:
        logger.info(
            f"Parent-child relationships: {total_parent_child}/{len(all_chunks)} chunks have parent_id"
        )

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
        {"id": chunk["id"], "text": chunk["content"], "metadata": chunk["metadata"]} for chunk in all_chunks
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
    parser.add_argument(
        "--contextualize",
        action="store_true",
        help=(
            "Enrich chunks with Anthropic-style narrative context (50-100 tok) "
            "before embedding/BM25 indexing. Heuristic fallback when no gateway "
            "is wired; live Claude calls when a gateway is injected."
        ),
    )

    args = parser.parse_args()

    ingest_code(
        source_dir=args.source_dir,
        collection_name=args.collection_name,
        dry_run=args.dry_run,
        contextualize=args.contextualize,
    )


if __name__ == "__main__":
    main()
