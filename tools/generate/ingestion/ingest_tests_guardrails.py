"""Ingest test files and guardrail docs into the canonical `tests_guardrails` ChromaDB collection.

Source mapping:
  tests/**test_*.py        → test (Python test source — functions, assertions, docstrings)
  tests/**/*.md            → test_doc (test documentation markdown)
  docs/policies/           → policy (access/usage policy docs)
  agentic_core/L5_safety/  → guardrail (safety layer Python modules — policy enforcement code)

Strategy for Python test files:
  - Each test file is chunked as plain text (full source).
  - Body < MIN_BODY_CHARS skipped (stub/empty files).
  - File-level chunks only (no per-function extraction — keeps indexing fast).

Usage:
    python tools/generate/ingestion/ingest_tests_guardrails.py [--store-path PATH] [--dry-run]

Embedding: BAAI/bge-m3 (1024-dim, L2-normalized, cosine)
Collection: tests_guardrails  hnsw:space=cosine
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION_NAME = "tests_guardrails"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
BATCH_SIZE = 256
CHUNK_CHARS = 2000
CHUNK_OVERLAP = 200
MIN_BODY_CHARS = 80

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "node_modules",
    "archives",
    ".mypy_cache",
    ".pytest_cache",
    "vector_store",
    "artifacts",
}

# (dir_rel, glob, doc_type)
SCAN_DIRS: list[tuple[str, str, str]] = [
    ("tests", "test_*.py", "test"),
    ("tests", "*.md", "test_doc"),
    ("docs/policies", "*.md", "policy"),
    ("agentic_core/L5_safety", "*.py", "guardrail"),
]


def compute_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def make_doc_id(id_parts: tuple) -> str:
    return hashlib.sha256(":".join(id_parts).encode("utf-8")).hexdigest()[:24]


def chunk_text(text: str, chunk_size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            boundary = text.rfind("\n\n", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
    return chunks


def collect_documents(repo_root: Path) -> list[dict]:
    all_docs: list[dict] = []
    seen: set[str] = set()

    for dir_rel, glob, doc_type in tqdm(SCAN_DIRS, desc="Processing", unit="item"):
        base = repo_root / dir_rel
        if not base.exists():
            continue
        batch = []
        for src_file in tqdm(sorted(base.rglob(glob)), desc="Processing", unit="item"):
            if not src_file.is_file():
                continue
            if any(excl in src_file.parts for excl in EXCLUDE_DIRS):
                continue
            rel_path = str(src_file.relative_to(repo_root)).replace("\\", "/")
            if rel_path in seen:
                continue
            seen.add(rel_path)
            try:
                source = src_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if len(source.strip()) < MIN_BODY_CHARS:
                continue
            canonical_digest = compute_digest(source)
            for chunk_idx, chunk in tqdm(enumerate(chunk_text(source)), desc="Processing", unit="item"):
                batch.append(
                    {
                        "text": chunk,
                        "metadata": {
                            "artifact_type": "test_guardrail",
                            "doc_type": doc_type,
                            "file_path": rel_path,
                            "layer": _detect_layer(src_file),
                            "chunk_index": chunk_idx,
                            "canonical_digest": canonical_digest,
                            "source": dir_rel,
                        },
                        "id_parts": (rel_path, str(chunk_idx)),
                    }
                )
        print(f"  [{dir_rel}/{glob}] {len(batch)} chunks")
        all_docs.extend(batch)

    return all_docs


def _detect_layer(file_path: Path) -> str:
    for part in file_path.parts:
        if part.startswith("L") and len(part) >= 2 and part[1].isdigit():
            return part[:2]
        if part == "tests":
            return "tests"
        if part.startswith("apps_"):
            return "apps"
    return "unknown"


def embed_batch(model, texts: list[str]) -> list[list[float]]:
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=False,
    ).tolist()
    return [[float(x) for x in emb] for emb in embeddings]


def validate_dim(embeddings: list[list[float]], expected: int = EMBEDDING_DIM) -> None:
    for i, emb in enumerate(embeddings):
        if len(emb) != expected:
            raise ValueError(f"Embedding[{i}] dim={len(emb)}, expected={expected} — aborting.")


def run(store_path: Path, dry_run: bool = False) -> None:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        print("ERROR: sentence-transformers not installed.")
        raise SystemExit(1) from exc
    try:
        import chromadb
    except ImportError as exc:
        print("ERROR: chromadb not installed.")
        raise SystemExit(1) from exc

    sys.path.insert(0, str(REPO_ROOT))
    from tools.progress_display import ProgressReporter

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
    model.max_seq_length = 512
    actual_dim = model.get_sentence_embedding_dimension()
    if actual_dim != EMBEDDING_DIM:
        raise RuntimeError(f"Model dim mismatch: got {actual_dim}, expected {EMBEDDING_DIM}")
    print(f"Model loaded. dim={actual_dim}")

    print("Collecting test/guardrail documents ...")
    docs = collect_documents(REPO_ROOT)
    print(f"Total collected: {len(docs)} chunks")

    if dry_run:
        print("DRY RUN — stopping before Chroma write.")
        return

    print(f"Connecting to Chroma store: {store_path}")
    client = chromadb.PersistentClient(path=str(store_path))

    existing = {c.name for c in client.list_collections()}
    if COLLECTION_NAME in existing:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' exists ({collection.count()}) — upserting.")
    else:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",
                "description": "Canonical test/guardrail corpus: test functions, safety layer modules, policy docs",
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dim": EMBEDDING_DIM,
            },
        )
        print(f"Created collection '{COLLECTION_NAME}'")

    ids = [make_doc_id(d["id_parts"]) for d in docs]
    texts = [d["text"] for d in docs]
    metadatas = [d["metadata"] for d in docs]

    seen_ids: dict[str, int] = {}
    for i, doc_id in enumerate(ids):
        seen_ids[doc_id] = i
    dedup = sorted(seen_ids.values())
    ids = [ids[i] for i in dedup]
    texts = [texts[i] for i in dedup]
    metadatas = [metadatas[i] for i in dedup]
    print(f"After dedup: {len(ids)} unique chunks")

    total = len(ids)
    reporter = ProgressReporter(total=total, label="Embedding + upserting tests_guardrails")
    t0 = time.time()

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch_embeddings = embed_batch(model, texts[batch_start:batch_end])
        validate_dim(batch_embeddings)
        collection.upsert(
            ids=ids[batch_start:batch_end],
            embeddings=batch_embeddings,
            documents=texts[batch_start:batch_end],
            metadatas=metadatas[batch_start:batch_end],
        )
        reporter.update(batch_end - batch_start, label=f"Upserted batch ending at {batch_end}")

    reporter.done()
    elapsed = time.time() - t0
    print(f"\nDone. collection='{COLLECTION_NAME}' count={collection.count()} elapsed={elapsed:.1f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest tests_guardrails into canonical Chroma store")
    parser.add_argument("--store-path", type=Path, default=CANONICAL_STORE)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(store_path=args.store_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
