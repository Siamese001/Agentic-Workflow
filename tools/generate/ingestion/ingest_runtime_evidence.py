"""Ingest runtime evidence into the canonical `runtime_evidence` ChromaDB collection.

Sources (real runtime/operational evidence — no quarantined traces):
  1. logs/runtime_state.json           — agent execution traces, layer transitions
  2. logs/compliance_reports/*.json    — coverage, healing actions, forensics
  3. logs/l4_state/**/*.json           — L4 healing records
  4. data/golden_state/healing_intakes/*.json  — individual healing intake records
  5. docs/reports/evidence/*.md        — narrative evidence documents
  6. docs/reports/rcas/*.md            — incident RCA documents
  7. docs/rca/*.md                     — additional RCA docs
  8. docs/runbooks/*.md                — incident playbooks

NOTE: data/corpus/healing_contexts_corpus.jsonl is EXCLUDED — it contains only
content_hash/trace_id with no document body (same source as the quarantined `traces` collection).

Usage:
    python tools/generate/ingestion/ingest_runtime_evidence.py [--store-path PATH] [--dry-run]

Embedding: BAAI/bge-m3 (1024-dim, L2-normalized, cosine)
Collection: runtime_evidence  hnsw:space=cosine
"""

from __future__ import annotations

import argparse
import hashlib
import json
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


REPO_ROOT = _discover_repo_root(Path(__file__).resolve().parent)
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION_NAME = "runtime_evidence"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
BATCH_SIZE = 256
CHUNK_CHARS = 2000
CHUNK_OVERLAP = 200
MIN_BODY_CHARS = 60


def compute_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def make_doc_id(id_parts: tuple) -> str:
    raw = ":".join(id_parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


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


def flatten_json_to_text(obj, max_depth: int = 4, depth: int = 0) -> str:
    """Recursively flatten a JSON object to readable text."""
    if depth > max_depth:
        return str(obj)[:200]
    if isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            v_str = flatten_json_to_text(v, max_depth, depth + 1)
            parts.append(f"{k}: {v_str}")
        return "\n".join(parts)
    if isinstance(obj, list):
        return "\n".join(flatten_json_to_text(item, max_depth, depth + 1) for item in obj[:20])
    return str(obj)


def collect_runtime_state(repo_root: Path) -> list[dict]:
    """Load agent execution trace from logs/runtime_state.json."""
    docs = []
    rs_path = repo_root / "logs" / "runtime_state.json"
    if not rs_path.exists():
        return docs
    try:
        data = json.loads(rs_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return docs

    canonical_digest = compute_digest(str(data))
    rel_path = "logs/runtime_state.json"

    # Top-level summary chunk
    summary_fields = {k: v for k, v in data.items() if not isinstance(v, (list, dict))}
    summary_text = f"runtime_state summary\n{flatten_json_to_text(summary_fields)}"
    if len(summary_text.strip()) >= MIN_BODY_CHARS:
        docs.append(
            {
                "text": summary_text,
                "metadata": {
                    "artifact_type": "runtime_evidence",
                    "evidence_type": "execution_trace",
                    "file_path": rel_path,
                    "layer": "all",
                    "canonical_digest": canonical_digest,
                    "source": "runtime_state_summary",
                },
                "id_parts": (rel_path, "summary"),
            }
        )

    # Completed agents chunks
    completed = data.get("completed_agents", [])
    for i, agent_rec in tqdm(enumerate(completed[:100]), desc="Processing", unit="item"):
        text = f"agent execution record\n{flatten_json_to_text(agent_rec)}"
        if len(text.strip()) < MIN_BODY_CHARS:
            continue
        docs.append(
            {
                "text": text[:CHUNK_CHARS],
                "metadata": {
                    "artifact_type": "runtime_evidence",
                    "evidence_type": "agent_execution",
                    "file_path": rel_path,
                    "layer": str(agent_rec.get("layer", "unknown")),
                    "canonical_digest": canonical_digest,
                    "source": "runtime_state_agent",
                },
                "id_parts": (rel_path, "agent", str(i)),
            }
        )

    return docs


def collect_compliance_reports(repo_root: Path) -> list[dict]:
    """Load compliance/healing reports from logs/compliance_reports/."""
    docs = []
    cr_dir = repo_root / "logs" / "compliance_reports"
    if not cr_dir.exists():
        return docs

    for json_file in tqdm(sorted(cr_dir.rglob("*.json")), desc="Processing", unit="item"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rel_path = str(json_file.relative_to(repo_root)).replace("\\", "/")
        text = f"compliance report: {json_file.name}\n{flatten_json_to_text(data)}"
        if len(text.strip()) < MIN_BODY_CHARS:
            continue
        canonical_digest = compute_digest(text)
        for chunk_idx, chunk in tqdm(enumerate(chunk_text(text)), desc="Processing", unit="item"):
            docs.append(
                {
                    "text": chunk,
                    "metadata": {
                        "artifact_type": "runtime_evidence",
                        "evidence_type": "compliance_report",
                        "file_path": rel_path,
                        "layer": "all",
                        "chunk_index": chunk_idx,
                        "canonical_digest": canonical_digest,
                        "source": "compliance_report",
                    },
                    "id_parts": (rel_path, str(chunk_idx)),
                }
            )
    return docs


def collect_l4_healing_records(repo_root: Path) -> list[dict]:
    """Load L4 healing records from logs/l4_state/."""
    docs = []
    l4_dir = repo_root / "logs" / "l4_state"
    if not l4_dir.exists():
        return docs

    for json_file in tqdm(sorted(l4_dir.rglob("*.json")), desc="Processing", unit="item"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rel_path = str(json_file.relative_to(repo_root)).replace("\\", "/")
        text = f"L4 healing record: {json_file.name}\n{flatten_json_to_text(data)}"
        if len(text.strip()) < MIN_BODY_CHARS:
            continue
        canonical_digest = compute_digest(text)
        docs.append(
            {
                "text": text[:CHUNK_CHARS],
                "metadata": {
                    "artifact_type": "runtime_evidence",
                    "evidence_type": "healing_record",
                    "file_path": rel_path,
                    "layer": "L4",
                    "canonical_digest": canonical_digest,
                    "source": "l4_healing",
                },
                "id_parts": (rel_path, "record"),
            }
        )
    return docs


def collect_healing_intakes(repo_root: Path) -> list[dict]:
    """Load structured healing intake records from data/golden_state/healing_intakes/."""
    docs = []
    hi_dir = repo_root / "data" / "golden_state" / "healing_intakes"
    if not hi_dir.exists():
        return docs

    for json_file in tqdm(sorted(hi_dir.rglob("*.json")), desc="Processing", unit="item"):
        if json_file.name == "_index.json":
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rel_path = str(json_file.relative_to(repo_root)).replace("\\", "/")
        text = f"healing intake: {json_file.stem[:20]}\n{flatten_json_to_text(data)}"
        if len(text.strip()) < MIN_BODY_CHARS:
            continue
        canonical_digest = compute_digest(text)
        docs.append(
            {
                "text": text[:CHUNK_CHARS],
                "metadata": {
                    "artifact_type": "runtime_evidence",
                    "evidence_type": "healing_intake",
                    "file_path": rel_path,
                    "layer": "L4",
                    "canonical_digest": canonical_digest,
                    "source": "healing_intake",
                },
                "id_parts": (rel_path, "intake"),
            }
        )
    return docs


def collect_evidence_docs(repo_root: Path) -> list[dict]:
    """Load narrative evidence/RCA/runbook markdown docs."""
    docs = []
    md_sources = [
        ("docs/reports/evidence", "evidence_report"),
        ("docs/reports/rcas", "rca_report"),
        ("docs/rca", "rca_report"),
        ("docs/runbooks", "runbook"),
    ]
    seen: set[str] = set()
    for dir_rel, evidence_type in tqdm(md_sources, desc="Processing", unit="item"):
        d = repo_root / dir_rel
        if not d.exists():
            continue
        for md_file in tqdm(sorted(d.rglob("*.md")), desc="Processing", unit="item"):
            try:
                source = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if len(source.strip()) < MIN_BODY_CHARS:
                continue
            rel_path = str(md_file.relative_to(repo_root)).replace("\\", "/")
            if rel_path in seen:
                continue
            seen.add(rel_path)
            canonical_digest = compute_digest(source)
            for chunk_idx, chunk in tqdm(enumerate(chunk_text(source)), desc="Processing", unit="item"):
                docs.append(
                    {
                        "text": chunk,
                        "metadata": {
                            "artifact_type": "runtime_evidence",
                            "evidence_type": evidence_type,
                            "file_path": rel_path,
                            "layer": "all",
                            "chunk_index": chunk_idx,
                            "canonical_digest": canonical_digest,
                            "source": "markdown",
                        },
                        "id_parts": (rel_path, str(chunk_idx)),
                    }
                )
    return docs


def collect_all(repo_root: Path) -> list[dict]:
    collectors = [
        ("runtime_state", collect_runtime_state),
        ("compliance_reports", collect_compliance_reports),
        ("l4_healing", collect_l4_healing_records),
        ("healing_intakes", collect_healing_intakes),
        ("evidence_docs", collect_evidence_docs),
    ]
    all_docs: list[dict] = []
    for label, fn in collectors:
        batch = fn(repo_root)
        print(f"  [{label}] {len(batch)} documents")
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

    _ensure_repo_on_syspath(REPO_ROOT)
    from tools.progress_display import ProgressReporter

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
    model.max_seq_length = 512
    actual_dim = model.get_sentence_embedding_dimension()
    if actual_dim != EMBEDDING_DIM:
        raise RuntimeError(f"Model dimension mismatch: got {actual_dim}, expected {EMBEDDING_DIM}")
    print(f"Model loaded. dim={actual_dim}")

    print("Collecting runtime evidence documents ...")
    docs = collect_all(REPO_ROOT)
    print(f"Total collected: {len(docs)} documents")

    if dry_run:
        print("DRY RUN — stopping before Chroma write.")
        return

    store_path.mkdir(parents=True, exist_ok=True)
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
                "description": "Canonical runtime evidence: agent traces, healing records, compliance reports, RCAs",
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
    print(f"After dedup: {len(ids)} unique documents")

    total = len(ids)
    reporter = ProgressReporter(total=total, label="Embedding + upserting runtime_evidence")
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
    final_count = collection.count()
    print(f"\nDone. collection='{COLLECTION_NAME}' count={final_count} elapsed={elapsed:.1f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest runtime_evidence into canonical Chroma store")
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
