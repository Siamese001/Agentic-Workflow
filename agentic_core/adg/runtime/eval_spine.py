"""G16 (gap): Evaluation and optimization spine runtime.

Models the live evaluation bus with groundedness, P@K, MRR, NDCG, completeness
scoring, drift alerts, DPO batch building, and controlled proposal/commit stages.

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OptimizationStage(str, Enum):
    SCORING = "scoring"
    DRIFT_DETECTED = "drift_detected"
    DPO_BUILDING = "dpo_building"
    PROPOSAL_STAGED = "proposal_staged"
    PROPOSAL_COMMITTED = "proposal_committed"
    PROPOSAL_REJECTED = "proposal_rejected"


@dataclass
class EvalMetricResult:
    """Result of a single evaluation metric computation."""

    metric_id: str = field(default_factory=lambda: f"em-{uuid.uuid4().hex[:8]}")
    metric_name: str = ""
    value: float = 0.0
    run_id: str = ""
    agent_id: str = ""
    k: int = 0
    computed_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "metric_name": self.metric_name,
            "value": self.value,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "k": self.k,
            "computed_at": self.computed_at,
        }


@dataclass
class DriftAlert:
    """Alert emitted when a metric drifts beyond a configured threshold."""

    alert_id: str = field(default_factory=lambda: f"da-{uuid.uuid4().hex[:8]}")
    metric_name: str = ""
    current_value: float = 0.0
    baseline_value: float = 0.0
    drift_magnitude: float = 0.0
    threshold: float = 0.05
    run_id: str = ""
    agent_id: str = ""
    emitted_at: float = field(default_factory=time.time)

    @property
    def is_critical(self) -> bool:
        return abs(self.drift_magnitude) > self.threshold * 2

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "drift_magnitude": self.drift_magnitude,
            "threshold": self.threshold,
            "is_critical": self.is_critical,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "emitted_at": self.emitted_at,
        }


@dataclass
class PreferencePair:
    """A single DPO preference pair (chosen / rejected)."""

    pair_id: str = field(default_factory=lambda: f"pp-{uuid.uuid4().hex[:8]}")
    prompt_hash: str = ""
    chosen_hash: str = ""
    rejected_hash: str = ""
    score_delta: float = 0.0
    source_metric: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "prompt_hash": self.prompt_hash,
            "chosen_hash": self.chosen_hash,
            "rejected_hash": self.rejected_hash,
            "score_delta": self.score_delta,
            "source_metric": self.source_metric,
        }


@dataclass
class DPOBatch:
    """A batch of preference pairs ready for DPO optimization."""

    batch_id: str = field(default_factory=lambda: f"dpo-{uuid.uuid4().hex[:10]}")
    run_id: str = ""
    agent_id: str = ""
    pairs: list[PreferencePair] = field(default_factory=list)
    built_at: float = field(default_factory=time.time)
    stage: OptimizationStage = OptimizationStage.DPO_BUILDING

    @property
    def pair_count(self) -> int:
        return len(self.pairs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "pair_count": self.pair_count,
            "built_at": self.built_at,
            "stage": self.stage.value,
        }


@dataclass
class OptimizationProposal:
    """A staged optimization proposal before commit."""

    proposal_id: str = field(default_factory=lambda: f"op-{uuid.uuid4().hex[:10]}")
    dpo_batch_id: str = ""
    run_id: str = ""
    agent_id: str = ""
    proposed_weight_deltas: dict[str, float] = field(default_factory=dict)
    stage: OptimizationStage = OptimizationStage.PROPOSAL_STAGED
    staged_at: float = field(default_factory=time.time)
    committed_at: float = 0.0
    rejection_reason: str = ""

    @property
    def is_committed(self) -> bool:
        return self.stage == OptimizationStage.PROPOSAL_COMMITTED

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "dpo_batch_id": self.dpo_batch_id,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "stage": self.stage.value,
            "is_committed": self.is_committed,
            "delta_count": len(self.proposed_weight_deltas),
            "staged_at": self.staged_at,
            "committed_at": self.committed_at,
            "rejection_reason": self.rejection_reason,
        }


@dataclass
class EvalSpineReport:
    """Aggregated report of all evaluation spine events for one session."""

    agent_id: str = ""
    run_id: str = ""
    metrics: list[EvalMetricResult] = field(default_factory=list)
    drift_alerts: list[DriftAlert] = field(default_factory=list)
    dpo_batches: list[DPOBatch] = field(default_factory=list)
    proposals: list[OptimizationProposal] = field(default_factory=list)

    @property
    def committed_proposal_count(self) -> int:
        return sum(1 for p in self.proposals if p.is_committed)

    @property
    def critical_drift_count(self) -> int:
        return sum(1 for a in self.drift_alerts if a.is_critical)

    def metrics_by_name(self) -> dict[str, list[float]]:
        result: dict[str, list[float]] = {}
        for m in self.metrics:
            result.setdefault(m.metric_name, []).append(m.value)
        return result

    def average_metric(self, name: str) -> float:
        values = self.metrics_by_name().get(name, [])
        return sum(values) / len(values) if values else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "metric_count": len(self.metrics),
            "drift_alert_count": len(self.drift_alerts),
            "critical_drift_count": self.critical_drift_count,
            "dpo_batch_count": len(self.dpo_batches),
            "proposal_count": len(self.proposals),
            "committed_proposal_count": self.committed_proposal_count,
        }

    @property
    def summary(self) -> str:
        return (
            f"EvalSpine [{self.agent_id}] — "
            f"{len(self.metrics)} metrics, "
            f"{len(self.drift_alerts)} drift alerts ({self.critical_drift_count} critical), "
            f"{len(self.dpo_batches)} DPO batches, "
            f"{self.committed_proposal_count}/{len(self.proposals)} proposals committed"
        )


class EvalSpine:
    """Runtime evaluation and optimization spine."""

    def __init__(self, agent_id: str, run_id: str) -> None:
        self.report = EvalSpineReport(agent_id=agent_id, run_id=run_id)

    def score_groundedness(self, value: float, metadata: dict[str, Any] | None = None) -> EvalMetricResult:
        return self._record("groundedness", value, metadata=metadata)

    def compute_pk(self, value: float, k: int = 10) -> EvalMetricResult:
        return self._record(f"P@{k}", value, k=k)

    def compute_mrr(self, value: float) -> EvalMetricResult:
        return self._record("MRR", value)

    def compute_ndcg(self, value: float, k: int = 10) -> EvalMetricResult:
        return self._record(f"NDCG@{k}", value, k=k)

    def _record(
        self,
        name: str,
        value: float,
        k: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> EvalMetricResult:
        m = EvalMetricResult(
            metric_name=name,
            value=value,
            run_id=self.report.run_id,
            agent_id=self.report.agent_id,
            k=k,
            metadata=metadata or {},
        )
        self.report.metrics.append(m)
        return m

    # guardian: allow-magic-config
    def emit_drift_alert(
        self,
        metric_name: str,
        current_value: float,
        baseline_value: float,
        threshold: float = 0.05,
    ) -> DriftAlert:
        alert = DriftAlert(
            metric_name=metric_name,
            current_value=current_value,
            baseline_value=baseline_value,
            drift_magnitude=current_value - baseline_value,
            threshold=threshold,
            run_id=self.report.run_id,
            agent_id=self.report.agent_id,
        )
        self.report.drift_alerts.append(alert)
        return alert

    def build_dpo_batch(self, pairs: list[dict[str, Any]] | None = None) -> DPOBatch:
        batch = DPOBatch(run_id=self.report.run_id, agent_id=self.report.agent_id)
        for p in pairs or []:
            pair = PreferencePair(**{k: v for k, v in p.items() if k in PreferencePair.__dataclass_fields__})
            batch.pairs.append(pair)
        self.report.dpo_batches.append(batch)
        return batch

    def stage_proposal(
        self, dpo_batch: DPOBatch, weight_deltas: dict[str, float] | None = None
    ) -> OptimizationProposal:
        proposal = OptimizationProposal(
            dpo_batch_id=dpo_batch.batch_id,
            run_id=self.report.run_id,
            agent_id=self.report.agent_id,
            proposed_weight_deltas=weight_deltas or {},
        )
        self.report.proposals.append(proposal)
        return proposal

    def commit_optimization(self, proposal: OptimizationProposal) -> bool:
        proposal.stage = OptimizationStage.PROPOSAL_COMMITTED
        proposal.committed_at = time.time()
        return True

    def reject_proposal(self, proposal: OptimizationProposal, reason: str = "") -> None:
        proposal.stage = OptimizationStage.PROPOSAL_REJECTED
        proposal.rejection_reason = reason
