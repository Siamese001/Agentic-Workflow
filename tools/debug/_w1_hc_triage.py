"""Dump all 19 HIGH+CRITICAL violations for triage."""
import sqlite3
from pathlib import Path
p = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"),
           key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
print(f"snap: {p.name}\n")
print(f"{'Sev':<10}{'Cat':<14}{'Class':<14}{'Evidence':<40}{'File:Line'}")
print("-" * 120)
for r in c.execute("""
    SELECT severity, category, violation_class, evidence, file_path, line_no
    FROM violations
    WHERE severity IN ('HIGH','CRITICAL')
    ORDER BY severity DESC, category, file_path
"""):
    sev, cat, cls, ev, fp, ln = r
    print(f"{sev:<10}{str(cat):<14}{str(cls):<14}{str(ev)[:38]:<40}{fp}:{ln}")
