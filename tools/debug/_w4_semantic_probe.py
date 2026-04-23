"""Probe semantic edges + safety/write-gateway landmarks for W4."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import importlib
_gate_base = importlib.import_module("ops_scripts.ci._adg_wiring_gate_base")
connect_snapshot = _gate_base.connect_snapshot
latest_snapshot = _gate_base.latest_snapshot

conn = connect_snapshot(latest_snapshot())

print("== relation_type + edge_kind combos ==")
for row in conn.execute(
    "SELECT relation_type, edge_kind, COUNT(*) FROM edges "
    "GROUP BY relation_type, edge_kind ORDER BY 3 DESC LIMIT 30"
):
    print(f"  {row[0]:25s} {row[1]:30s} {row[2]}")

print()
print("== semantic relation types (everything except imports/calls) ==")
for row in conn.execute(
    "SELECT relation_type, COUNT(*) FROM edges "
    "WHERE relation_type NOT IN ('imports','calls') "
    "GROUP BY relation_type ORDER BY 2 DESC"
):
    print(f"  {row[0]:30s} {row[1]}")

print()
print("== write_gateway module present? ==")
for row in conn.execute(
    "SELECT id, resolved_path, layer FROM nodes "
    "WHERE entity_type='module' AND resolved_path LIKE '%write_gateway%'"
):
    print(f"  {row}")

print()
print("== tool_registry module present? ==")
for row in conn.execute(
    "SELECT id, resolved_path, layer FROM nodes "
    "WHERE entity_type='module' AND resolved_path LIKE '%tool_registry%' LIMIT 10"
):
    print(f"  {row}")

print()
print("== L5 safety modules ==")
for row in conn.execute("SELECT COUNT(*) FROM nodes WHERE entity_type='module' AND layer='L5'"):
    print(f"  L5 modules: {row[0]}")

print()
print("== L_PG 'knowledge' vs 'prompt_governance' breakdown ==")
for row in conn.execute(
    "SELECT SUBSTR(resolved_path, 1, INSTR(SUBSTR(resolved_path, 16), '/') + 15) AS root, COUNT(*) "
    "FROM nodes WHERE entity_type='module' AND layer='L_PG' GROUP BY root ORDER BY 2 DESC LIMIT 10"
):
    print(f"  {row}")
