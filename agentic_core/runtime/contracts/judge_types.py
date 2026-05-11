"""Judge and gate result types — generic, app-agnostic contracts.

Phase 1.3 of apps-rg-ensemble-judge-restoration-a7c4e2.
W6 extended: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W6
  - CandidateGateResult: added gate_family, result enum, severity, fail_closed,
    repair_allowed, not_applicable_reason, unknown_reason, threshold, evidence_refs.
  - JudgeResult: added judge_version, judge_profile_ref, dimension, reasoning_ref,
    error, latency_ms, required_for_exit, informational_only.
  - JudgeJuryResult: added aggregate_score, consensus_status, selection_policy_applied,
    decisive_reason, missing_required_judges, informational_judges_missing.
  All new fields default-empty; existing fields preserved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict

# Result sentinel constants — used by gate runner and jury runner
GATE_RESULT_PASS = "PASS"
GATE_RESULT_FAIL = "FAIL"
GATE_RESULT_WARN = "WARN"
GATE_RESULT_UNKNOWN = "UNKNOWN"
GATE_RESULT_NOT_APPLICABLE = "NOT_APPLICABLE"

_VALID_GATE_RESULTS = frozenset(
    {GATE_RESULT_PASS, GATE_RESULT_FAIL, GATE_RESULT_WARN, GATE_RESULT_UNKNOWN, GATE_RESULT_NOT_APPLICABLE}
)


@dataclass(frozen=True, slots=True)
class CandidateGateResult:
    """Result of running one gate against one candidate.

    Produced by L2 candidate gate runner.

    Key invariants:
    - UNKNOWN is NOT PASS.
    - NOT_APPLICABLE requires not_applicable_reason to be non-empty.
    - FAIL with fail_closed=True blocks candidate.
    """

    gate_id: str = ""
    candidate_id: str = ""
    node_id: str = ""
    run_id: str = ""

    # W6: explicit result enum field
    result: str = GATE_RESULT_UNKNOWN  # PASS|FAIL|WARN|UNKNOWN|NOT_APPLICABLE

    # Outcome — original fields
    passed: bool = False
    rejection_reason: str = ""  # empty if passed
    gate_score: float = 0.0     # 0.0-1.0 if gate produces a score

    # W6: gate semantics
    gate_family: str = ""         # maps to runtime_gate_family from gate config
    severity: str = ""            # "hard_fail" | "warn"
    fail_closed: bool = True
    repair_allowed: bool = False
    threshold: float = 0.0
    reason: str = ""              # human-readable verdict reason (W6 alias for rejection_reason)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    not_applicable_reason: str = ""  # required when result==NOT_APPLICABLE
    unknown_reason: str = ""         # required when result==UNKNOWN

    # Metadata — original fields
    gate_type: str = ""
    gate_config_ref: str = ""
    execution_duration_ms: int = 0

    # Tracing — original fields
    trace_root: str = ""
    otel_span_ref: str = ""

    schema_version: str = "W6.a3f7e2"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "candidate_id": self.candidate_id,
            "node_id": self.node_id,
            "run_id": self.run_id,
            "result": self.result,
            "passed": self.passed,
            "rejection_reason": self.rejection_reason,
            "gate_score": self.gate_score,
            "gate_family": self.gate_family,
            "severity": self.severity,
            "fail_closed": self.fail_closed,
            "repair_allowed": self.repair_allowed,
            "threshold": self.threshold,
            "reason": self.reason or self.rejection_reason,
            "evidence_refs": list(self.evidence_refs),
            "not_applicable_reason": self.not_applicable_reason,
            "unknown_reason": self.unknown_reason,
            "gate_type": self.gate_type,
            "gate_config_ref": self.gate_config_ref,
            "execution_duration_ms": self.execution_duration_ms,
            "trace_root": self.trace_root,
            "otel_span_ref": self.otel_span_ref,
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class JudgeResult:
    """Score from one judge for one candidate.

    Produced by L2 judge jury runner.
    """

    judge_id: str = ""
    candidate_id: str = ""
    node_id: str = ""
    run_id: str = ""

    # W6: explicit judge metadata
    judge_version: str = ""
    judge_profile_ref: str = ""      # pointer to judge_profile config
    dimension: str = ""              # rubric dimension being scored

    # Scoring — original fields
    score: float = 0.0
    raw_score: float = 0.0
    confidence: float = 0.0
    abstained: bool = False
    abstain_reason: str = ""

    # W6: result detail
    reasoning_ref: str = ""          # ref to LLM reasoning artifact
    error: str = ""                  # non-empty if judge failed
    latency_ms: int = 0
    required_for_exit: bool = False  # if True, abstain/error fails closed
    informational_only: bool = False # if True, abstain/error is warn only

    # Rubric — original fields
    rubric_ref: str = ""
    rubric_dimensions_scored: tuple[str, ...] = field(default_factory=tuple)
    per_dimension_scores: tuple[float, ...] = field(default_factory=tuple)

    # Provider — original fields
    provider_ref: str = ""
    model_ref: str = ""
    provider_receipt_ref: str = ""
    execution_duration_ms: int = 0

    # W6 evidence refs
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    # Tracing — original fields
    trace_root: str = ""
    otel_span_ref: str = ""

    schema_version: str = "W6.a3f7e2"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "judge_id": self.judge_id,
            "candidate_id": self.candidate_id,
            "node_id": self.node_id,
            "run_id": self.run_id,
            "judge_version": self.judge_version,
            "judge_profile_ref": self.judge_profile_ref,
            "dimension": self.dimension,
            "score": self.score,
            "raw_score": self.raw_score,
            "confidence": self.confidence,
            "abstained": self.abstained,
            "abstain_reason": self.abstain_reason,
            "reasoning_ref": self.reasoning_ref,
            "error": self.error,
            "latency_ms": self.latency_ms or self.execution_duration_ms,
            "required_for_exit": self.required_for_exit,
            "informational_only": self.informational_only,
            "rubric_ref": self.rubric_ref,
            "rubric_dimensions_scored": list(self.rubric_dimensions_scored),
            "per_dimension_scores": list(self.per_dimension_scores),
            "provider_ref": self.provider_ref,
            "model_ref": self.model_ref,
            "provider_receipt_ref": self.provider_receipt_ref,
            "execution_duration_ms": self.execution_duration_ms,
            "evidence_refs": list(self.evidence_refs),
            "trace_root": self.trace_root,
            "otel_span_ref": self.otel_span_ref,
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class JudgeJuryResult:
    """Aggregated jury verdict for one candidate across all judges.

    Produced by L2 judge jury runner after collecting individual JudgeResults.

    Key invariants:
    - missing required judge → fails closed (missing_required_judges non-empty)
    - missing informational judge → does NOT fail (informational_judges_missing logged)
    - judge timeout for required dimension → fails closed
    """

    candidate_id: str = ""
    node_id: str = ""
    run_id: str = ""

    # W6: explicit aggregate fields
    aggregate_score: float = 0.0      # mean across non-abstaining judges
    consensus_status: str = ""        # "consensus" | "split" | "abstained" | "failed"
    selection_policy_applied: str = ""
    decisive_reason: str = ""
    missing_required_judges: tuple[str, ...] = field(default_factory=tuple)
    informational_judges_missing: tuple[str, ...] = field(default_factory=tuple)

    # Aggregated scoring — original fields
    aggregated_score: float = 0.0
    aggregation_method: str = ""
    judge_count: int = 0
    abstain_count: int = 0

    # Per-judge refs — original fields
    judge_result_refs: tuple[str, ...] = field(default_factory=tuple)
    judge_weights: tuple[float, ...] = field(default_factory=tuple)

    # W6 embedded judge results (compact transport)
    judge_results: tuple[str, ...] = field(default_factory=tuple)  # serialised JudgeResult refs

    # Verdict — original fields
    meets_threshold: bool = False
    threshold: float = 0.0

    # Tracing — original fields
    trace_root: str = ""
    otel_span_ref: str = ""
    verdict_timestamp: str = ""

    schema_version: str = "W6.a3f7e2"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "node_id": self.node_id,
            "run_id": self.run_id,
            "aggregate_score": self.aggregate_score or self.aggregated_score,
            "consensus_status": self.consensus_status,
            "selection_policy_applied": self.selection_policy_applied,
            "decisive_reason": self.decisive_reason,
            "missing_required_judges": list(self.missing_required_judges),
            "informational_judges_missing": list(self.informational_judges_missing),
            "aggregated_score": self.aggregated_score or self.aggregate_score,
            "aggregation_method": self.aggregation_method,
            "judge_count": self.judge_count,
            "abstain_count": self.abstain_count,
            "judge_result_refs": list(self.judge_result_refs),
            "judge_weights": list(self.judge_weights),
            "judge_results": list(self.judge_results),
            "meets_threshold": self.meets_threshold,
            "threshold": self.threshold,
            "trace_root": self.trace_root,
            "otel_span_ref": self.otel_span_ref,
            "verdict_timestamp": self.verdict_timestamp,
            "schema_version": self.schema_version,
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), separators=(",", ":"))
