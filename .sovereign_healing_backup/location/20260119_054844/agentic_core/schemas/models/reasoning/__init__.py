from __future__ import annotations
"""
Reasoning Contracts - SSOT for agent reasoning, code generation, and consensus models.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator


class AgentThoughtProcess(BaseModel):
    """
    Forces the agent to show its work before acting.
    This is the "Physics" of your Agent - the schema it must follow.
    """
    reasoning_trace: List[str] = Field(
        ...,
        description="Step-by-step logic leading to the decision. Each step should be clear and atomic."
    )
    relevant_context_keys: List[str] = Field(...)
    tool_choice: Literal["SEARCH", "CODE", "ANSWER", "DELEGATE", "TERMINATE"] = Field(
        ...,
        description="The action type to take"
    )
    tool_arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for the chosen tool"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in this decision (0.0 to 1.0)"
    )

    @field_validator('tool_arguments')
    @classmethod
    def validate_args(cls, v, info):
        """Self-validation inside the schema."""
        tool_choice = info.data.get('tool_choice')

        if tool_choice == 'CODE' and 'code' not in v:
            raise ValueError("Tool choice CODE requires a 'code' argument.")

        if tool_choice == 'SEARCH' and 'query' not in v:
            raise ValueError("Tool choice SEARCH requires a 'query' argument.")

        if tool_choice == 'DELEGATE' and 'subtask' not in v:
            raise ValueError("Tool choice DELEGATE requires a 'subtask' argument.")

        return v

# Backward compat alias


class CodeGenerationResult(BaseModel):
    """Schema for code generation tasks."""
    reasoning: str = Field(..., description="Why this code solves the problem")
    code: str = Field(..., description="The generated Python code")
    dependencies: List[str] = Field(
        default_factory=list,
        description="Required pip packages"
    )
    test_cases: List[str] = Field(
        default_factory=list,
        description="Test cases to verify the code"
    )
    safety_notes: List[str] = Field(
        default_factory=list,
        description="Potential safety concerns or limitations"
    )

# Backward compat alias


class ResearchResult(BaseModel):
    """Schema for research tasks."""
    query_understanding: str = Field(..., description="How you interpreted the research question")
    sources: List[Dict[str, str]] = Field(
        ...,
        description="List of sources with 'url' and 'relevance' keys"
    )
    key_findings: List[str] = Field(..., description="Main findings from the research")
    ConfidenceLevel: Literal["high", "medium", "low"] = Field(
        ...,
        description="Confidence in the research results"
    )
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up research questions"
    )

# Backward compat alias


class ConsensusVerdict(BaseModel):
    """Result of a consensus deliberation."""
    chosen_plan: str
    consensus_score: float  # 0.0 to 1.0
    dissenting_opinions: List[str] = Field(default_factory=list)
    reasoning: str
    safe_to_proceed: bool

# Backward compat alias


class ModelOpinion(BaseModel):
    """Individual model's opinion on a plan."""
    model_name: str
    plan: str
    reasoning: str
    risk_assessment: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float  # 0.0 to 1.0

# Backward compat alias


class AgentPlan(BaseModel):
    """Agent execution plan with reasoning and tool calls."""
    reasoning: str
    tool_calls: list[dict]

# Backward compat alias


# Public exports
__all__ = [
    # Snake case (canonical)
    "AgentThoughtProcess",
    "CodeGenerationResult",
    "ResearchResult",
    "ConsensusVerdict",
    "ModelOpinion",
    "AgentPlan",
    # PascalCase aliases (backward compat)
    "AgentThoughtProcess",
    "CodeGenerationResult",
    "ResearchResult",
    "ConsensusVerdict",
    "ModelOpinion",
    "AgentPlan",
]
