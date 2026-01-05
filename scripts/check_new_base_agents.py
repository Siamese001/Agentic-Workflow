"""Check which BaseAgent classes are now discovered."""
import json

with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

base_agents = [a for a in agents if 'BaseAgent' in a.get('class_name', '')]
print(f"Found {len(base_agents)} BaseAgent classes:")
for a in base_agents:
    path = a.get('relative_path') or a.get('path') or a.get('file_path', 'unknown')
    print(f"  {a['class_name']}: {path}")
