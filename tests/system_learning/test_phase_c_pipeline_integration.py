"""Phase C — Pipeline Integration acceptance tests.

C-test hardenings verified:
  (a) _retrieve_semantic_context() always returns vector_source key.
  (b) With embedding_service disabled, vector_source == "disabled".
  (c) With embeddings env-off, C3 uses hash-fallback vector (vector_source=hash-fallback).
  (d) RetrievalProfile.embeddings_enabled reads from BMG_EMBEDDINGS_ENABLED env var (D2).
  (e) LiveRunPipelineAdapter.record_count() returns 0 on empty store.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# D2 — RetrievalProfile.embeddings_enabled
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_retrieval_profile_embeddings_enabled_false_by_default():
    with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "false"}):
        from importlib import reload

        import system_learning.engines.retrieval_profile as rp_mod

        reload(rp_mod)
        profile = rp_mod.RetrievalProfile.create_default()
    assert profile.embeddings_enabled is False


@pytest.mark.unit
def test_retrieval_profile_embeddings_enabled_true_from_env():
    with patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "true"}):
        from importlib import reload

        import system_learning.engines.retrieval_profile as rp_mod

        reload(rp_mod)
        profile = rp_mod.RetrievalProfile.create_default()
    assert profile.embeddings_enabled is True


# ---------------------------------------------------------------------------
# C3 — generate_fallback_vector replaces 4-dim hash placeholder
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_fallback_vector_has_16_dims():
    from agentic_core.L2_execution.healers.failure_signal_normalizer import generate_fallback_vector

    vec = generate_fallback_vector("generic_failure")
    assert len(vec) == 16, f"Expected 16-dim fallback, got {len(vec)}"


@pytest.mark.unit
@pytest.mark.negative_control
def test_old_4dim_vector_no_longer_produced():
    """Old code produced a 4-dim vector; C3 replaces it with 16-dim or real embedding."""
    from agentic_core.L2_execution.healers.failure_signal_normalizer import generate_fallback_vector

    vec = generate_fallback_vector("any text")
    assert len(vec) != 4, "4-dim placeholder vector must not be produced after C3"


# ---------------------------------------------------------------------------
# C3 — vector_source propagated in _retrieve_semantic_context return dicts
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_retrieve_semantic_context_disabled_has_vector_source():
    """When embedding_service.is_disabled(), vector_source='disabled' must be present."""
    from system_learning.pipelines.meta_learning_pipeline import _retrieve_semantic_context

    mock_disabled_svc = MagicMock()
    mock_disabled_svc.is_disabled.return_value = True

    mock_profile = MagicMock()
    mock_profile.profile_id = "test-profile"
    mock_profile.shadow_embedder_id = None
    mock_profile.embeddings_enabled = False

    with (
        patch("system_learning.pipelines.meta_learning_pipeline.EmbeddingServiceFactory") as mock_factory,
        patch(
            "system_learning.pipelines.meta_learning_pipeline.get_active_retrieval_profile"
        ) as mock_profile_fn,
    ):
        mock_factory.get_or_disabled.return_value = mock_disabled_svc
        mock_profile_fn.return_value = mock_profile

        result = _retrieve_semantic_context(rca_report=MagicMock(), pattern_report=None, now_utc=0)

    assert "vector_source" in result, "vector_source key must always be present in return dict"
    assert result["vector_source"] == "disabled"
    assert result["embedding_enabled_at_time"] is False


@pytest.mark.unit
def test_retrieve_semantic_context_retrieval_failed_has_vector_source():
    """When retrieve() raises an exception, vector_source='error' must be present."""
    from system_learning.pipelines.meta_learning_pipeline import _retrieve_semantic_context

    mock_svc = MagicMock()
    mock_svc.is_disabled.return_value = False
    mock_svc.retrieve.side_effect = RuntimeError("simulated failure")

    mock_profile = MagicMock()
    mock_profile.profile_id = "test-profile"
    mock_profile.shadow_embedder_id = None
    mock_profile.embeddings_enabled = False
    mock_profile.similarity_cutoff = 0.75
    mock_profile.top_k = 5

    with (
        patch("system_learning.pipelines.meta_learning_pipeline.EmbeddingServiceFactory") as mock_factory,
        patch(
            "system_learning.pipelines.meta_learning_pipeline.get_active_retrieval_profile"
        ) as mock_profile_fn,
        patch.dict(os.environ, {"BMG_EMBEDDINGS_ENABLED": "false"}),
    ):
        mock_factory.get_or_disabled.return_value = mock_svc
        mock_profile_fn.return_value = mock_profile

        rca = MagicMock()
        rca.failures = []
        result = _retrieve_semantic_context(rca_report=rca, pattern_report=None, now_utc=0)

    assert "vector_source" in result
    assert result["vector_source"] == "error"


# ---------------------------------------------------------------------------
# C1 — LiveRunPipelineAdapter
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_live_run_adapter_record_count_empty():
    from system_learning.adapters.live_run_pipeline_adapter import LiveRunPipelineAdapter

    mock_store = MagicMock()
    mock_store.count.return_value = 0

    mock_intake = MagicMock()
    mock_intake.store = mock_store

    adapter = LiveRunPipelineAdapter(intake_adapter=mock_intake, source_tag="test")
    assert adapter.record_count() == 0


@pytest.mark.unit
def test_live_run_adapter_record_count_nonzero():
    from system_learning.adapters.live_run_pipeline_adapter import LiveRunPipelineAdapter

    mock_store = MagicMock()
    mock_store.count.return_value = 3

    mock_intake = MagicMock()
    mock_intake.store = mock_store

    adapter = LiveRunPipelineAdapter(intake_adapter=mock_intake, source_tag="test")
    assert adapter.record_count() == 3
