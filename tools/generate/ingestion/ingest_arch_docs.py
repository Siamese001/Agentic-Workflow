"""Ingest repo architecture/design documents into the canonical `arch_docs` ChromaDB collection.

Sources (in priority order):
  1. docs/architecture/  — ADRs, design docs, architecture notes
  2. docs/              — all other .md files (guides, contracts, standards)
  3. Top-level .md files (README, AGENTS.md, etc.)
  4. apps_*/  SVP_ENGINEERING_REVIEW.md, TECHNICAL_SPEC.md, TEST_STRATEGY.md

Usage:
    python tools/generate/ingestion/ingest_arch_docs.py [--store-path PATH] [--dry-run]

Embedding: BAAI/bge-m3 (1024-dim, L2-normalized, cosine)
Collection: arch_docs  hnsw:space=cosine
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
from pathlib import Path
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION_NAME = "arch_docs"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
BATCH_SIZE = 256
CHUNK_CHARS = 2000  # max chars per chunk
CHUNK_OVERLAP = 200  # overlap between consecutive chunks

SCAN_DIRS = [
    "docs",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
    "infrastructure",
    "tools",
    "ops_scripts",
    "agentic_core",
    "system_learning",
]

TOP_LEVEL_MD = [
    "README.md",
    "AGENTS.md",
]

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "archives",
    "node_modules",
    ".windsurf",
    "vector_store",
    "artifacts",
    ".pytest_cache",
    "data",
}

# Files to skip (generated / binary-ish markdown)
EXCLUDE_PATTERNS = [
    r"CHANGELOG",
    r"changelog",
    r"\.min\.",
]

MIN_BODY_CHARS = 80  # skip stub files


def compute_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def detect_doc_type(file_path: Path) -> str:
    parts = [p.lower() for p in file_path.parts]
    name = file_path.name.lower()
    if "adr" in parts or "adr" in name:
        return "adr"
    if "architecture" in parts or "architecture" in name:
        return "architecture"
    if "contract" in parts or "contract" in name:
        return "contract"
    if "guide" in parts or "guide" in name:
        return "guide"
    if "svp_engineering" in name or "technical_spec" in name or "test_strategy" in name:
        return "spec"
    if "readme" in name or "agents" in name:
        return "overview"
    return "doc"


def detect_layer(file_path: Path) -> str:
    parts = file_path.parts
    for part in parts:
        if part.startswith("L") and len(part) >= 2 and part[1].isdigit():
            return part[:2]
    for part in parts:
        if part.startswith("apps_"):
            return "apps"
    if "docs" in parts:
        return "docs"
    if "tools" in parts:
        return "tools"
    if "infrastructure" in parts:
        return "infrastructure"
    return "unknown"


def chunk_text(text: str, chunk_size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping character-based chunks, breaking at paragraph boundaries."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Try to break at a paragraph boundary
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


def should_exclude(file_path: Path) -> bool:
    if any(excl in file_path.parts for excl in EXCLUDE_DIRS):
        return True
    name = file_path.name
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, name):
            return True
    return False


def collect_documents(repo_root: Path) -> list[dict]:
    """Walk source dirs and collect arch doc chunks."""
    seen_paths: set[str] = set()
    docs = []

    def process_file(md_file: Path) -> None:
        rel_path = str(md_file.relative_to(repo_root)).replace("\\", "/")
        if rel_path in seen_paths:
            return
        seen_paths.add(rel_path)

        try:
            source = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return
        if len(source.strip()) < MIN_BODY_CHARS:
            return

        canonical_digest = compute_digest(source)
        doc_type = detect_doc_type(md_file)
        layer = detect_layer(md_file)

        chunks = chunk_text(source)
        for chunk_idx, chunk_text_val in tqdm(enumerate(chunks), desc="Processing", unit="item"):
            docs.append(
                {
                    "text": chunk_text_val,
                    "metadata": {
                        "artifact_type": "arch_doc",
                        "doc_type": doc_type,
                        "file_path": rel_path,
                        "layer": layer,
                        "chunk_index": chunk_idx,
                        "canonical_digest": canonical_digest,
                        "source": "markdown",
                    },
                    "id_parts": (rel_path, str(chunk_idx)),
                }
            )

    # Top-level .md files
    for name in TOP_LEVEL_MD:
        f = repo_root / name
        if f.exists():
            process_file(f)

    # Scan dirs
    for scan_dir in SCAN_DIRS:
        base = repo_root / scan_dir
        if not base.exists():
            continue
        for md_file in base.rglob("*.md"):
            if should_exclude(md_file):
                continue
            process_file(md_file)

    return docs


def make_doc_id(id_parts: tuple) -> str:
    raw = ":".join(id_parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


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
            raise ValueError(
                f"Embedding[{i}] dim={len(emb)}, expected={expected}. Model mismatch — aborting write."
            )


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
        raise RuntimeError(f"Model dimension mismatch: got {actual_dim}, expected {EMBEDDING_DIM}")
    print(f"Model loaded. dim={actual_dim}")

    print(f"Collecting arch doc chunks from {REPO_ROOT} ...")
    docs = collect_documents(REPO_ROOT)
    print(f"Collected {len(docs)} chunks from markdown sources")

    if dry_run:
        print("DRY RUN — stopping before Chroma write.")
        return

    print(f"Connecting to Chroma store: {store_path}")
    client = chromadb.PersistentClient(path=str(store_path))

    existing = {c.name for c in client.list_collections()}
    if COLLECTION_NAME in existing:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' already exists with {collection.count()} docs — upserting.")
    else:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",
                "description": "Canonical architecture/design docs: ADRs, guides, specs, READMEs",
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dim": EMBEDDING_DIM,
            },
        )
        print(f"Created collection '{COLLECTION_NAME}'")

    ids = [make_doc_id(d["id_parts"]) for d in docs]
    texts = [d["text"] for d in docs]
    metadatas = [d["metadata"] for d in docs]

    # Deduplicate by id (keep last)
    seen: dict[str, int] = {}
    for i, doc_id in enumerate(ids):
        seen[doc_id] = i
    dedup_indices = sorted(seen.values())
    ids = [ids[i] for i in dedup_indices]
    texts = [texts[i] for i in dedup_indices]
    metadatas = [metadatas[i] for i in dedup_indices]
    print(f"After dedup: {len(ids)} unique chunks")

    total = len(ids)
    reporter = ProgressReporter(total=total, label="Embedding + upserting arch_docs")
    t0 = time.time()

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch_ids = ids[batch_start:batch_end]
        batch_texts = texts[batch_start:batch_end]
        batch_metas = metadatas[batch_start:batch_end]

        batch_embeddings = embed_batch(model, batch_texts)
        validate_dim(batch_embeddings)

        collection.upsert(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_texts,
            metadatas=batch_metas,
        )
        reporter.update(batch_end - batch_start, label=f"Upserted batch ending at {batch_end}")

    reporter.done()
    elapsed = time.time() - t0
    final_count = collection.count()
    print(f"\nDone. collection='{COLLECTION_NAME}' count={final_count} elapsed={elapsed:.1f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest arch_docs into canonical Chroma store")
    parser.add_argument(
        "--store-path",
        type=Path,
        default=CANONICAL_STORE,
        help=f"ChromaDB persistence directory (default: {CANONICAL_STORE})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Collect without writing to Chroma")
    args = parser.parse_args()
    run(store_path=args.store_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
