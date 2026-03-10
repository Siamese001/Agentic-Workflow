"""
Phase 5: Evaluator-to-Proposer Bridge

Connects evaluation metrics, drift signals, and human feedback into a
unified improvement proposal for the Meta Learning Pipeline.

This bridge aggregates signals from:
- Offline evaluation reports (EvaluationReport)
- Drift monitoring snapshots (RetrievalDriftSnapshot, AnswerQualitySnapshot)
- Human feedback batches (DPOBatch)

And produces an ImprovementProposal that the Meta Learning Pipeline can
consume to decide on system configuration changes.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..monitoring.snapshots import AnswerQualitySnapshot, RetrievalDriftSnapshot
from ..schemas.evaluation_result_schema import EvaluationReport
from .schemas import DPOBatch


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _utcnow() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class ImprovementSignal:
    """A single improvement signal from one data source."""
    signal_type: str
    metric_name: str
    current_value: float
    target_value: float
    delta: float
    priority: str
    source: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_type": self.signal_type,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "delta": self.delta,
            "priority": self.priority,
            "source": self.source,
            "message": self.message,
        }


@dataclass
class ImprovementProposal:
    """Unified improvement proposal for the Meta Learning Pipeline."""
    proposal_id: str
    timestamp: str
    signals: list[ImprovementSignal]
    dpo_pair_count: int
    recommended_actions: list[str]
    overall_health_score: float
    requires_intervention: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "timestamp": self.timestamp,
            "signals": [s.to_dict() for s in self.signals],
            "dpo_pair_count": self.dpo_pair_count,
            "recommended_actions": self.recommended_actions,
            "overall_health_score": self.overall_health_score,
            "requires_intervention": self.requires_intervention,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ImprovementProposal:
        return cls(
            proposal_id=data["proposal_id"],
            timestamp=data["timestamp"],
            signals=[
                ImprovementSignal(**s) for s in data.get("signals", [])
            ],
            dpo_pair_count=data["dpo_pair_count"],
            recommended_actions=data["recommended_actions"],
            overall_health_score=data["overall_health_score"],
            requires_intervention=data["requires_intervention"],
            metadata=data.get("metadata", {}),
        )


class EvaluatorProposerBridge:
    """Aggregates all evaluation signals and emits an ImprovementProposal.

    Connects:
    - EvaluationReport (offline eval scores)
    - RetrievalDriftSnapshot (retrieval health)
    - AnswerQualitySnapshot (answer quality drift)
    - DPOBatch (human feedback signal strength)

    to: Meta Learning proposal generator
    """

    RETRIEVAL_TARGETS: dict[str, float] = {
        "precision@5": 0.80,
        "recall@10": 0.85,
        "MRR": 0.80,
        "NDCG@10": 0.80,
    }

    QUALITY_TARGETS: dict[str, float] = {
        "groundedness": 0.85,
        "answer_correctness": 0.80,
    }

    def __init__(self, l4_store: Any | None = None):
        self.l4_store = l4_store

    def propose(
        self,
        eval_report: EvaluationReport | None = None,
        retrieval_snapshot: RetrievalDriftSnapshot | None = None,
        answer_snapshot: AnswerQualitySnapshot | None = None,
        dpo_batch: DPOBatch | None = None,
    ) -> ImprovementProposal:
        """Build an ImprovementProposal from available signals.

        Args:
            eval_report: Latest offline evaluation report
            retrieval_snapshot: Latest retrieval drift snapshot
            answer_snapshot: Latest answer quality snapshot
            dpo_batch: Latest DPO batch from human feedback

        Returns:
            ImprovementProposal for the Meta Learning Pipeline
        """
        signals: list[ImprovementSignal] = []

        if eval_report is not None:
            signals.extend(self._signals_from_eval(eval_report))

        if retrieval_snapshot is not None:
            signals.extend(self._signals_from_retrieval(retrieval_snapshot))

        if answer_snapshot is not None:
            signals.extend(self._signals_from_answer(answer_snapshot))

        dpo_count = dpo_batch.pair_count if dpo_batch is not None else 0

        actions = self._recommend_actions(signals, dpo_count)
        health = self._compute_health_score(signals)
        requires_intervention = any(s.priority == "critical" for s in signals) or health < 0.60

        proposal = ImprovementProposal(
            proposal_id=str(uuid.uuid4()),
            timestamp=_utcnow(),
            signals=signals,
            dpo_pair_count=dpo_count,
            recommended_actions=actions,
            overall_health_score=health,
            requires_intervention=requires_intervention,
        )

        if self.l4_store is not None:
            self._persist(proposal)

        return proposal

    def _signals_from_eval(
        self, report: EvaluationReport
    ) -> list[ImprovementSignal]:
        """Extract improvement signals from eval report aggregate scores."""
        signals = []
        for metric, target in {**self.RETRIEVAL_TARGETS, **self.QUALITY_TARGETS}.items():
            current = report.aggregate_scores.get(metric)
            if current is None:
                continue
            delta = current - target
            priority = "ok" if delta >= 0 else ("critical" if delta < -0.15 else "warning")
            signals.append(ImprovementSignal(
                signal_type="eval_metric",
                metric_name=metric,
                current_value=current,
                target_value=target,
                delta=delta,
                priority=priority,
                source=f"eval_report:{report.run_id[:8]}",
                message=f"{metric} = {current:.3f} (target {target:.3f}, delta {delta:+.3f})",
            ))
        return signals

    def _signals_from_retrieval(
        self, snapshot: RetrievalDriftSnapshot
    ) -> list[ImprovementSignal]:
        """Extract signals from retrieval drift snapshot."""
        signals = []
        hit_target = 0.75
        delta = snapshot.retrieval_hit_rate - hit_target
        priority = "ok" if delta >= 0 else ("critical" if delta < -0.20 else "warning")
        signals.append(ImprovementSignal(
            signal_type="retrieval_drift",
            metric_name="retrieval_hit_rate",
            current_value=snapshot.retrieval_hit_rate,
            target_value=hit_target,
            delta=delta,
            priority=priority,
            source=f"retrieval_snapshot:{snapshot.timestamp[:10]}",
            message=f"Hit rate {snapshot.retrieval_hit_rate:.3f} vs target {hit_target:.3f}",
        ))
        return signals

    def _signals_from_answer(
        self, snapshot: AnswerQualitySnapshot
    ) -> list[ImprovementSignal]:
        """Extract signals from answer quality snapshot."""
        signals = []

        groundedness_target = 0.80
        g_delta = snapshot.groundedness_rate - groundedness_target
        g_priority = "ok" if g_delta >= 0 else ("critical" if g_delta < -0.20 else "warning")
        signals.append(ImprovementSignal(
            signal_type="answer_quality_drift",
            metric_name="groundedness_rate",
            current_value=snapshot.groundedness_rate,
            target_value=groundedness_target,
            delta=g_delta,
            priority=g_priority,
            source=f"answer_snapshot:{snapshot.timestamp[:10]}",
            message=f"Groundedness rate {snapshot.groundedness_rate:.3f}",
        ))

        hall_target = 0.10
        h_delta = hall_target - snapshot.hallucination_rate
        h_priority = "ok" if h_delta >= 0 else ("critical" if h_delta < -0.15 else "warning")
        signals.append(ImprovementSignal(
            signal_type="answer_quality_drift",
            metric_name="hallucination_rate",
            current_value=snapshot.hallucination_rate,
            target_value=hall_target,
            delta=h_delta,
            priority=h_priority,
            source=f"answer_snapshot:{snapshot.timestamp[:10]}",
            message=f"Hallucination rate {snapshot.hallucination_rate:.3f} (target < {hall_target:.3f})",
        ))

        return signals

    def _recommend_actions(
        self, signals: list[ImprovementSignal], dpo_count: int
    ) -> list[str]:
        """Build a deterministic list of recommended actions."""
        actions: list[str] = []

        critical = [s for s in signals if s.priority == "critical"]
        warning = [s for s in signals if s.priority == "warning"]

        for sig in critical:
            if sig.metric_name in ("retrieval_hit_rate", "precision@5", "recall@10"):
                actions.append("upgrade_to_hybrid_reranked_retrieval")
            elif sig.metric_name in ("groundedness", "groundedness_rate"):
                actions.append("increase_context_window")
            elif sig.metric_name == "hallucination_rate":
                actions.append("tighten_generation_constraints")

        for sig in warning:
            if sig.metric_name in ("MRR", "NDCG@10"):
                actions.append("tune_reranker")
            elif sig.metric_name == "answer_correctness":
                actions.append("improve_prompt_template")

        if dpo_count > 10:
            actions.append("trigger_dpo_finetuning")
        elif dpo_count > 0:
            actions.append("accumulate_more_dpo_pairs")

        return sorted(set(actions))

    def _compute_health_score(self, signals: list[ImprovementSignal]) -> float:
        """Compute an overall system health score from signals."""
        if not signals:
            return 1.0
        ok = sum(1 for s in signals if s.priority == "ok")
        return ok / len(signals)

    def _persist(self, proposal: ImprovementProposal) -> None:
        try:
            from agentic_core.L4_state.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="improvement_proposal",
                logical_id=f"proposal_{proposal.proposal_id[:8]}",
                payload=proposal.to_dict(),
            )
            self.l4_store.put(artifact)
        except Exception:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            pass


__all__ = [
    "ImprovementSignal",
    "ImprovementProposal",
    "EvaluatorProposerBridge",
]
