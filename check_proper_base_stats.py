import json

with open('agent_discovery_full.json', 'r') as f:
    data = json.load(f)

total = len(data)
proper = sum(1 for a in data if a.get('proper_base_class'))
print(f'Total agents: {total}')
print(f'Proper base class: {proper} ({round(proper/total*100,1)}%)')
print(f'Not proper: {total-proper} ({round((total-proper)/total*100,1)}%)')

base_agents = [a for a in data if "Base Class" in a.get("territory", "")]
print(f'\nBase Class territory agents: {len(base_agents)}')
print(f'  With proper_base_class=True: {sum(1 for a in base_agents if a.get("proper_base_class"))}')
print(f'  With proper_base_class=False: {sum(1 for a in base_agents if not a.get("proper_base_class"))}')

# Sample some that should be proper
print("\nSample base class agents:")
for a in base_agents[:3]:
    print(f"  {a['class_name']}: proper_base_class={a.get('proper_base_class')}")

# Check agents with canonical mixins
mcp_agents = [a for a in data if 'MCPHardenedMixin' in a.get('inheritance', [])]
print(f'\nAgents with MCPHardenedMixin: {len(mcp_agents)}')
print(f'  With proper_base_class=True: {sum(1 for a in mcp_agents if a.get("proper_base_class"))}')
