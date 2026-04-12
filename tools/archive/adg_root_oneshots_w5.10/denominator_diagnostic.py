"""Diagnostic: quantify synthetic vs real base edges in the ADG."""

import glob
import os
import sqlite3

ADG_DIR = r"C:\Git\Agentic-Workflow\artifacts\adg"
pattern = os.path.join(ADG_DIR, "adg_indexed_*.sqlite")
files = sorted(glob.glob(pattern))
db_path = files[-1]
print(f"Using: {db_path}")

conn = sqlite3.connect(db_path)

# 1. calls edges: how many target _emit_* symbols?
print("\n=== CALLS EDGES: synthetic _emit_* vs real ===")
total_calls = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='calls'").fetchone()[0]
emit_calls = conn.execute(
    "SELECT COUNT(*) FROM edges WHERE relation_type='calls' AND symbol LIKE '%._emit_%'",
).fetchone()[0]
emit_calls2 = conn.execute(
    "SELECT COUNT(*) FROM edges WHERE relation_type='calls' AND symbol LIKE '%.emit_%'",
).fetchone()[0]
print(f"  Total calls edges: {total_calls}")
print(f"  _emit_* calls (synthetic): {emit_calls}")
print(f"  emit_* calls (includes emit_replay_key etc): {emit_calls2}")
print(f"  Real calls (total - _emit_*): {total_calls - emit_calls}")

# Top 20 calls symbols
print("\n  Top 30 calls target symbols:")
rows = conn.execute(
    "SELECT symbol, COUNT(*) as cnt FROM edges WHERE relation_type='calls' GROUP BY symbol ORDER BY cnt DESC LIMIT 30",
).fetchall()
for sym, cnt in rows:
    marker = " *** SYNTHETIC" if "_emit_" in sym or sym.startswith("emit_") else ""
    print(f"    {sym}: {cnt}{marker}")

# 2. records_execution_trace: synthetic _emit_* vs real
print("\n=== RECORDS_EXECUTION_TRACE EDGES: synthetic vs real ===")
total_ret = conn.execute(
    "SELECT COUNT(*) FROM edges WHERE relation_type='records_execution_trace'"
).fetchone()[0]
emit_ret = conn.execute(
    "SELECT COUNT(*) FROM edges WHERE relation_type='records_execution_trace' AND symbol LIKE '%_emit_%'",
).fetchone()[0]
print(f"  Total records_execution_trace: {total_ret}")
print(f"  _emit_* sourced (synthetic): {emit_ret}")
print(f"  Real: {total_ret - emit_ret}")

print("\n  All records_execution_trace symbols:")
rows = conn.execute(
    "SELECT symbol, COUNT(*) as cnt FROM edges WHERE relation_type='records_execution_trace' GROUP BY symbol ORDER BY cnt DESC",
).fetchall()
for sym, cnt in rows:
    marker = " *** SYNTHETIC" if "_emit_" in sym else ""
    print(f"    {sym}: {cnt}{marker}")

# 3. writes_to: synthetic _emit_writes_through vs real
print("\n=== WRITES_TO EDGES: synthetic vs real ===")
total_wt = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='writes_to'").fetchone()[0]
emit_wt = conn.execute(
    "SELECT COUNT(*) FROM edges WHERE relation_type='writes_to' AND symbol LIKE '%_emit_%'",
).fetchone()[0]
print(f"  Total writes_to: {total_wt}")
print(f"  _emit_* sourced (synthetic): {emit_wt}")
print(f"  Real: {total_wt - emit_wt}")

print("\n  Top 20 writes_to symbols:")
rows = conn.execute(
    "SELECT symbol, COUNT(*) as cnt FROM edges WHERE relation_type='writes_to' GROUP BY symbol ORDER BY cnt DESC LIMIT 20",
).fetchall()
for sym, cnt in rows:
    marker = " *** SYNTHETIC" if "_emit_" in sym else ""
    print(f"    {sym}: {cnt}{marker}")

# 4. reads_from: check for synthetic sources
print("\n=== READS_FROM EDGES: by edge_kind ===")
rows = conn.execute(
    "SELECT edge_kind, COUNT(*) as cnt FROM edges WHERE relation_type='reads_from' GROUP BY edge_kind ORDER BY cnt DESC",
).fetchall()
for ek, cnt in rows:
    print(f"  {ek}: {cnt}")

conn.close()
