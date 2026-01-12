import json

with open('agent_discovery_full.json') as f:
    data = json.load(f)

l5_vals = [a for a in data if 'L5 Safety/Validators' in a.get('territory', '')]
no_base = [a for a in l5_vals if not a.get('proper_base_class')]

print(f'L5 Safety/Validators: {len(l5_vals)} agents')
print(f'Missing proper base: {len(no_base)}')
print()

for a in no_base:
    print(f"Agent: {a['name']}")
    print(f"  File: {a.get('file_path', 'N/A')}")
    print(f"  Inheritance: {a.get('inheritance', [])}")
    print()
