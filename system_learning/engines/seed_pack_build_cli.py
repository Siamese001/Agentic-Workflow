"""Seed Pack Build CLI for Plan B Phase 5.

Command-line interface for building production semantic embedding packs.

Writes packs to:
  <base_path>\\seed_packs\\<namespace>\\<seed_index_version_hash>\\
Containing:
  row_index.jsonl
  embeddings.f32
  seed_manifest.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from agentic_core.embeddings.embedding_factory import create_embedding_client
from system_learning.engines.seed_embedding_pack_builder import build_seed_embedding_pack
from system_learning.types.seed_embedding_pack_types import SeedEmbeddingPackConfig


def _find_default_corpus_path(namespace: str) -> Path:
    """
    Best-effort resolver for Plan A canonical corpus location.

    This does NOT create files. It only searches within repo-relative `data/`.
    Priority is given to plausible canonical names.
    """
    candidates = [
        Path("data") / "corpus" / f"{namespace}_corpus.jsonl",
        Path("data") / "corpora" / f"{namespace}_corpus.jsonl",
        Path("data") / f"{namespace}_corpus.jsonl",
        Path("data") / f"{namespace}.jsonl",
    ]
    for p in candidates:
        if p.exists():
            return p

    # Fallback: search for any jsonl containing namespace token.
    data_root = Path("data")
    if data_root.exists():
        hits = sorted(data_root.rglob(f"*{namespace}*jsonl"))
        if hits:
            return hits[0]

    # Return first candidate for error message clarity.
    return candidates[0]


def load_canonical_corpus(namespace: str, corpus_path: Path | None = None) -> list[dict[str, Any]]:
    """Load canonical Plan A corpus for namespace.

    Args:
        namespace: Namespace to load corpus for.
        corpus_path: Optional explicit corpus path.

    Returns:
        List of corpus rows with required fields.

    Raises:
        FileNotFoundError: If corpus file not found.
        ValueError: If corpus format invalid.
    """
    corpus_path = corpus_path or _find_default_corpus_path(namespace)

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Corpus file not found: {corpus_path}. "
            f"Pass --corpus-path explicitly or place corpus under data/."
        )

    corpus_rows: list[dict[str, Any]] = []
    with open(corpus_path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in line {line_num}: {e}") from e

            # Validate required fields (B0 expectations)
            required_fields = ["content_hash", "trace_id", "namespace", "created_utc"]
            for field in required_fields:
                if field not in row:
                    raise ValueError(f"Missing required field '{field}' in line {line_num}")

            # Namespace must match requested namespace to avoid cross-contamination
            if str(row.get("namespace")) != namespace:
                raise ValueError(
                    f"Namespace mismatch in line {line_num}: "
                    f"expected '{namespace}', got '{row.get('namespace')}'"
                )

            corpus_rows.append(row)

    if not corpus_rows:
        raise ValueError(f"No corpus rows found for namespace: {namespace} at {corpus_path}")

    return corpus_rows


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Build production semantic embedding packs")
    parser.add_argument(
        "--base-path",
        required=True,
        help=r"Base directory for seed pack storage (e.g., C:\AgenticEmbeddings)",
    )
    parser.add_argument("--namespace", required=True, help="Namespace to build pack for")
    parser.add_argument(
        "--model",
        default="text-embedding-3-large",
        help="OpenAI model to use (default: text-embedding-3-large)",
    )
    parser.add_argument(
        "--provider", default="openai", choices=["openai"], help="Embedding provider to use (default: openai)"
    )
    parser.add_argument(
        "--dimensions",
        type=int,
        default=1536,
        help="Embedding dimensions to use (default: 1536 for OpenAI Matryoshka)",
    )
    parser.add_argument(
        "--bootstrap-mode",
        default="minimal_seed",
        choices=["minimal_seed", "curated_seed"],
        help="Bootstrap mode (default: minimal_seed)",
    )
    parser.add_argument(
        "--minimal-seed-count",
        type=int,
        default=None,
        help="Minimal seed count for minimal_seed mode",
    )
    parser.add_argument(
        "--corpus-path",
        default=None,
        help=r"Optional explicit path to corpus JSONL (e.g., data\corpus\healing_contexts_corpus.jsonl)",
    )

    args = parser.parse_args()

    # Validate / create base path
    base_path = Path(args.base_path)
    if not base_path.exists():
        print(f"Creating base directory: {base_path}")
        base_path.mkdir(parents=True, exist_ok=True)

    # Resolve corpus path (optional override)
    corpus_path = Path(args.corpus_path) if args.corpus_path else None

    try:
        # Load corpus
        resolved_corpus_path = corpus_path or _find_default_corpus_path(args.namespace)
        print(f"Loading corpus for namespace: {args.namespace}")
        print(f"corpus_path: {resolved_corpus_path}")
        corpus_rows = load_canonical_corpus(args.namespace, corpus_path=corpus_path)
        print(f"Loaded {len(corpus_rows)} corpus rows")

        # Initialize embedder
        print(f"Initializing OpenAI embedder with model: {args.model}")

        # Check if we should use test mode (no real API key)
        if os.getenv("OPENAI_API_KEY") == "sk-proj-YOUR_ACTUAL_API_KEY_HERE":
            print("WARNING: Using test mode with deterministic embedder (no real API calls)")
            from system_learning.engines.seed_embedding_pack_builder import DeterministicHashEmbedder

            embedder = DeterministicHashEmbedder(dimensions=args.dimensions)
        else:
            embedder = create_embedding_client(
                provider=args.provider, model=args.model, dimensions=args.dimensions
            )

        print(f"Model dimensions: {args.dimensions}")

        # Create config
        model_checksum = hashlib.sha256(
            f"{args.provider}_{args.model}_{args.dimensions}".encode()
        ).hexdigest()

        config = SeedEmbeddingPackConfig(
            namespace=args.namespace,
            bootstrap_mode=args.bootstrap_mode,
            minimal_seed_count=args.minimal_seed_count,
            embedding_model_version=args.model,
            embedding_model_checksum=model_checksum,
            canonicalization_version="v1",
        )

        # Build seed pack (NOTE: build_seed_embedding_pack is a function, not a builder object)
        print("Building seed pack...")
        built_at_utc = int(time.time())

        manifest = build_seed_embedding_pack(
            base_path=base_path,
            config=config,
            corpus_rows=corpus_rows,
            embedder=embedder,
            built_at_utc=built_at_utc,
        )

        # Output results
        output_path = base_path / "seed_packs" / args.namespace / manifest.seed_index_version_hash

        print("\n=== Build Complete ===")
        print(f"vector_count: {manifest.vector_count}")
        print(f"dimensions: {manifest.dimensions}")
        print(f"seed_index_version_hash: {manifest.seed_index_version_hash}")
        print(f"output_path: {output_path}")
        print("\nExpected files:")
        print(f"  {output_path}\\row_index.jsonl")
        print(f"  {output_path}\\embeddings.f32")
        print(f"  {output_path}\\seed_manifest.json")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
