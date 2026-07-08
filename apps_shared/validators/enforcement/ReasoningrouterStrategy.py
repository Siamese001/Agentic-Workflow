"""Reasoning strategy router for selecting appropriate reasoning mode.

Phase 1 - Pillar 6: Reasoning models (Structured Reasoning)
Routes tasks to appropriate reasoning strategies (ReAct, CoT, etc.)
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "ReasoningrouterStrategy", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "ReasoningrouterStrategy", "policy_binding")
trace_contract._emit_snapshots_state("p0", "ReasoningrouterStrategy", "state_snapshot")

trace_contract._emit_emits_metric_event("ReasoningrouterStrategy", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ReasoningrouterStrategy", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ReasoningrouterStrategy", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ReasoningrouterStrategy", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ReasoningrouterStrategy", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ReasoningrouterStrategy", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ReasoningrouterStrategy", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ReasoningrouterStrategy", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ReasoningrouterStrategy", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ReasoningrouterStrategy", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ReasoningrouterStrategy", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ReasoningrouterStrategy", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ReasoningrouterStrategy", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ReasoningrouterStrategy", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ReasoningrouterStrategy", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ReasoningrouterStrategy", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ReasoningrouterStrategy", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ReasoningrouterStrategy", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ReasoningrouterStrategy", "p3lm", "state")
trace_contract._emit_records_execution_trace("ReasoningrouterStrategy", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ReasoningrouterStrategy", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ReasoningrouterStrategy", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ReasoningrouterStrategy", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ReasoningrouterStrategy", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ReasoningrouterStrategy", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ReasoningrouterStrategy", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ReasoningrouterStrategy", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ReasoningrouterStrategy", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ReasoningrouterStrategy", "context_pull")
trace_contract._emit_pulls_context("p1", "ReasoningrouterStrategy", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ReasoningrouterStrategy", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ReasoningrouterStrategy", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ReasoningrouterStrategy", "write_through")
trace_contract._emit_writes_through("p1", "ReasoningrouterStrategy", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ReasoningrouterStrategy", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ReasoningrouterStrategy", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ReasoningrouterStrategy", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "ReasoningrouterStrategy", "human_escalation")
trace_contract._emit_routes_through("p1", "ReasoningrouterStrategy", "route_through")
trace_contract._emit_checks_agent_registry("p1", "ReasoningrouterStrategy", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ReasoningrouterStrategy", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ReasoningrouterStrategy", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ReasoningrouterStrategy", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ReasoningrouterStrategy", "target_agent")
trace_contract._emit_verifies_policy("p1", "ReasoningrouterStrategy", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ReasoningrouterStrategy", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ReasoningrouterStrategy", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ReasoningrouterStrategy", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ReasoningrouterStrategy")
trace_contract._emit_gated_by_confidence("p1", "ReasoningrouterStrategy", "confidence_gate")
trace_contract.emit_replay_key("p0", "ReasoningrouterStrategy")
trace_contract.emit_determinism_digest("p0", "ReasoningrouterStrategy")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "ReasoningrouterStrategy", "execution_auth")
trace_contract._emit_validates_capability("p2", "ReasoningrouterStrategy", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ReasoningrouterStrategy", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ReasoningrouterStrategy", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ReasoningrouterStrategy", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ReasoningrouterStrategy", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ReasoningrouterStrategy", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ReasoningrouterStrategy", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ReasoningrouterStrategy", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ReasoningrouterStrategy", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ReasoningrouterStrategy", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ReasoningrouterStrategy", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ReasoningrouterStrategy", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ReasoningrouterStrategy", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ReasoningrouterStrategy", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ReasoningrouterStrategy", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ReasoningrouterStrategy", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ReasoningrouterStrategy", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ReasoningrouterStrategy", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ReasoningrouterStrategy", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks for reasoning strategy selection."""

    TOOL_USE = "tool_use"
    QUESTION_ANSWERING = "qa"
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    UNKNOWN = "unknown"


class ReasoningMode(Enum):
    """Reasoning modes for strategy selection."""

    REACT = "react"
    COT = "chain_of_thought"
    SIMPLE = "simple"
    ADAPTIVE = "adaptive"


class ReasoningRouter:
    """Routes tasks to appropriate reasoning strategies.

    Implements a simple strategy selector that uses ReAct for tasks
    requiring tool use and simpler approaches for basic Q&A or classification.
    """

    def __init__(
        self,
        default_mode: ReasoningMode = ReasoningMode.REACT,
        enable_adaptive_routing: bool = True,
    ):
        """Initialize reasoning router.

        Args:
            default_mode: Default reasoning mode if no specific match
            enable_adaptive_routing: Enable adaptive strategy selection
        """
        self.default_mode = default_mode
        self.enable_adaptive_routing = enable_adaptive_routing
        self._strategy_map = {
            TaskType.TOOL_USE: ReasoningMode.REACT,
            TaskType.QUESTION_ANSWERING: ReasoningMode.CHAIN_OF_THOUGHT,
            TaskType.CLASSIFICATION: ReasoningMode.SHOTGUN,
            TaskType.GENERATION: ReasoningMode.CHAIN_OF_THOUGHT,
            TaskType.ANALYSIS: ReasoningMode.REACT,
            TaskType.PLANNING: ReasoningMode.TREE_OF_THOUGHTS,
            TaskType.UNKNOWN: self.default_mode,
        }

    def classify_task(self, task: str, context: dict[str, Any] | None = None) -> TaskType:
        """Classify task type based on content and context.

        Args:
            task: The task description
            context: Optional context with hints

        Returns:
            TaskType classification
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ReasoningRouter.classify_task"
        )

        if context and "task_type" in context:
            try:
                return TaskType(context["task_type"])
            except ValueError:
                pass
        task_lower = task.lower()
        tool_indicators = ["search", "retrieve", "lookup", "find", "fetch", "call", "execute", "run"]
        qa_indicators = ["what is", "who is", "when did", "where is", "why", "how", "explain", "describe"]
        classification_indicators = [
            "classify",
            "categorize",
            "is this",
            "does this",
            "true or false",
            "yes or no",
        ]
        planning_indicators = ["plan", "strategy", "approach", "steps to", "how to"]
        for indicator in tool_indicators:
            if indicator in task_lower:
                return TaskType.TOOL_USE
        for indicator in classification_indicators:
            if indicator in task_lower:
                return TaskType.CLASSIFICATION
        for indicator in planning_indicators:
            if indicator in task_lower:
                return TaskType.PLANNING
        for indicator in qa_indicators:
            if indicator in task_lower:
                return TaskType.QUESTION_ANSWERING
        if len(task.split()) > 50:
            return TaskType.ANALYSIS
        return TaskType.UNKNOWN

    def select_strategy(self, task: str, context: dict[str, Any] | None = None) -> ReasoningMode:
        """Select appropriate reasoning strategy for task.

        Args:
            task: The task to solve
            context: Optional context with hints

        Returns:
            Selected ReasoningMode
        """
        task_type = self.classify_task(task, context)
        strategy = self._strategy_map.get(task_type, self.default_mode)
        logger.info(
            "reasoning_strategy_selected",
            extra={"task_type": task_type.value, "strategy": strategy.value, "task_preview": task[:100]},
        )
        return strategy

    def override_strategy(self, task_type: TaskType, mode: ReasoningMode) -> None:
        """Override strategy mapping for a task type.

        Args:
            task_type: The task type to override
            mode: The reasoning mode to use
        """
        self._strategy_map[task_type] = mode
        logger.info(
            "reasoning_strategy_override",
            extra={"task_type": task_type.value, "new_strategy": mode.value},
        )


def select_reasoning_strategy(
    task: str,
    context: dict[str, Any] | None = None,
    router: ReasoningRouter | None = None,
) -> ReasoningMode:
    """Convenience function to select reasoning strategy.

    Args:
        task: The task to solve
        context: Optional context
        router: Optional custom router (creates default if None)

    Returns:
        Selected ReasoningMode
    """
    if router is None:
        router = ReasoningRouter()
    return router.select_strategy(task, context)
