"""
Analyze agent_discovery_full.json for suspected non-agents.

This script identifies entries that may be misclassified as Sovereign Agents:
- Scripts (files in scripts/ directories)
- Mixins (class names containing 'Mixin')
- Data classes (no Agent suffix, no heal_repository)
- Utilities (in utils/ directories)
"""
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_JSON = PROJECT_ROOT / 'agent_discovery_full.json'

def analyze_suspects():
    """Analyze discovery JSON for suspected non-agents."""
    with open(DISCOVERY_JSON, encoding='utf-8') as f:
        agents = json.load(f)
    print(f'Total entries in agent_discovery_full.json: {len(agents)}')
    print('=' * 80)
    suspects = {'scripts': [], 'mixins': [], 'utils': [], 'no_agent_suffix': [], 'no_healing': [], 'clients': [], 'data_classes': []}
    for agent in agents:
        path = agent.get('path', '').replace('\\', '/').lower()
        name = agent.get('class_name', '')
        has_healing = agent.get('has_healing', False)
        agent.get('inheritance', [])
        if '/scripts/' in path:
            suspects['scripts'].append(agent)
        if 'Mixin' in name:
            suspects['mixins'].append(agent)
        if '/utils/' in path:
            suspects['utils'].append(agent)
        if not name.endswith('Agent'):
            suspects['no_agent_suffix'].append(agent)
        if name.endswith('Client'):
            suspects['clients'].append(agent)
        if not has_healing and (not name.endswith('Agent')):
            suspects['data_classes'].append(agent)
    for category, items in suspects.items():
        if items:
            print(f'\n{category.upper()} ({len(items)} entries):')
            print('-' * 60)
            for item in items[:15]:
                print(f"  {item['class_name']}")
                print(f"    Path: {item['path']}")
                print(f"    Layer: {item.get('layer', 'unknown')}")
                print(f"    Has Healing: {item.get('has_healing', False)}")
                print(f"    Inheritance: {item.get('inheritance', [])[:3]}")
            if len(items) > 15:
                print(f'  ... and {len(items) - 15} more')
    print('\n' + '=' * 80)
    print('SUMMARY OF POTENTIAL MISCLASSIFICATIONS:')
    print('=' * 80)
    all_suspect_names = set()
    for _category, items in suspects.items():
        for item in items:
            all_suspect_names.add(item['class_name'])
    print(f'Total unique suspects: {len(all_suspect_names)}')
    print(f"  - In scripts/: {len(suspects['scripts'])}")
    print(f"  - Mixins: {len(suspects['mixins'])}")
    print(f"  - In utils/: {len(suspects['utils'])}")
    print(f"  - No 'Agent' suffix: {len(suspects['no_agent_suffix'])}")
    print(f"  - Clients: {len(suspects['clients'])}")
    print('\n' + '-' * 80)
    print('ALL UNIQUE SUSPECTS (for exclusion filter):')
    print('-' * 80)
    for name in sorted(all_suspect_names):
        matching = [a for a in agents if a['class_name'] == name][0]
        print(f"  {name}: {matching['path']}")
    return suspects
if __name__ == '__main__':
    analyze_suspects()
