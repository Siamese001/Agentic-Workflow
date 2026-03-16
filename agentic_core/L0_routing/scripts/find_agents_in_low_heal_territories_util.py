"""Find actual agent files that belong to low heal capability territories."""

import json
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "find_agents_in_low_heal_territories_util")
emit_determinism_digest("p0", "find_agents_in_low_heal_territories_util")

_emit_dispatches_healing_run("p1", "find_agents_in_low_heal_territories_util", "L0")
_emit_routes_through("p1", "find_agents_in_low_heal_territories_util", "L0")
_emit_escalates_to_human("p1", "find_agents_in_low_heal_territories_util", "L0")
_emit_reads_policy_state("p1", "find_agents_in_low_heal_territories_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_agents_in_low_heal_territories_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_agents_in_low_heal_territories_util", "p0_governance")
_emit_snapshots_state("p0", "find_agents_in_low_heal_territories_util", "state_snapshot")
_emit_authorize_and_execute("p2", "find_agents_in_low_heal_territories_util", "execution_auth")
_emit_validates_capability("p2", "find_agents_in_low_heal_territories_util", "capability_check")
_emit_routes_to_capability("p2", "find_agents_in_low_heal_territories_util", "capability_route")
_emit_writes_via_uwg("p2", "find_agents_in_low_heal_territories_util", "uwg_write")
_emit_blocks_direct_write("p2", "find_agents_in_low_heal_territories_util", "direct_write_block")
_emit_records_tool_invocation("p2", "find_agents_in_low_heal_territories_util", "tool_invocation")
_emit_captures_execution_output("p2", "find_agents_in_low_heal_territories_util", "exec_output")
_emit_dispatches_agent("p3", "find_agents_in_low_heal_territories_util", "agent_dispatch")
_emit_coordinates_agents("p3", "find_agents_in_low_heal_territories_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "find_agents_in_low_heal_territories_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "find_agents_in_low_heal_territories_util", "healing_outcome")
_emit_escalates_failure("p3", "find_agents_in_low_heal_territories_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "find_agents_in_low_heal_territories_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "find_agents_in_low_heal_territories_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "find_agents_in_low_heal_territories_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "find_agents_in_low_heal_territories_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "find_agents_in_low_heal_territories_util", "eval_metric")
_emit_stores_embedding("p4", "find_agents_in_low_heal_territories_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "find_agents_in_low_heal_territories_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "find_agents_in_low_heal_territories_util", "exec_snapshot_link")

with open(
    "C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html",
    encoding="utf-8",
) as f:
    data = f.read()
start = data.find("const dashboardData = [")
end = data.find("];", start) + 1
json_str = data[start + 21 : end]
territories = json.loads(json_str)
print("=== All Territories with Heal Cap % ===")
for t in sorted(territories, key=lambda x: x.get("Heal Cap %", 100)):
    if t["Territory"] == "TOTAL":
        continue
    heal_cap = t.get("Heal Cap %", 100)
    total = t.get("Total", 0)
    if heal_cap < 100:
        print(f"  {t['Territory']}: {heal_cap}% ({total} agents)")
from agentic_core.utils.ssot_discovery_validator import get_agent_files

print("\n=== Searching for agents in L1 Cognition ===")
l1_agents = list(get_agent_files(Path("C:/Git/Agentic-Workflow/agentic_core/L1_cognition")))
for agent in l1_agents:
    content = agent.read_text(encoding="utf-8", errors="ignore")
    has_heal = "def heal_repository" in content
    print(f"  {('✅' if has_heal else '❌')} {agent.name}")
print("\n=== Searching for agents in L3 Orchestration ===")
l3_agents = list(get_agent_files(Path("C:/Git/Agentic-Workflow/agentic_core/L3_orchestration")))
for agent in l3_agents:
    content = agent.read_text(encoding="utf-8", errors="ignore")
    has_heal = "def heal_repository" in content
    print(f"  {('✅' if has_heal else '❌')} {agent.name}")
print("\n=== Agents MISSING heal_repository (need to fix) ===")
all_agents = get_agent_files(Path("C:/Git/Agentic-Workflow/agentic_core"))
missing = []
for agent in all_agents:
    content = agent.read_text(encoding="utf-8", errors="ignore")
    if "def heal_repository" not in content:
        missing.append(agent)
        print(f"  ❌ {agent.relative_to(Path('C:/Git/Agentic-Workflow'))}")
print(f"\nTotal agents missing heal_repository: {len(missing)}")
