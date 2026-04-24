"""Probe writes_to edges to calibrate UWG-bypass gate."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import importlib

_gate_base = importlib.import_module("ops_scripts.ci._adg_wiring_gate_base")
connect_snapshot = _gate_base.connect_snapshot
latest_snapshot = _gate_base.latest_snapshot

conn = connect_snapshot(latest_snapshot())

print("== writes_to edge src.layer distribution ==")
for row in conn.execute(
    """
    SELECT src.layer, COUNT(*)
    FROM edges e JOIN nodes src ON src.id = e.src_id
    WHERE e.relation_type = 'writes_to'
    GROUP BY src.layer ORDER BY 2 DESC
    """
):
    print(f"  {row[0] or '(null)':15s} {row[1]}")

print()
print("== writes_to edges by top src modules ==")
for row in conn.execute(
    """
    SELECT src.resolved_path, src.layer, COUNT(*)
    FROM edges e JOIN nodes src ON src.id = e.src_id
    WHERE e.relation_type = 'writes_to'
    GROUP BY src.resolved_path ORDER BY 3 DESC LIMIT 15
    """
):
    print(f"  {row[2]:5d}  {row[1]:10s} {row[0]}")

print()
print("== global_state_mutation src distribution ==")
for row in conn.execute(
    """
    SELECT src.layer, COUNT(*)
    FROM edges e JOIN nodes src ON src.id = e.src_id
    WHERE e.relation_type = 'antipattern' AND e.edge_kind = 'global_state_mutation'
    GROUP BY src.layer ORDER BY 2 DESC
    """
):
    print(f"  {row[0] or '(null)':15s} {row[1]}")

print()
print("== applies_guardrail edge src.layer distribution ==")
for row in conn.execute(
    """
    SELECT src.layer, dst.layer, COUNT(*)
    FROM edges e JOIN nodes src ON src.id = e.src_id
    JOIN nodes dst ON dst.id = e.dst_id
    WHERE e.relation_type = 'applies_guardrail'
    GROUP BY src.layer, dst.layer ORDER BY 3 DESC LIMIT 15
    """
):
    print(f"  {row[2]:5d}  {row[0]:10s} -> {row[1]:10s}")
