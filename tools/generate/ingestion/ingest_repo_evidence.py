"""Wave B2 ingestion — repo_evidence ChromaDB collection.

Status  : Active (Wave B2)
Replaces: local-source portions of ingest_curated_agent_docs.py (Lane C)
          ingest_arch_docs.py (Lane D)
          Both scripts are RETIRED in Wave B2.
See     : docs/requirements/wave_b_chromadb_topology.md
          docs/requirements/wave_b_metadata_contract.md

Collect repo-internal documents into the ``repo_evidence`` collection.

Lane C — repo_canonical / T4_repo_canonical:
    16 hand-curated local docs (ADRs, process maps, SVPs, standards, rules).
    invalid_for_normative_use = True (repo evidence only — not for requirements).

Lane D — repo_implementation / T4_implementation_evidence:
    Broad markdown scan of docs/ and top-level .md files (same scope as
    the retired ingest_arch_docs.py).  All noisy subdirs excluded.
    invalid_for_normative_use = True (always).

Chunking:
    Section-aware heading-based chunking (same algorithm as ingest_arch_docs.py).
    Heading path breadcrumb is preserved for each chunk.

Metadata contract:
    Wave B mandatory fields enforced fail-closed at validate_metadata().
    15 required fields (14 mandatory + file_path conditional).

Fail-closed rules:
    required=True local file missing → raise IngestionError (abort)
    malformed metadata               → raise MetadataContractError (abort)

Usage:
    python tools/generate/ingestion/ingest_repo_evidence.py [--dry-run]
    python tools/generate/ingestion/ingest_repo_evidence.py [--store-path PATH]
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
from agentic_core.L0_routing.config.path_constants import ADR_DIR

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION_NAME = "repo_evidence"
EMBEDDING_MODEL = BGE_M3_MODEL_ID
EMBEDDING_DIM = 1024
BATCH_SIZE = 256
CHUNK_CHARS = 2000
CHUNK_OVERLAP = 200
MIN_BODY_CHARS = 80

SCAN_DIRS: list[str] = ["docs"]
TOP_LEVEL_MD: list[str] = ["README.md", "AGENTS.md"]
EXCLUDE_DIRS: set[str] = {
    "__pycache__",
    ".git",
    "archives",
    "_archive",
    "node_modules",
    "docs/archive/windsurf/legacy-tree",
    "vector_store",
    "artifacts",
    ".pytest_cache",
    "data",
    "reports",
    "plans",
    "evidence",
    "windsurf",
}
EXCLUDE_PATTERNS: list[str] = [r"CHANGELOG", r"changelog", r"\.min\."]

# Wave B mandatory fields for repo_evidence (15 total: 14 mandatory + file_path).
REQUIRED_METADATA_KEYS: frozenset[str] = frozenset(
    {
        "source_collection",
        "source_band",
        "authority_tier",
        "normative_scope",
        "invalid_for_normative_use",
        "source_type",
        "topic_bucket",
        "doc_family",
        "source_url",
        "heading_path",
        "collapse_group",
        "title",
        "chunk_index",
        "canonical_digest",
        "file_path",
    }
)

_VALID_SOURCE_BANDS: frozenset[str] = frozenset({"repo_canonical", "repo_implementation"})
_VALID_AUTHORITY_TIERS: frozenset[str] = frozenset({"T4_repo_canonical", "T4_implementation_evidence"})


# ── Lane C — 16 hand-curated local sources ────────────────────────────────────
# Mirrors the local entries from the retired ingest_curated_agent_docs.py.

REPO_CANONICAL_SOURCES: list[dict] = [
    {
        "path": f"{ADR_DIR}/adr-0043-structural-agentic-checks.md",
        "title": "ADR-0043: Structural Conformance & Agentic Anti-Pattern Checks",
        "doc_family": "adr",
        "topic_bucket": "arch_standards",
        "collapse_group": "repo_adr",
        "required": True,
    },
    {
        "path": f"{ADR_DIR}/adr-002-interface-protocol-first.md",
        "title": "ADR-002: Interface & Protocol-First Design",
        "doc_family": "adr",
        "topic_bucket": "arch_standards",
        "collapse_group": "repo_adr",
        "required": True,
    },
    {
        "path": f"{ADR_DIR}/adr-0042-skills-consolidation.md",
        "title": "ADR-0042: Skills Consolidation",
        "doc_family": "adr",
        "topic_bucket": "arch_standards",
        "collapse_group": "repo_adr",
        "required": True,
    },
    {
        "path": f"{ADR_DIR}/ADR-018-chromadb-as-canonical-vector-store.md",
        "title": "ADR-018: ChromaDB as Canonical Vector Store",
        "doc_family": "adr",
        "topic_bucket": "rag_retrieval",
        "collapse_group": "repo_adr",
        "required": True,
    },
    {
        "path": f"{ADR_DIR}/ADR-019-adg-materialized-views.md",
        "title": "ADR-019: ADG Materialized Views",
        "doc_family": "adr",
        "topic_bucket": "arch_standards",
        "collapse_group": "repo_adr",
        "required": True,
    },
    # Removed 2026-04-27 (plan a3c9f1 closure): the doctrine notes in
    # docs/reference/_notes/ are scratchpads, not authority. The agent's
    # runtime KB must be grounded in the REQ_ID-validated Tier A SSOT under
    # docs/reference/00A..06,99 and docs/reference/contracts/step1/.
    {
        "path": "docs/architecture/governed-app-contract.md",
        "title": "Governed App Contract",
        "doc_family": "contract",
        "topic_bucket": "safety_eval",
        "collapse_group": "repo_architecture",
        "required": True,
    },
    {
        "path": "docs/architecture/eval_pipeline_acceptance.md",
        "title": "Eval Pipeline Acceptance Criteria",
        "doc_family": "architecture",
        "topic_bucket": "safety_eval",
        "collapse_group": "repo_architecture",
        "required": True,
    },
    {
        "path": "docs/svp/Retrieval_System_SVP.md",
        "title": "Retrieval System SVP",
        "doc_family": "spec",
        "topic_bucket": "rag_retrieval",
        "collapse_group": "repo_svp",
        "required": True,
    },
    {
        "path": "docs/svp/Technical_Implementation_Guide.md",
        "title": "Technical Implementation Guide (SVP)",
        "doc_family": "guide",
        "topic_bucket": "rag_retrieval",
        "collapse_group": "repo_svp",
        "required": True,
    },
    {
        "path": ".claude/rules/constitutional.md",
        "title": "Constitutional Floor — Hard Constraints",
        "doc_family": "standard",
        "topic_bucket": "safety_eval",
        "collapse_group": "repo_standards",
        "required": True,
    },
    {
        "path": ".claude/rules/global_rules.md",
        "title": "Global Rules — Always-On Policy",
        "doc_family": "standard",
        "topic_bucket": "arch_standards",
        "collapse_group": "repo_standards",
        "required": True,
    },
    {
        "path": "docs/STANDARDS.md",
        "title": "Repository Standards",
        "doc_family": "standard",
        "topic_bucket": "arch_standards",
        "collapse_group": "repo_standards",
        "required": True,
    },
    {
        "path": "docs/requirements/normative_requirements_spec.md",
        "title": "Agentic Routing and Retrieval System — Normative Requirements Specification",
        "doc_family": "spec",
        "topic_bucket": "arch_standards",
        "collapse_group": "repo_standards",
        "required": True,
    },
    {
        "path": "docs/architecture/adg-graph-projection.md",
        "title": "ADG Graph Projection Architecture",
        "doc_family": "architecture",
        "topic_bucket": "arch_standards",
        "collapse_group": "repo_architecture",
        "required": False,
    },
    {
        "path": "docs/architecture/healing_dispatch_routing_adr.md",
        "title": "ADR — Confidence-Scored Tiered Healing Dispatch Routing (F25-int)",
        "doc_family": "architecture",
        "topic_bucket": "orchestration",
        "collapse_group": "repo_architecture",
        "required": True,
    },
    {
        "path": "AGENTS.md",
        "title": "Agents Guide",
        "doc_family": "guide",
        "topic_bucket": "orchestration",
        "collapse_group": "repo_standards",
        "required": False,
    },
    {
        "path": "docs/architecture/write_governance_note.md",
        "title": "Write-Governance Advisory Note (F28 / WC-G04)",
        "doc_family": "architecture",
        "topic_bucket": "arch_standards",
        "collapse_group": "repo_architecture",
        "required": True,
    },
]


# ── Exceptions ────────────────────────────────────────────────────────────────


class IngestionError(RuntimeError):
    """Fail-closed: required source missing or config error."""


class MetadataContractError(ValueError):
    """Fail-closed: chunk metadata violates Wave B mandatory contract."""


# ── Utilities ─────────────────────────────────────────────────────────────────


def compute_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def make_doc_id(id_parts: tuple[str, ...]) -> str:
    return hashlib.sha256(":".join(id_parts).encode("utf-8")).hexdigest()[:24]


def chunk_text(text: str, chunk_size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    chunks: list[str] = []
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


def chunk_by_headings(
    text: str,
    max_chars: int = CHUNK_CHARS,
) -> list[tuple[str, str]]:
    """Split markdown by H1-H3 headings; return list of (heading_path, chunk_text)."""
    heading_re = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    boundaries: list[tuple[int, int, str]] = []
    for m in heading_re.finditer(text):
        level = len(m.group(1))
        title = m.group(2).strip()
        boundaries.append((m.start(), level, title))
    boundaries.append((len(text), 0, ""))

    if len(boundaries) <= 1:
        chunks = chunk_text(text, max_chars)
        return [("no-headings", c) for c in chunks]

    stack: list[str] = ["", "", ""]
    results: list[tuple[str, str]] = []

    for i, (pos, level, title) in enumerate(boundaries[:-1]):
        next_pos = boundaries[i + 1][0]
        stack[level - 1] = title
        for j in range(level, 3):
            stack[j] = ""
        heading_path = " > ".join(p for p in stack if p)
        section = text[pos:next_pos].strip()
        if len(section) < MIN_BODY_CHARS:
            continue
        for chunk in chunk_text(section, max_chars):
            results.append((heading_path, chunk))

    if not results:
        return [("no-headings", c) for c in chunk_text(text, max_chars)]
    return results


def _extract_title(text: str, path: Path) -> str:
    """Return first H1 or stem-based fallback, max 200 chars."""
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()[:200]
    return re.sub(r"[-_]", " ", path.stem)[:200]


def should_exclude(path: Path) -> bool:
    """Return True if path falls under any EXCLUDE_DIRS entry."""
    parts = {p.lower() for p in path.parts}
    return bool(parts & {d.lower() for d in EXCLUDE_DIRS})


def _matches_exclude_pattern(path: Path) -> bool:
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, path.name):
            return True
    return False


# ── Doc family / topic bucket helpers ─────────────────────────────────────────

_DOC_FAMILY_MAP: dict[str, str] = {
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
    "references": "reference",
    "policies": "policy",
    "policy": "policy",
    "svp": "spec",
}


def _compute_doc_family(path: Path) -> str:
    for part in reversed(path.parts):
        if part.lower() in _DOC_FAMILY_MAP:
            return _DOC_FAMILY_MAP[part.lower()]
    name_lower = path.name.lower()
    if name_lower in ("readme.md", "agents.md"):
        return "overview"
    return "doc"


def _compute_collapse_group(path: Path) -> str:
    rel = str(path).replace("\\", "/")
    if "adr" in rel.lower():
        return "repo_adr"
    if "svp" in rel.lower():
        return "repo_svp"
    if "architecture" in rel.lower():
        return "repo_architecture"
    if "docs/archive/windsurf/legacy-tree" in rel:
        return "repo_standards"
    return "repo_docs"


# ── Metadata ──────────────────────────────────────────────────────────────────


def _build_metadata_canonical(
    entry: dict,
    heading_path: str,
    chunk_index: int,
    canonical_digest: str,
    doc_title: str,
    rel_path: str,
) -> dict:
    """Build Wave B metadata for Lane C (repo_canonical) chunks."""
    return {
        "source_collection": COLLECTION_NAME,
        "source_band": "repo_canonical",
        "authority_tier": "T4_repo_canonical",
        "normative_scope": "repo_internal",
        "invalid_for_normative_use": True,
        "source_type": "local",
        "topic_bucket": entry["topic_bucket"],
        "doc_family": entry["doc_family"],
        "source_url": rel_path[:200],
        "heading_path": heading_path[:200],
        "collapse_group": entry["collapse_group"],
        "title": doc_title[:200],
        "chunk_index": chunk_index,
        "canonical_digest": canonical_digest,
        "file_path": rel_path[:200],
    }


def _build_metadata_implementation(
    file_path: Path,
    rel_path: str,
    heading_path: str,
    chunk_index: int,
    canonical_digest: str,
    doc_title: str,
) -> dict:
    """Build Wave B metadata for Lane D (repo_implementation) chunks."""
    doc_family = _compute_doc_family(file_path)
    collapse_group = _compute_collapse_group(file_path)
    return {
        "source_collection": COLLECTION_NAME,
        "source_band": "repo_implementation",
        "authority_tier": "T4_implementation_evidence",
        "normative_scope": "repo_internal",
        "invalid_for_normative_use": True,
        "source_type": "local",
        "topic_bucket": "unclassified",
        "doc_family": doc_family,
        "source_url": rel_path[:200],
        "heading_path": heading_path[:200],
        "collapse_group": collapse_group,
        "title": doc_title[:200],
        "chunk_index": chunk_index,
        "canonical_digest": canonical_digest,
        "file_path": rel_path[:200],
    }


def validate_metadata(meta: dict) -> None:
    """Raise MetadataContractError if Wave B mandatory fields are missing or type-invalid."""
    missing = REQUIRED_METADATA_KEYS - set(meta.keys())
    if missing:
        raise MetadataContractError(f"Missing mandatory Wave B fields: {sorted(missing)}")
    if not isinstance(meta["chunk_index"], int):
        raise MetadataContractError(f"chunk_index must be int, got {type(meta['chunk_index'])}")
    if not isinstance(meta["invalid_for_normative_use"], bool):
        raise MetadataContractError(
            f"invalid_for_normative_use must be bool, got {type(meta['invalid_for_normative_use'])}"
        )
    if meta["source_band"] not in _VALID_SOURCE_BANDS:
        raise MetadataContractError(f"source_band {meta['source_band']!r} not in {_VALID_SOURCE_BANDS}")
    if meta["authority_tier"] not in _VALID_AUTHORITY_TIERS:
        raise MetadataContractError(
            f"authority_tier {meta['authority_tier']!r} not in {_VALID_AUTHORITY_TIERS}"
        )


# ── Lane C collection ─────────────────────────────────────────────────────────


def collect_canonical_docs(repo_root: Path) -> list[dict]:
    """Collect Lane C: 16 curated local documents.

    Returns list of dicts: ``{text, metadata, id_parts}``.
    Raises ``IngestionError`` for required=True missing files.
    """
    all_docs: list[dict] = []

    for entry in REPO_CANONICAL_SOURCES:
        rel_path = entry["path"]
        abs_path = repo_root / rel_path
        if not abs_path.exists():
            if entry["required"]:
                raise IngestionError(f"required=True file missing: {rel_path}")
            continue
        try:
            source = abs_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            if entry["required"]:
                raise IngestionError(f"required=True file unreadable: {rel_path} — {exc}") from exc
            continue

        if not source.strip():
            if entry["required"]:
                raise IngestionError(f"required=True file is empty: {rel_path}")
            continue

        canonical_digest = compute_digest(source)
        doc_title = _extract_title(source, abs_path)
        if entry["title"]:
            doc_title = entry["title"]

        for chunk_index, (heading_path, chunk_text_body) in enumerate(chunk_by_headings(source)):
            meta = _build_metadata_canonical(
                entry=entry,
                heading_path=heading_path,
                chunk_index=chunk_index,
                canonical_digest=canonical_digest,
                doc_title=doc_title,
                rel_path=rel_path.replace("\\", "/"),
            )
            validate_metadata(meta)
            all_docs.append(
                {
                    "text": chunk_text_body,
                    "metadata": meta,
                    "id_parts": ("repo_canonical", rel_path, str(chunk_index)),
                }
            )

    return all_docs


# ── Lane D collection ─────────────────────────────────────────────────────────


def collect_repo_docs(repo_root: Path) -> list[dict]:
    """Collect Lane D: broad markdown scan of docs/ and top-level .md files.

    Returns list of dicts: ``{text, metadata, id_parts}``.
    Skips files already covered by Lane C (by relative path).
    """
    lane_c_paths: set[str] = {e["path"].replace("\\", "/") for e in REPO_CANONICAL_SOURCES}
    all_docs: list[dict] = []
    seen_rel: set[str] = set(lane_c_paths)

    # Scan SCAN_DIRS
    for dir_rel in SCAN_DIRS:
        base = repo_root / dir_rel
        if not base.exists():
            continue
        for f in sorted(base.rglob("*.md")):
            if not f.is_file():
                continue
            if should_exclude(f):
                continue
            if _matches_exclude_pattern(f):
                continue
            rel_path = str(f.relative_to(repo_root)).replace("\\", "/")
            if rel_path in seen_rel:
                continue
            seen_rel.add(rel_path)
            try:
                source = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if not source.strip() or len(source.strip()) < MIN_BODY_CHARS:
                continue
            canonical_digest = compute_digest(source)
            doc_title = _extract_title(source, f)
            for chunk_index, (heading_path, chunk_text_body) in enumerate(chunk_by_headings(source)):
                meta = _build_metadata_implementation(
                    file_path=f,
                    rel_path=rel_path,
                    heading_path=heading_path,
                    chunk_index=chunk_index,
                    canonical_digest=canonical_digest,
                    doc_title=doc_title,
                )
                validate_metadata(meta)
                all_docs.append(
                    {
                        "text": chunk_text_body,
                        "metadata": meta,
                        "id_parts": ("repo_impl", rel_path, str(chunk_index)),
                    }
                )

    # Top-level .md files
    for name in TOP_LEVEL_MD:
        f = repo_root / name
        if not f.is_file():
            continue
        rel_path = name
        if rel_path in seen_rel:
            continue
        seen_rel.add(rel_path)
        try:
            source = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not source.strip() or len(source.strip()) < MIN_BODY_CHARS:
            continue
        canonical_digest = compute_digest(source)
        doc_title = _extract_title(source, f)
        for chunk_index, (heading_path, chunk_text_body) in enumerate(chunk_by_headings(source)):
            meta = _build_metadata_implementation(
                file_path=f,
                rel_path=rel_path,
                heading_path=heading_path,
                chunk_index=chunk_index,
                canonical_digest=canonical_digest,
                doc_title=doc_title,
            )
            validate_metadata(meta)
            all_docs.append(
                {
                    "text": chunk_text_body,
                    "metadata": meta,
                    "id_parts": ("repo_impl", rel_path, str(chunk_index)),
                }
            )

    return all_docs


# ── Embedding helpers ─────────────────────────────────────────────────────────


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


# ── Run ───────────────────────────────────────────────────────────────────────


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

    print("Collecting Lane C (repo_canonical) docs ...")
    canonical_docs = collect_canonical_docs(REPO_ROOT)
    print(f"  Lane C: {len(canonical_docs)} chunks from {len(REPO_CANONICAL_SOURCES)} sources")

    print("Collecting Lane D (repo_implementation) docs ...")
    impl_docs = collect_repo_docs(REPO_ROOT)
    print(f"  Lane D: {len(impl_docs)} chunks from docs/ scan")

    all_docs = canonical_docs + impl_docs
    print(f"Total collected: {len(all_docs)} chunks")

    if dry_run:
        print(f"DRY RUN — stopping before Chroma write. chunks={len(all_docs)}")
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
                    "Wave B: repo evidence (Lane C repo_canonical + Lane D repo_implementation). "
                    "All chunks are invalid_for_normative_use=True."
                ),
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dim": EMBEDDING_DIM,
                "wave": "B2",
            },
        )
        print(f"Created collection '{COLLECTION_NAME}'")

    ids = [make_doc_id(tuple(d["id_parts"])) for d in all_docs]
    texts = [d["text"] for d in all_docs]
    metadatas = [d["metadata"] for d in all_docs]

    seen: dict[str, int] = {}
    for i, doc_id in enumerate(ids):
        seen[doc_id] = i
    dedup = sorted(seen.values())
    ids = [ids[i] for i in dedup]
    texts = [texts[i] for i in dedup]
    metadatas = [metadatas[i] for i in dedup]
    print(f"After dedup: {len(ids)} unique chunks")

    total = len(ids)
    reporter = ProgressReporter(total=total, label=f"Embedding + upserting {COLLECTION_NAME}")
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
    parser = argparse.ArgumentParser(description="Wave B2: Ingest repo-internal evidence into repo_evidence")
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
