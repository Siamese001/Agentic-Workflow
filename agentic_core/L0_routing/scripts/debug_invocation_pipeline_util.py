"""Debug script to identify invocation pipeline discrepancy."""

import json
from pathlib import Path

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "debug_invocation_pipeline_util")
emit_determinism_digest("p0", "debug_invocation_pipeline_util")

_emit_dispatches_healing_run("p1", "debug_invocation_pipeline_util", "L0")
_emit_routes_through("p1", "debug_invocation_pipeline_util", "L0")
_emit_escalates_to_human("p1", "debug_invocation_pipeline_util", "L0")
_emit_reads_policy_state("p1", "debug_invocation_pipeline_util", "L0")

_emit_records_execution_trace("p0", "evidence", "debug_invocation_pipeline_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "debug_invocation_pipeline_util", "p0_governance")
_emit_snapshots_state("p0", "debug_invocation_pipeline_util", "state_snapshot")

PROJECT_ROOT = Path(__file__).parent.parent
registry = json.load(open(PROJECT_ROOT / AGENT_DISCOVERY_JSON))
print(f"JSON agents: {len(registry)}")
registry_by_path = {}
for entry in registry:
    p = (entry.get("path") or "").replace("\\", "/")
    if p:
        registry_by_path[p] = entry
print(f"Registry paths: {len(registry_by_path)}")
inv_counts = {}
for entry in registry:
    inv = entry.get("invocation", "Missing")
    inv_counts[inv] = inv_counts.get(inv, 0) + 1
print(f"JSON invocation counts: {inv_counts}")
all_agents = []
for agent in registry:
    path_str = agent.get("path", "")
    if path_str:
        full_path = PROJECT_ROOT / path_str
        if full_path.exists():
            all_agents.append(full_path)
print(f"Resolved agent paths: {len(all_agents)}")
found = 0
not_found = 0
not_found_paths = []
invocation_from_lookup = {"Yes": 0, "No (missing super)": 0, "Inherited": 0}
for agent in all_agents:
    rel_path = str(agent.relative_to(PROJECT_ROOT)).replace("\\", "/")
    entry = registry_by_path.get(rel_path)
    if entry:
        found += 1
        inv = entry.get("invocation", "Inherited")
        invocation_from_lookup[inv] = invocation_from_lookup.get(inv, 0) + 1
    else:
        not_found += 1
        not_found_paths.append(rel_path)
print(f"\nLookup results: found={found}, not_found={not_found}")
if not_found_paths:
    print("Not found paths:")
    for p in not_found_paths[:10]:
        print(f"  {p}")
print(f"Invocation from lookup: {invocation_from_lookup}")
yes = invocation_from_lookup.get("Yes", 0)
inh = invocation_from_lookup.get("Inherited", 0)
no = invocation_from_lookup.get("No (missing super)", 0)
total = yes + inh + no
if total > 0:
    pct = (yes + inh) / total * 100
    print(f"\nExpected Invocation %: {pct:.1f}%")
print("\nSample registry paths:")
for _i, p in enumerate(list(registry_by_path.keys())[:5]):
    print(f"  {p}")
print("\nSample agent rel_paths:")
for _i, a in enumerate(all_agents[:5]):
    print(f"  {str(a.relative_to(PROJECT_ROOT)).replace(chr(92), '/')}")
