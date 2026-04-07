"""
RCA: Agent Count Drop Analysis
Compares current discovery vs backup to identify missing agents
"""
import json
from pathlib import Path


def main():
    current_path = Path('agent_discovery_full.json')
    backup_path = Path('agent_discovery_full.json.backup_phase3')
    with open(current_path, encoding='utf-8') as f:
        current = json.load(f)
    with open(backup_path, encoding='utf-8') as f:
        backup = json.load(f)
    current_agents = current if isinstance(current, list) else current.get('agents', [])
    backup_agents = backup if isinstance(backup, list) else backup.get('agents', [])

    def get_name(a):
        return a.get('class_name') or a.get('name') or 'unknown'
    current_names = {get_name(a) for a in current_agents}
    backup_names = {get_name(a) for a in backup_agents}
    missing = backup_names - current_names
    new_agents = current_names - backup_names
    print(f'Current: {len(current_agents)} agents')
    print(f'Backup (Phase 3): {len(backup_agents)} agents')
    print(f'Missing: {len(missing)} agents')
    print(f'New: {len(new_agents)} agents')
    print('\n=== MISSING AGENTS ===')
    missing_details = []
    for name in sorted(missing):
        for a in backup_agents:
            if get_name(a) == name:
                missing_details.append({'name': name, 'path': a.get('rel_path', 'unknown'), 'layer': a.get('layer', 'unknown')})
                print(f"  - {name}: {a.get('rel_path', 'unknown')}")
                break
    if new_agents:
        print('\n=== NEW AGENTS ===')
        for name in sorted(new_agents):
            for a in current_agents:
                if get_name(a) == name:
                    print(f"  + {name}: {a.get('rel_path', 'unknown')}")
                    break
    print('\n=== ANALYSIS ===')
    layer_counts = {}
    path_patterns = {}
    for d in missing_details:
        layer = d['layer']
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        path = d['path']
        if '/' in path:
            folder = '/'.join(path.split('/')[:2])
            path_patterns[folder] = path_patterns.get(folder, 0) + 1
    print('\nMissing by layer:')
    for layer, count in sorted(layer_counts.items(), key=lambda x: -x[1]):
        print(f'  {layer}: {count}')
    print('\nMissing by folder:')
    for folder, count in sorted(path_patterns.items(), key=lambda x: -x[1])[:15]:
        print(f'  {folder}: {count}')
if __name__ == '__main__':
    main()
