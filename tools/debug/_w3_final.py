import sqlite3
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR
p = sorted(Path(ADG_ARTIFACTS_DIR).glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
print(f"snap: {p.name}")
row = c.execute("SELECT value FROM meta WHERE key='guardian_exemptions'").fetchone()
print(f"guardian_exemptions: {row[0] if row else '?'}")
print("by severity:")
for sev, n in c.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity"):
    print(f"  {sev}: {n}")
