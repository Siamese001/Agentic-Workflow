"""Validate sparse SQLite FTS5 indexes built by build_sparse_index.py.

Runs exact-match and sub-token probe queries against each sidecar DB
and confirms FTS5 + term_freq table are populated and queryable.

Usage
─────
  python tools/generate/ingestion/validate_sparse_index.py
  python tools/generate/ingestion/validate_sparse_index.py --collection symbols
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
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


def _parse_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


REPO_ROOT = _discover_repo_root(Path(__file__).resolve().parent)
SPARSE_PATH = REPO_ROOT / "data" / "cache" / "sparse"

TARGET_COLLECTIONS = [
    "code_chunks",
    "symbols",
    "arch_docs",
    "tests_guardrails",
    "runtime_evidence",
    "process_docs",
    "ext_knowledge",
    "incidents_rca",
]

# ---------------------------------------------------------------------------
# Exact-match probe queries per collection
# Each entry: (label, fts_query, expect_min_hits)
# ---------------------------------------------------------------------------

PROBES: dict[str, list[tuple[str, str, int]]] = {
    "code_chunks": [
        # compound identifier confirmed present in collection
        ("compound: _emit_records_execution_trace", "_emit_records_execution_trace", 1),
        # sub-token lookup (emitted alongside compound)
        ("sub-token: execution", "execution", 1),
        ("sub-token: orchestration", "orchestration", 1),
        # common type identifiers
        ("type: dict", "dict", 1),
        ("type: str", "str", 1),
        # common field names
        ("field: trace", "trace", 1),
        ("field: agent", "agent", 1),
        # path fragment
        ("path: agentic_core", "agentic_core", 1),
        # policy term
        ("policy: guardian", "guardian", 1),
        # class marker
        ("class: adg", "adg", 1),
    ],
    "symbols": [
        # exact symbol names — stored as compound tokens
        ("symbol: QueryRouter", "QueryRouter", 1),
        ("symbol: HybridSearchEngine", "HybridSearchEngine", 1),
        ("symbol: route_query", "route_query", 1),
        ("symbol: get_bm25_store", "get_bm25_store", 1),
        # layer designator
        ("layer: L3_ORCHESTRATION", "L3_ORCHESTRATION", 1),
        ("layer: L4_STATE", "L4_STATE", 1),
        # module path
        ("module: semantic_retriever", "semantic_retriever", 1),
        # relation type
        ("relation: calls", "calls", 1),
        # ADG prefix
        ("adg: ADG Symbol", "ADG", 1),
        # class suffix
        ("class: Bm25Store", "Bm25Store", 1),
    ],
    "arch_docs": [
        # policy/section names
        ("policy: constitutional", "constitutional", 1),
        ("policy: HITL enforcement", "hitl", 1),
        ("policy: plan location SSOT", "ssot", 1),
        # section marker
        ("section: Phase", "phase", 1),
        # layer designator
        ("layer: L0_routing", "L0_routing", 1),
        # doc-type keyword
        ("keyword: ADR", "adr", 1),
        # exact phrase fragment
        ("phrase: query_progress_bar", "query_progress_bar", 1),
        # file path fragment
        ("path: windsurf", "windsurf", 1),
        # process keyword
        ("keyword: rollback", "rollback", 1),
        # guardrail keyword
        ("keyword: anti_pattern", "anti_pattern", 1),
    ],
    "tests_guardrails": [
        # test function name — compound token
        ("fn sub-token: gateway", "gateway", 1),
        # enum/field lookup
        ("enum: GuardrailAction", "GuardrailAction", 1),
        ("enum: query_type", "query_type", 1),
        # policy keyword
        ("policy: assert", "assert", 1),
        # file path
        ("path: test_guardrails", "test_guardrails", 1),
        # marker
        ("marker: pytest", "pytest", 1),
        # class name sub-tokens (CamelCase splits to sub-tokens individually)
        ("class sub-token: governance", "governance", 1),
        # layer keyword
        ("keyword: L5_safety", "L5_safety", 1),
        # identifier
        ("id: canonical_digest", "canonical_digest", 1),
        # policy section
        ("policy: strict_mode", "strict_mode", 1),
    ],
}


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------


def fts5_search(conn: sqlite3.Connection, query: str, limit: int = 5) -> list[dict]:
    """Run FTS5 full-text search and return matching rows."""
    rows = conn.execute(
        "SELECT id, snippet(docs_fts, 1, '[', ']', '...', 8) AS snip "
        "FROM docs_fts WHERE docs_fts MATCH ? ORDER BY rank LIMIT ?",
        (query, limit),
    ).fetchall()
    return [{"id": r[0], "snippet": r[1]} for r in rows]


def term_freq_search(conn: sqlite3.Connection, term: str, limit: int = 5) -> list[dict]:
    """Exact term lookup in term_freq table."""
    rows = conn.execute(
        "SELECT doc_id, freq FROM term_freq WHERE term = ? ORDER BY freq DESC LIMIT ?",
        (term.lower(), limit),
    ).fetchall()
    return [{"doc_id": r[0], "freq": r[1]} for r in rows]


def check_meta(conn: sqlite3.Connection) -> dict[str, str]:
    rows = conn.execute("SELECT key, value FROM meta").fetchall()
    return {r[0]: r[1] for r in rows}


# ---------------------------------------------------------------------------
# Validation per collection
# ---------------------------------------------------------------------------


def validate_collection(collection_name: str, verbose: bool = False) -> bool:
    db_path = SPARSE_PATH / f"{collection_name}.db"
    print(f"\n=== VALIDATE SPARSE: {collection_name} @ {db_path.name} ===")

    if not db_path.exists():
        print(f"  [FAIL] Sidecar DB not found: {db_path}")
        return False

    try:
        with sqlite3.connect(str(db_path)) as conn:
            # 1. Meta check
            meta = check_meta(conn)
            doc_count = _parse_int(meta.get("doc_count"), 0)
            term_count = _parse_int(meta.get("term_count"), 0)
            print(f"  [OK]   Meta: doc_count={doc_count} term_rows={term_count}")

            if doc_count == 0:
                print("  [FAIL] doc_count=0 — index is empty")
                return False

            # 2. FTS5 table exists
            fts_tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='docs_fts'"
            ).fetchall()
            if not fts_tables:
                print("  [FAIL] docs_fts virtual table missing")
                return False
            print("  [OK]   FTS5 table present")

            # 3. term_freq populated
            tf_count = _parse_int(conn.execute("SELECT COUNT(*) FROM term_freq").fetchone()[0], 0)
            if tf_count == 0:
                print("  [FAIL] term_freq table is empty")
                return False
            print(f"  [OK]   term_freq rows={tf_count}")

            # 4. Probe queries
            probes = PROBES.get(collection_name, [])
            passed = 0
            failed = 0
            for label, fts_query, expect_min in tqdm(probes, desc="Processing", unit="item"):
                hits = fts5_search(conn, fts_query, limit=3)
                ok = len(hits) >= expect_min
                status = "[OK]  " if ok else "[FAIL]"
                if ok:
                    passed += 1
                else:
                    failed += 1
                snip = hits[0]["snippet"][:80].replace("\n", " ") if hits else "—no results—"
                print(f"  {status} {label}: {len(hits)} hit(s) | {snip!r}")
                if verbose and hits:
                    for h in hits[:2]:
                        print(f"         id={h['id'][:60]}")
    except sqlite3.Error as exc:
        print(f"  [FAIL] SQLite validation error: {exc}")
        return False

    total_probes = passed + failed
    print(f"\n  Probes: {passed}/{total_probes} passed")
    result = failed == 0
    print(f"  Result: {'PASS' if result else 'FAIL'} — {collection_name}")
    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate SQLite FTS5 sparse indexes for canonical collections."
    )
    parser.add_argument(
        "--collection",
        choices=TARGET_COLLECTIONS,
        default=None,
        help="Validate a single collection (default: all 4 targets)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show matching doc IDs for each probe",
    )
    args = parser.parse_args()

    targets = [args.collection] if args.collection else TARGET_COLLECTIONS
    results: dict[str, bool] = {}

    for col in targets:
        results[col] = validate_collection(col, verbose=args.verbose)

    print("\n" + "=" * 60)
    all_pass = all(results.values())
    for col, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {col}")
    print("=" * 60)
    print(f"  Overall: {'ALL PASS' if all_pass else 'SOME FAILED'}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
