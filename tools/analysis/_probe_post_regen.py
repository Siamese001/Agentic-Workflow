"""Quick burndown report from latest snapshot."""

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import sqlite3
from pathlib import Path

# Find latest snapshot
snaps = sorted(Path(r"artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
db = snaps[0]
print(f"Latest snapshot: {db.name} (mtime={db.stat().st_mtime})")

c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
cur = c.cursor()

# ADG snapshot metadata (table name is snapshot_metadata in this schema)
try:
    cur.execute("SELECT * FROM snapshot_metadata LIMIT 5")
    cols = [d[0] for d in cur.description]
    for r in cur.fetchall():
        for c_, v in zip(cols, r):
            print(f"  {c_}: {v}")
except sqlite3.OperationalError as e:
    print(f"  (no snapshot_metadata: {e})")

print()
print("=== VIOLATION BURNDOWN ===")
cur.execute("SELECT category, severity, COUNT(*) FROM violations GROUP BY category, severity ORDER BY 1, 2")
for r in cur.fetchall():
    print(f"  {r[0]:>15s} / {r[1]:>10s}: {r[2]:>5d}")

print()
print("=== NODE/EDGE COUNTS ===")
cur.execute("SELECT COUNT(*) FROM nodes")
print(f"  nodes: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM edges")
print(f"  edges: {cur.fetchone()[0]}")

print()
print("=== P0/P1/P2/P3 BREAKDOWN (from severity_band column if present) ===")
try:
    cur.execute("SELECT severity_band, COUNT(*) FROM violations GROUP BY severity_band ORDER BY 1")
    for r in cur.fetchall():
        print(f"  {r[0]:>10s}: {r[1]}")
except sqlite3.OperationalError:
    print("  (no severity_band column)")
