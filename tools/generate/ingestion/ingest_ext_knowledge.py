"""Wave B2 ingestion — ext_raw ChromaDB collection.

Status  : Active (Wave B2) — replaces ext_knowledge collection.
See     : docs/requirements/wave_b_chromadb_topology.md
          docs/requirements/wave_b_metadata_contract.md

Ingest unvetted scraped web content into the ``ext_raw`` collection (Lane E).

Sources:
  1. agentic_best_practices (ChromaDB) — web-scraped external docs
       Domains: nvlpubs.nist.gov, huggingface.co, microsoft.github.io,
                www.paulgraham.com, python.langchain.com, modelcontextprotocol.io,
                docs.trychroma.com, docs.anthropic.com, etc.
       Filter: skip docs whose source_url already appears in ext_authority (URL dedup).
               skip any doc containing 'Loading...' (SPA-render failure).
               skip any doc with body < MIN_BODY_CHARS (empty/stub).

  2. docs/external/ — markdown files (VSCodium extension docs)

  3. data/external/ — markdown + YAML + JSON files

Explicitly excluded:
  - agentic_best_practices_semantic (does not exist — confirmed absent)
  - healing_contexts_corpus.jsonl   (content-hash only, no doc body — quarantined)
  - Any URL already present in ext_authority (deduped at run() start)
  - Any doc body containing 'Loading...' repeated pattern

Metadata: Wave B Lane E fields — source_band=unvetted, authority_tier=T5_unvetted,
          invalid_for_normative_use=True for all chunks.

Usage:
    python tools/generate/ingestion/ingest_ext_knowledge.py [--store-path PATH] [--dry-run]

Embedding: BAAI/bge-m3 (1024-dim, L2-normalized, cosine)
Collection: ext_raw  hnsw:space=cosine
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION_NAME = "ext_raw"
SOURCE_COLLECTION = "agentic_best_practices"

# Wave B Lane E metadata constants
_WAVE_B_EXT_RAW_FIELDS: dict = {
    "source_collection": "ext_raw",
    "source_band": "unvetted",
    "authority_tier": "T5_unvetted",
    "normative_scope": "unvetted",
    "invalid_for_normative_use": True,
}
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
BATCH_SIZE = 256
CHUNK_CHARS = 2000
CHUNK_OVERLAP = 200
MIN_BODY_CHARS = 80

# Garbage filter: any doc matching these patterns is skipped
GARBAGE_PATTERNS = [
    "Loading...",
    "Loading..Loading..",
]

ON_DISK_DIRS: list[tuple[str, str, list[str]]] = [
    ("docs/external", "ext_doc", ["*.md"]),
    ("data/external", "ext_playbook", ["*.md", "*.yaml", "*.yml"]),
]


def is_garbage(text: str) -> bool:
    """Return True if the document body is SPA garbage or too short."""
    if not text or len(text.strip()) < MIN_BODY_CHARS:
        return True
    for pat in GARBAGE_PATTERNS:
        if pat in text:
            return True
    return False


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


def collect_from_chroma(chroma_path: str) -> tuple[list[dict], int, int]:
    """
    Read clean documents from the agentic_best_practices collection.
    Returns (docs, total_read, garbage_skipped).
    """
    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError("chromadb not installed") from exc

    client = chromadb.PersistentClient(path=chroma_path)
    try:
        src_col = client.get_collection(SOURCE_COLLECTION)
    except (ValueError, chromadb.errors.NotFoundError) as exc:
        print(f"  [{SOURCE_COLLECTION}] collection not found ({exc}) — skipping")
        return [], 0, 0

    total_count = src_col.count()
    print(f"  [{SOURCE_COLLECTION}] reading {total_count} source documents ...")

    all_docs: list[dict] = []
    garbage_skipped = 0
    batch_size = 500
    offset = 0
    seen_hashes: set[str] = set()

    while offset < total_count:
        r = src_col.get(limit=batch_size, offset=offset, include=["documents", "metadatas"])
        batch_docs = r.get("documents") or []
        batch_metas = r.get("metadatas") or []
        offset += len(batch_docs)
        if not batch_docs:
            break

        for doc, meta in tqdm(zip(batch_docs, batch_metas), desc="Processing", unit="item"):
            meta = meta or {}
            if is_garbage(doc):
                garbage_skipped += 1
                continue
            content_hash = meta.get("content_hash", compute_digest(doc or ""))
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)

            source_url = meta.get("source_url", "")
            domain = meta.get("domain", "unknown")
            title = meta.get("document_title", "")
            canonical_digest = compute_digest(doc)

            all_docs.append(
                {
                    "text": doc,
                    "metadata": {
                        "artifact_type": "ext_raw",
                        "doc_type": "web",
                        "domain": domain,
                        "source_url": source_url,
                        "document_title": title[:200] if title else "",
                        "file_path": source_url[:200] if source_url else domain,
                        "layer": "ext",
                        "canonical_digest": canonical_digest,
                        "source": "agentic_best_practices",
                        "source_collection": _WAVE_B_EXT_RAW_FIELDS["source_collection"],
                        "source_band": _WAVE_B_EXT_RAW_FIELDS["source_band"],
                        "authority_tier": _WAVE_B_EXT_RAW_FIELDS["authority_tier"],
                        "normative_scope": _WAVE_B_EXT_RAW_FIELDS["normative_scope"],
                        "invalid_for_normative_use": _WAVE_B_EXT_RAW_FIELDS["invalid_for_normative_use"],
                        "topic_bucket": "unclassified",
                        "doc_family": "web",
                        "heading_path": "no-headings",
                        "collapse_group": domain,
                        "title": title[:200] if title else "",
                        "chunk_index": 0,
                        "version_or_date": "",
                    },
                    "id_parts": ("web", domain, content_hash[:16]),
                }
            )

    return all_docs, total_count, garbage_skipped


def collect_from_disk(repo_root: Path) -> list[dict]:
    """Read on-disk external files."""
    all_docs: list[dict] = []
    seen: set[str] = set()

    for dir_rel, doc_type, globs in tqdm(ON_DISK_DIRS, desc="Processing", unit="item"):
        base = repo_root / dir_rel
        if not base.exists():
            continue
        batch = []
        for glob in tqdm(globs, desc="Processing", unit="item"):
            for f in tqdm(sorted(base.rglob(glob)), desc="Processing", unit="item"):
                if not f.is_file():
                    continue
                rel_path = str(f.relative_to(repo_root)).replace("\\", "/")
                if rel_path in seen:
                    continue
                seen.add(rel_path)
                try:
                    source = f.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                if is_garbage(source):
                    continue
                canonical_digest = compute_digest(source)
                for chunk_idx, chunk in tqdm(enumerate(chunk_text(source)), desc="Processing", unit="item"):
                    batch.append(
                        {
                            "text": chunk,
                            "metadata": {
                                "artifact_type": "ext_raw",
                                "doc_type": doc_type,
                                "domain": "local",
                                "source_url": "",
                                "document_title": f.stem,
                                "file_path": rel_path,
                                "layer": "ext",
                                "chunk_index": chunk_idx,
                                "canonical_digest": canonical_digest,
                                "source": "disk",
                                "source_collection": _WAVE_B_EXT_RAW_FIELDS["source_collection"],
                                "source_band": _WAVE_B_EXT_RAW_FIELDS["source_band"],
                                "authority_tier": _WAVE_B_EXT_RAW_FIELDS["authority_tier"],
                                "normative_scope": _WAVE_B_EXT_RAW_FIELDS["normative_scope"],
                                "invalid_for_normative_use": _WAVE_B_EXT_RAW_FIELDS[
                                    "invalid_for_normative_use"
                                ],
                                "topic_bucket": "unclassified",
                                "doc_family": doc_type,
                                "heading_path": "no-headings",
                                "collapse_group": dir_rel,
                                "title": f.stem,
                                "version_or_date": "",
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
            raise ValueError(
                f"Embedding[{i}] dim={len(emb)}, expected={expected}. Model mismatch — aborting."
            )


def _load_ext_authority_urls(store_path: Path) -> set[str]:
    """Load source_url values from ext_authority for URL dedup (ext_raw skips these)."""
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(store_path))
        existing = {c.name for c in client.list_collections()}
        if "ext_authority" not in existing:
            return set()
        try:
            col = client.get_collection("ext_authority")
        except (ValueError, chromadb.errors.NotFoundError):
            return set()
        total = col.count()
        if total == 0:
            return set()
        urls: set[str] = set()
        offset = 0
        batch_size = 500
        while offset < total:
            r = col.get(limit=batch_size, offset=offset, include=["metadatas"])
            metas = r.get("metadatas") or []
            for m in metas:
                url_val = m.get("source_url") if m else None
                if isinstance(url_val, str) and url_val:
                    urls.add(url_val)
            offset += len(metas)
            if not metas:
                break
        return urls
    except (ValueError, ImportError, RuntimeError) as exc:
        print(f"  [ext_authority dedup] Warning: could not load URLs — {exc}", file=sys.stderr)
        return set()


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

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from tools.progress_display import ProgressReporter

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
    model.max_seq_length = 512
    actual_dim = model.get_sentence_embedding_dimension()
    if actual_dim != EMBEDDING_DIM:
        raise RuntimeError(f"Model dim mismatch: got {actual_dim}, expected {EMBEDDING_DIM}")
    print(f"Model loaded. dim={actual_dim}")

    print("Loading ext_authority URLs for dedup ...")
    ext_authority_urls = _load_ext_authority_urls(store_path)
    print(f"  ext_authority URL dedup set: {len(ext_authority_urls)} URLs")

    print("Collecting ext_raw documents ...")
    chroma_docs, total_read, garbage_skipped = collect_from_chroma(str(store_path))
    print(
        f"  [{SOURCE_COLLECTION}] total_read={total_read} garbage_skipped={garbage_skipped} clean={len(chroma_docs)}"
    )
    disk_docs = collect_from_disk(REPO_ROOT)
    all_docs_raw = chroma_docs + disk_docs

    # URL dedup: remove any document whose source_url is already in ext_authority
    all_docs = [d for d in all_docs_raw if not d["metadata"].get("source_url") in ext_authority_urls]
    dedup_removed = len(all_docs_raw) - len(all_docs)
    print(f"Total collected: {len(all_docs)} documents (ext_authority dedup removed {dedup_removed})")

    if dry_run:
        print(f"DRY RUN — stopping before Chroma write. garbage_filtered={garbage_skipped}")
        return

    print(f"Connecting to Chroma store: {store_path}")
    client = chromadb.PersistentClient(path=str(store_path))

    existing = {c.name for c in client.list_collections()}
    if COLLECTION_NAME in existing:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' exists ({collection.count()} docs) — upserting.")
    else:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",
                "description": (
                    "Wave B Lane E: unvetted scraped external knowledge. "
                    "source_band=unvetted, invalid_for_normative_use=True for all chunks."
                ),
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dim": EMBEDDING_DIM,
                "wave": "B2",
            },
        )
        print(f"Created collection '{COLLECTION_NAME}'")

    ids = [make_doc_id(d["id_parts"]) for d in all_docs]
    texts = [d["text"] for d in all_docs]
    metadatas = [d["metadata"] for d in all_docs]

    # Deduplicate by id (keep last)
    seen_ids: dict[str, int] = {}
    for i, doc_id in enumerate(ids):
        seen_ids[doc_id] = i
    dedup = sorted(seen_ids.values())
    ids = [ids[i] for i in dedup]
    texts = [texts[i] for i in dedup]
    metadatas = [metadatas[i] for i in dedup]
    print(f"After dedup: {len(ids)} unique documents")

    total = len(ids)
    reporter = ProgressReporter(total=total, label="Embedding + upserting ext_raw")
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
    print(
        f"Garbage excluded: {garbage_skipped} Loading.../short-body docs from {SOURCE_COLLECTION}. "
        f"ext_authority dedup removed: {dedup_removed}."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Wave B2: Ingest unvetted web scrapes into ext_raw")
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
