#!/usr/bin/env python3
"""
Fix Base Agent naming convention in agent_discovery_full.json.
- "Base/Base Class" → "Sovereign Base Agent"
- "L6_Observability/Base Class" → "L6_Observability/Base Agent"
- "L5 Safety/Base Class" → "L5 Safety/Base Agent"
- etc. for all layers L0-L6
"""
import json
from pathlib import Path
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

project_root = Path(__file__).parent.parent
discovery_file = project_root / "agent_discovery_full.json"

# Load data
with open(discovery_file, 'r', encoding='utf-8') as f:
    agents = json.load(f)

print(f"Loaded {len(agents)} agents")

# Define territory name mappings
TERRITORY_MAPPINGS = {
    'Base/Base Class': 'Sovereign Base Agent',
    'L6_Observability/Base Class': 'L6_Observability/Base Agent',
    'L5 Safety/Base Class': 'L5 Safety/Base Agent',
    'L4 State/Base Class': 'L4 State/Base Agent',
    'L3 Orchestration/Base Class': 'L3 Orchestration/Base Agent',
    'L2 Execution/Base Class': 'L2 Execution/Base Agent',
    'L1 Cognition/Base Class': 'L1 Cognition/Base Agent',
    'L0 Maintenance/Base Class': 'L0 Maintenance/Base Agent'
}

# Apply mappings
changes = []
for agent in agents:
    old_territory = agent.get('territory')
    if old_territory in TERRITORY_MAPPINGS:
        new_territory = TERRITORY_MAPPINGS[old_territory]
        agent['territory'] = new_territory
        changes.append(f"{old_territory} → {new_territory}")

print(f"\nApplied {len(changes)} territory name changes:")
for change in sorted(set(changes)):
    count = changes.count(change)
    print(f"  {change} ({count} agents)")

# Save updated data
with open(discovery_file, 'w', encoding='utf-8') as f:
    json.dump(agents, f, indent=2, ensure_ascii=False)

print(f"\n✅ Updated {discovery_file}")
print("Now regenerate dashboard data with: python scripts/regenerate_dashboard_data.py")
