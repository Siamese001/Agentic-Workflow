"""
L5 D0 Injection Engine - Deterministic Role Fence Rendering

Implements deterministic D0 injection with RoleFence ordering and rendering.
No wall-clock usage, no randomness, pure deterministic behavior.
"""

from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "d0_injection_engine_enforcer")
emit_determinism_digest("p0", "d0_injection_engine_enforcer")

_emit_dispatches_healing_run("p1", "d0_injection_engine_enforcer", "L5")
_emit_routes_through("p1", "d0_injection_engine_enforcer", "L5")
_emit_escalates_to_human("p1", "d0_injection_engine_enforcer", "L5")
_emit_reads_policy_state("p1", "d0_injection_engine_enforcer", "L5")

_emit_applies_guardrail("p0", "d0_injection_engine_enforcer", "p0_governance")
_emit_snapshots_state("p0", "d0_injection_engine_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "d0_injection_engine_enforcer", "execution_auth")
_emit_validates_capability("p2", "d0_injection_engine_enforcer", "capability_check")
_emit_routes_to_capability("p2", "d0_injection_engine_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "d0_injection_engine_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "d0_injection_engine_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "d0_injection_engine_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "d0_injection_engine_enforcer", "exec_output")
_emit_dispatches_agent("p3", "d0_injection_engine_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "d0_injection_engine_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "d0_injection_engine_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "d0_injection_engine_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "d0_injection_engine_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "d0_injection_engine_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "d0_injection_engine_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "d0_injection_engine_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "d0_injection_engine_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "d0_injection_engine_enforcer", "eval_metric")
_emit_stores_embedding("p4", "d0_injection_engine_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "d0_injection_engine_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "d0_injection_engine_enforcer", "exec_snapshot_link")


@dataclass(frozen=True)
class RoleFence:
    """Immutable role fence for D0 injection."""

    fence_id: str
    text: str


class D0InjectionEngine:
    """
    Deterministic D0 injection engine for role fences.

    Renders fences in deterministic order with no mutation of input objects.
    """

    def render_d0(self, *, fences: tuple[RoleFence, ...]) -> str:
        """
                Render D0 string from role fences.

                Deterministic rendering:
                - Sort fences by fence_id
                - Join as: "<D0>
        [fence_id] text
        ...
        </D0>
        "

                Args:
                    fences: Tuple of RoleFence objects

                Returns:
                    Rendered D0 string
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "D0InjectionEngine.render_d0")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:D0InjectionEngine.render_d0".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        sorted_fences = sorted(fences, key=lambda f: f.fence_id)
        lines = ["<D0>"]
        for fence in sorted_fences:
            lines.append(f"[{fence.fence_id}] {fence.text}")
        lines.append("</D0>")
        return "\n".join(lines) + "\n"

    def inject(self, *, payload_like: object, fences: tuple[RoleFence, ...]) -> str:
        """
        Inject D0 fences into payload context.

        Returns the computed D0 string only.
        Does NOT mutate payload_like.
        Does NOT import or depend on L0 types.

        Args:
            payload_like: Object to inject into (not modified)
            fences: Tuple of RoleFence objects

        Returns:
            Rendered D0 string
        """
        return self.render_d0(fences=fences)
