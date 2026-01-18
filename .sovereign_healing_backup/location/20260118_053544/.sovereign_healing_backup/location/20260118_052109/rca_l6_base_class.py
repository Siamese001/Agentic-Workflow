#!/usr/bin/env python3
"""RCA: Why L6 Base Class row went missing from dashboard."""
import json
import re
from pathlib import Path

print("=" * 80)
print("RCA: L6 BASE CLASS MISSING FROM DASHBOARD")
print("=" * 80)

# 1. Check current dashboard territories
print("\n1. CURRENT DASHBOARD TERRITORIES")
print("-" * 80)

dashboard_path = Path('C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
with open(dashboard_path, 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
data = json.loads(match.group(1))

territories = [r['Territory'] for r in data]
print(f"Total territories: {len(territories)}")
for t in territories:
    is_l6 = 'L6' in t
    print(f"  {'*' if is_l6 else ' '} {t}")

# Check for L6 Base Class
l6_base_territories = [t for t in territories if 'L6' in t and 'Base' in t]
print(f"\nL6 Base Class territories: {l6_base_territories}")

# 2. Check agent discovery for L6 base agents
print("\n2. L6 AGENTS IN DISCOVERY DATA")
print("-" * 80)

with open('C:/Git/Agentic-Workflow/agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

# Find L6 agents
l6_agents = [a for a in agents if 'L6' in a.get('layer', '') or 'L6_observability' in a.get('path', '').lower()]
print(f"Total L6 agents: {len(l6_agents)}")

# Find L6 base agents
l6_base_agents = [a for a in l6_agents if 'BaseAgent' in a.get('class_name', '')]
print(f"L6 Base Agents: {len(l6_base_agents)}")

for a in l6_base_agents:
    print(f"  - {a['class_name']}")
    print(f"    Path: {a['path']}")
    print(f"    Layer: {a.get('layer', 'UNKNOWN')}")
    print(f"    Territory: {a.get('territory', 'UNKNOWN')}")

# 3. Check TERRITORY_ORDER in generate_dashboard.py
print("\n3. TERRITORY_ORDER IN GENERATE_DASHBOARD.PY")
print("-" * 80)

gen_path = Path('C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/generate_dashboard.py')
with open(gen_path, 'r', encoding='utf-8') as f:
    gen_content = f.read()

# Extract TERRITORY_ORDER
territory_match = re.search(r'TERRITORY_ORDER = \[(.*?)\]', gen_content, re.DOTALL)
if territory_match:
    territory_list = territory_match.group(1)
    l6_territories = [t.strip().strip('"').strip("'") for t in territory_list.split(',') if 'L6' in t]
    print(f"L6 territories in TERRITORY_ORDER:")
    for t in l6_territories:
        print(f"  - {t}")
    
    # Check if L6 Base Class is in the list
    if 'L6_Observability/Base Class' in territory_list or 'L6 Observability/Base Class' in territory_list:
        print("\n✅ L6 Base Class IS in TERRITORY_ORDER")
    else:
        print("\n❌ L6 Base Class is NOT in TERRITORY_ORDER!")
        print("   This is why it's missing from the dashboard!")

# 4. Check territory mapping logic
print("\n4. TERRITORY MAPPING LOGIC")
print("-" * 80)

# Check what territory L6ObservabilityBaseAgent would be mapped to
for a in l6_base_agents:
    path = a.get('path', '').replace('\\', '/')
    class_name = a.get('class_name', '')
    layer = a.get('layer', '')
    
    print(f"Agent: {class_name}")
    print(f"  Path: {path}")
    print(f"  Layer: {layer}")
    
    # Simulate mapping logic
    if 'L6_observability' in path or 'L6_Observability' in path:
        if '/metrics' in path or 'Metric' in class_name:
            mapped = "L6_Observability/Metrics"
        elif '/telemetry' in path or 'Telemetry' in class_name:
            mapped = "L6_Observability/Telemetry"
        elif '/tracing' in path or 'Tracing' in class_name or 'Trace' in class_name:
            mapped = "L6_Observability/Tracing"
        elif '/compliance' in path or 'Compliance' in class_name:
            mapped = "L6_Observability/Compliance"
        elif 'BaseAgent' in class_name:
            mapped = "L6_Observability/Base Class (SHOULD BE)"
        else:
            mapped = "L6_Observability/Metrics (default)"
    else:
        mapped = "Unknown"
    
    print(f"  Should map to: {mapped}")
    
    # But the actual logic in the file doesn't check for BaseAgent for L6!
    if 'BaseAgent' in class_name and 'L6' in path:
        print(f"  ❌ BUG: L6 territory mapping doesn't check for BaseAgent!")
        print(f"     The L6 block doesn't have 'if BaseAgent in class_name' check")

print("\n" + "=" * 80)
print("ROOT CAUSE ANALYSIS COMPLETE")
print("=" * 80)
print("""
FINDING: The L6 territory mapping logic in generate_dashboard.py
does NOT check for 'BaseAgent' in the class name like other layers do.

Other layers have this pattern:
    if 'BaseAgent' in class_name or 'base_class' in path.lower():
        territory = "Lx Layer/Base Class"
        
But L6 block only checks:
    if '/metrics' in path or 'Metric' in class_name:
        territory = "L6_Observability/Metrics"
    ...
    else:
        territory = "L6_Observability/Metrics"  # Default L6

L6ObservabilityBaseAgent falls through to the default case!

FIX REQUIRED:
1. Add 'L6_Observability/Base Class' to TERRITORY_ORDER
2. Add BaseAgent check to L6 territory mapping logic
""")
