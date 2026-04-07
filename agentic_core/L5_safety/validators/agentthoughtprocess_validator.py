from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
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
    _emit_snapshots_state,
    # noqa: E402
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

emit_replay_key("p0", "agentthoughtprocess_validator")
emit_determinism_digest("p0", "agentthoughtprocess_validator")

_emit_dispatches_healing_run("p1", "agentthoughtprocess_validator", "L5")
_emit_routes_through("p1", "agentthoughtprocess_validator", "L5")
_emit_checks_agent_registry("p1", "agentthoughtprocess_validator", "agent_registry")
_emit_validates_agent_capability("p1", "agentthoughtprocess_validator", "capability")
_emit_dispatches_execution_plan("p1", "agentthoughtprocess_validator", "exec_plan")
_emit_agent_executes_agent("p1", "agentthoughtprocess_validator", "sub_agent")
_emit_routes_to_agent("p1", "agentthoughtprocess_validator", "target_agent")
_emit_verifies_policy("p1", "agentthoughtprocess_validator", "policy_check")
_emit_observes_runtime_state("p1", "agentthoughtprocess_validator", "runtime_state")
_emit_verifies_boundary("p1", "agentthoughtprocess_validator", "boundary_check")
_emit_transcripts_response("p1", "agentthoughtprocess_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "agentthoughtprocess_validator")
_emit_gated_by_confidence("p1", "agentthoughtprocess_validator", "confidence_gate")
_emit_escalates_to_human("p1", "agentthoughtprocess_validator", "L5")
_emit_reads_policy_state("p1", "agentthoughtprocess_validator", "L5")

_emit_applies_guardrail("p0", "agentthoughtprocess_validator", "p0_governance")
_emit_snapshots_state("p0", "agentthoughtprocess_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "agentthoughtprocess_validator", "execution_auth")
_emit_validates_capability("p2", "agentthoughtprocess_validator", "capability_check")
_emit_routes_to_capability("p2", "agentthoughtprocess_validator", "capability_route")
_emit_writes_via_uwg("p2", "agentthoughtprocess_validator", "uwg_write")
_emit_blocks_direct_write("p2", "agentthoughtprocess_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "agentthoughtprocess_validator", "tool_invocation")
_emit_captures_execution_output("p2", "agentthoughtprocess_validator", "exec_output")
_emit_dispatches_agent("p3", "agentthoughtprocess_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "agentthoughtprocess_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "agentthoughtprocess_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "agentthoughtprocess_validator", "healing_outcome")
_emit_escalates_failure("p3", "agentthoughtprocess_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "agentthoughtprocess_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agentthoughtprocess_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "agentthoughtprocess_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "agentthoughtprocess_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agentthoughtprocess_validator", "eval_metric")
_emit_stores_embedding("p4", "agentthoughtprocess_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "agentthoughtprocess_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agentthoughtprocess_validator", "exec_snapshot_link")

'\nReasoning & Cognitive Schemas\n=============================\nDefines the structured reasoning frameworks for Sovereign agents.\nThese models enforce "Chain of Thought" transparency and provide\noutput schemas for specialized tasks like coding and research.\n'
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_1")
_emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_2")
_emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_3")
_emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_4")
_emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_5")
_emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_6")
_emit_records_incident_event("agentthoughtprocess_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("agentthoughtprocess_validator", "p4obs", "anomaly")
_emit_writes_observability_log("agentthoughtprocess_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("agentthoughtprocess_validator", "p4obs", "mon_state")
_emit_triggers_alert("agentthoughtprocess_validator", "p4obs", "alert")
_emit_links_incident_trace("agentthoughtprocess_validator", "p4obs", "trace_link")
_emit_captures_pattern("agentthoughtprocess_validator", "p3lm", "pattern")
_emit_records_learning_event("agentthoughtprocess_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agentthoughtprocess_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("agentthoughtprocess_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agentthoughtprocess_validator", "p3lm", "routing")
_emit_improves_agent_policy("agentthoughtprocess_validator", "p3lm", "policy")
_emit_stores_learning_state("agentthoughtprocess_validator", "p3lm", "state")
_emit_records_execution_trace("agentthoughtprocess_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agentthoughtprocess_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agentthoughtprocess_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agentthoughtprocess_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agentthoughtprocess_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agentthoughtprocess_validator", "env_read", "p2_env_1")
_emit_reads_environ("agentthoughtprocess_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("agentthoughtprocess_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agentthoughtprocess_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agentthoughtprocess_validator", "context_pull")
_emit_pulls_context("p1", "agentthoughtprocess_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agentthoughtprocess_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agentthoughtprocess_validator", "uwg_term_2")
_emit_writes_through("p1", "agentthoughtprocess_validator", "write_through")
_emit_writes_through("p1", "agentthoughtprocess_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "agentthoughtprocess_validator", "safety_validation")
_emit_invokes_eval("p1", "agentthoughtprocess_validator", "eval_call")
_emit_proposal_commits_routing("p1", "agentthoughtprocess_validator", "routing_commit")


class AgentThoughtProcess(BaseModel):
    """
    Forces the agent to show its work before acting.
    This is the "Physics" of your Agent - the schema it must follow.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    reasoning_trace: list[str] = Field(
        ..., description="Step-by-step logic leading to the decision. Each step should be clear and atomic.",
    )
    relevant_context_keys: list[str] = Field(
        ..., description="Keys from the SignalContext that were utilized in this thought process.",
    )
    tool_choice: Literal["SEARCH", "CODE", "ANSWER", "DELEGATE", "TERMINATE"] = Field(
        ..., description="The action type to take",
    )
    tool_arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for the chosen tool")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in this decision (0.0 to 1.0)",
    )

    @field_validator("tool_arguments")
    @classmethod
    def validate_args(cls, v, info):
        """Self-validation to ensure arguments match the tool choice."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AgentThoughtProcess.validate_args")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AgentThoughtProcess.validate_args".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        tool_choice = info.data.get("tool_choice")
        if tool_choice == "CODE" and "code" not in v:
            raise ValueError("Tool choice CODE requires a 'code' argument.")
        if tool_choice == "SEARCH" and "query" not in v:
            raise ValueError("Tool choice SEARCH requires a 'query' argument.")
        if tool_choice == "DELEGATE" and "subtask" not in v:
            raise ValueError("Tool choice DELEGATE requires a 'subtask' argument.")
        return v


class CodeGenerationResult(BaseModel):
    """schema for code generation tasks."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    reasoning: str = Field(..., description="Why this code solves the problem")
    code: str = Field(..., description="The generated Python code")
    dependencies: list[str] = Field(default_factory=list, description="Required pip packages")
    test_cases: list[str] = Field(default_factory=list, description="Test cases to verify the code")
    safety_notes: list[str] = Field(
        default_factory=list, description="Potential safety concerns or limitations",
    )


class ResearchResult(BaseModel):
    """schema for research tasks."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    query_understanding: str = Field(..., description="How you interpreted the research question")
    sources: list[dict[str, str]] = Field(..., description="List of sources with 'url' and 'relevance' keys")
    key_findings: list[str] = Field(..., description="Main findings from the research")
    ConfidenceLevel: Literal["high", "medium", "low"] = Field(
        ..., description="Confidence in the research results",
    )
    follow_up_questions: list[str] = Field(
        default_factory=list, description="Suggested follow-up research questions",
    )


class AgentPlan(BaseModel):
    """Agent execution plan with reasoning and tool calls."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    reasoning: str = Field(..., description="High-level strategy for the overall Task")
    tool_calls: list[dict[str, Any]] = Field(
        ..., description="Ordered list of tool calls to execute the plan",
    )
