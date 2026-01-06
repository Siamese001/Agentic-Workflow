"""Check if all discovered agents end with 'Agent' suffix."""
import json

data = json.load(open('agent_discovery_full.json'))

non_agent = [d['class_name'] for d in data if not d['class_name'].endswith('Agent')]

print(f'Total agents: {len(data)}')
print(f'Agents ending with "Agent": {len(data) - len(non_agent)}')
print(f'Classes NOT ending with "Agent": {len(non_agent)}')
print()

if non_agent:
    print('Classes without Agent suffix:')
    for name in sorted(non_agent):
        # Find the entry to show path
        entry = next((d for d in data if d['class_name'] == name), None)
        if entry:
            print(f'  {name} - {entry.get("path", "unknown")}')
