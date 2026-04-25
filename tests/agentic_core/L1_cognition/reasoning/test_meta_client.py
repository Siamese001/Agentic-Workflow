"""
Tests for MetaClient - meta-learning interface and client operations.

Coverage:
- Meta-learning model initialization
- Feature extraction for meta-decisions
- Prediction requests
- Model versioning
- Error handling for model failures
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentic_core.L1_cognition.reasoning.meta_client import MetaClient


class TestMetaClient:
    """Test suite for MetaClient."""

    def test_init_with_valid_model_path(self):
        """Test initialization with valid model path."""
        client = MetaClient(model_path="/valid/path/model.pkl")
        assert client.model_path == "/valid/path/model.pkl"

    def test_init_with_missing_model_path(self):
        """Test initialization fails with missing model."""
        with pytest.raises(FileNotFoundError):
            MetaClient(model_path="/nonexistent/model.pkl")

    def test_extract_features_from_context(self):
        """Test feature extraction from reasoning context."""
        client = MetaClient(model_path="/fake/path")  # Mock model
        client.model = Mock()
        
        context = {
            "task_complexity": "high",
            "layer": "L2",
            "estimated_tokens": 5000,
            "has_dependencies": True
        }
        
        features = client.extract_features(context)
        
        assert isinstance(features, dict)
        assert "task_complexity" in features or "complexity" in features

    def test_predict_decision_outcome(self):
        """Test prediction of decision outcome."""
        client = MetaClient(model_path="/fake/path")
        client.model = Mock()
        client.model.predict.return_value = [0.85]  # High confidence
        
        context = {
            "task_complexity": "high",
            "layer": "L2"
        }
        
        prediction = client.predict(context)
        
        assert prediction["confidence"] == 0.85
        assert prediction["success_probability"] >= 0.8

    def test_predict_with_low_confidence(self):
        """Test prediction with low confidence."""
        client = MetaClient(model_path="/fake/path")
        client.model = Mock()
        client.model.predict.return_value = [0.45]  # Low confidence
        
        context = {"task_complexity": "unknown"}
        prediction = client.predict(context)
        
        assert prediction["confidence"] == 0.45
        assert prediction["success_probability"] < 0.5

    def test_batch_predict(self):
        """Test batch prediction for multiple contexts."""
        client = MetaClient(model_path="/fake/path")
        client.model = Mock()
        client.model.predict.side_effect = [[0.8], [0.6], [0.9]]
        
        contexts = [
            {"task": "A"},
            {"task": "B"},
            {"task": "C"}
        ]
        
        predictions = client.batch_predict(contexts)
        
        assert len(predictions) == 3
        assert predictions[0]["confidence"] == 0.8

    def test_get_model_version(self):
        """Test retrieving model version information."""
        client = MetaClient(model_path="/fake/path")
        client.model_version = "1.2.3"
        
        version = client.get_version()
        assert version == "1.2.3"

    def test_handle_model_prediction_error(self):
        """Test graceful handling of model prediction errors."""
        client = MetaClient(model_path="/fake/path")
        client.model = Mock()
        client.model.predict.side_effect = Exception("Model error")
        
        context = {"task": "test"}
        
        with pytest.raises(RuntimeError):
            client.predict(context)

    def test_update_model(self):
        """Test updating the meta-learning model."""
        client = MetaClient(model_path="/fake/path")
        new_model = Mock()
        
        client.update_model(new_model)
        assert client.model == new_model

    def test_get_feature_importance(self):
        """Test retrieving feature importance from model."""
        client = MetaClient(model_path="/fake/path")
        client.model = Mock()
        client.model.feature_importances_ = [0.3, 0.5, 0.2]
        
        importance = client.get_feature_importance()
        
        assert len(importance) == 3
        assert max(importance) == 0.5

    def test_validate_input_features(self):
        """Test validation of input features."""
        client = MetaClient(model_path="/fake/path")
        client.required_features = ["complexity", "layer", "tokens"]
        
        valid_features = {
            "complexity": "high",
            "layer": "L2",
            "tokens": 5000
        }
        
        assert client.validate_features(valid_features) is True

    def test_validate_missing_features(self):
        """Test validation fails with missing features."""
        client = MetaClient(model_path="/fake/path")
        client.required_features = ["complexity", "layer", "tokens"]
        
        invalid_features = {
            "complexity": "high"
            # Missing layer and tokens
        }
        
        assert client.validate_features(invalid_features) is False
