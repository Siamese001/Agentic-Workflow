"""Ingest process/operational documents into the canonical `process_docs` ChromaDB collection.

Source mapping — directories rolled into `process_docs`:
  docs/guides/          → guides (migration, ADG MCP, tooling guides)
  docs/rules/           → rules (constitutional, policy rules)
  docs/contracts/       → contracts (guardian_to_L6, etc.)
  docs/specs/           → specs (layer specs, component specs)
  docs/standards/       → standards (coding/architectural standards)
  docs/svp/             → svp (system value proposition docs)
  docs/testing/         → testing (test procedures, strategy docs)
  docs/runbooks/        → runbooks (incident/operational playbooks)
  docs/policies/        → policies (access/usage policies)
  docs/handoff/         → handoff (session handoff docs)
  docs/tools/           → tools (tooling documentation)
  docs/reference/       → reference (all reference docs, EXCLUDING already-in-arch_docs)
  docs/windsurf/        → windsurf (IDE config docs)
  docs/mcp/             → mcp (MCP server docs)
  docs/monitoring/      → monitoring (observability/monitoring docs)
  docs/technical/       → technical (technical notes)
  docs/project/         → project (project-level docs)
  .claude/rules/      → windsurf_rules (constitutional/model rules)
  apps_*/README.md      → apps (per-app README)
  apps_*/TECHNICAL_SPEC.md, TEST_STRATEGY.md, SVP_ENGINEERING_REVIEW.md → apps

Explicitly excluded (already in other canonical collections):
  docs/architecture/    → arch_docs
  docs/reports/evidence/, docs/reports/rcas/, docs/rca/ → runtime_evidence
  docs/external/        → ext_knowledge (future)

Legacy collections consolidated here:
  agentic_process_docs (1536-dim/wrong model — re-embed from source)
  audits, constitutional_rules, contracts, guides, rules, specs, svp, testing, apps
  (all 1024-dim but unknown model/no hnsw:space metadata — re-embed from source)

Usage:
    python tools/generate/ingestion/ingest_process_docs.py [--store-path PATH] [--dry-run]

Embedding: BAAI/bge-m3 (1024-dim, L2-normalized, cosine)
Collection: process_docs  hnsw:space=cosine
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

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
from agentic_core.L0_routing.config.path_constants import DOCS_REPORTS_DIR

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION_NAME = "process_docs"
EMBEDDING_MODEL = BGE_M3_MODEL_ID
EMBEDDING_DIM = 1024
BATCH_SIZE = 256
CHUNK_CHARS = 2000
CHUNK_OVERLAP = 200
MIN_BODY_CHARS = 80

# Directories to include (relative to repo root) with their doc_type label
SCAN_DIRS: list[tuple[str, str]] = [
    ("docs/guides", "guide"),
    ("docs/rules", "rule"),
    ("docs/contracts", "contract"),
    ("docs/specs", "spec"),
    ("docs/standards", "standard"),
    ("docs/svp", "svp"),
    ("docs/testing", "testing"),
    ("docs/runbooks", "runbook"),
    ("docs/policies", "policy"),
    ("docs/handoff", "handoff"),
    ("docs/tools", "tooling"),
    ("docs/reference", "reference"),
    ("docs/windsurf", "windsurf"),
    ("docs/mcp", "mcp"),
    ("docs/monitoring", "monitoring"),
    ("docs/technical", "technical"),
    ("docs/project", "project"),
    (".claude/rules", "rule"),
]

# Per-app named files to include
APPS_NAMED_FILES = [
    "README.md",
    "TECHNICAL_SPEC.md",
    "TEST_STRATEGY.md",
    "SVP_ENGINEERING_REVIEW.md",
]

APP_DIRS = [
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
]

# Paths to explicitly exclude (handled by other canonical collections)
EXCLUDE_PATH_PREFIXES = [
    "docs/architecture",
    f"{DOCS_REPORTS_DIR}/evidence",
    f"{DOCS_REPORTS_DIR}/rcas",
    "docs/rca",
    "docs/external",
    f"{DOCS_REPORTS_DIR}/plans",
]

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "node_modules",
    "archives",
    "vector_store",
    "artifacts",
    ".mypy_cache",
    ".pytest_cache",
}

EXCLUDE_PATTERNS = [r"CHANGELOG", r"changelog", r"\.min\."]


def compute_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def make_doc_id(id_parts: tuple) -> str:
    return hashlib.sha256(":".join(id_parts).encode("utf-8")).hexdigest()[:24]


def should_exclude(file_path: Path, repo_root: Path) -> bool:
    if any(excl in file_path.parts for excl in EXCLUDE_DIRS):
        return True
    rel = str(file_path.relative_to(repo_root)).replace("\\", "/")
    if any(rel.startswith(p) for p in EXCLUDE_PATH_PREFIXES):
        return True
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, file_path.name):
            return True
    return False


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


def detect_layer(file_path: Path) -> str:
    parts = file_path.parts
    for part in parts:
        if part.startswith("L") and len(part) >= 2 and part[1].isdigit():
            return part[:2]
        if part.startswith("apps_"):
            return "apps"
    if "docs/archive/windsurf/legacy-tree" in parts:
        return "windsurf"
    if "docs" in parts:
        return "docs"
    return "unknown"


def process_file(md_file: Path, doc_type: str, repo_root: Path, seen: set[str]) -> list[dict]:
    rel_path = str(md_file.relative_to(repo_root)).replace("\\", "/")
    if rel_path in seen:
        return []
    seen.add(rel_path)
    try:
        source = md_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    if len(source.strip()) < MIN_BODY_CHARS:
        return []
    canonical_digest = compute_digest(source)
    layer = detect_layer(md_file)
    docs = []
    for chunk_idx, chunk in tqdm(enumerate(chunk_text(source)), desc="Processing", unit="item"):
        docs.append(
            {
                "text": chunk,
                "metadata": {
                    "artifact_type": "process_doc",
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
    return docs


def collect_documents(repo_root: Path) -> list[dict]:
    all_docs: list[dict] = []
    seen: set[str] = set()
    counts: dict[str, int] = {}

    # Scan configured directories
    for dir_rel, doc_type in tqdm(SCAN_DIRS, desc="Processing", unit="item"):
        base = repo_root / dir_rel
        if not base.exists():
            continue
        batch = []
        for md_file in sorted(base.rglob("*.md")):
            if should_exclude(md_file, repo_root):
                continue
            batch.extend(process_file(md_file, doc_type, repo_root, seen))
        counts[dir_rel] = len(batch)
        all_docs.extend(batch)

    # Per-app named files
    apps_batch = []
    for app_dir in APP_DIRS:
        base = repo_root / app_dir
        if not base.exists():
            continue
        for fname in APPS_NAMED_FILES:
            f = base / fname
            if f.exists():
                apps_batch.extend(process_file(f, "apps", repo_root, seen))
    counts["apps_*/named"] = len(apps_batch)
    all_docs.extend(apps_batch)

    # Print source breakdown
    for src, cnt in counts.items():
        print(f"  [{src}] {cnt} chunks")

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

    print(f"Collecting process doc chunks from {REPO_ROOT} ...")
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
        print(f"Collection '{COLLECTION_NAME}' exists ({collection.count()} docs) — upserting.")
    else:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",
                "description": "Canonical process/operational docs: guides, rules, specs, standards, contracts, SVP, testing, reference",
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dim": EMBEDDING_DIM,
            },
        )
        print(f"Created collection '{COLLECTION_NAME}'")

    ids = [make_doc_id(d["id_parts"]) for d in docs]
    texts = [d["text"] for d in docs]
    metadatas = [d["metadata"] for d in docs]

    # Deduplicate by id (keep last)
    seen_ids: dict[str, int] = {}
    for i, doc_id in enumerate(ids):
        seen_ids[doc_id] = i
    dedup = sorted(seen_ids.values())
    ids = [ids[i] for i in dedup]
    texts = [texts[i] for i in dedup]
    metadatas = [metadatas[i] for i in dedup]
    print(f"After dedup: {len(ids)} unique chunks")

    total = len(ids)
    reporter = ProgressReporter(total=total, label="Embedding + upserting process_docs")
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
    parser = argparse.ArgumentParser(description="Ingest process_docs into canonical Chroma store")
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
