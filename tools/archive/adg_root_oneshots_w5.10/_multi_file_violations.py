"""Check exact module-level import lines for multiple files."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

FILES = [
    "meta_apply.py",
    "meta_apply_ops.py",
    "ssot_adapters.py",
    "timeshift_router.py",
    "SubAtomicRegistryAgent.py",
    "decorators_util.py",
    "domain_constitution_config.py",
    "registry_config.py",
    "safety_agents.py",
    "constants_config.py",
    "non_conforming_agent_finder_config.py",
    "SovereignBaseAgent.py",
    "IBlackboardLeaseVerifierProtocol.py",
    "meta_learning.py",
    "meta_client.py",
    "case_library.py",
    "sovereign_rag_orchestrator.py",
    "tool_call_store.py",
    "LocationHealerAgent.py",
]

BAD_LAYERS = ("L1", "L2", "L3", "L4", "L5", "L6", "L_SL", "L_APP", "L_PG", "L_RUNTIME")

for fname in FILES:
    rows = list(
        conn.execute(
            """
        SELECT DISTINCT e.line_no, n2.layer as tgt_layer, n2.resolved_path as tgt_path
        FROM edges e
        JOIN nodes n1 ON e.src_id = n1.id
        JOIN nodes n2 ON e.dst_id = n2.id
        WHERE (n1.resolved_path LIKE ? OR n1.resolved_path LIKE ?)
        AND n2.layer IN ('L1','L2','L3','L4','L5','L6','L_SL','L_APP','L_PG','L_RUNTIME')
        AND e.relation_type = 'imports'
        ORDER BY e.line_no
    """,
            (f"%/{fname}", f"%\\{fname}"),
        ),
    )
    if rows:
        print(f"\n=== {fname} ===")
        for r in rows:
            print(f"  line {r['line_no']:5d}  {r['tgt_layer']:10s}  {r['tgt_path']}")

conn.close()
