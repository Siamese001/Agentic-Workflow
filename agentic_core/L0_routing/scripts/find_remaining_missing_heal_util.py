"""Find the remaining agents missing heal_repository."""
import json
import sys
from pathlib import Path
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from agentic_core.utils.project_root_util import get_project_root
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
project_root = get_project_root()
with open(project_root / 'agent_discovery_full.json', encoding='utf-8') as f:
    data = json.load(f)
missing = [a for a in data if not a.get('has_healing')]
print(f'Agents missing healing: {len(missing)}')
for agent in missing:
    print(f"  {agent['path']}")
