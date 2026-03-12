from pathlib import Path
'Check the actual SovereignBaseAgent class vs territory classification.'
import json
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / 'agent_discovery_full.json') as f:
    agents = json.load(f)
sovereign_class = [a for a in agents if a.get('class_name') == 'SovereignBaseAgent']
if sovereign_class:
    for _a in sovereign_class:
        pass
territory_sovereign = [a for a in agents if a.get('territory') == 'Sovereign Base Agent']
base_layer = [a for a in agents if a.get('layer') == 'Base']
