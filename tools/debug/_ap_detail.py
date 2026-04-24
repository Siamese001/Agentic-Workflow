"""Anti-pattern detail: by evidence type (detector) and disposition."""
import sqlite3
from pathlib import Path
p = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)

print("=== evidence (detector) × severity ===")
for r in c.execute("""
    SELECT evidence, severity, COUNT(*) AS n
    FROM violations GROUP BY evidence, severity ORDER BY severity, n DESC
"""):
    print(f"  [{r[1]:8s}] {str(r[0]):35s} {r[2]:6d}")

print("\n=== disposition breakdown (exemption/triage state) ===")
for r in c.execute("""
    SELECT disposition, COUNT(*) FROM violations GROUP BY disposition ORDER BY COUNT(*) DESC
"""):
    print(f"  {str(r[0]):25s} {r[1]}")

print("\n=== severity × disposition (gross vs net) ===")
for r in c.execute("""
    SELECT severity, disposition, COUNT(*) AS n
    FROM violations GROUP BY severity, disposition ORDER BY severity, n DESC
"""):
    print(f"  [{r[0]:8s}] {str(r[1]):25s} {r[2]:6d}")
