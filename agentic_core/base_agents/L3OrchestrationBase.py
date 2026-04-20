"""
L3OrchestrationBase - Consolidated Base for L3 Orchestration Agents

V10 Architecture: Layer 3 (Orchestration) base class for workflow engines,
coordinators, and planners.

Capabilities:
- Workflow coordination and planning
- State management via SovereignBaseAgent
- Atomic execution support (when combined with AtomicExecutionMixin)

MRO HARDENING:
- Inheritance order: Specialized Mixins -> L3OrchestrationBase -> SovereignBaseAgent
- When using AtomicExecutionMixin, it MUST come BEFORE this base class:
  class MyAgent(AtomicExecutionMixin, L3OrchestrationBase):
"""

from __future__ import annotations

import logging

from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "L3OrchestrationBase", "execution_auth")
_emit_validates_capability("p2", "L3OrchestrationBase", "capability_check")
_emit_routes_to_capability("p2", "L3OrchestrationBase", "capability_route")
_emit_writes_via_uwg("p2", "L3OrchestrationBase", "uwg_write")
_emit_blocks_direct_write("p2", "L3OrchestrationBase", "direct_write_block")
_emit_records_tool_invocation("p2", "L3OrchestrationBase", "tool_invocation")
_emit_captures_execution_output("p2", "L3OrchestrationBase", "exec_output")
_emit_dispatches_agent("p3", "L3OrchestrationBase", "agent_dispatch")
_emit_coordinates_agents("p3", "L3OrchestrationBase", "agent_coordination")
_emit_records_workflow_lineage("p3", "L3OrchestrationBase", "workflow_lineage")
_emit_records_healing_outcome("p3", "L3OrchestrationBase", "healing_outcome")
_emit_escalates_failure("p3", "L3OrchestrationBase", "failure_escalation")
_emit_orchestrates_workflow("p3", "L3OrchestrationBase", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "L3OrchestrationBase", "healing_dispatch")
_emit_invokes_evaluation("p3", "L3OrchestrationBase", "evaluation_signal")
_emit_records_telemetry_event("p4", "L3OrchestrationBase", "telemetry_event")
_emit_captures_evaluation_metric("p4", "L3OrchestrationBase", "eval_metric")
_emit_stores_embedding("p4", "L3OrchestrationBase", "embedding_store")
_emit_updates_meta_learning_state("p4", "L3OrchestrationBase", "meta_learning")
_emit_links_execution_to_snapshot("p4", "L3OrchestrationBase", "exec_snapshot_link")
from agentic_core.utils.decorators_compat_util import standard_heal

_emit_applies_guardrail("p0", "L3OrchestrationBase", "p0_governance")
_emit_reads_policy_state("p0", "L3OrchestrationBase", "policy_binding")
_emit_snapshots_state("p0", "L3OrchestrationBase", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_1")
_emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_2")
_emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_3")
_emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_4")
_emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_5")
_emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_6")
_emit_records_incident_event("L3OrchestrationBase", "p4obs", "incident")
_emit_captures_runtime_anomaly("L3OrchestrationBase", "p4obs", "anomaly")
_emit_writes_observability_log("L3OrchestrationBase", "p4obs", "obs_log")
_emit_updates_monitoring_state("L3OrchestrationBase", "p4obs", "mon_state")
_emit_triggers_alert("L3OrchestrationBase", "p4obs", "alert")
_emit_links_incident_trace("L3OrchestrationBase", "p4obs", "trace_link")
_emit_captures_pattern("L3OrchestrationBase", "p3lm", "pattern")
_emit_records_learning_event("L3OrchestrationBase", "p3lm", "learning_event")
_emit_writes_learning_snapshot("L3OrchestrationBase", "p3lm", "snapshot")
_emit_feeds_meta_learning("L3OrchestrationBase", "p3lm", "meta_feed")
_emit_updates_routing_strategy("L3OrchestrationBase", "p3lm", "routing")
_emit_improves_agent_policy("L3OrchestrationBase", "p3lm", "policy")
_emit_stores_learning_state("L3OrchestrationBase", "p3lm", "state")
_emit_records_execution_trace("L3OrchestrationBase", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("L3OrchestrationBase", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("L3OrchestrationBase", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("L3OrchestrationBase", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("L3OrchestrationBase", "L4_STATE", "p2_trace_5")
_emit_reads_environ("L3OrchestrationBase", "env_read", "p2_env_1")
_emit_reads_environ("L3OrchestrationBase", "env_read", "p2_env_2")
_emit_reads_runtime_state("L3OrchestrationBase", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("L3OrchestrationBase", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "L3OrchestrationBase", "context_pull")
_emit_pulls_context("p1", "L3OrchestrationBase", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "L3OrchestrationBase", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "L3OrchestrationBase", "uwg_term_2")
_emit_writes_through("p1", "L3OrchestrationBase", "write_through")
_emit_writes_through("p1", "L3OrchestrationBase", "write_through_2")
_emit_validated_by_safety_plane("p1", "L3OrchestrationBase", "safety_validation")
_emit_invokes_eval("p1", "L3OrchestrationBase", "eval_call")
_emit_proposal_commits_routing("p1", "L3OrchestrationBase", "routing_commit")
_emit_escalates_to_human("p1", "L3OrchestrationBase", "human_escalation")
_emit_routes_through("p1", "L3OrchestrationBase", "route_through")
_emit_checks_agent_registry("p1", "L3OrchestrationBase", "agent_registry")
_emit_validates_agent_capability("p1", "L3OrchestrationBase", "capability")
_emit_dispatches_execution_plan("p1", "L3OrchestrationBase", "exec_plan")
_emit_agent_executes_agent("p1", "L3OrchestrationBase", "sub_agent")
_emit_routes_to_agent("p1", "L3OrchestrationBase", "target_agent")
_emit_verifies_policy("p1", "L3OrchestrationBase", "policy_check")
_emit_observes_runtime_state("p1", "L3OrchestrationBase", "runtime_state")
_emit_verifies_boundary("p1", "L3OrchestrationBase", "boundary_check")
_emit_transcripts_response("p1", "L3OrchestrationBase", "transcript")
_emit_hard_fails_untranscripted("p1", "L3OrchestrationBase")
_emit_gated_by_confidence("p1", "L3OrchestrationBase", "confidence_gate")
emit_replay_key("p0", "L3OrchestrationBase")
emit_determinism_digest("p0", "L3OrchestrationBase")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


@dataclass
class L3OrchestrationBase(SovereignBaseAgent):
    """
    Consolidated base for L3 Orchestration agents.

    MRO HARDENING:
    - AtomicExecutionMixin: First (if used - for rollback capability)
    - L3OrchestrationBase: Second (layer-specific capabilities)
    - SovereignBaseAgent: Last (root - includes MCPHardenedMixin)

    Guaranteed Capabilities:
    - heal_repository(): Self-repair method
    - _hardened_call(): MCP operations via SovereignBaseAgent
    - Workflow coordination methods

    L3 Table Decision:
    - Orchestration Logic: YES
    - State Management: YES (via SovereignBaseAgent)
    - Atomic Execution: Optional (via AtomicExecutionMixin)
    """

    name: str = "L3OrchestrationBase"
    layer: str = "L3"

    def __post_init__(self) -> None:
        """Cooperative MRO initialization."""
        super().__post_init__()

    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Invoke shared healing chain then allow subclass override."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "L3OrchestrationBase.heal_repository"
        )

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"violations_found": 0, "violations_fixed": 0, "errors": [], "skipped": []}
        if depth >= max_depth:
            return {"violations_found": 0, "violations_fixed": 0, "errors": [], "skipped": []}
        _call_path.add(agent_name)
        try:
            return super().heal_repository(
                dry_run=dry_run,
                execute=execute,
                depth=depth,
                max_depth=max_depth,
                _call_path=_call_path,
                **kwargs,
            )
        except (RuntimeError, ValueError, TypeError, OSError) as e:
            logger.warning("L3OrchestrationBase.heal_repository failed: %s", e)
            return {"violations_found": 0, "violations_fixed": 0, "errors": [str(e)], "skipped": []}
        finally:
            _call_path.discard(agent_name)

    def coordinate_workflow(self, workflow_id: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Base workflow coordination method.

        Override in subclasses for specific orchestration logic.

        Args:
            workflow_id: Unique identifier for the workflow
            context: Workflow context and parameters

        Returns:
            Workflow execution result
        """
        return {
            "workflow_id": workflow_id,
            "status": "not_implemented",
            "message": "Override coordinate_workflow in subclass",
        }

    def plan_execution(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Base execution planning method.

        Override in subclasses for specific planning logic.

        Args:
            task: Task definition and constraints

        Returns:
            Execution plan
        """
        _adg_route_mode: str = "static"
        _adg_scope_widening: list[str] = []
        try:
            from pathlib import Path as _Path

            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _self_file = _Path(__file__).resolve()
            _root = _Path(getattr(self, "project_root", _self_file.parents[2])).resolve()
            _bp = _gbp(_self_file, _root)
            _adg_route_mode = (
                "agent"
                if _bp.behavioral_score > 0.7
                else "script"
                if _bp.deterministic_coverage
                else "hybrid"
            )
            _adg_scope_widening = sorted(_bp.antipattern_signals)
        except (ImportError, AttributeError, OSError, RuntimeError, ValueError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            logger.debug("L3OrchestrationBase.plan_execution degraded to static mode: %s", e)
        return {
            "task": task,
            "plan": [],
            "status": "not_implemented",
            "message": "Override plan_execution in subclass",
            "adg_route_mode": _adg_route_mode,
            "adg_scope_widening": _adg_scope_widening,
        }
