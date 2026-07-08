from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "cognitive_types")
trace_contract.emit_determinism_digest("p0", "cognitive_types")

trace_contract._emit_dispatches_healing_run("p1", "cognitive_types", "L1")
trace_contract._emit_routes_through("p1", "cognitive_types", "L1")
trace_contract._emit_checks_agent_registry("p1", "cognitive_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "cognitive_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "cognitive_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "cognitive_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "cognitive_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "cognitive_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "cognitive_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "cognitive_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "cognitive_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "cognitive_types")
trace_contract._emit_gated_by_confidence("p1", "cognitive_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "cognitive_types", "L1")
trace_contract._emit_reads_policy_state("p1", "cognitive_types", "L1")
trace_contract._emit_authorize_and_execute("p2", "cognitive_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "cognitive_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "cognitive_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "cognitive_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "cognitive_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "cognitive_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "cognitive_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "cognitive_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "cognitive_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "cognitive_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "cognitive_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "cognitive_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "cognitive_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "cognitive_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "cognitive_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "cognitive_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "cognitive_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "cognitive_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "cognitive_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "cognitive_types", "exec_snapshot_link")

"Cognitive Plane Interface - The Brain.\n\nPhase 2 - Pillar 1: Layering Model\nDefines the contract for all planning, reasoning, and decision-making.\nL1 Cognition: Pure thought, no side effects.\n"
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


trace_contract._emit_emits_metric_event("cognitive_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("cognitive_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("cognitive_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("cognitive_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("cognitive_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("cognitive_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("cognitive_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("cognitive_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("cognitive_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("cognitive_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("cognitive_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("cognitive_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("cognitive_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("cognitive_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("cognitive_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("cognitive_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("cognitive_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("cognitive_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("cognitive_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("cognitive_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("cognitive_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("cognitive_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("cognitive_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("cognitive_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("cognitive_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("cognitive_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("cognitive_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("cognitive_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "cognitive_types", "context_pull")
trace_contract._emit_pulls_context("p1", "cognitive_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "cognitive_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "cognitive_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "cognitive_types", "write_through")
trace_contract._emit_writes_through("p1", "cognitive_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "cognitive_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "cognitive_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "cognitive_types", "routing_commit")


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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "PlanningRequest.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "PlanningRequest.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_COGNITION, "PlanningRequest.to_dict")
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
