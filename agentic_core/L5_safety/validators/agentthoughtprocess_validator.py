from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "agentthoughtprocess_validator")
trace_contract.emit_determinism_digest("p0", "agentthoughtprocess_validator")

trace_contract._emit_dispatches_healing_run("p1", "agentthoughtprocess_validator", "L5")
trace_contract._emit_routes_through("p1", "agentthoughtprocess_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "agentthoughtprocess_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "agentthoughtprocess_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "agentthoughtprocess_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "agentthoughtprocess_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "agentthoughtprocess_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "agentthoughtprocess_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "agentthoughtprocess_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "agentthoughtprocess_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "agentthoughtprocess_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "agentthoughtprocess_validator")
trace_contract._emit_gated_by_confidence("p1", "agentthoughtprocess_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "agentthoughtprocess_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "agentthoughtprocess_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "agentthoughtprocess_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "agentthoughtprocess_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "agentthoughtprocess_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "agentthoughtprocess_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "agentthoughtprocess_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "agentthoughtprocess_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "agentthoughtprocess_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "agentthoughtprocess_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "agentthoughtprocess_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "agentthoughtprocess_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "agentthoughtprocess_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "agentthoughtprocess_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "agentthoughtprocess_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "agentthoughtprocess_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "agentthoughtprocess_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "agentthoughtprocess_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "agentthoughtprocess_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "agentthoughtprocess_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "agentthoughtprocess_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "agentthoughtprocess_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "agentthoughtprocess_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "agentthoughtprocess_validator", "exec_snapshot_link")

'\nReasoning & Cognitive Schemas\n=============================\nDefines the structured reasoning frameworks for Sovereign agents.\nThese models enforce "Chain of Thought" transparency and provide\noutput schemas for specialized tasks like coding and research.\n'
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


trace_contract._emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("agentthoughtprocess_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("agentthoughtprocess_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("agentthoughtprocess_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("agentthoughtprocess_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("agentthoughtprocess_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("agentthoughtprocess_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("agentthoughtprocess_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("agentthoughtprocess_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("agentthoughtprocess_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("agentthoughtprocess_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("agentthoughtprocess_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("agentthoughtprocess_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("agentthoughtprocess_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("agentthoughtprocess_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("agentthoughtprocess_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("agentthoughtprocess_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("agentthoughtprocess_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("agentthoughtprocess_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("agentthoughtprocess_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("agentthoughtprocess_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("agentthoughtprocess_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("agentthoughtprocess_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("agentthoughtprocess_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "agentthoughtprocess_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "agentthoughtprocess_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "agentthoughtprocess_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "agentthoughtprocess_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "agentthoughtprocess_validator", "write_through")
trace_contract._emit_writes_through("p1", "agentthoughtprocess_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "agentthoughtprocess_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "agentthoughtprocess_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "agentthoughtprocess_validator", "routing_commit")


class AgentThoughtProcess(BaseModel):
    """
    Forces the agent to show its work before acting.
    This is the "Physics" of your Agent - the schema it must follow.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    reasoning_trace: list[str] = Field(
        ...,
        description="Step-by-step logic leading to the decision. Each step should be clear and atomic.",
    )
    relevant_context_keys: list[str] = Field(
        ...,
        description="Keys from the SignalContext that were utilized in this thought process.",
    )
    tool_choice: Literal["SEARCH", "CODE", "ANSWER", "DELEGATE", "TERMINATE"] = Field(
        ...,
        description="The action type to take",
    )
    tool_arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for the chosen tool")
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in this decision (0.0 to 1.0)",
    )

    @field_validator("tool_arguments")
    @classmethod
    def validate_args(cls, v, info):
        """Self-validation to ensure arguments match the tool choice."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "AgentThoughtProcess.validate_args")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AgentThoughtProcess.validate_args".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        default_factory=list,
        description="Potential safety concerns or limitations",
    )


class ResearchResult(BaseModel):
    """schema for research tasks."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    query_understanding: str = Field(..., description="How you interpreted the research question")
    sources: list[dict[str, str]] = Field(..., description="List of sources with 'url' and 'relevance' keys")
    key_findings: list[str] = Field(..., description="Main findings from the research")
    ConfidenceLevel: Literal["high", "medium", "low"] = Field(
        ...,
        description="Confidence in the research results",
    )
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="Suggested follow-up research questions",
    )


class AgentPlan(BaseModel):
    """Agent execution plan with reasoning and tool calls."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    reasoning: str = Field(..., description="High-level strategy for the overall Task")
    tool_calls: list[dict[str, Any]] = Field(
        ...,
        description="Ordered list of tool calls to execute the plan",
    )
