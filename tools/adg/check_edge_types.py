"""Check what edge relation types exist for test->src coverage."""

import glob
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
db = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

# What relation types do test files have to agentic_core src?
rows = list(
    conn.execute(
        "SELECT e.relation_type, e.edge_kind, COUNT(*) as cnt "
        "FROM edges e "
        "JOIN nodes n1 ON e.src_id=n1.id "
        "JOIN nodes n2 ON e.dst_id=n2.id "
        "WHERE n1.resolved_path LIKE 'tests/%' "
        "AND n2.resolved_path LIKE 'agentic_core/%' "
        "GROUP BY e.relation_type, e.edge_kind "
        "ORDER BY cnt DESC",
    ),
)
print("Edge types from tests/ -> agentic_core/:")
for r in rows:
    print(f"  {r['relation_type']:<20} {r['edge_kind']:<25} count={r['cnt']}")

# Specifically for the react_chunking_telemetry stub
stub = "tests/unit/agentic_core/L1_cognition/telemetry/test_react_chunking_telemetry_adg.py"
row = conn.execute("SELECT id FROM nodes WHERE resolved_path=?", (stub,)).fetchone()
if row:
    print(f"\nEdges from {stub}:")
    for e in conn.execute(
        "SELECT e.relation_type, e.edge_kind, n2.resolved_path "
        "FROM edges e JOIN nodes n2 ON e.dst_id=n2.id "
        "WHERE e.src_id=?",
        (row["id"],),
    ):
        print(f"  {e['relation_type']:<20} {e['edge_kind']:<25} -> {e['resolved_path']}")

conn.close()
