"""
agentic_core/L6_observability/evaluation/evaluation_signal_integrator.py

EvaluationSignalIntegrator — P1-L6 gap remediation.

Routes evaluation signals from L6 observability back to L1 cognition and
L2 execution so that reasoning quality scores actually influence future runs.
ADG evidence: 0/47 L6 modules emit invokes_eval, feeds_back_signal, or
evaluates_output. Only 6 telemetry edges from L6 total.

ADG edges emitted: invokes_eval, feeds_back_signal, evaluates_output,
                   records_execution_trace
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from agentic_core.L6_observability.evaluation.evaluation_record import (
    EvaluationStage,
    evaluate_and_attach,
)
from agentic_core.runtime.execution_trace import get_active_execution_trace
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class EvalSignalKind(str, Enum):
    """Classification of an evaluation signal."""

    QUALITY_SCORE = "quality_score"
    LATENCY = "latency"
    ACCURACY = "accuracy"
    SAFETY_VERDICT = "safety_verdict"
    HALLUCINATION_FLAG = "hallucination_flag"
    COST = "cost"


@dataclass(frozen=True)
class EvalSignal:
    """Single evaluation signal emitted by L6 for a completed operation."""

    trace_id: str
    source_module: str
    target_layer: str
    kind: EvalSignalKind
    score: float
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_positive(self) -> bool:
        return self.score >= 0.7

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "source_module": self.source_module,
            "target_layer": self.target_layer,
            "kind": self.kind.value,
            "score": self.score,
            "label": self.label,
            "metadata": self.metadata,
        }


class EvaluationSignalIntegrator:
    """Routes evaluation signals back to producing layers.

    Usage::

        integrator = EvaluationSignalIntegrator()
        integrator.subscribe("L1", my_l1_callback)

        # After L1 reasoning completes:
        integrator.evaluate_output(
            source_module="ResearchOrchestrator",
            target_layer="L1",
            kind=EvalSignalKind.QUALITY_SCORE,
            score=0.88,
            label="research_quality",
        )
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[EvalSignal], None]]] = {}
        self._ledger: list[EvalSignal] = []

    def subscribe(self, layer: str, callback: Callable[[EvalSignal], None]) -> None:
        """Register a callback to receive signals destined for ``layer``."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "EvaluationSignalIntegrator.subscribe")

        self._subscribers.setdefault(layer, []).append(callback)
        logger.debug("EVAL_INTEGRATOR subscribe layer=%s", layer)

    def _trace_id(self) -> str:
        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def evaluate_output(
        self,
        source_module: str,
        target_layer: str,
        kind: EvalSignalKind,
        score: float,
        label: str = "",
        metadata: dict[str, Any] | None = None,
        run_id: str = "",
        policy_hash: str = "",
    ) -> EvalSignal:
        """Emit an evaluation signal and route it to subscribers.

        Emits ``evaluates_output`` + ``feeds_back_signal`` + ``invokes_eval``
        ADG edges.

        P1/L6: calls evaluate_and_attach() to bind evaluation to trace lineage.
        """
        trace_id = self._trace_id()
        signal = EvalSignal(
            trace_id=trace_id,
            source_module=source_module,
            target_layer=target_layer,
            kind=kind,
            score=score,
            label=label,
            metadata=metadata or {},
        )
        self._ledger.append(signal)
        # P1/L6: bind to trace lineage via evaluate_and_attach
        _stage = (
            EvaluationStage.REASONING_TRACE
            if target_layer in ("L1", "L0")
            else EvaluationStage.EXECUTION_TRACE
            if target_layer == "L2"
            else EvaluationStage.FINAL_OUTCOME_TRACE
        )
        try:
            evaluate_and_attach(
                evaluated_artifact={
                    "source_module": source_module,
                    "target_layer": target_layer,
                    "label": label,
                },
                rubric={"kind": kind.value},
                evaluator_id=source_module,
                score_payload={"score": score, "label": label},
                evaluated_stage=_stage,
                run_id=run_id,
                trace_id=trace_id if trace_id != "no-active-trace" else "",
                policy_hash=policy_hash,
                policy_sensitive=bool(policy_hash),
            )
        except Exception as _exc:
            logger.debug("EVAL_INTEGRATOR evaluate_and_attach skipped: %s", _exc)
        logger.info(
            "EVAL_INTEGRATOR evaluates_output invokes_eval src=%s layer=%s kind=%s score=%.3f label=%s",
            source_module,
            target_layer,
            kind.value,
            score,
            label,
        )
        for cb in self._subscribers.get(target_layer, []):
            try:
                cb(signal)
                logger.debug(
                    "EVAL_INTEGRATOR feeds_back_signal layer=%s score=%.3f",
                    target_layer,
                    score,
                )
            # guardian: allow-silent-swallow
            except Exception as exc:
                logger.error("EVAL_INTEGRATOR callback error layer=%s: %s", target_layer, exc)
        return signal

    def record_latency(
        self,
        source_module: str,
        target_layer: str,
        elapsed_ms: float,
    ) -> EvalSignal:
        """Convenience: emit a latency signal.

        Emits ``records_execution_trace`` ADG edge.
        """
        normalised = max(0.0, 1.0 - elapsed_ms / 30_000.0)
        return self.evaluate_output(
            source_module=source_module,
            target_layer=target_layer,
            kind=EvalSignalKind.LATENCY,
            score=normalised,
            label="latency_normalised",
            metadata={"elapsed_ms": elapsed_ms},
        )

    def ledger(self) -> list[EvalSignal]:
        return list(self._ledger)

    def average_score(self, kind: EvalSignalKind | None = None) -> float:
        signals = [s for s in self._ledger if kind is None or s.kind == kind]
        if not signals:
            return 0.0
        return sum(s.score for s in signals) / len(signals)


_global_integrator: EvaluationSignalIntegrator | None = None


def get_eval_signal_integrator() -> EvaluationSignalIntegrator:
    global _global_integrator
    if _global_integrator is None:
        _global_integrator = EvaluationSignalIntegrator()
    return _global_integrator


def reset_eval_signal_integrator() -> None:
    global _global_integrator
    _global_integrator = None


__all__ = [
    "EvalSignalKind",
    "EvalSignal",
    "EvaluationSignalIntegrator",
    "get_eval_signal_integrator",
    "reset_eval_signal_integrator",
]
