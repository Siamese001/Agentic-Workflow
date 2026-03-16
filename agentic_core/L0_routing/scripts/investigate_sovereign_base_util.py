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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "investigate_sovereign_base_util")
emit_determinism_digest("p0", "investigate_sovereign_base_util")

_emit_dispatches_healing_run("p1", "investigate_sovereign_base_util", "L0")
_emit_routes_through("p1", "investigate_sovereign_base_util", "L0")
_emit_escalates_to_human("p1", "investigate_sovereign_base_util", "L0")
_emit_reads_policy_state("p1", "investigate_sovereign_base_util", "L0")

_emit_records_execution_trace("p0", "evidence", "investigate_sovereign_base_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "investigate_sovereign_base_util", "p0_governance")
_emit_snapshots_state("p0", "investigate_sovereign_base_util", "state_snapshot")

"Investigate Sovereign Base Agent territory classification."
import json

PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / "agent_discovery_full.json") as f:
    agents = json.load(f)
sovereign_agents = [a for a in agents if a.get("territory") == "Sovereign Base Agent"]
for a in sovereign_agents[:20]:
    layer = a.get("layer", "?")
    path = a.get("path", "no path")
path_prefixes = {}
for a in sovereign_agents:
    path = a.get("path", "")
    if "/" in path or "\\" in path:
        prefix = path.split("/")[0] if "/" in path else path.split("\\")[0]
        path_prefixes[prefix] = path_prefixes.get(prefix, 0) + 1
for prefix, _count in sorted(path_prefixes.items(), key=lambda x: -x[1]):
    pass
