"""Build persistent SQLite FTS5 sparse index from canonical ChromaDB collections.

Writes one sidecar DB per collection to data/cache/sparse/<collection>.db.

Schema per DB
─────────────
  docs(id TEXT PK, document TEXT, metadata TEXT)       -- raw source
  docs_fts(id, document)                               -- FTS5 virtual table
  term_freq(term TEXT, doc_id TEXT, freq INTEGER)      -- for BM25 offline scoring

Usage
─────
  python tools/generate/ingestion/build_sparse_index.py                     # all 4 targets
  python tools/generate/ingestion/build_sparse_index.py --collection symbols
  python tools/generate/ingestion/build_sparse_index.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from collections import Counter
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


def _safe_unlink(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


REPO_ROOT = _discover_repo_root(Path(__file__).resolve().parent)


def _resolve_chroma_path() -> Path:
    """ChromaDB source for the sparse build.

    Honors ``CHROMA_PERSIST_DIR`` (absolute or repo-relative) so the builder can read a
    relocated/pointed store — e.g. when run from a git worktree whose own
    ``data/cache/chromadb`` is empty but the canonical store lives elsewhere. Mirrors
    ``agentic_core.L4_state.config.chroma_paths.canonical_persist_dir``. Falls back to the
    repo-local ``data/cache/chromadb``.
    """
    override = os.environ.get("CHROMA_PERSIST_DIR", "").strip()
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = REPO_ROOT / p
        return p.resolve()
    return REPO_ROOT / "data" / "cache" / "chromadb"


CHROMA_PATH = _resolve_chroma_path()
# Sparse sidecars are read by bm25_store from ``<repo_root>/data/cache/sparse`` (no env
# override there), so we always WRITE to the repo-local sparse dir to keep reads/writes aligned.
SPARSE_PATH = REPO_ROOT / "data" / "cache" / "sparse"

TARGET_COLLECTIONS = [
    # Original tools/generate/ingestion/ targets (legacy)
    "code_chunks",
    "symbols",
    "arch_docs",
    "tests_guardrails",
    "runtime_evidence",
    "process_docs",
    "ext_knowledge",
    "incidents_rca",
    # tools/ingestion/ pipeline collection names (W4.1)
    "repo_code_chunks",
    "docs",
    "repo_tests_guardrails",
    "repo_runtime_evidence",
    "repo_incidents_rca",
    "traces",
    "agentic_best_practices",
    "repo_git_history",
    # apps_rg C0.2 hybrid sparse lane (Brown & Brown product proof)
    "fact_vectors",
]

BATCH_SIZE = 500


# ---------------------------------------------------------------------------
# Lightweight tokenizer — avoids importing ASTAwareTokenizer (heavy _emit_ side-effects)
# ---------------------------------------------------------------------------

_STOP = frozenset(
    "self cls none true false return if else elif for while try except finally with "
    "as import from def class pass break continue and or not in is lambda yield raise "
    "assert del global nonlocal async await the a an of to".split()
)

_SPLIT_RE = re.compile(r"[^A-Za-z0-9_]+")
_CAMEL_RE = re.compile(r"([a-z0-9])([A-Z])")


def _split_identifier(name: str) -> list[str]:
    """Split snake_case and CamelCase into lowercase sub-tokens."""
    parts = name.split("_")
    result: list[str] = []
    for part in parts:
        for sub in _CAMEL_RE.sub(r"\1 \2", part).split():
            if len(sub) > 1:
                result.append(sub.lower())
    return result


def tokenize(text: str) -> list[str]:
    """Tokenize text for sparse indexing.

    Strategy:
    - Split on non-alphanumeric boundaries (space, punctuation, colons, etc.)
    - Emit the raw token (e.g. ``bge_embed_query``) as-is for exact lookup
    - Also emit CamelCase/snake_case sub-tokens for partial matching
    - FTS5 will further sub-tokenize on underscore via unicode61 defaults,
      so storing the compound token lets term_freq find it exactly.
    - Deduplicate within document to keep term_freq counts sensible.
    """
    # Split on everything except alphanumeric and underscore
    raw_tokens = re.split(r"[^A-Za-z0-9_]+", text)
    tokens: list[str] = []
    seen: set[str] = set()

    def _emit(t: str) -> None:
        if t and t not in seen:
            seen.add(t)
            tokens.append(t)

    for tok in tqdm(raw_tokens, desc="Processing", unit="item"):
        if not tok or len(tok) < 2:
            continue
        lower = tok.lower()
        if lower in _STOP:
            continue
        # 1. Whole token (e.g. bge_embed_query, QueryRouter)
        _emit(lower)
        # 2. Sub-tokens from snake_case / CamelCase splitting
        for sub in _split_identifier(tok):
            if sub not in _STOP:
                _emit(sub)

    return tokens


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS docs (
            id       TEXT PRIMARY KEY,
            document TEXT NOT NULL,
            metadata TEXT NOT NULL DEFAULT '{}'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts
            USING fts5(
                id UNINDEXED,
                document,
                content=docs,
                content_rowid=rowid,
                tokenize="unicode61 tokenchars '_'"
            );

        CREATE TABLE IF NOT EXISTS term_freq (
            term   TEXT NOT NULL,
            doc_id TEXT NOT NULL,
            freq   INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (term, doc_id)
        );

        CREATE INDEX IF NOT EXISTS idx_term ON term_freq(term);
        CREATE INDEX IF NOT EXISTS idx_doc  ON term_freq(doc_id);

        CREATE TABLE IF NOT EXISTS meta (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
        """
    )
    conn.commit()


def _rebuild_fts(conn: sqlite3.Connection) -> None:
    """Rebuild FTS5 index from docs table."""
    conn.execute("INSERT INTO docs_fts(docs_fts) VALUES('rebuild')")
    conn.commit()


def _upsert_docs_batch(
    conn: sqlite3.Connection,
    rows: list[tuple[str, str, str]],
) -> None:
    """Insert/replace (id, document, metadata) rows."""
    conn.executemany(
        "INSERT OR REPLACE INTO docs(id, document, metadata) VALUES(?, ?, ?)",
        rows,
    )
    conn.commit()


def _upsert_term_batch(
    conn: sqlite3.Connection,
    term_rows: list[tuple[str, str, int]],
) -> None:
    conn.executemany(
        """INSERT INTO term_freq(term, doc_id, freq) VALUES(?, ?, ?)
           ON CONFLICT(term, doc_id) DO UPDATE SET freq = excluded.freq""",
        term_rows,
    )
    conn.commit()


def _delete_docs_batch(conn: sqlite3.Connection, doc_ids: list[str]) -> None:
    """Delete stale sparse rows for document ids before incremental replacement."""
    conn.executemany("DELETE FROM term_freq WHERE doc_id = ?", [(doc_id,) for doc_id in doc_ids])
    conn.executemany("DELETE FROM docs WHERE id = ?", [(doc_id,) for doc_id in doc_ids])
    conn.commit()


def _refresh_meta(conn: sqlite3.Connection, collection_name: str) -> dict[str, int]:
    doc_count = int(conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0] or 0)
    term_count = int(conn.execute("SELECT COUNT(*) FROM term_freq").fetchone()[0] or 0)
    conn.executemany(
        "INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)",
        [
            ("collection", collection_name),
            ("doc_count", str(doc_count)),
            ("term_count", str(term_count)),
            ("built_at", str(time.time())),
        ],
    )
    conn.commit()
    return {"doc_count": doc_count, "term_count": term_count}


def upsert_documents(
    collection_name: str,
    rows: list[dict[str, object]],
    *,
    sparse_dir: str | Path | None = None,
) -> dict[str, int]:
    """Incrementally upsert documents into one SQLite FTS5 sparse sidecar.

    W2 promotion uses this after dense Chroma upsert so learned facts become visible to
    both dense and sparse lanes without requiring a full sidecar rebuild.
    """
    target_dir = Path(sparse_dir) if sparse_dir is not None else SPARSE_PATH
    target_dir.mkdir(parents=True, exist_ok=True)
    db_path = target_dir / f"{collection_name}.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    _create_schema(conn)

    doc_rows: list[tuple[str, str, str]] = []
    term_rows: list[tuple[str, str, int]] = []
    for row in rows:
        doc_id = str(row.get("id") or "").strip()
        if not doc_id:
            continue
        document = str(row.get("document") or "")
        metadata = row.get("metadata")
        metadata_json = json.dumps(metadata if isinstance(metadata, dict) else {})
        doc_rows.append((doc_id, document, metadata_json))
        for term, freq in Counter(tokenize(document)).items():
            term_rows.append((term, doc_id, freq))

    if doc_rows:
        _delete_docs_batch(conn, [row[0] for row in doc_rows])
        _upsert_docs_batch(conn, doc_rows)
        _upsert_term_batch(conn, term_rows)
        _rebuild_fts(conn)
    stats = _refresh_meta(conn, collection_name)
    conn.close()
    return {"upserted_count": len(doc_rows), **stats}


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------


def build_for_collection(
    collection_name: str,
    dry_run: bool = False,
    *,
    chroma_path: str | Path | None = None,
    sparse_dir: str | Path | None = None,
) -> dict[str, int]:
    """Fetch all docs from Chroma collection and write sparse sidecar DB.

    Returns stats dict with doc_count, term_count.
    """
    try:
        import chromadb
    except ImportError:
        print("ERROR: chromadb not installed.")
        sys.exit(1)

    source_chroma_path = Path(chroma_path) if chroma_path is not None else CHROMA_PATH
    chroma = chromadb.PersistentClient(path=str(source_chroma_path))

    try:
        col = chroma.get_collection(collection_name)
    except (ValueError, KeyError):
        print(f"  SKIP: collection '{collection_name}' not found in Chroma store.")
        return {"doc_count": 0, "term_count": 0}

    total = col.count()
    if total == 0:
        print(f"  SKIP: collection '{collection_name}' is empty.")
        return {"doc_count": 0, "term_count": 0}

    if dry_run:
        print(f"  DRY RUN: '{collection_name}' has {total} docs — would write sparse index.")
        return {"doc_count": total, "term_count": 0}

    target_dir = Path(sparse_dir) if sparse_dir is not None else SPARSE_PATH
    db_path = target_dir / f"{collection_name}.db"
    target_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    _create_schema(conn)
    conn.execute("DELETE FROM term_freq")
    conn.execute("DELETE FROM docs")
    conn.commit()

    offset = 0
    doc_count = 0
    all_term_rows: list[tuple[str, str, int]] = []

    print(f"  Fetching {total} docs from '{collection_name}' ...")
    t0 = time.time()

    while offset < total:
        batch = col.get(
            limit=BATCH_SIZE,
            offset=offset,
            include=["documents", "metadatas"],
        )
        ids = batch["ids"]
        documents = batch["documents"]
        metadatas = batch["metadatas"]

        if not ids:
            break

        doc_rows: list[tuple[str, str, str]] = []
        for doc_id, doc, meta in zip(ids, documents, metadatas):
            doc_text = doc or ""
            meta_json = json.dumps(meta or {})
            doc_rows.append((doc_id, doc_text, meta_json))

            tokens = tokenize(doc_text)
            freq_map = Counter(tokens)
            for term, freq in freq_map.items():
                all_term_rows.append((term, doc_id, freq))

        _upsert_docs_batch(conn, doc_rows)
        doc_count += len(ids)
        offset += BATCH_SIZE

        pct = int(100 * doc_count / total)
        bar_filled = pct * 40 // 100
        bar = "█" * bar_filled + "░" * (40 - bar_filled)
        elapsed = time.time() - t0
        rate = doc_count / max(elapsed, 0.001)
        eta = int((total - doc_count) / max(rate, 0.001))
        if pct >= 90:
            color = "\033[92m"
        elif pct >= 70:
            color = "\033[94m"
        elif pct >= 40:
            color = "\033[93m"
        else:
            color = "\033[91m"
        print(
            f"\r  {color}[{bar}] {pct:3d}% ({doc_count}/{total}) - ETA: {eta}s\033[0m",
            end="",
            flush=True,
        )

    print()

    print(f"  Writing {len(all_term_rows)} term-frequency rows ...")
    chunk_size = 5000
    for i in range(0, len(all_term_rows), chunk_size):
        _upsert_term_batch(conn, all_term_rows[i : i + chunk_size])

    print("  Rebuilding FTS5 index ...")
    _rebuild_fts(conn)

    conn.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)",
        ("collection", collection_name),
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)",
        ("doc_count", str(doc_count)),
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)",
        ("term_count", str(len(all_term_rows))),
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)",
        ("built_at", str(time.time())),
    )
    conn.commit()
    conn.close()

    elapsed = time.time() - t0
    unique_terms = len({r[0] for r in all_term_rows})
    print(
        f"  Done. docs={doc_count} term_rows={len(all_term_rows)} "
        f"unique_terms={unique_terms} elapsed={elapsed:.1f}s -> {db_path.name}"
    )
    return {"doc_count": doc_count, "term_count": unique_terms}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build SQLite FTS5 sparse index from canonical Chroma collections."
    )
    parser.add_argument(
        "--collection",
        choices=TARGET_COLLECTIONS,
        default=None,
        help="Build for a single collection (default: all 8 targets)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without writing any files",
    )
    args = parser.parse_args()

    targets = [args.collection] if args.collection else TARGET_COLLECTIONS
    print(f"Sparse index builder — targets: {targets}")
    if args.dry_run:
        print("DRY RUN mode — no files will be written.\n")

    total_start = time.time()
    for col in targets:
        print(f"\n[{col}]")
        build_for_collection(col, dry_run=args.dry_run)

    print(f"\nAll done in {time.time() - total_start:.1f}s")


if __name__ == "__main__":
    main()
