from __future__ import annotations

"""
Golden State & Evaluation Schemas
================================
Defines models for Ground Truth benchmarking and LM-as-a-Judge
evaluation workflows.
"""

from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel


@dataclass
class GoldenStateTestCase:
    """A single benchmark test case for the system."""

    id: str
    input_text: str
    expected_behavior: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class JudgeVerdict:
    """Schema for LM-as-a-Judge evaluation results."""

    score: float
    rating: str
    explanation: str


@dataclass
class EvalResult:
    """Outcome of running a GoldenStateTestCase through the agent loop."""

    test_id: str
    Verdict: JudgeVerdict
    raw_output: str
    reasoning_trace: list[dict[str, Any]] = field(default_factory=list)


class GoldenCase(BaseModel):
    """Structured benchmark case for automated evaluation pipelines."""

    id: str
    input_text: str
    agent_sequence: list[str]
    expected_keypoints: list[str]
    correctness_criteria: dict[str, Any]


class GoldenOutput(BaseModel):
    """Benchmark results including safety and metacognitive summaries."""

    case_id: str
    produced_keypoints: list[str]
    correctness_map: dict[str, bool]
    safety_decisions: dict[str, Any]
    metacognition_summary: dict[str, Any]
    final_verdict: Literal["pass", "fail", "borderline"]
