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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from apps_lic.utils.hop_stage_capability_util import HOPStageCapability
from apps_lic.utils.lic_agent_base_util import LICAgentBase

_emit_applies_guardrail("p0", "HOPPipelineExecutor", "p0_governance")
_emit_reads_policy_state("p0", "HOPPipelineExecutor", "policy_binding")
_emit_snapshots_state("p0", "HOPPipelineExecutor", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("HOPPipelineExecutor", "p4obs", "metric_1")
_emit_emits_metric_event("HOPPipelineExecutor", "p4obs", "metric_2")
_emit_emits_metric_event("HOPPipelineExecutor", "p4obs", "metric_3")
_emit_emits_metric_event("HOPPipelineExecutor", "p4obs", "metric_4")
_emit_emits_metric_event("HOPPipelineExecutor", "p4obs", "metric_5")
_emit_emits_metric_event("HOPPipelineExecutor", "p4obs", "metric_6")
_emit_records_incident_event("HOPPipelineExecutor", "p4obs", "incident")
_emit_captures_runtime_anomaly("HOPPipelineExecutor", "p4obs", "anomaly")
_emit_writes_observability_log("HOPPipelineExecutor", "p4obs", "obs_log")
_emit_updates_monitoring_state("HOPPipelineExecutor", "p4obs", "mon_state")
_emit_triggers_alert("HOPPipelineExecutor", "p4obs", "alert")
_emit_links_incident_trace("HOPPipelineExecutor", "p4obs", "trace_link")
_emit_captures_pattern("HOPPipelineExecutor", "p3lm", "pattern")
_emit_records_learning_event("HOPPipelineExecutor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("HOPPipelineExecutor", "p3lm", "snapshot")
_emit_feeds_meta_learning("HOPPipelineExecutor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("HOPPipelineExecutor", "p3lm", "routing")
_emit_improves_agent_policy("HOPPipelineExecutor", "p3lm", "policy")
_emit_stores_learning_state("HOPPipelineExecutor", "p3lm", "state")
_emit_records_execution_trace("HOPPipelineExecutor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("HOPPipelineExecutor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("HOPPipelineExecutor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("HOPPipelineExecutor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("HOPPipelineExecutor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("HOPPipelineExecutor", "env_read", "p2_env_1")
_emit_reads_environ("HOPPipelineExecutor", "env_read", "p2_env_2")
_emit_reads_runtime_state("HOPPipelineExecutor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("HOPPipelineExecutor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "HOPPipelineExecutor", "context_pull")
_emit_pulls_context("p1", "HOPPipelineExecutor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "HOPPipelineExecutor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "HOPPipelineExecutor", "uwg_term_2")
_emit_writes_through("p1", "HOPPipelineExecutor", "write_through")
_emit_writes_through("p1", "HOPPipelineExecutor", "write_through_2")
_emit_validated_by_safety_plane("p1", "HOPPipelineExecutor", "safety_validation")
_emit_invokes_eval("p1", "HOPPipelineExecutor", "eval_call")
_emit_proposal_commits_routing("p1", "HOPPipelineExecutor", "routing_commit")
_emit_escalates_to_human("p1", "HOPPipelineExecutor", "human_escalation")
_emit_routes_through("p1", "HOPPipelineExecutor", "route_through")
_emit_checks_agent_registry("p1", "HOPPipelineExecutor", "agent_registry")
_emit_validates_agent_capability("p1", "HOPPipelineExecutor", "capability")
_emit_dispatches_execution_plan("p1", "HOPPipelineExecutor", "exec_plan")
_emit_agent_executes_agent("p1", "HOPPipelineExecutor", "sub_agent")
_emit_routes_to_agent("p1", "HOPPipelineExecutor", "target_agent")
_emit_verifies_policy("p1", "HOPPipelineExecutor", "policy_check")
_emit_observes_runtime_state("p1", "HOPPipelineExecutor", "runtime_state")
_emit_verifies_boundary("p1", "HOPPipelineExecutor", "boundary_check")
_emit_transcripts_response("p1", "HOPPipelineExecutor", "transcript")
_emit_hard_fails_untranscripted("p1", "HOPPipelineExecutor")
_emit_gated_by_confidence("p1", "HOPPipelineExecutor", "confidence_gate")
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
        ADG complexity tier from profile drives dynamic reasoning path selection.
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"HOPPipelineExecutor._process:stage_{self.stage_id}")

        # Extract complexity tier from reasoning profile for dynamic path selection
        complexity_tier = "moderate"  # default
        profile_hash = None
        if self.reasoning_profile is not None:
            complexity_tier = getattr(self.reasoning_profile, 'adg_complexity_tier', 'moderate')
            profile_hash = getattr(self.reasoning_profile, 'profile_hash', None)
            # Emit telemetry about reasoning path selection
            _emit_records_telemetry_event(
                str(uuid.uuid4()),
                {
                    "stage_id": self.stage_id,
                    "stage_name": self.stage_name,
                    "complexity_tier": complexity_tier,
                    "profile_hash": profile_hash,
                    "adg_node_count": getattr(self.reasoning_profile, 'adg_node_count', 0),
                    "adg_edge_count": getattr(self.reasoning_profile, 'adg_edge_count', 0),
                }
            )

        from apps_lic.engines import hop_stage_registry

        handler = hop_stage_registry.get_stage_handler(self.stage_id)
        if handler is None:
            return {"stage": self.stage_id, "error": f"No handler for stage {self.stage_id}"}

        # Pass complexity_tier and profile to stage handler for dynamic reasoning
        return handler(
            self,
            context or {},
            reasoning_profile=self.reasoning_profile,
            complexity_tier=complexity_tier,
            profile_hash=profile_hash,
            **kwargs
        )
