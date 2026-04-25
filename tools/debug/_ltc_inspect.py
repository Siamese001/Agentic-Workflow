"""Inspect lifecycle_trace_contract node 1985."""

import sqlite3

c = sqlite3.connect(r"artifacts/adg/adg_indexed_04232026_0925.sqlite")

print("== node 1985 ==")
for r in c.execute(
    "SELECT id,adg_name,entity_type,layer,resolved_path,identity_kind FROM nodes WHERE id=1985"
):
    print(r)

print("\n== fan-in by relation_type ==")
for r in c.execute(
    "SELECT relation_type, COUNT(*) FROM edges WHERE dst_id=1985 GROUP BY relation_type ORDER BY 2 DESC"
):
    print(r)

print("\n== distinct source files importing node 1985 ==")
for r in c.execute(
    "SELECT COUNT(DISTINCT n.resolved_path) FROM edges e "
    "JOIN nodes n ON n.id=e.src_id "
    "WHERE e.dst_id=1985 AND e.relation_type='imports'"
):
    print(r)

print("\n== top 15 src files by edge count (imports) ==")
for r in c.execute(
    "SELECT n.resolved_path, COUNT(*) AS n FROM edges e "
    "JOIN nodes n ON n.id=e.src_id "
    "WHERE e.dst_id=1985 AND e.relation_type='imports' "
    "GROUP BY n.resolved_path ORDER BY n DESC LIMIT 15"
):
    print(r)

print("\n== sample 5 raw edges ==")
for r in c.execute(
    "SELECT e.id,e.src_id,e.relation_type,e.edge_kind,e.symbol,"
    "e.source_file,e.line_no "
    "FROM edges e WHERE e.dst_id=1985 AND e.relation_type='imports' LIMIT 5"
):
    print(r)

print("\n== any other nodes with same resolved_path? ==")
for r in c.execute(
    "SELECT id, adg_name, entity_type FROM nodes "
    "WHERE resolved_path='agentic_core/runtime/contracts/lifecycle_trace_contract.py' "
    "LIMIT 20"
):
    print(r)

print("\n== symbols exported by node 1985 (top 15 via exports relation) ==")
for r in c.execute(
    "SELECT e.symbol, COUNT(*) FROM edges e "
    "WHERE e.src_id=1985 AND e.relation_type='exports' "
    "GROUP BY e.symbol ORDER BY 2 DESC LIMIT 15"
):
    print(r)

print("\n== top imported symbols FROM this module ==")
for r in c.execute(
    "SELECT e.symbol, COUNT(*) FROM edges e "
    "WHERE e.dst_id=1985 AND e.relation_type='imports' "
    "GROUP BY e.symbol ORDER BY 2 DESC LIMIT 15"
):
    print(r)
