"""Validate a canonical Chroma collection post-ingestion.

Checks:
  1. Collection exists
  2. count > 0
  3. Sample embeddings are expected_dim
  4. Sample documents are non-empty
  5. Metadata keys are present
  6. hnsw:space and embedding_model declared in collection metadata
  7. Sparse sidecar DB present (for Phase-A target collections)

Usage:
    python tools/generate/ingestion/validate_collection.py \
        --collection code_chunks [--store-path PATH] [--dim 1024] [--sample 10]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


REPO_ROOT = _discover_repo_root(Path(__file__).resolve().parent)
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"
SPARSE_PATH = REPO_ROOT / "data" / "cache" / "sparse"
DEFAULT_DIM = 1024
DEFAULT_SAMPLE = 10

REQUIRED_META_KEYS = {
    "code_chunks": {"artifact_type", "file_path", "layer", "canonical_digest", "entity_type"},
    "symbols": {"artifact_type", "symbol_name", "entity_type", "file_path", "layer", "canonical_digest"},
    "arch_docs": {"artifact_type", "doc_type", "file_path", "layer", "canonical_digest"},
    "runtime_evidence": {"artifact_type", "evidence_type", "file_path", "layer", "canonical_digest"},
    "process_docs": {"artifact_type", "doc_type", "file_path", "layer", "canonical_digest"},
    "ext_knowledge": {"artifact_type", "doc_type", "domain", "layer", "canonical_digest"},
    "incidents_rca": {"artifact_type", "doc_type", "file_path", "layer", "canonical_digest"},
    "tests_guardrails": {"artifact_type", "doc_type", "file_path", "layer", "canonical_digest"},
}


def validate(store_path: Path, collection_name: str, expected_dim: int, sample_size: int) -> bool:
    try:
        import chromadb
    except ImportError:
        print("ERROR: chromadb not installed.")
        return False

    ok = True
    sample_size = max(1, sample_size)

    print(f"\n=== VALIDATE: {collection_name} @ {store_path} ===")

    if not store_path.exists():
        print(f"  [FAIL] Chroma store path does not exist: {store_path}")
        return False

    # 1. Collection exists
    try:
        client = chromadb.PersistentClient(path=str(store_path))
        existing = {c.name for c in client.list_collections()}
    except (OSError, RuntimeError, ValueError, AttributeError) as exc:
        print(f"  [FAIL] Could not open Chroma store: {exc}")
        return False
    if collection_name not in existing:
        print(f"  [FAIL] Collection '{collection_name}' does not exist.")
        return False
    print(f"  [OK]   Collection exists")

    collection = client.get_collection(collection_name)

    # 2. Count > 0
    count = collection.count()
    if count == 0:
        print(f"  [FAIL] count=0 — collection is empty")
        ok = False
    else:
        print(f"  [OK]   count={count}")

    # 3. Collection-level metadata
    col_meta = collection.metadata or {}
    hnsw_space = col_meta.get("hnsw:space")
    emb_model = col_meta.get("embedding_model")
    emb_dim_meta = col_meta.get("embedding_dim")

    if hnsw_space == "cosine":
        print(f"  [OK]   hnsw:space=cosine")
    else:
        print(f"  [FAIL] hnsw:space={hnsw_space!r} (expected 'cosine')")
        ok = False

    if emb_model:
        print(f"  [OK]   embedding_model={emb_model}")
    else:
        print(f"  [WARN] embedding_model not declared in collection metadata")

    if emb_dim_meta:
        print(f"  [OK]   embedding_dim={emb_dim_meta} (declared)")
    else:
        print(f"  [WARN] embedding_dim not declared in collection metadata")

    if count == 0:
        return ok

    # 4–6. Sample embeddings, documents, metadata
    n = min(sample_size, count)
    result = collection.get(limit=n, include=["embeddings", "documents", "metadatas"])

    embeddings = result.get("embeddings") or []
    documents = result.get("documents") or []
    metadatas = result.get("metadatas") or []

    dim_errors = 0
    empty_doc_errors = 0
    meta_errors = 0
    required_keys = REQUIRED_META_KEYS.get(collection_name, set())
    observed = max(len(embeddings), len(documents), len(metadatas))
    if observed < n:
        print(f"  [WARN] Requested sample={n}, but collection returned only {observed} rows")

    for i in range(observed):  # tqdm: sampled embedding check, no bar needed
        emb = embeddings[i]
        if emb is None:
            dim_errors += 1
            continue
        emb_list = emb.tolist() if hasattr(emb, "tolist") else list(emb)
        if len(emb_list) != expected_dim:
            dim_errors += 1
            print(f"  [FAIL] Embedding[{i}] dim={len(emb_list)}, expected={expected_dim}")

        doc = documents[i] if i < len(documents) else None
        if not doc or len(doc.strip()) == 0:
            empty_doc_errors += 1

        meta = metadatas[i] if i < len(metadatas) else {}
        missing = required_keys - set((meta or {}).keys())
        if missing:
            meta_errors += 1
            if meta_errors == 1:
                print(f"  [FAIL] Metadata missing keys {missing} (first occurrence at index {i})")

    if dim_errors == 0:
        print(f"  [OK]   All {n} sampled embeddings are dim={expected_dim}")
    else:
        print(f"  [FAIL] {dim_errors}/{n} embeddings have wrong dimension")
        ok = False

    if empty_doc_errors == 0:
        print(f"  [OK]   All {n} sampled documents are non-empty")
    else:
        print(f"  [FAIL] {empty_doc_errors}/{n} documents are empty")
        ok = False

    if meta_errors == 0:
        print(f"  [OK]   Metadata keys present in all {n} sampled documents")
    else:
        print(f"  [FAIL] {meta_errors}/{n} documents have missing required metadata keys")
        ok = False

    # 7. Sparse sidecar check (Phase-A target collections only)
    _SPARSE_TARGET_COLLECTIONS = {
        "code_chunks",
        "symbols",
        "arch_docs",
        "tests_guardrails",
        "runtime_evidence",
        "process_docs",
        "ext_knowledge",
        "incidents_rca",
    }
    if collection_name in _SPARSE_TARGET_COLLECTIONS:
        sidecar = SPARSE_PATH / f"{collection_name}.db"
        if sidecar.exists():
            print(f"  [OK]   Sparse sidecar present: {sidecar.name}")
        else:
            print(f"  [WARN] Sparse sidecar missing: {sidecar} — run build_sparse_index.py")

    # Show one sample metadata for reference
    if metadatas:
        print(f"\n  Sample metadata schema (doc[0]):")
        for k, v in sorted((metadatas[0] or {}).items()):
            print(f"    {k}: {str(v)[:80]!r}")

    print(f"\n  Result: {'PASS' if ok else 'FAIL'} — {collection_name}")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a canonical Chroma collection")
    parser.add_argument("--collection", required=True, help="Collection name to validate")
    parser.add_argument("--store-path", type=Path, default=CANONICAL_STORE)
    parser.add_argument("--dim", type=int, default=DEFAULT_DIM, help="Expected embedding dimension")
    parser.add_argument("--sample", type=int, default=DEFAULT_SAMPLE, help="Sample size for checks")
    args = parser.parse_args()

    passed = validate(args.store_path, args.collection, args.dim, args.sample)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
