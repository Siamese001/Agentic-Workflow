"""Evaluation Spine types — metric containers for Components B, C, D.

Defines types for:
  - OutcomeEvaluationResult    — Component B (task completion, groundedness, etc.)
  - TrajectoryEvaluationResult — Component C (tool selection, arg correctness, etc.)
  - GGateValidationResult      — Component D (exact match, schema/state checks)

All types are frozen dataclasses with deterministic to_dict()/to_json()/stable_hash()
methods. No wall-clock reads; timestamps are caller-supplied.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_blocks_direct_write,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from system_learning.enforcement.determinism import deterministic_json, stable_sha256_json

# ADG wiring for evaluation spine types
_emit_records_execution_trace("evaluation_spine_types", "p0", "evaluation_spine_trace")
_emit_applies_guardrail("p0", "evaluation_spine_types", "p0_governance")
emit_replay_key("p0", "evaluation_spine_types")
emit_determinism_digest("p0", "evaluation_spine_types")
_emit_writes_via_uwg("p2", "evaluation_spine_types", "uwg_write")
_emit_blocks_direct_write("p2", "evaluation_spine_types", "direct_write_block")
_emit_records_tool_invocation("p2", "evaluation_spine_types", "tool_invocation")
_emit_captures_execution_output("p2", "evaluation_spine_types", "exec_output")
_emit_dispatches_agent("p3", "evaluation_spine_types", "agent_dispatch")
_emit_dispatches_execution_plan("p3", "evaluation_spine_types", "exec_plan")
_emit_routes_to_agent("p3", "evaluation_spine_types", "target_agent")
_emit_checks_agent_registry("p3", "evaluation_spine_types", "agent_registry")
_emit_validates_agent_capability("p3", "evaluation_spine_types", "capability")
_emit_verifies_policy("p3", "evaluation_spine_types", "policy_check")
_emit_verifies_boundary("p3", "evaluation_spine_types", "boundary_check")


# =============================================================================
# Shared leaf types
# =============================================================================


@dataclass(frozen=True)
class MetricScore:
    """Individual metric score with confidence.

    Attributes
    ----------
    metric_name:
        Name of the metric (e.g., "task_completion").
    score:
        Numeric score (0.0 to 1.0).
    confidence:
        Confidence in the score (0.0 to 1.0).
    evidence:
        Evidence supporting the score.
    """

    metric_name: str
    score: float
    confidence: float
    evidence: str

    def __post_init__(self) -> None:
        if not self.metric_name:
            raise ValueError("metric_name must not be empty")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be in [0.0, 1.0], got {self.score}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")

    def to_dict(self) -> dict[str, object]:
        return {
            "confidence": self.confidence,
            "evidence": self.evidence,
            "metric_name": self.metric_name,
            "score": self.score,
        }


# =============================================================================
# Component B: Outcome Evaluation Result
# =============================================================================


@dataclass(frozen=True)
class OutcomeEvaluationResult:
    """Outcome evaluation result — Component B of Evaluation Spine.

    Evaluates:
      - Task completion
      - Groundedness
      - Citation support
      - Abstain correctness
      - Escalation correctness
      - Answer relevance

    Attributes
    ----------
    artifact_type:
        Always ``OUTCOME_EVALUATION_RESULT``.
    result_id:
        Deterministic SHA-256 ID for this result.
    trace_id:
        Source execution trace identifier.
    task_completion:
        Score for task completion (0.0 to 1.0).
    groundedness:
        Score for groundedness (0.0 to 1.0).
    citation_support:
        Score for citation support (0.0 to 1.0).
    abstain_correctness:
        Score for abstain correctness (0.0 to 1.0).
    escalation_correctness:
        Score for escalation correctness (0.0 to 1.0).
    answer_relevance:
        Score for answer relevance (0.0 to 1.0).
    overall_score:
        Weighted overall outcome score.
    metric_scores:
        Detailed metric scores with evidence.
    evaluation_summary:
        Human-readable evaluation summary.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["OUTCOME_EVALUATION_RESULT"]
    result_id: str
    trace_id: str
    task_completion: float
    groundedness: float
    citation_support: float
    abstain_correctness: float
    escalation_correctness: float
    answer_relevance: float
    overall_score: float
    metric_scores: tuple[MetricScore, ...]
    evaluation_summary: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "OUTCOME_EVALUATION_RESULT":
            raise ValueError(f"artifact_type must be 'OUTCOME_EVALUATION_RESULT', got {self.artifact_type!r}")
        if not self.result_id:
            raise ValueError("result_id must not be empty")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        for score in [
            self.task_completion,
            self.groundedness,
            self.citation_support,
            self.abstain_correctness,
            self.escalation_correctness,
            self.answer_relevance,
            self.overall_score,
        ]:
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"All scores must be in [0.0, 1.0], got {score}")

    def to_dict(self) -> dict[str, object]:
        return {
            "abstain_correctness": self.abstain_correctness,
            "answer_relevance": self.answer_relevance,
            "artifact_type": self.artifact_type,
            "citation_support": self.citation_support,
            "escalation_correctness": self.escalation_correctness,
            "evaluation_summary": self.evaluation_summary,
            "groundedness": self.groundedness,
            "metric_scores": [m.to_dict() for m in self.metric_scores],
            "overall_score": self.overall_score,
            "result_id": self.result_id,
            "task_completion": self.task_completion,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# =============================================================================
# Component C: Trajectory Evaluation Result
# =============================================================================


@dataclass(frozen=True)
class TrajectoryEvaluationResult:
    """Trajectory evaluation result — Component C of Evaluation Spine.

    Evaluates:
      - Tool selection/order
      - Argument correctness
      - Retry thrashing
      - Budget discipline
      - Policy compliance

    Attributes
    ----------
    artifact_type:
        Always ``TRAJECTORY_EVALUATION_RESULT``.
    result_id:
        Deterministic SHA-256 ID for this result.
    trace_id:
        Source execution trace identifier.
    tool_selection:
        Score for tool selection quality (0.0 to 1.0).
    arg_correctness:
        Score for argument correctness (0.0 to 1.0).
    retry_thrashing:
        Score for retry efficiency (0.0 to 1.0, higher is better).
    budget_discipline:
        Score for budget adherence (0.0 to 1.0).
    policy_compliance:
        Score for policy compliance (0.0 to 1.0).
    overall_score:
        Weighted overall trajectory score.
    metric_scores:
        Detailed metric scores with evidence.
    tool_sequence:
        Sequence of tool calls made during execution.
    retry_count:
        Number of retries performed.
    budget_used:
        Budget consumed (tokens, latency, etc.).
    budget_allocated:
        Budget allocated for the execution.
    evaluation_summary:
        Human-readable evaluation summary.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["TRAJECTORY_EVALUATION_RESULT"]
    result_id: str
    trace_id: str
    tool_selection: float
    arg_correctness: float
    retry_thrashing: float
    budget_discipline: float
    policy_compliance: float
    overall_score: float
    metric_scores: tuple[MetricScore, ...]
    tool_sequence: tuple[str, ...]
    retry_count: int
    budget_used: float
    budget_allocated: float
    evaluation_summary: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "TRAJECTORY_EVALUATION_RESULT":
            raise ValueError(
                f"artifact_type must be 'TRAJECTORY_EVALUATION_RESULT', got {self.artifact_type!r}"
            )
        if not self.result_id:
            raise ValueError("result_id must not be empty")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        for score in [
            self.tool_selection,
            self.arg_correctness,
            self.retry_thrashing,
            self.budget_discipline,
            self.policy_compliance,
            self.overall_score,
        ]:
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"All scores must be in [0.0, 1.0], got {score}")
        if self.retry_count < 0:
            raise ValueError(f"retry_count must be non-negative, got {self.retry_count}")
        if self.budget_used < 0 or self.budget_allocated < 0:
            raise ValueError("budget values must be non-negative")

    def to_dict(self) -> dict[str, object]:
        return {
            "arg_correctness": self.arg_correctness,
            "artifact_type": self.artifact_type,
            "budget_allocated": self.budget_allocated,
            "budget_discipline": self.budget_discipline,
            "budget_used": self.budget_used,
            "evaluation_summary": self.evaluation_summary,
            "metric_scores": [m.to_dict() for m in self.metric_scores],
            "overall_score": self.overall_score,
            "policy_compliance": self.policy_compliance,
            "result_id": self.result_id,
            "retry_count": self.retry_count,
            "retry_thrashing": self.retry_thrashing,
            "timestamp_utc": self.timestamp_utc,
            "tool_selection": self.tool_selection,
            "tool_sequence": list(self.tool_sequence),
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# =============================================================================
# Component D: G-Gate Regression Validation Result
# =============================================================================


@dataclass(frozen=True)
class GGateValidationResult:
    """G-Gate regression validation result — Component D of Evaluation Spine.

    Validates:
      - Exact match
      - Schema/state checks
      - Trajectory invariance
      - API drift detection
      - Rubric grading consistency

    Attributes
    ----------
    artifact_type:
        Always ``G_GATE_VALIDATION_RESULT``.
    result_id:
        Deterministic SHA-256 ID for this result.
    trace_id:
        Source execution trace identifier.
    exact_match_pass:
        True if exact match validation passed.
    schema_state_pass:
        True if schema/state validation passed.
    trajectory_invariant_pass:
        True if trajectory invariance check passed.
    api_drift_detected:
        True if API drift was detected.
    rubric_consistency_pass:
        True if rubric grading is consistent.
    overall_pass:
        True if all validations passed.
    drift_details:
        Details of any drift detected.
    baseline_digest:
        SHA-256 of baseline state.
    current_digest:
        SHA-256 of current state.
    diff_summary:
        Summary of differences found.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["G_GATE_VALIDATION_RESULT"]
    result_id: str
    trace_id: str
    exact_match_pass: bool
    schema_state_pass: bool
    trajectory_invariant_pass: bool
    api_drift_detected: bool
    rubric_consistency_pass: bool
    overall_pass: bool
    drift_details: tuple[str, ...]
    baseline_digest: str
    current_digest: str
    diff_summary: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "G_GATE_VALIDATION_RESULT":
            raise ValueError(f"artifact_type must be 'G_GATE_VALIDATION_RESULT', got {self.artifact_type!r}")
        if not self.result_id:
            raise ValueError("result_id must not be empty")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if not self.baseline_digest:
            raise ValueError("baseline_digest must not be empty")
        if not self.current_digest:
            raise ValueError("current_digest must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "api_drift_detected": self.api_drift_detected,
            "artifact_type": self.artifact_type,
            "baseline_digest": self.baseline_digest,
            "current_digest": self.current_digest,
            "diff_summary": self.diff_summary,
            "drift_details": list(self.drift_details),
            "exact_match_pass": self.exact_match_pass,
            "overall_pass": self.overall_pass,
            "result_id": self.result_id,
            "rubric_consistency_pass": self.rubric_consistency_pass,
            "schema_state_pass": self.schema_state_pass,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
            "trajectory_invariant_pass": self.trajectory_invariant_pass,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


__all__ = [
    "GGateValidationResult",
    "MetricScore",
    "OutcomeEvaluationResult",
    "TrajectoryEvaluationResult",
]
