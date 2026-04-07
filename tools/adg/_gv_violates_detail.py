"""Inspect what GV_violates edges look like in the ADG."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

# Check if there's a 'violates' relation type
vtypes = list(
    conn.execute("SELECT DISTINCT relation_type FROM edges WHERE relation_type LIKE '%viol%' LIMIT 20"),
)
print("Violation relation types:", [r["relation_type"] for r in vtypes])

# Count GV_violates edges
gv = list(
    conn.execute("""
    SELECT e.relation_type, COUNT(*) as cnt
    FROM edges e
    WHERE e.relation_type IN ('violates','gravity_violates','layer_violates')
    GROUP BY e.relation_type
"""),
)
print("GV edge counts:", [(r["relation_type"], r["cnt"]) for r in gv])

# Check if GV is stored differently - look at all relation types
all_types = list(
    conn.execute(
        "SELECT DISTINCT relation_type, COUNT(*) as cnt FROM edges GROUP BY relation_type ORDER BY cnt DESC LIMIT 20",
    ),
)
print("\nAll edge types:")
for r in all_types:
    print(f"  {r['cnt']:6d}  {r['relation_type']}")

conn.close()
