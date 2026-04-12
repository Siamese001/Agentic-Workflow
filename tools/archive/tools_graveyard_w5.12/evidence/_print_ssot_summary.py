"""Print key findings from ssot_healing_detailed_report.json."""

import json
from pathlib import Path

PATH = Path("docs/reports/plans/ssot_healing_detailed_report.json")
with open(PATH, encoding="utf-8") as f:
    r = json.load(f)
print("=== RUN METADATA ===")
for k, v in r["run_metadata"].items():
    print(f"  {k}: {v}")
print("\n=== SUMMARY ===")
for k, v in r["summary"].items():
    print(f"  {k}: {v}")
print("\n=== PREFLIGHT CHECKS ===")
for k, v in r["preflight_checks"].items():
    print(f"  {k}: {v}")
print("\n=== AGENTS ROSTER ===")
print(f"  validation_status: {r['agents_roster']['validation_status']}")
for a in r["agents_roster"]["registered"]:
    print(f"    - {a}")
print("\n=== PROTECTED ROOT BEHAVIOR ===")
for msg in r["protected_root_behavior"]:
    print(f"  {msg}")
print("\n=== KNOWN FAILURES (RCA) ===")
for kf in r["known_failures_rca"]:
    print(f"  failure_type: {kf['failure_type']}")
    for k, v in kf.items():
        if k != "failure_type":
            print(f"    {k}: {v}")
print("\n=== TERRITORY EXECUTION ===")
for t, v in r["territory_execution"].items():
    print(f"  {t}: {v['entry_count']} log entries, {v['errors']} errors, {v['warnings']} warnings")
print("\n=== SSOT DRIFT VIOLATIONS (all 60) ===")
for msg in r["ssot_drift_violations"]:
    print(f"  {msg}")
print("\n=== ERRORS ===")
for e in r["errors"]:
    print(f"  [{e['level']}] {e['logger']}: {e['message'][:120]}")
    for tb in e.get("traceback", [])[:3]:
        print(f"    {tb}")
