"""Tests for agentic_core/utils/workflow_engines/drift_monitor.py hardening changes."""

from __future__ import annotations


def test_retrieval_monitor_persist_none_store_returns_silently():
    """RetrievalDriftMonitor._persist with l4_store=None returns without error."""
    from agentic_core.utils.workflow_engines.drift_monitor import RetrievalDriftMonitor
    from agentic_core.utils.workflow_engines.snapshots import RetrievalDriftSnapshot

    monitor = RetrievalDriftMonitor(l4_store=None)
    snapshot = RetrievalDriftSnapshot(
        timestamp="2024-01-01T00:00:00Z",
        system_version="test",
        retrieval_hit_rate=0.9,
        score_distribution_mean=0.75,
        score_distribution_std=0.1,
        top_k_stability=0.8,
        sample_size=10,
    )
    monitor._persist(snapshot)  # must not raise


def test_embedding_monitor_persist_none_store_returns_silently():
    """EmbeddingDriftMonitor._persist with l4_store=None returns without error."""
    from agentic_core.utils.workflow_engines.drift_monitor import EmbeddingDriftMonitor
    from agentic_core.utils.workflow_engines.snapshots import EmbeddingHealthSnapshot

    monitor = EmbeddingDriftMonitor(l4_store=None)
    snapshot = EmbeddingHealthSnapshot(
        timestamp="2024-01-01T00:00:00Z",
        embedding_model_version="v1",
        vector_norm_mean=1.0,
        vector_norm_std=0.05,
        similarity_distribution_mean=0.8,
        similarity_distribution_std=0.1,
        version_mismatch_detected=False,
        sample_size=10,
    )
    monitor._persist(snapshot)  # must not raise


def test_answer_quality_monitor_persist_none_store_returns_silently():
    """AnswerQualityMonitor._persist with l4_store=None returns without error."""
    from agentic_core.utils.workflow_engines.drift_monitor import AnswerQualityMonitor
    from agentic_core.utils.workflow_engines.snapshots import AnswerQualitySnapshot

    monitor = AnswerQualityMonitor(l4_store=None)
    snapshot = AnswerQualitySnapshot(
        timestamp="2024-01-01T00:00:00Z",
        system_version="test",
        groundedness_rate=0.9,
        hallucination_rate=0.05,
        human_override_rate=0.1,
        answer_correctness_mean=0.85,
        sample_size=10,
    )
    monitor._persist(snapshot)  # must not raise


def test_emit_alerts_to_registry_empty_alerts_returns_silently():
    """emit_alerts_to_registry with empty alerts list returns without error."""
    from agentic_core.utils.workflow_engines.drift_monitor import emit_alerts_to_registry

    emit_alerts_to_registry([], source="retrieval")  # must not raise
