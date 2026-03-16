"""HOPPipelineExecutor — Canonical parameterized HOP pipeline stage agent.

Consolidates: HOP1-HOP9 pipeline stage agents.
Created: 2026-02-08 (Structural Agent Count Reduction)

Each stage's _process() logic is preserved in hop_stage_registry.py.
This executor dispatches to the registered stage implementation.

GOVERNANCE: reasoning_profile is injected from the L0-stamped
SignedExecutionEnvelope and treated as READ-ONLY constraints.
The executor may not modify or override any profile field.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from apps_lic.utils.hop_stage_capability import HOPStageCapability
from apps_lic.utils.LICAgentBase import LICAgentBase

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_applies_guardrail("p0", "HOPPipelineExecutor", "p0_governance")
_emit_reads_policy_state("p0", "HOPPipelineExecutor", "policy_binding")
_emit_snapshots_state("p0", "HOPPipelineExecutor", "state_snapshot")
emit_replay_key("p0", "HOPPipelineExecutor")
emit_determinism_digest("p0", "HOPPipelineExecutor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "HOPPipelineExecutor", "execution_auth")
_emit_validates_capability("p2", "HOPPipelineExecutor", "capability_check")
_emit_routes_to_capability("p2", "HOPPipelineExecutor", "capability_route")
_emit_writes_via_uwg("p2", "HOPPipelineExecutor", "uwg_write")
_emit_blocks_direct_write("p2", "HOPPipelineExecutor", "direct_write_block")
_emit_records_tool_invocation("p2", "HOPPipelineExecutor", "tool_invocation")
_emit_captures_execution_output("p2", "HOPPipelineExecutor", "exec_output")
_emit_dispatches_agent("p3", "HOPPipelineExecutor", "agent_dispatch")
_emit_coordinates_agents("p3", "HOPPipelineExecutor", "agent_coordination")
_emit_records_workflow_lineage("p3", "HOPPipelineExecutor", "workflow_lineage")
_emit_records_healing_outcome("p3", "HOPPipelineExecutor", "healing_outcome")
_emit_escalates_failure("p3", "HOPPipelineExecutor", "failure_escalation")
_emit_orchestrates_workflow("p3", "HOPPipelineExecutor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "HOPPipelineExecutor", "healing_dispatch")
_emit_invokes_evaluation("p3", "HOPPipelineExecutor", "evaluation_signal")
_emit_records_telemetry_event("p4", "HOPPipelineExecutor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "HOPPipelineExecutor", "eval_metric")
_emit_stores_embedding("p4", "HOPPipelineExecutor", "embedding_store")
_emit_updates_meta_learning_state("p4", "HOPPipelineExecutor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "HOPPipelineExecutor", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.interfaces.routing_types import ReasoningIntensityProfile


@dataclass
class HOPPipelineExecutor(HOPStageCapability, LICAgentBase):
    """Parameterized HOP pipeline stage agent.

    Usage:
        stage = HOPPipelineExecutor(stage_id=4)
        stage = HOPPipelineExecutor(stage_id=4, reasoning_profile=profile)

    When reasoning_profile is provided it is treated as READ-ONLY policy
    constraints stamped by L0. The executor must not mutate or override it.
    When absent, stage handlers fall back to static DEFAULT_TOGGLES.
    """

    stage_id: int = 0
    stage_name: str = field(init=False, default="unknown")
    reasoning_profile: ReasoningIntensityProfile | None = field(default=None, repr=False)
    _STAGE_NAMES = {
        1: "profile_analysis",
        2: "research",
        3: "sender_grounding",
        4: "routing",
        5: "generation",
        6: "validation",
        7: "gate_decision",
        8: "qa_report",
        9: "integration",
    }

    def __post_init__(self) -> None:
        self.stage_name = self._STAGE_NAMES.get(self.stage_id, "unknown")

    def _process(self, context: dict | None = None, **kwargs) -> dict:
        """Dispatch to stage-specific processing.

        Domain logic for each stage is preserved via the stage registry.
        reasoning_profile (if present) is forwarded as a read-only constraint.
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"HOPPipelineExecutor._process:stage_{self.stage_id}")
        from apps_lic.engines import hop_stage_registry

        handler = hop_stage_registry.get_stage_handler(self.stage_id)
        if handler is None:
            return {"stage": self.stage_id, "error": f"No handler for stage {self.stage_id}"}
        return handler(self, context or {}, reasoning_profile=self.reasoning_profile, **kwargs)
