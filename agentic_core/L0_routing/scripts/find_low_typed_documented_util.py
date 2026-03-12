"""Find agents with Typed % < 100% or Documented % < 100%."""
import json
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / 'agent_discovery_full.json', encoding='utf-8') as f:
    agents = json.load(f)
low_typed = [a for a in agents if a.get('typed_pct', 100) < 100]
low_doc = [a for a in agents if a.get('documented_pct', 100) < 100]
print(f'Agents with Typed < 100%: {len(low_typed)}')
print(f'Agents with Documented < 100%: {len(low_doc)}')
print('\n' + '=' * 70)
print('LOW TYPED AGENTS:')
print('=' * 70)
for a in low_typed:
    print(f"  {a['class_name']}: {a['typed_pct']}% - {a['path']}")
print('\n' + '=' * 70)
print('LOW DOCUMENTED AGENTS:')
print('=' * 70)
for a in low_doc:
    print(f"  {a['class_name']}: {a['documented_pct']}% - {a['path']}")
