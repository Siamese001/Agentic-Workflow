"""Find which L0 Maintenance/Core agent is not MCP hardened."""

import json
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "find_non_hardened_l0_util", "L0")
_emit_routes_through("p1", "find_non_hardened_l0_util", "L0")
_emit_escalates_to_human("p1", "find_non_hardened_l0_util", "L0")
_emit_reads_policy_state("p1", "find_non_hardened_l0_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_non_hardened_l0_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_non_hardened_l0_util", "p0_governance")
_emit_snapshots_state("p0", "find_non_hardened_l0_util", "state_snapshot")

project_root = Path(__file__).parent.parent
with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
    data = json.load(f)
l0_agents = [a for a in data if a.get("territory") == "L0 Maintenance/Core"]
print(f"L0 Maintenance/Core agents: {len(l0_agents)}")
non_hardened = [a for a in l0_agents if not a.get("mcp_hardened", False)]
print(f"\nNon-MCP hardened: {len(non_hardened)}")
if non_hardened:
    print("\nAgents WITHOUT MCP hardening:")
    for a in non_hardened:
        print(f"  ❌ {a['class_name']}")
        print(f"     Path: {a['path']}")
        print(f"     Inheritance: {a.get('inheritance', [])}")
else:
    print("\n✅ All L0 Maintenance/Core agents are MCP hardened")
hardened_count = len([a for a in l0_agents if a.get("mcp_hardened", False)])
total_count = len(l0_agents)
percentage = hardened_count / total_count * 100 if total_count > 0 else 0
print(f"\nMCP Hardening: {hardened_count}/{total_count} = {percentage:.1f}%")
