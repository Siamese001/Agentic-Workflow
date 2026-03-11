#!/usr/bin/env python3
"""
Find agents that have healing capability but invocation='No'.
These need to have invocation added to reach 100% invocation rate.
"""

import json

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Load agent discovery data
with open("agent_discovery_full.json") as f:
    agents = json.load(f)

print(f"Total agents: {len(agents)}")

# Find agents with healing but no invocation
missing_invocation = []
for agent in agents:
    invocation = agent.get("invocation", "No")
    has_healing = agent.get("has_healing", False)

    # Has healing but invocation is No
    if has_healing and invocation != "Yes":
        missing_invocation.append(agent)

print(f"\n{'=' * 70}")
print(f"AGENTS WITH HEALING BUT NO INVOCATION: {len(missing_invocation)}")
print(f"{'=' * 70}")

if not missing_invocation:
    print("✅ All agents with healing have invocation!")
else:
    for agent in missing_invocation:
        print(f"\n  - {agent['class_name']}")
        print(f"    Path: {agent['path']}")
        print(f"    Territory: {agent.get('territory')}")
        print(f"    Invocation: {agent.get('invocation')}")
        print(f"    Has Healing: {agent.get('has_healing')}")

print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")
print(f"Total agents: {len(agents)}")
print(f"Agents with healing: {sum(1 for a in agents if a.get('has_healing'))}")
print(f"Agents with invocation=Yes: {sum(1 for a in agents if a.get('invocation') == 'Yes')}")
print(f"Missing invocation: {len(missing_invocation)}")
current_pct = sum(1 for a in agents if a.get("invocation") == "Yes") / len(agents) * 100
print(f"Current Invocation %: {current_pct:.1f}%")
print("Target: 100%")
