"""Inspect truth-expansion detection quality."""

import sqlite3

con = sqlite3.connect("artifacts/adg/adg_truth_test.sqlite")
con.row_factory = sqlite3.Row

print("=== A12 gate_self_inconsistent ===")
for r in con.execute(
    "SELECT gate_file, claim_phrase, sql_snippet FROM gate_self_consistency WHERE consistent = 0"
):
    print(f"  {r['gate_file']}")
    print(f"     CLAIM: {r['claim_phrase']}")
    print(f"     SQL  : {r['sql_snippet']}")

print("\n=== A11 false_success_stub by file (top 10) ===")
for r in con.execute(
    "SELECT file_path, COUNT(*) c FROM overlay_violations "
    "WHERE category='false_success_stub' GROUP BY file_path "
    "ORDER BY c DESC LIMIT 10"
):
    print(f"  {r['c']:4d}  {r['file_path']}")

print("\n=== A8 hidden_write_outside_uwg (sample) ===")
for r in con.execute(
    "SELECT file_path, line_no, evidence FROM overlay_violations "
    "WHERE category='hidden_write_outside_uwg' LIMIT 12"
):
    print(f"  L{r['line_no']:4d} {r['file_path']}")
    print(f"        {r['evidence']}")

print("\n=== A8 hidden_write top files ===")
for r in con.execute(
    "SELECT file_path, COUNT(*) c FROM overlay_violations "
    "WHERE category='hidden_write_outside_uwg' GROUP BY file_path "
    "ORDER BY c DESC LIMIT 10"
):
    print(f"  {r['c']:3d}  {r['file_path']}")

print("\n=== A9 config_target_missing (sample) ===")
for r in con.execute(
    "SELECT file_path, evidence FROM overlay_violations WHERE category='config_target_missing' LIMIT 12"
):
    print(f"  {r['file_path']}")
    print(f"     -> {r['evidence']}")

print("\n=== A6 entrypoint_kind_summary ===")
for r in con.execute("SELECT * FROM mv_entrypoint_kind_summary"):
    print(f"  {r['n']:5d}  {r['kind']}")

print("\n=== mv_truth_expansion_summary ===")
for r in con.execute("SELECT * FROM mv_truth_expansion_summary"):
    for k in r.keys():
        print(f"  {k:30s}  {r[k]}")
