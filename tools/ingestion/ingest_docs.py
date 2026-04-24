#!/usr/bin/env python3
"""
Document Ingestion Pipeline for Vector DB Population

Ingests markdown documents from docs/ directory into ChromaDB vector store
with proper chunking, metadata extraction, and OpenAI embeddings.

Usage:
    python tools/ingestion/ingest_docs.py [--source-dir docs/] [--collection-name docs]
"""

import argparse
import fnmatch
import hashlib
import json
import logging
import os
import random
import re
import sys
from pathlib import Path

import chromadb
from openai import OpenAI

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# W6.2 (plan anthropic-rag-gaps-7f3c2a): imports at module scope so the
# ``--contextualize`` branch below can reference them without conditional
# scoping. Placed AFTER the ``sys.path`` insertion above because this
# module depends on the ``tools`` package being resolvable when
# ingest_docs.py is invoked as a script (not just via ``-m``).
from tools.ingestion.contextual_chunk_builder import (  # noqa: E402 — see comment above
    ContextualChunkBuilder,
    ContextualizationRequest,
    prepend_context,
)

# G1-residual (plan c0-context-assembly-best-practices-b7c3a1): gateway
# adapter so the existing Claude-generated contextual-retrieval path becomes
# reachable. build_from_env() returns None when ANTHROPIC_API_KEY is absent,
# which preserves the heuristic-only baseline for offline / CI runs.
from tools.ingestion.anthropic_context_gateway import (  # noqa: E402 — see above
    build_from_env as build_anthropic_context_gateway,
)
from tools.ingestion.late_chunking_helper import (  # noqa: E402 — see above
    apply_late_chunking,
    is_enabled_from_env_or_flag as late_chunking_enabled,
)

try:
    from agentic_core.L4_state.config.memory_store_config import MemoryStoreConfig
except ImportError:
    # memory_store_config is untracked infra; fall back to a minimal shim
    # that exposes only the attribute we actually consume (VECTOR_METRIC).
    class MemoryStoreConfig:  # type: ignore[no-redef]
        VECTOR_METRIC = "cosine"

from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str
from agentic_core.L4_state.utils.chunk_metadata import (
    build_canonical_digest,
    build_required,
    compute_source_sha,
    infer_layer,
    now_utc_iso,
    validate as validate_chunk_metadata,
)

# Import embedding factory for BGE-M3 support via the sovereignty-allowlisted
# bridge. Running as __main__ cannot call the factory directly — see
# tools/ingestion/_embedding_factory_bridge.py for the rationale.
try:
    from tools.ingestion._embedding_factory_bridge import create_embedding_client

    EMBEDDING_FACTORY_AVAILABLE = True
except ImportError:
    EMBEDDING_FACTORY_AVAILABLE = False
    logging.warning("Embedding factory bridge not available - BGE-M3 support disabled")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
Logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunks markdown documents by section headers with metadata preservation."""

    def __init__(self, min_chunk_size: int = 200, max_chunk_size: int = 1000):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.header_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def chunk_document(
        self,
        file_path: Path,
        *,
        embedding_model: str | None = None,
        embedding_dim: int | None = None,
    ) -> list[dict]:
        """Split a markdown document into ChunkMetadataV1-compliant chunks."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except OSError as exc:
            Logger.error("Failed to read %s: %s", file_path, exc)
            return []

        base_metadata = self._extract_metadata(
            file_path,
            content,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
        )
        source_path = base_metadata["source_path"]
        sections = self._split_by_headers(content)

        chunks: list[dict] = []
        current_section = "Introduction"

        def _emit(chunk_content: str, section: str, subsection: str, sub_ix: int) -> None:
            anchor = f"{section}/{subsection}:{sub_ix}"
            chunk_meta = base_metadata.copy()
            chunk_meta.update(
                {
                    "section": section,
                    "subsection": subsection,
                    "chunk_type": "section",
                    "canonical_digest": build_canonical_digest(
                        artifact_type="doc_chunk",
                        source_path=source_path,
                        anchor=anchor,
                    ),
                }
            )
            chunks.append({"content": chunk_content, "metadata": chunk_meta})

        for section_title, section_content in sections:
            if not section_content.strip():
                continue
            if len(section_content) > self.max_chunk_size:
                for sub_ix, sub_chunk in enumerate(
                    self._split_large_section(section_content, current_section)
                ):
                    _emit(sub_chunk, current_section, section_title, sub_ix)
            else:
                _emit(section_content, current_section, section_title, 0)
            current_section = section_title

        return chunks

    def _extract_metadata(
        self,
        file_path: Path,
        content: str,
        *,
        embedding_model: str | None = None,
        embedding_dim: int | None = None,
    ) -> dict:
        """Build a ChunkMetadataV1-compliant base metadata dict for a doc.

        The returned dict carries every REQUIRED contract field plus the
        doc-specific OPTIONAL keys (doc_id / doc_type / category). Per-chunk
        section / subsection / canonical_digest fields are layered on top by
        :meth:`chunk_document`.
        """
        base_path = Path.cwd().resolve()
        try:
            relative_path = str(file_path.relative_to(base_path)).replace("\\", "/")
        except ValueError:
            relative_path = file_path.name

        # Doc-type inference (unchanged from legacy behaviour).
        doc_type = "unknown"
        if "architecture" in relative_path:
            doc_type = "architecture"
        elif "reports" in relative_path:
            doc_type = "report"
        elif "specs" in relative_path:
            doc_type = "specification"
        elif "policies" in relative_path:
            doc_type = "policy"
        elif "contracts" in relative_path:
            doc_type = "contract"
        elif "runbooks" in relative_path:
            doc_type = "runbook"
        elif Path(relative_path).name == "README.md":
            doc_type = "readme"

        # Layer: prefer the SSOT path-based inferrer. Only override with an
        # embedded L<N> marker when inference returned L_UNKNOWN / L_DOCS and
        # the path literally contains a layer tag.
        layer = infer_layer(relative_path)
        if layer in {"L_DOCS", "L_UNKNOWN"}:
            for tag in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
                if tag in relative_path:
                    layer = tag
                    break

        try:
            source_sha = compute_source_sha(file_path)
        except OSError:
            source_sha = compute_source_sha(content.encode("utf-8"))

        # canonical_digest and canonical chunk_id are filled per-chunk later
        # (each chunk needs its own anchor). Stamp a placeholder here that
        # ``chunk_document`` overwrites.
        contract = build_required(
            artifact_type="doc_chunk",
            source_path=relative_path,
            source_sha=source_sha,
            canonical_digest="pending",
            layer=layer,
            embedding_model=embedding_model or "BAAI/bge-m3",
            embedding_dim=embedding_dim or 1024,
        )
        contract.update(
            {
                "doc_id": relative_path,
                "doc_type": doc_type,
                "category": self._determine_category(doc_type, layer),
                # Legacy aliases.
                "file_path": relative_path,
                "created_date": now_utc_iso(),
            }
        )
        return contract

    def _determine_category(self, doc_type: str, layer: str) -> str:
        """Determine document category."""
        if doc_type in ["architecture", "specification"]:
            return "technical"
        elif doc_type in ["report", "policy"]:
            return "governance"
        elif doc_type == "readme":
            return "overview"
        elif doc_type == "runbook":
            return "operations"
        else:
            return "general"

    def _split_by_headers(self, content: str) -> list[tuple[str, str]]:
        """Split content by markdown headers."""
        lines = content.split("\n")
        sections = []
        current_title = "Introduction"
        current_lines = []

        for line in lines:
            header_match = self.header_pattern.match(line)
            if header_match:
                # Save previous section
                if current_lines:
                    sections.append((current_title, "\n".join(current_lines)))

                # Start new section
                current_title = header_match.group(2).strip()
                current_lines = []
            else:
                current_lines.append(line)

        # Save last section
        if current_lines:
            sections.append((current_title, "\n".join(current_lines)))

        return sections

    def _split_large_section(self, content: str, section_title: str) -> list[str]:
        """Split a large section into smaller chunks."""
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= self.max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks


class EmbeddingGenerator:
    """Generates embeddings using OpenAI API, BGE-M3, or mock embeddings for testing."""

    def __init__(
        self,
        model: str = "text-embedding-ada-002",
        mock_embeddings: bool = False,
        embedding_provider: str = "openai",
    ):
        self.model = model
        self.mock_embeddings = mock_embeddings
        self.embedding_provider = embedding_provider
        self.embedding_client = None
        self.vector_dimensions = 1536  # Default for OpenAI

        if mock_embeddings:
            Logger.info("Using mock embeddings for testing")
            self.vector_dimensions = 1536
        elif embedding_provider == "bge-m3":
            if not EMBEDDING_FACTORY_AVAILABLE:
                raise ValueError("Embedding factory not available. Cannot use BGE-M3 provider.")
            Logger.info("Using BGE-M3 embeddings via embedding factory")
            self.embedding_client = create_embedding_client("bge-m3")
            self.vector_dimensions = getattr(self.embedding_client, "observed_dimension", 1024)
            Logger.info(f"BGE-M3 client initialized with {self.vector_dimensions} dimensions")
        else:
            # Default OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable not set. "
                    "Please set it with: export OPENAI_API_KEY=your_key_here "
                    "or use --mock-embeddings for testing "
                    "or use --embedding-provider bge-m3 for local embeddings",
                )
            self.client = OpenAI(api_key=api_key)
            self.vector_dimensions = 1536

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if self.mock_embeddings:
            # Generate mock embeddings
            Logger.info(f"Generating {len(texts)} mock embeddings ({self.vector_dimensions}d)")
            return [[random.uniform(-1, 1) for _ in range(self.vector_dimensions)] for _ in texts]

        if self.embedding_provider == "bge-m3" and self.embedding_client:
            return self._generate_bge_m3_embeddings(texts)

        return self._generate_openai_embeddings(texts)

    def _generate_bge_m3_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using BGE-M3 via embedding factory."""
        if not texts:
            return []

        Logger.info(f"Generating {len(texts)} BGE-M3 embeddings")

        # Use the underlying model directly for batch encoding.
        # NO silent fallback: a failure here must raise — zero vectors corrupt
        # cosine similarity and silently poison every downstream retrieval.
        model = self.embedding_client.model
        encoded = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        )
        if encoded is None or len(encoded) != len(texts):
            raise RuntimeError(
                f"BGE_EMBED_FAILED: expected {len(texts)} rows, "
                f"got {0 if encoded is None else len(encoded)}"
            )
        if encoded.shape[1] != self.vector_dimensions:
            raise RuntimeError(
                f"BGE_DIM_MISMATCH: expected {self.vector_dimensions}, "
                f"got {encoded.shape[1]}"
            )
        embeddings = [[float(x) for x in emb] for emb in encoded.tolist()]
        Logger.info(f"Successfully generated {len(embeddings)} BGE-M3 embeddings")
        return embeddings

    def _generate_openai_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using OpenAI API."""
        embeddings = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            # NO silent fallback: zero vectors silently corrupt cosine similarity.
            response = self.client.embeddings.create(model=self.model, input=batch)
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
            Logger.info(f"Generated embeddings for batch {i // batch_size + 1}")
        return embeddings


class VectorDBIngestor:
    """Handles ingestion into ChromaDB vector store."""

    def __init__(
        self,
        collection_name: str = "docs",
        persist_directory: str = None,
        vector_dimensions: int = 1536,
    ):
        self.collection_name = collection_name
        self.config = MemoryStoreConfig()
        self.vector_dimensions = vector_dimensions

        # Initialize ChromaDB client with persistent storage
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            # Default to the canonical ChromaDB persist dir (data/cache/chromadb).
            persist_dir = Path(canonical_persist_dir_str())
            persist_dir.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(persist_dir))

        try:
            self.collection = self.client.get_or_create_collection(name=collection_name)
            Logger.info(f"Initialized ChromaDB collection: {collection_name} ({vector_dimensions}d)")
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            Logger.error(f"Failed to initialize ChromaDB collection '{collection_name}': {e}")
            raise

    def ingest_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> int:
        """Ingest chunks and embeddings into ChromaDB."""
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []

        # Idempotent chunk IDs: use canonical_digest so re-ingest of the same
        # doc at the same revision upserts cleanly (W2 / G7 fix). Previously
        # the loop index leaked into the ID, causing duplicate chunks on
        # every re-run.
        for chunk in chunks:
            meta = chunk["metadata"]
            # Stamp ingestion timestamp + run V1 contract validator.
            meta["ingested_at"] = now_utc_iso()
            errors = validate_chunk_metadata(meta)
            if errors:
                Logger.warning(
                    "ChunkMetadataV1 drift for %s: %s",
                    meta.get("canonical_digest", "<no-digest>"),
                    errors,
                )
            ids.append(meta["canonical_digest"])
            documents.append(chunk["content"])
            metadatas.append(meta)

        # Add to ChromaDB in batches to handle size limits
        batch_size = 5000  # ChromaDB default limit
        total_ingested = 0

        for i in range(0, len(chunks), batch_size):
            batch_ids = ids[i : i + batch_size]
            batch_documents = documents[i : i + batch_size]
            batch_metadatas = metadatas[i : i + batch_size]
            batch_embeddings = embeddings[i : i + batch_size]

            try:
                self.collection.add(
                    ids=batch_ids,
                    documents=batch_documents,
                    metadatas=batch_metadatas,
                    embeddings=batch_embeddings,
                )
                batch_count = len(batch_ids)
                total_ingested += batch_count
                Logger.info(f"Successfully ingested batch {i // batch_size + 1}: {batch_count} chunks")
            except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                Logger.error(f"Failed to ingest batch {i // batch_size + 1}: {e}")
                # Continue with next batch instead of failing completely

        Logger.info(f"Successfully ingested {total_ingested} chunks into ChromaDB")
        return total_ingested

    def get_collection_stats(self) -> dict:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "vector_dimensions": self.vector_dimensions,
                "vector_metric": self.config.VECTOR_METRIC,
            }
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            Logger.error(f"Failed to get collection stats: {e}")
            return {}


def find_markdown_files(source_dir: Path, exclude_patterns: list[str] = None) -> list[Path]:
    """Find all markdown files in the source directory."""
    if exclude_patterns is not None and not isinstance(exclude_patterns, list):
        raise TypeError(f"exclude_patterns must be a list, got {type(exclude_patterns).__name__}")

    source_dir = source_dir.resolve()
    markdown_files = []
    exclude_patterns = exclude_patterns or []

    for file_path in source_dir.rglob("*.md"):
        # Skip certain directories
        if any(skip in str(file_path) for skip in [".git", "__pycache__", "node_modules"]):
            continue

        # Check exclude glob patterns
        rel_path = file_path.relative_to(source_dir)
        excluded = False
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(str(file_path), pattern):
                excluded = True
                break

        if not excluded:
            markdown_files.append(file_path.resolve())

    return sorted(markdown_files)


def main():
    parser = argparse.ArgumentParser(description="Ingest markdown documents into ChromaDB")
    parser.add_argument("--source-dir", default="docs", help="Source directory containing markdown files")
    parser.add_argument("--collection-name", default="docs", help="ChromaDB collection name")
    parser.add_argument("--dry-run", action="store_true", help="Preview without ingesting")
    parser.add_argument("--mock-embeddings", action="store_true", help="Use mock embeddings for testing")
    parser.add_argument(
        "--embedding-provider",
        default="openai",
        choices=["openai", "bge-m3"],
        help="Embedding provider to use",
    )
    parser.add_argument(
        "--exclude-glob",
        action="append",
        help="Glob pattern to exclude (can be used multiple times)",
    )
    parser.add_argument("--limit", type=int, help="Limit number of files to process (for testing)")
    parser.add_argument(
        "--contextualize",
        action="store_true",
        help=(
            "Rewrite each chunk with an Anthropic Contextual Retrieval prefix "
            "(50-100 tokens of document-level context) before embedding. "
            "Mirrors the --contextualize path on ingest_code.py. See plan "
            "anthropic-rag-gaps-7f3c2a phase W6.2."
        ),
    )
    parser.add_argument(
        "--late-chunking",
        action="store_true",
        help=(
            "Use Jina Late Chunking (ADR-045 Alt-5): embed each chunk from a "
            "single full-doc encoder pass instead of in isolation. Stacks "
            "with --contextualize. Can also be enabled via LATE_CHUNKING=1."
        ),
    )

    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        Logger.error(f"Source directory {source_dir} does not exist")
        return 1

    # Find markdown files
    markdown_files = find_markdown_files(source_dir, args.exclude_glob)
    if args.limit:
        markdown_files = markdown_files[: args.limit]

    Logger.info(f"Found {len(markdown_files)} markdown files to process")

    # Initialize components
    chunker = DocumentChunker()
    embedding_generator = EmbeddingGenerator(
        mock_embeddings=args.mock_embeddings,
        embedding_provider=args.embedding_provider,
    )
    ingestor = VectorDBIngestor(args.collection_name, vector_dimensions=embedding_generator.vector_dimensions)

    # Process documents.
    # W6.2 (plan anthropic-rag-gaps-7f3c2a): when --contextualize is set,
    # lazily construct one ContextualChunkBuilder and feed each (document,
    # chunk) pair through it. Contextualization happens PER FILE (while the
    # file has already been read into memory for chunking) to avoid a second
    # file-system pass. Failures are logged and skipped — contextualization
    # is best-effort enrichment, never fatal to ingestion.
    all_chunks = []
    total_files = 0
    context_builder = None
    enriched_count = 0
    if args.contextualize:
        # G1-residual: inject the Anthropic gateway adapter when
        # ANTHROPIC_API_KEY is set. When absent, build_from_env returns None
        # and ContextualChunkBuilder falls back to the heuristic path —
        # matching the prior unreachable-Claude-path behaviour, but now with
        # a clear log line so operators know which mode is active.
        gateway = build_anthropic_context_gateway()
        context_builder = ContextualChunkBuilder(gateway=gateway)
        mode = "GATEWAY (Claude-generated)" if gateway is not None else "HEURISTIC (metadata-only)"
        Logger.info(
            "Contextualization ENABLED — mode=%s — each chunk will be prefixed with document-level context.",
            mode,
        )

    for file_path in markdown_files:
        Logger.info(f"Processing: {file_path}")
        chunks = chunker.chunk_document(file_path)

        if context_builder is not None and chunks:
            try:
                document_text = Path(file_path).read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                Logger.warning("Skip contextualization for %s: %s", file_path, exc)
                document_text = ""
            if document_text:
                for chunk in chunks:
                    metadata = chunk.get("metadata", {}) or {}
                    request = ContextualizationRequest(
                        document=document_text,
                        chunk=chunk.get("content", ""),
                        metadata=metadata,
                    )
                    result = context_builder.build(request)
                    if not result.context:
                        continue
                    metadata["chunk_context"] = result.context
                    chunk["content"] = prepend_context(chunk.get("content", ""), result.context)
                    chunk["metadata"] = metadata
                    enriched_count += 1

        all_chunks.extend(chunks)
        total_files += 1

        if len(chunks) == 0:
            Logger.warning(f"No chunks generated from {file_path}")

    Logger.info(f"Generated {len(all_chunks)} chunks from {total_files} files")
    if args.contextualize:
        Logger.info(
            f"Contextualization complete: {enriched_count}/{len(all_chunks)} chunks enriched."
        )

    if args.dry_run:
        Logger.info("DRY RUN - Not ingesting into ChromaDB")
        for chunk in all_chunks[:3]:  # Show first 3 chunks as preview
            Logger.info(f"Preview chunk: {chunk['metadata']['doc_id']}")
        return 0

    # Generate embeddings. Jina Late Chunking (ADR-045 Alt-5) replaces the
    # default per-chunk embedder with a single full-doc encoder pass when
    # --late-chunking (or LATE_CHUNKING=1) is active. Falls back to the
    # default path on any failure (returns None).
    late_enabled = late_chunking_enabled(args.late_chunking)
    embeddings = None
    if late_enabled:
        Logger.info(
            "Late chunking ENABLED \u2014 embedding %d chunks via single-pass encoder per file",
            len(all_chunks),
        )
        embeddings = apply_late_chunking(all_chunks)
        if embeddings is None:
            Logger.warning("Late chunking returned None; falling back to default embedder")
        elif len(embeddings) != len(all_chunks):
            Logger.error(
                "Late chunking length mismatch (%d vs %d); falling back",
                len(embeddings),
                len(all_chunks),
            )
            embeddings = None
    if embeddings is None:
        Logger.info("Generating embeddings...")
        texts = [chunk["content"] for chunk in all_chunks]
        embeddings = embedding_generator.generate_embeddings(texts)

    # Ingest into ChromaDB
    Logger.info("Ingesting into ChromaDB...")
    ingested_count = ingestor.ingest_chunks(all_chunks, embeddings)

    # Show final stats
    stats = ingestor.get_collection_stats()
    Logger.info(f"Ingestion complete: {ingested_count} chunks ingested")
    Logger.info(f"Collection stats: {json.dumps(stats, indent=2)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
