#!/usr/bin/env python3
"""Validate the 3 fixes: hotspot centrality, cone risk, SC checks."""

import sqlite3
import sys
from pathlib import Path

# Add tools to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from tools.generate.materialized_views.phase_a_path_authority import materialize_phase_a
from tools.generate.materialized_views.phase_b_capability_tool_task import materialize_phase_b

# Find latest SQLite
adg_dir = Path("artifacts/adg")
sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
if not sqlite_files:
    print("ERROR: No SQLite found")
    sys.exit(1)
sqlite_path = sqlite_files[-1]
print(f"Using: {sqlite_path.name}")

# Run Phase A to get hotspot centrality
print("\n=== Running Phase A materialization ===")
counts_a = materialize_phase_a(sqlite_path)
print(f"mv_hotspot_centrality: {counts_a.get('mv_hotspot_centrality', 0)} rows")

# Run Phase B to get cone risk
print("\n=== Running Phase B materialization ===")
counts_b = materialize_phase_b(sqlite_path)
print(f"mv_dependency_cone_risk: {counts_b.get('mv_dependency_cone_risk', 0)} rows")

# Connect and validate
conn = sqlite3.connect(str(sqlite_path))
cur = conn.cursor()

print("\n=== VALIDATION: mv_hotspot_centrality ===")
cur.execute(
    "SELECT COUNT(*), AVG(fan_in), MAX(fan_in), AVG(fan_out), MAX(fan_out) FROM mv_hotspot_centrality"
)
total, avg_fi, max_fi, avg_fo, max_fo = cur.fetchone()
print(f"Total modules: {total}")
print(f"Fan-in: avg={avg_fi:.1f}, max={max_fi}")
print(f"Fan-out: avg={avg_fo:.1f}, max={max_fo}")

if max_fi and max_fi > 0:
    print("✅ PASS: fan_in is no longer zero for all rows")
    cur.execute(
        "SELECT resolved_path, layer, fan_in, fan_out FROM mv_hotspot_centrality ORDER BY fan_in DESC LIMIT 10"
    )
    print("\nTop 10 by fan_in:")
    for row in cur.fetchall():
        layer = row[1] or "N/A"
        print(f"  {layer:8} fi={row[2]:5} fo={row[3]:5} {row[0][:50]}")
else:
    print("❌ FAIL: fan_in still zero for all rows")

print("\n=== VALIDATION: mv_dependency_cone_risk ===")
cur.execute("SELECT COUNT(*), AVG(cone_risk_score), MAX(cone_risk_score) FROM mv_dependency_cone_risk")
total, avg_score, max_score = cur.fetchone()
print(f"Total modules: {total}")
print(f"Cone risk: avg={avg_score:.2f}, max={max_score}")

cur.execute("SELECT COUNT(*) FROM mv_dependency_cone_risk WHERE hop2_fan_in > 0")
hop2_count = cur.fetchone()[0]
print(f"Modules with hop-2 fan-in > 0: {hop2_count}")

if max_score and max_score > 0:
    print("✅ PASS: cone_risk_score is no longer zero")
    cur.execute(
        "SELECT resolved_path, layer, direct_fan_in, hop2_fan_in, cone_risk_score FROM mv_dependency_cone_risk ORDER BY cone_risk_score DESC LIMIT 10"
    )
    print("\nTop 10 by cone risk:")
    for row in cur.fetchall():
        layer = row[1] or "N/A"
        print(f"  {layer:8} d={row[2]:4} h2={row[3]:4} score={row[4]:6.2f} {row[0][:40]}")
else:
    print("❌ FAIL: cone_risk_score still zero for all rows")

print("\n=== VALIDATION: SC-1 / SC-5 Enabled ===")
cur.execute("SELECT COUNT(*) FROM violations WHERE category = 'SC-1'")
sc1_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM violations WHERE category = 'SC-5'")
sc5_count = cur.fetchone()[0]
print(f"SC-1 violations: {sc1_count}")
print(f"SC-5 violations: {sc5_count}")

if sc1_count > 0 or sc5_count > 0:
    print("✅ PASS: SC-1/SC-5 checks are producing violations")
else:
    print("⚠️  NOTE: SC-1/SC-5 enabled but no violations found (may be valid or checks need to run)")

conn.close()
print("\n=== Validation complete ===")
