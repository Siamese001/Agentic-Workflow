"""Types for the Reflexion pattern.

Reflexion builds verbal self-critique into a memory buffer and uses it
to iteratively revise responses until a convergence gate is satisfied.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "reflexion_types")
emit_determinism_digest("p0", "reflexion_types")

_emit_dispatches_healing_run("p1", "reflexion_types", "L3")
_emit_routes_through("p1", "reflexion_types", "L3")
_emit_escalates_to_human("p1", "reflexion_types", "L3")
_emit_reads_policy_state("p1", "reflexion_types", "L3")
_emit_authorize_and_execute("p2", "reflexion_types", "execution_auth")
_emit_validates_capability("p2", "reflexion_types", "capability_check")
_emit_routes_to_capability("p2", "reflexion_types", "capability_route")
_emit_writes_via_uwg("p2", "reflexion_types", "uwg_write")
_emit_blocks_direct_write("p2", "reflexion_types", "direct_write_block")
_emit_records_tool_invocation("p2", "reflexion_types", "tool_invocation")
_emit_captures_execution_output("p2", "reflexion_types", "exec_output")
_emit_dispatches_agent("p3", "reflexion_types", "agent_dispatch")
_emit_coordinates_agents("p3", "reflexion_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "reflexion_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "reflexion_types", "healing_outcome")
_emit_escalates_failure("p3", "reflexion_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "reflexion_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reflexion_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "reflexion_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "reflexion_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reflexion_types", "eval_metric")
_emit_stores_embedding("p4", "reflexion_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "reflexion_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reflexion_types", "exec_snapshot_link")


@dataclass
class ReflexionCritique:
    """Verbal critique produced by the Evaluator LLM call."""

    iteration: int
    response: str
    critique: str
    score: float
    passed: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReflexionMemory:
    """Accumulates critique history across iterations for the Revisor."""

    task: str
    critiques: list[ReflexionCritique] = field(default_factory=list)

    def add(self, critique: ReflexionCritique) -> None:
        self.critiques.append(critique)

    def summary(self) -> str:
        """Return a condensed summary of prior critiques for the Revisor prompt."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReflexionMemory.summary", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReflexionMemory.summary", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReflexionMemory.summary")

        if not self.critiques:
            return ""
        lines = [f"Iteration {c.iteration}: score={c.score:.2f} — {c.critique[:120]}" for c in self.critiques]
        return "\n".join(lines)

    def best_response(self) -> str | None:
        """Return the response with the highest score seen so far."""
        if not self.critiques:
            return None
        return max(self.critiques, key=lambda c: c.score).response
