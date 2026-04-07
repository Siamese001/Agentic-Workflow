"""
ADG validation script: prove retrieval layers (L1-L5 per Agentic Retrieval Models v18)
are wired across agentic_core (L0-L6) and all apps_*.

Retrieval Layer Definitions from v18 spec:
  L1 = Query Embedding & Intent Expansion (L1_cognition)
  L2 = Semantic Enrichment / Chunking / Conservation Lab (L2_execution)
  L3 = Context Assembly & Orchestration (L3_orchestration)
  L4 = Canonical Store / ChunkManifest / ParentChildIndex / Vector DB (L4_state)
  L5 = Safety / Guardrail / Policy enforcement on retrieval (L5_safety)

Each retrieval layer maps to relation types in the ADG. We query:
  - pulls_context        -> L1/L3 context pull
  - reads_from           -> L4 canonical store reads
  - writes_to            -> L4/L2 write path
  - reads_through        -> L3 governance read path
  - validated_by_safety_plane -> L5 guardrail
  - calls                -> cross-layer call wiring
  - routes_through       -> L3 orchestration routing
  - emits_metric_event   -> L6 observability
"""

import os
import sqlite3
import sys

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

AGENTIC_CORE_LAYERS = ["L0_routing", "L1_cognition", "L2_execution",
                        "L3_orchestration", "L4_state", "L5_safety", "L6_observability"]

APPS_PACKAGES = ["apps_lic", "apps_rg", "apps_eval", "apps_exec",
                 "apps_research", "apps_rfp", "apps_shared", "apps_underwriting_ai"]

# Retrieval-specific symbol patterns from v18 spec
RETRIEVAL_SYMBOLS = [
    # L1 - query embedding / intent expansion
    "query_intent_expansion", "QueryIntentExpansion", "embed", "intent",
    # L2 - chunking / enrichment / conservation
    "chunk", "Chunk", "enrich", "Enrich", "semantic_enrichment", "ChunkManifest",
    "conservation", "ingestion", "DocumentLoader",
    # L3 - context assembly / orchestration
    "context_assembl", "ContextAssembl", "retrieval_orchestrat", "RetrievalOrchestrat",
    "GraphRAG", "graphrag", "graph_rag",
    # L4 - canonical store / vector / state
    "vector", "Vector", "faiss", "chroma", "ParentChildIndex", "chunk_manifest",
    "retrieval_cache", "RetrievalCache", "semantic_cache", "SemanticCache",
    # L5 - safety / guardrail on retrieval
    "retrieval_guard", "RetrievalGate", "AdaptiveRetrievalGate",
    "retrieval_gate", "adaptive_retrieval",
]


def run():
    if not os.path.exists(SQLITE_PATH):
        print(f"[ERROR] SQLite not found: {SQLITE_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()

    results = {}

    print("=" * 70)
    print("ADG RETRIEVAL WIRING VALIDATION")
    print(f"SQLite: {os.path.basename(SQLITE_PATH)}")
    print("=" * 70)

    # 1. Total graph size
    cur.execute("SELECT COUNT(*) FROM nodes")
    node_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM edges")
    edge_count = cur.fetchone()[0]
    print(f"\n[GRAPH] Nodes={node_count:,}  Edges={edge_count:,}")

    # 2. Retrieval relation coverage
    print("\n[RETRIEVAL RELATIONS]")
    for rel in RETRIEVAL_RELATIONS:
        cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
        count = cur.fetchone()[0]
        status = "OK" if count > 0 else "MISSING"
        print(f"  [{status}] {rel}: {count:,}")
        results[rel] = count

    # 3. Per-layer retrieval edge counts (source module contains layer name)
    print("\n[AGENTIC_CORE LAYER COVERAGE - retrieval relations]")
    layer_coverage = {}
    for layer in AGENTIC_CORE_LAYERS:
        cur.execute("""
            SELECT relation_type, COUNT(*) as cnt
            FROM edges
            WHERE (source LIKE ? OR target LIKE ?)
              AND relation_type IN ({})
            GROUP BY relation_type
        """.format(",".join("?" * len(RETRIEVAL_RELATIONS))),
        [f"%{layer}%", f"%{layer}%"] + RETRIEVAL_RELATIONS)
        rows = cur.fetchall()
        total = sum(r[1] for r in rows)
        layer_coverage[layer] = {"total": total, "by_rel": {r[0]: r[1] for r in rows}}
        status = "OK" if total > 0 else "GAP"
        print(f"  [{status}] {layer}: {total:,} retrieval edges")
        for rel, cnt in sorted(layer_coverage[layer]["by_rel"].items()):
            print(f"           {rel}: {cnt}")

    # 4. apps_* coverage
    print("\n[APPS_* COVERAGE - retrieval relations]")
    apps_coverage = {}
    for app in APPS_PACKAGES:
        cur.execute("""
            SELECT relation_type, COUNT(*) as cnt
            FROM edges
            WHERE (source LIKE ? OR target LIKE ?)
              AND relation_type IN ({})
            GROUP BY relation_type
        """.format(",".join("?" * len(RETRIEVAL_RELATIONS))),
        [f"%{app}%", f"%{app}%"] + RETRIEVAL_RELATIONS)
        rows = cur.fetchall()
        total = sum(r[1] for r in rows)
        apps_coverage[app] = {"total": total, "by_rel": {r[0]: r[1] for r in rows}}
        status = "OK" if total > 0 else "GAP"
        print(f"  [{status}] {app}: {total:,} retrieval edges")

    # 5. Retrieval-specific symbol presence (nodes)
    print("\n[RETRIEVAL SYMBOL PRESENCE IN ADG NODES]")
    symbol_hits = {}
    for sym in RETRIEVAL_SYMBOLS:
        cur.execute("SELECT COUNT(*) FROM nodes WHERE id LIKE ?", (f"%{sym}%",))
        count = cur.fetchone()[0]
        if count > 0:
            symbol_hits[sym] = count
            print(f"  [PRESENT] {sym}: {count} nodes")
    missing_syms = [s for s in RETRIEVAL_SYMBOLS if s not in symbol_hits]
    if missing_syms:
        print("\n  [ABSENT] symbols with ZERO nodes in ADG:")
        for s in missing_syms:
            print(f"    - {s}")

    # 6. Cross-layer retrieval edges (L1->L4, L2->L4, L3->L4, etc.)
    print("\n[CROSS-LAYER RETRIEVAL EDGES]")
    cross_pairs = [
        ("L1_cognition", "L4_state"),
        ("L2_execution", "L4_state"),
        ("L3_orchestration", "L4_state"),
        ("L3_orchestration", "L2_execution"),
        ("L5_safety", "L3_orchestration"),
        ("L0_routing", "L1_cognition"),
        ("L6_observability", "L4_state"),
    ]
    for src_layer, tgt_layer in cross_pairs:
        cur.execute("""
            SELECT COUNT(*) FROM edges
            WHERE source LIKE ? AND target LIKE ?
        """, (f"%{src_layer}%", f"%{tgt_layer}%"))
        fwd = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(*) FROM edges
            WHERE source LIKE ? AND target LIKE ?
        """, (f"%{tgt_layer}%", f"%{src_layer}%"))
        rev = cur.fetchone()[0]
        status = "OK" if (fwd + rev) > 0 else "GAP"
        print(f"  [{status}] {src_layer} <-> {tgt_layer}: {fwd} fwd / {rev} rev")

    # 7. apps_* -> agentic_core retrieval wiring
    print("\n[APPS_* -> AGENTIC_CORE RETRIEVAL WIRING]")
    for app in APPS_PACKAGES:
        for layer in ["L1_cognition", "L2_execution", "L3_orchestration", "L4_state", "L5_safety"]:
            cur.execute("""
                SELECT COUNT(*) FROM edges
                WHERE (source LIKE ? AND target LIKE ?)
                   OR (source LIKE ? AND target LIKE ?)
            """, (f"%{app}%", f"%{layer}%", f"%{layer}%", f"%{app}%"))
            count = cur.fetchone()[0]
            if count == 0:
                print(f"  [GAP]  {app} <-> {layer}: 0 edges")
            else:
                print(f"  [OK]   {app} <-> {layer}: {count}")

    conn.close()
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run()
