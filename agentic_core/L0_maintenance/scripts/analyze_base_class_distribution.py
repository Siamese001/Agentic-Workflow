#!/usr/bin/env python3
"""Analyze where base class agents are distributed across territories"""
from pathlib import Path
import json

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

# Load agent discovery data
discovery_path = Path(AGENT_DISCOVERY_JSON)
if not discovery_path.exists():
    print("agent_discovery_full.json not found")
    exit(1)

with open(discovery_path) as f:
    discovery = json.load(f)

# Handle both list and dict formats
agents = discovery if isinstance(discovery, list) else discovery.get('agents', [])

print("Base Class Agent Analysis")
print("=" * 80)

# Find all agents that look like base classes
base_class_patterns = ['BaseAgent', 'Base', 'Mixin']
base_agents = []

for agent in agents:
    class_name = agent.get('class_name', '')
    file_path = agent.get('file', '')
    layer = agent.get('layer', 'Unknown')
    
    # Check if this is a base class
    is_base = False
    if 'base' in class_name.lower() and 'agent' in class_name.lower():
        is_base = True
    elif 'mixin' in class_name.lower():
        is_base = True
    elif 'BaseAgent' in class_name:
        is_base = True
    
    if is_base:
        base_agents.append({
            'class_name': class_name,
            'file': file_path,
            'layer': layer
        })

print(f"\nFound {len(base_agents)} base class agents in discovery:")
print("-" * 80)
for agent in base_agents:
    print(f"  {agent['layer']:5} | {agent['class_name']:40} | {agent['file']}")

# Now check dashboard data
print("\n" + "=" * 80)
print("Dashboard Territory Distribution:")
print("=" * 80)

html = Path('reports/autonomy_dashboard.html').read_text(encoding='utf-8')
start = html.find('const dashboardData = ') + 22
end = html.find('];', start) + 1
data = json.loads(html[start:end])

# Count agents per territory
print(f"\n{'Territory':<45} {'Count':>6}")
print("-" * 55)
for r in data:
    territory = r.get('Territory', 'N/A')
    total = r.get('Total', 0)
    if total > 0:
        print(f"{territory:<45} {total:>6}")

# Check which territories have base_class in their key
print("\n" + "=" * 80)
print("Territories with 'base_class' sub-territory (from config):")
print("=" * 80)
print("""
Expected base_class territories:
  - L5_safety/base_class (NOT defined - L5 uses folder-based only)
  - L4_state/base_class
  - L3_orchestration/base_class
  - L2_execution/base_class
  - L1_cognition/base_class
  - L0_maintenance/base_class
""")

# Check if base class agents are being classified correctly
print("\n" + "=" * 80)
print("Why only L1 Cognition/Base Class shows up:")
print("=" * 80)
print("""
The issue is that base class agents are being classified by:
1. Path matching (e.g., /L1_cognition/thought_engine/)
2. Sub-territory classification (_classify_subterritory)

For L1CognitionBaseAgent:
  - Path: agentic_core/L1_cognition/thought_engine/L1CognitionBaseAgent.py
  - Layer: L1
  - Sub-territory: base_class (because 'base' in name)
  - Result: Counted in L1_cognition/base_class territory

For other layers, the base class agents may not exist or may be in different locations.
""")
