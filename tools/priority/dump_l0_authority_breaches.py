"""W1.1 catalog: dump all 17 L_APP_core_bypass breaches to CSV for remediation."""
import csv
import logging
import sqlite3
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
out = Path("docs/reports/maintenance/l0_authority_breaches_catalog.csv")
out.parent.mkdir(parents=True, exist_ok=True)
logging.info("C3 write receipt: tools/priority/dump_l0_authority_breaches.py write side effect recorded")

con = sqlite3.connect(snap)
cur = con.cursor()
cur.execute("PRAGMA table_info(mv_authority_boundary_breaches)")
cols = [r[1] for r in cur.fetchall()]
cur.execute("""
    SELECT src_file, src_layer, dst_file, dst_layer, line_no, breach_class
    FROM mv_authority_boundary_breaches
    ORDER BY src_file, line_no
""")
rows = cur.fetchall()

with out.open("w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["#", "src_file", "src_layer", "dst_file", "dst_layer", "line_no", "breach_class", "remediation_tier"])
    for i, r in enumerate(rows, 1):
        # Tier 1 (simple): typing or constants imports — exempt-or-relocate
        # Tier 2 (structural): logic imports — needs orchestrator wrapper
        dst = r[2]
        tier = "T1-simple" if any(k in dst for k in ("/types/", "/config/", "_constants", "/contracts")) else "T2-structural"
        w.writerow([i, r[0], r[1], r[2], r[3], r[4], r[5], tier])

print(f"Wrote {len(rows)} rows to {out}")

# Tier breakdown
import collections

counter = collections.Counter()
for r in rows:
    dst = r[2]
    tier = "T1-simple" if any(k in dst for k in ("/types/", "/config/", "_constants", "/contracts")) else "T2-structural"
    counter[tier] += 1
print(f"Tier breakdown: {dict(counter)}")

# By source file
src_counter = collections.Counter(r[0] for r in rows)
print(f"\nBy source file:")
for src, n in src_counter.most_common():
    print(f"  {n:2d}  {src}")
con.close()
