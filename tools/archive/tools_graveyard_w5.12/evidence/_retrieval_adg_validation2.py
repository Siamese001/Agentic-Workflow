"""
ADG retrieval wiring validation — uses actual schema:
  nodes(id, adg_name, entity_type, layer, resolved_path, ...)
  edges(id, src_id, dst_id, relation_type, source_file, ...)
"""

import os
import sqlite3

SQLITE_PATH = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03312026_1808.sqlite"

RETRIEVAL_RELATIONS = [
    "pulls_context",
    "reads_from",
    "writes_to",
    "reads_through",
    "writes_through",
    "validated_by_safety_plane",
    "calls",
    "routes_through",
    "emits_metric_event",
    "execution_terminates_at_uwg",
]

AGENTIC_CORE_LAYERS = [
    "L0_routing",
    "L1_cognition",
    "L2_execution",
    "L3_orchestration",
    "L4_state",
    "L5_safety",
    "L6_observability",
]

APPS_PACKAGES = [
    "apps_lic",
    "apps_rg",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_rfp",
    "apps_shared",
    "apps_underwriting_ai",
]

RETRIEVAL_KEYWORDS = [
    "retrieval",
    "chunk",
    "embed",
    "vector",
    "faiss",
    "chroma",
    "rag",
    "graphrag",
    "context_assembl",
    "query_intent",
    "semantic_cache",
    "ingestion",
    "enrich",
    "parent_child",
    "adaptive_retrieval",
]


def run():
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()

    print("=" * 70)
    print("ADG RETRIEVAL WIRING VALIDATION")
    print(f"SQLite: {os.path.basename(SQLITE_PATH)}")
    print("=" * 70)

    cur.execute("SELECT COUNT(*) FROM nodes")
    node_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM edges")
    edge_count = cur.fetchone()[0]
    print(f"\n[GRAPH] Nodes={node_count:,}  Edges={edge_count:,}")

    # 1. Retrieval relation counts (global)
    print("\n[1] RETRIEVAL RELATION GLOBAL COUNTS")
    rel_counts = {}
    for rel in RETRIEVAL_RELATIONS:
        cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
        count = cur.fetchone()[0]
        rel_counts[rel] = count
        status = "OK  " if count > 0 else "MISS"
        print(f"  [{status}] {rel}: {count:,}")

    # 2. Per agentic_core layer — edges where source_file contains layer name
    print("\n[2] AGENTIC_CORE LAYER COVERAGE (source_file match)")
    layer_gaps = []
    for layer in AGENTIC_CORE_LAYERS:
        pat = f"%{layer}%"
        cur.execute(
            """
            SELECT relation_type, COUNT(*) FROM edges
            WHERE source_file LIKE ?
              AND relation_type IN ({})
            GROUP BY relation_type
        """.format(",".join("?" * len(RETRIEVAL_RELATIONS))),
            [pat] + RETRIEVAL_RELATIONS,
        )
        rows = cur.fetchall()
        total = sum(r[1] for r in rows)
        status = "OK  " if total > 0 else "GAP "
        if total == 0:
            layer_gaps.append(layer)
        print(f"  [{status}] {layer}: {total:,} edges  {dict(rows) if rows else ''}")

    # 3. apps_* coverage via source_file
    print("\n[3] APPS_* COVERAGE (source_file match)")
    apps_gaps = []
    for app in APPS_PACKAGES:
        pat = f"%{app}%"
        cur.execute(
            """
            SELECT relation_type, COUNT(*) FROM edges
            WHERE source_file LIKE ?
              AND relation_type IN ({})
            GROUP BY relation_type
        """.format(",".join("?" * len(RETRIEVAL_RELATIONS))),
            [pat] + RETRIEVAL_RELATIONS,
        )
        rows = cur.fetchall()
        total = sum(r[1] for r in rows)
        status = "OK  " if total > 0 else "GAP "
        if total == 0:
            apps_gaps.append(app)
        print(f"  [{status}] {app}: {total:,} edges")

    # 4. Retrieval keyword presence in node ids
    print("\n[4] RETRIEVAL SYMBOL NODES")
    present = []
    absent = []
    for kw in RETRIEVAL_KEYWORDS:
        cur.execute("SELECT COUNT(*) FROM nodes WHERE id LIKE ?", (f"%{kw}%",))
        count = cur.fetchone()[0]
        if count > 0:
            present.append((kw, count))
        else:
            absent.append(kw)
    for kw, cnt in present:
        print(f"  [PRESENT] {kw}: {cnt:,} nodes")
    if absent:
        print(f"  [ABSENT]  {absent}")

    # 5. Cross-layer retrieval edges
    print("\n[5] CROSS-LAYER RETRIEVAL EDGES (source_file x target via node join)")
    cross_pairs = [
        ("L1_cognition", "L4_state"),
        ("L2_execution", "L4_state"),
        ("L3_orchestration", "L4_state"),
        ("L3_orchestration", "L2_execution"),
        ("L5_safety", "L3_orchestration"),
        ("L0_routing", "L1_cognition"),
        ("L6_observability", "L4_state"),
    ]
    for src_l, tgt_l in cross_pairs:
        cur.execute(
            """
            SELECT COUNT(*) FROM edges e
            JOIN nodes n_src ON e.src_id = n_src.id
            JOIN nodes n_dst ON e.dst_id = n_dst.id
            WHERE (n_src.id LIKE ? AND n_dst.id LIKE ?)
               OR (n_src.id LIKE ? AND n_dst.id LIKE ?)
        """,
            (f"%{src_l}%", f"%{tgt_l}%", f"%{tgt_l}%", f"%{src_l}%"),
        )
        count = cur.fetchone()[0]
        status = "OK  " if count > 0 else "GAP "
        print(f"  [{status}] {src_l} <-> {tgt_l}: {count:,}")

    # 6. apps_* <-> retrieval layers (L1-L5)
    print("\n[6] APPS_* <-> RETRIEVAL LAYERS L1-L5 WIRING")
    for app in APPS_PACKAGES:
        app_gaps = []
        for layer in ["L1_cognition", "L2_execution", "L3_orchestration", "L4_state", "L5_safety"]:
            cur.execute(
                """
                SELECT COUNT(*) FROM edges
                WHERE source_file LIKE ?
            """,
                (f"%{app}%",),
            )
            # Use source_file for app side, node id for layer side
            cur.execute(
                """
                SELECT COUNT(*) FROM edges e
                JOIN nodes n_src ON e.src_id = n_src.id
                JOIN nodes n_dst ON e.dst_id = n_dst.id
                WHERE (e.source_file LIKE ? AND (n_src.id LIKE ? OR n_dst.id LIKE ?))
                   OR (e.source_file LIKE ? AND (n_src.id LIKE ? OR n_dst.id LIKE ?))
            """,
                (
                    f"%{app}%",
                    f"%{layer}%",
                    f"%{layer}%",
                    f"%{layer}%",
                    f"%{app}%",
                    f"%{app}%",
                ),
            )
            count = cur.fetchone()[0]
            if count == 0:
                app_gaps.append(layer)
        if app_gaps:
            print(f"  [GAP ] {app} missing wiring to: {app_gaps}")
        else:
            print(f"  [OK  ] {app} wired to all L1-L5 retrieval layers")

    # 7. Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    missing_rels = [r for r, c in rel_counts.items() if c == 0]
    print(f"  Relation types MISSING:     {missing_rels if missing_rels else 'NONE'}")
    print(f"  agentic_core layer GAPS:    {layer_gaps if layer_gaps else 'NONE'}")
    print(f"  apps_* GAPS:                {apps_gaps if apps_gaps else 'NONE'}")
    print(f"  Absent retrieval symbols:   {absent if absent else 'NONE'}")
    print()

    conn.close()


if __name__ == "__main__":
    run()
