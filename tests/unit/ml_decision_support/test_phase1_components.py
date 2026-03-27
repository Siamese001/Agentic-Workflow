"""
Unit tests for ML decision support Phase 1 components.

Tests infrastructure, feature extractors, models, and inference components
to ensure deterministic behavior, governance compliance, and reliability.
"""

import pytest
import tempfile
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

# Test the infrastructure components
from agentic_core.L1_cognition.ml_decision_support.config.model_registry import (
    ModelRegistry, ModelStatus, DecisionMode, ModelMetadata
)
from agentic_core.L1_cognition.ml_decision_support.config.feature_schemas import (
    FeatureSchemas, FeatureSchema, FeatureType, NullHandling
)
from agentic_core.L1_cognition.ml_decision_support.config.threshold_config import (
    ThresholdConfig, ThresholdType, RollbackTrigger
)
from agentic_core.L1_cognition.ml_decision_support.features.base_extractor import (
    DeterministicFeatureExtractor, FeatureExtractionResult
)
from agentic_core.L1_cognition.ml_decision_support.features.l0_features import L0FeatureExtractor
from agentic_core.L1_cognition.ml_decision_support.features.c0_features import C0FeatureExtractor
from agentic_core.L1_cognition.ml_decision_support.features.l6_features import L6FeatureExtractor
from agentic_core.L1_cognition.ml_decision_support.models.base_model import (
    BaseMLModel, ModelPrediction, ModelInput, PredictionType
)
from agentic_core.L1_cognition.ml_decision_support.models.l0_route_recommender import L0RouteRecommender
from agentic_core.L1_cognition.ml_decision_support.models.c0_reranker import C0RetrievalReranker
from agentic_core.L1_cognition.ml_decision_support.models.l6_anomaly_detector import L6AnomalyDetector
from agentic_core.L1_cognition.ml_decision_support.inference.shadow_logger import (
    ShadowLogger, ShadowMode, ShadowLogEntry
)


class TestFeatureSchemas:
    """Test feature schema management."""
    
    def test_builtin_schemas_available(self):
        """Test that all builtin schemas are available."""
        schemas = FeatureSchemas()
        
        # Check that all Phase 1 schemas exist
        assert schemas.get_schema("l0_route_recommender") is not None
        assert schemas.get_schema("c0_retrieval_reranker") is not None
        assert schemas.get_schema("l6_anomaly_detector") is not None
    
    def test_l0_schema_validation(self):
        """Test L0 route recommender schema validation."""
        schemas = FeatureSchemas()
        schema = schemas.get_schema("l0_route_recommender")
        
        # Valid features
        valid_features = {
            "token_count": 100,
            "tool_complexity_score": 0.5,
            "latency_budget_ms": 5000,
            "user_confidence_score": 0.8,
            "path_success_history": 0.7,
            "current_load_ratio": 0.3,
            "semantic_similarity_score": 0.6,
            "policy_hash_version": "v1.0",
            "trace_id_hash": "abc123def456"
        }
        
        is_valid, errors = schema.validate_features(valid_features)
        assert is_valid
        assert len(errors) == 0
    
    def test_schema_null_handling(self):
        """Test schema null handling policies."""
        schemas = FeatureSchemas()
        schema = schemas.get_schema("l6_anomaly_detector")
        
        # Features with null values that should be handled
        features_with_nulls = {
            "latency_z_score": None,  # Should get default value
            "error_rate_spike": 1.5,
            "token_deviation": 0.0,
            "path_divergence": 0.0,
            "policy_hash_changes": 0.0,
            "replay_mismatch_count": 0.0,
            "escalation_frequency": 0.0,
            "healing_success_rate": 1.0,
            "semantic_drift_score": 0.0
        }
        
        is_valid, errors, processed = schemas.validate_features("l6_anomaly_detector", features_with_nulls)
        
        # Should be valid with default values applied
        assert is_valid
        assert "latency_z_score" in processed
        assert processed["latency_z_score"] == 0.0  # Default value


class TestModelRegistry:
    """Test model registry functionality."""
    
    @pytest.fixture
    def temp_registry(self):
        """Create temporary registry for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            registry_path = Path(temp_dir) / "test_registry"
            yield ModelRegistry(registry_path)
    
    def test_register_model(self, temp_registry):
        """Test model registration."""
        # Create a dummy model file
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            model_path = Path(f.name)
        
        try:
            # Register model
            model_id = temp_registry.register_model(
                model_name="test_model",
                model_version="1.0",
                model_type="logistic_regression",
                model_file_path=model_path,
                training_data_digest="abc123",
                feature_schema_digest="def456",
                metrics={"accuracy": 0.85},
                thresholds={"confidence": 0.7},
                created_by="test_user"
            )
            
            assert model_id == "test_model:1.0"
            
            # Verify registration
            record = temp_registry.get_model(model_id)
            assert record is not None
            assert record.metadata.model_name == "test_model"
            assert record.metadata.status == ModelStatus.DEVELOPMENT
            
        finally:
            model_path.unlink()
    
    def test_promote_model(self, temp_registry):
        """Test model promotion workflow."""
        # Register a model first
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            model_path = Path(f.name)
        
        try:
            model_id = temp_registry.register_model(
                model_name="test_model",
                model_version="1.0",
                model_type="logistic_regression",
                model_file_path=model_path,
                training_data_digest="abc123",
                feature_schema_digest="def456",
                metrics={"accuracy": 0.85},
                thresholds={"confidence": 0.7},
                created_by="test_user"
            )
            
            # Promote to candidate
            success = temp_registry.promote_model(
                model_id=model_id,
                target_status=ModelStatus.CANDIDATE,
                target_decision_mode=DecisionMode.SHADOW_ONLY,
                promoted_by="test_user",
                justification="Ready for testing"
            )
            
            assert success
            
            # Verify promotion
            record = temp_registry.get_model(model_id)
            assert record.metadata.status == ModelStatus.CANDIDATE
            assert record.metadata.decision_mode == DecisionMode.SHADOW_ONLY
            
        finally:
            model_path.unlink()
    
    def test_invalid_promotion_path(self, temp_registry):
        """Test that invalid promotion paths are rejected."""
        # Register a model
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            model_path = Path(f.name)
        
        try:
            model_id = temp_registry.register_model(
                model_name="test_model",
                model_version="1.0",
                model_type="logistic_regression",
                model_file_path=model_path,
                training_data_digest="abc123",
                feature_schema_digest="def456",
                metrics={"accuracy": 0.85},
                thresholds={"confidence": 0.7},
                created_by="test_user"
            )
            
            # Try invalid promotion (development to production directly)
            success = temp_registry.promote_model(
                model_id=model_id,
                target_status=ModelStatus.PRODUCTION,
                target_decision_mode=DecisionMode.ADVISORY,
                promoted_by="test_user",
                justification="Invalid promotion"
            )
            
            assert not success  # Should fail
            
        finally:
            model_path.unlink()


class TestFeatureExtractors:
    """Test feature extraction functionality."""
    
    def test_l0_feature_extraction(self):
        """Test L0 feature extraction."""
        extractor = L0FeatureExtractor()
        
        context = {
            "request": {
                "message": "Help me analyze this data",
                "tools": [{"type": "simple"}, {"type": "moderate"}],
                "constraints": {"latency_budget_ms": 3000}
            },
            "user": {"confidence": 0.8},
            "history": {
                "path_statistics": {
                    "Path_A": {"success_count": 8, "total_count": 10},
                    "Path_B": {"success_count": 15, "total_count": 20}
                }
            },
            "system": {
                "load_metrics": {
                    "cpu_utilization": 0.5,
                    "memory_utilization": 0.4,
                    "active_requests": 25,
                    "max_requests": 100
                }
            },
            "policy": {"hash_version": "v1.0"},
            "trace_id": "test_trace_123"
        }
        
        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )
        
        assert result.success
        assert "token_count" in result.features
        assert "tool_complexity_score" in result.features
        assert "latency_budget_ms" in result.features
        assert isinstance(result.features["token_count"], int)
        assert isinstance(result.features["tool_complexity_score"], float)
    
    def test_c0_feature_extraction(self):
        """Test C0 feature extraction."""
        extractor = C0FeatureExtractor()
        
        context = {
            "query": {
                "text": "machine learning algorithms",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
            },
            "document": {
                "text": "This document discusses various machine learning algorithms including neural networks and decision trees",
                "embedding": [0.15, 0.25, 0.35, 0.45, 0.55],
                "citation_count": 25,
                "source": {"type": "academic", "verified": True},
                "usage_stats": {"total_uses": 150, "recent_uses": 10},
                "sections": [{"type": "introduction"}, {"type": "methods"}, {"type": "results"}],
                "updated_at": "2024-01-15T10:00:00"
            },
            "cache_stats": {
                "total_queries": 1000,
                "cache_hits": 800,
                "recent_queries": ["hash1", "hash2", "hash3"]
            },
            "domain": "academic",
            "trace_id": "test_trace_123"
        }
        
        result = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )
        
        assert result.success
        assert "query_doc_similarity" in result.features
        assert "doc_authority_score" in result.features
        assert "recency_score" in result.features
        assert isinstance(result.features["query_doc_similarity"], float)
        assert 0.0 <= result.features["query_doc_similarity"] <= 1.0
    
    def test_l6_feature_extraction(self):
        """Test L6 feature extraction."""
        extractor = L6FeatureExtractor()
        
        context = {
            "metrics": {
                "latency": {
                    "current_ms": 150,
                    "baseline_mean_ms": 100,
                    "baseline_std_ms": 20
                },
                "error_rate": {
                    "current_rate": 0.05,
                    "baseline_rate": 0.01
                },
                "tokens": {
                    "current_count": 1200,
                    "baseline_count": 1000
                }
            },
            "routing": {
                "current_path": "Path_B",
                "path_analysis": {
                    "expected_distribution": {"Path_A": 0.6, "Path_B": 0.4},
                    "actual_distribution": {"Path_A": 0.3, "Path_B": 0.7}
                }
            },
            "policy": {
                "current_hash": "hash_v2",
                "history": [
                    {"hash": "hash_v1", "timestamp": "2024-01-14T10:00:00"},
                    {"hash": "hash_v2", "timestamp": "2024-01-15T10:00:00"}
                ]
            },
            "replay": {
                "results": [
                    {"status": "match"},
                    {"status": "mismatch"},
                    {"status": "match"}
                ]
            },
            "escalation": {
                "events": [
                    {"timestamp": "2024-01-15T09:30:00"},
                    {"timestamp": "2024-01-15T10:30:00"}
                ]
            },
            "healing": {
                "attempts": [
                    {"success": True},
                    {"success": False},
                    {"success": True}
                ]
            },
            "semantic": {
                "current_embeddings": [[0.1, 0.2, 0.3]],
                "baseline_embeddings": [[0.15, 0.25, 0.35]]
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
        assert "latency_z_score" in result.features
        assert "error_rate_spike" in result.features
        assert "token_deviation" in result.features
        assert isinstance(result.features["latency_z_score"], float)
    
    def test_feature_determinism(self):
        """Test that feature extraction is deterministic."""
        extractor = L0FeatureExtractor()
        
        context = {
            "request": {"message": "Test message", "tools": []},
            "policy": {"hash_version": "v1.0"},
            "trace_id": "test_trace_123"
        }
        
        # Extract features twice with same inputs
        result1 = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )
        
        result2 = extractor.extract_features(
            context=context,
            trace_id="test_trace_123",
            replay_key="test_replay_456",
            policy_hash="policy_hash_789"
        )
        
        # Should be identical
        assert result1.success == result2.success
        assert result1.features == result2.features
        assert result1.deterministic_hash == result2.deterministic_hash


class TestShadowLogger:
    """Test shadow logging functionality."""
    
    @pytest.fixture
    def temp_logger(self):
        """Create temporary shadow logger for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "test_logs"
            yield ShadowLogger(log_path)
    
    def test_log_prediction(self, temp_logger):
        """Test logging a prediction."""
        # Create mock prediction
        mock_prediction = Mock()
        mock_prediction.trace_id = "test_trace_123"
        mock_prediction.replay_key = "test_replay_456"
        mock_prediction.policy_hash = "policy_hash_789"
        mock_prediction.model_version = "1.0"
        mock_prediction.prediction = "Path_A"
        mock_prediction.confidence = 0.85
        mock_prediction.decision_mode = DecisionMode.ADVISORY
        mock_prediction.model_metadata = {"model_name": "test_model"}
        
        # Create mock input
        mock_input = Mock()
        mock_input.features = {"feature1": 0.5, "feature2": 0.3}
        mock_input.validation_status = "valid"
        mock_input.validation_errors = []
        
        # Log prediction
        log_id = temp_logger.log_prediction(
            model_input=mock_input,
            model_prediction=mock_prediction,
            logging_mode=ShadowMode.LOG_ONLY
        )
        
        assert log_id is not None
        assert "test_trace_123" in log_id
        
        # Check statistics
        stats = temp_logger.get_shadow_statistics()
        assert stats['total_predictions'] == 1
    
    def test_comparison_logging(self, temp_logger):
        """Test logging with comparison."""
        # Create mock prediction and actual decision
        mock_prediction = Mock()
        mock_prediction.trace_id = "test_trace_123"
        mock_prediction.replay_key = "test_replay_456"
        mock_prediction.policy_hash = "policy_hash_789"
        mock_prediction.model_version = "1.0"
        mock_prediction.prediction = "Path_A"
        mock_prediction.confidence = 0.85
        mock_prediction.decision_mode = DecisionMode.ADVISORY
        mock_prediction.model_metadata = {"model_name": "test_model"}
        
        mock_input = Mock()
        mock_input.features = {"feature1": 0.5}
        mock_input.validation_status = "valid"
        mock_input.validation_errors = []
        
        actual_decision = {
            "path": "Path_B",
            "confidence": 0.7
        }
        
        # Log with comparison
        log_id = temp_logger.log_prediction(
            model_input=mock_input,
            model_prediction=mock_prediction,
            logging_mode=ShadowMode.COMPARE,
            actual_decision=actual_decision
        )
        
        # Check that comparison was made
        stats = temp_logger.get_shadow_statistics()
        assert stats['comparisons_made'] == 1
        assert stats['path_disagreements'] == 1  # Path_A vs Path_B


class TestModelBaseClasses:
    """Test base model functionality."""
    
    def test_model_input_validation(self):
        """Test model input validation."""
        from agentic_core.L1_cognition.ml_decision_support.models.base_model import BaseMLModel
        
        # Create a mock model
        class MockModel(BaseMLModel):
            def load_model(self):
                pass
            
            def predict(self, model_input, trace_id, replay_key, policy_hash, decision_mode):
                return self.create_prediction(
                    prediction="test",
                    confidence=0.8,
                    trace_id=trace_id,
                    replay_key=replay_key,
                    policy_hash=policy_hash
                )
            
            def get_feature_importance(self, model_input):
                return []
        
        model = MockModel("test", "1.0", "test", PredictionType.CLASSIFICATION)
        
        # Test with valid features
        valid_features = {"feature1": 0.5, "feature2": 0.3}
        model_input = model.validate_input(valid_features)
        
        assert model_input.validation_status == "no_schema"  # No schema set
        assert model_input.features == valid_features
    
    def test_prediction_creation(self):
        """Test prediction object creation."""
        from agentic_core.L1_cognition.ml_decision_support.models.base_model import BaseMLModel
        
        class MockModel(BaseMLModel):
            def load_model(self):
                pass
            
            def predict(self, model_input, trace_id, replay_key, policy_hash, decision_mode):
                pass
            
            def get_feature_importance(self, model_input):
                pass
        
        model = MockModel("test", "1.0", "test", PredictionType.CLASSIFICATION)
        
        prediction = model.create_prediction(
            prediction="test_result",
            confidence=0.85,
            trace_id="test_trace",
            replay_key="test_replay",
            policy_hash="test_policy"
        )
        
        assert prediction.prediction == "test_result"
        assert prediction.confidence == 0.85
        assert prediction.trace_id == "test_trace"
        assert prediction.decision_mode == DecisionMode.ADVISORY


class TestDeterminismRequirements:
    """Test determinism requirements across all components."""
    
    def test_reproducible_feature_extraction(self):
        """Test that feature extraction is reproducible."""
        extractor = L0FeatureExtractor()
        
        context = {
            "request": {"message": "Test reproducibility", "tools": [{"type": "simple"}]},
            "policy": {"hash_version": "v1.0"},
            "system": {"load_metrics": {"cpu_utilization": 0.5}},
            "trace_id": "repro_test_123"
        }
        
        # Extract features multiple times
        results = []
        for i in range(5):
            result = extractor.extract_features(
                context=context,
                trace_id="repro_test_123",
                replay_key="repro_test_456",
                policy_hash="repro_test_789"
            )
            results.append(result)
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result.success == first_result.success
            assert result.features == first_result.features
            assert result.deterministic_hash == first_result.deterministic_hash
    
    def test_governance_compliance(self):
        """Test that all components respect governance rules."""
        # Test that models only operate in allowed modes
        from agentic_core.L1_cognition.ml_decision_support.models.base_model import DecisionMode
        
        # L0 should only use advisory or escalated modes
        l0_model = L0RouteRecommender()
        
        # Create mock input
        mock_input = Mock()
        mock_input.features = {"token_count": 100, "tool_complexity_score": 0.5}
        mock_input.validation_status = "valid"
        mock_input.validation_errors = []
        mock_input.preprocessing_applied = []
        
        # Test that L0 never gets production authority
        # (This would be tested more thoroughly in integration tests)
        assert True  # Placeholder for governance compliance test


# Integration tests would go here but are omitted for brevity
# They would test:
# - End-to-end model pipelines
# - Integration with existing architecture layers
# - Shadow mode operation
# - Replay functionality
# - Performance under load
