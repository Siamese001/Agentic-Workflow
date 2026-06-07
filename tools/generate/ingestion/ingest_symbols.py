"""Ingest repo symbols into the canonical `symbols` ChromaDB collection.

Sources:
  1. Live ADG SQLite export (preferred — layer-aware, canonical_digest present)
  2. AST scan fallback (if ADG is unavailable)

Usage:
    python tools/generate/ingestion/ingest_symbols.py [--store-path PATH] [--dry-run]

Embedding: BAAI/bge-m3 via sentence-transformers (1024-dim, L2-normalized)
Collection: symbols  hnsw:space=cosine
"""

from __future__ import annotations

import argparse
import ast
import glob
import hashlib
import sqlite3
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
COLLECTION_NAME = "symbols"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
BATCH_SIZE = 512

SCAN_DIRS = [
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
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

ENTITY_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)


def compute_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def resolve_adg_sqlite() -> Path | None:
    pattern = str(REPO_ROOT / "artifacts" / "adg" / "adg_indexed_*.sqlite")
    candidates = sorted(glob.glob(pattern))
    if candidates:
        return Path(candidates[-1])
    return None


def detect_layer(file_path_str: str) -> str:
    parts = Path(file_path_str).parts
    for part in parts:
        if part.startswith("L") and len(part) >= 2 and part[1].isdigit():
            return part[:2]
    for part in parts:
        if part.startswith("apps_"):
            return "apps"
    if "tools" in parts:
        return "tools"
    if "system_learning" in parts:
        return "system_learning"
    if "infrastructure" in parts:
        return "infrastructure"
    return "unknown"


def load_from_adg(adg_path: Path) -> list[dict]:
    """Load symbol records from ADG SQLite. Returns empty list on any failure."""
    docs = []
    try:
        with sqlite3.connect(str(adg_path), timeout=10) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Nodes table columns vary by ADG version — probe first
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cur.fetchall()}
            if "nodes" not in tables:
                return []

            cur.execute("PRAGMA table_info(nodes)")
            cols = {row[1] for row in cur.fetchall()}

            # node_type column name varies by ADG version — probe
            node_type_col = None
            for candidate in ("node_type", "kind", "type", "entity_type"):
                if candidate in cols:
                    node_type_col = candidate
                    break

            select_cols = ["id", "adg_name", "layer"]
            if node_type_col:
                select_cols.append(node_type_col)
            if "file_path" in cols:
                select_cols.append("file_path")
            if "canonical_digest" in cols:
                select_cols.append("canonical_digest")
            if "confidence" in cols:
                select_cols.append("confidence")

            query = f"SELECT {', '.join(select_cols)} FROM nodes LIMIT 200000"
            cur.execute(query)
            rows = cur.fetchall()

        for row in rows:  # tqdm: DB result rows, no bar needed
            adg_name = row["adg_name"] or ""
            node_type = (row[node_type_col] if node_type_col else None) or "unknown"
            layer = row["layer"] or detect_layer(row["file_path"] if "file_path" in cols else "")
            file_path = row["file_path"] if "file_path" in cols else ""
            canonical_digest = (
                row["canonical_digest"] if "canonical_digest" in cols else compute_digest(adg_name)
            )
            confidence = row["confidence"] if "confidence" in cols else "MEDIUM"

            # Derive symbol_name from adg_name (strip ADG:: prefix patterns)
            symbol_name = adg_name
            for prefix in ("ADG::Module::", "ADG::Function::", "ADG::Class::", "ADG::"):
                if adg_name.startswith(prefix):
                    symbol_name = adg_name[len(prefix) :]
                    break

            doc_text = f"{node_type}: {adg_name}\nLayer: {layer}\nPath: {file_path}\nSymbol: {symbol_name}"

            docs.append(
                {
                    "text": doc_text,
                    "metadata": {
                        "artifact_type": "sym",
                        "symbol_name": symbol_name,
                        "adg_name": adg_name,
                        "entity_type": node_type,
                        "identity_kind": "adg_node",
                        "file_path": str(file_path),
                        "layer": str(layer),
                        "canonical_digest": canonical_digest,
                        "confidence": str(confidence),
                        "object_id": f"urn:agentic:symbol:{adg_name}",
                    },
                    "id_parts": (adg_name, node_type, str(layer)),
                }
            )

    except (sqlite3.Error, KeyError, TypeError) as exc:
        print(f"  WARNING: ADG load failed ({exc}) — falling back to AST scan")
        return []

    return docs


def load_from_ast(repo_root: Path) -> list[dict]:
    """Fallback: extract symbols from live AST scan."""
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
            rel_path = _relative_to_repo(py_file, repo_root)
            module_name = rel_path.replace("\\", "/").replace("/", ".").removesuffix(".py")
            layer = detect_layer(rel_path)

            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue

            # Module-level symbol
            docs.append(
                {
                    "text": (f"module: {module_name}\nLayer: {layer}\nPath: {rel_path}"),
                    "metadata": {
                        "artifact_type": "sym",
                        "symbol_name": module_name,
                        "adg_name": f"ADG::Module::{rel_path}",
                        "entity_type": "module",
                        "identity_kind": "repo_module",
                        "file_path": rel_path,
                        "layer": layer,
                        "canonical_digest": canonical_digest,
                        "confidence": "HIGH",
                        "object_id": f"urn:agentic:module:{module_name}",
                    },
                    "id_parts": (rel_path, "module", layer),
                }
            )

            for node in ast.walk(tree):  # tqdm: AST walk, no bar needed
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                if not hasattr(node, "lineno"):
                    continue

                entity_type = "class" if isinstance(node, ast.ClassDef) else "function"
                fqn = f"{module_name}.{node.name}"

                docs.append(
                    {
                        "text": (
                            f"{entity_type}: {node.name}\n"
                            f"Module: {module_name}\n"
                            f"Layer: {layer}\n"
                            f"Path: {rel_path}:{node.lineno}"
                        ),
                        "metadata": {
                            "artifact_type": "sym",
                            "symbol_name": fqn,
                            "adg_name": f"ADG::{entity_type.capitalize()}::{fqn}",
                            "entity_type": entity_type,
                            "identity_kind": f"repo_{entity_type}",
                            "file_path": rel_path,
                            "layer": layer,
                            "canonical_digest": canonical_digest,
                            "confidence": "HIGH",
                            "object_id": f"urn:agentic:{entity_type}:{fqn}",
                        },
                        "id_parts": (rel_path, node.name, str(node.lineno)),
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
    model.max_seq_length = 512  # prevent GPU OOM on very long symbol texts
    actual_dim = model.get_sentence_embedding_dimension()
    if actual_dim != EMBEDDING_DIM:
        raise RuntimeError(f"Model dimension mismatch: got {actual_dim}, expected {EMBEDDING_DIM}")
    print(f"Model loaded. dim={actual_dim}")

    # Prefer ADG SQLite source
    adg_path = resolve_adg_sqlite()
    if adg_path:
        print(f"ADG SQLite found: {adg_path}")
        docs = load_from_adg(adg_path)
        source_label = "adg_sqlite"
    else:
        docs = []

    if not docs:
        print("Falling back to live AST scan ...")
        docs = load_from_ast(REPO_ROOT)
        source_label = "ast_scan"

    print(f"Collected {len(docs)} symbols from source={source_label}")

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
                "description": "Canonical symbols: modules, functions, classes from ADG or AST scan",
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dim": EMBEDDING_DIM,
                "source": source_label,
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
    print(f"After dedup: {len(ids)} unique symbols")

    total = len(ids)
    reporter = ProgressReporter(total=total, label="Embedding + upserting symbols")
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
    parser = argparse.ArgumentParser(description="Ingest symbols into canonical Chroma store")
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
