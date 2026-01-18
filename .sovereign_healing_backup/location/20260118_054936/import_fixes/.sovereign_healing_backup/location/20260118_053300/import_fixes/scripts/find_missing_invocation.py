"""Find agents missing super().heal_repository() invocation."""
import json
import re
from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
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

PROJECT_ROOT = Path(__file__).parent.parent

# Read the dashboard HTML to extract agent data
dashboard_path = PROJECT_ROOT / REPORTS_DIR / "autonomy_dashboard.html"
content = dashboard_path.read_text(encoding="utf-8")

# Find the embedded agent data - look for agentDataByTerritory
# Extract the JSON from: const agentDataByTerritory = {...}
match = re.search(r'const agentDataByTerritory\s*=\s*(\{.*?\});', content, re.DOTALL)
if match:
    try:
        agent_data = json.loads(match.group(1))
        print(f"Found agentDataByTerritory with {len(agent_data)} territories")
        
        # Count all agents and their invocation status
        total_agents = 0
        invocation_yes = 0
        invocation_no = 0
        invocation_inherited = 0
        
        missing_invocation_agents = []
        
        for territory, agents in agent_data.items():
            for agent in agents:
                total_agents += 1
                inv = agent.get('invocation', '')
                name = agent.get('name', 'Unknown')
                path = agent.get('path', '')
                
                if inv == 'Yes':
                    invocation_yes += 1
                elif inv == 'Inherited':
                    invocation_inherited += 1
                else:
                    invocation_no += 1
                    missing_invocation_agents.append({
                        'name': name,
                        'path': path,
                        'territory': territory
                    })
        
        print(f"\nTotal agents: {total_agents}")
        print(f"Invocation Yes: {invocation_yes}")
        print(f"Invocation Inherited: {invocation_inherited}")
        print(f"Invocation No/Missing: {invocation_no}")
        print(f"Invocation %: {(invocation_yes + invocation_inherited) / total_agents * 100:.1f}%")
        
        print(f"\n=== Agents MISSING invocation ({len(missing_invocation_agents)}) ===")
        for agent in sorted(missing_invocation_agents, key=lambda x: x['path']):
            print(f"  {agent['path']}")
            
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
else:
    print("Could not find agentDataByTerritory in dashboard")
    
    # Try alternative approach - find all invocation values
    all_invocations = re.findall(r'"invocation":\s*"([^"]*)"', content)
    print(f"\nFound {len(all_invocations)} invocation values via regex")
    from collections import Counter
    print(Counter(all_invocations))
    
    # Extract all agent objects - they appear as {...} blocks with "name", "path", "invocation"
    # Find the line with all agent data
    for line in content.split('\n'):
        if '"invocation": "No (missing super)"' in line and len(line) > 10000:
            # This line contains the embedded agent data
            # Extract individual agent objects
            agent_pattern = r'\{"name":\s*"([^"]+)"[^}]*"path":\s*"([^"]+)"[^}]*"invocation":\s*"([^"]+)"'
            matches = re.findall(agent_pattern, line)
            
            missing_paths = []
            for name, path, inv in matches:
                if 'No' in inv or 'missing' in inv:
                    missing_paths.append(path)
            
            print(f"\n=== Files needing super().heal_repository() ({len(missing_paths)}) ===")
            for path in sorted(set(missing_paths)):
                print(path)
            break
