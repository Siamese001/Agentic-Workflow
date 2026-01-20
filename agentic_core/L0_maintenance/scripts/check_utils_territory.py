#!/usr/bin/env python3
"""
Check for Utils territory in agent discovery and dashboard data.
"""
import json
import re
from pathlib import Path
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"
DASHBOARD_DATA = PROJECT_ROOT / "agentic_core/L6_observability/dashboards/data/dashboard_data.js"

def main():
    """Check Utils territory."""
    print("=" * 70)
    print("UTILS TERRITORY RCA")
    print("=" * 70)
    
    # Check agent discovery
    with open(DISCOVERY_FILE, 'r', encoding='utf-8') as f:
        agents = json.load(f)
    
    utils_agents = [a for a in agents if a.get('territory') == 'Utils']
    apps_shared_agents = [a for a in agents if a.get('territory') == 'Apps Shared']
    
    print(f"\nAgent Discovery:")
    print(f"  Agents with 'Utils' territory: {len(utils_agents)}")
    print(f"  Agents with 'Apps Shared' territory: {len(apps_shared_agents)}")
    
    if utils_agents:
        print(f"\nAgents marked as 'Utils':")
        for agent in utils_agents[:20]:
            print(f"  - {agent['class_name']}")
            print(f"    Path: {agent['path']}")
    
    # Check dashboard data
    content = DASHBOARD_DATA.read_text(encoding='utf-8')
    match = re.search(r'window\.dashboardData = (\[.*?\]);', content, re.DOTALL)
    if match:
        data = json.loads(match.group(1))
        
        utils_row = next((r for r in data if r.get('Territory') == 'Utils'), None)
        apps_shared_row = next((r for r in data if r.get('Territory') == 'Apps Shared'), None)
        
        print(f"\nDashboard Data:")
        if utils_row:
            print(f"  ✗ 'Utils' row found: {utils_row.get('Total', 0)} agents")
        else:
            print(f"  ✓ No 'Utils' row")
        
        if apps_shared_row:
            print(f"  ✓ 'Apps Shared' row found: {apps_shared_row.get('Total', 0)} agents")
        else:
            print(f"  ✗ No 'Apps Shared' row")
    
    print("\n" + "=" * 70)
    print("RCA CONCLUSION:")
    print("=" * 70)
    
    if utils_agents:
        print(f"\n{len(utils_agents)} agents are marked with 'Utils' territory")
        print("These should be 'Apps Shared' territory")
        print("\nRoot cause: Agent discovery is assigning 'Utils' instead of 'Apps Shared'")
        print("Fix: Update territory mapping in agent discovery script")
    else:
        print("\nNo agents with 'Utils' territory in discovery data")
        print("Issue may be in dashboard data generation")

if __name__ == "__main__":
    main()
