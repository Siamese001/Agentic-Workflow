"""Query ADG SQLite for build plan analysis."""

import sqlite3

DB = r"c:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0745.sqlite"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Table names
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print("TABLES:", tables)

# Layer breakdown
cur.execute("SELECT layer, COUNT(*) FROM nodes GROUP BY layer ORDER BY COUNT(*) DESC")
print("\nLAYER COUNTS:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# All L_APP nodes (apps_* modules) - use adg_name column
cur.execute("""
    SELECT adg_name, layer, entity_type, resolved_path
    FROM nodes
    WHERE layer = 'L_APP'
    ORDER BY adg_name
    LIMIT 100
""")
print("\nL_APP SAMPLE (first 100):")
for row in cur.fetchall():
    print(f"  {row[0]} | {row[2]} | {row[3]}")

# Distinct app top-level folders
cur.execute("""
    SELECT DISTINCT
        CASE
            WHEN resolved_path LIKE 'apps_lic/%' THEN 'apps_lic'
            WHEN resolved_path LIKE 'apps_rg/%' THEN 'apps_rg'
            WHEN resolved_path LIKE 'apps_exec/%' THEN 'apps_exec'
            WHEN resolved_path LIKE 'apps_eval/%' THEN 'apps_eval'
            WHEN resolved_path LIKE 'apps_research/%' THEN 'apps_research'
            WHEN resolved_path LIKE 'apps_rfp/%' THEN 'apps_rfp'
            WHEN resolved_path LIKE 'apps_shared/%' THEN 'apps_shared'
            ELSE 'other_' || substr(resolved_path, 1, instr(resolved_path||'/', '/') - 1)
        END as app_folder,
        COUNT(*) as cnt
    FROM nodes
    WHERE layer IN ('L_APP', 'L_SHARED')
    GROUP BY app_folder
    ORDER BY cnt DESC
""")
print("\nAPP FOLDER GROUPS:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# L_SHARED nodes
cur.execute("""
    SELECT adg_name, entity_type, resolved_path
    FROM nodes
    WHERE layer = 'L_SHARED'
    ORDER BY adg_name
    LIMIT 50
""")
print("\nL_SHARED SAMPLE (first 50):")
for row in cur.fetchall():
    print(f"  {row[2]} | {row[1]}")

# Relation types used across app layers
cur.execute("""
    SELECT relation_type, COUNT(*) as cnt
    FROM edges e
    JOIN nodes n ON e.src_id = n.id
    WHERE n.layer IN ('L_APP', 'L_SHARED')
    GROUP BY relation_type
    ORDER BY cnt DESC
    LIMIT 30
""")
print("\nRELATION TYPES FROM APP/SHARED:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# apps_shared outgoing imports - what does shared import from core?
cur.execute("""
    SELECT n2.layer, COUNT(*) as cnt
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE n1.layer = 'L_SHARED'
    AND e.relation_type = 'imports'
    GROUP BY n2.layer
    ORDER BY cnt DESC
""")
print("\napps_shared IMPORTS BY TARGET LAYER:")
for row in cur.fetchall():
    print(f"  -> {row[0]}: {row[1]}")

# What imports apps_shared?
cur.execute("""
    SELECT n1.layer, COUNT(*) as cnt
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE n2.layer = 'L_SHARED'
    AND e.relation_type = 'imports'
    GROUP BY n1.layer
    ORDER BY cnt DESC
""")
print("\nWHAT IMPORTS apps_shared (by layer):")
for row in cur.fetchall():
    print(f"  {row[0]} ->: {row[1]}")

# apps_shared missing coverage (no test covers)
cur.execute("""
    SELECT n.resolved_path
    FROM nodes n
    WHERE n.layer = 'L_SHARED'
    AND n.entity_type = 'module'
    AND n.id NOT IN (
        SELECT dst_id FROM edges WHERE relation_type = 'covers'
    )
    ORDER BY n.resolved_path
    LIMIT 30
""")
print("\napps_shared MODULES WITH NO TEST COVERAGE:")
for row in cur.fetchall():
    print(f"  {row[0]}")

conn.close()
