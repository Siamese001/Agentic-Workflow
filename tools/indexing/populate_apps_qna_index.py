"""Populate apps_qna interview card index with BGE-M3 embeddings.

ETL pipeline:
1. Generate 110 interview card variants (22 cards × 5 archetypes)
2. Embed all variants using BGE-M3 (1024 dimensions)
3. Create seed pack (embeddings.f32, row_index.jsonl, seed_manifest.json)
4. Populate active index (index.json, manifest.json, meta.json)

Usage:
    python tools/indexing/populate_apps_qna_index.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.embedders import get_embedder
from tools.indexing import generate_corpus

if TYPE_CHECKING:
    from tools.indexing.interview_card_corpus import InterviewCard

_LOGGER = logging.getLogger(__name__)

# Paths
INDEX_BASE = Path("C:/AgenticEmbeddings")
SEED_PACKS_DIR = INDEX_BASE / "seed_packs" / "apps_qna_interview_cards"
INDEXES_DIR = INDEX_BASE / "indexes" / "apps_qna_interview_cards"

# Model config
MODEL_NAME = "BAAI/bge-m3"
EXPECTED_DIMS = 1024


def _compute_content_hash(text: str) -> str:
    """Compute SHA-256 hash of content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _compute_matrix_hash(embeddings: list[list[float]]) -> str:
    """Compute hash of embedding matrix for integrity verification."""
    hasher = hashlib.sha256()
    for vec in embeddings:
        for val in vec:
            hasher.update(struct.pack("<f", val))
    return hasher.hexdigest()


def embed_corpus(corpus: list[InterviewCard], show_progress: bool = True) -> list[list[float]]:
    """Embed all cards in corpus using BGE-M3.

    Args:
        corpus: List of interview cards
        show_progress: Whether to show progress bar

    Returns:
        List of 1024-dimensional embeddings
    """
    embedder = get_embedder()

    if not embedder.is_available():
        raise RuntimeError(
            "BGE-M3 embedder not available. "
            "Install: pip install sentence-transformers"
        )

    texts = [card.question_text for card in corpus]
    _LOGGER.info(f"Embedding {len(texts)} cards with BGE-M3...")

    embeddings = embedder.embed_batch(texts, show_progress=show_progress)

    # Validate
    failed = sum(1 for e in embeddings if len(e) != EXPECTED_DIMS)
    if failed > 0:
        raise RuntimeError(f"{failed} embeddings failed (returned wrong dimensions)")

    _LOGGER.info(f"Successfully embedded {len(embeddings)} cards")
    return embeddings


def create_seed_pack(
    corpus: list[InterviewCard],
    embeddings: list[list[float]],
    force: bool = False,
) -> Path:
    """Create seed pack directory with embedded corpus.

    Args:
        corpus: Interview cards
        embeddings: BGE-M3 embeddings
        force: Overwrite existing seed pack

    Returns:
        Path to created seed pack directory
    """
    # Compute version hash from matrix content
    matrix_hash = _compute_matrix_hash(embeddings)
    seed_pack_dir = SEED_PACKS_DIR / matrix_hash[:64]

    if seed_pack_dir.exists() and not force:
        _LOGGER.info(f"Seed pack already exists: {seed_pack_dir}")
        return seed_pack_dir

    seed_pack_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write embeddings as binary f32 array
    embeddings_path = seed_pack_dir / "embeddings.f32"
    with open(embeddings_path, "wb") as f:
        for vec in embeddings:
            for val in vec:
                f.write(struct.pack("<f", val))
    _LOGGER.info(f"Wrote embeddings: {embeddings_path} ({len(embeddings)} vectors)")

    # 2. Write row index
    row_index_path = seed_pack_dir / "row_index.jsonl"
    with open(row_index_path, "w", encoding="utf-8") as f:
        for i, card in enumerate(corpus):
            row = {
                "content_hash": _compute_content_hash(card.question_text),
                "created_utc": int(datetime.now(timezone.utc).timestamp()),
                "namespace": "apps_qna",
                "row_id": card.interview_slug,
                "trace_id": f"card_{i:04d}",
                "card_id": card.card_id,
                "base_card_type": card.base_card_type,
                "archetype": card.archetype,
                "expected_evidence": card.expected_evidence,
            }
            f.write(json.dumps(row) + "\n")
    _LOGGER.info(f"Wrote row index: {row_index_path}")

    # 3. Write seed manifest
    seed_manifest = {
        "bootstrap_mode": "full_corpus",
        "built_at_utc": int(datetime.now(timezone.utc).timestamp()),
        "canonicalization_version": "v1",
        "dimensions": EXPECTED_DIMS,
        "embedding_model_checksum": hashlib.sha256(MODEL_NAME.encode()).hexdigest()[:16],
        "embedding_model_version": MODEL_NAME,
        "matrix_hash": matrix_hash,
        "namespace": "apps_qna",
        "row_index_hash": _compute_content_hash(row_index_path.read_text()),
        "seed_index_version_hash": matrix_hash[:64],
        "vector_count": len(corpus),
    }
    manifest_path = seed_pack_dir / "seed_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(seed_manifest, f, indent=2)
    _LOGGER.info(f"Wrote seed manifest: {manifest_path}")

    return seed_pack_dir


def populate_active_index(
    seed_pack_dir: Path,
    corpus: list[InterviewCard],
    embeddings: list[list[float]],
) -> None:
    """Populate the active index from seed pack.

    Args:
        seed_pack_dir: Path to seed pack directory
        corpus: Interview cards
        embeddings: BGE-M3 embeddings
    """
    INDEXES_DIR.mkdir(parents=True, exist_ok=True)

    # Compute hashes
    matrix_hash = _compute_matrix_hash(embeddings)
    meta_hash = hashlib.sha256(
        json.dumps({"dims": EXPECTED_DIMS, "model": MODEL_NAME}, sort_keys=True).encode()
    ).hexdigest()

    # 1. Write index.json (flat index for now — can be upgraded to HNSW)
    index_data = {
        "index_type": "flat",
        "distance_metric": "cosine",
        "vectors": [
            {
                "id": card.interview_slug,
                "embedding": vec,
                "metadata": {
                    "card_id": card.card_id,
                    "base_card_type": card.base_card_type,
                    "archetype": card.archetype,
                    "expected_evidence": card.expected_evidence,
                },
            }
            for card, vec in zip(corpus, embeddings)
        ],
    }
    index_path = INDEXES_DIR / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)
    _LOGGER.info(f"Wrote active index: {index_path}")

    # 2. Write manifest.json
    manifest = {
        "dims": EXPECTED_DIMS,
        "embedder_id": MODEL_NAME,
        "model_version": MODEL_NAME,
        "schema_version": "1",
        "sha256_index": matrix_hash,
        "sha256_meta_canonical": meta_hash,
        "vector_count": len(corpus),
    }
    manifest_path = INDEXES_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    _LOGGER.info(f"Wrote manifest: {manifest_path}")

    # 3. Write meta.json
    meta = {
        "dims": EXPECTED_DIMS,
        "embedder_id": MODEL_NAME,
        "index_id": "apps_qna_interview_cards",
        "index_version_hash": matrix_hash[:64],
        "model_version": MODEL_NAME,
        "schema_version": "1",
        "vector_count": len(corpus),
    }
    meta_path = INDEXES_DIR / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    _LOGGER.info(f"Wrote meta: {meta_path}")


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Populate apps_qna interview card index")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing seed pack if present",
    )
    parser.add_argument(
        "--skip-embedding",
        action="store_true",
        help="Skip embedding (useful for testing structure)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Generate corpus
        _LOGGER.info("Generating interview card corpus...")
        corpus = generate_corpus()
        _LOGGER.info(f"Generated {len(corpus)} card variants")

        if args.skip_embedding:
            _LOGGER.info("Skipping embedding (--skip-embedding)")
            return 0

        # Embed corpus
        embeddings = embed_corpus(corpus, show_progress=True)

        # Create seed pack
        seed_pack_dir = create_seed_pack(corpus, embeddings, force=args.force)

        # Populate active index
        populate_active_index(seed_pack_dir, corpus, embeddings)

        _LOGGER.info("Index population complete!")
        _LOGGER.info(f"  Seed pack: {seed_pack_dir}")
        _LOGGER.info(f"  Active index: {INDEXES_DIR}")
        _LOGGER.info(f"  Vectors: {len(corpus)} (BGE-M3, 1024 dims)")

        return 0

    except Exception as exc:
        _LOGGER.error(f"Index population failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
