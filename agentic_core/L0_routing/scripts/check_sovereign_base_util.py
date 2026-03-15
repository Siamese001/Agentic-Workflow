from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "check_sovereign_base_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "check_sovereign_base_util", "p0_governance")
_emit_snapshots_state("p0", "check_sovereign_base_util", "state_snapshot")

"Check the actual SovereignBaseAgent class vs territory classification."
import json

PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / "agent_discovery_full.json") as f:
    agents = json.load(f)
sovereign_class = [a for a in agents if a.get("class_name") == "SovereignBaseAgent"]
if sovereign_class:
    for _a in sovereign_class:
        pass
territory_sovereign = [a for a in agents if a.get("territory") == "Sovereign Base Agent"]
base_layer = [a for a in agents if a.get("layer") == "Base"]
