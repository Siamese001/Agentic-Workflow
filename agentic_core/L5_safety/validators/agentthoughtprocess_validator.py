from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "agentthoughtprocess_validator")
emit_determinism_digest("p0", "agentthoughtprocess_validator")

_emit_dispatches_healing_run("p1", "agentthoughtprocess_validator", "L5")
_emit_routes_through("p1", "agentthoughtprocess_validator", "L5")
_emit_escalates_to_human("p1", "agentthoughtprocess_validator", "L5")
_emit_reads_policy_state("p1", "agentthoughtprocess_validator", "L5")

_emit_applies_guardrail("p0", "agentthoughtprocess_validator", "p0_governance")
_emit_snapshots_state("p0", "agentthoughtprocess_validator", "state_snapshot")

'\nReasoning & Cognitive Schemas\n=============================\nDefines the structured reasoning frameworks for Sovereign agents.\nThese models enforce "Chain of Thought" transparency and provide\noutput schemas for specialized tasks like coding and research.\n'
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class AgentThoughtProcess(BaseModel):
    """
    Forces the agent to show its work before acting.
    This is the "Physics" of your Agent - the schema it must follow.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
    reasoning_trace: list[str] = Field(
        ..., description="Step-by-step logic leading to the decision. Each step should be clear and atomic."
    )
    relevant_context_keys: list[str] = Field(
        ..., description="Keys from the SignalContext that were utilized in this thought process."
    )
    tool_choice: Literal["SEARCH", "CODE", "ANSWER", "DELEGATE", "TERMINATE"] = Field(
        ..., description="The action type to take"
    )
    tool_arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for the chosen tool")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in this decision (0.0 to 1.0)"
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
        default_factory=list, description="Potential safety concerns or limitations"
    )


class ResearchResult(BaseModel):
    """schema for research tasks."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    query_understanding: str = Field(..., description="How you interpreted the research question")
    sources: list[dict[str, str]] = Field(..., description="List of sources with 'url' and 'relevance' keys")
    key_findings: list[str] = Field(..., description="Main findings from the research")
    ConfidenceLevel: Literal["high", "medium", "low"] = Field(
        ..., description="Confidence in the research results"
    )
    follow_up_questions: list[str] = Field(
        default_factory=list, description="Suggested follow-up research questions"
    )


class AgentPlan(BaseModel):
    """Agent execution plan with reasoning and tool calls."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    reasoning: str = Field(..., description="High-level strategy for the overall Task")
    tool_calls: list[dict[str, Any]] = Field(
        ..., description="Ordered list of tool calls to execute the plan"
    )
