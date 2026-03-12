"""Debug script to identify invocation pipeline discrepancy."""
import json
from pathlib import Path
from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
PROJECT_ROOT = Path(__file__).parent.parent
registry = json.load(open(PROJECT_ROOT / AGENT_DISCOVERY_JSON))
print(f'JSON agents: {len(registry)}')
registry_by_path = {}
for entry in registry:
    p = (entry.get('path') or '').replace('\\', '/')
    if p:
        registry_by_path[p] = entry
print(f'Registry paths: {len(registry_by_path)}')
inv_counts = {}
for entry in registry:
    inv = entry.get('invocation', 'Missing')
    inv_counts[inv] = inv_counts.get(inv, 0) + 1
print(f'JSON invocation counts: {inv_counts}')
all_agents = []
for agent in registry:
    path_str = agent.get('path', '')
    if path_str:
        full_path = PROJECT_ROOT / path_str
        if full_path.exists():
            all_agents.append(full_path)
print(f'Resolved agent paths: {len(all_agents)}')
found = 0
not_found = 0
not_found_paths = []
invocation_from_lookup = {'Yes': 0, 'No (missing super)': 0, 'Inherited': 0}
for agent in all_agents:
    rel_path = str(agent.relative_to(PROJECT_ROOT)).replace('\\', '/')
    entry = registry_by_path.get(rel_path)
    if entry:
        found += 1
        inv = entry.get('invocation', 'Inherited')
        invocation_from_lookup[inv] = invocation_from_lookup.get(inv, 0) + 1
    else:
        not_found += 1
        not_found_paths.append(rel_path)
print(f'\nLookup results: found={found}, not_found={not_found}')
if not_found_paths:
    print('Not found paths:')
    for p in not_found_paths[:10]:
        print(f'  {p}')
print(f'Invocation from lookup: {invocation_from_lookup}')
yes = invocation_from_lookup.get('Yes', 0)
inh = invocation_from_lookup.get('Inherited', 0)
no = invocation_from_lookup.get('No (missing super)', 0)
total = yes + inh + no
if total > 0:
    pct = (yes + inh) / total * 100
    print(f'\nExpected Invocation %: {pct:.1f}%')
print('\nSample registry paths:')
for _i, p in enumerate(list(registry_by_path.keys())[:5]):
    print(f'  {p}')
print('\nSample agent rel_paths:')
for _i, a in enumerate(all_agents[:5]):
    print(f"  {str(a.relative_to(PROJECT_ROOT)).replace(chr(92), '/')}")
