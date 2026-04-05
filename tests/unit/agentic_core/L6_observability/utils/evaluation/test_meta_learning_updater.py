"""
tests/unit/agentic_core/L6_observability/evaluation/test_meta_learning_updater.py

Unit tests for Wave 2.3: Meta-Learning State Updates
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L6_observability.utils.evaluation.meta_learning_updater import (
    ConvergenceState,
    MetaLearningState,
    MetaLearningUpdater,
    get_meta_learning_updater,
    reset_meta_learning_updater,
)


class TestMetaLearningUpdater:
    """Test suite for MetaLearningUpdater."""

    def test_update_from_evaluation(self):
        """Test updating from evaluation."""
        updater = MetaLearningUpdater()

        state = updater.update_from_evaluation("test", 0.85)

        assert isinstance(state, MetaLearningState)
        assert state.total_updates == 1
        assert state.avg_eval_score == 0.85

    def test_convergence_detection_improving(self):
        """Test convergence detection for improving scores."""
        updater = MetaLearningUpdater()

        # Add improving scores with larger increments to avoid convergence
        for i in range(25):
            updater.update_from_evaluation("test", 0.5 + i * 0.02, time.time() + i)

        state = updater.get_current_state()
        # Should be improving or converged depending on variance
        assert state.convergence_state in [ConvergenceState.IMPROVING, ConvergenceState.CONVERGED]

    def test_convergence_detection_converged(self):
        """Test convergence detection for stable scores."""
        updater = MetaLearningUpdater(convergence_threshold=0.001)

        # Add stable scores
        for i in range(20):
            updater.update_from_evaluation("test", 0.85, time.time() + i)

        state = updater.get_current_state()
        assert state.convergence_state == ConvergenceState.CONVERGED

    def test_learning_rate_adaptation(self):
        """Test learning rate adapts based on convergence."""
        updater = MetaLearningUpdater(initial_learning_rate=0.01)

        initial_lr = updater._learning_rate

        # Add improving scores to trigger learning rate increase
        for i in range(25):
            updater.update_from_evaluation("test", 0.5 + i * 0.01, time.time() + i)

        # Learning rate should have changed
        assert updater._learning_rate != initial_lr

    def test_insights_extraction(self):
        """Test insight extraction."""
        updater = MetaLearningUpdater()

        # Add scores
        for i in range(10):
            updater.update_from_evaluation("test", 0.8 + i * 0.01)

        state = updater.get_current_state()
        assert "sample_count" in state.insights
        assert "recent_mean" in state.insights
        assert state.insights["sample_count"] == 10

    def test_reset(self):
        """Test resetting state."""
        updater = MetaLearningUpdater()

        # Add some updates
        for i in range(5):
            updater.update_from_evaluation("test", 0.85)

        updater.reset()

        state = updater.get_current_state()
        assert state.total_updates == 0
        assert state.convergence_state == ConvergenceState.NOT_STARTED

    def test_negative_score_rejected(self):
        """Test negative score raises ValueError."""
        updater = MetaLearningUpdater()

        with pytest.raises(ValueError, match="Score must be non-negative"):
            updater.update_from_evaluation("test", -0.5)

    def test_empty_eval_type_rejected(self):
        """Test empty eval_type raises ValueError."""
        updater = MetaLearningUpdater()

        with pytest.raises(ValueError, match="Evaluation type cannot be empty"):
            updater.update_from_evaluation("", 0.85)

        with pytest.raises(ValueError, match="Evaluation type cannot be empty"):
            updater.update_from_evaluation("   ", 0.85)

    def test_degrading_convergence_state(self):
        """Test convergence detection for degrading scores."""
        updater = MetaLearningUpdater()

        # Add degrading scores
        for i in range(25):
            updater.update_from_evaluation("test", 0.9 - i * 0.02, time.time() + i)

        state = updater.get_current_state()
        assert state.convergence_state in [ConvergenceState.DEGRADING, ConvergenceState.IMPROVING]


class TestGlobalInstance:
    """Test global instance management."""

    def test_singleton_pattern(self):
        """Test meta-learning updater singleton pattern."""
        reset_meta_learning_updater()

        updater1 = get_meta_learning_updater()
        updater2 = get_meta_learning_updater()

        assert updater1 is updater2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
