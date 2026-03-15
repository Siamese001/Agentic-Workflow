"""Check ProposalCommitter detection."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()

print("=== ProposalCommitter symbol usage ===")
c.execute("SELECT source_file, relation_type, symbol FROM edges WHERE symbol LIKE '%ProposalCommitter%'")
for r in c.fetchall():
    print(" ", r)

print("\n=== ROUTING_COMMIT_SYMBOLS in schema.py ===")
with open("agentic_core/adg/schema.py") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "ROUTING_COMMIT_SYMBOLS" in line:
            for j in range(i, min(i + 10, len(lines))):
                print(f"  {j}: {lines[j].rstrip()}")
                if ")" in lines[j] and "]" in lines[j]:
                    break

conn.close()
