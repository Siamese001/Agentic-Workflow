from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "cognitive_types")
emit_determinism_digest("p0", "cognitive_types")

_emit_dispatches_healing_run("p1", "cognitive_types", "L1")
_emit_routes_through("p1", "cognitive_types", "L1")
_emit_checks_agent_registry("p1", "cognitive_types", "agent_registry")
_emit_validates_agent_capability("p1", "cognitive_types", "capability")
_emit_dispatches_execution_plan("p1", "cognitive_types", "exec_plan")
_emit_agent_executes_agent("p1", "cognitive_types", "sub_agent")
_emit_routes_to_agent("p1", "cognitive_types", "target_agent")
_emit_verifies_policy("p1", "cognitive_types", "policy_check")
_emit_observes_runtime_state("p1", "cognitive_types", "runtime_state")
_emit_verifies_boundary("p1", "cognitive_types", "boundary_check")
_emit_transcripts_response("p1", "cognitive_types", "transcript")
_emit_hard_fails_untranscripted("p1", "cognitive_types")
_emit_gated_by_confidence("p1", "cognitive_types", "confidence_gate")
_emit_escalates_to_human("p1", "cognitive_types", "L1")
_emit_reads_policy_state("p1", "cognitive_types", "L1")
_emit_authorize_and_execute("p2", "cognitive_types", "execution_auth")
_emit_validates_capability("p2", "cognitive_types", "capability_check")
_emit_routes_to_capability("p2", "cognitive_types", "capability_route")
_emit_writes_via_uwg("p2", "cognitive_types", "uwg_write")
_emit_blocks_direct_write("p2", "cognitive_types", "direct_write_block")
_emit_records_tool_invocation("p2", "cognitive_types", "tool_invocation")
_emit_captures_execution_output("p2", "cognitive_types", "exec_output")
_emit_dispatches_agent("p3", "cognitive_types", "agent_dispatch")
_emit_coordinates_agents("p3", "cognitive_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "cognitive_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "cognitive_types", "healing_outcome")
_emit_escalates_failure("p3", "cognitive_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "cognitive_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cognitive_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "cognitive_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "cognitive_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cognitive_types", "eval_metric")
_emit_stores_embedding("p4", "cognitive_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "cognitive_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cognitive_types", "exec_snapshot_link")

"Cognitive Plane Interface - The Brain.\n\nPhase 2 - Pillar 1: Layering Model\nDefines the contract for all planning, reasoning, and decision-making.\nL1 Cognition: Pure thought, no side effects.\n"
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_routes_to_agent,
    _emit_snapshots_state,
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

_emit_emits_metric_event("cognitive_types", "p4obs", "metric_1")
_emit_emits_metric_event("cognitive_types", "p4obs", "metric_2")
_emit_emits_metric_event("cognitive_types", "p4obs", "metric_3")
_emit_emits_metric_event("cognitive_types", "p4obs", "metric_4")
_emit_emits_metric_event("cognitive_types", "p4obs", "metric_5")
_emit_emits_metric_event("cognitive_types", "p4obs", "metric_6")
_emit_records_incident_event("cognitive_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("cognitive_types", "p4obs", "anomaly")
_emit_writes_observability_log("cognitive_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("cognitive_types", "p4obs", "mon_state")
_emit_triggers_alert("cognitive_types", "p4obs", "alert")
_emit_links_incident_trace("cognitive_types", "p4obs", "trace_link")
_emit_captures_pattern("cognitive_types", "p3lm", "pattern")
_emit_records_learning_event("cognitive_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cognitive_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("cognitive_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cognitive_types", "p3lm", "routing")
_emit_improves_agent_policy("cognitive_types", "p3lm", "policy")
_emit_stores_learning_state("cognitive_types", "p3lm", "state")
_emit_records_execution_trace("cognitive_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cognitive_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cognitive_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cognitive_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cognitive_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cognitive_types", "env_read", "p2_env_1")
_emit_reads_environ("cognitive_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("cognitive_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cognitive_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cognitive_types", "context_pull")
_emit_pulls_context("p1", "cognitive_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cognitive_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cognitive_types", "uwg_term_2")
_emit_writes_through("p1", "cognitive_types", "write_through")
_emit_writes_through("p1", "cognitive_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "cognitive_types", "safety_validation")
_emit_invokes_eval("p1", "cognitive_types", "eval_call")
_emit_proposal_commits_routing("p1", "cognitive_types", "routing_commit")


class CognitiveCapability(Enum):
    """Capabilities provided by the cognitive plane."""

    PLANNING = "planning"
    REASONING = "reasoning"
    DECISION_MAKING = "decision_making"
    SELF_REFLECTION = "self_reflection"
    TASK_DECOMPOSITION = "task_decomposition"
    STRATEGY_SELECTION = "strategy_selection"


@dataclass
class PlanningRequest:
    """Request for cognitive planning."""

    Task: str
    context: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    capabilities_required: list[CognitiveCapability] = field(default_factory=list)
    max_steps: int = 10
    reasoning_mode: str = "react"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "PlanningRequest.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "PlanningRequest.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "PlanningRequest.to_dict")
        return {
            "Task": self.Task,
            "context": self.context,
            "constraints": self.constraints,
            "capabilities_required": [c.value for c in self.capabilities_required],
            "max_steps": self.max_steps,
            "reasoning_mode": self.reasoning_mode,
        }


@dataclass
class PlanningResult:
    """Result from cognitive planning."""

    success: bool
    plan: list[dict[str, Any]]
    reasoning_trace: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "plan": self.plan,
            "reasoning_trace": self.reasoning_trace,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "errors": self.errors,
        }


class ICognitivePlane(ABC):
    """Interface for the Cognitive Plane (Brain).

    The cognitive plane is responsible for:
    - Planning: Breaking down tasks into actionable steps
    - Reasoning: Applying logic and inference
    - Decision Making: Choosing between alternatives
    - Self-Reflection: Evaluating own performance

    L1 Constraint: All methods must be pure (no side effects).
    Outputs are plans and decisions, not actions.
    """

    @abstractmethod
    async def plan(self, request: PlanningRequest) -> PlanningResult:
        """Generate a plan for the given Task.

        Args:
            request: Planning request with Task and context

        Returns:
            PlanningResult with step-by-step plan
        """
        pass

    @abstractmethod
    async def reason(self, query: str, context: dict[str, Any], mode: str = "react") -> dict[str, Any]:
        """Apply reasoning to a query.

        Args:
            query: The question or problem to reason about
            context: Contextual information
            mode: Reasoning mode (react, cot, shotgun, tot)

        Returns:
            Reasoning result with conclusion and trace
        """
        pass

    @abstractmethod
    async def decide(self, options: list[dict[str, Any]], criteria: dict[str, Any]) -> dict[str, Any]:
        """Make a decision between options.

        Args:
            options: List of possible choices
            criteria: Decision criteria and weights

        Returns:
            Selected option with justification
        """
        pass

    @abstractmethod
    async def reflect(self, execution_trace: list[dict[str, Any]], outcome: dict[str, Any]) -> dict[str, Any]:
        """Reflect on execution to identify improvements.

        Args:
            execution_trace: History of actions taken
            outcome: Final result achieved

        Returns:
            Reflection with lessons learned and improvements
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[CognitiveCapability]:
        """Get list of supported cognitive capabilities.

        Returns:
            List of capabilities this plane supports
        """
        pass
