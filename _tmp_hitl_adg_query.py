import sqlite3

db = r'C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03152026_0344.sqlite'
con = sqlite3.connect(db)
cur = con.cursor()

# Schema inspection
for tname in ['nodes', 'edges']:
    cur.execute(f"PRAGMA table_info({tname})")
    cols = [c[1] for c in cur.fetchall()]
    print(f"{tname} cols: {cols}")

print()

# nodes.adg_name format: "path::Symbol" or just symbol
# edges has: src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol
# Let's find canonical symbols via edges (already confirmed to work)

symbols_of_interest = [
    'log_hitl_decision', 'HumanDecisionArtifact', 'DPOExampleId', 'DPOPair',
    'DPOPairGenerator', 'DefaultDeterministicDPOPairGenerator', 'RLHFOptimizer',
    'HITLDecisionLogger', 'propose_from_dpo', 'dpo_batch_bytes',
]

cur.execute("PRAGMA table_info(edges)")
ecols = [c[1] for c in cur.fetchall()]

print("=== Symbol lookup via edges (export edges only) ===")
for sym in symbols_of_interest:
    cur.execute(
        "SELECT source_file, line_no, relation_type FROM edges WHERE symbol=? AND relation_type='exports' LIMIT 3",
        (sym,)
    )
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"  [FOUND] {sym}: {r[0]}:{r[1]} ({r[2]})")
    else:
        # fallback: any relation
        cur.execute("SELECT source_file, line_no, relation_type FROM edges WHERE symbol=? LIMIT 3", (sym,))
        rows = cur.fetchall()
        if rows:
            for r in rows:
                print(f"  [FOUND non-export] {sym}: {r[0]}:{r[1]} ({r[2]})")
        else:
            print(f"  [MISSING] {sym}")

# Check nodes for partial matches on missing ones
print()
print("=== Partial adg_name search for missing symbols ===")
for partial in ['propose_from_dpo', 'dpo_batch_bytes', 'original_plan_hash', 'structured_patch', 'HumanDecisionArtifact']:
    cur.execute("SELECT adg_name, entity_type, layer, resolved_path FROM nodes WHERE adg_name LIKE ?", (f'%{partial}%',))
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"  [NODE MATCH '{partial}'] adg_name={r[0]} type={r[1]} layer={r[2]} path={r[3]}")
    else:
        print(f"  [NO NODE MATCH] {partial}")

# Also search edges source_file for hitl/dpo files to get all their exports
print()
print("=== All exports from HITL/DPO/RLHF source files ===")
hitl_files = [
    'agentic_core/L5_safety/hitl/decision_logger.py',
    'agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py',
    'agentic_core/L6_observability/types/dpo_types.py',
    'system_learning/engines/rlhf_optimizer.py',
    'system_learning/pipelines/meta_learning_pipeline.py',
]
for f in hitl_files:
    cur.execute(
        "SELECT symbol, line_no, relation_type FROM edges WHERE source_file=? AND relation_type='exports' ORDER BY line_no",
        (f,)
    )
    rows = cur.fetchall()
    print(f"\n  {f}:")
    for r in rows:
        print(f"    line {r[1]}: {r[0]}")

con.close()
