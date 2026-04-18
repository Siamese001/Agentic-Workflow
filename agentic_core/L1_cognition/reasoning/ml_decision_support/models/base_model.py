"""
Base ML Model

Abstract base class for all ML models in the decision support layer.
Ensures consistent interface, governance compliance, and auditability.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_records_execution_trace

from ..config.model_registry import DecisionMode


class PredictionType(Enum):
    """Types of predictions models can make."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    RANKING = "ranking"
    ANOMALY_DETECTION = "anomaly_detection"
    MULTICLASS = "multiclass"


@dataclass
class ModelPrediction:
    """Single model prediction with full metadata."""

    prediction: Any  # The actual prediction
    confidence: float | None = None  # Confidence score (0-1)
    probability_distribution: dict[str, float] | None = None  # For classification
    top_features: list[dict[str, Any]] | None = None  # Feature importance
    model_version: str = ""
    feature_digest: str = ""
    training_data_digest: str = ""
    threshold_used: float | None = None
    decision_mode: DecisionMode = DecisionMode.ADVISORY
    prediction_timestamp: datetime = None
    trace_id: str = ""
    replay_key: str = ""
    policy_hash: str = ""
    model_metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.prediction_timestamp is None:
            self.prediction_timestamp = datetime.now()
        if self.model_metadata is None:
            self.model_metadata = {}


@dataclass
class ModelInput:
    """Model input with validation metadata."""

    features: dict[str, Any]
    feature_provenance: dict[str, Any]
    input_hash: str
    validation_status: str  # "valid", "invalid", "partial"
    validation_errors: list[str]
    preprocessing_applied: list[str]


class BaseMLModel(ABC):
    """
    Base class for all ML models in the decision support layer.

    Ensures all models:
    - Follow governance rules (advisory only, fail closed)
    - Provide full provenance and auditability
    - Support deterministic replay
    - Include confidence and feature importance
    - Respect architectural boundaries
    """

    def __init__(
        self,
        model_name: str,
        model_version: str,
        model_type: str,
        prediction_type: PredictionType,
        model_file_path: Path | None = None,
    ):
        self.model_name = model_name
        self.model_version = model_version
        self.model_type = model_type
        self.prediction_type = prediction_type
        self.model_file_path = model_file_path
        self.model = None
        self.feature_schema = None
        self.threshold_config = None
        self.is_loaded = False

        # Load model if file path provided
        if model_file_path and model_file_path.exists():
            self.load_model()

    @abstractmethod
    def load_model(self) -> None:
        """Load the model from file."""
        pass

    @abstractmethod
    def predict(
        self,
        model_input: ModelInput,
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.ADVISORY,
    ) -> ModelPrediction:
        """
        Make a prediction with full governance compliance.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Model prediction with full metadata
        """
        pass

    @abstractmethod
    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        pass

    def validate_input(self, features: dict[str, Any]) -> ModelInput:
        """
        Validate model input against feature schema.

        Args:
            features: Raw feature dictionary

        Returns:
            Validated model input
        """
        if not self.feature_schema:
            # No schema to validate against
            return ModelInput(
                features=features,
                feature_provenance={},
                input_hash="",
                validation_status="no_schema",
                validation_errors=[],
                preprocessing_applied=[],
            )

        # Validate features
        is_valid, errors = self.feature_schema.validate_features(features)

        # Compute input hash
        input_hash = self._compute_input_hash(features)

        return ModelInput(
            features=features,
            feature_provenance={},  # Will be filled by feature extractor
            input_hash=input_hash,
            validation_status="valid" if is_valid else "invalid",
            validation_errors=errors,
            preprocessing_applied=[],
        )

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """
        Preprocess features for model input.

        Args:
            features: Raw features

        Returns:
            Tuple of (processed_features, preprocessing_steps)
        """
        processed_features = features.copy()
        preprocessing_steps = []

        # Handle missing values according to schema
        if self.feature_schema:
            for feature_def in self.feature_schema.features:
                feature_name = feature_def.name

                if feature_name not in processed_features:
                    if feature_def.null_handling.value == "default_value":
                        processed_features[feature_name] = feature_def.default_value
                        preprocessing_steps.append(f"null_handling_default_{feature_name}")
                    elif feature_def.null_handling.value == "drop_feature":
                        # Feature will be dropped
                        preprocessing_steps.append(f"null_handling_drop_{feature_name}")

        # Type conversions
        for key, value in processed_features.items():
            if isinstance(value, str) and value.replace(".", "").replace("-", "").isdigit():
                # Convert string numbers to numeric
                if "." in value:
                    processed_features[key] = float(value)
                    preprocessing_steps.append(f"type_conversion_float_{key}")
                else:
                    processed_features[key] = int(value)
                    preprocessing_steps.append(f"type_conversion_int_{key}")

        return processed_features, preprocessing_steps

    def check_thresholds(self, prediction: ModelPrediction) -> bool:
        """
        Check if prediction meets configured thresholds.

        Args:
            prediction: Model prediction

        Returns:
            True if prediction passes thresholds
        """
        if not self.threshold_config:
            return True  # No thresholds to check

        # Check confidence threshold
        if prediction.confidence is not None:
            confidence_threshold = self.threshold_config.get("confidence_threshold", 0.5)
            if prediction.confidence < confidence_threshold:
                return False

        # Check prediction-specific thresholds based on type
        if self.prediction_type == PredictionType.CLASSIFICATION:
            return self._check_classification_thresholds(prediction)
        elif self.prediction_type == PredictionType.REGRESSION:
            return self._check_regression_thresholds(prediction)
        elif self.prediction_type == PredictionType.ANOMALY_DETECTION:
            return self._check_anomaly_thresholds(prediction)

        return True

    def _check_classification_thresholds(self, prediction: ModelPrediction) -> bool:
        """Check classification-specific thresholds."""
        if not prediction.probability_distribution:
            return True

        # Check minimum probability for predicted class
        pred_class = str(prediction.prediction)
        if pred_class in prediction.probability_distribution:
            min_prob = self.threshold_config.get("min_class_probability", 0.1)
            if prediction.probability_distribution[pred_class] < min_prob:
                return False

        return True

    def _check_regression_thresholds(self, prediction: ModelPrediction) -> bool:
        """Check regression-specific thresholds."""
        pred_value = float(prediction.prediction)

        # Check value range
        min_value = self.threshold_config.get("min_prediction_value")
        max_value = self.threshold_config.get("max_prediction_value")

        if min_value is not None and pred_value < min_value:
            return False
        if max_value is not None and pred_value > max_value:
            return False

        return True

    def _check_anomaly_thresholds(self, prediction: ModelPrediction) -> bool:
        """Check anomaly detection thresholds."""
        # For anomaly detection, lower scores typically mean more anomalous
        anomaly_score = float(prediction.prediction)
        anomaly_threshold = self.threshold_config.get("anomaly_threshold", 0.1)

        # Return True if not anomalous (score above threshold)
        return anomaly_score >= anomaly_threshold

    def create_prediction(
        self,
        prediction: Any,
        confidence: float | None = None,
        probability_distribution: dict[str, float] | None = None,
        top_features: list[dict[str, Any]] | None = None,
        threshold_used: float | None = None,
        decision_mode: DecisionMode = DecisionMode.ADVISORY,
        trace_id: str = "",
        replay_key: str = "",
        policy_hash: str = "",
    ) -> ModelPrediction:
        """Create a standardized prediction object."""
        return ModelPrediction(
            prediction=prediction,
            confidence=confidence,
            probability_distribution=probability_distribution,
            top_features=top_features,
            model_version=self.model_version,
            feature_digest=self._get_feature_digest(),
            training_data_digest=self._get_training_data_digest(),
            threshold_used=threshold_used,
            decision_mode=decision_mode,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

    def log_prediction(self, prediction: ModelPrediction, model_input: ModelInput) -> None:
        """Log prediction for audit and monitoring."""
        try:
            log_data = {
                "model_name": self.model_name,
                "model_version": self.model_version,
                "model_type": self.model_type,
                "prediction_type": self.prediction_type.value,
                "prediction": prediction.prediction,
                "confidence": prediction.confidence,
                "decision_mode": prediction.decision_mode.value,
                "threshold_used": prediction.threshold_used,
                "input_hash": model_input.input_hash,
                "feature_count": len(model_input.features),
                "validation_status": model_input.validation_status,
                "prediction_timestamp": prediction.prediction_timestamp.isoformat(),
                "trace_id": prediction.trace_id,
                "policy_hash": prediction.policy_hash,
            }

            # Log to execution trace
            _emit_records_execution_trace(
                root_trace_id=prediction.trace_id,
                layer="L1_ML_DECISION_SUPPORT",
                operation="prediction_made",
            )

        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
            # Log failure but don't fail the prediction
            print(f"Failed to log prediction: {e}")

    def _compute_input_hash(self, features: dict[str, Any]) -> str:
        """Compute hash of input features for reproducibility."""
        import hashlib
        import json

        # Normalize features for consistent hashing
        normalized_features = {}
        for key, value in sorted(features.items()):
            if isinstance(value, (int, float, str, bool)):
                normalized_features[key] = value
            else:
                normalized_features[key] = str(value)

        features_str = json.dumps(normalized_features, sort_keys=True)
        return hashlib.sha256(features_str.encode()).hexdigest()

    def _get_feature_digest(self) -> str:
        """Get feature schema digest."""
        return self.feature_schema.schema_digest if self.feature_schema else ""

    def _get_training_data_digest(self) -> str:
        """Get training data digest."""
        # This should be set during model training
        return getattr(self, "_training_data_digest", "")

    def set_training_data_digest(self, digest: str) -> None:
        """Set training data digest."""
        self._training_data_digest = digest

    def get_model_info(self) -> dict[str, Any]:
        """Get model information for registry."""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_type": self.model_type,
            "prediction_type": self.prediction_type.value,
            "is_loaded": self.is_loaded,
            "feature_schema_digest": self._get_feature_digest(),
            "training_data_digest": self._get_training_data_digest(),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.model_name}, version={self.model_version}, type={self.model_type})"
