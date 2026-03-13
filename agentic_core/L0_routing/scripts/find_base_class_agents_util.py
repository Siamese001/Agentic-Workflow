"""Find all agents with 'Base Class' in their territory field."""

import json
from pathlib import Path

project_root = Path(__file__).parent.parent
discovery_file = project_root / "agent_discovery_full.json"
with open(discovery_file, encoding="utf-8") as f:
    agents = json.load(f)
base_class_agents = [a for a in agents if "Base Class" in a.get("territory", "")]
print(f"\n{'=' * 70}")
print(f"AGENTS WITH 'Base Class' IN TERRITORY: {len(base_class_agents)}")
print(f"{'=' * 70}\n")
for agent in base_class_agents:
    class_name = agent.get("class_name", "Unknown")
    territory = agent.get("territory", "Unknown")
    path = agent.get("path", "Unknown")
    print(f"Class: {class_name}")
    print(f"  Territory: {territory}")
    print(f"  Path: {path}")
    print()
print(f"{'=' * 70}")
print("TERRITORY NAMES TO FIX")
print(f"{'=' * 70}\n")
territory_mappings = {
    "Base/Base Class": "Sovereign Base Agent",
    "L6_Observability/Base Class": "L6_Observability/Base Agent",
    "L5 Safety/Base Class": "L5 Safety/Base Agent",
    "L4 State/Base Class": "L4 State/Base Agent",
    "L3 Orchestration/Base Class": "L3 Orchestration/Base Agent",
    "L2 Execution/Base Class": "L2 Execution/Base Agent",
    "L1 Cognition/Base Class": "L1 Cognition/Base Agent",
    "L0 Maintenance/Base Class": "L0 Maintenance/Base Agent",
}
for old, new in territory_mappings.items():
    count = sum(1 for a in agents if a.get("territory") == old)
    print(f"{old:40} → {new:40} ({count} agents)")
