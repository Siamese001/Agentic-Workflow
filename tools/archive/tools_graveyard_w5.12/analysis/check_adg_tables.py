import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_03252026_0422.sqlite")
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in ADG:")
for table in tables:
    print(f"  {table}")

# Check if violations table exists
if "violations" in tables:
    cursor = conn.execute("SELECT COUNT(*) FROM violations WHERE category='antipattern'")
    count = cursor.fetchone()[0]
    print(f"Antipattern violations: {count}")
else:
    print("No violations table found")

conn.close()
