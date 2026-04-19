"""Quick check: P1 violation counts in the latest ADG snapshot."""

import sqlite3
import pathlib

dbs = sorted(pathlib.Path("artifacts/adg").glob("adg_indexed_*.sqlite"))
if not dbs:
    print("No ADG snapshots found")
    raise SystemExit(1)

db = dbs[-1]
print(f"Latest snapshot: {db.name}")

conn = sqlite3.connect(str(db))
c = conn.cursor()

# Check if violations table exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='violations'")
if not c.fetchone():
    print("No violations table found")
    # Try alternative table names
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print(f"Available tables: {tables}")
    conn.close()
    raise SystemExit(1)

# Get column names
c.execute("PRAGMA table_info(violations)")
cols = [r[1] for r in c.fetchall()]
print(f"Columns: {cols}")

# Distinct severity values
c.execute("SELECT DISTINCT severity, COUNT(*) FROM violations GROUP BY severity ORDER BY COUNT(*) DESC")
print("Severity distribution:")
for sev, cnt in c.fetchall():
    print(f"  {sev}: {cnt}")

# Distinct category values
c.execute("SELECT DISTINCT category, COUNT(*) FROM violations GROUP BY category ORDER BY COUNT(*) DESC")
print("\nCategory distribution:")
for cat, cnt in c.fetchall():
    print(f"  {cat}: {cnt}")

# Distinct violation_class values
c.execute(
    "SELECT DISTINCT violation_class, COUNT(*) FROM violations GROUP BY violation_class ORDER BY COUNT(*) DESC"
)
print("\nViolation class distribution:")
for vc, cnt in c.fetchall():
    print(f"  {vc}: {cnt}")

# Sample rows
c.execute("SELECT * FROM violations LIMIT 5")
print("\nSample rows:")
for row in c.fetchall():
    print(f"  {row}")

# Now check the anti-pattern table if it exists
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print(f"\nAll tables: {tables}")

# Check if there's an antipattern or hygiene table
for t in tables:
    if "anti" in t.lower() or "hygiene" in t.lower() or "defect" in t.lower() or "pattern" in t.lower():
        c.execute(f"SELECT COUNT(*) FROM [{t}]")
        print(f"\nTable {t}: {c.fetchone()[0]} rows")
        c.execute(f"PRAGMA table_info([{t}])")
        tcols = [r[1] for r in c.fetchall()]
        print(f"  Columns: {tcols}")

conn.close()
