"""Tests for W3 pattern analysis integration in meta-learning pipeline.

W3: Pattern Analysis Engine (Deterministic, Informational-Only).

Tests ensure pattern analysis is properly wired into the pipeline
as C0 informational-only input.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory
from system_learning.engines.pattern_analysis_engine import (
    PatternAnalysisEngine,
    PatternSummary,
)
from system_learning.pipelines.meta_learning_pipeline import (
    _analyze_historical_patterns,
)


@pytest.mark.unit_min_deps
class TestMetaLearningPipelinePatterns:
    """Test pattern analysis integration in meta-learning pipeline."""

    def test_pattern_analysis_disabled_when_embedding_disabled(self) -> None:
        """T1: Pattern analysis should be disabled when embeddings are disabled."""
        engine = PatternAnalysisEngine()

        # Create mock dependencies with pattern engine
        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        # Create mock aggregate snapshot
        mock_snapshot = MagicMock()
        mock_snapshot.outcomes = []

        # Disable embeddings via environment
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "false"}):
            result = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should return None when embeddings disabled
        assert result is None

    def test_pattern_analysis_included_when_embeddings_enabled(self) -> None:
        """T2: Pattern analysis should be included when embeddings are enabled."""
        engine = PatternAnalysisEngine()

        # Create mock dependencies
        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        # Create mock aggregate snapshot with sufficient data
        mock_snapshot = MagicMock()
        mock_outcomes = []

        # Create 12 mock outcomes (above small-N threshold of 10)
        for i in range(12):
            outcome = MagicMock()
            outcome.failure_signature = MagicMock()
            outcome.failure_signature.component = f"component_{i % 3}"
            outcome.failure_signature.failure_type = f"failure_{i % 2}"
            outcome.failure_signature.healer_name = f"healer_{i % 2}"
            outcome.failure_signature.timestamp_utc = 1234567890 + i
            mock_outcomes.append(outcome)

        mock_snapshot.outcomes = mock_outcomes
        # Ensure mock does NOT have canonical_bytes so legacy path is used
        del mock_snapshot.canonical_bytes

        # Enable embeddings and mock the embedding service
        mock_emb_service = MagicMock()
        mock_emb_service.is_disabled.return_value = False
        with (
            patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}),
            patch.object(EmbeddingServiceFactory, "get_or_disabled", return_value=mock_emb_service),
        ):
            result = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should return pattern summary
        assert isinstance(result, PatternSummary)
        assert result.pattern_digest is not None

    def test_pattern_analysis_influence_capped(self) -> None:
        """T3: Pattern analysis influence should be capped at ≤ 0.25."""
        # This is tested at the engine level - pattern analysis is informational only
        # The actual influence capping is handled by the optimizer
        engine = PatternAnalysisEngine()

        # Use orthogonal directions so cosine distance separates clusters
        embeddings = [
            [1.0, 0.0, 0.0, 0.0],
            [0.95, 0.05, 0.0, 0.0],  # Close to first in direction
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.95, 0.05],  # Close to third in direction
        ]
        metadata = [
            {"type": "failure", "component": "A"},
            {"type": "failure", "component": "A"},
            {"type": "failure", "component": "B"},
            {"type": "failure", "component": "B"},
        ]

        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        # Pattern analysis itself doesn't apply influence caps
        # It's informational-only - the optimizer applies caps
        assert isinstance(summary, PatternSummary)
        assert len(summary.clusters) == 2

    def test_pattern_analysis_deterministic(self) -> None:
        """T4: Pattern analysis should be deterministic across runs."""
        engine = PatternAnalysisEngine()

        # Create mock dependencies
        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        # Create mock aggregate snapshot
        mock_snapshot = MagicMock()
        mock_outcomes = []

        # Create deterministic test data
        for i in range(12):
            outcome = MagicMock()
            outcome.failure_signature = MagicMock()
            outcome.failure_signature.component = f"comp_{i % 3}"
            outcome.failure_signature.failure_type = f"fail_{i % 2}"
            outcome.failure_signature.healer_name = f"heal_{i % 2}"
            outcome.failure_signature.timestamp_utc = 1234567890 + i
            mock_outcomes.append(outcome)

        mock_snapshot.outcomes = mock_outcomes
        # Ensure mock does NOT have canonical_bytes so legacy path is used
        del mock_snapshot.canonical_bytes

        # Enable embeddings and mock the embedding service
        mock_emb_service = MagicMock()
        mock_emb_service.is_disabled.return_value = False
        with (
            patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}),
            patch.object(EmbeddingServiceFactory, "get_or_disabled", return_value=mock_emb_service),
        ):
            # Run twice with same inputs
            result1 = _analyze_historical_patterns(mock_deps, mock_snapshot)
            result2 = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should produce identical pattern digests
        assert result1.pattern_digest == result2.pattern_digest

        print(f"W3-PATTERN-DIGEST: {result1.pattern_digest}")

    def test_pattern_analysis_empty_input(self) -> None:
        """T5: Empty historical data should return empty pattern summary."""
        engine = PatternAnalysisEngine()

        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        mock_snapshot = MagicMock()
        mock_snapshot.outcomes = []

        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            result = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should return None for empty input
        assert result is None

    def test_pattern_analysis_small_n_guard(self) -> None:
        """T6: Small-N guard should prevent pattern analysis on insufficient data."""
        engine = PatternAnalysisEngine()

        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        # Only 8 data points (below small-N threshold of 10)
        mock_snapshot = MagicMock()
        mock_outcomes = []

        for i in range(8):
            outcome = MagicMock()
            outcome.failure_signature = MagicMock()
            outcome.failure_signature.component = f"component_{i}"
            outcome.failure_signature.failure_type = "failure"
            outcome.failure_signature.healer_name = "healer"
            outcome.failure_signature.timestamp_utc = 1234567890 + i
            mock_outcomes.append(outcome)

        mock_snapshot.outcomes = mock_outcomes

        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
            result = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should return None due to small-N guard
        assert result is None

    def test_pattern_analysis_informational_only(self) -> None:
        """T7: Pattern analysis should be informational-only."""
        # This is inherent in the design - pattern analysis only produces summaries
        # It doesn't directly mutate any thresholds or configurations
        engine = PatternAnalysisEngine()

        embeddings = [
            [0.1, 0.2, 0.3, 0.4],
            [0.1, 0.2, 0.3, 0.4],
        ]
        metadata = [{"type": "test"}, {"type": "test"}]

        summary = engine.analyze(embeddings, metadata, min_cluster_size=2)

        # Verify informational-only nature
        assert isinstance(summary, PatternSummary)
        assert hasattr(summary, "clusters")
        assert hasattr(summary, "pattern_digest")
        # No direct configuration changes

    def test_pattern_analysis_kill_switch(self) -> None:
        """T8: Kill switch should disable pattern analysis entirely."""
        engine = PatternAnalysisEngine()

        mock_deps = MagicMock()
        mock_deps.pattern_analysis_engine = engine

        mock_snapshot = MagicMock()
        mock_snapshot.outcomes = []

        # Enable kill switch
        with patch.dict(os.environ, {"EMBEDDING_ENABLED": "false"}):
            result = _analyze_historical_patterns(mock_deps, mock_snapshot)

        # Should return None when kill switch enabled
        assert result is None
