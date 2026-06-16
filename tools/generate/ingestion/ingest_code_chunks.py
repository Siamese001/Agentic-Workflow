"""Ingest live repo Python source into the canonical `code_chunks` ChromaDB collection.

Merges the schema from the legacy `repo_code_chunks` (provenance metadata) and
`code` (entity-level metadata) collections into a unified superset.

Usage:
    python tools/generate/ingestion/ingest_code_chunks.py [--store-path PATH] [--dry-run]

Embedding: BAAI/bge-m3 via sentence-transformers (1024-dim, L2-normalized)
Collection: code_chunks  hnsw:space=cosine
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

import argparse
import ast
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
COLLECTION_NAME = "code_chunks"
EMBEDDING_MODEL = BGE_M3_MODEL_ID
EMBEDDING_DIM = 1024
BATCH_SIZE = 512

SCAN_DIRS = [
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
    "infrastructure",
    "system_learning",
    "tools",
    "ops_scripts",
]

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "archives",
    "node_modules",
    "docs/archive/windsurf/legacy-tree",
    "vector_store",
    "artifacts",
}


def compute_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def detect_layer(file_path: Path) -> str:
    parts = file_path.parts
    for part in parts:
        if part.startswith("L") and len(part) >= 2 and part[1].isdigit():
            return part[:2]
    for part in parts:
        if part.startswith("apps_"):
            return "apps"
    if "tools" in parts:
        return "tools"
    if "ops_scripts" in parts:
        return "ops"
    if "system_learning" in parts:
        return "system_learning"
    if "infrastructure" in parts:
        return "infrastructure"
    return "unknown"


def detect_subsystem(file_path: Path) -> str:
    parts = file_path.parts
    for i, part in enumerate(parts):
        if part.startswith("L") and len(part) >= 2 and part[1].isdigit() and i + 1 < len(parts):
            return parts[i + 1]
    return "general"


def extract_entities(source: str, file_path: Path) -> list[dict]:
    """Extract top-level functions and classes from a Python source file."""
    entities = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return entities

    rel_path = _relative_to_repo(file_path, REPO_ROOT)
    module_name = rel_path.replace("\\", "/").replace("/", ".").removesuffix(".py")

    for node in ast.walk(tree):  # tqdm: AST walk, no bar needed
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if not hasattr(node, "lineno"):
            continue

        entity_type = "class" if isinstance(node, ast.ClassDef) else "function"
        name = node.name
        line_start = node.lineno
        line_end = getattr(node, "end_lineno", line_start)
        docstring = ast.get_docstring(node) or ""

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
        else:
            args = []

        source_lines = source.splitlines()
        body_text = "\n".join(source_lines[line_start - 1 : line_end])

        entities.append(
            {
                "name": name,
                "entity_type": entity_type,
                "module": module_name,
                "file_path": rel_path,
                "line_start": line_start,
                "line_end": line_end,
                "args": ",".join(args),
                "docstring": docstring[:300],
                "body": body_text,
                "layer": detect_layer(file_path),
                "subsystem": detect_subsystem(file_path),
            }
        )

    return entities


def chunk_file(source: str, file_path: Path, chunk_size: int = 60) -> list[dict]:
    """Split a file into overlapping line-based chunks."""
    lines = source.splitlines(keepends=True)
    if not lines:
        return []

    rel_path = _relative_to_repo(file_path, REPO_ROOT)
    chunks = []
    step = max(1, chunk_size - 10)

    for i in range(0, len(lines), step):  # tqdm: line-chunk window, no bar needed
        chunk_lines = lines[i : i + chunk_size]
        chunk_text = "".join(chunk_lines)
        if not chunk_text.strip():
            continue
        chunks.append(
            {
                "text": chunk_text,
                "file_path": rel_path,
                "chunk_index": i // step,
                "layer": detect_layer(file_path),
                "subsystem": detect_subsystem(file_path),
            }
        )

    return chunks


def collect_documents(repo_root: Path) -> list[dict]:
    """Walk repo source dirs and collect entity+chunk documents."""
    docs = []
    for scan_dir in SCAN_DIRS:  # tqdm: small fixed dir list, no bar needed
        base = repo_root / scan_dir
        if not base.exists():
            continue
        for py_file in base.rglob("*.py"):  # tqdm: filesystem rglob, no bar needed
            if any(excl in py_file.parts for excl in EXCLUDE_DIRS):
                continue
            try:
                source = py_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if not source.strip():
                continue

            canonical_digest = compute_digest(source)

            # Entity-level documents (functions + classes)
            for entity in extract_entities(source, py_file):  # tqdm: per-file entities, no bar needed
                doc_text = (
                    f"def {entity['name']}({entity['args']}):\n"
                    if entity["entity_type"] == "function"
                    else f"class {entity['name']}:\n"
                ) + entity["body"]
                docs.append(
                    {
                        "text": doc_text,
                        "metadata": {
                            "artifact_type": "code",
                            "chunk_type": "entity",
                            "file_path": entity["file_path"],
                            "layer": entity["layer"],
                            "subsystem": entity["subsystem"],
                            "entity_type": entity["entity_type"],
                            "name": entity["name"],
                            "module": entity["module"],
                            "line_start": entity["line_start"],
                            "line_end": entity["line_end"],
                            "args": entity["args"],
                            "docstring": entity["docstring"],
                            "canonical_digest": canonical_digest,
                            "has_sparse": False,
                        },
                        "id_parts": (entity["file_path"], entity["name"], str(entity["line_start"])),
                    }
                )

            # File-level chunks
            for chunk in chunk_file(source, py_file):  # tqdm: per-file chunks, no bar needed
                chunk_id_str = f"{chunk['file_path']}:chunk:{chunk['chunk_index']}"
                docs.append(
                    {
                        "text": chunk["text"],
                        "metadata": {
                            "artifact_type": "code",
                            "chunk_type": "file_chunk",
                            "file_path": chunk["file_path"],
                            "layer": chunk["layer"],
                            "subsystem": chunk["subsystem"],
                            "entity_type": "chunk",
                            "name": "",
                            "module": "",
                            "line_start": chunk["chunk_index"] * max(1, 60 - 10),
                            "line_end": 0,
                            "args": "",
                            "docstring": "",
                            "canonical_digest": canonical_digest,
                            "chunk_index": chunk["chunk_index"],
                            "has_sparse": False,
                        },
                        "id_parts": (chunk["file_path"], "chunk", str(chunk["chunk_index"])),
                    }
                )

    return docs


def make_doc_id(id_parts: tuple) -> str:
    raw = ":".join(id_parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def embed_batch(model, texts: list[str]) -> list[list[float]]:
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        batch_size=32,  # internal ST mini-batch; outer loop controls Chroma batch
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
        print("ERROR: sentence-transformers not installed. Run: pip install sentence-transformers")
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
    model.max_seq_length = 512  # prevent GPU OOM on very long code texts
    actual_dim = model.get_sentence_embedding_dimension()
    if actual_dim != EMBEDDING_DIM:
        raise RuntimeError(f"Model dimension mismatch: got {actual_dim}, expected {EMBEDDING_DIM}")
    print(f"Model loaded. dim={actual_dim}")

    print(f"Collecting documents from {REPO_ROOT} ...")
    docs = collect_documents(REPO_ROOT)
    print(f"Collected {len(docs)} documents (entities + chunks)")

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
                "description": "Canonical code chunks: entity-level functions/classes + file chunks",
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
    reporter = ProgressReporter(total=total, label="Embedding + upserting code_chunks")
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
    parser = argparse.ArgumentParser(description="Ingest code_chunks into canonical Chroma store")
    parser.add_argument(
        "--store-path",
        type=Path,
        default=CANONICAL_STORE,
        help=f"ChromaDB persistence directory (default: {CANONICAL_STORE})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Collect and embed without writing to Chroma")
    args = parser.parse_args()
    run(store_path=args.store_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
