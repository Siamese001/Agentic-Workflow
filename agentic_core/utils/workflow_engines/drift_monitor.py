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

_logger = logging.getLogger(__name__)

from .snapshots import (
    AnswerQualitySnapshot,
    DriftAlert,
    EmbeddingHealthSnapshot,
    RetrievalDriftSnapshot,
)


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

    def __init__(
        self,
        hit_rate_threshold: float = 0.70,
        score_std_threshold: float = 0.20,
        stability_threshold: float = 0.60,
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
        n = len(queries)
        if n == 0:
            raise ValueError("queries must be non-empty")

        hits = sum(1 for ret, gt in zip(retrieved_doc_ids, ground_truth_doc_ids) if set(ret) & set(gt))
        hit_rate = hits / n

        all_scores = [s for query_scores in scores for s in query_scores]
        score_mean = _mean(all_scores)
        score_std = _std(all_scores)

        top1_docs = [ret[0] if ret else "" for ret in retrieved_doc_ids]
        unique_top1 = len(set(top1_docs))
        top_k_stability = 1.0 - (unique_top1 / n) if n > 1 else 1.0

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
                    message=(
                        f"Retrieval hit rate {snapshot.retrieval_hit_rate:.3f} "
                        f"below threshold {self.hit_rate_threshold:.3f}"
                    ),
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
                    message=(
                        f"Score distribution std {snapshot.score_distribution_std:.3f} "
                        f"exceeds threshold {self.score_std_threshold:.3f}"
                    ),
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
                    message=(
                        f"Top-k stability {snapshot.top_k_stability:.3f} "
                        f"below threshold {self.stability_threshold:.3f}"
                    ),
                )
            )

        return alerts

    def _persist(self, snapshot: RetrievalDriftSnapshot) -> None:
        try:
            from agentic_core.L4_state.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="retrieval_drift_snapshot",
                logical_id=f"retrieval_drift_{snapshot.timestamp[:10]}",
                payload=snapshot.to_dict(),
            )
            self.l4_store.put(artifact)
        except Exception:  # guardian: allow-silent-swallow
            _logger.debug("RetrievalDriftMonitor._persist failed", exc_info=True)


class EmbeddingDriftMonitor:
    """Tracks vector_norm_distribution, similarity_distribution, version mismatch."""

    def __init__(
        self,
        norm_std_threshold: float = 0.15,
        similarity_mean_threshold: float = 0.50,
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

    def check_alerts(self, snapshot: EmbeddingHealthSnapshot) -> list[DriftAlert]:
        """Return DriftAlerts for detected embedding health issues."""
        alerts: list[DriftAlert] = []

        if snapshot.version_mismatch_detected:
            alerts.append(
                DriftAlert(
                    alert_id=str(uuid.uuid4()),
                    timestamp=_utcnow(),
                    alert_type="embedding_drift",
                    metric_name="embedding_model_version",
                    current_value=0.0,
                    threshold_value=0.0,
                    delta=0.0,
                    severity="critical",
                    message=(
                        f"Embedding model version mismatch: "
                        f"expected {self.current_model_version!r}, "
                        f"got {snapshot.embedding_model_version!r}"
                    ),
                )
            )

        if snapshot.vector_norm_std > self.norm_std_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=str(uuid.uuid4()),
                    timestamp=_utcnow(),
                    alert_type="embedding_drift",
                    metric_name="vector_norm_std",
                    current_value=snapshot.vector_norm_std,
                    threshold_value=self.norm_std_threshold,
                    delta=snapshot.vector_norm_std - self.norm_std_threshold,
                    severity="warning",
                    message=(
                        f"Vector norm std {snapshot.vector_norm_std:.3f} "
                        f"exceeds threshold {self.norm_std_threshold:.3f}"
                    ),
                )
            )

        if snapshot.similarity_distribution_mean < self.similarity_mean_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=str(uuid.uuid4()),
                    timestamp=_utcnow(),
                    alert_type="embedding_drift",
                    metric_name="similarity_distribution_mean",
                    current_value=snapshot.similarity_distribution_mean,
                    threshold_value=self.similarity_mean_threshold,
                    delta=snapshot.similarity_distribution_mean - self.similarity_mean_threshold,
                    severity="warning",
                    message=(
                        f"Similarity distribution mean {snapshot.similarity_distribution_mean:.3f} "
                        f"below threshold {self.similarity_mean_threshold:.3f}"
                    ),
                )
            )

        return alerts

    def _persist(self, snapshot: EmbeddingHealthSnapshot) -> None:
        try:
            from agentic_core.L4_state.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="embedding_health_snapshot",
                logical_id=f"embedding_health_{snapshot.timestamp[:10]}",
                payload=snapshot.to_dict(),
            )
            self.l4_store.put(artifact)
        except Exception:  # guardian: allow-silent-swallow
            _logger.debug("EmbeddingDriftMonitor._persist failed", exc_info=True)


class AnswerQualityMonitor:
    """Tracks groundedness_rate, hallucination_rate, human_override_rate."""

    def __init__(
        self,
        groundedness_threshold: float = 0.70,
        hallucination_threshold: float = 0.15,
        override_threshold: float = 0.20,
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

    def check_alerts(self, snapshot: AnswerQualitySnapshot) -> list[DriftAlert]:
        """Return DriftAlerts for answer quality degradation."""
        alerts: list[DriftAlert] = []

        if snapshot.groundedness_rate < self.groundedness_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=str(uuid.uuid4()),
                    timestamp=_utcnow(),
                    alert_type="answer_quality_drift",
                    metric_name="groundedness_rate",
                    current_value=snapshot.groundedness_rate,
                    threshold_value=self.groundedness_threshold,
                    delta=snapshot.groundedness_rate - self.groundedness_threshold,
                    severity="warning",
                    message=(
                        f"Groundedness rate {snapshot.groundedness_rate:.3f} "
                        f"below threshold {self.groundedness_threshold:.3f}"
                    ),
                )
            )

        if snapshot.hallucination_rate > self.hallucination_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=str(uuid.uuid4()),
                    timestamp=_utcnow(),
                    alert_type="answer_quality_drift",
                    metric_name="hallucination_rate",
                    current_value=snapshot.hallucination_rate,
                    threshold_value=self.hallucination_threshold,
                    delta=snapshot.hallucination_rate - self.hallucination_threshold,
                    severity="critical",
                    message=(
                        f"Hallucination rate {snapshot.hallucination_rate:.3f} "
                        f"exceeds threshold {self.hallucination_threshold:.3f}"
                    ),
                )
            )

        if snapshot.human_override_rate > self.override_threshold:
            alerts.append(
                DriftAlert(
                    alert_id=str(uuid.uuid4()),
                    timestamp=_utcnow(),
                    alert_type="answer_quality_drift",
                    metric_name="human_override_rate",
                    current_value=snapshot.human_override_rate,
                    threshold_value=self.override_threshold,
                    delta=snapshot.human_override_rate - self.override_threshold,
                    severity="warning",
                    message=(
                        f"Human override rate {snapshot.human_override_rate:.3f} "
                        f"exceeds threshold {self.override_threshold:.3f}"
                    ),
                )
            )

        return alerts

    def _persist(self, snapshot: AnswerQualitySnapshot) -> None:
        try:
            from agentic_core.L4_state.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="answer_quality_snapshot",
                logical_id=f"answer_quality_{snapshot.timestamp[:10]}",
                payload=snapshot.to_dict(),
            )
            self.l4_store.put(artifact)
        except Exception:  # guardian: allow-silent-swallow
            _logger.debug("AnswerQualityMonitor._persist failed", exc_info=True)


__all__ = [
    "RetrievalDriftMonitor",
    "EmbeddingDriftMonitor",
    "AnswerQualityMonitor",
]
