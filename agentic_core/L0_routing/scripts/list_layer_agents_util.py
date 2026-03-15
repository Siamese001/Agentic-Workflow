"""
List agents by layer for batch hardening.

Reads from agent_discovery_full.json - run full_agent_discovery.py first.
"""

import json
import sys

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "list_layer_agents_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "list_layer_agents_util", "p0_governance")
_emit_snapshots_state("p0", "list_layer_agents_util", "state_snapshot")

layer = sys.argv[1] if len(sys.argv) > 1 else APPS_RG_DIR
data = json.load(open(AGENT_DISCOVERY_JSON))
agents = [a for a in data if a.get("layer") == layer]
print(f"{layer} agents ({len(agents)}):")
for a in agents:
    heal = "H" if a.get("has_healing") else "-"
    mcp = "M" if a.get("mcp_hardened") else "-"
    test = "T" if a.get("testing") != "None" else "-"
    print(f"  [{heal}{mcp}{test}] {a['class_name']} - {a['path']}")
