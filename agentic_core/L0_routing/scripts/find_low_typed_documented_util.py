"""Find agents with Typed % < 100% or Documented % < 100%."""

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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "find_low_typed_documented_util")
emit_determinism_digest("p0", "find_low_typed_documented_util")

_emit_dispatches_healing_run("p1", "find_low_typed_documented_util", "L0")
_emit_routes_through("p1", "find_low_typed_documented_util", "L0")
_emit_escalates_to_human("p1", "find_low_typed_documented_util", "L0")
_emit_reads_policy_state("p1", "find_low_typed_documented_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_low_typed_documented_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_low_typed_documented_util", "p0_governance")
_emit_snapshots_state("p0", "find_low_typed_documented_util", "state_snapshot")

PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / "agent_discovery_full.json", encoding="utf-8") as f:
    agents = json.load(f)
low_typed = [a for a in agents if a.get("typed_pct", 100) < 100]
low_doc = [a for a in agents if a.get("documented_pct", 100) < 100]
print(f"Agents with Typed < 100%: {len(low_typed)}")
print(f"Agents with Documented < 100%: {len(low_doc)}")
print("\n" + "=" * 70)
print("LOW TYPED AGENTS:")
print("=" * 70)
for a in low_typed:
    print(f"  {a['class_name']}: {a['typed_pct']}% - {a['path']}")
print("\n" + "=" * 70)
print("LOW DOCUMENTED AGENTS:")
print("=" * 70)
for a in low_doc:
    print(f"  {a['class_name']}: {a['documented_pct']}% - {a['path']}")
