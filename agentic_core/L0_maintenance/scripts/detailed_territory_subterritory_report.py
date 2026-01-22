from pathlib import Path
"""Generate detailed agent report by territory and sub-territory."""
import json
PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / 'agent_discovery_full.json', 'r') as f:
    agents = json.load(f)
by_territory = defaultdict(list)
for agent in agents:
    territory = agent.get('territory', 'Unknown')
    by_territory[territory].append(agent)
territory_groups = {'L0': [], 'L1': [], 'L2': [], 'L3': [], 'L4': [], 'L5': [], 'L6': [], 'Apps Lic': [], 'Apps Rg': [], 'Apps Shared': [], 'Other': []}
for territory in sorted(by_territory.keys()):
    if territory.startswith('L0'):
        territory_groups['L0'].append(territory)
    elif territory.startswith('L1'):
        territory_groups['L1'].append(territory)
    elif territory.startswith('L2'):
        territory_groups['L2'].append(territory)
    elif territory.startswith('L3'):
        territory_groups['L3'].append(territory)
    elif territory.startswith('L4'):
        territory_groups['L4'].append(territory)
    elif territory.startswith('L5'):
        territory_groups['L5'].append(territory)
    elif territory.startswith('L6'):
        territory_groups['L6'].append(territory)
    elif territory.startswith('Apps Lic'):
        territory_groups['Apps Lic'].append(territory)
    elif territory.startswith('Apps Rg'):
        territory_groups['Apps Rg'].append(territory)
    elif territory.startswith('Apps Shared'):
        territory_groups['Apps Shared'].append(territory)
    else:
        territory_groups['Other'].append(territory)
group_titles = {'L0': 'L0 - MAINTENANCE', 'L1': 'L1 - COGNITION', 'L2': 'L2 - EXECUTION', 'L3': 'L3 - ORCHESTRATION', 'L4': 'L4 - STATE', 'L5': 'L5 - SAFETY', 'L6': 'L6 - OBSERVABILITY', 'Apps Lic': 'APPS - LIC (LinkedIn/Outreach)', 'Apps Rg': 'APPS - RG (Resume)', 'Apps Shared': 'APPS - SHARED', 'Other': 'OTHER'}
total_by_group = {}
for group_key in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'Apps Lic', 'Apps Rg', 'Apps Shared', 'Other']:
    territories = territory_groups[group_key]
    if not territories:
        continue
    group_total = sum((len(by_territory[t]) for t in territories))
    total_by_group[group_key] = group_total
    for territory in sorted(territories):
        agents_list = by_territory[territory]
        if '/' in territory:
            sub = territory.split('/', 1)[1]
        else:
            sub = territory
        for a in sorted(agents_list, key=lambda x: x['class_name']):
            name = a['class_name']
            category = a.get('category', '-')[:10]
            healing = 'H' if a.get('has_healing') else '-'
            mcp = 'M' if a.get('mcp_hardened') else '-'
            subatomic = 'S' if a.get('has_subatomic') else '-'
            loc = a.get('loc', 0)
grand_total = 0
for group_key in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'Apps Lic', 'Apps Rg', 'Apps Shared', 'Other']:
    if group_key in total_by_group:
        count = total_by_group[group_key]
        grand_total += count
        bar = '#' * (count // 3)
for territory in sorted(by_territory.keys()):
    count = len(by_territory[territory])
