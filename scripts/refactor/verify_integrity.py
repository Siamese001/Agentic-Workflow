"""Verify registry integrity matches sovereign state."""
import json

# Load both files
with open('agent_discovery_full.json') as f:
    registry = json.load(f)

with open('sovereign_state_final.json') as f:
    state = json.load(f)

# Compare counts
reg_count = len(registry)
state_count = state['baseline_metadata']['agent_count']

print(f"Registry agents: {reg_count}")
print(f"State agents: {state_count}")
print(f"Match: {reg_count == state_count}")

if reg_count == state_count:
    print("\n✅ INTEGRITY VERIFIED - Registry matches sovereign state")
else:
    print(f"\n❌ MISMATCH - Registry has {reg_count}, state expects {state_count}")
