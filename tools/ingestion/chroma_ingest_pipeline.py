"""Dry-run-safe ingestion pipeline for the process_docs Chroma collection.

W6 (chroma-graphrag-core-wiring-gaps-b3f7a1) implementation.

GAP-07: Provide a safe, operator-controlled pipeline for ingesting documents
into the process_docs Chroma collection using BAAI/bge-m3 embeddings.

Safety invariants (mandatory):
  - --dry-run is the safe default.  Running without --execute never writes data.
  - --execute must be passed explicitly for any write operation.
  - dry-run exits 0 and creates NO Chroma collections.
  - dry-run writes NO vectors and NO durable state.
  - Collection name is hard-coded to process_docs (W6 target).
  - Embedding model is BAAI/bge-m3, 1024 dimensions.
  - No L4 runtime state is written — this pipeline is a tooling-layer operator
    script, not a runtime path.

Usage::

    # Safe by default (dry-run — inspect without writing):
    python -m tools.ingestion.chroma_ingest_pipeline --input /path/to/docs

    # Execute ingestion (requires explicit flag):
    python -m tools.ingestion.chroma_ingest_pipeline \\
        --input /path/to/docs \\
        --chromadb-path /path/to/chroma \\
        --execute
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COLLECTION_NAME: str = "process_docs"
EMBEDDING_MODEL: str = "BAAI/bge-m3"
EMBEDDING_DIMENSIONS: int = 1024


# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------


def _load_embedding_model() -> Any:
    """Lazy-load SentenceTransformer("BAAI/bge-m3").

    Raises ImportError with install hint if sentence-transformers is missing.
    """
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "chroma_ingest_pipeline requires sentence-transformers. "
            "Install with: pip install sentence-transformers>=2.2.0"
        ) from exc
    _log.info("[chroma_ingest_pipeline] loading model %s", EMBEDDING_MODEL)
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_text(model: Any, text: str) -> list[float]:
    """Produce a 1024-dim BAAI/bge-m3 embedding for text."""
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


# ---------------------------------------------------------------------------
# Document loading (minimal; operator supplies pre-chunked JSON lines)
# ---------------------------------------------------------------------------


def load_documents(input_path: Path) -> list[dict[str, Any]]:
    """Load documents from a JSON-lines file.

    Each line must be a JSON object with at least:
        - "id": str
        - "text": str
        - "metadata": dict (optional; scalar values only for Chroma)

    Args:
        input_path: Path to the .jsonl file.

    Returns:
        List of document dicts.
    """
    docs: list[dict[str, Any]] = []
    with input_path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"chroma_ingest_pipeline: malformed JSON on line {lineno} "
                    f"in {input_path}: {exc}"
                ) from exc
            if "id" not in doc or "text" not in doc:
                raise ValueError(
                    f"chroma_ingest_pipeline: document on line {lineno} missing "
                    f"required keys 'id' and/or 'text'"
                )
            docs.append(doc)
    return docs


# ---------------------------------------------------------------------------
# Dry-run report
# ---------------------------------------------------------------------------


def dry_run_report(docs: list[dict[str, Any]]) -> None:
    """Print a dry-run summary to stdout. No collections, no writes."""
    print("[DRY RUN] chroma_ingest_pipeline — no data written")
    print(f"  collection : {COLLECTION_NAME}")
    print(f"  model      : {EMBEDDING_MODEL} ({EMBEDDING_DIMENSIONS} dims)")
    print(f"  documents  : {len(docs)}")
    if docs:
        preview_ids = [d["id"] for d in docs[:5]]
        print(f"  first ids  : {preview_ids}")
    print("[DRY RUN] complete — exit 0, no Chroma collection created")


# ---------------------------------------------------------------------------
# Live ingestion (requires --execute)
# ---------------------------------------------------------------------------


def run_ingestion(
    docs: list[dict[str, Any]],
    chromadb_path: str,
    batch_size: int = 64,
) -> int:
    """Ingest documents into the process_docs Chroma collection.

    Args:
        docs: List of document dicts from load_documents().
        chromadb_path: On-disk path for PersistentClient.
        batch_size: Number of documents per Chroma add() call.

    Returns:
        Number of documents ingested.
    """
    try:
        import chromadb  # type: ignore[import]
    except ImportError as exc:
        raise RuntimeError(
            "chroma_ingest_pipeline requires chromadb. "
            "Install with: pip install chromadb"
        ) from exc

    model = _load_embedding_model()
    client = chromadb.PersistentClient(path=chromadb_path)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    _log.info(
        "[chroma_ingest_pipeline] ingesting %d docs into %s at %s",
        len(docs), COLLECTION_NAME, chromadb_path,
    )

    total = 0
    for batch_start in range(0, len(docs), batch_size):
        batch = docs[batch_start: batch_start + batch_size]
        ids = [d["id"] for d in batch]
        texts = [d["text"] for d in batch]
        embeddings = [embed_text(model, t) for t in texts]
        metadatas = [d.get("metadata", {}) for d in batch]
        # Ensure all metadata values are Chroma-compatible scalars
        safe_metas = [
            {k: str(v) if not isinstance(v, (str, int, float, bool)) else v
             for k, v in m.items()}
            for m in metadatas
        ]
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=safe_metas,
        )
        total += len(batch)
        _log.info(
            "[chroma_ingest_pipeline] ingested batch %d–%d (%d total)",
            batch_start + 1, batch_start + len(batch), total,
        )

    return total


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chroma_ingest_pipeline",
        description=(
            "Dry-run-safe ingestion pipeline for the process_docs Chroma collection "
            "(BAAI/bge-m3, 1024 dims). Default mode is --dry-run. "
            "Pass --execute to write data."
        ),
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to JSON-lines file of documents to ingest.",
    )
    parser.add_argument(
        "--chromadb-path",
        type=str,
        default=None,
        help="On-disk Chroma persistent client path. Required when --execute is set.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help=(
            "Execute real ingestion. Without this flag the pipeline runs in dry-run mode "
            "and creates no collections, writes no vectors, and writes no durable state."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Explicit dry-run flag (default behaviour; provided for clarity in scripts).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Documents per Chroma add() batch (default: 64).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point.  Returns exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)

    # Determine effective mode: dry-run unless --execute is explicit
    is_dry_run = not args.execute

    if is_dry_run:
        # Dry-run: safe path — no Chroma, no writes, no model load
        docs: list[dict[str, Any]] = []
        if args.input is not None:
            if not args.input.exists():
                print(
                    f"[DRY RUN] WARNING: --input path does not exist: {args.input}",
                    file=sys.stderr,
                )
            else:
                try:
                    docs = load_documents(args.input)
                except (ValueError, OSError) as exc:
                    print(f"[DRY RUN] ERROR loading documents: {exc}", file=sys.stderr)
                    return 1
        dry_run_report(docs)
        return 0

    # --execute path — operator intent required
    if args.chromadb_path is None:
        print(
            "ERROR: --chromadb-path is required when --execute is set.",
            file=sys.stderr,
        )
        return 2

    if args.input is None:
        print(
            "ERROR: --input is required when --execute is set.",
            file=sys.stderr,
        )
        return 2

    if not args.input.exists():
        print(f"ERROR: --input path does not exist: {args.input}", file=sys.stderr)
        return 2

    try:
        docs = load_documents(args.input)
    except (ValueError, OSError) as exc:
        print(f"ERROR loading documents: {exc}", file=sys.stderr)
        return 1

    ingested = run_ingestion(
        docs=docs,
        chromadb_path=args.chromadb_path,
        batch_size=args.batch_size,
    )
    print(
        f"[chroma_ingest_pipeline] complete: {ingested} documents ingested "
        f"into '{COLLECTION_NAME}' at {args.chromadb_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
