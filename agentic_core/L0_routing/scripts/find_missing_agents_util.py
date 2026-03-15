"""Find which agent is missing from dashboard territories."""

import json
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "find_missing_agents_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_missing_agents_util", "p0_governance")
_emit_snapshots_state("p0", "find_missing_agents_util", "state_snapshot")

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_PATH = PROJECT_ROOT / "agent_discovery_full.json"
with open(DISCOVERY_PATH, encoding="utf-8") as f:
    agents = json.load(f)
territory_counts = defaultdict(int)
for agent in agents:
    territory = agent.get("territory", "Unknown")
    territory_counts[territory] += 1
print("Territory counts from discovery:")
for t, count in sorted(territory_counts.items()):
    print(f"  {t}: {count}")
print(f"\nTotal: {sum(territory_counts.values())}")
