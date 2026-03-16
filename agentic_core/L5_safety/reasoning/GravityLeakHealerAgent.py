"""GravityLeakHealerAgent - canonical healer name alias for GravityLeakRepairAgent."""

from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
    GravityLeakRepairAgent as GravityLeakHealerAgent,
)
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

emit_replay_key("p0", "GravityLeakHealerAgent")
emit_determinism_digest("p0", "GravityLeakHealerAgent")

_emit_dispatches_healing_run("p1", "GravityLeakHealerAgent", "L5")
_emit_routes_through("p1", "GravityLeakHealerAgent", "L5")
_emit_escalates_to_human("p1", "GravityLeakHealerAgent", "L5")
_emit_reads_policy_state("p1", "GravityLeakHealerAgent", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "GravityLeakHealerAgent")
_emit_applies_guardrail("p0", "GravityLeakHealerAgent", "p0_governance")
_emit_snapshots_state("p0", "GravityLeakHealerAgent", "state_snapshot")

__all__ = ["GravityLeakHealerAgent"]
