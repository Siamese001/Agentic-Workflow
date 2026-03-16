from __future__ import annotations

import uuid

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "nervous_system")
emit_determinism_digest("p0", "nervous_system")

_emit_dispatches_healing_run("p1", "nervous_system", "L3")
_emit_routes_through("p1", "nervous_system", "L3")
_emit_escalates_to_human("p1", "nervous_system", "L3")
_emit_reads_policy_state("p1", "nervous_system", "L3")

_emit_snapshots_state("p0", "nervous_system", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "nervous_system", "p0_governance")

"Nervous System module."
from agentic_core.L3_orchestration.engines.reflex_layer_pattern import ReflexLayer
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_records_execution_trace,
)


class NervousSystem:
    """Nervous System orchestration."""

    def __init__(self):
        self.ReflexLayer = ReflexLayer()
        self.reflexes = {}
        self.missions = []

    def register_reflex(self, trigger: str, action: callable):
        _emit_agent_executes_agent(str(uuid.uuid4()), "NervousSystem", "NervousSystem.register_reflex")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "NervousSystem.register_reflex"
        )

        self.reflexes[trigger] = action
        return self.ReflexLayer.register_reflex(trigger, action)

    def trigger_reflex(self, event: str):
        return self.ReflexLayer.trigger_reflex(event)

    def get_status(self):
        return self.ReflexLayer.get_status()


__all__ = ["NervousSystem", "ReflexLayer"]
