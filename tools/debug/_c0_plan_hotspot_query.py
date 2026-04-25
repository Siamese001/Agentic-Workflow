"""One-shot hotspot query for plan c0-context-assembly-best-practices-b7c3a1.

Reads the ADG sqlite snapshot and emits markdown-ready hotspot evidence for
the C0 retrieval surface.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

SNAPSHOT = Path("artifacts/adg/adg_indexed_04232026_2319.sqlite")

# Files the plan's W1-W6 touch. Restricted to the retrieval surface.
PLAN_FILES = [
    "agentic_core/knowledge/retrieval/hybrid_recall_stage.py",
    "agentic_core/knowledge/retrieval/senior_librarian_reranker.py",
    "agentic_core/knowledge/retrieval/evidence_contract_builder.py",
    "agentic_core/knowledge/retrieval/parent_child_hydrator.py",
    "agentic_core/knowledge/retrieval/retrieval_plan.py",
    "agentic_core/knowledge/retrieval/dual_pass_citation_orchestrator.py",
    "agentic_core/knowledge/retrieval/anthropic_cache_control.py",
    "agentic_core/knowledge/retrieval/anthropic_prompt_renderer.py",
    "agentic_core/knowledge/retrieval/anthropic_citation_adapter.py",
    "agentic_core/knowledge/retrieval/corpus_size_gate.py",
    "agentic_core/knowledge/retrieval/prompt_envelope.py",
    "agentic_core/knowledge/chunking/chunk_policy_engine.py",
    "agentic_core/knowledge/chunking/chunking_modes.py",
    "agentic_core/knowledge/ingestion/intake_clerk.py",
    "agentic_core/knowledge/canonical/chunk_manifest.py",
    "agentic_core/L4_state/utils/memory/bm25_store.py",
    "agentic_core/L4_state/memory/semantic/bm25_scorer.py",
    "agentic_core/L4_state/memory/semantic/hybrid_merger.py",
    "agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py",
    "agentic_core/L3_orchestration/reasoning/engines/retrieval_benchmark.py",
    "agentic_core/L4_state/utils/retrieval/context_retrieval_orchestrator.py",
]


def all_tables(cur: sqlite3.Cursor) -> list[str]:
    cur.execute("SELECT name FROM sqlite_master WHERE type IN ('view','table') ORDER BY name")
    return [r[0] for r in cur.fetchall()]


def nodes_columns(cur: sqlite3.Cursor) -> list[str]:
    cur.execute("PRAGMA table_info(nodes)")
    return [r[1] for r in cur.fetchall()]


def edges_columns(cur: sqlite3.Cursor) -> list[str]:
    cur.execute("PRAGMA table_info(edges)")
    return [r[1] for r in cur.fetchall()]


def file_fanin(cur: sqlite3.Cursor, file_path: str) -> dict:
    """Fan-in to all module-scope nodes within a given file, imports only."""
    cur.execute(
        """
        WITH file_nodes AS (
            SELECT id FROM nodes WHERE resolved_path = ?
        )
        SELECT COUNT(DISTINCT e.src_id)
        FROM edges e
        WHERE e.dst_id IN (SELECT id FROM file_nodes)
          AND e.relation_type = 'imports'
        """,
        (file_path,),
    )
    row = cur.fetchone()
    import_fanin = row[0] if row else 0

    cur.execute(
        """
        WITH file_nodes AS (
            SELECT id FROM nodes WHERE resolved_path = ?
        )
        SELECT COUNT(DISTINCT e.src_id)
        FROM edges e
        WHERE e.dst_id IN (SELECT id FROM file_nodes)
          AND e.relation_type = 'calls'
        """,
        (file_path,),
    )
    row = cur.fetchone()
    call_fanin = row[0] if row else 0

    cur.execute(
        """
        WITH file_nodes AS (
            SELECT id FROM nodes WHERE resolved_path = ?
        )
        SELECT COUNT(DISTINCT e.dst_id)
        FROM edges e
        WHERE e.src_id IN (SELECT id FROM file_nodes)
          AND e.relation_type = 'imports'
        """,
        (file_path,),
    )
    row = cur.fetchone()
    import_fanout = row[0] if row else 0

    cur.execute("SELECT COUNT(*) FROM nodes WHERE resolved_path = ?", (file_path,))
    n = cur.fetchone()[0]

    cur.execute(
        "SELECT DISTINCT layer FROM nodes WHERE resolved_path = ? AND layer IS NOT NULL",
        (file_path,),
    )
    layers = sorted({r[0] for r in cur.fetchall()})

    return {
        "file": file_path,
        "nodes": n,
        "layer": ",".join(layers) if layers else "?",
        "import_fanin": import_fanin,
        "call_fanin": call_fanin,
        "import_fanout": import_fanout,
    }


def violations_for_file(cur: sqlite3.Cursor, file_path: str) -> dict:
    # violations table schema: (id, kind, severity, file_path, line, ...)
    cur.execute(
        "SELECT category, severity, COUNT(*) FROM violations WHERE file_path = ? GROUP BY category, severity",
        (file_path,),
    )
    rows = cur.fetchall()
    return {f"{k}/{s}": c for (k, s, c) in rows}


def pview_matches(cur: sqlite3.Cursor, pview: str, file_path: str) -> int:
    try:
        cur.execute(
            f"SELECT COUNT(*) FROM {pview} WHERE file_path = ?",
            (file_path,),
        )
        return cur.fetchone()[0]
    except sqlite3.Error:
        return -1


def mv_rows_for_file(cur: sqlite3.Cursor, mv: str, file_path: str) -> int:
    try:
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info({mv})").fetchall()]
        if "file_path" in cols:
            cur.execute(f"SELECT COUNT(*) FROM {mv} WHERE file_path = ?", (file_path,))
            return cur.fetchone()[0]
        return -1
    except sqlite3.Error:
        return -2


def main() -> int:
    if not SNAPSHOT.exists():
        print(f"[ERR] snapshot missing: {SNAPSHOT}")
        return 1

    con = sqlite3.connect(f"file:{SNAPSHOT.as_posix()}?mode=ro", uri=True)
    cur = con.cursor()

    tables = all_tables(cur)
    print("=" * 80)
    print(f"snapshot: {SNAPSHOT.name}")
    print(f"tables/views: {len(tables)}")

    mv_views = [t for t in tables if t.startswith("mv_")]
    p_views = [t for t in tables if t.startswith("v_p")]
    print(f"mv_*: {len(mv_views)}, v_p*: {len(p_views)}")
    print(f"nodes columns: {nodes_columns(cur)}")

    print("\n=== PLAN FILE FAN-IN / FAN-OUT ===")
    rows = []
    for fp in PLAN_FILES:
        rows.append(file_fanin(cur, fp))
    rows.sort(key=lambda r: -(r["import_fanin"] + r["call_fanin"]))
    print(f"{'file':<70} {'layer':<6} {'nodes':>6} {'imp_in':>7} {'call_in':>8} {'imp_out':>8}")
    for r in rows:
        print(
            f"{r['file']:<70} {r['layer']:<6} {r['nodes']:>6} "
            f"{r['import_fanin']:>7} {r['call_fanin']:>8} {r['import_fanout']:>8}"
        )

    print("\n=== VIOLATIONS BY FILE ===")
    for fp in PLAN_FILES:
        v = violations_for_file(cur, fp)
        if v:
            print(f"{fp}: {v}")

    print("\n=== P-VIEW MEMBERSHIP ===")
    for pview in p_views:
        hits = []
        for fp in PLAN_FILES:
            n = pview_matches(cur, pview, fp)
            if n > 0:
                hits.append((fp, n))
        if hits:
            print(f"\n{pview}:")
            for fp, n in hits:
                print(f"  {fp}: {n}")

    print("\n=== MATERIALIZED VIEW MEMBERSHIP (selected) ===")
    priority_mvs = [
        "mv_graph_reverse_dependency_hotspots",
        "mv_graph_chokepoint_bridges",
        "mv_graph_critical_path_blast_radius",
        "mv_hotspot_centrality",
        "mv_dependency_cone_risk",
        "mv_path_criticality_rollup",
        "mv_exemptions_near_critical_paths",
        "mv_debt_concentration_hotspots",
    ]
    for mv in priority_mvs:
        if mv not in mv_views:
            print(f"{mv}: [NOT PRESENT IN SNAPSHOT]")
            continue
        hits = []
        for fp in PLAN_FILES:
            n = mv_rows_for_file(cur, mv, fp)
            if n > 0:
                hits.append((fp, n))
        if hits:
            print(f"\n{mv}:")
            for fp, n in hits:
                print(f"  {fp}: {n}")
        else:
            print(f"{mv}: no rows for plan files")

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
