"""
Evaluation Report Schema

Structured output schemas for reporting evaluation runs to L6 observability
and for consumption by the Meta Learning Pipeline.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .evaluation_result_schema import DeltaReport, EvaluationReport
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass(frozen=True)
class SystemEvaluationSummary:
    """High-level summary suitable for L6 dashboard and Meta Learning signals."""
    system_version: str
    dataset_name: str
    retrieval_quality_score: float
    answer_quality_score: float
    safety_compliance_score: float
    hallucination_risk_score: float
    timestamp: str
    run_id: str

    @property
    def overall_score(self) -> float:
        """Composite quality score across all dimensions."""
        return (self.retrieval_quality_score + self.answer_quality_score + self.safety_compliance_score + (1.0 - self.hallucination_risk_score)) / 4.0

    def to_dict(self) -> dict[str, Any]:
        return {'system_version': self.system_version, 'dataset_name': self.dataset_name, 'retrieval_quality_score': self.retrieval_quality_score, 'answer_quality_score': self.answer_quality_score, 'safety_compliance_score': self.safety_compliance_score, 'hallucination_risk_score': self.hallucination_risk_score, 'overall_score': self.overall_score, 'timestamp': self.timestamp, 'run_id': self.run_id}

    @classmethod
    def from_report(cls, report: EvaluationReport) -> SystemEvaluationSummary:
        """Build summary from aggregate scores in an EvaluationReport."""
        scores = report.aggregate_scores
        return cls(system_version=report.system_version, dataset_name=report.dataset_name, retrieval_quality_score=scores.get('precision@5', 0.0), answer_quality_score=scores.get('answer_correctness', 0.0), safety_compliance_score=scores.get('safety_compliance', 1.0), hallucination_risk_score=scores.get('hallucination_risk', 0.0), timestamp=report.timestamp, run_id=report.run_id)

@dataclass(frozen=True)
class ComparativeEvaluationSummary:
    """Summary of a comparative (replay) evaluation run for Meta Learning proposals."""
    baseline_run_id: str
    candidate_run_id: str
    baseline_version: str
    candidate_version: str
    timestamp: str
    improvements: dict[str, float]
    regressions: dict[str, float]
    net_delta: float
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return {'baseline_run_id': self.baseline_run_id, 'candidate_run_id': self.candidate_run_id, 'baseline_version': self.baseline_version, 'candidate_version': self.candidate_version, 'timestamp': self.timestamp, 'improvements': dict(self.improvements), 'regressions': dict(self.regressions), 'net_delta': self.net_delta, 'recommendation': self.recommendation}

    @classmethod
    def from_delta_report(cls, delta: DeltaReport, baseline_version: str, candidate_version: str) -> ComparativeEvaluationSummary:
        """Build comparative summary from a DeltaReport."""
        improvements = {k: v for k, v in delta.metric_deltas.items() if v > 0}
        regressions = {k: v for k, v in delta.metric_deltas.items() if v < 0}
        net_delta = sum(delta.metric_deltas.values())
        recommendation = 'promote' if net_delta > 0 else 'reject'
        return cls(baseline_run_id=delta.run_id_a, candidate_run_id=delta.run_id_b, baseline_version=baseline_version, candidate_version=candidate_version, timestamp=delta.timestamp, improvements=improvements, regressions=regressions, net_delta=net_delta, recommendation=recommendation)
__all__ = ['SystemEvaluationSummary', 'ComparativeEvaluationSummary']
