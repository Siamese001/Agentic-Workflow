#!/usr/bin/env python3
"""Check territory names and order in dashboard data."""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"

content = data_file.read_text(encoding='utf-8')
lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
data = json.loads(content)

print("\n" + "="*70)
print("CURRENT TERRITORY ORDER IN DASHBOARD")
print("="*70)
for i, row in enumerate(data):
    print(f"{i+1:2}. {row['Territory']}")

print("\n" + "="*70)
print("EXPECTED TERRITORY ORDER (Base Agent First)")
print("="*70)
expected = [
    'TOTAL',
    'Sovereign Base Agent',
    'L6_Observability/Base Agent',
    'L6_Observability/Metrics',
    'L6_Observability/Telemetry',
    'L5 Safety/Base Agent',
    'L5 Safety/Validators',
    'L5 Safety/Guardrails',
    'L5 Safety/Red Teaming',
    'L5 Safety/Gravity',
    'L4 State/Base Agent',
    'L4 State/Infrastructure',
    'L4 State/Core',
    'L3 Orchestration/Base Agent',
    'L3 Orchestration/Core',
    'L2 Execution/Base Agent',
    'L2 Execution/Core',
    'L1 Cognition/Base Agent',
    'L1 Cognition/Core',
    'L0 Maintenance/Base Agent',
    'L0 Maintenance/Core',
    'Apps Rg',
    'Apps Lic',
    'Utils'
]

for i, territory in enumerate(expected):
    print(f"{i+1:2}. {territory}")

print("\n" + "="*70)
print("COMPARISON")
print("="*70)

actual_territories = [row['Territory'] for row in data]

print(f"\nActual count: {len(actual_territories)}")
print(f"Expected count: {len(expected)}")

missing = set(expected) - set(actual_territories)
extra = set(actual_territories) - set(expected)

if missing:
    print(f"\n❌ MISSING territories:")
    for t in sorted(missing):
        print(f"  - {t}")

if extra:
    print(f"\n⚠️  EXTRA territories (not in expected):")
    for t in sorted(extra):
        print(f"  - {t}")

if not missing and not extra:
    print("\n✅ All expected territories present")
    
    # Check order
    mismatches = []
    for i, expected_t in enumerate(expected):
        if i < len(actual_territories):
            actual_t = actual_territories[i]
            if actual_t != expected_t:
                mismatches.append(f"Position {i+1}: expected '{expected_t}', got '{actual_t}'")
    
    if mismatches:
        print(f"\n❌ ORDER MISMATCHES:")
        for m in mismatches:
            print(f"  {m}")
    else:
        print("\n✅ Order is correct")
