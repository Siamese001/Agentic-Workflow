"""Late-chunking helper for ingest_code.py and ingest_docs.py (Wave C).

Turns a list of ingest chunks into a list of pre-computed BGE-M3 embeddings
using the Jina Late Chunking technique (single full-doc encoder pass, pool
token vectors into per-chunk vectors). Shipped as a helper rather than
embedded inline in each ingest script so both ingest_code and ingest_docs
can call it with the same semantics and the same error handling.

Shape contract
--------------
Input:  ordered list of chunks. Each chunk is a dict with at minimum:
        {"id": str, "content": str, "metadata": {...}}. ``metadata`` MAY
        carry "file_path" (ingest_code) or "source_path" (ingest_docs) or
        "doc_id" (ingest_docs legacy). We try all three in that order.
        Chunks that lack file_path OR whose content cannot be re-located
        inside the file fall back to per-chunk ``bge_embed_query``.

Output: list of embeddings in the SAME ORDER as the input chunks. Every
        input chunk maps to exactly one output vector. When late chunking
        is fully unavailable (LateChunkingUnavailable raised), the helper
        returns ``None`` so the caller can delegate to the standard embedder.

Invariants
----------
* Never raises outwards: either returns embeddings, returns None (force
  default path), or returns a list whose failed entries came from the
  fallback bge_embed_query path.
* Reads each source file at most once (in-memory cache keyed by absolute
  path). Matches ``_apply_contextualization``'s caching discipline.
* File locating chunks inside the source text uses the FIRST occurrence
  of ``chunk["content"]`` in the file. For AST-chunked Python this is
  unambiguous; for markdown the first occurrence is the correct one as
  long as chunks don't repeat verbatim (which they don't in the shipped
  DocumentChunker).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _resolve_source_path(metadata: dict[str, Any]) -> Path | None:
    """Try the three known source-path keys in a deterministic order.

    ingest_code stamps ``file_path``; ingest_docs' V1 metadata has
    ``source_path``; older ingest_docs rows carry ``doc_id`` = filename.
    """
    for key in ("file_path", "source_path", "doc_id"):
        value = metadata.get(key)
        if not value:
            continue
        candidate = Path(str(value))
        if candidate.exists():
            return candidate
    return None


def _locate_chunk_span(
    doc_text: str,
    chunk_content: str,
) -> tuple[int, int] | None:
    """Return (start, end) char offsets of ``chunk_content`` in ``doc_text``.

    Returns None when the chunk can't be found verbatim. This happens when
    the caller has already mutated ``chunk["content"]`` (e.g. contextualization
    prefixed a narrative to it). Caller falls back to per-chunk embedding.
    """
    if not chunk_content:
        return None
    idx = doc_text.find(chunk_content)
    if idx < 0:
        return None
    return idx, idx + len(chunk_content)


def apply_late_chunking(
    chunks: list[dict[str, Any]],
) -> list[list[float]] | None:
    """Compute late-chunked embeddings for ``chunks`` in input order.

    Returns:
        * list[list[float]] — one embedding per input chunk, same order.
        * None — late chunking unavailable (dep missing); caller falls back
          to the default embedding path.
    """
    try:
        from agentic_core.knowledge.retrieval.late_chunking import (  # noqa: PLC0415
            ChunkSpan,
            LateChunkingEmbedder,
            LateChunkingUnavailable,
        )
    except ImportError as exc:
        logger.warning("Late chunking module unavailable: %s; skipping", exc)
        return None

    try:
        embedder = LateChunkingEmbedder()
    except LateChunkingUnavailable as exc:
        logger.warning("Late chunking backends unavailable: %s; skipping", exc)
        return None

    # Group chunks by source file so we make one encoder pass per file.
    # ``file_order`` preserves first-seen ordering so the per-file batches
    # are reproducible across runs.
    file_cache: dict[str, str] = {}
    file_order: list[str] = []
    per_file_spans: dict[str, list[tuple[str, ChunkSpan]]] = {}
    fallback_ids: set[str] = set()

    for chunk in chunks:
        chunk_id = str(chunk.get("id") or "")
        if not chunk_id:
            fallback_ids.add(chunk_id)
            continue
        metadata = chunk.get("metadata", {}) or {}
        src_path = _resolve_source_path(metadata)
        if src_path is None:
            fallback_ids.add(chunk_id)
            continue
        key = str(src_path.resolve())
        if key not in file_cache:
            try:
                file_cache[key] = src_path.read_text(encoding="utf-8", errors="replace")
                file_order.append(key)
                per_file_spans[key] = []
            except OSError as exc:
                logger.warning("Late chunking skip %s: %s", src_path, exc)
                fallback_ids.add(chunk_id)
                continue
        doc_text = file_cache[key]
        span = _locate_chunk_span(doc_text, chunk.get("content", ""))
        if span is None:
            fallback_ids.add(chunk_id)
            continue
        per_file_spans[key].append(
            (chunk_id, ChunkSpan(chunk_id=chunk_id, start=span[0], end=span[1]))
        )

    # Run the embedder once per file, collect the {chunk_id: vector} map.
    all_vectors: dict[str, list[float]] = {}
    for key in file_order:
        spans = per_file_spans[key]
        if not spans:
            continue
        chunk_spans = [cs for _, cs in spans]
        try:
            vectors = embedder.embed_chunks_from_doc(file_cache[key], chunk_spans)
        except (RuntimeError, ValueError, LateChunkingUnavailable) as exc:
            logger.warning(
                "Late chunking failed for %s (%s); falling back for its %d chunks",
                key,
                exc,
                len(spans),
            )
            for cid, _ in spans:
                fallback_ids.add(cid)
            continue
        all_vectors.update(vectors)

    # For any chunk we couldn't late-chunk (missing file, relocate miss,
    # embedder error), fall back to the standard per-chunk embedder so the
    # output list is fully populated and shape-aligned.
    if fallback_ids:
        from agentic_core.embeddings.bge_runtime import bge_embed_query  # noqa: PLC0415

        for chunk in chunks:
            chunk_id = str(chunk.get("id") or "")
            if chunk_id not in fallback_ids:
                continue
            content = (chunk.get("content") or "").strip()
            if not content:
                all_vectors[chunk_id] = [0.0] * 1024
                continue
            try:
                all_vectors[chunk_id] = bge_embed_query(content)
            except (RuntimeError, ValueError) as exc:
                logger.warning(
                    "Per-chunk embed fallback failed for %s: %s; emitting zero vector",
                    chunk_id,
                    exc,
                )
                all_vectors[chunk_id] = [0.0] * 1024

    # Emit in input order so the caller can pass the result straight to
    # ``SovereignChromaClient.add_documents(embeddings=...)``.
    out: list[list[float]] = []
    for chunk in chunks:
        chunk_id = str(chunk.get("id") or "")
        vec = all_vectors.get(chunk_id)
        if vec is None:
            # Shape safety: should never happen given the fallback logic
            # above, but belt-and-suspenders for the "missing id" edge case.
            logger.warning("Late chunking: no vector for chunk id=%s; zero vector", chunk_id)
            out.append([0.0] * 1024)
        else:
            out.append(vec)
    return out


def is_enabled_from_env_or_flag(cli_flag: bool) -> bool:
    """Resolve the late-chunking enable signal from CLI flag + env fallback.

    Precedence: explicit CLI --late-chunking wins; else LATE_CHUNKING=1 env.
    Keeps the decision path in one place so ingest_code and ingest_docs
    make the same call.
    """
    if cli_flag:
        return True
    import os  # noqa: PLC0415 — local import so module stays env-free at import

    return os.environ.get("LATE_CHUNKING", "").strip().lower() in {"1", "true", "yes", "on"}


__all__ = ["apply_late_chunking", "is_enabled_from_env_or_flag"]
