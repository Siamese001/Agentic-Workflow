# Probe: deeper Q6 fan-out diagnosis
import sqlite3

DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04252026_0521.sqlite"
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

# Check top fan_out values
print("=== Top 10 fan_out values in centrality ===")
for r in cur.execute(
    "SELECT fan_out, COUNT(*) FROM mv_hotspot_centrality WHERE fan_out>0 "
    "GROUP BY fan_out ORDER BY fan_out DESC LIMIT 10"
).fetchall():
    print(r)

# Check: for a known high-fan-out module, what callee layers exist via edges?
print("\n=== Edges FROM lifecycle_trace_contract.py symbols ===")
for r in cur.execute(
    "SELECT dst_n.layer, COUNT(*) as cnt "
    "FROM nodes sym "
    "JOIN edges e ON e.src_id = sym.id "
    "JOIN nodes dst_n ON dst_n.id = e.dst_id "
    "WHERE sym.resolved_path = 'agentic_core/runtime/contracts/lifecycle_trace_contract.py' "
    "AND sym.entity_type = 'symbol' "
    "AND e.relation_type IN ('imports','calls','references','flows_to','controls_flow',"
    "'writes_to','reads_from','invokes_provider','invokes_dynamic',"
    "'routes_through','retrieves_via','resolves_callsite',"
    "'emits_side_effect','applies','instantiates') "
    "GROUP BY dst_n.layer ORDER BY cnt DESC"
).fetchall():
    print(r)

# Also check module-level edges FROM that file
print("\n=== Module-level edges FROM lifecycle_trace_contract.py ===")
for r in cur.execute(
    "SELECT dst_n.layer, COUNT(*) as cnt "
    "FROM nodes mod "
    "JOIN edges e ON e.src_id = mod.id "
    "JOIN nodes dst_n ON dst_n.id = e.dst_id "
    "WHERE mod.resolved_path = 'agentic_core/runtime/contracts/lifecycle_trace_contract.py' "
    "AND mod.entity_type = 'module' "
    "AND e.relation_type IN ('imports','calls','references','flows_to','controls_flow',"
    "'writes_to','reads_from','invokes_provider','invokes_dynamic',"
    "'routes_through','retrieves_via','resolves_callsite',"
    "'emits_side_effect','applies','instantiates') "
    "GROUP BY dst_n.layer ORDER BY cnt DESC"
).fetchall():
    print(r)

con.close()
