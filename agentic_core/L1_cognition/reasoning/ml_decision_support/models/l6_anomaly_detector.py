"""
L6 Anomaly Detector

Isolation Forest model for detecting system anomalies including
performance issues, behavioral changes, and semantic drift.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
except ImportError:
    IsolationForest = None
    StandardScaler = None

from ..config.model_registry import DecisionMode
from ..features.l6_features import L6FeatureExtractor
from ._pickle_io import safe_pickle_dump, safe_pickle_load
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType
from tqdm import tqdm


class L6AnomalyDetector(BaseMLModel):
    """
    Isolation Forest model for L6 anomaly detection.

    Detects anomalies in system behavior including:
    - Performance anomalies (latency spikes, error rate changes)
    - Behavioral anomalies (path divergence, escalation patterns)
    - Integrity anomalies (policy changes, replay mismatches)
    - Recovery anomalies (healing success rates)
    - Semantic anomalies (drift in embeddings)
    - Operational health indicators

    Always operates in shadow/escalated mode - L6 remains observation-only.
    """

    def __init__(self, model_file_path: Path | None = None):
        if IsolationForest is None or StandardScaler is None:
            raise ImportError("scikit-learn is required for L6AnomalyDetector")

        super().__init__(
            model_name="l6_anomaly_detector",
            model_version="1.0",
            model_type="isolation_forest",
            prediction_type=PredictionType.ANOMALY_DETECTION,
            model_file_path=model_file_path,
        )

        # Initialize feature extractor
        self.feature_extractor = L6FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.pipeline = None
        self.feature_names = None
        self.contamination_rate = 0.1  # Expected anomaly rate

        # Default thresholds
        self.threshold_config = {
            "anomaly_threshold": 0.1,
            "high_anomaly_threshold": 0.05,
            "critical_anomaly_threshold": 0.02,
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the Isolation Forest model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            model_data = safe_pickle_load(self.model_file_path)

            self.pipeline = model_data.get("pipeline")
            self.feature_names = model_data.get("feature_names", [])
            self.contamination_rate = model_data.get("contamination_rate", 0.1)
            self.threshold_config = model_data.get("threshold_config", self.threshold_config)
            self._training_data_digest = model_data.get("training_data_digest", "")

            if self.pipeline is None:
                raise ValueError("No model found in saved file")

            self.is_loaded = True

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def save_model(self, model_file_path: Path) -> None:
        """Save the model to file."""
        if self.pipeline is None:
            raise RuntimeError("No model to save")

        model_data = {
            "pipeline": self.pipeline,
            "feature_names": self.feature_names,
            "contamination_rate": self.contamination_rate,
            "threshold_config": self.threshold_config,
            "training_data_digest": getattr(self, "_training_data_digest", ""),
            "model_metadata": {
                "model_name": self.model_name,
                "model_version": self.model_version,
                "model_type": self.model_type,
                "prediction_type": self.prediction_type.value,
                "feature_schema_digest": self.feature_schema.schema_digest,
                "saved_at": datetime.now().isoformat(),
                "isolation_forest_params": self._get_model_params(),
            },
        }

        safe_pickle_dump(model_data, model_file_path)

    def predict(
        self,
        model_input: ModelInput,
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.SHADOW_ONLY,
    ) -> ModelPrediction:
        """
        Predict anomaly score for system monitoring.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Anomaly score prediction with full metadata
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        # Preprocess features
        processed_features, preprocessing_steps = self.preprocess_features(model_input.features)
        model_input.preprocessing_applied = preprocessing_steps

        # Extract features in correct order
        feature_vector = self._extract_feature_vector(processed_features)

        if feature_vector is None:
            # Failed to extract features
            return self.create_prediction(
                prediction=0.5,  # Neutral anomaly score
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # Isolation Forest prediction
            # Note: Isolation Forest returns -1 for anomalies, 1 for normal
            # We convert to anomaly score (0-1, where higher = more anomalous)
            raw_prediction = self.pipeline.predict(feature_vector.reshape(1, -1))[0]
            anomaly_score = self.pipeline.decision_function(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to normalized anomaly score (0-1)
            # Lower decision function values indicate more anomalous
            # We normalize to 0-1 where higher = more anomalous
            normalized_score = self._normalize_anomaly_score(anomaly_score)

            # Calculate confidence based on isolation depth
            confidence = self._calculate_anomaly_confidence(feature_vector, normalized_score)

            # Get feature contributions
            top_features = self.get_feature_importance(model_input)

            # Determine anomaly level
            anomaly_level = self._classify_anomaly_level(normalized_score)

            # Check thresholds
            threshold_used = self.threshold_config.get("anomaly_threshold", 0.1)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=normalized_score,
                    confidence=confidence,
                    threshold_used=threshold_used,
                ),
            )

            # Always operate in shadow or escalated mode for anomaly detection
            final_decision_mode = DecisionMode.SHADOW_ONLY
            if not passes_threshold or normalized_score > self.threshold_config.get(
                "high_anomaly_threshold", 0.05
            ):
                final_decision_mode = DecisionMode.ESCALATED

            # Create prediction
            prediction = self.create_prediction(
                prediction=normalized_score,
                confidence=confidence,
                top_features=top_features,
                threshold_used=threshold_used,
                decision_mode=final_decision_mode,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

            # Add prediction metadata
            prediction.model_metadata.update(
                {
                    "prediction_time_ms": prediction_time * 1000,
                    "feature_vector_length": len(feature_vector),
                    "preprocessing_steps": preprocessing_steps,
                    "raw_prediction": int(raw_prediction),
                    "anomaly_level": anomaly_level,
                    "is_anomaly": normalized_score > threshold_used,
                    "anomaly_indicators": self._get_anomaly_indicators(model_input.features),
                }
            )

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
            # Prediction failed
            return self.create_prediction(
                prediction=0.5,
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

    def detect_anomalies_batch(
        self,
        contexts: list[dict[str, Any]],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> list[dict[str, Any]]:
        """
        Detect anomalies in a batch of contexts.

        Args:
            contexts: List of contexts to analyze
            trace_id: Base trace ID
            replay_key: Replay key
            policy_hash: Policy hash

        Returns:
            List of anomaly detection results
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        # Extract features for all contexts
        batch_features = self.feature_extractor.extract_batch_features(
            contexts=contexts,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        # Detect anomalies for each context
        anomaly_results = []

        for i, (context, features) in tqdm(
            enumerate(zip(contexts, batch_features)), desc="Processing", unit="item"
        ):
            context_trace_id = f"{trace_id}_batch_{i}"

            # Validate input
            model_input = self.validate_input(features)

            # Make prediction
            prediction = self.predict(
                model_input=model_input,
                trace_id=context_trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

            # Get human-readable indicators
            indicators = self.feature_extractor.get_anomaly_indicators_summary(features)

            anomaly_results.append(
                {
                    "context_index": i,
                    "context": context,
                    "features": features,
                    "prediction": prediction,
                    "indicators": indicators,
                    "is_anomaly": prediction.prediction > self.threshold_config.get("anomaly_threshold", 0.1),
                    "anomaly_level": prediction.model_metadata.get("anomaly_level", "normal"),
                }
            )

        return anomaly_results

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        if not self.is_loaded or not self.feature_names:
            return []

        try:
            # For Isolation Forest, we can analyze feature contributions
            # by examining how each feature affects the isolation score

            feature_vector = self._extract_feature_vector(model_input.features)
            if feature_vector is None:
                return []

            # Get base anomaly score
            base_score = self.pipeline.decision_function(feature_vector.reshape(1, -1))[0]

            # Calculate feature contributions by perturbation
            contributions = []

            for i, feature_name in tqdm(enumerate(self.feature_names), desc="Processing", unit="item"):
                if i < len(feature_vector):
                    # Create perturbed feature vector
                    perturbed_vector = feature_vector.copy()
                    perturbed_vector[i] = 0.0  # Zero out this feature

                    # Calculate new score
                    perturbed_score = self.pipeline.decision_function(perturbed_vector.reshape(1, -1))[0]

                    # Contribution is the difference in scores
                    contribution = abs(base_score - perturbed_score)

                    contributions.append(
                        {
                            "feature_name": feature_name,
                            "contribution_score": float(contribution),
                            "feature_value": model_input.features.get(feature_name),
                            "base_score": float(base_score),
                            "perturbed_score": float(perturbed_score),
                            "rank": 0,  # Will be set after sorting
                        }
                    )

            # Sort by contribution
            contributions.sort(key=lambda x: x["contribution_score"], reverse=True)

            # Update ranks
            for i, contrib in enumerate(contributions):
                contrib["rank"] = i + 1

            # Return top 10 features
            return contributions[:10]

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
            # Failed to compute importance
            return []

    def _extract_feature_vector(self, features: dict[str, Any]) -> np.ndarray | None:
        """Extract features in the correct order for the model."""
        if not self.feature_names:
            return None

        try:
            feature_vector = []
            for feature_name in tqdm(self.feature_names, desc="Processing", unit="item"):
                value = features.get(feature_name, 0.0)  # Default to 0 if missing

                # Convert to numeric
                if isinstance(value, str):
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0.0

                feature_vector.append(float(value))

            return np.array(feature_vector)

        except (
            TypeError,
            ValueError,
        ) as _fe:  # guardian: allow-return-none-swallow -- _extract_feature_vector: Optional return by contract, callers explicitly handle None, warning now logged
            logging.getLogger(__name__).warning("Feature vector construction failed: %s", _fe)
            return None

    def _normalize_anomaly_score(self, raw_score: float) -> float:
        """Normalize raw anomaly score to 0-1 range."""
        # Isolation Forest decision_function returns values where
        # lower values indicate more anomalous
        # We normalize to 0-1 where higher = more anomalous

        # Simple normalization using sigmoid function
        # This maps negative values (anomalies) to higher scores
        normalized = 1.0 / (1.0 + np.exp(raw_score))

        return float(np.clip(normalized, 0.0, 1.0))

    def _calculate_anomaly_confidence(self, feature_vector: np.ndarray, anomaly_score: float) -> float:
        """Calculate confidence score for anomaly prediction."""
        # For anomaly detection, confidence is based on:
        # 1. How extreme the anomaly score is
        # 2. Feature vector characteristics
        # 3. Model certainty (isolation depth)

        # Base confidence from anomaly score
        if anomaly_score > 0.8:
            base_confidence = 0.9  # High confidence for strong anomalies
        elif anomaly_score > 0.6:
            base_confidence = 0.7  # Medium confidence for moderate anomalies
        elif anomaly_score < 0.2:
            base_confidence = 0.8  # High confidence for normal behavior
        else:
            base_confidence = 0.5  # Lower confidence for ambiguous cases

        # Adjust based on feature vector completeness
        non_zero_features = np.count_nonzero(feature_vector)
        completeness_factor = min(0.1, non_zero_features / len(feature_vector) * 0.1)

        # Adjust based on feature variance
        feature_variance = np.var(feature_vector)
        variance_factor = min(0.1, feature_variance / 10.0)

        confidence = base_confidence + completeness_factor + variance_factor
        return round(min(1.0, max(0.0, confidence)), 3)

    def _classify_anomaly_level(self, anomaly_score: float) -> str:
        """Classify anomaly level based on score."""
        if anomaly_score > self.threshold_config.get("critical_anomaly_threshold", 0.02):
            return "critical"
        elif anomaly_score > self.threshold_config.get("high_anomaly_threshold", 0.05):
            return "high"
        elif anomaly_score > self.threshold_config.get("anomaly_threshold", 0.1):
            return "moderate"
        else:
            return "normal"

    def _get_anomaly_indicators(self, features: dict[str, Any]) -> list[str]:
        """Get specific anomaly indicators from features."""
        indicators = []

        # Check each feature for anomalous values
        feature_thresholds = {
            "latency_z_score": 2.0,
            "error_rate_spike": 2.0,
            "token_deviation": 0.5,
            "path_divergence": 0.3,
            "policy_hash_changes": 5.0,
            "replay_mismatch_count": 10.0,
            "escalation_frequency": 5.0,
            "healing_success_rate": 0.5,
            "semantic_drift_score": 0.2,
        }

        for feature_name, threshold in tqdm(feature_thresholds.items(), desc="Processing", unit="item"):
            value = features.get(feature_name, 0.0)

            if feature_name == "healing_success_rate":
                # Lower is worse for success rate
                if value < threshold:
                    indicators.append(f"Low {feature_name.replace('_', ' ')}")
            else:
                # Higher is worse for other features
                if value > threshold:
                    indicators.append(f"High {feature_name.replace('_', ' ')}")

        return indicators

    def _get_model_params(self) -> dict[str, Any]:
        """Get Isolation Forest parameters."""
        if self.pipeline and hasattr(self.pipeline, "named_steps"):
            isolation_forest = self.pipeline.named_steps.get("isolation_forest")
            if isolation_forest:
                return {
                    "n_estimators": isolation_forest.n_estimators,
                    "max_samples": isolation_forest.max_samples,
                    "contamination": isolation_forest.contamination,
                    "max_features": isolation_forest.max_features,
                    "random_state": isolation_forest.random_state,
                }
        return {}

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for Isolation Forest."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for Isolation Forest
        for key, value in tqdm(processed_features.items(), desc="Processing", unit="item"):
            # Ensure all features are numeric
            if isinstance(value, str):
                try:
                    processed_features[key] = float(value)
                    preprocessing_steps.append(f"string_to_numeric_{key}")
                except ValueError:
                    processed_features[key] = 0.0
                    preprocessing_steps.append(f"string_to_default_{key}")
            elif not isinstance(value, (int, float)):
                processed_features[key] = 0.0
                preprocessing_steps.append(f"non_numeric_to_default_{key}")

        return processed_features, preprocessing_steps

    def train_model(
        self,
        training_data: list[dict[str, Any]],
        feature_names: list[str],
        training_data_digest: str = "",
        contamination: float = 0.1,
        n_estimators: int = 100,
    ) -> None:
        """
        Train the Isolation Forest model.

        Args:
            training_data: List of training examples with features
            feature_names: Names of features to use
            training_data_digest: Digest of training data for provenance
            contamination: Expected contamination rate
            n_estimators: Number of estimators
        """
        # Extract features
        X = []

        for example in training_data:
            features = example["features"]

            feature_vector = []
            for feature_name in feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            X.append(feature_vector)

        X = np.array(X)

        # Create pipeline with scaling and isolation forest
        self.pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "isolation_forest",
                    IsolationForest(
                        n_estimators=n_estimators,
                        contamination=contamination,
                        max_features=1.0,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        )

        # Train model
        self.pipeline.fit(X)

        # Store feature names and parameters
        self.feature_names = feature_names
        self.contamination_rate = contamination

        # Store training digest
        self._training_data_digest = training_data_digest

        self.is_loaded = True

    def predict_from_context(
        self,
        context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.SHADOW_ONLY,
    ) -> ModelPrediction:
        """
        Predict anomaly from context (convenience method).

        Args:
            context: System monitoring context
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Anomaly score prediction
        """
        # Extract features
        extraction_result = self.feature_extractor.extract_features(
            context=context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        if not extraction_result.success:
            # Feature extraction failed
            return self.create_prediction(
                prediction=0.5,
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        # Validate input
        model_input = self.validate_input(extraction_result.features)
        model_input.feature_provenance = extraction_result.provenance

        # Make prediction
        return self.predict(
            model_input=model_input,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
            decision_mode=decision_mode,
        )
