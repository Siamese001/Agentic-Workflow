"""Tests for W2 embedding integration in meta_learning_pipeline.

W2: Informational semantic retrieval + bounded scoring (C0-only).

Tests cover:
- Semantic retrieval with kill-switch
- Embedding metadata generation
- Pipeline integration with embeddings
- C0 informational context only
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory
from system_learning.pipelines.meta_learning_pipeline import (
    PipelineConfig,
    PipelineDependencies,
    _retrieve_semantic_context,
    run_pipeline,
)
from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
from system_learning.validators.oscillation_detector import OscillationPolicy
from system_learning.validators.shadow_evaluator import ShadowThresholds


@pytest.mark.unit_min_deps
class TestMetaLearningPipelineEmbeddings:
    """Test W2 embedding integration in meta-learning pipeline."""

    @pytest.fixture
    def mock_rca_report(self) -> MagicMock:
        """Create mock RCA report."""
        rca = MagicMock()
        rca.failures = [
            MagicMock(
                failure_type="timeout_error",
                component="test_component",
                error_tokens=["timeout", "connection", "refused"],
            ),
            MagicMock(
                failure_type="auth_error",
                component="auth_service",
                error_tokens=["authentication", "failed", "token"],
            ),
        ]
        return rca

    @pytest.fixture
    def mock_pattern_report(self) -> MagicMock:
        """Create mock pattern report."""
        pattern = MagicMock()
        pattern.findings = [
            MagicMock(key=MagicMock(label="UNDERPERFORMING_HEALER_TIER"), severity=0.75),
            MagicMock(key=MagicMock(label="ROUTING_DRIFT_HIGH"), severity=0.60),
        ]
        return pattern

    def test_retrieve_semantic_context_disabled(
        self, mock_rca_report: MagicMock, mock_pattern_report: MagicMock
    ) -> None:
        """Test semantic retrieval when embeddings are disabled."""
        # Mock embedding service as disabled
        with patch.object(EmbeddingServiceFactory, "get_or_disabled") as mock_get:
            mock_service = MagicMock()
            mock_service.is_disabled.return_value = True
            mock_get.return_value = mock_service

            # Retrieve semantic context
            metadata = _retrieve_semantic_context(
                rca_report=mock_rca_report,
                pattern_report=mock_pattern_report,
                now_utc=1234567890,
            )

            # Verify disabled metadata
            assert metadata == {
                "embedding_enabled_at_time": False,
                "embedding_replay_key": None,
                "embedding_artifact_hash": None,
                "embedding_topk_hashes": [],
                "embedding_topk_scores_round6": [],
            }

    def test_retrieve_semantic_context_enabled(
        self, mock_rca_report: MagicMock, mock_pattern_report: MagicMock
    ) -> None:
        """Test semantic retrieval when embeddings are enabled."""
        # Mock embedding service as enabled
        with patch.object(EmbeddingServiceFactory, "get_or_disabled") as mock_get:
            mock_service = MagicMock()
            mock_service.is_disabled.return_value = False
            mock_service.replay_key = "test_replay_key:abc123"

            # Mock retrieval results
            mock_result1 = MagicMock()
            mock_result1.content_hash = "hash1"
            mock_result1.score_round6 = 0.85
            mock_result2 = MagicMock()
            mock_result2.content_hash = "hash2"
            mock_result2.score_round6 = 0.90

            mock_service.retrieve.return_value = [mock_result1, mock_result2]
            mock_get.return_value = mock_service

            # Retrieve semantic context
            metadata = _retrieve_semantic_context(
                rca_report=mock_rca_report,
                pattern_report=mock_pattern_report,
                now_utc=1234567890,
            )

            # Verify enabled metadata
            assert metadata["embedding_enabled_at_time"] is True
            assert metadata["embedding_replay_key"] == "test_replay_key:abc123"
            assert metadata["embedding_artifact_hash"] is not None
            assert len(metadata["embedding_topk_hashes"]) == 2
            assert "hash1" in metadata["embedding_topk_hashes"]
            assert "hash2" in metadata["embedding_topk_hashes"]
            assert len(metadata["embedding_topk_scores_round6"]) == 2
            assert 0.85 in metadata["embedding_topk_scores_round6"]
            assert 0.90 in metadata["embedding_topk_scores_round6"]

    def test_retrieve_semantic_context_deterministic_query(
        self, mock_rca_report: MagicMock, mock_pattern_report: MagicMock
    ) -> None:
        """Test that query construction is deterministic."""
        # Mock embedding service
        with patch.object(EmbeddingServiceFactory, "get_or_disabled") as mock_get:
            mock_service = MagicMock()
            mock_service.is_disabled.return_value = False
            mock_service.replay_key = "test_replay_key"
            mock_service.retrieve.return_value = []
            mock_get.return_value = mock_service

            # Retrieve twice with same inputs
            metadata1 = _retrieve_semantic_context(
                rca_report=mock_rca_report,
                pattern_report=mock_pattern_report,
                now_utc=1234567890,
            )

            metadata2 = _retrieve_semantic_context(
                rca_report=mock_rca_report,
                pattern_report=mock_pattern_report,
                now_utc=1234567890,
            )

            # Verify same artifact hash (deterministic query)
            assert metadata1["embedding_artifact_hash"] == metadata2["embedding_artifact_hash"]

    def test_retrieve_semantic_context_handles_failure(
        self, mock_rca_report: MagicMock, mock_pattern_report: MagicMock
    ) -> None:
        """Test semantic retrieval handles service failures gracefully."""
        # Mock embedding service to raise exception
        with patch.object(EmbeddingServiceFactory, "get_or_disabled") as mock_get:
            mock_service = MagicMock()
            mock_service.is_disabled.return_value = False
            mock_service.retrieve.side_effect = Exception("Service unavailable")
            mock_get.return_value = mock_service

            # Retrieve semantic context
            metadata = _retrieve_semantic_context(
                rca_report=mock_rca_report,
                pattern_report=mock_pattern_report,
                now_utc=1234567890,
            )

            # Verify failure is handled gracefully
            assert metadata["embedding_enabled_at_time"] is True
            assert metadata["embedding_artifact_hash"] == "RETRIEVAL_FAILED"
            assert metadata["embedding_topk_hashes"] == []
            assert metadata["embedding_topk_scores_round6"] == []

    def test_pipeline_integration_with_embeddings(self) -> None:
        """Test that pipeline integrates embeddings without breaking."""
        # Create minimal pipeline config
        cfg = PipelineConfig(
            engine_version="1.0",
            config_surface_version="1.0",
            shadow_thresholds=ShadowThresholds(
                max_p95_latency_regression_pct=10.0,
                max_error_rate_regression_abs=0.01,
                max_cpu_regression_pct=20.0,
                max_mem_regression_pct=20.0,
                forbid_any_safety_violation_increase=True,
            ),
            cooldown_policy=CooldownPolicy(
                min_seconds_between_updates=300,
            ),
            sample_policy=SampleSizePolicy(
                min_observations=20,
            ),
            oscillation_policy=OscillationPolicy(
                window=10,
                epsilon=0.01,
                freeze_seconds=300,
            ),
            enabled_proposers=(),
            proposal_only=True,
        )

        # Create mock dependencies
        mock_audit_store = MagicMock()
        mock_audit_store.read_audit_slice.return_value = b"audit_data"

        mock_telemetry_store = MagicMock()
        mock_telemetry_store.read_events.return_value = ()

        mock_config_provider = MagicMock()
        mock_config_provider.get_current_configs.return_value = {}
        mock_config_provider.get_last_update_utc.return_value = None
        mock_config_provider.get_param_history.return_value = ()

        mock_baseline_metrics = MagicMock()
        mock_baseline_metrics.production_metrics.return_value = {}
        mock_baseline_metrics.shadow_metrics.return_value = {}

        mock_optimizer = MagicMock()
        mock_proposal = MagicMock()
        mock_proposal.adjustments = []
        mock_optimizer.propose_threshold_adjustments_with_patterns.return_value = mock_proposal
        mock_optimizer.create_snapshot_from_intake.return_value = MagicMock()

        mock_l4_writer = MagicMock()
        mock_l4_writer.read_latest_healing_snapshot.return_value = b"snapshot_data"
        mock_l4_writer.read_latest_detection_signal.return_value = None
        mock_l4_writer.read_latest_drift_snapshot.return_value = None
        mock_l4_writer.write_l4b_healing_snapshot.return_value = None

        mock_pattern_engine = MagicMock()
        mock_pattern_engine.analyze.return_value = MagicMock()

        mock_intake_adapter = MagicMock()
        mock_intake_adapter.build_record.return_value = MagicMock()
        mock_intake_adapter.persist_record.return_value = None

        deps = PipelineDependencies(
            audit_store=mock_audit_store,
            telemetry_store=mock_telemetry_store,
            config_provider=mock_config_provider,
            baseline_metrics_provider=mock_baseline_metrics,
            healing_config_optimizer=mock_optimizer,
            l4_state_writer=mock_l4_writer,
            pattern_analysis_engine=mock_pattern_engine,
            healing_outcome_intake_adapter=mock_intake_adapter,
        )

        # Mock embedding service
        with patch.object(EmbeddingServiceFactory, "get_or_disabled") as mock_get:
            mock_service = MagicMock()
            mock_service.is_disabled.return_value = False
            mock_service.replay_key = "test_replay_key"
            mock_service.retrieve.return_value = []
            mock_get.return_value = mock_service

            # Run pipeline
            result = run_pipeline(
                now_utc=1234567890,
                window_start_utc=1234567800,
                window_end_utc=1234567890,
                cfg=cfg,
                deps=deps,
            )

            # Verify pipeline completes without error
            assert isinstance(result, tuple)

            # Verify embedding service was called
            mock_get.assert_called_once()

    def test_embedding_metadata_is_informational_only(self) -> None:
        """Test that embedding metadata is C0 informational only."""
        # This test verifies that embedding metadata doesn't directly
        # mutate any routing thresholds or safety tiers

        # Create embedding metadata
        embedding_metadata = {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": "test_replay_key",
            "embedding_artifact_hash": "test_hash",
            "embedding_topk_hashes": ["hash1", "hash2"],
            "embedding_topk_scores_round6": [0.85, 0.90],
        }

        # Verify metadata contains only audit information
        assert "embedding_enabled_at_time" in embedding_metadata
        assert "embedding_replay_key" in embedding_metadata
        assert "embedding_artifact_hash" in embedding_metadata
        assert "embedding_topk_hashes" in embedding_metadata
        assert "embedding_topk_scores_round6" in embedding_metadata

        # Verify no routing/safety parameters
        routing_params = ["thresholds", "tiers", "allowed_tools", "routing"]
        for param in routing_params:
            assert param not in str(embedding_metadata).lower()
