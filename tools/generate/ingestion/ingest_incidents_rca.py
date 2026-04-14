"""Ingest incident/RCA documents into the canonical `incidents_rca` ChromaDB collection.

Source mapping:
  docs/reports/rcas/    → rca (7 RCA markdown files)
  docs/rca/             → rca (1 RCA markdown file)
  docs/reports/rca/     → rca (3 RCA markdown files)
  docs/reports/evidence/→ evidence (34 evidence/healing markdown files)

Excluded:
  docs/reports/plans/   → process_docs (not incident evidence)
  docs/reports/apps_*/  → process_docs (app-level reports)
  data/golden_state/healing_intakes/ → runtime_evidence (already ingested there)

Usage:
    python tools/generate/ingestion/ingest_incidents_rca.py [--store-path PATH] [--dry-run]

Embedding: BAAI/bge-m3 (1024-dim, L2-normalized, cosine)
Collection: incidents_rca  hnsw:space=cosine
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path
from tqdm import tqdm


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


def _ensure_repo_on_syspath(repo_root: Path) -> None:
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)


def _relative_to_repo(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


REPO_ROOT = _discover_repo_root(Path(__file__).resolve().parent)
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION_NAME = "incidents_rca"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
BATCH_SIZE = 256
CHUNK_CHARS = 2000
CHUNK_OVERLAP = 200
MIN_BODY_CHARS = 80

SCAN_DIRS: list[tuple[str, str]] = [
    ("docs/reports/rcas", "rca"),
    ("docs/rca", "rca"),
    ("docs/reports/rca", "rca"),
    ("docs/reports/evidence", "evidence"),
]

EXCLUDE_DIRS = {"__pycache__", ".git", "node_modules", "archives"}


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

    for dir_rel, doc_type in tqdm(SCAN_DIRS, desc="Processing", unit="item"):
        base = repo_root / dir_rel
        if not base.exists():
            continue
        batch = []
        for md_file in tqdm(sorted(base.rglob("*.md")), desc="Processing", unit="item"):
            if any(excl in md_file.parts for excl in EXCLUDE_DIRS):
                continue
            rel_path = _relative_to_repo(md_file, repo_root)
            if rel_path in seen:
                continue
            seen.add(rel_path)
            try:
                source = md_file.read_text(encoding="utf-8")
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
                            "artifact_type": "incident_rca",
                            "doc_type": doc_type,
                            "file_path": rel_path,
                            "layer": "all",
                            "chunk_index": chunk_idx,
                            "canonical_digest": canonical_digest,
                            "source": dir_rel,
                        },
                        "id_parts": (rel_path, str(chunk_idx)),
                    }
                )
        print(f"  [{dir_rel}] {len(batch)} chunks")
        all_docs.extend(batch)

    return all_docs


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

    _ensure_repo_on_syspath(REPO_ROOT)
    from tools.progress_display import ProgressReporter

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
    model.max_seq_length = 512
    actual_dim = model.get_sentence_embedding_dimension()
    if actual_dim != EMBEDDING_DIM:
        raise RuntimeError(f"Model dim mismatch: got {actual_dim}, expected {EMBEDDING_DIM}")
    print(f"Model loaded. dim={actual_dim}")

    print("Collecting incident/RCA documents ...")
    docs = collect_documents(REPO_ROOT)
    print(f"Total collected: {len(docs)} chunks")

    if dry_run:
        print("DRY RUN — stopping before Chroma write.")
        return

    store_path.mkdir(parents=True, exist_ok=True)
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
                "description": "Canonical incident/RCA docs: post-mortems, root cause analyses, evidence reports",
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
    reporter = ProgressReporter(total=total, label="Embedding + upserting incidents_rca")
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
    parser = argparse.ArgumentParser(description="Ingest incidents_rca into canonical Chroma store")
    parser.add_argument("--store-path", type=Path, default=CANONICAL_STORE)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(store_path=args.store_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
