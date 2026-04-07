"""ADG violation + dead import audit — generates phase plan data."""

import pathlib
import sqlite3
from collections import defaultdict

DB = pathlib.Path("artifacts/adg/adg_indexed_03122026.sqlite")
conn = sqlite3.connect(DB)

# ── Violations by rule (symbol) ───────────────────────────────────────────────
print("=== VIOLATIONS BY RULE ===")
rows = conn.execute(
    "SELECT e.symbol, COUNT(*) as cnt FROM edges e "
    "WHERE e.relation_type='violates' GROUP BY e.symbol ORDER BY cnt DESC",
).fetchall()
for r in rows:
    print(f"  {r[1]:4d}  {r[0]}")

# ── Top violating files ────────────────────────────────────────────────────────
print("\n=== TOP VIOLATING FILES (>=2 violations) ===")
rows2 = conn.execute(
    "SELECT e.source_file, COUNT(*) as cnt FROM edges e "
    "WHERE e.relation_type='violates' GROUP BY e.source_file "
    "HAVING cnt >= 2 ORDER BY cnt DESC",
).fetchall()
for r in rows2:
    print(f"  {r[1]:4d}  {r[0]}")

# ── execute_ssot.py violations (biggest offender) ─────────────────────────────
print("\n=== execute_ssot.py violations ===")
rows3 = conn.execute(
    "SELECT e.symbol, e.line_no FROM edges e "
    "WHERE e.relation_type='violates' AND e.source_file LIKE '%execute_ssot%' "
    "ORDER BY e.line_no",
).fetchall()
for r in rows3:
    print(f"  line {r[1]:5d}  {r[0]}")

# ── Dead imports by top-level directory ───────────────────────────────────────
print("\n=== DEAD IMPORTS BY TOP DIR ===")
rows4 = conn.execute(
    "SELECT e.source_file, COUNT(*) as cnt FROM edges e "
    "WHERE e.relation_type='dead_imports' GROUP BY e.source_file "
    "ORDER BY cnt DESC LIMIT 20",
).fetchall()
for r in rows4:
    print(f"  {r[1]:5d}  {r[0]}")

# ── Summary by layer ──────────────────────────────────────────────────────────
print("\n=== VIOLATIONS BY SOURCE LAYER ===")
by_layer = defaultdict(int)
all_viols = conn.execute("SELECT e.source_file FROM edges e WHERE e.relation_type='violates'").fetchall()
for (sf,) in all_viols:
    parts = sf.split("/")
    layer = parts[1] if len(parts) > 1 and parts[0] == "agentic_core" else parts[0]
    by_layer[layer] += 1
for layer, cnt in sorted(by_layer.items(), key=lambda x: -x[1]):
    print(f"  {cnt:4d}  {layer}")

conn.close()
