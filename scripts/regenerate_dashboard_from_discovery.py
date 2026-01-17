#!/usr/bin/env python3
"""
[DEPRECATED] This script is deprecated. Use regenerate_dashboard_full.py instead.

DEPRECATION REASON: This script attempts to parse JSON from HTML which fails.
It does not use SSOT definitions for calculations.

CANONICAL SSOT: scripts/regenerate_dashboard_full.py
"""
import sys
print("[DEPRECATED] This script is deprecated. Use regenerate_dashboard_full.py instead.")
sys.exit(1)

# Original code below for reference:
"""
Regenerate dashboard territory data from agent_discovery_full.json.

This ensures dashboard data matches the source of truth.
"""
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_PATH = PROJECT_ROOT / 'agent_discovery_full.json'
DASHBOARD_PATH = PROJECT_ROOT / 'agentic_core' / 'L6_observability' / 'dashboards' / 'autonomy_dashboard.html'


def main():
    print("=" * 70)
    print("Regenerating dashboard territory data from agent_discovery_full.json")
    print("=" * 70)
    
    # Load agent discovery
    with open(DISCOVERY_PATH, 'r', encoding='utf-8') as f:
        agents = json.load(f)
    
    print(f"Loaded {len(agents)} agents from discovery")
    
    # Group agents by territory
    territory_agents = defaultdict(list)
    for agent in agents:
        territory = agent.get('territory', 'Unknown')
        territory_agents[territory].append(agent)
    
    print(f"Found {len(territory_agents)} territories")
    
    # Load dashboard
    content = DASHBOARD_PATH.read_text(encoding='utf-8')
    
    # Extract dashboardData JSON
    start_marker = 'const dashboardData = ['
    end_marker = '];'
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx) + len(end_marker)
    
    json_str = content[start_idx + len(start_marker) - 1:end_idx - 1]
    territories = json.loads(json_str)
    
    # Territory name mapping (discovery -> dashboard)
    territory_mapping = {
        'Base/Base Class': 'Base/Root',
        'L0 Maintenance/Base Class': 'L0 Maintenance/Base Agent',
        'L1 Cognition/Base Class': 'L1 Cognition/Base Agent',
        'L2 Execution/Base Class': 'L2 Execution/Base Agent',
        'L3 Orchestration/Base Class': 'L3 Orchestration/Base Agent',
        'L4 State/Base Class': 'L4 State/Base Agent',
        'L5 Safety/Base Class': 'L5 Safety/Base Agent',
        'L6_Observability/Base Class': 'L6 Observability/Base Agent',
        'L6_Observability/Metrics': 'L6 Observability/Metrics',
        'L6_Observability/Telemetry': 'L6 Observability/Infrastructure',
        'L1/Prompt_Governance': 'L1 Cognition/Core',  # Merge into L1 Core
        'Utils': 'Apps Shared',  # Merge Utils into Apps Shared
    }
    
    # Normalize territory names in agents
    normalized_agents = defaultdict(list)
    for territory, agent_list in territory_agents.items():
        mapped_name = territory_mapping.get(territory, territory)
        normalized_agents[mapped_name].extend(agent_list)
    
    # Update each territory with actual agent counts
    updated = 0
    for territory in territories:
        name = territory.get('Territory')
        if name == 'TOTAL':
            # Update TOTAL row
            territory['Total'] = len(agents)
            territory['Compliant'] = len(agents)
            updated += 1
            continue
        
        # Find matching agents for this territory
        matching_agents = normalized_agents.get(name, [])
        if matching_agents:
            old_total = territory.get('Total', 0)
            new_total = len(matching_agents)
            if old_total != new_total:
                territory['Total'] = new_total
                territory['Compliant'] = new_total
                print(f"  {name}: {old_total} -> {new_total}")
                updated += 1
    
    # Reconstruct JSON
    new_json = json.dumps(territories, indent=2)
    
    # Replace in content
    new_content = content[:start_idx + len(start_marker) - 1] + new_json + content[end_idx - 1:]
    
    DASHBOARD_PATH.write_text(new_content, encoding='utf-8')
    
    print(f"\n✅ Updated {updated} territories")
    print("Dashboard regenerated!")
    
    return 0


if __name__ == "__main__":
    main()
