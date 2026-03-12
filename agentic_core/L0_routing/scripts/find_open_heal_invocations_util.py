"""
Find agents with open heal invocations.
Open heal invocation = agent has invocation='Yes' but has_healing=False
This is a data integrity issue that needs to be fixed.
"""
import json
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
with open('agent_discovery_full.json') as f:
    agents = json.load(f)
print(f'Total agents: {len(agents)}')
open_invocations = []
for agent in agents:
    invocation = agent.get('invocation', 'No')
    has_healing = agent.get('has_healing', False)
    if invocation == 'Yes' and (not has_healing):
        open_invocations.append(agent)
print(f"\n{'=' * 70}")
print(f'AGENTS WITH OPEN HEAL INVOCATIONS: {len(open_invocations)}')
print(f"{'=' * 70}")
if not open_invocations:
    print('✅ No open heal invocations found - all agents are consistent!')
else:
    by_territory = {}
    for agent in open_invocations:
        territory = agent.get('territory', 'Unknown')
        if territory not in by_territory:
            by_territory[territory] = []
        by_territory[territory].append(agent)
    for territory in sorted(by_territory.keys()):
        agents_list = by_territory[territory]
        print(f'\n{territory} ({len(agents_list)} agents):')
        for agent in agents_list:
            print(f"  - {agent['class_name']}")
            print(f"    Path: {agent['path']}")
            print(f"    Invocation: {agent.get('invocation')}")
            print(f"    Has Healing: {agent.get('has_healing')}")
            print(f"    Inheritance: {', '.join(agent.get('inheritance', []))}")
print(f"\n{'=' * 70}")
print('SUMMARY')
print(f"{'=' * 70}")
print(f'Total agents: {len(agents)}')
print(f"Agents with healing: {sum((1 for a in agents if a.get('has_healing')))}")
print(f"Agents with invocation: {sum((1 for a in agents if a.get('invocation') == 'Yes'))}")
print(f'Open heal invocations: {len(open_invocations)}')
print('\nExpected: Invocation count should equal Healing count')
print(f"Actual gap: {sum((1 for a in agents if a.get('invocation') == 'Yes')) - sum((1 for a in agents if a.get('has_healing')))}")
