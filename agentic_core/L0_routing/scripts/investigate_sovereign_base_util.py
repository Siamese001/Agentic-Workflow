from pathlib import Path
'Investigate Sovereign Base Agent territory classification.'
import json
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / 'agent_discovery_full.json') as f:
    agents = json.load(f)
sovereign_agents = [a for a in agents if a.get('territory') == 'Sovereign Base Agent']
for a in sovereign_agents[:20]:
    layer = a.get('layer', '?')
    path = a.get('path', 'no path')
path_prefixes = {}
for a in sovereign_agents:
    path = a.get('path', '')
    if '/' in path or '\\' in path:
        prefix = path.split('/')[0] if '/' in path else path.split('\\')[0]
        path_prefixes[prefix] = path_prefixes.get(prefix, 0) + 1
for prefix, _count in sorted(path_prefixes.items(), key=lambda x: -x[1]):
    pass
