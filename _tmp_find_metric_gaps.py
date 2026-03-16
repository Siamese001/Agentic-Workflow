"""Find modules with calls but missing emits_metric_event edge."""
import sqlite3, glob, os

db_files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)
db = db_files[-1]
print(f"Using: {db}")
conn = sqlite3.connect(db)

# Modules that have calls but NO emits_metric_event
q = """
SELECT DISTINCT r1.source_file
FROM relations r1
WHERE r1.relation_type = 'calls'
  AND r1.source_file NOT IN (
    SELECT DISTINCT r2.source_file
    FROM relations r2
    WHERE r2.relation_type = 'emits_metric_event'
  )
ORDER BY r1.source_file
LIMIT 30
"""
rows = conn.execute(q).fetchall()
print(f"\nFound {len(rows)} candidate modules missing emits_metric_event:")
for r in rows:
    print(f"  {r[0]}")

# Also show current ratio
total = conn.execute("SELECT COUNT(DISTINCT source_file) FROM relations WHERE relation_type='calls'").fetchone()[0]
have = conn.execute("SELECT COUNT(DISTINCT source_file) FROM relations WHERE relation_type='emits_metric_event'").fetchone()[0]
print(f"\nCurrent ratio: {have}/{total} = {have/total*100:.2f}%")
conn.close()
