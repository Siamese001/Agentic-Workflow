"""Query the ADG SQLite artifact at artifacts/adg/adg_indexed_03122026.sqlite.

Confirms:
1. Relation types present in the graph
2. All /types/ production modules ranked by fan-in (inbound edges)
3. Which of those are uncovered (no 'covers' edge from any test node)
"""

import sqlite3

DB = r"artifacts/adg/adg_indexed_03122026.sqlite"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Relation types present
rel_types = [
    r[0] for r in conn.execute("SELECT DISTINCT relation_type FROM edges ORDER BY relation_type").fetchall()
]
print("Relation types in ADG:", rel_types)
print()

# All production /types/ modules ranked by total inbound edges (fan-in)
all_types = conn.execute("""
    SELECT n.resolved_path, COUNT(e.dst_id) AS fan_in
    FROM nodes n
    LEFT JOIN edges e ON e.dst_id = n.id
    WHERE n.resolved_path LIKE '%/types/%'
      AND n.resolved_path NOT LIKE '%__init__%'
      AND n.resolved_path NOT LIKE 'tests/%'
      AND n.entity_type = 'module'
    GROUP BY n.id
    ORDER BY fan_in DESC
""").fetchall()
print(f"All production /types/ modules ranked by fan-in ({len(all_types)}):")
for r in all_types:
    print(f"  fan_in={r['fan_in']:4d}  {r['resolved_path']}")
print()

# Uncovered: no 'covers' edge from any test module pointing to them
uncovered = conn.execute("""
    SELECT n.resolved_path, COUNT(e.dst_id) AS fan_in
    FROM nodes n
    LEFT JOIN edges e ON e.dst_id = n.id
    WHERE n.resolved_path LIKE '%/types/%'
      AND n.resolved_path NOT LIKE '%__init__%'
      AND n.resolved_path NOT LIKE 'tests/%'
      AND n.entity_type = 'module'
      AND NOT EXISTS (
          SELECT 1 FROM edges e2
          JOIN nodes src ON src.id = e2.src_id
          WHERE e2.dst_id = n.id
            AND e2.relation_type = 'covers'
      )
    GROUP BY n.id
    ORDER BY fan_in DESC
""").fetchall()
print(f"UNCOVERED production /types/ modules (no 'covers' edge) ({len(uncovered)}):")
for r in uncovered:
    print(f"  fan_in={r['fan_in']:4d}  {r['resolved_path']}")

conn.close()
