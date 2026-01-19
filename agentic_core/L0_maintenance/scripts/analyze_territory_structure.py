"""
Analyze territory structure across L1-L5 layers.
Identify inconsistencies in how territories are reported.
"""
import re
import json
from pathlib import Path
from collections import defaultdict

dashboard_path = Path("reports/autonomy_dashboard.html")
html = dashboard_path.read_text(encoding='utf-8')

data_match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
rows = json.loads(data_match.group(1))

non_total = [r for r in rows if r.get('Territory') != 'TOTAL']

# Group by layer
layers = defaultdict(list)
for row in non_total:
    territory = row.get('Territory', '')
    
    # Extract layer (L0-L5)
    if territory.startswith('L5'):
        layer = 'L5'
    elif territory.startswith('L4'):
        layer = 'L4'
    elif territory.startswith('L3'):
        layer = 'L3'
    elif territory.startswith('L2'):
        layer = 'L2'
    elif territory.startswith('L1'):
        layer = 'L1'
    elif territory.startswith('L0'):
        layer = 'L0'
    else:
        layer = 'Other'
    
    layers[layer].append(territory)

print("=" * 80)
print("TERRITORY STRUCTURE ANALYSIS BY LAYER")
print("=" * 80)
print()

# Analyze each layer
for layer in ['L5', 'L4', 'L3', 'L2', 'L1', 'L0']:
    territories = layers.get(layer, [])
    print(f"\n{layer} Layer ({len(territories)} territories):")
    print("-" * 60)
    
    # Categorize by subterritory type
    categories = defaultdict(list)
    for terr in territories:
        # Extract category after layer prefix
        if '/' in terr:
            parts = terr.split('/')
            if len(parts) >= 2:
                category = parts[1]
                categories[category].append(terr)
        else:
            categories['No Subterritory'].append(terr)
    
    for category in sorted(categories.keys()):
        terrs = categories[category]
        print(f"  {category}: {len(terrs)}")
        for t in terrs:
            print(f"    - {t}")

print("\n" + "=" * 80)
print("BASE CLASS ANALYSIS")
print("=" * 80)

base_class_territories = [t for t in non_total if 'Base Cl' in t.get('Territory', '')]
print(f"\nFound {len(base_class_territories)} Base Class territories:")
for row in base_class_territories:
    terr = row.get('Territory')
    total = row.get('Total', 0)
    print(f"  - {terr}: {total} agents")

print("\n" + "=" * 80)
print("SUBTERRITORY CONSISTENCY CHECK")
print("=" * 80)

# Check which subterritory types appear in which layers
subterr_by_layer = defaultdict(set)
for row in non_total:
    territory = row.get('Territory', '')
    if '/' in territory:
        parts = territory.split('/')
        layer = parts[0]
        if len(parts) >= 2:
            subterr = parts[1]
            subterr_by_layer[subterr].add(layer)

print("\nSubterritory types and which layers they appear in:")
for subterr in sorted(subterr_by_layer.keys()):
    layers_list = sorted(subterr_by_layer[subterr])
    print(f"  {subterr}: {', '.join(layers_list)}")

print("\n" + "=" * 80)
print("INCONSISTENCIES DETECTED")
print("=" * 80)

inconsistencies = []

# Check 1: Base Class only in L1, L2
base_class_layers = set()
for row in base_class_territories:
    terr = row.get('Territory', '')
    if terr.startswith('L'):
        layer = terr.split()[0]
        base_class_layers.add(layer)

if base_class_layers:
    expected_layers = {'L1', 'L2', 'L3', 'L4', 'L5'}
    missing_layers = expected_layers - base_class_layers
    if missing_layers:
        inconsistencies.append({
            'type': 'Base Class Missing',
            'description': f"Base Class territories only in {sorted(base_class_layers)}, missing in {sorted(missing_layers)}",
            'severity': 'HIGH'
        })

# Check 2: Subterritories that appear in some layers but not others
common_subterrs = ['Core', 'Infrastructure', 'Specialized', 'Special']
for subterr in common_subterrs:
    layers_with = subterr_by_layer.get(subterr, set())
    if layers_with and len(layers_with) < 6:  # Not in all layers
        inconsistencies.append({
            'type': 'Subterritory Inconsistency',
            'description': f"{subterr} appears in {sorted(layers_with)} but not all layers",
            'severity': 'MEDIUM'
        })

# Check 3: Naming inconsistencies (Specialized vs Special, Infrastructure vs Infrast)
naming_variants = defaultdict(set)
for subterr in subterr_by_layer.keys():
    base = subterr.lower()[:6]  # First 6 chars
    naming_variants[base].add(subterr)

for base, variants in naming_variants.items():
    if len(variants) > 1:
        inconsistencies.append({
            'type': 'Naming Inconsistency',
            'description': f"Multiple naming variants: {sorted(variants)}",
            'severity': 'LOW'
        })

print(f"\nFound {len(inconsistencies)} inconsistencies:\n")
for i, issue in enumerate(inconsistencies, 1):
    print(f"{i}. [{issue['severity']}] {issue['type']}")
    print(f"   {issue['description']}")
    print()
