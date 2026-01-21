from __future__ import annotations
"""
Golden State & Evaluation Schemas
================================
Defines models for Ground Truth benchmarking and LM-as-a-Judge
evaluation workflows.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field


@dataclass
class GoldenStateTestCase:
    """A single benchmark test case for the system."""
    id: str
    input_text: str
    expected_behavior: str
    metadata: Dict[str, Any] = field(default_factory=dict)

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
    reasoning_trace: List[Dict[str, Any]] = field(default_factory=list)

class GoldenCase(BaseModel):
    """Structured benchmark case for automated evaluation pipelines."""
    id: str
    input_text: str
    agent_sequence: List[str]
    expected_keypoints: List[str]
    correctness_criteria: Dict[str, Any]

class GoldenOutput(BaseModel):
    """Benchmark results including safety and metacognitive summaries."""
    case_id: str
    produced_keypoints: List[str]
    correctness_map: Dict[str, bool]
    safety_decisions: Dict[str, Any]
    metacognition_summary: Dict[str, Any]
    final_verdict: Literal["pass", "fail", "borderline"]
