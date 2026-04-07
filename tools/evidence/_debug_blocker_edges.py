"""Debug: dump all edges for specific blocker modules from the latest ADG."""
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.path.join(ROOT, "artifacts", "adg", "adg_indexed_03162026_2358.sqlite")

conn = sqlite3.connect(db_path)
c = conn.cursor()

MODULES = [
    "agentic_core/L0_routing/enforcement/traceability_contracts.py",
    "agentic_core/L0_routing/enforcement/trace_id_generator.py",
]

for module in MODULES:
    print(f"\n{'='*70}")
    print(f"MODULE: {module}")
    print(f"{'='*70}")

    # Check by source_file
    rows = c.execute(
        "SELECT relation_type, edge_kind, symbol, line_no FROM edges WHERE source_file = ? ORDER BY relation_type",
        (module,),
    ).fetchall()
    print(f"  Edges by source_file: {len(rows)}")
    for r in rows[:30]:
        print(f"    {r[0]:40s} {r[1]:30s} {r[2][:40]:40s} L{r[3]}")
    if len(rows) > 30:
        print(f"    ... {len(rows) - 30} more")

    # Also check by from_name matching the module
    # The from_name uses ADG naming like Module::agentic_core/...
    rows2 = c.execute(
        "SELECT e.relation_type, e.source_file, e.symbol FROM edges e "
        "JOIN nodes n ON e.src_id = n.id "
        "WHERE n.resolved_path LIKE ? ORDER BY e.relation_type",
        (f"%{module}%",),
    ).fetchall()
    print(f"\n  Edges by resolved_path match: {len(rows2)}")
    # Check if emits_determinism_digest or records_execution_trace present
    rels = set(r[0] for r in rows2)
    print(f"  Relation types: {sorted(rels)}")
    has_digest = "emits_determinism_digest" in rels
    has_trace = "records_execution_trace" in rels
    print(f"  emits_determinism_digest: {'YES' if has_digest else 'NO'}")
    print(f"  records_execution_trace: {'YES' if has_trace else 'NO'}")

conn.close()
