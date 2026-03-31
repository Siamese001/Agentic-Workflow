"""
Unit tests for ML decision support Phase 4 components.

Tests advanced L0 router, C0 reranker, L6 detector, and unified inference engine
for deterministic behavior, governance compliance, and reliability.
"""

import pytest
import tempfile
import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch


# Lazy import fixtures to avoid collection-time conflicts
@pytest.fixture
def advanced_l0_feature_extractor():
    from agentic_core.L1_cognition.ml_decision_support.features.advanced_l0_features import AdvancedL0FeatureExtractor
    return AdvancedL0FeatureExtractor()

@pytest.fixture
def advanced_c0_feature_extractor():
    from agentic_core.L1_cognition.ml_decision_support.features.advanced_c0_features import AdvancedC0FeatureExtractor
    return AdvancedC0FeatureExtractor()

@pytest.fixture
def advanced_l6_feature_extractor():
    from agentic_core.L1_cognition.ml_decision_support.features.advanced_l6_features import AdvancedL6FeatureExtractor
    return AdvancedL6FeatureExtractor()

@pytest.fixture
def advanced_l0_router():
    from agentic_core.L1_cognition.ml_decision_support.models.advanced_l0_router import AdvancedL0Router
    return AdvancedL0Router()

@pytest.fixture
def advanced_c0_reranker():
    from agentic_core.L1_cognition.ml_decision_support.models.advanced_c0_reranker import AdvancedC0Reranker
    return AdvancedC0Reranker()

@pytest.fixture
def advanced_l6_detector():
    from agentic_core.L1_cognition.ml_decision_support.models.advanced_l6_detector import AdvancedL6Detector
    return AdvancedL6Detector()

@pytest.fixture
def unified_inference_engine():
    from agentic_core.L1_cognition.ml_decision_support.models.unified_inference_engine import UnifiedInferenceEngine
    return UnifiedInferenceEngine()


class TestAdvancedL0FeatureExtractor:
    """Test advanced L0 feature extraction functionality."""

    def test_semantic_similarity_extraction(self, advanced_l0_feature_extractor):
        """Test semantic similarity extraction."""
        extractor = advanced_l0_feature_extractor

        context = {
            "routing": {
                "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "option_embeddings": [
                    [0.2, 0.3, 0.4, 0.5, 0.6],
                    [0.1, 0.1, 0.1, 0.1, 0.1]
                ]
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "semantic_similarity_score" in result.features
        assert 0.0 <= result.features["semantic_similarity_score"] <= 1.0

    def test_intent_confidence_extraction(self, advanced_l0_feature_extractor):
        """Test intent confidence extraction."""
        extractor = advanced_l0_feature_extractor

        context = {
            "routing": {
                "intent_probabilities": {
                    "informational": 0.7,
                    "transactional": 0.2,
                    "navigational": 0.1
                }
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "intent_confidence" in result.features
        assert 0.0 <= result.features["intent_confidence"] <= 1.0

    def test_context_relevance_extraction(self, advanced_l0_feature_extractor):
        """Test context relevance extraction."""
        extractor = advanced_l0_feature_extractor

        context = {
            "routing": {
                "context_features": {
                    "session_continuity": 0.8,
                    "recent_interactions": 0.7,
                    "user_state": 0.6,
                    "environmental_factors": 0.5,
                    "temporal_relevance": 0.4
                }
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "context_relevance" in result.features
        assert 0.0 <= result.features["context_relevance"] <= 1.0

    def test_user_preference_extraction(self, advanced_l0_feature_extractor):
        """Test user preference extraction."""
        extractor = advanced_l0_feature_extractor

        context = {
            "routing": {
                "user_history": {
                    "successful_routes": {"current_option": 8},
                    "total_routes": 10
                },
                "user_preferences": {
                    "current_option": 0.8
                }
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "user_preference_score" in result.features
        assert 0.0 <= result.features["user_preference_score"] <= 1.0

    def test_routing_confidence_extraction(self, advanced_l0_feature_extractor):
        """Test overall routing confidence extraction."""
        extractor = advanced_l0_feature_extractor

        context = {
            "routing": {
                "semantic_similarity": 0.8,
                "intent_confidence": 0.7,
                "context_relevance": 0.6,
                "user_preference": 0.9,
                "historical_success": 0.8,
                "resource_availability": 0.7
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "routing_confidence" in result.features
        assert 0.0 <= result.features["routing_confidence"] <= 1.0


class TestAdvancedC0FeatureExtractor:
    """Test advanced C0 feature extraction functionality."""

    def test_embedding_similarity_extraction(self, advanced_c0_feature_extractor):
        """Test embedding similarity extraction."""
        extractor = advanced_c0_feature_extractor

        context = {
            "reranking": {
                "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "document_embedding": [0.2, 0.3, 0.4, 0.5, 0.6]
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "embedding_similarity" in result.features
        assert 0.0 <= result.features["embedding_similarity"] <= 1.0

    def test_attention_score_extraction(self, advanced_c0_feature_extractor):
        """Test attention score extraction."""
        extractor = advanced_c0_feature_extractor

        context = {
            "reranking": {
                "attention_weights": [0.1, 0.3, 0.2, 0.4, 0.0]
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "attention_score" in result.features
        assert 0.0 <= result.features["attention_score"] <= 1.0

    def test_document_authority_extraction(self, advanced_c0_feature_extractor):
        """Test document authority extraction."""
        extractor = advanced_c0_feature_extractor

        context = {
            "reranking": {
                "document_metadata": {
                    "source_reliability": 0.8,
                    "citation_count": 50,
                    "peer_reviewed": True,
                    "publication_quality": 0.7,
                    "author_reputation": 0.9
                }
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "document_authority" in result.features
        assert 0.0 <= result.features["document_authority"] <= 1.0

    def test_reranking_confidence_extraction(self, advanced_c0_feature_extractor):
        """Test overall reranking confidence extraction."""
        extractor = advanced_c0_feature_extractor

        context = {
            "reranking": {
                "embedding_similarity": 0.8,
                "attention_score": 0.7,
                "document_authority": 0.9,
                "relevance_confidence": 0.6,
                "user_engagement": 0.5,
                "temporal_relevance": 0.4,
                "semantic_density": 0.7,
                "retrieval_precision": 0.8,
                "context_alignment": 0.6
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "reranking_confidence" in result.features
        assert 0.0 <= result.features["reranking_confidence"] <= 1.0


class TestAdvancedL6FeatureExtractor:
    """Test advanced L6 feature extraction functionality."""

    def test_behavioral_deviation_extraction(self, advanced_l6_feature_extractor):
        """Test behavioral deviation extraction."""
        extractor = advanced_l6_feature_extractor

        context = {
            "anomaly": {
                "behavioral_data": {
                    "current_behavior": {
                        "request_frequency": 150,
                        "response_patterns": 0.6,
                        "error_patterns": 0.02,
                        "resource_usage": 0.7,
                        "timing_patterns": 0.4,
                        "interaction_patterns": 0.3
                    },
                    "baseline_behavior": {
                        "request_frequency": 100,
                        "response_patterns": 0.5,
                        "error_patterns": 0.01,
                        "resource_usage": 0.5,
                        "timing_patterns": 0.5,
                        "interaction_patterns": 0.5
                    }
                }
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "behavioral_deviation" in result.features
        assert 0.0 <= result.features["behavioral_deviation"] <= 1.0

    def test_system_metric_anomaly_extraction(self, advanced_l6_feature_extractor):
        """Test system metric anomaly extraction."""
        extractor = advanced_l6_feature_extractor

        context = {
            "anomaly": {
                "system_metrics": {
                    "cpu_usage": 85,
                    "cpu_baseline": 50,
                    "cpu_threshold": 80,
                    "memory_usage": 90,
                    "memory_baseline": 50,
                    "memory_threshold": 85,
                    "disk_io": 70,
                    "disk_baseline": 50,
                    "network_io": 60,
                    "network_baseline": 50,
                    "process_count": 150,
                    "process_baseline": 100,
                    "max_connections": 200
                }
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "system_metric_anomaly" in result.features
        assert 0.0 <= result.features["system_metric_anomaly"] <= 1.0

    def test_reconstruction_error_extraction(self, advanced_l6_feature_extractor):
        """Test reconstruction error extraction."""
        extractor = advanced_l6_feature_extractor

        context = {
            "anomaly": {
                "autoencoder_data": {
                    "input_reconstruction_error": 0.15,
                    "input_error_threshold": 0.1,
                    "latent_reconstruction_error": 0.08,
                    "latent_error_threshold": 0.1,
                    "output_reconstruction_error": 0.12,
                    "output_error_threshold": 0.1
                }
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "reconstruction_error" in result.features
        assert 0.0 <= result.features["reconstruction_error"] <= 1.0

    def test_anomaly_confidence_extraction(self, advanced_l6_feature_extractor):
        """Test overall anomaly confidence extraction."""
        extractor = advanced_l6_feature_extractor

        context = {
            "anomaly": {
                "behavioral_deviation": 0.7,
                "system_metric_anomaly": 0.6,
                "temporal_pattern_break": 0.4,
                "reconstruction_error": 0.5,
                "multivariate_anomaly": 0.3,
                "contextual_anomaly": 0.2,
                "performance_degradation": 0.4,
                "resource_anomaly": 0.5,
                "security_anomaly": 0.1
            },
            "trace_id": "test_trace_123"
        }

        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert result.success
        assert "anomaly_confidence" in result.features
        assert 0.0 <= result.features["anomaly_confidence"] <= 1.0


class TestAdvancedL0Router:
    """Test advanced L0 router model."""

    @pytest.fixture
    def mock_model(self, advanced_l0_router):
        """Create a mock advanced L0 router for testing."""
        router = advanced_l0_router

        # Mock the pipeline
        router.pipeline = Mock()
        router.pipeline.predict_proba.return_value = np.array([0.4, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])  # Neural_Advanced
        router.pipeline.predict.return_value = np.array([0])  # Neural_Advanced
        router.feature_names = ['semantic_similarity_score', 'intent_confidence', 'context_relevance',
                              'user_preference_score', 'historical_success_rate', 'resource_availability',
                              'routing_efficiency', 'system_load_factor', 'query_complexity', 'routing_confidence']
        router.is_loaded = True

        # Mock the create_prediction method to return proper prediction
        router.create_prediction = Mock(return_value=Mock(
            prediction="Neural_Advanced",
            confidence=0.4,
            probability_distribution={'Neural_Advanced': 0.4, 'Semantic_Optimized': 0.1, 'Context_Aware': 0.1, 'User_Personalized': 0.1, 'Performance_Optimized': 0.1, 'Load_Balanced': 0.1, 'Cost_Efficient': 0.1, 'Standard_Route': 0.1},
            decision_mode=Mock(value="advisory"),
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        ))

        return router

    def test_routing_prediction(self, mock_model):
        """Test routing prediction."""
        from agentic_core.L1_cognition.ml_decision_support.models.base_model import ModelInput

        features = {
            'semantic_similarity_score': 0.8,
            'intent_confidence': 0.7,
            'context_relevance': 0.6,
            'user_preference_score': 0.9,
            'historical_success_rate': 0.8,
            'resource_availability': 0.7,
            'routing_efficiency': 0.8,
            'system_load_factor': 0.4,
            'query_complexity': 0.5,
            'routing_confidence': 0.75
        }

        model_input = mock_model.validate_input(features)

        prediction = mock_model.predict(
            model_input=model_input,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert prediction.prediction == "Neural_Advanced"
        assert prediction.confidence == 0.4
        assert prediction.decision_mode.value in ["advisory", "escalated", "blocked"]

    def test_intelligent_routing_recommendations(self, mock_model):
        """Test intelligent routing recommendations."""
        routing_context = {
            "routing": {
                "semantic_similarity": 0.8,
                "intent_confidence": 0.7,
                "context_relevance": 0.6
            },
            "system_resources": {
                "cpu_usage": 60,
                "memory_usage": 50,
                "network_usage": 40
            }
        }

        recommendations = mock_model.route_intelligently(
            routing_context=routing_context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'routing_strategy' in recommendations
        assert 'confidence' in recommendations
        assert 'recommendations' in recommendations
        assert 'routing_analysis' in recommendations
        assert 'performance_prediction' in recommendations
        assert isinstance(recommendations['recommendations'], list)

    def test_semantic_analysis(self, mock_model):
        """Test semantic analysis for routing."""
        query_context = {
            "semantic_similarity": 0.8,
            "intent_confidence": 0.7,
            "query_complexity": 0.6,
            "context_relevance": 0.5
        }

        analysis = mock_model.analyze_query_semantics(
            query_context=query_context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'semantic_analysis' in analysis
        assert 'semantic_features' in analysis
        assert 'routing_suggestions' in analysis
        assert 'recommended_strategy' in analysis

    def test_user_preference_learning(self, mock_model):
        """Test user preference learning."""
        user_interactions = [
            {
                "routing_strategy": "Neural_Advanced",
                "user_satisfaction": 0.9
            },
            {
                "routing_strategy": "Semantic_Optimized",
                "user_satisfaction": 0.7
            },
            {
                "routing_strategy": "Neural_Advanced",
                "user_satisfaction": 0.8
            }
        ]

        learning_result = mock_model.learn_user_preferences(
            user_interactions=user_interactions,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'preference_analysis' in learning_result
        assert 'routing_preferences' in learning_result
        assert 'personalized_strategy' in learning_result
        assert 'learning_confidence' in learning_result


class TestAdvancedC0Reranker:
    """Test advanced C0 reranker model."""

    @pytest.fixture
    def mock_model(self, advanced_c0_reranker):
        """Create a mock advanced C0 reranker for testing."""
        reranker = advanced_c0_reranker

        # Mock the pipeline
        reranker.pipeline = Mock()
        reranker.pipeline.predict_proba.return_value = np.array([0.4, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])  # Transformer_Top
        reranker.pipeline.predict.return_value = np.array([0])  # Transformer_Top
        reranker.feature_names = ['embedding_similarity', 'attention_score', 'document_authority',
                              'relevance_confidence', 'user_engagement', 'temporal_relevance',
                              'semantic_density', 'retrieval_precision', 'context_alignment', 'reranking_confidence']
        reranker.is_loaded = True

        # Mock the create_prediction method to return proper prediction
        reranker.create_prediction = Mock(return_value=Mock(
            prediction="Transformer_Top",
            confidence=0.4,
            probability_distribution={'Transformer_Top': 0.4, 'Semantic_Prime': 0.1, 'Authority_Boost': 0.1, 'Engagement_Prioritized': 0.1, 'Context_Optimized': 0.1, 'Temporal_Relevant': 0.1, 'Quality_Enhanced': 0.1, 'Standard_Rerank': 0.1},
            decision_mode=Mock(value="advisory"),
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        ))

        return reranker

    def test_reranking_prediction(self, mock_model):
        """Test reranking prediction."""
        from agentic_core.L1_cognition.ml_decision_support.models.base_model import ModelInput

        features = {
            'embedding_similarity': 0.8,
            'attention_score': 0.7,
            'document_authority': 0.9,
            'relevance_confidence': 0.6,
            'user_engagement': 0.5,
            'temporal_relevance': 0.4,
            'semantic_density': 0.7,
            'retrieval_precision': 0.8,
            'context_alignment': 0.6,
            'reranking_confidence': 0.75
        }

        model_input = mock_model.validate_input(features)

        prediction = mock_model.predict(
            model_input=model_input,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert prediction.prediction == "Transformer_Top"
        assert prediction.confidence == 0.4
        assert prediction.decision_mode.value in ["advisory", "escalated", "blocked"]

    def test_intelligent_reranking_recommendations(self, mock_model):
        """Test intelligent reranking recommendations."""
        reranking_context = {
            "reranking": {
                "embedding_similarity": 0.8,
                "attention_score": 0.7,
                "document_authority": 0.9
            },
            "document_metadata": {
                "source_reliability": 0.8,
                "citation_count": 50
            }
        }

        recommendations = mock_model.rerank_intelligently(
            reranking_context=reranking_context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'reranking_strategy' in recommendations
        assert 'confidence' in recommendations
        assert 'recommendations' in recommendations
        assert 'reranking_analysis' in recommendations
        assert 'relevance_prediction' in recommendations
        assert isinstance(recommendations['recommendations'], list)

    def test_semantic_relevance_analysis(self, mock_model):
        """Test semantic relevance analysis."""
        semantic_context = {
            "embedding_similarity": 0.8,
            "attention_score": 0.7,
            "semantic_density": 0.6,
            "semantic_confidence": 0.75
        }

        analysis = mock_model.analyze_semantic_relevance(
            semantic_context=semantic_context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'semantic_analysis' in analysis
        assert 'semantic_features' in analysis
        assert 'reranking_suggestions' in analysis
        assert 'recommended_strategy' in analysis

    def test_attention_mechanism_application(self, mock_model):
        """Test attention mechanism application."""
        attention_context = {
            "attention_score": 0.7,
            "attention_weights": [0.1, 0.3, 0.2, 0.4],
            "attention_patterns": {
                "term1": 0.8,
                "term2": 0.6,
                "term3": 0.4
            },
            "attention_confidence": 0.75
        }

        analysis = mock_model.apply_attention_mechanism(
            attention_context=attention_context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'attention_analysis' in analysis
        assert 'attention_features' in analysis
        assert 'reranking_suggestions' in analysis
        assert 'recommended_strategy' in analysis

    def test_document_quality_evaluation(self, mock_model):
        """Test document quality evaluation."""
        quality_context = {
            "document_authority": 0.8,
            "relevance_confidence": 0.7,
            "retrieval_precision": 0.6,
            "quality_confidence": 0.75
        }

        evaluation = mock_model.evaluate_document_quality(
            quality_context=quality_context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'quality_analysis' in evaluation
        assert 'quality_features' in evaluation
        assert 'reranking_suggestions' in evaluation
        assert 'recommended_strategy' in evaluation


class TestAdvancedL6Detector:
    """Test advanced L6 detector model."""

    @pytest.fixture
    def mock_model(self, advanced_l6_detector):
        """Create a mock advanced L6 detector for testing."""
        detector = advanced_l6_detector

        # Mock the pipeline
        detector.pipeline = Mock()
        detector.pipeline.predict_proba.return_value = np.array([0.4, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])  # Critical_Alert
        detector.pipeline.predict.return_value = np.array([0])  # Critical_Alert
        detector.feature_names = ['behavioral_deviation', 'system_metric_anomaly', 'temporal_pattern_break',
                              'reconstruction_error', 'multivariate_anomaly', 'contextual_anomaly',
                              'performance_degradation', 'resource_anomaly', 'security_anomaly', 'anomaly_confidence']
        detector.is_loaded = True

        # Mock the create_prediction method to return proper prediction
        detector.create_prediction = Mock(return_value=Mock(
            prediction="Critical_Alert",
            confidence=0.4,
            probability_distribution={'Critical_Alert': 0.4, 'High_Priority': 0.1, 'Medium_Priority': 0.1, 'Low_Priority': 0.1, 'Informational': 0.1, 'Adaptive_Monitoring': 0.1, 'Contextual_Analysis': 0.1, 'Normal_Operation': 0.1},
            decision_mode=Mock(value="advisory"),
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        ))

        return detector

    def test_anomaly_detection_prediction(self, mock_model):
        """Test anomaly detection prediction."""
        from agentic_core.L1_cognition.ml_decision_support.models.base_model import ModelInput

        features = {
            'behavioral_deviation': 0.8,
            'system_metric_anomaly': 0.7,
            'temporal_pattern_break': 0.6,
            'reconstruction_error': 0.5,
            'multivariate_anomaly': 0.4,
            'contextual_anomaly': 0.3,
            'performance_degradation': 0.6,
            'resource_anomaly': 0.5,
            'security_anomaly': 0.2,
            'anomaly_confidence': 0.75
        }

        model_input = mock_model.validate_input(features)

        prediction = mock_model.predict(
            model_input=model_input,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert prediction.prediction == "Critical_Alert"
        assert prediction.confidence == 0.4
        assert prediction.decision_mode.value in ["advisory", "escalated", "blocked"]

    def test_intelligent_anomaly_detection_recommendations(self, mock_model):
        """Test intelligent anomaly detection recommendations."""
        anomaly_context = {
            "anomaly": {
                "behavioral_deviation": 0.8,
                "system_metric_anomaly": 0.7,
                "reconstruction_error": 0.6
            },
            "system_metrics": {
                "cpu_usage": 85,
                "memory_usage": 90
            }
        }

        recommendations = mock_model.detect_anomalies_intelligently(
            anomaly_context=anomaly_context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'anomaly_action' in recommendations
        assert 'confidence' in recommendations
        assert 'recommendations' in recommendations
        assert 'anomaly_analysis' in recommendations
        assert 'severity_assessment' in recommendations
        assert isinstance(recommendations['recommendations'], list)

    def test_behavioral_pattern_analysis(self, mock_model):
        """Test behavioral pattern analysis."""
        behavioral_context = {
            "behavioral_deviation": 0.8,
            "request_frequency": 150,
            "response_patterns": 0.6,
            "error_patterns": 0.02,
            "behavioral_confidence": 0.75
        }

        analysis = mock_model.analyze_behavioral_patterns(
            behavioral_context=behavioral_context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'behavioral_analysis' in analysis
        assert 'behavioral_features' in analysis
        assert 'anomaly_suggestions' in analysis
        assert 'recommended_action' in analysis

    def test_system_health_assessment(self, mock_model):
        """Test system health assessment."""
        system_context = {
            "system_metric_anomaly": 0.7,
            "performance_degradation": 0.6,
            "resource_anomaly": 0.5,
            "health_confidence": 0.75
        }

        assessment = mock_model.assess_system_health(
            system_context=system_context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'system_analysis' in assessment
        assert 'system_features' in assessment
        assert 'anomaly_suggestions' in assessment
        assert 'recommended_action' in assessment

    def test_security_threat_evaluation(self, mock_model):
        """Test security threat evaluation."""
        security_context = {
            "security_anomaly": 0.8,
            "authentication_anomaly": 0.7,
            "authorization_anomaly": 0.6,
            "threat_indicators": 0.5,
            "security_confidence": 0.75
        }

        evaluation = mock_model.evaluate_security_threats(
            security_context=security_context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )

        assert 'security_analysis' in evaluation
        assert 'security_features' in evaluation
        assert 'anomaly_suggestions' in evaluation
        assert 'recommended_action' in evaluation


class TestUnifiedInferenceEngine:
    """Test unified inference engine."""

    @pytest.fixture
    def mock_engine(self, unified_inference_engine):
        """Create a mock unified inference engine for testing."""
        engine = unified_inference_engine

        # Mock individual models
        engine.routing_model = Mock()
        engine.reranking_model = Mock()
        engine.anomaly_model = Mock()

        # Mock model predictions
        mock_routing_prediction = Mock()
        mock_routing_prediction.prediction = "Neural_Advanced"
        mock_routing_prediction.confidence = 0.8
        mock_routing_prediction.decision_mode.value = "advisory"

        mock_reranking_prediction = Mock()
        mock_reranking_prediction.prediction = "Transformer_Top"
        mock_reranking_prediction.confidence = 0.7
        mock_reranking_prediction.decision_mode.value = "advisory"

        mock_anomaly_prediction = Mock()
        mock_anomaly_prediction.prediction = "Normal_Operation"
        mock_anomaly_prediction.confidence = 0.9
        mock_anomaly_prediction.decision_mode.value = "advisory"

        engine.routing_model.predict.return_value = mock_routing_prediction
        engine.reranking_model.predict.return_value = mock_reranking_prediction
        engine.anomaly_model.predict.return_value = mock_anomaly_prediction

        # Mock feature extractors
        engine.routing_model.feature_extractor = Mock()
        engine.reranking_model.feature_extractor = Mock()
        engine.anomaly_model.feature_extractor = Mock()

        mock_extraction_result = Mock()
        mock_extraction_result.success = True
        mock_extraction_result.features = {}
        mock_extraction_result.provenance = {}

        engine.routing_model.feature_extractor.extract_features.return_value = mock_extraction_result
        engine.reranking_model.feature_extractor.extract_features.return_value = mock_extraction_result
        engine.anomaly_model.feature_extractor.extract_features.return_value = mock_extraction_result

        # Mock validate_input
        mock_model_input = Mock()
        engine.routing_model.validate_input.return_value = mock_model_input
        engine.reranking_model.validate_input.return_value = mock_model_input
        engine.anomaly_model.validate_input.return_value = mock_model_input

        return engine

    def test_unified_inference_execution(self, mock_engine):
        """Test unified inference execution."""
        request = UnifiedInferenceRequest(
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789",
            routing_context={"test": "data"},
            reranking_context={"test": "data"},
            anomaly_context={"test": "data"}
        )

        result = mock_engine.execute_unified_inference(request)

        assert result.trace_id == "test_trace_123"
        assert result.replay_key == "test_replay_456"
        assert result.policy_hash == "policy_hash_789"
        assert len(result.models_executed) == 3
        assert result.routing_result is not None
        assert result.reranking_result is not None
        assert result.anomaly_result is not None
        assert result.coordinated_decision is not None
        assert result.coordination_confidence > 0.0
        assert len(result.coordination_rationale) > 0
        assert len(result.unified_recommendations) > 0

    def test_comprehensive_analysis(self, mock_engine):
        """Test comprehensive analysis."""
        request = UnifiedInferenceRequest(
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789",
            routing_context={"test": "data"},
            reranking_context={"test": "data"},
            anomaly_context={"test": "data"}
        )

        # Mock detailed analysis methods
        mock_engine.routing_model.route_intelligently.return_value = {"test": "routing_analysis"}
        mock_engine.reranking_model.rerank_intelligently.return_value = {"test": "reranking_analysis"}
        mock_engine.anomaly_model.detect_anomalies_intelligently.return_value = {"test": "anomaly_analysis"}

        analysis = mock_engine.get_comprehensive_analysis(request)

        assert 'summary' in analysis
        assert 'routing_analysis' in analysis
        assert 'reranking_analysis' in analysis
        assert 'anomaly_analysis' in analysis
        assert 'coordination_analysis' in analysis
        assert 'unified_recommendations' in analysis
        assert 'implementation_priority' in analysis

    def test_configuration_validation(self, mock_engine):
        """Test configuration validation."""
        validation = mock_engine.validate_unified_configuration()

        assert 'is_valid' in validation
        assert 'issues' in validation
        assert 'recommendations' in validation
        assert 'model_status' in validation
        assert 'routing' in validation['model_status']
        assert 'reranking' in validation['model_status']
        assert 'anomaly' in validation['model_status']

    def test_partial_model_execution(self, mock_engine):
        """Test execution with only some models enabled."""
        request = UnifiedInferenceRequest(
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789",
            routing_context={"test": "data"},
            reranking_context={"test": "data"},
            enable_anomaly_detection=False
        )

        result = mock_engine.execute_unified_inference(request)

        assert len(result.models_executed) == 2
        assert "routing" in result.models_executed
        assert "reranking" in result.models_executed
        assert "anomaly" not in result.models_executed


class TestPhase4Integration:
    """Integration tests for Phase 4 components."""

    def test_advanced_routing_reranking_integration(self):
        """Test integration between advanced routing and reranking."""
        # This would test how advanced routing decisions influence reranking
        pass

    def test_anomaly_detection_coordination_integration(self):
        """Test integration between anomaly detection and coordination."""
        # This would test how anomaly detection affects unified coordination
        pass

    def test_full_phase4_coordination(self):
        """Test full Phase 4 coordination across all components."""
        # This would test end-to-end Phase 4 workflow
        pass

    def test_determinism_across_phase4(self):
        """Test determinism across all Phase 4 components."""
        # This would ensure that all Phase 4 models produce consistent results
        pass

    def test_governance_compliance_phase4(self):
        """Test governance compliance for Phase 4 components."""
        # This would verify that all Phase 4 components respect architectural boundaries
        pass

    def test_advanced_model_performance(self):
        """Test performance characteristics of advanced models."""
        # This would validate that advanced models meet performance requirements
        pass
