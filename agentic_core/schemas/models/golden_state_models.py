from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel


@dataclass
class GoldenStateTestCase:
    """Single golden-state test case.

    `expected_behavior` is a free-form description used by judges.
    `metadata` can hold scenario tags, Severity, etc.
    """

    id: str
    input_text: str
    expected_behavior: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class JudgeVerdict:
    """LM-as-a-judge style Verdict.

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
    Verdict: JudgeVerdict
    raw_output: str
    reasoning_trace: list[dict[str, object]] = field(default_factory=list)


class GoldenCase(BaseModel):
    id: str
    input_text: str
    agent_sequence: list[str]
    expected_keypoints: list[str]
    correctness_criteria: dict[str, object]


class GoldenOutput(BaseModel):
    case_id: str
    produced_keypoints: list[str]
    correctness_map: dict[str, bool]
    safety_decisions: dict[str, object]
    metacognition_summary: dict[str, object]
    final_verdict: Literal["pass", "fail", "borderline"]
