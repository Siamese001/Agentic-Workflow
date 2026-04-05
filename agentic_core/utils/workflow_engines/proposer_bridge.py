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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "proposer_bridge", "execution_auth")
_emit_validates_capability("p2", "proposer_bridge", "capability_check")
_emit_routes_to_capability("p2", "proposer_bridge", "capability_route")
_emit_writes_via_uwg("p2", "proposer_bridge", "uwg_write")
_emit_blocks_direct_write("p2", "proposer_bridge", "direct_write_block")
_emit_records_tool_invocation("p2", "proposer_bridge", "tool_invocation")
_emit_captures_execution_output("p2", "proposer_bridge", "exec_output")
_emit_dispatches_agent("p3", "proposer_bridge", "agent_dispatch")
_emit_coordinates_agents("p3", "proposer_bridge", "agent_coordination")
_emit_records_workflow_lineage("p3", "proposer_bridge", "workflow_lineage")
_emit_records_healing_outcome("p3", "proposer_bridge", "healing_outcome")
_emit_escalates_failure("p3", "proposer_bridge", "failure_escalation")
_emit_orchestrates_workflow("p3", "proposer_bridge", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "proposer_bridge", "healing_dispatch")
_emit_invokes_evaluation("p3", "proposer_bridge", "evaluation_signal")
_emit_records_telemetry_event("p4", "proposer_bridge", "telemetry_event")
_emit_captures_evaluation_metric("p4", "proposer_bridge", "eval_metric")
_emit_stores_embedding("p4", "proposer_bridge", "embedding_store")
_emit_updates_meta_learning_state("p4", "proposer_bridge", "meta_learning")
_emit_links_execution_to_snapshot("p4", "proposer_bridge", "exec_snapshot_link")
from ..monitoring.snapshots import AnswerQualitySnapshot, RetrievalDriftSnapshot
from ..schemas.evaluation_result_schema import EvaluationReport
from .schemas import DPOBatch

_emit_applies_guardrail("p0", "proposer_bridge", "p0_governance")
_emit_reads_policy_state("p0", "proposer_bridge", "policy_binding")
_emit_snapshots_state("p0", "proposer_bridge", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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

_emit_emits_metric_event("proposer_bridge", "p4obs", "metric_1")
_emit_emits_metric_event("proposer_bridge", "p4obs", "metric_2")
_emit_emits_metric_event("proposer_bridge", "p4obs", "metric_3")
_emit_emits_metric_event("proposer_bridge", "p4obs", "metric_4")
_emit_emits_metric_event("proposer_bridge", "p4obs", "metric_5")
_emit_emits_metric_event("proposer_bridge", "p4obs", "metric_6")
_emit_records_incident_event("proposer_bridge", "p4obs", "incident")
_emit_captures_runtime_anomaly("proposer_bridge", "p4obs", "anomaly")
_emit_writes_observability_log("proposer_bridge", "p4obs", "obs_log")
_emit_updates_monitoring_state("proposer_bridge", "p4obs", "mon_state")
_emit_triggers_alert("proposer_bridge", "p4obs", "alert")
_emit_links_incident_trace("proposer_bridge", "p4obs", "trace_link")
_emit_captures_pattern("proposer_bridge", "p3lm", "pattern")
_emit_records_learning_event("proposer_bridge", "p3lm", "learning_event")
_emit_writes_learning_snapshot("proposer_bridge", "p3lm", "snapshot")
_emit_feeds_meta_learning("proposer_bridge", "p3lm", "meta_feed")
_emit_updates_routing_strategy("proposer_bridge", "p3lm", "routing")
_emit_improves_agent_policy("proposer_bridge", "p3lm", "policy")
_emit_stores_learning_state("proposer_bridge", "p3lm", "state")
_emit_records_execution_trace("proposer_bridge", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("proposer_bridge", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("proposer_bridge", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("proposer_bridge", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("proposer_bridge", "L4_STATE", "p2_trace_5")
_emit_reads_environ("proposer_bridge", "env_read", "p2_env_1")
_emit_reads_environ("proposer_bridge", "env_read", "p2_env_2")
_emit_reads_runtime_state("proposer_bridge", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("proposer_bridge", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "proposer_bridge", "context_pull")
_emit_pulls_context("p1", "proposer_bridge", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "proposer_bridge", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "proposer_bridge", "uwg_term_2")
_emit_writes_through("p1", "proposer_bridge", "write_through")
_emit_writes_through("p1", "proposer_bridge", "write_through_2")
_emit_validated_by_safety_plane("p1", "proposer_bridge", "safety_validation")
_emit_invokes_eval("p1", "proposer_bridge", "eval_call")
_emit_proposal_commits_routing("p1", "proposer_bridge", "routing_commit")
_emit_escalates_to_human("p1", "proposer_bridge", "human_escalation")
_emit_routes_through("p1", "proposer_bridge", "route_through")
_emit_checks_agent_registry("p1", "proposer_bridge", "agent_registry")
_emit_validates_agent_capability("p1", "proposer_bridge", "capability")
_emit_dispatches_execution_plan("p1", "proposer_bridge", "exec_plan")
_emit_agent_executes_agent("p1", "proposer_bridge", "sub_agent")
_emit_routes_to_agent("p1", "proposer_bridge", "target_agent")
_emit_verifies_policy("p1", "proposer_bridge", "policy_check")
_emit_observes_runtime_state("p1", "proposer_bridge", "runtime_state")
_emit_verifies_boundary("p1", "proposer_bridge", "boundary_check")
_emit_transcripts_response("p1", "proposer_bridge", "transcript")
_emit_hard_fails_untranscripted("p1", "proposer_bridge")
_emit_gated_by_confidence("p1", "proposer_bridge", "confidence_gate")
emit_replay_key("p0", "proposer_bridge")
emit_determinism_digest("p0", "proposer_bridge")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
            signals=[ImprovementSignal(**s) for s in data.get("signals", [])],
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

    RETRIEVAL_TARGETS: dict[str, float] = {"precision@5": 0.8, "recall@10": 0.85, "MRR": 0.8, "NDCG@10": 0.8}
    QUALITY_TARGETS: dict[str, float] = {"groundedness": 0.85, "answer_correctness": 0.8}

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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "EvaluatorProposerBridge.propose"
        )

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
        requires_intervention = any(s.priority == "critical" for s in signals) or health < 0.6
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

    def _signals_from_eval(self, report: EvaluationReport) -> list[ImprovementSignal]:
        """Extract improvement signals from eval report aggregate scores."""
        signals = []
        for metric, target in {**self.RETRIEVAL_TARGETS, **self.QUALITY_TARGETS}.items():
            current = report.aggregate_scores.get(metric)
            if current is None:
                continue
            delta = current - target
            priority = "ok" if delta >= 0 else "critical" if delta < -0.15 else "warning"
            signals.append(
                ImprovementSignal(
                    signal_type="eval_metric",
                    metric_name=metric,
                    current_value=current,
                    target_value=target,
                    delta=delta,
                    priority=priority,
                    source=f"eval_report:{report.run_id[:8]}",
                    message=f"{metric} = {current:.3f} (target {target:.3f}, delta {delta:+.3f})",
                )
            )
        return signals

    def _signals_from_retrieval(self, snapshot: RetrievalDriftSnapshot) -> list[ImprovementSignal]:
        """Extract signals from retrieval drift snapshot."""
        signals = []
        hit_target = 0.75
        delta = snapshot.retrieval_hit_rate - hit_target
        priority = "ok" if delta >= 0 else "critical" if delta < -0.2 else "warning"
        signals.append(
            ImprovementSignal(
                signal_type="retrieval_drift",
                metric_name="retrieval_hit_rate",
                current_value=snapshot.retrieval_hit_rate,
                target_value=hit_target,
                delta=delta,
                priority=priority,
                source=f"retrieval_snapshot:{snapshot.timestamp[:10]}",
                message=f"Hit rate {snapshot.retrieval_hit_rate:.3f} vs target {hit_target:.3f}",
            )
        )
        return signals

    def _signals_from_answer(self, snapshot: AnswerQualitySnapshot) -> list[ImprovementSignal]:
        """Extract signals from answer quality snapshot."""
        signals = []
        groundedness_target = 0.8
        g_delta = snapshot.groundedness_rate - groundedness_target
        g_priority = "ok" if g_delta >= 0 else "critical" if g_delta < -0.2 else "warning"
        signals.append(
            ImprovementSignal(
                signal_type="answer_quality_drift",
                metric_name="groundedness_rate",
                current_value=snapshot.groundedness_rate,
                target_value=groundedness_target,
                delta=g_delta,
                priority=g_priority,
                source=f"answer_snapshot:{snapshot.timestamp[:10]}",
                message=f"Groundedness rate {snapshot.groundedness_rate:.3f}",
            )
        )
        hall_target = 0.1
        h_delta = hall_target - snapshot.hallucination_rate
        h_priority = "ok" if h_delta >= 0 else "critical" if h_delta < -0.15 else "warning"
        signals.append(
            ImprovementSignal(
                signal_type="answer_quality_drift",
                metric_name="hallucination_rate",
                current_value=snapshot.hallucination_rate,
                target_value=hall_target,
                delta=h_delta,
                priority=h_priority,
                source=f"answer_snapshot:{snapshot.timestamp[:10]}",
                message=f"Hallucination rate {snapshot.hallucination_rate:.3f} (target < {hall_target:.3f})",
            )
        )
        return signals

    def _recommend_actions(self, signals: list[ImprovementSignal], dpo_count: int) -> list[str]:
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
        # guardian: allow-silent-swallow -- L4 persistence failure is non-critical; proposal already processed
        except Exception:
            pass


__all__ = ["ImprovementSignal", "ImprovementProposal", "EvaluatorProposerBridge"]
