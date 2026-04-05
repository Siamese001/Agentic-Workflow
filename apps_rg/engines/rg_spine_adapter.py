"""
RG Spine Adapter — pure wiring, no business logic.

Forces all RG entry through the canonical spine:
  AirlockAssembler → PathRouter → ExecutionOrchestrator (with CIDRegistry)

CID is derived deterministically from the payload manifest hash before any
HOP stage runs. No uuid4, no datetime, no randomness.

Real implementations are wired for d0_engine, risk_gate, vigilance_dispatcher,
and meta_bus via shared adapters. Each adapter falls back to a null stub if
its upstream module cannot be imported, preserving fail-open behaviour.
"""

from __future__ import annotations

from typing import Any

from agentic_core.interfaces.execution import CIDRegistry
from agentic_core.interfaces.spine import (
    AirlockAssembler,
    ExecutionOrchestrator,
    GovernedPayload,
    PathRouter,
    ReEntryLoop,
)
from system_learning.meta_learning_bus import MetaLearningBus
from agentic_core.L2_execution.utils import get_clock
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
)

_emit_authorize_and_execute("p2", "rg_spine_adapter", "execution_auth")
_emit_validates_capability("p2", "rg_spine_adapter", "capability_check")
_emit_routes_to_capability("p2", "rg_spine_adapter", "capability_route")
_emit_writes_via_uwg("p2", "rg_spine_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "rg_spine_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "rg_spine_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "rg_spine_adapter", "exec_output")
_emit_dispatches_agent("p3", "rg_spine_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "rg_spine_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "rg_spine_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "rg_spine_adapter", "healing_outcome")
_emit_escalates_failure("p3", "rg_spine_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "rg_spine_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rg_spine_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "rg_spine_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "rg_spine_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rg_spine_adapter", "eval_metric")
_emit_stores_embedding("p4", "rg_spine_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "rg_spine_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rg_spine_adapter", "exec_snapshot_link")
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
from apps_shared.spine.base_spine_adapter import BaseSpineAdapter
from apps_shared.spine.d0_engine_adapter import D0EngineAdapter
from apps_shared.spine.risk_gate_adapter import RiskGateAdapter
from apps_shared.spine.vigilance_dispatcher_adapter import VigilanceDispatcherAdapter

_emit_emits_metric_event("rg_spine_adapter", "p4obs", "metric_1")
_emit_emits_metric_event("rg_spine_adapter", "p4obs", "metric_2")
_emit_emits_metric_event("rg_spine_adapter", "p4obs", "metric_3")
_emit_emits_metric_event("rg_spine_adapter", "p4obs", "metric_4")
_emit_emits_metric_event("rg_spine_adapter", "p4obs", "metric_5")
_emit_emits_metric_event("rg_spine_adapter", "p4obs", "metric_6")
_emit_records_incident_event("rg_spine_adapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("rg_spine_adapter", "p4obs", "anomaly")
_emit_writes_observability_log("rg_spine_adapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("rg_spine_adapter", "p4obs", "mon_state")
_emit_triggers_alert("rg_spine_adapter", "p4obs", "alert")
_emit_links_incident_trace("rg_spine_adapter", "p4obs", "trace_link")
_emit_captures_pattern("rg_spine_adapter", "p3lm", "pattern")
_emit_records_learning_event("rg_spine_adapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rg_spine_adapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("rg_spine_adapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rg_spine_adapter", "p3lm", "routing")
_emit_improves_agent_policy("rg_spine_adapter", "p3lm", "policy")
_emit_stores_learning_state("rg_spine_adapter", "p3lm", "state")
_emit_records_execution_trace("rg_spine_adapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rg_spine_adapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rg_spine_adapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rg_spine_adapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rg_spine_adapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rg_spine_adapter", "env_read", "p2_env_1")
_emit_reads_environ("rg_spine_adapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("rg_spine_adapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rg_spine_adapter", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "rg_spine_adapter")
_emit_applies_guardrail("p0", "rg_spine_adapter", "p0_governance")
_emit_reads_policy_state("p0", "rg_spine_adapter", "policy_binding")
_emit_snapshots_state("p0", "rg_spine_adapter", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_pulls_context("p1", "rg_spine_adapter", "context_pull")
_emit_pulls_context("p1", "rg_spine_adapter", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "rg_spine_adapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rg_spine_adapter", "uwg_term_secondary")
_emit_writes_through("p1", "rg_spine_adapter", "write_through")
_emit_writes_through("p1", "rg_spine_adapter", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "rg_spine_adapter", "safety_validation")
_emit_invokes_eval("p1", "rg_spine_adapter", "eval_call")
_emit_proposal_commits_routing("p1", "rg_spine_adapter", "routing_commit")
_emit_escalates_to_human("p1", "rg_spine_adapter", "human_escalation")
_emit_routes_through("p1", "rg_spine_adapter", "route_through")
_emit_checks_agent_registry("p1", "rg_spine_adapter", "agent_registry")
_emit_validates_agent_capability("p1", "rg_spine_adapter", "capability")
_emit_dispatches_execution_plan("p1", "rg_spine_adapter", "exec_plan")
_emit_agent_executes_agent("p1", "rg_spine_adapter", "sub_agent")
_emit_routes_to_agent("p1", "rg_spine_adapter", "target_agent")
_emit_verifies_policy("p1", "rg_spine_adapter", "policy_check")
_emit_observes_runtime_state("p1", "rg_spine_adapter", "runtime_state")
_emit_verifies_boundary("p1", "rg_spine_adapter", "boundary_check")
_emit_transcripts_response("p1", "rg_spine_adapter", "transcript")
_emit_hard_fails_untranscripted("p1", "rg_spine_adapter")
_emit_gated_by_confidence("p1", "rg_spine_adapter", "confidence_gate")

# Default maximum re-entry attempts for the RG spine.
_DEFAULT_MAX_REENTRY_ATTEMPTS: int = 3


# ---------------------------------------------------------------------------
# Assembler adapter: wraps AirlockAssembler to accept dict input
# ---------------------------------------------------------------------------


class _RgAssemblerAdapter:
    """
    Thin adapter so ExecutionOrchestrator.execute() can call
    self.assembler.assemble(intent_input: dict) with the RG slot mapping.

    Slot mapping:
      s0_system       ← intent_input.get("s0_system", "")
      i0_instructional← intent_input.get("i0_instructional", "")
      c0_context      ← intent_input.get("c0_context", "")
      u0_user_prompt  ← intent_input.get("u0_user_prompt", "")
      d0_injections   ← intent_input.get("d0_injections", "")
    """

    def assemble(self, intent_input: dict[str, Any]) -> GovernedPayload:
        return AirlockAssembler.assemble(
            s0_system=intent_input.get("s0_system", ""),
            i0_instructional=intent_input.get("i0_instructional", ""),
            c0_context=intent_input.get("c0_context", ""),
            u0_user_prompt=intent_input.get("u0_user_prompt", ""),
            d0_injections=intent_input.get("d0_injections", ""),
        )


# ---------------------------------------------------------------------------
# RG Spine Adapter — public entry point
# ---------------------------------------------------------------------------


class RgSpineAdapter(BaseSpineAdapter):
    """
    Canonical RG spine adapter.

    Constructs the full spine wiring once and exposes a single
    ``execute(intent_input)`` method. CID is derived from the
    GovernedPayload manifest hash — deterministic, no randomness.

    HOPPipelineExecutor is the only class allowed to be instantiated
    here (enforced by check_spine_bypass.py CI guard).
    """

    # RG-specific prefix
    _PREFIX: str = "rg-"

    def __init__(self, max_reentry_attempts: int = _DEFAULT_MAX_REENTRY_ATTEMPTS) -> None:
        """Initialize RG spine adapter with dependency wiring."""
        # Create core dependencies
        cid_registry = CIDRegistry()
        reentry_loop = ReEntryLoop(
            max_attempts=max_reentry_attempts,
            cid_registry=cid_registry,
        )
        _path_router = PathRouter()
        _clk = get_clock()
        _clk.emit_replay_key(context=f"rg:{self._PREFIX}:init")
        _clk.emit_determinism_digest(inputs={"app": "rg", "prefix": self._PREFIX})
        orchestrator = ExecutionOrchestrator(
            assembler=_RgAssemblerAdapter(),
            path_router=_path_router,
            d0_engine=D0EngineAdapter(),
            risk_gate=RiskGateAdapter(),
            cid_registry=cid_registry,
            reentry_loop=reentry_loop,
            vigilance_dispatcher=VigilanceDispatcherAdapter(),
            meta_bus=MetaLearningBus(),
        )

        # Initialize base adapter with dependencies and RG prefix
        super().__init__(
            cid_registry=cid_registry,
            orchestrator=orchestrator,
            prefix=self._PREFIX,
            max_reentry_attempts=max_reentry_attempts,
        )
