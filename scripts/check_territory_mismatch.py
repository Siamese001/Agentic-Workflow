#!/usr/bin/env python3
"""Check for territory mismatches between dashboard_data.js and agent_data.js"""
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DASHBOARD_DATA_FILE = PROJECT_ROOT / "agentic_core/L6_observability/dashboards/data/dashboard_data.js"
AGENT_DATA_FILE = PROJECT_ROOT / "agentic_core/L6_observability/dashboards/data/agent_data.js"

def main():
    print("=" * 70)
    print("CHECKING TERRITORY MISMATCHES")
    print("=" * 70)
    
    # Load dashboard_data.js
    content = DASHBOARD_DATA_FILE.read_text(encoding='utf-8')
    match = re.search(r'window\.dashboardData = (\[.*?\]);', content, re.DOTALL)
    dashboard_data = json.loads(match.group(1))
    dashboard_territories = {row['Territory'] for row in dashboard_data}
    
    # Load agent_data.js
    content = AGENT_DATA_FILE.read_text(encoding='utf-8')
    match = re.search(r'window\.realAgentData = (\{.*\});', content, re.DOTALL)
    agent_data = json.loads(match.group(1))
    agent_territories = set(agent_data.keys())
    
    print(f"\nDashboard territories: {len(dashboard_territories)}")
    print(f"Agent data territories: {len(agent_territories)}")
    
    # Find mismatches
    in_dashboard_not_agent = dashboard_territories - agent_territories
    in_agent_not_dashboard = agent_territories - dashboard_territories
    
    print(f"\nIn dashboard_data.js but NOT in agent_data.js: {len(in_dashboard_not_agent)}")
    for t in sorted(in_dashboard_not_agent):
        print(f"  - '{t}'")
    
    print(f"\nIn agent_data.js but NOT in dashboard_data.js: {len(in_agent_not_dashboard)}")
    for t in sorted(in_agent_not_dashboard):
        print(f"  - '{t}'")
    
    # TOTAL is expected to be in dashboard but not agent_data (it's a summary row)
    expected_dashboard_only = {'TOTAL'}
    actual_mismatches = in_dashboard_not_agent - expected_dashboard_only
    
    if not actual_mismatches and not in_agent_not_dashboard:
        print("\n✅ All territories match between files (TOTAL row excluded as expected)")
    else:
        print("\n⚠️  Territory mismatches found - this causes 'No Agent data available' tooltips")
        if actual_mismatches:
            print(f"   Unexpected in dashboard only: {actual_mismatches}")

if __name__ == "__main__":
    main()
