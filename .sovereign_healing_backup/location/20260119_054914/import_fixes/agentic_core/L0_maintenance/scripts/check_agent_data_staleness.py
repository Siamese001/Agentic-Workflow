#!/usr/bin/env python3
"""Check for stale data in agent_data.js vs agent_discovery_full.json"""
import json
import re
from pathlib import Path
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"
AGENT_DATA_FILE = PROJECT_ROOT / "agentic_core/L6_observability/dashboards/data/agent_data.js"

def main():
    print("=" * 70)
    print("CHECKING AGENT DATA STALENESS")
    print("=" * 70)
    
    # Load discovery data
    with open(DISCOVERY_FILE, 'r', encoding='utf-8') as f:
        discovery = json.load(f)
    
    discovery_by_name = {a['class_name']: a for a in discovery}
    
    # Load agent_data.js
    content = AGENT_DATA_FILE.read_text(encoding='utf-8')
    match = re.search(r'window\.realAgentData = (\{.*\});', content, re.DOTALL)
    agent_data = json.loads(match.group(1))
    
    # Check for mismatches
    mismatches = []
    
    for territory, territory_data in agent_data.items():
        for agent in territory_data.get('agents', []):
            name = agent.get('name')
            if name in discovery_by_name:
                disc_agent = discovery_by_name[name]
                
                # Check has_tests mismatch
                ad_has_tests = agent.get('has_tests', False)
                disc_has_tests = disc_agent.get('has_tests', False)
                
                if ad_has_tests != disc_has_tests:
                    mismatches.append({
                        'agent': name,
                        'field': 'has_tests',
                        'agent_data': ad_has_tests,
                        'discovery': disc_has_tests
                    })
    
    print(f"\nDiscovery agents: {len(discovery)}")
    print(f"Agent data territories: {len(agent_data)}")
    print(f"\nMismatches found: {len(mismatches)}")
    
    if mismatches:
        print("\nMismatched agents:")
        for m in mismatches[:20]:
            print(f"  - {m['agent']}: {m['field']} = {m['agent_data']} (should be {m['discovery']})")
        if len(mismatches) > 20:
            print(f"  ... and {len(mismatches) - 20} more")
    else:
        print("\n✅ No mismatches - data is in sync")

if __name__ == "__main__":
    main()
