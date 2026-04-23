"""Probe M1 LOC gate — why did it return 0?"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import importlib
_gate_base = importlib.import_module("ops_scripts.ci._adg_wiring_gate_base")
connect_snapshot = _gate_base.connect_snapshot
latest_snapshot = _gate_base.latest_snapshot

conn = connect_snapshot(latest_snapshot())

print("== top 10 modules by MAX(span_end_line) ==")
for row in conn.execute(
    """
    SELECT resolved_path, MAX(span_end_line)
    FROM nodes
    WHERE entity_type='symbol' AND resolved_path IS NOT NULL
    GROUP BY resolved_path
    ORDER BY 2 DESC
    LIMIT 10
    """
):
    print(f"  {row[1]:6d}  {row[0]}")

print()
for threshold in (100, 200, 300, 400, 500, 1000):
    n = conn.execute(
        "SELECT COUNT(DISTINCT resolved_path) FROM nodes WHERE entity_type='symbol' AND span_end_line > ?",
        (threshold,),
    ).fetchone()[0]
    print(f"  modules with any symbol span_end_line > {threshold}: {n}")

print()
print("== schema check: do modules have span info? ==")
for row in conn.execute(
    """
    SELECT entity_type, COUNT(*),
           SUM(CASE WHEN span_end_line > 0 THEN 1 ELSE 0 END)
    FROM nodes GROUP BY entity_type
    """
):
    print(f"  {row[0]:15s} total={row[1]:8d}  with span_end_line>0={row[2]}")
