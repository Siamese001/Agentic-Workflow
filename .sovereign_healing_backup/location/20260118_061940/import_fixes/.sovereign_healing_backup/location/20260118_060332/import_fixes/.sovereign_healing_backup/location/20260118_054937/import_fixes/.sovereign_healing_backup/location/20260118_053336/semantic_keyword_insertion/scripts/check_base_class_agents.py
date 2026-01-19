"""
Check which base class agents exist in L1-L5 and if they're being reported.
"""
import json
import sys
from pathlib import Path

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

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load agent discovery
discovery_path = project_root / AGENT_DISCOVERY_JSON
if not discovery_path.exists():
    print("❌ agent_discovery_full.json not found")
    exit(1)

with open(discovery_path, 'r', encoding='utf-8') as f:
    agents = json.load(f)

print("=" * 80)
print("BASE CLASS AGENTS IN CODEBASE")
print("=" * 80)
print()

# Find all base class agents
base_agents = {}
for agent in agents:
    rel_path = agent.get('relative_path', '')
    class_name = agent.get('class_name', '')
    
    # Check if it's a base class agent
    if 'BaseAgent' in class_name or 'base' in rel_path.lower():
        # Determine layer
        if rel_path.startswith('agentic_core/L5'):
            layer = 'L5'
        elif rel_path.startswith('agentic_core/L4'):
            layer = 'L4'
        elif rel_path.startswith('agentic_core/L3'):
            layer = 'L3'
        elif rel_path.startswith('agentic_core/L2'):
            layer = 'L2'
        elif rel_path.startswith('agentic_core/L1'):
            layer = 'L1'
        elif rel_path.startswith('agentic_core/L0'):
            layer = 'L0'
        else:
            layer = 'Other'
        
        if layer not in base_agents:
            base_agents[layer] = []
        base_agents[layer].append({
            'class': class_name,
            'path': rel_path
        })

# Print findings
for layer in ['L5', 'L4', 'L3', 'L2', 'L1', 'L0']:
    agents_list = base_agents.get(layer, [])
    print(f"{layer} Base Class Agents: {len(agents_list)}")
    for agent in agents_list:
        print(f"  - {agent['class']}")
        print(f"    {agent['path']}")
    print()

# Load dashboard data
dashboard_path = project_root / REPORTS_DIR / "autonomy_dashboard.html"
if dashboard_path.exists():
    import re
    html = dashboard_path.read_text(encoding='utf-8')
    data_match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
    if data_match:
        rows = json.loads(data_match.group(1))
        
        print("=" * 80)
        print("BASE CLASS TERRITORIES IN DASHBOARD")
        print("=" * 80)
        print()
        
        base_class_rows = [r for r in rows if 'Base Cl' in r.get('Territory', '')]
        for row in base_class_rows:
            terr = row.get('Territory')
            total = row.get('Total', 0)
            agents_list = row.get('agents', [])
            print(f"{terr}: {total} agents")
            for agent in agents_list:
                print(f"  - {agent.get('rel', 'unknown')}")
            print()
        
        print("=" * 80)
        print("RECONCILIATION")
        print("=" * 80)
        print()
        
        # Check which layers have base agents in codebase but not in dashboard
        for layer in ['L5', 'L4', 'L3', 'L2', 'L1', 'L0']:
            has_in_code = len(base_agents.get(layer, [])) > 0
            has_in_dashboard = any(row.get('Territory', '').startswith(layer) and 'Base Cl' in row.get('Territory', '') for row in base_class_rows)
            
            if has_in_code and not has_in_dashboard:
                print(f"⚠️  {layer}: Has base agents in code but NOT in dashboard")
                for agent in base_agents.get(layer, []):
                    print(f"     - {agent['class']}")
            elif has_in_code and has_in_dashboard:
                print(f"✅ {layer}: Base agents in both code and dashboard")
            elif not has_in_code and not has_in_dashboard:
                print(f"ℹ️  {layer}: No base agents (consistent)")
            else:
                print(f"❓ {layer}: In dashboard but not in code (unexpected)")
