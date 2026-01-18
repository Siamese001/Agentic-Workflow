import json
from collections import defaultdict

with open('agent_discovery_full.json') as f:
    data = json.load(f)

name_map = defaultdict(list)
for agent in data:
    name = agent.get('class_name', agent.get('name', 'Unknown'))
    path = agent.get('path', '')
    name_map[name].append(path)

duplicates = {name: paths for name, paths in name_map.items() if len(paths) > 1}

print(f"Found {len(duplicates)} duplicate agent names\n")
print("="*70)

for name in sorted(duplicates.keys()):
    paths = duplicates[name]
    print(f"\n{name}:")
    for path in paths:
        if 'apps_rg' in path:
            print(f"  [apps_rg] {path}")
        elif 'apps_lic' in path:
            print(f"  [apps_lic] {path}")
        else:
            print(f"  [core]    {path}")

apps_count = sum(1 for paths in duplicates.values() for p in paths if 'apps_' in p)
print(f"\n{'='*70}")
print(f"Total app agents needing renaming: {apps_count}")
