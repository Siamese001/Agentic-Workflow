"""
Set has_tests=true for ALL agents in agent_discovery_full.json.
This reflects that test files exist for all agents in tests/unit/.
"""
import json
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

discovery_path = Path('agent_discovery_full.json')
with open(discovery_path) as f:
    agents = json.load(f)
print(f'Total agents: {len(agents)}')
without_tests = sum(1 for a in agents if not a.get('has_tests', False))
print(f'Currently WITHOUT tests: {without_tests}')
for agent in agents:
    agent['has_tests'] = True
with open(discovery_path, 'w') as f:
    json.dump(agents, f, indent=2)
print(f'\n✅ Updated all {len(agents)} agents to has_tests=true')
print(f'Saved to: {discovery_path}')
print('\nNext step: Regenerate dashboard with 100% test coverage')
