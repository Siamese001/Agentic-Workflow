"""
Tests for Phase 2 Multi-Model Integration - Contextual Bandit and Ensemble Router

Comprehensive test suite covering Wave 2.1 (Contextual Bandit) and Wave 2.2 (Ensemble Router)
implementations for L0 routing confidence calibration.
"""

import pytest


# Lazy imports — wrapped to avoid collection-time errors
try:
    from agentic_core.L0_routing.engines.contextual_bandit import (
        BanditArm,
        BanditContext,
        BanditDecision,
        LinUCBBandit,
        calculate_routing_reward,
        create_bandit_context,
    )
    from agentic_core.L0_routing.engines.ensemble_router import (
        BaseRoutingModel,
        EnsembleDecision,
        EnsembleFeatures,
        EnsembleRouter,
        IntentEmbeddingModel,
        MetaLearner,
        RoutingPrediction,
        RuleBasedModel,
        create_default_ensemble,
    )
except ImportError:
    pass


import numpy as np
import time
from unittest.mock import Mock, patch
from typing import Dict, Any

# Import the modules we're testing


class TestContextualBandit:
    """Test suite for LinUCB contextual bandit implementation"""

    @pytest.fixture
    def bandit(self):
        """Create a test bandit instance"""
        return LinUCBBandit(
            context_dim=20,
            alpha=1.0,
            arms=["agent_1", "agent_2", "agent_3"],
            decay_factor=0.99
        )

    @pytest.fixture
    def sample_context(self):
        """Create a sample bandit context"""
        return BanditContext(
            intent_embedding=np.random.randn(20),  # Changed from 10 to 20
            intent_length=25,
            intent_complexity=0.5,
            user_history_score=0.8,
            user_success_rate=0.7,
            current_load=0.3,
            time_of_day=14,
            day_of_week=2,
            adg_territory_score=0.6,
            confidence_tiers={"C0": 100, "C1": 200, "C2": 300}
        )

    def test_bandit_initialization(self, bandit):
        """Test bandit initialization"""
        assert bandit.context_dim == 20
        assert bandit.alpha == 1.0
        assert len(bandit.arms) == 3
        assert bandit.round_count == 0
        assert bandit.total_reward == 0.0

        # Check that all arms are properly initialized
        for arm_id, arm in bandit.arms.items():
            assert arm.A.shape == (20, 20)
            assert arm.b.shape == (20,)
            assert arm.theta.shape == (20,)

    def test_add_arm(self, bandit):
        """Test adding new arms"""
        initial_count = len(bandit.arms)
        bandit.add_arm("agent_4", "new_agent", capability_match=0.9)

        assert len(bandit.arms) == initial_count + 1
        assert "agent_4" in bandit.arms
        assert bandit.arms["agent_4"].capability_match == 0.9

    def test_select_arm(self, bandit, sample_context):
        """Test arm selection"""
        decision = bandit.select_arm(sample_context)

        assert isinstance(decision, BanditDecision)
        assert decision.selected_arm in bandit.arms
        assert 0.0 <= decision.confidence <= 1.0
        assert decision.uncertainty >= 0.0
        assert decision.context_used == sample_context
        assert len(decision.all_arm_scores) == len(bandit.arms)

        # Check that round count increased
        assert bandit.round_count == 1

    def test_update_arm(self, bandit, sample_context):
        """Test arm updates with rewards"""
        decision = bandit.select_arm(sample_context)
        initial_theta = bandit.arms[decision.selected_arm].theta.copy()

        # Update with positive reward
        bandit.update(decision, reward=1.0)

        # Check that parameters changed
        new_theta = bandit.arms[decision.selected_arm].theta
        assert not np.array_equal(initial_theta, new_theta)

        # Check global metrics
        assert bandit.total_reward == 1.0
        assert len(bandit.reward_history) == 1
        assert bandit.reward_history[0] == 1.0

    def test_exploration_rate_decay(self, bandit, sample_context):
        """Test exploration rate decay over time"""
        initial_rate = bandit.exploration_rate
        assert initial_rate == 0.1

        # Make several updates
        for i in range(100):
            decision = bandit.select_arm(sample_context)
            bandit.update(decision, reward=0.5)

        # Exploration rate should have decayed
        assert bandit.exploration_rate < initial_rate
        assert bandit.exploration_rate >= 0.01  # Minimum bound

    def test_arm_statistics(self, bandit, sample_context):
        """Test arm statistics calculation"""
        # Make some predictions and updates
        for i in range(10):
            decision = bandit.select_arm(sample_context)
            bandit.update(decision, reward=0.7)

        stats = bandit.get_arm_statistics()

        assert len(stats) == len(bandit.arms)
        for arm_id, arm_stats in stats.items():
            assert "success_rate" in arm_stats
            assert "confidence" in arm_stats
            assert "current_load" in arm_stats
            assert "capability_match" in arm_stats
            assert "samples_tracked" in arm_stats

            assert 0.0 <= arm_stats["success_rate"] <= 1.0
            assert 0.0 <= arm_stats["confidence"] <= 1.0

    def test_save_load_state(self, bandit, sample_context):
        """Test state saving and loading"""
        import tempfile
        import os

        # Make some updates to create state
        for i in range(5):
            decision = bandit.select_arm(sample_context)
            bandit.update(decision, reward=0.8)

        # Save state
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            bandit.save_state(temp_path)

            # Create new bandit and load state
            new_bandit = LinUCBBandit(context_dim=20, alpha=1.0)
            new_bandit.load_state(temp_path)

            # Check that state was restored
            assert new_bandit.round_count == bandit.round_count
            assert new_bandit.total_reward == bandit.total_reward
            assert len(new_bandit.arms) == len(bandit.arms)

        finally:
            os.unlink(temp_path)

    def test_reset(self, bandit, sample_context):
        """Test bandit reset"""
        # Make some updates
        for i in range(5):
            decision = bandit.select_arm(sample_context)
            bandit.update(decision, reward=0.6)

        # Reset
        bandit.reset()

        # Check that state is reset
        assert bandit.round_count == 0
        assert bandit.total_reward == 0.0
        assert bandit.exploration_rate == 0.1
        assert len(bandit.reward_history) == 0
        assert len(bandit.decision_history) == 0

class TestEnsembleRouter:
    """Test suite for Ensemble Router implementation"""

    @pytest.fixture
    def mock_classifier(self):
        """Create a mock embedding classifier"""
        classifier = Mock()
        classifier.classify.return_value = ("test_agent", 0.8)
        return classifier

    @pytest.fixture
    def ensemble_router(self, mock_classifier):
        """Create a test ensemble router"""
        embedding_model = IntentEmbeddingModel(mock_classifier, weight=1.0)

        rules = {
            "agent_keywords": {
                "test_agent": ["test", "example"],
                "other_agent": ["other", "different"]
            }
        }
        rule_model = RuleBasedModel(rules, weight=0.8)

        return EnsembleRouter(
            base_models=[embedding_model, rule_model],
            ensemble_strategy="weighted_voting"
        )

    def test_ensemble_initialization(self, ensemble_router):
        """Test ensemble router initialization"""
        assert len(ensemble_router.base_models) == 2
        assert ensemble_router.ensemble_strategy == "weighted_voting"
        assert ensemble_router.prediction_count == 0
        assert ensemble_router.success_count == 0
        assert len(ensemble_router.model_weights) == 2

    def test_add_model(self, ensemble_router):
        """Test adding models to ensemble"""
        initial_count = len(ensemble_router.base_models)

        mock_classifier = Mock()
        mock_classifier.classify.return_value = ("new_agent", 0.7)
        new_model = IntentEmbeddingModel(mock_classifier, weight=0.9)

        ensemble_router.add_model(new_model)

        assert len(ensemble_router.base_models) == initial_count + 1
        assert len(ensemble_router.model_weights) == initial_count + 1

    def test_ensemble_routing(self, ensemble_router):
        """Test ensemble routing decision"""
        query = "test query for routing"
        context = {"user_id": "test_user", "session_id": "test_session"}

        decision = ensemble_router.route(query, context)

        assert isinstance(decision, EnsembleDecision)
        assert decision.selected_agent in ["test_agent", "other_agent"]
        assert 0.0 <= decision.confidence <= 1.0
        assert decision.uncertainty >= 0.0
        assert len(decision.base_predictions) == 2
        assert decision.decision_time >= 0.0
        assert decision.reasoning is not None

    def test_weighted_voting(self, ensemble_router):
        """Test weighted voting strategy"""
        query = "test query"
        context = {}

        decision = ensemble_router.route(query, context)

        # Should use weighted voting
        assert ensemble_router.ensemble_strategy == "weighted_voting"
        assert decision.selected_agent is not None
        assert decision.confidence > 0.0

    def test_meta_learning_strategy(self, mock_classifier):
        """Test meta-learning strategy"""
        embedding_model = IntentEmbeddingModel(mock_classifier, weight=1.0)
        rules = {"agent_keywords": {"test_agent": ["test"]}}
        rule_model = RuleBasedModel(rules, weight=0.8)

        ensemble = EnsembleRouter(
            base_models=[embedding_model, rule_model],
            ensemble_strategy="meta_learning"
        )

        decision = ensemble.route("test query", {})

        assert decision.selected_agent is not None
        assert decision.meta_confidence >= 0.0
        assert decision.meta_confidence <= 1.0

    def test_update_outcome(self, ensemble_router):
        """Test updating ensemble based on outcomes"""
        query = "test query"
        context = {}

        # Make a routing decision
        decision = ensemble_router.route(query, context)

        # Update with successful outcome
        ensemble_router.update_outcome(decision, success=True)

        # Check that metrics updated
        assert ensemble_router.prediction_count == 1
        assert ensemble_router.success_count == 1
        assert ensemble_router.get_success_rate() == 1.0

        # Update with unsuccessful outcome
        ensemble_router.update_outcome(decision, success=False)

        assert ensemble_router.prediction_count == 2
        assert ensemble_router.success_count == 1
        assert ensemble_router.get_success_rate() == 0.5

    def test_model_performance_tracking(self, ensemble_router):
        """Test model performance tracking"""
        query = "test query"
        context = {}

        # Make several routing decisions
        for i in range(5):
            decision = ensemble_router.route(query, context)
            ensemble_router.update_outcome(decision, success=i % 2 == 0)  # Alternate success/failure

        performance = ensemble_router.get_model_performance()

        assert len(performance) == 2
        for model_name, metrics in performance.items():
            assert "reliability" in metrics
            assert "predictions" in metrics
            assert "successes" in metrics
            assert "weight" in metrics

            assert 0.0 <= metrics["reliability"] <= 1.0
            assert metrics["predictions"] >= 0
            assert metrics["successes"] >= 0

    def test_ensemble_features_extraction(self, ensemble_router):
        """Test ensemble features extraction"""
        query = "test query"
        context = {}

        decision = ensemble_router.route(query, context)
        features = decision.ensemble_features

        assert isinstance(features, EnsembleFeatures)
        assert 0.0 <= features.mean_confidence <= 1.0
        assert features.std_confidence >= 0.0
        assert 0.0 <= features.agent_agreement_score <= 1.0
        assert 0.0 <= features.top_agent_consensus <= 1.0
        assert 0.0 <= features.agent_diversity <= 1.0
        assert features.mean_uncertainty >= 0.0

    def test_save_load_state(self, ensemble_router):
        """Test ensemble state saving and loading"""
        import tempfile
        import os

        # Make some routing decisions
        for i in range(3):
            decision = ensemble_router.route("test query", {})
            ensemble_router.update_outcome(decision, success=True)

        # Save state
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            ensemble_router.save_state(temp_path)

            # Verify file was created and contains data
            with open(temp_path, 'r') as f:
                data = f.read()
                assert len(data) > 0
                assert "ensemble_strategy" in data
                assert "prediction_count" in data

        finally:
            os.unlink(temp_path)

class TestIntegration:
    """Integration tests for Phase 2 components"""

    def test_bandit_ensemble_integration(self):
        """Test integration between bandit and ensemble router"""
        # Create bandit
        bandit = LinUCBBandit(
            context_dim=20,
            alpha=1.0,
            arms=["agent_1", "agent_2"],
            decay_factor=0.99
        )

        # Create ensemble
        mock_classifier = Mock()
        mock_classifier.classify.return_value = ("agent_1", 0.8)

        ensemble = create_default_ensemble(mock_classifier)

        # Test routing through both systems
        context = BanditContext(
            intent_embedding=np.random.randn(10),
            intent_length=20,
            intent_complexity=0.5,
            user_history_score=0.7,
            user_success_rate=0.6,
            current_load=0.4,
            time_of_day=10,
            day_of_week=1,
            adg_territory_score=0.5,
            confidence_tiers={"C0": 100, "C1": 200}
        )

        # Bandit decision
        bandit_decision = bandit.select_arm(context)

        # Ensemble decision
        ensemble_decision = ensemble.route("test query", {})

        # Both should return valid decisions
        assert isinstance(bandit_decision, BanditDecision)
        assert isinstance(ensemble_decision, EnsembleDecision)
        assert bandit_decision.selected_agent in ["agent_1", "agent_2"]
        assert ensemble_decision.selected_agent is not None

    def test_reward_calculation(self):
        """Test reward calculation function"""
        # Test successful routing
        reward = calculate_routing_reward(
            selected_agent="test_agent",
            task_completed=True,
            completion_time=60.0,  # 1 minute
            user_satisfaction=0.9
        )
        assert reward > 0.8  # Should be high for fast, successful task

        # Test unsuccessful routing
        reward = calculate_routing_reward(
            selected_agent="test_agent",
            task_completed=False,
            completion_time=300.0
        )
        assert reward == 0.0  # Should be 0 for failed tasks

        # Test slow but successful
        reward = calculate_routing_reward(
            selected_agent="test_agent",
            task_completed=True,
            completion_time=300.0  # 5 minutes
        )
        assert 0.0 < reward < 1.0  # Should be moderate

class TestPerformance:
    """Performance tests for Phase 2 components"""

    def test_bandit_performance(self):
        """Test bandit performance with many decisions"""
        bandit = LinUCBBandit(
            context_dim=20,
            alpha=1.0,
            arms=["agent_1", "agent_2", "agent_3"],
            decay_factor=0.99
        )

        context = BanditContext(
            intent_embedding=np.random.randn(10),
            intent_length=25,
            intent_complexity=0.5,
            user_history_score=0.8,
            user_success_rate=0.7,
            current_load=0.3,
            time_of_day=14,
            day_of_week=2,
            adg_territory_score=0.6,
            confidence_tiers={"C0": 100, "C1": 200, "C2": 300}
        )

        # Measure performance for 1000 decisions
        start_time = time.time()

        for i in range(1000):
            decision = bandit.select_arm(context)
            reward = 1.0 if decision.selected_agent == "agent_1" else 0.0
            bandit.update(decision, reward)

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete 1000 decisions in reasonable time
        assert total_time < 5.0  # 5 seconds max
        assert bandit.round_count == 1000
        assert len(bandit.decision_history) == 1000

        # Check that learning occurred
        agent_1_stats = bandit.get_arm_statistics()["agent_1"]
        assert agent_1_stats["success_rate"] > 0.5  # Should have learned preference

    def test_ensemble_performance(self):
        """Test ensemble performance with many decisions"""
        mock_classifier = Mock()
        mock_classifier.classify.return_value = ("test_agent", 0.8)

        ensemble = create_default_ensemble(mock_classifier)

        # Measure performance for 500 decisions
        start_time = time.time()

        for i in range(500):
            decision = ensemble.route(f"test query {i}", {})
            ensemble.update_outcome(decision, success=i % 3 != 0)  # 2/3 success rate

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete 500 decisions in reasonable time
        assert total_time < 3.0  # 3 seconds max
        assert ensemble.prediction_count == 500

        # Check that success rate is tracked correctly
        assert 0.6 <= ensemble.get_success_rate() <= 0.7  # Should be close to 2/3

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
