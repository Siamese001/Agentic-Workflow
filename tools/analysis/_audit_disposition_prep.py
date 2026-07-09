"""Generate a disposition triage CSV for AUDIT_6 89 HIGH/CRITICAL/P0 untriaged rows.

Output: docs/reports/audit_6_disposition_triage.csv
The CSV is the canonical work-list for a follow-up wave that resolves each row
either by (a) fixing the antipattern in source, or (b) recording a guardian
exemption with justification, or (c) marking 'deferred' with a tracking ticket.
"""
from __future__ import annotations

import csv
import glob
import logging
import os
import sqlite3
from pathlib import Path

REPO = Path(".")
OUT = REPO / "docs" / "reports" / "audit_6_disposition_triage.csv"

latest = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
print(f"Snapshot: {latest}")
logging.info("C3 write receipt: tools/analysis/_audit_disposition_prep.py write side effect recorded")
c = sqlite3.connect(latest)
cur = c.cursor()
cur.execute(
    "SELECT id, category, severity, evidence, file_path, line_no, violation_class "
    "FROM violations "
    "WHERE disposition='untriaged' AND severity IN ('HIGH','CRITICAL','P0') "
    "ORDER BY severity DESC, file_path, line_no"
)
rows = cur.fetchall()
print(f"Found {len(rows)} HIGH/CRITICAL/P0 untriaged rows")

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow([
        "violation_id", "severity", "category", "violation_class",
        "evidence", "file_path", "line_no",
        "proposed_disposition", "guardian_justification", "owner", "tracking_link",
    ])
    for r in rows:
        vid, cat, sev, ev, fp, ln, vc = r
        # Heuristic proposed disposition based on evidence
        if cat == "SC-1":
            proposed = "fix-required"
            justification = "P0 SC-1 layer violations cannot be exempted; refactor to remove cross-layer import."
        elif sev in ("CRITICAL", "P0"):
            proposed = "fix-required"
            justification = ""
        elif ev in ("Exception", "AttributeError", "ImportError", "OSError", "getattr"):
            proposed = "guardian-or-fix"
            justification = "Broad-catch antipattern — must replace with specific exception OR add guardian comment with case-specific justification per anti-pattern-author-gate.md."
        else:
            proposed = "review"
            justification = ""
        w.writerow([vid, sev, cat, vc, ev, fp, ln, proposed, justification, "", ""])

print(f"Wrote {OUT}")

# Summary by severity + evidence
print("\nDisposition prep summary:")
cur2 = c.cursor()
cur2.execute(
    "SELECT severity, evidence, COUNT(*) FROM violations "
    "WHERE disposition='untriaged' AND severity IN ('HIGH','CRITICAL','P0') "
    "GROUP BY severity, evidence ORDER BY severity DESC, COUNT(*) DESC"
)
for sev, ev, n in cur2.fetchall():
    print(f"  {sev:<10} {ev:<35} {n}")
