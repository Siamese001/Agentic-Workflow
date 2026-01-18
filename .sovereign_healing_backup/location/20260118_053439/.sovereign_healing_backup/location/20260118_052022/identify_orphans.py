#!/usr/bin/env python3
"""Identify orphaned agents (no inheritance) from discovery data."""
import json
from pathlib import Path
from collections import defaultdict

discovery_file = Path("agent_discovery_full.json")
data = json.loads(discovery_file.read_text())

# Find orphans
orphans = [a for a in data if not a.get('inheritance') or len(a.get('inheritance', [])) == 0]

print(f"Total orphans: {len(orphans)}\n")
print("=" * 80)

# Categorize by pattern
categories = defaultdict(list)
for agent in sorted(orphans, key=lambda x: x['class_name']):
    name = agent['class_name']
    path = agent['path']
    
    # Categorize
    if name.startswith('Test'):
        categories['Test Fixtures'].append((name, path))
    elif 'Validator' in name or 'Enforcer' in name:
        categories['Validators/Enforcers'].append((name, path))
    elif 'Detector' in name or 'Analyzer' in name:
        categories['Detectors/Analyzers'].append((name, path))
    elif 'Exerciser' in name:
        categories['Exercisers'].append((name, path))
    elif 'apps_' in path:
        categories['App-Specific'].append((name, path))
    else:
        categories['Other'].append((name, path))

# Print by category
for category, agents in sorted(categories.items()):
    print(f"\n{category} ({len(agents)} agents):")
    print("-" * 80)
    for name, path in agents:
        print(f"  {name}")
        print(f"    → {path}")
