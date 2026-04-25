#!/usr/bin/env python3
"""
Code Ingestion Script for ChromaDB
Ingests Python source code with AST-based chunking.
"""

import argparse
import ast
import hashlib
import logging
import os
import sqlite3

# Import SovereignChromaClient for centralized ChromaDB access
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core"))
from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str
from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient
from agentic_core.L4_state.utils.chunk_metadata import (
    build_canonical_digest,
    build_required,
    compute_source_sha,
    infer_layer,
    now_utc_iso,
    validate as validate_chunk_metadata,
)
from agentic_core.embeddings.bge_runtime import BGE_MODEL, BGE_QUERY_DIM
from agentic_core.L4_state.utils.memory.bm25_store import get_bm25_store
from tools.ingestion.contextual_chunk_builder import (
    ContextualChunkBuilder,
    ContextualizationRequest,
    prepend_context,
)
from tools.ingestion.late_chunking_helper import (
    apply_late_chunking,
    is_enabled_from_env_or_flag as late_chunking_enabled,
)

# Contextualization gateway selection (plan c0-context-assembly-best-practices-b7c3a1).
# Preference order (first non-None wins):
#   1. Qwen local vLLM (free, GPU-backed) — default when vLLM server reachable
#   2. Anthropic Claude (paid) — opt-in via CONTEXT_GATEWAY=anthropic env var
#   3. Heuristic fallback (no LLM) — when both above are unavailable/disabled
# See ``tools/ingestion/qwen_context_gateway.py`` and
# ``tools/ingestion/anthropic_context_gateway.py`` for factory contracts.
from tools.ingestion.anthropic_context_gateway import (
    build_from_env as build_anthropic_context_gateway,
)
from tools.ingestion.qwen_context_gateway import (
    build_from_env as build_qwen_context_gateway,
)


def _build_context_gateway() -> Any:
    """Resolve the preferred contextualization gateway per CONTEXT_GATEWAY env.

    Returns None when no gateway is available; callers treat that as "heuristic
    only" per the ``ContextualChunkBuilder`` contract.

    Env knob ``CONTEXT_GATEWAY`` values:
      * unset or "auto" (default) — try Qwen first, fall back to Anthropic if
        ANTHROPIC_API_KEY is set, else None (heuristic).
      * "qwen" — Qwen only; return None if vLLM unreachable (no Anthropic
        fallback, preserves $0 guarantee).
      * "anthropic" — Anthropic only; return None if key absent.
      * "none" / "heuristic" — skip all LLM gateways; force heuristic path.
    """
    choice = os.environ.get("CONTEXT_GATEWAY", "auto").lower()
    if choice in {"none", "heuristic", "off"}:
        return None
    if choice == "anthropic":
        return build_anthropic_context_gateway()
    if choice == "qwen":
        return build_qwen_context_gateway()
    # auto: prefer local/free path
    gw = build_qwen_context_gateway()
    if gw is not None:
        return gw
    return build_anthropic_context_gateway()


# Setup logging (needed by ADGNodeResolver below)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Repo root = 3 levels up from this file (tools/ingestion/ingest_code.py)
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _repo_relative(file_path: Path) -> str:
    """Return a POSIX-style repo-relative path for metadata stamping.

    Falls back to the basename when ``file_path`` sits outside the repo
    (e.g. synthetic fixtures in tests). Keeps ``infer_layer`` startswith
    checks working for L_APPS / L_TOOLS / L_OPS classifications.
    """
    fp = Path(file_path).resolve()
    try:
        rel = fp.relative_to(_REPO_ROOT)
    except ValueError:
        return fp.name
    return rel.as_posix()


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
            logger.warning(
                "ADGNodeResolver: snapshot not found at %s; node_id resolution disabled", self._path
            )
            return
        try:
            uri = f"file:{self._path.as_posix()}?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=10.0)
        except sqlite3.Error as exc:
            logger.warning("ADGNodeResolver: cannot open ADG (%s); node_id resolution disabled", exc)
            return
        try:
            cur = conn.execute(
                "SELECT id, adg_name, resolved_path FROM nodes WHERE adg_name IS NOT NULL AND adg_name != ''"
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
        "embedding_dim",
        "ingested_at",
        "parent_id",
        # Anthropic Contextual Retrieval: narrative context prepended to the
        # chunk content. Populated by _apply_contextualization when --contextualize
        # is passed to the ingest CLI.
        "chunk_context",
        # ChunkMetadataV1 contract fields (W2). Accepted alongside legacy keys
        # during the migration window; the authoritative validator is
        # ``agentic_core.L4_state.utils.chunk_metadata.validate``.
        "artifact_type",
        "source_path",
        "source_sha",
        "canonical_digest",
        "metadata_version",
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
        # W5.1-fix: accept the full canonical LAYER_TOKENS set from
        # chunk_metadata (L0-L6 plus L_APPS / L_TOOLS / L_OPS / L_SHARED /
        # L_SYSTEM_LEARNING / L_INFRASTRUCTURE / L_CONFIG / L_DOCS / L_TESTS /
        # L_UNKNOWN). Legacy ``Unknown`` (capital U) retained for back-compat.
        from agentic_core.L4_state.utils.chunk_metadata import LAYER_TOKENS

        if "layer" in metadata and metadata["layer"] not in (LAYER_TOKENS | {"Unknown"}):
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

            # Walk through AST nodes. W3.2: no longer skip zero-arg functions,
            # argless async, or methodless classes — they still carry docstrings
            # and are addressable by ADG node id, so coverage > filter.
            for node in ast.walk(tree):
                chunk = None

                if isinstance(node, ast.FunctionDef):
                    chunk = self._create_function_chunk(node, content, file_path, module_name, layer)
                elif isinstance(node, ast.ClassDef):
                    methods = [
                        item.name
                        for item in node.body
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]
                    chunk = self._create_class_chunk(node, content, file_path, module_name, layer)
                    class_chunks[node.name] = (chunk["id"], set(methods))
                elif isinstance(node, ast.AsyncFunctionDef):
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

        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
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

        # Stamp ChunkMetadataV1 contract: stable source_path / canonical_digest
        # drives idempotent upsert; legacy file_path + type preserved for
        # pre-W2 retrieval consumers during migration.
        entity_type = "async_function" if is_async else "function"
        # W5.1-fix: source_path MUST be repo-relative so ``infer_layer``
        # startswith-checks resolve to L_APPS / L_TOOLS / L_OPS etc. instead
        # of falling through to L_UNKNOWN on absolute Windows paths.
        source_path = _repo_relative(file_path)
        try:
            source_sha = compute_source_sha(file_path)
        except OSError:
            source_sha = compute_source_sha(content.encode("utf-8"))
        canonical_digest = build_canonical_digest(
            artifact_type="code_chunk",
            source_path=source_path,
            anchor=f"{entity_type}:{node.name}:{start_line}",
        )

        contract = build_required(
            artifact_type="code_chunk",
            source_path=source_path,
            source_sha=source_sha,
            canonical_digest=canonical_digest,
            # W5.1-fix: ``_detect_layer`` is a naïve substring matcher that
            # mis-labels ``apps_shared/types/state_*.py`` as L4 etc. Trust
            # ``infer_layer`` (path-prefix) as the single canonical source.
            layer=infer_layer(source_path),
            embedding_model=BGE_MODEL,
            embedding_dim=BGE_QUERY_DIM,
        )
        contract.update(
            {
                "entity_type": entity_type,
                "name": node.name,
                "line_start": start_line,
                "line_end": end_line,
                "args": [arg.arg for arg in node.args.args] if node.args.args else [],
                "docstring": ast.get_docstring(node) or "",
                "module": module_name,
                "adg_node_id": self.adg_resolver.resolve(file_path, node.name)
                if self.adg_resolver is not None
                else None,
                # Legacy aliases for pre-W2 consumers; drop in W5 cleanup.
                "file_path": source_path,
                "type": "code",
            }
        )
        return {
            "id": canonical_digest,
            "content": func_code,
            "metadata": contract,
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

        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)

        # Stamp ChunkMetadataV1 contract (see _create_function_chunk).
        source_path = _repo_relative(file_path)
        try:
            source_sha = compute_source_sha(file_path)
        except OSError:
            source_sha = compute_source_sha(content.encode("utf-8"))
        canonical_digest = build_canonical_digest(
            artifact_type="code_chunk",
            source_path=source_path,
            anchor=f"class:{node.name}:{start_line}",
        )

        contract = build_required(
            artifact_type="code_chunk",
            source_path=source_path,
            source_sha=source_sha,
            canonical_digest=canonical_digest,
            # W5.1-fix: ``_detect_layer`` is a naïve substring matcher that
            # mis-labels ``apps_shared/types/state_*.py`` as L4 etc. Trust
            # ``infer_layer`` (path-prefix) as the single canonical source.
            layer=infer_layer(source_path),
            embedding_model=BGE_MODEL,
            embedding_dim=BGE_QUERY_DIM,
        )
        contract.update(
            {
                "entity_type": "class",
                "name": node.name,
                "line_start": start_line,
                "line_end": end_line,
                "methods": methods if methods else [],
                "docstring": ast.get_docstring(node) or "",
                "module": module_name,
                "adg_node_id": self.adg_resolver.resolve(file_path, node.name)
                if self.adg_resolver is not None
                else None,
                # Legacy aliases for pre-W2 consumers; drop in W5 cleanup.
                "file_path": source_path,
                "type": "code",
            }
        )
        return {
            "id": canonical_digest,
            "content": class_code,
            "metadata": contract,
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
    if builder is None:
        # Resolve preferred gateway (Qwen local vLLM by default, Anthropic
        # opt-in, heuristic when neither available). See _build_context_gateway.
        builder = ContextualChunkBuilder(gateway=_build_context_gateway())
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
    late_chunking: bool = False,
):
    """Ingest Python code into ChromaDB using SovereignChromaClient.

    Args:
        source_dir: Source directory with Python files
        collection_name: ChromaDB collection name (default: repo_code_chunks)
        dry_run: If True, don't actually ingest (for testing)
        contextualize: Prepend LLM-generated chunk context (ADR-045 main path).
        late_chunking: Use Jina Late Chunking embedder (ADR-045 Alternative 5)
            instead of the default per-chunk BGE embedding. Stacks with
            contextualize. Can also be enabled via ``LATE_CHUNKING=1`` env.
    """
    import sqlite3
    from datetime import datetime

    # Initialize SovereignChromaClient against the canonical persist_dir SSOT.
    chroma_client = SovereignChromaClient(persist_dir=canonical_persist_dir_str())

    logger.info(f"Using collection: {collection_name}")

    # Query ADG for node IDs. The snapshot path is resolved at runtime from
    # `artifacts/adg/adg_indexed_*.sqlite` (newest by mtime) so the ChromaDB
    # corpus never binds to a stale ADG snapshot. Override via env var
    # `ADG_SNAPSHOT_PATH`. See tools/ingestion/_adg_snapshot.py (W1.4).
    from tools.ingestion._adg_snapshot import latest_adg_snapshot

    adg_db_path_obj = latest_adg_snapshot()
    adg_node_map: dict[str, int] = {}
    if adg_db_path_obj is not None and adg_db_path_obj.exists():
        logger.info("Using ADG snapshot: %s", adg_db_path_obj)
        try:
            conn = sqlite3.connect(str(adg_db_path_obj))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT id, resolved_path FROM nodes WHERE resolved_path LIKE ?",
                (f"%{source_dir}%",),
            )
            for row in cur.fetchall():
                adg_node_map[row["resolved_path"]] = row["id"]
            conn.close()
            logger.info("Loaded %d ADG node mappings", len(adg_node_map))
        except sqlite3.Error as exc:
            logger.warning("Could not load ADG node mappings: %s", exc)
    else:
        logger.warning(
            "No ADG snapshot found under artifacts/adg/adg_indexed_*.sqlite; "
            "adg_node_id will be null for all chunks. Run: python tools/generate_full_adg.py"
        )

    # Build ADGNodeResolver so per-chunk adg_node_id resolution works (W2.4).
    # Previously CodeChunker() was constructed without an ADG resolver, so
    # every chunk got adg_node_id=None regardless of ADG health.
    adg_resolver = ADGNodeResolver(adg_db_path_obj) if adg_db_path_obj else None

    # Find Python files.
    # W5.1-fix: ``--source-dir`` may be relative (e.g. ``apps_rg``) when the
    # pipeline dispatches multi-root stages. Resolve against CWD so every
    # downstream ``file_path.relative_to(REPO_ROOT)`` call sees an absolute
    # path under the repo, rather than erroring with "not in the subpath".
    source_path = Path(source_dir)
    if not source_path.is_absolute():
        source_path = (Path.cwd() / source_path).resolve()
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
    chunker = CodeChunker(adg_resolver=adg_resolver)
    all_chunks = []

    for py_file in python_files:
        logger.info(f"Processing: {py_file}")
        chunks = chunker.chunk_file(py_file)
        # Add ADG node ID if available
        file_path_str = str(py_file)
        adg_node_id = adg_node_map.get(file_path_str)
        valid_chunks = []
        for chunk in chunks:
            # Fill adg_node_id only if the per-file map has it and the chunk
            # did not already resolve one via ADGNodeResolver.
            if adg_node_id is not None and chunk["metadata"].get("adg_node_id") is None:
                chunk["metadata"]["adg_node_id"] = adg_node_id
            # Refresh ingested_at to the actual ingestion timestamp (UTC ISO).
            chunk["metadata"]["ingested_at"] = now_utc_iso()

            # Legacy per-chunker validator (kept for the required_fields check).
            is_valid, errors = CodeChunker.validate_metadata(chunk["metadata"])
            if not is_valid:
                logger.warning("Legacy metadata validation failed for %s: %s", chunk["id"], errors)
                continue

            # ChunkMetadataV1 contract validator — promote to warning-for-now so
            # a single drift doesn't lose the whole batch. Upgrade to hard-fail
            # in W2.3 once the full pipeline re-run is green.
            contract_errors = validate_chunk_metadata(chunk["metadata"])
            if contract_errors:
                logger.warning(
                    "ChunkMetadataV1 drift for %s: %s",
                    chunk["id"],
                    contract_errors,
                )

            valid_chunks.append(chunk)
        all_chunks.extend(valid_chunks)

    logger.info(f"Generated {len(all_chunks)} chunks from {len(python_files)} files")

    # Anthropic Contextual Retrieval enrichment (opt-in).
    # When enabled, generates a 50-100 token narrative context per chunk and
    # prepends it to the chunk content + records it in metadata.chunk_context.
    # Uses heuristic fallback when no Anthropic gateway is wired (offline-safe).
    if contextualize:
        # Announce which contextualization backend is active so operators can
        # distinguish free local runs from paid API runs from heuristic-only.
        gateway = _build_context_gateway()
        if gateway is None:
            mode = "HEURISTIC (metadata-only, no LLM)"
        else:
            gw_name = type(gateway).__name__
            mode = f"GATEWAY ({gw_name})"
        logger.info("Contextualizing chunks — mode=%s", mode)
        builder = ContextualChunkBuilder(gateway=gateway)
        enriched = _apply_contextualization(all_chunks, builder=builder)
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

    # Optional: Jina Late Chunking (ADR-045 Alt-5). Computes per-chunk
    # embeddings up front from single full-doc encoder passes. When enabled,
    # we pass the pre-computed vectors to SovereignChromaClient so it
    # doesn't re-embed the (possibly contextualized) chunk text. Returns
    # None on unavailability -> default path takes over.
    late_enabled = late_chunking_enabled(late_chunking)
    precomputed_embeddings: list[list[float]] | None = None
    if late_enabled:
        logger.info(
            "Late chunking ENABLED \u2014 embedding %d chunks via single-pass encoder per file",
            len(all_chunks),
        )
        precomputed_embeddings = apply_late_chunking(all_chunks)
        if precomputed_embeddings is None:
            logger.warning("Late chunking returned None (deps unavailable); falling back to default embedder")
        elif len(precomputed_embeddings) != len(all_chunks):
            logger.error(
                "Late chunking output length (%d) != chunks (%d); falling back",
                len(precomputed_embeddings),
                len(all_chunks),
            )
            precomputed_embeddings = None

    # Ingest into ChromaDB using SovereignChromaClient
    logger.info("Ingesting into ChromaDB...")

    batch_size = 5000
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]

        ids = [chunk["id"] for chunk in batch]
        documents = [chunk["content"] for chunk in batch]
        metadatas = [chunk["metadata"] for chunk in batch]
        batch_embeddings = (
            precomputed_embeddings[i : i + batch_size] if precomputed_embeddings is not None else None
        )

        chroma_client.add_documents(
            collection_name=collection_name,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=batch_embeddings,
        )

        logger.info(f"Successfully ingested batch {i // batch_size + 1}: {len(batch)} chunks")

    # Get collection stats
    stats = chroma_client.get_collection_stats(collection_name)
    stats["total_chunks"] = len(all_chunks)
    stats["embedding_model"] = BGE_MODEL
    stats["vector_dimensions"] = BGE_QUERY_DIM

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
    parser.add_argument(
        "--late-chunking",
        action="store_true",
        help=(
            "Use Jina Late Chunking (ADR-045 Alt-5) to embed each chunk from "
            "a single full-doc encoder pass, giving each chunk cross-chunk "
            "context at no LLM cost. Stacks with --contextualize. Can also "
            "be enabled via LATE_CHUNKING=1 env var."
        ),
    )

    args = parser.parse_args()

    ingest_code(
        source_dir=args.source_dir,
        collection_name=args.collection_name,
        dry_run=args.dry_run,
        contextualize=args.contextualize,
        late_chunking=args.late_chunking,
    )


if __name__ == "__main__":
    main()
