"""Check P1 (HIGH) detail breakdown in latest ADG snapshot."""

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

# Severity distribution
c.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity ORDER BY COUNT(*) DESC")
print("Severity distribution:")
for sev, cnt in c.fetchall():
    print(f"  {sev}: {cnt}")

# HIGH (P1) by evidence pattern
c.execute(
    "SELECT evidence, COUNT(*) FROM violations "
    "WHERE severity='HIGH' GROUP BY evidence "
    "ORDER BY COUNT(*) DESC LIMIT 20"
)
print("\nHIGH (P1) by evidence pattern:")
for ev, cnt in c.fetchall():
    print(f"  {ev}: {cnt}")

# Specifically Exception evidence at HIGH
c.execute("SELECT COUNT(*) FROM violations WHERE severity='HIGH' AND evidence='Exception'")
print(f"\nHIGH with evidence='Exception': {c.fetchone()[0]}")

# Files with HIGH Exception
c.execute(
    "SELECT file_path, COUNT(*) FROM violations "
    "WHERE severity='HIGH' AND evidence='Exception' "
    "GROUP BY file_path ORDER BY COUNT(*) DESC LIMIT 30"
)
print("\nTop files with HIGH/Exception:")
for fp, cnt in c.fetchall():
    print(f"  {cnt:3d} {fp}")

conn.close()
