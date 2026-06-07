"""Inspect R6 detection quality."""

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3

con = sqlite3.connect("artifacts/adg/adg_r6_test.sqlite")
con.row_factory = sqlite3.Row

print("=== A13 async_fire_and_forget ===")
for r in con.execute("SELECT * FROM async_fire_and_forget LIMIT 10"):
    print(f"  {r['file_path']}:L{r['line_no']}  {r['callee']}()")

print("\n=== A16 boundary_string_unresolved (sample) ===")
for r in con.execute("SELECT file_path, line_no, target FROM boundary_strings WHERE resolved=0 LIMIT 12"):
    print(f"  {r['file_path']}:L{r['line_no']}  -> {r['target']}")

print("\n=== A19 mcp_contract_drift ===")
for r in con.execute("SELECT drift_kind, server_or_tool, note FROM mv_mcp_contract_drift LIMIT 20"):
    print(f"  [{r['drift_kind']}] {r['server_or_tool']}")
    print(f"     {r['note']}")

print("\n=== A17 rename_shim_consumer_risk (all shims fan-in) ===")
for r in con.execute("SELECT * FROM mv_rename_shim_consumers"):
    print(f"  fanin={r['import_fanin']:3d}  {r['shim_file']}")

print("\n=== A18 module_origins (non-handwritten) ===")
for r in con.execute(
    "SELECT origin, COUNT(*) c FROM module_origins WHERE origin != 'handwritten' GROUP BY origin"
):
    print(f"  {r['c']:4d}  {r['origin']}")
print("\n  generated examples:")
for r in con.execute("SELECT file_path FROM module_origins WHERE origin='generated' LIMIT 8"):
    print(f"    {r['file_path']}")

print("\n=== A15 snapshot_metadata ===")
for r in con.execute("SELECT * FROM snapshot_metadata"):
    print(f"  {r['key']:25s}  {r['value']}")

print("\n=== mv_r6_summary ===")
for r in con.execute("SELECT * FROM mv_r6_summary"):
    for k in r.keys():
        print(f"  {k:30s}  {r[k]}")
