"""Find the remaining agents missing heal_repository."""

import json
import sys
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

emit_replay_key("p0", "find_remaining_missing_heal_util")
emit_determinism_digest("p0", "find_remaining_missing_heal_util")

_emit_dispatches_healing_run("p1", "find_remaining_missing_heal_util", "L0")
_emit_routes_through("p1", "find_remaining_missing_heal_util", "L0")
_emit_escalates_to_human("p1", "find_remaining_missing_heal_util", "L0")
_emit_reads_policy_state("p1", "find_remaining_missing_heal_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_remaining_missing_heal_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_remaining_missing_heal_util", "p0_governance")
_emit_snapshots_state("p0", "find_remaining_missing_heal_util", "state_snapshot")

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from agentic_core.utils.project_root_util import get_project_root

project_root = get_project_root()
with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
    data = json.load(f)
missing = [a for a in data if not a.get("has_healing")]
print(f"Agents missing healing: {len(missing)}")
for agent in missing:
    print(f"  {agent['path']}")
