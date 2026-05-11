"""Judge and gate result types — generic, app-agnostic contracts.

Phase 1.3 of apps-rg-ensemble-judge-restoration-a7c4e2.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CandidateGateResult:
    """Result of running one gate against one candidate.

    Produced by L2 candidate gate runner.
    """

    gate_id: str = ""
    candidate_id: str = ""
    node_id: str = ""
    run_id: str = ""

    # Outcome
    passed: bool = False
    rejection_reason: str = ""  # empty if passed
    gate_score: float = 0.0  # 0.0-1.0 if gate produces a score

    # Metadata
    gate_type: str = ""  # e.g. "length_check", "toxicity_check", "format_check"
    gate_config_ref: str = ""
    execution_duration_ms: int = 0

    # Tracing
    trace_root: str = ""
    otel_span_ref: str = ""

    schema_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class JudgeResult:
    """Score from one judge for one candidate.

    Produced by L2 judge jury runner.
    """

    judge_id: str = ""
    candidate_id: str = ""
    node_id: str = ""
    run_id: str = ""

    # Scoring
    score: float = 0.0  # 0.0-1.0 normalized
    raw_score: float = 0.0  # provider-native scale
    confidence: float = 0.0  # judge self-confidence 0.0-1.0
    abstained: bool = False
    abstain_reason: str = ""

    # Rubric
    rubric_ref: str = ""
    rubric_dimensions_scored: tuple[str, ...] = field(default_factory=tuple)
    per_dimension_scores: tuple[float, ...] = field(default_factory=tuple)

    # Provider
    provider_ref: str = ""
    model_ref: str = ""
    provider_receipt_ref: str = ""
    execution_duration_ms: int = 0

    # Tracing
    trace_root: str = ""
    otel_span_ref: str = ""

    schema_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class JudgeJuryResult:
    """Aggregated jury verdict for one candidate across all judges.

    Produced by L2 judge jury runner after collecting individual JudgeResults.
    """

    candidate_id: str = ""
    node_id: str = ""
    run_id: str = ""

    # Aggregated scoring
    aggregated_score: float = 0.0
    aggregation_method: str = ""  # e.g. "weighted_average", "median", "min"
    judge_count: int = 0
    abstain_count: int = 0

    # Per-judge refs
    judge_result_refs: tuple[str, ...] = field(default_factory=tuple)
    judge_weights: tuple[float, ...] = field(default_factory=tuple)

    # Verdict
    meets_threshold: bool = False
    threshold: float = 0.0

    # Tracing
    trace_root: str = ""
    otel_span_ref: str = ""
    verdict_timestamp: str = ""

    schema_version: str = "1.0"
