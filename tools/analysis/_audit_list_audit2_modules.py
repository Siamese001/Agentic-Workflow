"""Identify the 4 modules currently failing AUDIT_2 (observability blind spot)."""

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3, glob, os
latest = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
c = sqlite3.connect(latest)
cur = c.cursor()
cur.execute("""
    SELECT n.id, n.adg_name, n.layer, n.resolved_path, h.fan_in, h.fan_out
    FROM nodes n
    JOIN mv_hotspot_centrality h ON h.node_id = n.id
    WHERE n.entity_type = 'module'
      AND h.fan_in >= 50
      AND n.layer IN ('L0', 'L1', 'L2', 'L3', 'L4', 'L5')
      AND n.resolved_path NOT LIKE 'tests/%'
      AND n.resolved_path NOT LIKE 'archives/%'
      AND n.resolved_path NOT LIKE 'docs/archive/windsurf/legacy-tree/%'
      AND n.id NOT IN (
          SELECT DISTINCT e.src_id FROM edges e
          JOIN nodes dst ON dst.id = e.dst_id
          WHERE dst.layer = 'L6'
             OR dst.adg_name LIKE '%trace%'
             OR dst.adg_name LIKE '%logger%'
             OR dst.adg_name LIKE '%logging%'
             OR dst.adg_name LIKE '%metric%'
             OR dst.adg_name LIKE '%audit%'
             OR dst.adg_name LIKE '%observ%'
             OR dst.adg_name LIKE '%otel%'
             OR dst.adg_name LIKE '%span%'
             OR dst.adg_name LIKE '%emit%'
             OR dst.adg_name LIKE '%MetricsEmission%'
      )
    ORDER BY h.fan_in DESC
""")
print(f"AUDIT_2 blind modules ({latest}):")
for row in cur.fetchall():
    print(f"  fan_in={row[4]:>4} fan_out={row[5]:>4} layer={row[2]} {row[3]}")
