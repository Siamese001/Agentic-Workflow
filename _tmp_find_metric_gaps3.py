"""Find modules with calls but missing emits_metric_event edge."""
import sqlite3, glob, os

db_files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)
db = db_files[-1]
print(f"Using: {db}")
conn = sqlite3.connect(db)

# Modules that have calls but NO emits_metric_event
q = """
SELECT DISTINCT e1.source_file
FROM edges e1
WHERE e1.relation_type = 'calls'
  AND e1.source_file NOT IN (
    SELECT DISTINCT e2.source_file
    FROM edges e2
    WHERE e2.relation_type = 'emits_metric_event'
  )
ORDER BY e1.source_file
LIMIT 30
"""
rows = conn.execute(q).fetchall()
print(f"\nFound {len(rows)} candidate modules missing emits_metric_event:")
for r in rows:
    print(f"  {r[0]}")

# Current ratio
total = conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type='calls'").fetchone()[0]
have = conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type='emits_metric_event'").fetchone()[0]
print(f"\nCurrent ratio: {have}/{total} = {have/total*100:.2f}%")

# Also check all relation_type counts for context
print("\n--- All relation_type edge counts ---")
for row in conn.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY COUNT(*) DESC").fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
