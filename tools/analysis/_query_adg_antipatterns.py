#!/usr/bin/env python3
"""Query ADG for antipattern violations - full reclassification analysis."""
import os
import sqlite3
from pathlib import Path

# Always use the latest non-empty ADG sqlite that has the violations table
adg_dir = Path(__file__).resolve().parents[2] / "artifacts" / "adg"
dbs = sorted(
    [p for p in adg_dir.glob("adg_indexed_*.sqlite") if p.stat().st_size > 0],
    key=os.path.getmtime,
    reverse=True,
)
if not dbs:
    raise FileNotFoundError("No non-empty ADG sqlite found in artifacts/adg/")

DB_PATH = str(dbs[0])
print(f"DB: {dbs[0].name}\n")

conn = sqlite3.connect(DB_PATH)

# Verify violations table exists
tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
if "violations" not in tables:
    print("ERROR: violations table not present — run ADG generation first.")
    conn.close()
    raise SystemExit(1)

SEV_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

# 1. All antipattern edge_kinds by severity
print("=== 1. ANTIPATTERN edge_kinds x severity (current ADG) ===")
rows = conn.execute(
    "SELECT e.edge_kind, v.severity, COUNT(*) cnt"
    " FROM violations v JOIN edges e ON v.edge_id=e.id"
    " WHERE e.relation_type='antipattern'"
    " GROUP BY e.edge_kind, v.severity ORDER BY cnt DESC"
).fetchall()
for r in rows:
    print(f"  {r[1]:8}  {r[0]:40}  {r[2]:6}")

# 2. LOW antipatterns broken down by layer (critical vs non-critical)
print("\n=== 2. LOW antipatterns — critical-layer count ===")
critical_prefixes = (
    "agentic_core/L0_routing/",
    "agentic_core/L5_safety/",
    "agentic_core/L2_execution/",
    "agentic_core/L3_orchestration/",
)
all_low_kinds = [
    r[0] for r in conn.execute(
        "SELECT DISTINCT e.edge_kind FROM violations v JOIN edges e ON v.edge_id=e.id"
        " WHERE e.relation_type='antipattern' AND v.severity='LOW'"
    ).fetchall()
]
for kind in sorted(all_low_kinds):
    total = conn.execute(
        "SELECT COUNT(*) FROM violations v JOIN edges e ON v.edge_id=e.id"
        " WHERE e.relation_type='antipattern' AND v.severity='LOW' AND e.edge_kind=?",
        (kind,)
    ).fetchone()[0]
    in_critical = conn.execute(
        "SELECT COUNT(*) FROM violations v JOIN edges e ON v.edge_id=e.id"
        " WHERE e.relation_type='antipattern' AND v.severity='LOW' AND e.edge_kind=?"
        " AND (e.source_file LIKE 'agentic_core/L0_routing/%'"
        "   OR e.source_file LIKE 'agentic_core/L5_safety/%'"
        "   OR e.source_file LIKE 'agentic_core/L2_execution/%'"
        "   OR e.source_file LIKE 'agentic_core/L3_orchestration/%')",
        (kind,)
    ).fetchone()[0]
    print(f"  {kind:40}  total={total:5}  in_critical={in_critical:5}")

# 3. Sample each LOW kind (up to 8 rows) — source file + symbol for FP analysis
sample_kinds = all_low_kinds
print("\n=== 3. SAMPLE: LOW antipatterns (source + symbol) ===")
for kind in sorted(sample_kinds):
    rows = conn.execute(
        "SELECT e.source_file, e.line_no, e.symbol"
        " FROM violations v JOIN edges e ON v.edge_id=e.id"
        " WHERE e.relation_type='antipattern' AND v.severity='LOW' AND e.edge_kind=?"
        " ORDER BY e.source_file LIMIT 8",
        (kind,)
    ).fetchall()
    print(f"\n  [{kind}]")
    for r in rows:
        print(f"    {r[0]}:{r[1]}  sym={r[2]}")

# 4. MEDIUM antipatterns — top files (potential P2 candidates)
print("\n=== 4. MEDIUM antipatterns — top files by count ===")
rows = conn.execute(
    "SELECT e.edge_kind, e.source_file, COUNT(*) cnt"
    " FROM violations v JOIN edges e ON v.edge_id=e.id"
    " WHERE e.relation_type='antipattern' AND v.severity='MEDIUM'"
    " GROUP BY e.edge_kind, e.source_file ORDER BY cnt DESC LIMIT 30"
).fetchall()
for r in rows:
    print(f"  {r[0]:35}  {r[2]:5}  {r[1]}")

# 5. All violation categories in DB (not just antipattern)
print("\n=== 5. ALL violation categories x severity ===")
rows = conn.execute(
    "SELECT v.category, v.severity, COUNT(*) cnt"
    " FROM violations v GROUP BY v.category, v.severity ORDER BY cnt DESC"
).fetchall()
for r in rows:
    print(f"  cat={r[0]:25}  sev={r[1]:10}  cnt={r[2]}")

conn.close()
