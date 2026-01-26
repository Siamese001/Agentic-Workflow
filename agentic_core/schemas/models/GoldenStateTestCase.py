from __future__ import annotations

"""
Golden State & Evaluation Schemas
================================
Defines models for Ground Truth benchmarking and LM-as-a-Judge
evaluation workflows.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GoldenStateTestCase(BaseModel):
    """A single benchmark test case for the system."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Unique test case identifier")
    input_text: str = Field(..., description="Input text for the test case")
    expected_behavior: str = Field(..., description="Expected behavior description")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("input_text", "expected_behavior")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """[HARDENED] Ensure required text fields are not empty."""
        if not value.strip():
            raise ValueError("Text fields cannot be empty")
        return value.strip()


class JudgeVerdict(BaseModel):
    """schema for LM-as-a-Judge evaluation results."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    score: float = Field(..., ge=0.0, le=1.0, description="Verdict score between 0 and 1")
    rating: str = Field(..., description="Qualitative rating")
    explanation: str = Field(..., description="Explanation of the verdict")

    @field_validator("rating", "explanation")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        """[HARDENED] Ensure rating and explanation are not empty."""
        if not value.strip():
            raise ValueError("Rating and explanation cannot be empty")
        return value.strip()


class EvalResult(BaseModel):
    """Outcome of running a GoldenStateTestCase through the agent loop."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    test_id: str = Field(..., description="ID of the executed test case")
    verdict: JudgeVerdict = Field(..., description="Judge verdict")
    raw_output: str = Field(..., description="Raw model output")
    reasoning_trace: list[dict[str, Any]] = Field(default_factory=list, description="Reasoning trace")


class GoldenCase(BaseModel):
    """Structured benchmark case for automated evaluation pipelines."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    input_text: str
    agent_sequence: list[str]
    expected_keypoints: list[str]
    correctness_criteria: dict[str, Any]


class GoldenOutput(BaseModel):
    """Benchmark results including safety and metacognitive summaries."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    case_id: str
    produced_keypoints: list[str]
    correctness_map: dict[str, bool]
    safety_decisions: dict[str, Any]
    metacognition_summary: dict[str, Any]
    final_verdict: Literal["pass", "fail", "borderline"]
