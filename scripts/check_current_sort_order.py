#!/usr/bin/env python3
"""Check current sort order in dashboard_data.js"""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"

content = data_file.read_text(encoding='utf-8')
lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
content = '\n'.join(lines)
content = content.replace('window.dashboardData = ', '').strip().rstrip(';')

data = json.loads(content)

print("\nCURRENT SORT ORDER IN dashboard_data.js:")
print("="*60)
for i, row in enumerate(data, 1):
    print(f"{i:2}. {row['Territory']}")

print("\n\nEXPECTED SORT ORDER:")
print("="*60)
expected = [
    "TOTAL",
    "Base/Base Class",  # or SovereignBaseAgent
    "L6_Observability/Metrics",
    "L6_Observability/Telemetry", 
    "L6_Observability/Base Class",
    "L5 Safety/Validators",
    "L5 Safety/Guardrails",
    "L5 Safety/Red Teaming",
    "L5 Safety/Gravity",
    "L5 Safety/Base Class",
    "L4 State/Infrastructure",
    "L4 State/Core",
    "L4 State/Base Class",
    "L3 Orchestration/Core",
    "L3 Orchestration/Base Class",
    "L2 Execution/Core",
    "L2 Execution/Base Class",
    "L1 Cognition/Core",
    "L1 Cognition/Base Class",
    "L0 Maintenance/Core",
    "L0 Maintenance/Base Class",
    "Apps Rg",
    "Apps Lic",
    "Apps Shared",
    "Utils"
]

for i, territory in enumerate(expected, 1):
    print(f"{i:2}. {territory}")
