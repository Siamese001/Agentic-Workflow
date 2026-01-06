"""Check which new Agent-suffixed classes were discovered."""
import json

data = json.load(open('agent_discovery_full.json'))

new_agent_files = [
    'GenerativeGuardAgent.py',
    'SystemArchitectAgent.py', 
    'OrchestrationHandshakeAgent.py',
    'OutreachTestPilotAgent.py',
    'StateValidatorAgent.py'
]

print(f"Total agents in registry: {len(data)}\n")

print("New Agent-suffixed classes:")
for d in data:
    if any(f in d['path'] for f in new_agent_files):
        print(f"  ✓ {d['class_name']} - {d['path']}")

print("\nOld classes still in registry (should be removed):")
old_classes = ['GenerativeGuard', 'SystemArchitect', 'OutreachTestPilot', 'StateValidator']
for d in data:
    if d['class_name'] in old_classes:
        print(f"  ✗ {d['class_name']} - {d['path']}")
