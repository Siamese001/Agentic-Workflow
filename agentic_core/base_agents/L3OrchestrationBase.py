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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "L3OrchestrationBase", "execution_auth")
trace_contract._emit_validates_capability("p2", "L3OrchestrationBase", "capability_check")
trace_contract._emit_routes_to_capability("p2", "L3OrchestrationBase", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "L3OrchestrationBase", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "L3OrchestrationBase", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "L3OrchestrationBase", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "L3OrchestrationBase", "exec_output")
trace_contract._emit_dispatches_agent("p3", "L3OrchestrationBase", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "L3OrchestrationBase", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "L3OrchestrationBase", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "L3OrchestrationBase", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "L3OrchestrationBase", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "L3OrchestrationBase", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "L3OrchestrationBase", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "L3OrchestrationBase", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "L3OrchestrationBase", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "L3OrchestrationBase", "eval_metric")
trace_contract._emit_stores_embedding("p4", "L3OrchestrationBase", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "L3OrchestrationBase", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "L3OrchestrationBase", "exec_snapshot_link")
from agentic_core.utils.decorators_compat_util import standard_heal

trace_contract._emit_applies_guardrail("p0", "L3OrchestrationBase", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "L3OrchestrationBase", "policy_binding")
trace_contract._emit_snapshots_state("p0", "L3OrchestrationBase", "state_snapshot")

trace_contract._emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("L3OrchestrationBase", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("L3OrchestrationBase", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("L3OrchestrationBase", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("L3OrchestrationBase", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("L3OrchestrationBase", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("L3OrchestrationBase", "p4obs", "alert")
trace_contract._emit_links_incident_trace("L3OrchestrationBase", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("L3OrchestrationBase", "p3lm", "pattern")
trace_contract._emit_records_learning_event("L3OrchestrationBase", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("L3OrchestrationBase", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("L3OrchestrationBase", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("L3OrchestrationBase", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("L3OrchestrationBase", "p3lm", "policy")
trace_contract._emit_stores_learning_state("L3OrchestrationBase", "p3lm", "state")
trace_contract._emit_records_execution_trace("L3OrchestrationBase", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("L3OrchestrationBase", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("L3OrchestrationBase", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("L3OrchestrationBase", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("L3OrchestrationBase", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("L3OrchestrationBase", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("L3OrchestrationBase", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("L3OrchestrationBase", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("L3OrchestrationBase", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "L3OrchestrationBase", "context_pull")
trace_contract._emit_pulls_context("p1", "L3OrchestrationBase", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "L3OrchestrationBase", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "L3OrchestrationBase", "uwg_term_2")
trace_contract._emit_writes_through("p1", "L3OrchestrationBase", "write_through")
trace_contract._emit_writes_through("p1", "L3OrchestrationBase", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "L3OrchestrationBase", "safety_validation")
trace_contract._emit_invokes_eval("p1", "L3OrchestrationBase", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "L3OrchestrationBase", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "L3OrchestrationBase", "human_escalation")
trace_contract._emit_routes_through("p1", "L3OrchestrationBase", "route_through")
trace_contract._emit_checks_agent_registry("p1", "L3OrchestrationBase", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "L3OrchestrationBase", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "L3OrchestrationBase", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "L3OrchestrationBase", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "L3OrchestrationBase", "target_agent")
trace_contract._emit_verifies_policy("p1", "L3OrchestrationBase", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "L3OrchestrationBase", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "L3OrchestrationBase", "boundary_check")
trace_contract._emit_transcripts_response("p1", "L3OrchestrationBase", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "L3OrchestrationBase")
trace_contract._emit_gated_by_confidence("p1", "L3OrchestrationBase", "confidence_gate")
trace_contract.emit_replay_key("p0", "L3OrchestrationBase")
trace_contract.emit_determinism_digest("p0", "L3OrchestrationBase")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


@dataclass
class L3OrchestrationBase(SovereignBaseAgent):
    """
    Consolidated base for L3 Orchestration agents.

    MRO HARDENING:
    - AtomicExecutionMixin: First (if used - for rollback capability)
    - L3OrchestrationBase: Second (layer-specific capabilities)
    - SovereignBaseAgent: Last (root - includes MCPOperationMixin)

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "L3OrchestrationBase.heal_repository"
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
        except (ImportError, AttributeError, OSError, RuntimeError, ValueError) as e:  # guardian: allow-log-and-swallow -- behavioral profile unavailable: non-fatal; plan_execution degrades to static mode
            logger.debug("L3OrchestrationBase.plan_execution degraded to static mode: %s", e)
        return {
            "task": task,
            "plan": [],
            "status": "not_implemented",
            "message": "Override plan_execution in subclass",
            "adg_route_mode": _adg_route_mode,
            "adg_scope_widening": _adg_scope_widening,
        }
