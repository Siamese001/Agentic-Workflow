"""W0 ADG probe for L2 best-practices gap plan. Read-only."""

import sqlite3, glob, os, sys

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
print(f"snapshot={db}")
con = sqlite3.connect(db)
cur = con.cursor()

targets = [
    "preventative_sandbox",
    "l2_agent_wrappers",
    "tool_intent_executor",
    "SovereignLLMGateway",
    "healing_router",
    "ptc_contract",
    "execution_tool_contract",
    "execution_guardrail_chokepoint",
    "boundary_verifier",
    "replay_guard",
    "l2_execution_contract",
    "ml_write_intent_types",
    "blast_radius_controls_types",
    "budget_enforcer",
    "SubAtomicRegistryAgent",
    "tool_chain_executor",
    "firecracker_manager",
    "sandbox_envelope_types",
]

print(f"\n{'file':<40} {'fan_in':>7} {'fan_out':>7}  resolved_path")
rows_out = []
for t in targets:
    cur.execute(
        "SELECT id, resolved_path FROM nodes WHERE resolved_path LIKE ? AND entity_type='module'",
        (f"%{t}.py",),
    )
    for nid, rp in cur.fetchall():
        cur.execute("SELECT COUNT(*) FROM edges WHERE dst_id=? AND relation_type=?", (nid, "imports"))
        fi = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM edges WHERE src_id=? AND relation_type=?", (nid, "imports"))
        fo = cur.fetchone()[0]
        rows_out.append((t, fi, fo, rp))
        print(f"{t:<40} {fi:>7} {fo:>7}  {rp}")

print("\nViolation counts (any severity):")
for t in targets:
    cur.execute(
        "SELECT severity, COUNT(*) FROM violations WHERE file_path LIKE ? GROUP BY severity", (f"%{t}.py",)
    )
    sev = dict(cur.fetchall())
    if sev:
        print(f"{t:<40} {sev}")

# Materialized views available
print("\nAvailable mv_/v_p views:")
cur.execute(
    "SELECT name FROM sqlite_master WHERE type IN ('view','table') AND (name LIKE 'mv_%' OR name LIKE 'v_p%') ORDER BY name"
)
for (n,) in cur.fetchall():
    print(" -", n)

con.close()
