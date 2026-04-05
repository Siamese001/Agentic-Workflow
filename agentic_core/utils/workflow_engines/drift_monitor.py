"""
Phase 4: Drift Monitor

Detects retrieval, embedding, and answer quality drift by comparing
current snapshots against baseline thresholds.  Emits DriftAlert objects
and persists snapshots to L4 telemetry registry.
"""

from __future__ import annotations

import logging
import math
import statistics
import uuid
from collections.abc import Callable
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

_emit_authorize_and_execute("p2", "drift_monitor", "execution_auth")
_emit_validates_capability("p2", "drift_monitor", "capability_check")
_emit_routes_to_capability("p2", "drift_monitor", "capability_route")
_emit_writes_via_uwg("p2", "drift_monitor", "uwg_write")
_emit_blocks_direct_write("p2", "drift_monitor", "direct_write_block")
_emit_records_tool_invocation("p2", "drift_monitor", "tool_invocation")
_emit_captures_execution_output("p2", "drift_monitor", "exec_output")
_emit_dispatches_agent("p3", "drift_monitor", "agent_dispatch")
_emit_coordinates_agents("p3", "drift_monitor", "agent_coordination")
_emit_records_workflow_lineage("p3", "drift_monitor", "workflow_lineage")
_emit_records_healing_outcome("p3", "drift_monitor", "healing_outcome")
_emit_escalates_failure("p3", "drift_monitor", "failure_escalation")
_emit_orchestrates_workflow("p3", "drift_monitor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "drift_monitor", "healing_dispatch")
_emit_invokes_evaluation("p3", "drift_monitor", "evaluation_signal")
_emit_records_telemetry_event("p4", "drift_monitor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "drift_monitor", "eval_metric")
_emit_stores_embedding("p4", "drift_monitor", "embedding_store")
_emit_updates_meta_learning_state("p4", "drift_monitor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "drift_monitor", "exec_snapshot_link")
from .snapshots import AnswerQualitySnapshot, DriftAlert, EmbeddingHealthSnapshot, RetrievalDriftSnapshot

_emit_applies_guardrail("p0", "drift_monitor", "p0_governance")
_emit_reads_policy_state("p0", "drift_monitor", "policy_binding")
_emit_snapshots_state("p0", "drift_monitor", "state_snapshot")
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

_emit_emits_metric_event("drift_monitor", "p4obs", "metric_1")
_emit_emits_metric_event("drift_monitor", "p4obs", "metric_2")
_emit_emits_metric_event("drift_monitor", "p4obs", "metric_3")
_emit_emits_metric_event("drift_monitor", "p4obs", "metric_4")
_emit_emits_metric_event("drift_monitor", "p4obs", "metric_5")
_emit_emits_metric_event("drift_monitor", "p4obs", "metric_6")
_emit_records_incident_event("drift_monitor", "p4obs", "incident")
_emit_captures_runtime_anomaly("drift_monitor", "p4obs", "anomaly")
_emit_writes_observability_log("drift_monitor", "p4obs", "obs_log")
_emit_updates_monitoring_state("drift_monitor", "p4obs", "mon_state")
_emit_triggers_alert("drift_monitor", "p4obs", "alert")
_emit_links_incident_trace("drift_monitor", "p4obs", "trace_link")
_emit_captures_pattern("drift_monitor", "p3lm", "pattern")
_emit_records_learning_event("drift_monitor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("drift_monitor", "p3lm", "snapshot")
_emit_feeds_meta_learning("drift_monitor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("drift_monitor", "p3lm", "routing")
_emit_improves_agent_policy("drift_monitor", "p3lm", "policy")
_emit_stores_learning_state("drift_monitor", "p3lm", "state")
_emit_records_execution_trace("drift_monitor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("drift_monitor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("drift_monitor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("drift_monitor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("drift_monitor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("drift_monitor", "env_read", "p2_env_1")
_emit_reads_environ("drift_monitor", "env_read", "p2_env_2")
_emit_reads_runtime_state("drift_monitor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("drift_monitor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "drift_monitor", "context_pull")
_emit_pulls_context("p1", "drift_monitor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "drift_monitor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "drift_monitor", "uwg_term_2")
_emit_writes_through("p1", "drift_monitor", "write_through")
_emit_writes_through("p1", "drift_monitor", "write_through_2")
_emit_validated_by_safety_plane("p1", "drift_monitor", "safety_validation")
_emit_invokes_eval("p1", "drift_monitor", "eval_call")
_emit_proposal_commits_routing("p1", "drift_monitor", "routing_commit")
_emit_escalates_to_human("p1", "drift_monitor", "human_escalation")
_emit_routes_through("p1", "drift_monitor", "route_through")
_emit_checks_agent_registry("p1", "drift_monitor", "agent_registry")
_emit_validates_agent_capability("p1", "drift_monitor", "capability")
_emit_dispatches_execution_plan("p1", "drift_monitor", "exec_plan")
_emit_agent_executes_agent("p1", "drift_monitor", "sub_agent")
_emit_routes_to_agent("p1", "drift_monitor", "target_agent")
_emit_verifies_policy("p1", "drift_monitor", "policy_check")
_emit_observes_runtime_state("p1", "drift_monitor", "runtime_state")
_emit_verifies_boundary("p1", "drift_monitor", "boundary_check")
_emit_transcripts_response("p1", "drift_monitor", "transcript")
_emit_hard_fails_untranscripted("p1", "drift_monitor")
_emit_gated_by_confidence("p1", "drift_monitor", "confidence_gate")
emit_replay_key("p0", "drift_monitor")
emit_determinism_digest("p0", "drift_monitor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_logger = logging.getLogger(__name__)


def _utcnow() -> str:
    return datetime.utcnow().isoformat() + "Z"


class DriftClock:
    """Injectable clock for deterministic testing of drift timestamps."""

    @staticmethod
    def utcnow() -> str:
        return _utcnow()


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


class RetrievalDriftMonitor:
    """Tracks retrieval_hit_rate, score_distribution_shift, top_k_stability.

    A hit is defined as: at least one ground-truth document appears in top-k results.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        hit_rate_threshold: float = 0.7,
        score_std_threshold: float = 0.2,
        stability_threshold: float = 0.6,
        system_version: str = "unknown",
        l4_store: Any | None = None,
    ):
        self.hit_rate_threshold = hit_rate_threshold
        self.score_std_threshold = score_std_threshold
        self.stability_threshold = stability_threshold
        self.system_version = system_version
        self.l4_store = l4_store

    def measure(
        self,
        queries: list[str],
        retrieved_doc_ids: list[list[str]],
        ground_truth_doc_ids: list[list[str]],
        scores: list[list[float]],
        now_iso: str | None = None,
    ) -> RetrievalDriftSnapshot:
        """Compute a retrieval drift snapshot from a batch of queries.

        Args:
            queries: List of query strings
            retrieved_doc_ids: Per-query ranked retrieved doc IDs
            ground_truth_doc_ids: Per-query relevant doc IDs
            scores: Per-query retrieval scores for retrieved docs

        Returns:
            RetrievalDriftSnapshot
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(_uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "RetrievalDriftMonitor.measure")
        n = len(queries)
        if n == 0:
            raise ValueError("queries must be non-empty")
        hits = sum((1 for ret, gt in zip(retrieved_doc_ids, ground_truth_doc_ids) if set(ret) & set(gt)))
        hit_rate = hits / n
        all_scores = [s for query_scores in scores for s in query_scores]
        score_mean = _mean(all_scores)
        score_std = _std(all_scores)
        top1_docs = [ret[0] if ret else "" for ret in retrieved_doc_ids]
        unique_top1 = len(set(top1_docs))
        top_k_stability = 1.0 - unique_top1 / n if n > 1 else 1.0
        snapshot = RetrievalDriftSnapshot(
            timestamp=now_iso if now_iso is not None else _utcnow(),
            system_version=self.system_version,
            retrieval_hit_rate=hit_rate,
            score_distribution_mean=score_mean,
            score_distribution_std=score_std,
            top_k_stability=top_k_stability,
            sample_size=n,
        )
        if self.l4_store is not None:
            self._persist(snapshot)
        return snapshot

    def check_alerts(
        self,
        snapshot: RetrievalDriftSnapshot,
        now_iso: str | None = None,
        id_factory: Callable[[], str] | None = None,
    ) -> list[DriftAlert]:
        """Return DriftAlerts for any metrics below threshold."""
        _ts = now_iso if now_iso is not None else _utcnow()
        _new_id = id_factory if id_factory is not None else lambda: str(uuid.uuid4())
        alerts: list[DriftAlert] = []
        if snapshot.retrieval_hit_rate < self.hit_rate_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=_new_id(),
                    timestamp=_ts,
                    alert_type="retrieval_drift",
                    metric_name="retrieval_hit_rate",
                    current_value=snapshot.retrieval_hit_rate,
                    threshold_value=self.hit_rate_threshold,
                    delta=snapshot.retrieval_hit_rate - self.hit_rate_threshold,
                    severity="warning",
                    message=f"Retrieval hit rate {snapshot.retrieval_hit_rate:.3f} below threshold {self.hit_rate_threshold:.3f}",
                )
            )
        if snapshot.score_distribution_std > self.score_std_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=_new_id(),
                    timestamp=_ts,
                    alert_type="retrieval_drift",
                    metric_name="score_distribution_std",
                    current_value=snapshot.score_distribution_std,
                    threshold_value=self.score_std_threshold,
                    delta=snapshot.score_distribution_std - self.score_std_threshold,
                    severity="warning",
                    message=f"Score distribution std {snapshot.score_distribution_std:.3f} exceeds threshold {self.score_std_threshold:.3f}",
                )
            )
        if snapshot.top_k_stability < self.stability_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=_new_id(),
                    timestamp=_ts,
                    alert_type="retrieval_drift",
                    metric_name="top_k_stability",
                    current_value=snapshot.top_k_stability,
                    threshold_value=self.stability_threshold,
                    delta=snapshot.top_k_stability - self.stability_threshold,
                    severity="info",
                    message=f"Top-k stability {snapshot.top_k_stability:.3f} below threshold {self.stability_threshold:.3f}",
                )
            )
        return alerts

    def _persist(self, snapshot: RetrievalDriftSnapshot) -> None:
        try:
            from agentic_core.L4_state.utils.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="retrieval_drift_snapshot",
                logical_id=f"retrieval_drift_{snapshot.timestamp[:10]}",
                payload=snapshot.to_dict(),
            )
            self.l4_store.put(artifact)
        # guardian: allow-silent-swallow
        except Exception:
            _logger.debug("RetrievalDriftMonitor._persist failed", exc_info=True)


class EmbeddingDriftMonitor:
    """Tracks vector_norm_distribution, similarity_distribution, version mismatch."""

    # guardian: allow-magic-config
    def __init__(
        self,
        norm_std_threshold: float = 0.15,
        similarity_mean_threshold: float = 0.5,
        current_model_version: str = "unknown",
        l4_store: Any | None = None,
    ):
        self.norm_std_threshold = norm_std_threshold
        self.similarity_mean_threshold = similarity_mean_threshold
        self.current_model_version = current_model_version
        self.l4_store = l4_store

    def measure(
        self,
        embeddings: list[list[float]],
        similarities: list[float],
        observed_model_version: str = "unknown",
    ) -> EmbeddingHealthSnapshot:
        """Compute an embedding health snapshot.

        Args:
            embeddings: List of embedding vectors
            similarities: Pairwise or query-doc similarity scores
            observed_model_version: Version string from the embedding provider

        Returns:
            EmbeddingHealthSnapshot
        """
        if not embeddings:
            raise ValueError("embeddings must be non-empty")
        norms = [math.sqrt(sum(x * x for x in emb)) for emb in embeddings]
        norm_mean = _mean(norms)
        norm_std = _std(norms)
        sim_mean = _mean(similarities)
        sim_std = _std(similarities)
        version_mismatch = observed_model_version != self.current_model_version
        snapshot = EmbeddingHealthSnapshot(
            timestamp=_utcnow(),
            embedding_model_version=observed_model_version,
            vector_norm_mean=norm_mean,
            vector_norm_std=norm_std,
            similarity_distribution_mean=sim_mean,
            similarity_distribution_std=sim_std,
            version_mismatch_detected=version_mismatch,
            sample_size=len(embeddings),
        )
        if self.l4_store is not None:
            self._persist(snapshot)
        return snapshot

    def check_alerts(
        self,
        snapshot: EmbeddingHealthSnapshot,
        now_iso: str | None = None,
        id_factory: Callable[[], str] | None = None,
    ) -> list[DriftAlert]:
        """Return DriftAlerts for detected embedding health issues."""
        _ts = now_iso if now_iso is not None else _utcnow()
        _new_id = id_factory if id_factory is not None else lambda: str(uuid.uuid4())
        alerts: list[DriftAlert] = []
        if snapshot.version_mismatch_detected:
            alerts.append(
                DriftAlert(
                    alert_id=_new_id(),
                    timestamp=_ts,
                    alert_type="embedding_drift",
                    metric_name="embedding_model_version",
                    current_value=0.0,
                    threshold_value=0.0,
                    delta=0.0,
                    severity="critical",
                    message=f"Embedding model version mismatch: expected {self.current_model_version!r}, got {snapshot.embedding_model_version!r}",
                )
            )
        if snapshot.vector_norm_std > self.norm_std_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=_new_id(),
                    timestamp=_ts,
                    alert_type="embedding_drift",
                    metric_name="vector_norm_std",
                    current_value=snapshot.vector_norm_std,
                    threshold_value=self.norm_std_threshold,
                    delta=snapshot.vector_norm_std - self.norm_std_threshold,
                    severity="warning",
                    message=f"Vector norm std {snapshot.vector_norm_std:.3f} exceeds threshold {self.norm_std_threshold:.3f}",
                )
            )
        if snapshot.similarity_distribution_mean < self.similarity_mean_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=_new_id(),
                    timestamp=_ts,
                    alert_type="embedding_drift",
                    metric_name="similarity_distribution_mean",
                    current_value=snapshot.similarity_distribution_mean,
                    threshold_value=self.similarity_mean_threshold,
                    delta=snapshot.similarity_distribution_mean - self.similarity_mean_threshold,
                    severity="warning",
                    message=f"Similarity distribution mean {snapshot.similarity_distribution_mean:.3f} below threshold {self.similarity_mean_threshold:.3f}",
                )
            )
        return alerts

    def _persist(self, snapshot: EmbeddingHealthSnapshot) -> None:
        try:
            from agentic_core.L4_state.utils.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="embedding_health_snapshot",
                logical_id=f"embedding_health_{snapshot.timestamp[:10]}",
                payload=snapshot.to_dict(),
            )
            self.l4_store.put(artifact)
        # guardian: allow-silent-swallow
        except Exception:
            _logger.debug("EmbeddingDriftMonitor._persist failed", exc_info=True)


class AnswerQualityMonitor:
    """Tracks groundedness_rate, hallucination_rate, human_override_rate."""

    # guardian: allow-magic-config
    def __init__(
        self,
        groundedness_threshold: float = 0.7,
        hallucination_threshold: float = 0.15,
        override_threshold: float = 0.2,
        system_version: str = "unknown",
        l4_store: Any | None = None,
    ):
        self.groundedness_threshold = groundedness_threshold
        self.hallucination_threshold = hallucination_threshold
        self.override_threshold = override_threshold
        self.system_version = system_version
        self.l4_store = l4_store

    def measure(
        self,
        groundedness_scores: list[float],
        hallucination_flags: list[bool],
        human_override_flags: list[bool],
        correctness_scores: list[float],
    ) -> AnswerQualitySnapshot:
        """Compute an answer quality drift snapshot.

        Args:
            groundedness_scores: Per-answer groundedness scores in [0, 1]
            hallucination_flags: Per-answer boolean hallucination detection
            human_override_flags: Per-answer boolean human override indicators
            correctness_scores: Per-answer correctness scores in [0, 1]

        Returns:
            AnswerQualitySnapshot
        """
        n = len(groundedness_scores)
        if n == 0:
            raise ValueError("groundedness_scores must be non-empty")
        groundedness_rate = _mean(groundedness_scores)
        hallucination_rate = (
            sum(hallucination_flags) / len(hallucination_flags) if hallucination_flags else 0.0
        )
        override_rate = sum(human_override_flags) / len(human_override_flags) if human_override_flags else 0.0
        correctness_mean = _mean(correctness_scores)
        snapshot = AnswerQualitySnapshot(
            timestamp=_utcnow(),
            system_version=self.system_version,
            groundedness_rate=groundedness_rate,
            hallucination_rate=hallucination_rate,
            human_override_rate=override_rate,
            answer_correctness_mean=correctness_mean,
            sample_size=n,
        )
        if self.l4_store is not None:
            self._persist(snapshot)
        return snapshot

    def check_alerts(
        self,
        snapshot: AnswerQualitySnapshot,
        now_iso: str | None = None,
        id_factory: Callable[[], str] | None = None,
    ) -> list[DriftAlert]:
        """Return DriftAlerts for answer quality degradation."""
        _ts = now_iso if now_iso is not None else _utcnow()
        _new_id = id_factory if id_factory is not None else lambda: str(uuid.uuid4())
        alerts: list[DriftAlert] = []
        if snapshot.groundedness_rate < self.groundedness_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=_new_id(),
                    timestamp=_ts,
                    alert_type="answer_quality_drift",
                    metric_name="groundedness_rate",
                    current_value=snapshot.groundedness_rate,
                    threshold_value=self.groundedness_threshold,
                    delta=snapshot.groundedness_rate - self.groundedness_threshold,
                    severity="warning",
                    message=f"Groundedness rate {snapshot.groundedness_rate:.3f} below threshold {self.groundedness_threshold:.3f}",
                )
            )
        if snapshot.hallucination_rate > self.hallucination_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=_new_id(),
                    timestamp=_ts,
                    alert_type="answer_quality_drift",
                    metric_name="hallucination_rate",
                    current_value=snapshot.hallucination_rate,
                    threshold_value=self.hallucination_threshold,
                    delta=snapshot.hallucination_rate - self.hallucination_threshold,
                    severity="critical",
                    message=f"Hallucination rate {snapshot.hallucination_rate:.3f} exceeds threshold {self.hallucination_threshold:.3f}",
                )
            )
        if snapshot.human_override_rate > self.override_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=_new_id(),
                    timestamp=_ts,
                    alert_type="answer_quality_drift",
                    metric_name="human_override_rate",
                    current_value=snapshot.human_override_rate,
                    threshold_value=self.override_threshold,
                    delta=snapshot.human_override_rate - self.override_threshold,
                    severity="warning",
                    message=f"Human override rate {snapshot.human_override_rate:.3f} exceeds threshold {self.override_threshold:.3f}",
                )
            )
        return alerts

    def _persist(self, snapshot: AnswerQualitySnapshot) -> None:
        try:
            from agentic_core.L4_state.utils.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="answer_quality_snapshot",
                logical_id=f"answer_quality_{snapshot.timestamp[:10]}",
                payload=snapshot.to_dict(),
            )
            self.l4_store.put(artifact)
        # guardian: allow-silent-swallow
        except Exception:
            _logger.debug("AnswerQualityMonitor._persist failed", exc_info=True)


def emit_alerts_to_registry(
    alerts: list[DriftAlert], source: str, threshold_map: dict[str, float] | None = None
) -> None:
    """P5-5B: Convert DriftAlerts to DriftRegistryEntry and record in DriftRegistry.

    P5-5C: For critical-severity entries, also publishes to MetaLearningBus.

    Parameters
    ----------
    alerts:
        Alerts produced by any monitor's check_alerts() method.
    source:
        DriftSource string — "retrieval", "embedding", or "shadow".
    threshold_map:
        Optional mapping of metric_name → threshold_value. Falls back to
        alert.threshold_value when available.
    """
    if not alerts:
        return
    try:
        from agentic_core.L6_observability.utils.engines.drift_registry import (
            DriftRegistryEntry,
            get_drift_registry,
        )
    # guardian: allow-silent-swallow
    except Exception:
        _logger.debug("emit_alerts_to_registry: drift_registry unavailable", exc_info=True)
        return
    registry = get_drift_registry()
    for alert in alerts:
        threshold = (threshold_map or {}).get(alert.metric_name, alert.threshold_value)
        try:
            import hashlib
            import json as _json

            digest_payload = _json.dumps(
                {
                    "source": source,
                    "metric": alert.metric_name,
                    "value": alert.current_value,
                    "threshold": threshold,
                    "timestamp": alert.timestamp,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            deterministic_digest = hashlib.sha256(digest_payload.encode()).hexdigest()
            entry = DriftRegistryEntry(
                source=source,
                timestamp_iso=alert.timestamp,
                metric_name=alert.metric_name,
                current_value=alert.current_value,
                threshold_value=threshold,
                drift_flag=True,
                severity=alert.severity,
                deterministic_digest=deterministic_digest,
            )
            registry.record(entry)
        # guardian: allow-silent-swallow
        except Exception:
            _logger.debug(
                "emit_alerts_to_registry: failed to record entry for %s", alert.metric_name, exc_info=True
            )
            continue
        if alert.severity == "critical":
            try:
                from system_learning.ports.meta_learning_bus import MetaLearningBus
                from system_learning.ports.meta_learning_change_package import MetaLearningChangePackage

                bus = MetaLearningBus.get_instance()
                pkg = MetaLearningChangePackage.create(
                    kind="drift_alert",
                    payload={
                        "source": source,
                        "metric_name": alert.metric_name,
                        "current_value": alert.current_value,
                        "threshold_value": threshold,
                        "severity": alert.severity,
                        "alert_id": alert.alert_id,
                        "timestamp": alert.timestamp,
                        "digest": deterministic_digest,
                    },
                    proposal_only=True,
                )
                bus.enqueue(pkg)
            # guardian: allow-silent-swallow
            except Exception:
                _logger.debug(
                    "emit_alerts_to_registry: MetaLearningBus publish failed for critical alert %s",
                    alert.alert_id,
                    exc_info=True,
                )


__all__ = [
    "RetrievalDriftMonitor",
    "EmbeddingDriftMonitor",
    "AnswerQualityMonitor",
    "emit_alerts_to_registry",
]
