"""Check what RootHygieneAgent actually did in the heal run."""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
data = json.loads((ROOT / "logs/compliance_reports/heal_run_complete.json").read_text())

print("=== ROOTHYGIENEAGENT DETAILED ACTIONS ===\n")
for action in data["healing_actions"]:
    if "RootHygiene" in action["agent"]:
        print(f"Agent: {action['agent']}")
        print(f"Territory: {action['territory']}")
        print(f"Outcome: {action['outcome']}")
        print(f"Fix Summary: {action['fix_summary']}")
        print(f"Violations Submitted: {action.get('violations_submitted', 'N/A')}")
        print(f"Violations Fixed: {action.get('violations_fixed', 'N/A')}")

        # Check if there's detail about what was actually done
        if "details" in action:
            print(f"Details: {action['details']}")

        print()

# Check what violations were detected
print("\n=== ROOT HYGIENE VIOLATIONS IN AGGREGATE REPORT ===\n")
agg_data = json.loads((ROOT / "logs/compliance_reports/compliance_report_AGGREGATE.json").read_text())
root_violations = [v for v in agg_data.get("global_violations", []) if v.get("source") == "RootHygieneAgent"]

print(f"Found {len(root_violations)} root hygiene violations:\n")
for i, v in enumerate(root_violations, 1):
    print(f"{i}. {v['type']}: {Path(v['file']).name}")
    print(f"   Severity: {v['severity']}")
    print(f"   Message: {v['message']}")
    print()
