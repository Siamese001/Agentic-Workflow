"""Ingest repo architecture/design documents into the canonical `arch_docs` ChromaDB collection.

Sources (in priority order):
  1. docs/architecture/  — ADRs, design docs, architecture notes
  2. docs/              — all other .md files (guides, contracts, standards)
  3. Top-level .md files (README, AGENTS.md, etc.)

Noisy subdirs explicitly excluded: reports, plans, evidence, windsurf, _archive, artifacts.

Usage:
    python tools/generate/ingestion/ingest_arch_docs.py [--store-path PATH] [--dry-run]

Embedding: BAAI/bge-m3 (1024-dim, L2-normalized, cosine)
Collection: arch_docs  hnsw:space=cosine
Metadata added (Phase 2): title, heading_path, authority_level, doc_family,
    canonical, retrieval_weight, source_area.
"""

from __future__ import annotations

import argparse
import hashlib
import re
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
COLLECTION_NAME = "arch_docs"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
BATCH_SIZE = 256
CHUNK_CHARS = 2000  # max chars per chunk
CHUNK_OVERLAP = 200  # overlap between consecutive chunks

SCAN_DIRS = [
    "docs",
]

TOP_LEVEL_MD = [
    "README.md",
    "AGENTS.md",
]

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "archives",
    "_archive",
    "node_modules",
    ".windsurf",
    "vector_store",
    "artifacts",
    ".pytest_cache",
    "data",
    "reports",
    "plans",
    "evidence",
    "windsurf",
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


_AUTHORITY_MAP: list[tuple[str, float]] = [
    ("adr", 1.0),
    ("architecture", 0.85),
    ("contract", 0.75),
    ("spec", 0.65),
    ("standard", 0.60),
    ("guide", 0.55),
    ("reference", 0.50),
    ("overview", 0.45),
    ("doc", 0.40),
    ("report", 0.20),
    ("plan", 0.10),
]

_NOISY_PATH_PARTS = {"reports", "plans", "evidence", "artifacts", "windsurf", "_archive", "archives"}


def _compute_authority_level(file_path: Path, doc_type: str) -> float:
    """Return authority level [0.0, 1.0] based on file path and doc_type."""
    parts_lower = {p.lower() for p in file_path.parts}
    if parts_lower & _NOISY_PATH_PARTS:
        return 0.10
    for name, level in _AUTHORITY_MAP:
        if name == doc_type:
            return level
    return 0.40


def _compute_doc_family(file_path: Path) -> str:
    """Return the doc family based on the file's parent directory hierarchy."""
    canonical_dirs = {
        "adr": "adr",
        "architecture": "architecture",
        "contracts": "contract",
        "contract": "contract",
        "specs": "spec",
        "spec": "spec",
        "standards": "standard",
        "standard": "standard",
        "guides": "guide",
        "guide": "guide",
        "reference": "reference",
        "svp": "svp",
        "policies": "policy",
        "policy": "policy",
    }
    for part in file_path.parts:
        mapped = canonical_dirs.get(part.lower())
        if mapped:
            return mapped
    name_lower = file_path.name.lower()
    if name_lower in ("readme.md", "agents.md"):
        return "overview"
    return "doc"


def _compute_source_area(file_path: Path) -> str:
    """Return coarse source area for filtering (arch, contract, spec, guide, etc.)."""
    family = _compute_doc_family(file_path)
    if family in ("adr", "architecture"):
        return "arch"
    if family in ("contract",):
        return "contract"
    if family in ("spec",):
        return "spec"
    if family in ("standard",):
        return "standard"
    if family in ("guide",):
        return "guide"
    if family in ("reference",):
        return "reference"
    if family in ("svp", "policy"):
        return "policy"
    if family == "overview":
        return "overview"
    return "doc"


def _is_canonical(file_path: Path, doc_type: str) -> bool:
    """Return True if the document is a canonical authority source."""
    if doc_type in ("adr", "architecture", "contract", "spec", "standard", "overview"):
        return True
    parts_lower = {p.lower() for p in file_path.parts}
    return not bool(parts_lower & _NOISY_PATH_PARTS)


def _extract_title(source: str, file_path: Path) -> str:
    """Extract the first H1 heading, or derive from filename."""
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()[:200]
    return file_path.stem.replace("_", " ").replace("-", " ")[:200]


def chunk_by_headings(
    text: str, max_chars: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP
) -> list[tuple[str, str]]:
    """Split text into section-aware chunks keyed by heading breadcrumb.

    Returns a list of (heading_path, chunk_text) tuples where heading_path is
    a " > "-delimited breadcrumb of H1/H2/H3 headings, e.g.
    "Architecture Design > Query Routing > Fallback Strategy".
    Falls back to character-based chunks when no headings are found.
    """
    heading_re = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    boundaries = [(m.start(), len(m.group(1)), m.group(2).strip()) for m in heading_re.finditer(text)]

    if not boundaries:
        return [("no-headings", chunk) for chunk in chunk_text(text, max_chars, overlap) if chunk]

    boundaries.append((len(text), 0, ""))

    stack: list[str] = ["", "", ""]
    results: list[tuple[str, str]] = []

    for i, (pos, level, title) in enumerate(boundaries[:-1]):
        next_pos = boundaries[i + 1][0]

        if level == 1:
            stack = [title, "", ""]
        elif level == 2:
            stack[1] = title
            stack[2] = ""
        elif level == 3:
            stack[2] = title

        heading_path = " > ".join(h for h in stack if h)
        section = text[pos:next_pos].strip()
        if not section or len(section) < MIN_BODY_CHARS:
            continue

        for chunk in chunk_text(section, max_chars, overlap):
            if chunk:
                results.append((heading_path, chunk))

    return results if results else [("no-headings", c) for c in chunk_text(text, max_chars, overlap) if c]


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
        doc_family = _compute_doc_family(md_file)
        source_area = _compute_source_area(md_file)
        authority_level = _compute_authority_level(md_file, doc_type)
        canonical = _is_canonical(md_file, doc_type)
        retrieval_weight = 1.0 if canonical else 0.4
        title = _extract_title(source, md_file)

        heading_chunks = chunk_by_headings(source)
        for chunk_idx, (heading_path, chunk_text_val) in enumerate(heading_chunks):
            docs.append(
                {
                    "text": chunk_text_val,
                    "metadata": {
                        "artifact_type": "arch_doc",
                        "doc_type": doc_type,
                        "doc_family": doc_family,
                        "file_path": rel_path,
                        "layer": layer,
                        "chunk_index": chunk_idx,
                        "canonical_digest": canonical_digest,
                        "source": "markdown",
                        "title": title,
                        "heading_path": heading_path,
                        "authority_level": authority_level,
                        "canonical": canonical,
                        "retrieval_weight": retrieval_weight,
                        "source_area": source_area,
                        "source_collection": "arch_docs",
                        "authority_tier": "T4_implementation_evidence",
                        "normative_scope": "evidence_only",
                        "invalid_for_normative_use": True,
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

    if str(REPO_ROOT) not in sys.path:
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
