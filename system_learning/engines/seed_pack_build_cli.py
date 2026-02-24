"""Seed Pack Build CLI for Plan B Phase 5.

Command-line interface for building production semantic embedding packs.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from system_learning.engines.openai_embedder import OpenAIEmbedder
from system_learning.engines.seed_embedding_pack_builder import (
    SeedEmbeddingPackBuilder,
)
from system_learning.types.seed_embedding_pack_types import (
    SeedEmbeddingPackConfig,
)


def load_canonical_corpus(namespace: str) -> list[dict[str, any]]:
    """Load canonical Plan A corpus for namespace.
    
    Args:
        namespace: Namespace to load corpus for.
        
    Returns:
        List of corpus rows with required fields.
        
    Raises:
        FileNotFoundError: If corpus file not found.
        ValueError: If corpus format invalid.
    """
    # This is a placeholder - in production, this would load from
    # the actual Plan A corpus storage location
    corpus_path = Path(f"data/corpus/{namespace}_corpus.jsonl")
    
    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Corpus file not found: {corpus_path}. "
            f"Ensure corpus exists for namespace: {namespace}"
        )
    
    corpus_rows = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                row = json.loads(line)
                # Validate required fields
                required_fields = ["content_hash", "trace_id", "namespace", "created_utc"]
                for field in required_fields:
                    if field not in row:
                        raise ValueError(
                            f"Missing required field '{field}' in line {line_num}"
                        )
                
                corpus_rows.append(row)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in line {line_num}: {e}"
                )
    
    if not corpus_rows:
        raise ValueError(f"No corpus rows found for namespace: {namespace}")
    
    return corpus_rows


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Build production semantic embedding packs"
    )
    parser.add_argument(
        "--base-path",
        required=True,
        help="Base directory for seed pack storage (e.g., C:\\AgenticEmbeddings)"
    )
    parser.add_argument(
        "--namespace",
        required=True,
        help="Namespace to build pack for"
    )
    parser.add_argument(
        "--model",
        default="text-embedding-3-large",
        help="OpenAI model to use (default: text-embedding-3-large)"
    )
    parser.add_argument(
        "--bootstrap-mode",
        default="full",
        choices=["full", "minimal_seed", "curated_seed"],
        help="Bootstrap mode (default: full)"
    )
    parser.add_argument(
        "--minimal-seed-count",
        type=int,
        default=None,
        help="Minimal seed count for minimal_seed mode"
    )
    
    args = parser.parse_args()
    
    # Validate base path
    base_path = Path(args.base_path)
    if not base_path.exists():
        print(f"Creating base directory: {base_path}")
        base_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load corpus
        print(f"Loading corpus for namespace: {args.namespace}")
        corpus_rows = load_canonical_corpus(args.namespace)
        print(f"Loaded {len(corpus_rows)} corpus rows")
        
        # Initialize embedder
        print(f"Initializing OpenAI embedder with model: {args.model}")
        embedder = OpenAIEmbedder(model=args.model)
        model_info = embedder.get_model_info()
        print(f"Model dimensions: {model_info['dimensions']}")
        
        # Create config
        config = SeedEmbeddingPackConfig(
            namespace=args.namespace,
            bootstrap_mode=args.bootstrap_mode,
            minimal_seed_count=args.minimal_seed_count,
            embedding_model_version=args.model,
            embedding_model_checksum=embedder.get_model_checksum(),
            canonicalization_version="v1",
            dimensions=model_info['dimensions'],
        )
        
        # Build seed pack
        print("Building seed pack...")
        builder = SeedEmbeddingPackBuilder()
        built_at_utc = int(time.time())
        
        manifest = builder.build(
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
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
