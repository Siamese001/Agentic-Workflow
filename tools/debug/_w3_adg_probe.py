"""Probe ADG for pre-existing layer/gravity signals before building W3 gates."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import importlib
_gate_base = importlib.import_module("ops_scripts.ci._adg_wiring_gate_base")
connect_snapshot = _gate_base.connect_snapshot
latest_snapshot = _gate_base.latest_snapshot

conn = connect_snapshot(latest_snapshot())

print("== violations table schema ==")
for row in conn.execute("PRAGMA table_info(violations)"):
    print(" ", row)
print()

print("== violations categories + severities ==")
for row in conn.execute(
    "SELECT category, severity, COUNT(*) FROM violations GROUP BY category, severity ORDER BY 3 DESC LIMIT 30"
):
    print(f"  {row[0]:40s} {row[1]:10s} {row[2]}")
print()

print("== nodes schema (to see if loc/complexity tracked) ==")
for row in conn.execute("PRAGMA table_info(nodes)"):
    print(" ", row)
print()

print("== distinct layers ==")
for row in conn.execute(
    "SELECT layer, COUNT(*) FROM nodes WHERE layer IS NOT NULL GROUP BY layer ORDER BY 2 DESC"
):
    print(f"  {row[0]:15s} {row[1]}")
print()

print("== sample L_PG modules ==")
for row in conn.execute(
    "SELECT resolved_path FROM nodes WHERE layer='L_PG' AND entity_type='module' LIMIT 10"
):
    print(f"  {row[0]}")
