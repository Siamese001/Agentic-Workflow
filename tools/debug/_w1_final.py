"""Final W1 burndown report."""

import sqlite3
from pathlib import Path

p = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
print(f"snap: {p.name}\n")
print("violations by severity:")
order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
rows = sorted(
    c.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity").fetchall(),
    key=lambda r: order.get(r[0], 99),
)
for sev, n in rows:
    print(f"  {sev:<10}{n}")
meta = c.execute("SELECT value FROM meta WHERE key='guardian_exemptions'").fetchone()
print(f"\nguardian exemptions applied: {meta[0] if meta else '?'}")
