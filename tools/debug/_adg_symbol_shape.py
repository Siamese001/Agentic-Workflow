"""Inspect symbol-node shape to understand how to match to archived files."""
from __future__ import annotations

import sqlite3

c = sqlite3.connect("artifacts/adg/adg_indexed_04232026_0925.sqlite")
print("Sample symbol rows:")
for r in c.execute(
    "SELECT adg_name, resolved_path, enclosing_symbol "
    "FROM nodes WHERE entity_type='symbol' LIMIT 8"
):
    print(f"  name={r[0][:60]:<60}  path={r[1][:60]}  enc={r[2][:40]}")

print("\nSymbols with resolved_path ending .py:")
n = c.execute(
    "SELECT COUNT(*) FROM nodes "
    "WHERE entity_type='symbol' AND resolved_path LIKE '%.py'"
).fetchone()[0]
print(f"  count = {n}")

print("\nSymbols for one archived file via LIKE on resolved_path:")
for r in c.execute(
    "SELECT COUNT(*) FROM nodes "
    "WHERE resolved_path LIKE 'apps_shared/utils/unified_signal_pipeline_util%'"
):
    print(f"  matches = {r[0]}")

print("\nAre symbols keyed by a file-qualified name in adg_name?")
for r in c.execute(
    "SELECT adg_name FROM nodes WHERE entity_type='symbol' "
    "AND adg_name LIKE '%unified_signal_pipeline_util%' LIMIT 5"
):
    print(f"  {r[0]}")
