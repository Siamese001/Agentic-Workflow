#!/usr/bin/env python3
"""Build and persist FAISS index from healing_contexts seed pack.

Reads the pre-computed embeddings.f32 + row_index.jsonl from the seed pack,
builds a LocalFAISSStore IndexFlatIP index, and persists the 3-file artifact
(index.json, meta.json, manifest.json) to C:/AgenticEmbeddings/indexes/healing_contexts.

After this runs, verify_indexes_at_boot() will find and verify the artifact.
"""

from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system_learning.engines.local_faiss_store import LocalFAISSStore

SEED_PACK = pathlib.Path(
    "C:/AgenticEmbeddings/seed_packs/healing_contexts"
    "/5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9"
)
INDEX_OUT = pathlib.Path("C:/AgenticEmbeddings/indexes")
INDEX_ID = "healing_contexts"

MANIFEST = json.loads((SEED_PACK / "seed_manifest.json").read_text())
DIM = MANIFEST["dimensions"]
VECTOR_COUNT = MANIFEST["vector_count"]
EMBEDDER_ID = MANIFEST["embedding_model_version"]
MODEL_CHECKSUM = MANIFEST["embedding_model_checksum"]
CANON_VER = MANIFEST["canonicalization_version"]
BUILT_AT = MANIFEST["built_at_utc"]

BATCH = 5000  # rows per add_vectors call — keeps peak RAM reasonable


def main() -> int:
    print(f"Building FAISS index: id={INDEX_ID} dim={DIM} vectors={VECTOR_COUNT}")
    print(f"  seed pack : {SEED_PACK}")
    print(f"  output    : {INDEX_OUT}")

    store = LocalFAISSStore(base_path=INDEX_OUT)
    store.begin_build(INDEX_ID, dimension=DIM, seed=42)

    emb_path = SEED_PACK / "embeddings.f32"
    row_path = SEED_PACK / "row_index.jsonl"

    # Memory-map the embeddings (avoids loading 1.17 GB into RAM all at once)
    raw = np.memmap(emb_path, dtype=np.float32, mode="r", shape=(VECTOR_COUNT, DIM))

    with row_path.open(encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh]

    assert len(rows) == VECTOR_COUNT, f"row count mismatch: {len(rows)} vs {VECTOR_COUNT}"

    t0 = time.time()
    for start in range(0, VECTOR_COUNT, BATCH):
        end = min(start + BATCH, VECTOR_COUNT)
        batch_vecs = raw[start:end].tolist()
        batch_meta = rows[start:end]
        store.add_vectors(INDEX_ID, batch_vecs, batch_meta)
        elapsed = time.time() - t0
        print(f"  {end}/{VECTOR_COUNT} vectors added  ({elapsed:.1f}s)", end="\r", flush=True)

    print()
    print("Finalizing index...")
    metadata = store.finalize_build(
        INDEX_ID,
        built_at_utc=BUILT_AT,
        canonicalization_version=CANON_VER,
        embedding_model_version=EMBEDDER_ID,
        embedding_model_checksum=MODEL_CHECKSUM,
    )
    print(f"  vector_count={metadata.vector_count}  hash={metadata.index_version_hash[:16]}...")

    print("Persisting to disk...")
    INDEX_OUT.mkdir(parents=True, exist_ok=True)
    digest = store.persist_to_disk(
        INDEX_ID,
        dest_dir=INDEX_OUT,
        embedder_id=EMBEDDER_ID,
        model_version=EMBEDDER_ID,
    )
    print(f"  manifest digest: {digest[:16]}...")

    # Verify immediately
    print("Verifying boot sweep...")
    result = LocalFAISSStore.verify_indexes_at_boot(INDEX_OUT)
    if not result:
        print("ERROR: boot sweep returned empty — artifact not found!")
        return 1
    print(f"  verified: {list(result.keys())}")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s — F3 FIXED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
