from __future__ import annotations
'\nReasoning & Cognitive Schemas\n=============================\nDefines the structured reasoning frameworks for Sovereign agents.\nThese models enforce "Chain of Thought" transparency and provide\noutput schemas for specialized tasks like coding and research.\n'
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class AgentThoughtProcess(BaseModel):
    """
    Forces the agent to show its work before acting.
    This is the "Physics" of your Agent - the schema it must follow.
    """
    model_config = ConfigDict(frozen=True, extra='forbid')
    reasoning_trace: list[str] = Field(..., description='Step-by-step logic leading to the decision. Each step should be clear and atomic.')
    relevant_context_keys: list[str] = Field(..., description='Keys from the SignalContext that were utilized in this thought process.')
    tool_choice: Literal['SEARCH', 'CODE', 'ANSWER', 'DELEGATE', 'TERMINATE'] = Field(..., description='The action type to take')
    tool_arguments: dict[str, Any] = Field(default_factory=dict, description='Arguments for the chosen tool')
    confidence_score: float = Field(..., ge=0.0, le=1.0, description='Confidence in this decision (0.0 to 1.0)')

    @field_validator('tool_arguments')
    @classmethod
    def validate_args(cls, v, info):
        """Self-validation to ensure arguments match the tool choice."""
        tool_choice = info.data.get('tool_choice')
        if tool_choice == 'CODE' and 'code' not in v:
            raise ValueError("Tool choice CODE requires a 'code' argument.")
        if tool_choice == 'SEARCH' and 'query' not in v:
            raise ValueError("Tool choice SEARCH requires a 'query' argument.")
        if tool_choice == 'DELEGATE' and 'subtask' not in v:
            raise ValueError("Tool choice DELEGATE requires a 'subtask' argument.")
        return v

class CodeGenerationResult(BaseModel):
    """schema for code generation tasks."""
    model_config = ConfigDict(frozen=True, extra='forbid')
    reasoning: str = Field(..., description='Why this code solves the problem')
    code: str = Field(..., description='The generated Python code')
    dependencies: list[str] = Field(default_factory=list, description='Required pip packages')
    test_cases: list[str] = Field(default_factory=list, description='Test cases to verify the code')
    safety_notes: list[str] = Field(default_factory=list, description='Potential safety concerns or limitations')

class ResearchResult(BaseModel):
    """schema for research tasks."""
    model_config = ConfigDict(frozen=True, extra='forbid')
    query_understanding: str = Field(..., description='How you interpreted the research question')
    sources: list[dict[str, str]] = Field(..., description="List of sources with 'url' and 'relevance' keys")
    key_findings: list[str] = Field(..., description='Main findings from the research')
    ConfidenceLevel: Literal['high', 'medium', 'low'] = Field(..., description='Confidence in the research results')
    follow_up_questions: list[str] = Field(default_factory=list, description='Suggested follow-up research questions')

class AgentPlan(BaseModel):
    """Agent execution plan with reasoning and tool calls."""
    model_config = ConfigDict(frozen=True, extra='forbid')
    reasoning: str = Field(..., description='High-level strategy for the overall Task')
    tool_calls: list[dict[str, Any]] = Field(..., description='Ordered list of tool calls to execute the plan')
