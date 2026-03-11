"""Dump meta-learning and healing action state from runtime_state.json."""
import json
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

d = json.loads(Path("runtime_state.json").read_text(encoding="utf-8"))
ha = d.get("healing_actions", [])
ml = d["meta_learning"]

print("=== RUNTIME STATE SUMMARY ===")
print(f"  status:          {d.get('status')}")
print(f"  end_time:        {d.get('end_time')}")
print(f"  ml_enabled:      {ml['enabled']}")
print(f"  ml_experiences:  {ml['total_experiences']}")
print(f"  ml_recent:       {ml['recent_experiences']}")
print(f"  healing_actions: {len(ha)}")
print()

print("=== HEALING ACTIONS (from last execute_ssot --heal run) ===")
for i, a in enumerate(ha):
    print(f"  [{i}] agent={a['agent']}")
    print(f"       territory={a['territory']}  confidence={a['confidence']}")
    print(f"       tier={a['routing_tier']}  outcome={a['outcome']}")
    print(f"       fix: {a['fix_summary']}")
    print(f"       time: {a['timestamp']}")
    print()

# Aggregate by agent
from collections import Counter
agent_counts = Counter(a["agent"] for a in ha)
territory_counts = Counter(a["territory"] for a in ha)
tier_counts = Counter(a["routing_tier"] for a in ha)
outcome_counts = Counter(a["outcome"] for a in ha)

print("=== AGGREGATE STATS ===")
print(f"  By agent:     {dict(agent_counts)}")
print(f"  By territory: {dict(territory_counts)}")
print(f"  By tier:      {dict(tier_counts)}")
print(f"  By outcome:   {dict(outcome_counts)}")
