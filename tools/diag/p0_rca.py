"""RCA: verify what the P0 gate actually queried vs where the P0 data lives."""

import sqlite3
import glob
import os

adg_dir = r"artifacts\adg"
snapshots = sorted(glob.glob(os.path.join(adg_dir, "adg_indexed_*.sqlite")))
db = snapshots[-1]
print(f"DB: {db}\n")

conn = sqlite3.connect(db)
cur = conn.cursor()

# What _check_p0_violations queries:
cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='violates'")
print(f"edges WHERE relation_type='violates' (what P0 gate checks): {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='in_cycle'")
print(f"edges WHERE relation_type='in_cycle' (P0 Tier 1A):           {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='dynamic_exec'")
print(f"edges WHERE relation_type='dynamic_exec' (P0 Tier 1B):       {cur.fetchone()[0]}")

# Where P0 data actually lives:
cur.execute("SELECT COUNT(*) FROM violations WHERE severity='P0'")
print(f"\nviolations WHERE severity='P0' (actual P0 data):            {cur.fetchone()[0]}")

cur.execute(
    "SELECT COUNT(*) FROM violations WHERE severity='P0' AND violation_class='structural_conformance'"
)
print(f"violations P0 + structural_conformance (SC-1 bucket):       {cur.fetchone()[0]}")

# Available relation types in edges
cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY 2 DESC LIMIT 15")
print("\n=== Top edge relation types ===")
for rt, cnt in cur.fetchall():
    print(f"  {rt}: {cnt}")

conn.close()
