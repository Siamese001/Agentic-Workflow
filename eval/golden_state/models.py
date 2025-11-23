from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

from pydantic import BaseModel


@dataclass
class TestCase:
    """Single golden-state test case.

    `expected_behavior` is a free-form description used by judges.
    `metadata` can hold scenario tags, severity, etc.
    """

    id: str
    input_text: str
    expected_behavior: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JudgeVerdict:
    """LM-as-a-judge style verdict.

    `score` is a numeric score (0.0–1.0) for aggregation.
    `rating` is a coarse label such as "pass" / "fail" / "borderline".
    """

    score: float
    rating: str
    explanation: str


@dataclass
class EvalResult:
    """Result of running a golden test case through the system."""

    test_id: str
    verdict: JudgeVerdict
    raw_output: str
    reasoning_trace: List[Dict[str, Any]] = field(default_factory=list)


class GoldenCase(BaseModel):
    id: str
    input_text: str
    agent_sequence: List[str]
    expected_keypoints: List[str]
    correctness_criteria: Dict[str, Any]


class GoldenOutput(BaseModel):
    case_id: str
    produced_keypoints: List[str]
    correctness_map: Dict[str, bool]
    safety_decisions: Dict[str, Any]
    metacognition_summary: Dict[str, Any]
    final_verdict: Literal["pass", "fail", "borderline"]

