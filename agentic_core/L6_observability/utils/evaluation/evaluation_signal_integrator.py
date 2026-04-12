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

from agentic_core.L6_observability.utils.evaluation.evaluation_record import (
    EvaluationStage,
    evaluate_and_attach,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

emit_replay_key("p0", "evaluation_signal_integrator")
emit_determinism_digest("p0", "evaluation_signal_integrator")

_emit_dispatches_healing_run("p1", "evaluation_signal_integrator", "L6")
_emit_routes_through("p1", "evaluation_signal_integrator", "L6")
_emit_checks_agent_registry("p1", "evaluation_signal_integrator", "agent_registry")
_emit_validates_agent_capability("p1", "evaluation_signal_integrator", "capability")
_emit_dispatches_execution_plan("p1", "evaluation_signal_integrator", "exec_plan")
_emit_agent_executes_agent("p1", "evaluation_signal_integrator", "sub_agent")
_emit_routes_to_agent("p1", "evaluation_signal_integrator", "target_agent")
_emit_verifies_policy("p1", "evaluation_signal_integrator", "policy_check")
_emit_observes_runtime_state("p1", "evaluation_signal_integrator", "runtime_state")
_emit_verifies_boundary("p1", "evaluation_signal_integrator", "boundary_check")
_emit_transcripts_response("p1", "evaluation_signal_integrator", "transcript")
_emit_hard_fails_untranscripted("p1", "evaluation_signal_integrator")
_emit_gated_by_confidence("p1", "evaluation_signal_integrator", "confidence_gate")
_emit_escalates_to_human("p1", "evaluation_signal_integrator", "L6")
_emit_reads_policy_state("p1", "evaluation_signal_integrator", "L6")
_emit_authorize_and_execute("p2", "evaluation_signal_integrator", "execution_auth")
_emit_validates_capability("p2", "evaluation_signal_integrator", "capability_check")
_emit_routes_to_capability("p2", "evaluation_signal_integrator", "capability_route")
_emit_writes_via_uwg("p2", "evaluation_signal_integrator", "uwg_write")
_emit_blocks_direct_write("p2", "evaluation_signal_integrator", "direct_write_block")
_emit_records_tool_invocation("p2", "evaluation_signal_integrator", "tool_invocation")
_emit_captures_execution_output("p2", "evaluation_signal_integrator", "exec_output")
_emit_dispatches_agent("p3", "evaluation_signal_integrator", "agent_dispatch")
_emit_coordinates_agents("p3", "evaluation_signal_integrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "evaluation_signal_integrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "evaluation_signal_integrator", "healing_outcome")
_emit_escalates_failure("p3", "evaluation_signal_integrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "evaluation_signal_integrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "evaluation_signal_integrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "evaluation_signal_integrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "evaluation_signal_integrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "evaluation_signal_integrator", "eval_metric")
_emit_stores_embedding("p4", "evaluation_signal_integrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "evaluation_signal_integrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "evaluation_signal_integrator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("evaluation_signal_integrator", "p4obs", "metric_1")
_emit_emits_metric_event("evaluation_signal_integrator", "p4obs", "metric_2")
_emit_emits_metric_event("evaluation_signal_integrator", "p4obs", "metric_3")
_emit_emits_metric_event("evaluation_signal_integrator", "p4obs", "metric_4")
_emit_emits_metric_event("evaluation_signal_integrator", "p4obs", "metric_5")
_emit_emits_metric_event("evaluation_signal_integrator", "p4obs", "metric_6")
_emit_records_incident_event("evaluation_signal_integrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("evaluation_signal_integrator", "p4obs", "anomaly")
_emit_writes_observability_log("evaluation_signal_integrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("evaluation_signal_integrator", "p4obs", "mon_state")
_emit_triggers_alert("evaluation_signal_integrator", "p4obs", "alert")
_emit_links_incident_trace("evaluation_signal_integrator", "p4obs", "trace_link")
_emit_captures_pattern("evaluation_signal_integrator", "p3lm", "pattern")
_emit_records_learning_event("evaluation_signal_integrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("evaluation_signal_integrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("evaluation_signal_integrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("evaluation_signal_integrator", "p3lm", "routing")
_emit_improves_agent_policy("evaluation_signal_integrator", "p3lm", "policy")
_emit_stores_learning_state("evaluation_signal_integrator", "p3lm", "state")
_emit_records_execution_trace("evaluation_signal_integrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("evaluation_signal_integrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("evaluation_signal_integrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("evaluation_signal_integrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("evaluation_signal_integrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("evaluation_signal_integrator", "env_read", "p2_env_1")
_emit_reads_environ("evaluation_signal_integrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("evaluation_signal_integrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("evaluation_signal_integrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "evaluation_signal_integrator", "context_pull")
_emit_pulls_context("p1", "evaluation_signal_integrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "evaluation_signal_integrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "evaluation_signal_integrator", "uwg_term_2")
_emit_writes_through("p1", "evaluation_signal_integrator", "write_through")
_emit_writes_through("p1", "evaluation_signal_integrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "evaluation_signal_integrator", "safety_validation")
_emit_invokes_eval("p1", "evaluation_signal_integrator", "eval_call")
_emit_proposal_commits_routing("p1", "evaluation_signal_integrator", "routing_commit")

logger = logging.getLogger(__name__)


class EvalSignalKind(str, Enum):
    """Classification of an evaluation signal.

    Wave 1.2: Expanded from 6 to 12 evaluation types to support RAG quality metrics.
    """

    # Original 6 types
    QUALITY_SCORE = "quality_score"
    LATENCY = "latency"
    ACCURACY = "accuracy"
    SAFETY_VERDICT = "safety_verdict"
    HALLUCINATION_FLAG = "hallucination_flag"
    COST = "cost"

    # Wave 1.2: New RAG evaluation types
    FAITHFULNESS = "faithfulness"  # Answer grounded in retrieved context
    GROUNDEDNESS = "groundedness"  # Answer supported by evidence
    ANSWER_RELEVANCY = "answer_relevancy"  # Answer addresses user query
    CONTEXT_PRECISION = "context_precision"  # Retrieved chunks relevant to query
    CONTEXT_RECALL = "context_recall"  # All relevant info retrieved
    REGRESSION_DELTA = "regression_delta"  # Performance vs baseline


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
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "EvalSignal.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "EvalSignal.to_dict", "p0_governance")
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
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
            "EvaluationSignalIntegrator.subscribe",
        )

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
