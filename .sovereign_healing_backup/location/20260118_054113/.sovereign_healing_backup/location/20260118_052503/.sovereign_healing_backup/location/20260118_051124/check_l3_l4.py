import json

with open('C:/Git/Agentic-Workflow/agent_discovery_full.json', 'r') as f:
    data = json.load(f)

l3 = [a for a in data if a.get('layer', '').startswith('L3')]
l4 = [a for a in data if a.get('layer', '').startswith('L4')]

print(f'L3 agents in file: {len(l3)}')
print('Sample L3 agents:')
for a in l3[:5]:
    print(f'  {a["class_name"]}: layer={a.get("layer")}, sub_dir={a.get("sub_dir", "")}')

print(f'\nL4 agents in file: {len(l4)}')
print('Sample L4 agents:')
for a in l4[:5]:
    print(f'  {a["class_name"]}: layer={a.get("layer")}, sub_dir={a.get("sub_dir", "")}')
