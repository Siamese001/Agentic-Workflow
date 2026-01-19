"""Identify all duplicate agent names that need Rg/Lic prefixes."""
import json
from collections import defaultdict

with open('agent_discovery_full.json') as f:
    data = json.load(f)

# Group agents by class name
name_map = defaultdict(list)
for agent in data:
    name = agent.get('class_name', agent.get('name', 'Unknown'))
    path = agent.get('path', '')
    name_map[name].append(path)

# Find duplicates
duplicates = {name: paths for name, paths in name_map.items() if len(paths) > 1}

print(f"Found {len(duplicates)} duplicate agent names:\n")

for name, paths in sorted(duplicates.items()):
    print(f"\n{name}:")
    for path in paths:
        prefix = "  [apps_rg]" if 'apps_rg' in path else "  [apps_lic]" if 'apps_lic' in path else "  [core]   "
        print(f"{prefix} {path}")

# Identify which need renaming (apps only)
apps_to_rename = []
for name, paths in duplicates.items():
    for path in paths:
        if 'apps_rg' in path or 'apps_lic' in path:
            apps_to_rename.append((name, path))

print(f"\n\n{'='*70}")
print(f"TOTAL: {len(apps_to_rename)} app agents need renaming")
print(f"{'='*70}")
