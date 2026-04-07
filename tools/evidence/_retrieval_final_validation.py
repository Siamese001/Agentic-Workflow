"""
Final ADG retrieval wiring validation using correct schema:
- nodes.resolved_path contains the file path (e.g. agentic_core/L1_cognition/...)
- edges.source_file contains the file path of the edge source
- edges.src_id / dst_id are integer FKs to nodes.id (integer PK)
"""
import os
import sqlite3

SQLITE_PATH = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03312026_1808.sqlite"

RETRIEVAL_RELATIONS = [
    "pulls_context", "reads_from", "writes_to", "reads_through", "writes_through",
    "validated_by_safety_plane", "calls", "routes_through", "emits_metric_event",
    "execution_terminates_at_uwg",
]

AGENTIC_CORE_LAYERS = [
    "L0_routing", "L1_cognition", "L2_execution",
    "L3_orchestration", "L4_state", "L5_safety", "L6_observability",
]

APPS_PACKAGES = [
    "apps_lic", "apps_rg", "apps_eval", "apps_exec",
    "apps_research", "apps_rfp", "apps_shared", "apps_underwriting_ai",
]

# v18 spec retrieval symbols — exact module/class names to look for in resolved_path
RETRIEVAL_SYMBOL_PATTERNS = [
    # L1 — query embedding & intent expansion
    "query_intent_expansion", "graphrag_config", "react_config",
    # L2 — chunking / enrichment / conservation lab
    "chunk", "enrich", "ingestion", "document_load",
    "brief_assembly", "source_ingestion",
    # L3 — context assembly / orchestration / GraphRAG
    "context", "orchestrat", "retrieval", "graph_rag", "graphrag",
    # L4 — canonical store / vector / state
    "vector", "faiss", "chroma", "l4d", "l4e", "manifest",
    "semantic_cache", "parent_child",
    # L5 — safety / guardrail on retrieval
    "adaptive_retrieval", "retrieval_gate", "guardrail",
    # L6 — observability
    "rag_evaluator", "evaluation_cache", "retrieval_eval",
]


def run():
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()

    print("=" * 70)
    print("ADG RETRIEVAL WIRING VALIDATION (v18 spec)")
    print(f"SQLite: {os.path.basename(SQLITE_PATH)}")
    print("=" * 70)

    cur.execute("SELECT COUNT(*) FROM nodes")
    node_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM edges")
    edge_count = cur.fetchone()[0]
    print(f"\n[GRAPH] Nodes={node_count:,}  Edges={edge_count:,}\n")

    # ----------------------------------------------------------------
    # 1. Global retrieval relation counts
    # ----------------------------------------------------------------
    print("[1] RETRIEVAL RELATION GLOBAL COUNTS")
    rel_counts = {}
    for rel in RETRIEVAL_RELATIONS:
        cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
        count = cur.fetchone()[0]
        rel_counts[rel] = count
        print(f"  {'OK  ' if count else 'MISS'} {rel}: {count:,}")

    # ----------------------------------------------------------------
    # 2. Per agentic_core layer — edges where source_file contains layer
    # ----------------------------------------------------------------
    print("\n[2] AGENTIC_CORE LAYER COVERAGE (any retrieval relation, source_file match)")
    layer_gaps = []
    layer_detail = {}
    for layer in AGENTIC_CORE_LAYERS:
        pat = f"%/{layer}/%"
        placeholders = ",".join("?" * len(RETRIEVAL_RELATIONS))
        cur.execute(
            f"SELECT relation_type, COUNT(*) FROM edges "
            f"WHERE source_file LIKE ? AND relation_type IN ({placeholders}) "
            f"GROUP BY relation_type",
            [pat] + RETRIEVAL_RELATIONS,
        )
        rows = dict(cur.fetchall())
        total = sum(rows.values())
        layer_detail[layer] = rows
        if total == 0:
            layer_gaps.append(layer)
        print(f"  {'OK  ' if total else 'GAP '} {layer}: {total:,}  {rows}")

    # ----------------------------------------------------------------
    # 3. apps_* coverage
    # ----------------------------------------------------------------
    print("\n[3] APPS_* COVERAGE (any retrieval relation, source_file match)")
    apps_gaps = []
    for app in APPS_PACKAGES:
        pat = f"%{app}/%"
        placeholders = ",".join("?" * len(RETRIEVAL_RELATIONS))
        cur.execute(
            f"SELECT relation_type, COUNT(*) FROM edges "
            f"WHERE source_file LIKE ? AND relation_type IN ({placeholders}) "
            f"GROUP BY relation_type",
            [pat] + RETRIEVAL_RELATIONS,
        )
        rows = dict(cur.fetchall())
        total = sum(rows.values())
        if total == 0:
            apps_gaps.append(app)
        print(f"  {'OK  ' if total else 'GAP '} {app}: {total:,}  {rows}")

    # ----------------------------------------------------------------
    # 4. Retrieval symbol nodes (resolved_path contains keyword)
    # ----------------------------------------------------------------
    print("\n[4] RETRIEVAL SYMBOL PRESENCE (resolved_path)")
    present = {}
    absent = []
    for kw in RETRIEVAL_SYMBOL_PATTERNS:
        cur.execute(
            "SELECT COUNT(*) FROM nodes WHERE resolved_path LIKE ?",
            (f"%{kw}%",),
        )
        count = cur.fetchone()[0]
        if count > 0:
            present[kw] = count
        else:
            absent.append(kw)
    for kw, cnt in present.items():
        print(f"  PRESENT  {kw}: {cnt:,} nodes")
    if absent:
        print("\n  ABSENT (0 nodes in ADG):")
        for kw in absent:
            print(f"    - {kw}")

    # ----------------------------------------------------------------
    # 5. Cross-layer retrieval edges (source_file x target resolved_path)
    # ----------------------------------------------------------------
    print("\n[5] CROSS-LAYER RETRIEVAL EDGES (source_file -> dst node resolved_path)")
    cross_pairs = [
        ("L1_cognition", "L4_state"),
        ("L2_execution", "L4_state"),
        ("L3_orchestration", "L4_state"),
        ("L3_orchestration", "L2_execution"),
        ("L5_safety", "L3_orchestration"),
        ("L0_routing", "L1_cognition"),
        ("L6_observability", "L4_state"),
        ("apps_shared", "L2_execution"),
        ("apps_lic", "L2_execution"),
    ]
    placeholders = ",".join("?" * len(RETRIEVAL_RELATIONS))
    for src_pat, dst_pat in cross_pairs:
        cur.execute(
            f"""SELECT COUNT(*) FROM edges e
               JOIN nodes n_dst ON e.dst_id = n_dst.id
               WHERE e.source_file LIKE ?
                 AND n_dst.resolved_path LIKE ?
                 AND e.relation_type IN ({placeholders})""",
            [f"%{src_pat}%", f"%{dst_pat}%"] + RETRIEVAL_RELATIONS,
        )
        fwd = cur.fetchone()[0]
        cur.execute(
            f"""SELECT COUNT(*) FROM edges e
               JOIN nodes n_dst ON e.dst_id = n_dst.id
               WHERE e.source_file LIKE ?
                 AND n_dst.resolved_path LIKE ?
                 AND e.relation_type IN ({placeholders})""",
            [f"%{dst_pat}%", f"%{src_pat}%"] + RETRIEVAL_RELATIONS,
        )
        rev = cur.fetchone()[0]
        total = fwd + rev
        print(f"  {'OK  ' if total else 'GAP '} {src_pat} <-> {dst_pat}: fwd={fwd} rev={rev}")

    # ----------------------------------------------------------------
    # 6. apps_* <-> retrieval layers L1-L5 detailed
    # ----------------------------------------------------------------
    print("\n[6] APPS_* <-> L1-L5 WIRING (calls/reads_from via source_file x resolved_path)")
    for app in APPS_PACKAGES:
        row_gaps = []
        row_ok = []
        for layer in ["L1_cognition", "L2_execution", "L3_orchestration", "L4_state", "L5_safety"]:
            cur.execute(
                """SELECT COUNT(*) FROM edges e
                   JOIN nodes n_dst ON e.dst_id = n_dst.id
                   WHERE (e.source_file LIKE ? AND n_dst.resolved_path LIKE ?)
                      OR (e.source_file LIKE ? AND n_dst.resolved_path LIKE ?)""",
                [f"%{app}%", f"%{layer}%", f"%{layer}%", f"%{app}%"],
            )
            count = cur.fetchone()[0]
            if count == 0:
                row_gaps.append(layer)
            else:
                row_ok.append(f"{layer}:{count}")
        if row_gaps:
            print(f"  GAP  {app}  missing: {row_gaps}  wired: {row_ok}")
        else:
            print(f"  OK   {app}  {row_ok}")

    # ----------------------------------------------------------------
    # 7. Summary gap register
    # ----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUMMARY — GAP REGISTER")
    print("=" * 70)
    missing_rels = [r for r, c in rel_counts.items() if c == 0]
    print(f"  GAP-1 Missing relation types:     {missing_rels or 'NONE'}")
    print(f"  GAP-2 agentic_core layer gaps:    {layer_gaps or 'NONE'}")
    print(f"  GAP-3 apps_* source gaps:         {apps_gaps or 'NONE'}")
    print(f"  GAP-4 Absent retrieval symbols:   {absent or 'NONE'}")

    conn.close()


if __name__ == "__main__":
    run()
