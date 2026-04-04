"""
L0 Route Recommender

Logistic regression model for recommending optimal routing paths
(Basic, Standard, Advanced, Expert) based on request characteristics,
user context, and system state.
"""

import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ..config.model_registry import DecisionMode
from ..features.l0_features import L0FeatureExtractor
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType


class L0RouteRecommender(BaseMLModel):
    """
    Logistic regression model for L0 route recommendation.

    Recommends optimal routing paths (A=Basic, B=Standard, C=Advanced, D=Expert)
    based on:
    - Request complexity (tokens, tools, latency budget)
    - User confidence and preferences
    - System load and availability
    - Historical success patterns
    - Semantic similarity to past requests

    Always operates in advisory mode - L0 retains final routing authority.
    """

    # Path mapping
    PATH_MAPPING = {
        0: "Path_A",  # Basic - simple requests
        1: "Path_B",  # Standard - moderate complexity
        2: "Path_C",  # Advanced - high complexity
        3: "Path_D"   # Expert - maximum complexity/escalation
    }

    # Reverse mapping
    REVERSE_PATH_MAPPING = {v: k for k, v in PATH_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        super().__init__(
            model_name="l0_route_recommender",
            model_version="1.0",
            model_type="logistic_regression",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path
        )

        # Initialize feature extractor
        self.feature_extractor = L0FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.pipeline = None
        self.feature_names = None
        self.class_names = list(self.PATH_MAPPING.values())

        # Default thresholds
        self.threshold_config = {
            "confidence_threshold": 0.7,
            "min_class_probability": 0.3,
            "escalation_threshold": 0.8
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the logistic regression model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            with open(self.model_file_path, 'rb') as f:
                model_data = pickle.load(f)

            self.pipeline = model_data.get('pipeline')
            self.feature_names = model_data.get('feature_names', [])
            self.threshold_config = model_data.get('threshold_config', self.threshold_config)
            self._training_data_digest = model_data.get('training_data_digest', '')

            self.is_loaded = True

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def save_model(self, model_file_path: Path) -> None:
        """Save the model to file."""
        model_data = {
            'pipeline': self.pipeline,
            'feature_names': self.feature_names,
            'threshold_config': self.threshold_config,
            'training_data_digest': getattr(self, '_training_data_digest', ''),
            'model_metadata': {
                'model_name': self.model_name,
                'model_version': self.model_version,
                'model_type': self.model_type,
                'prediction_type': self.prediction_type.value,
                'class_names': self.class_names,
                'feature_schema_digest': self.feature_schema.schema_digest,
                'saved_at': datetime.now().isoformat()
            }
        }

        with open(model_file_path, 'wb') as f:
            pickle.dump(model_data, f)

    def predict(
        self,
        model_input: ModelInput,
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.ADVISORY
    ) -> ModelPrediction:
        """
        Make routing recommendation with full governance compliance.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Route recommendation with full metadata
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
                prediction="Path_A",  # Default fallback
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # Get prediction probabilities
            probabilities = self.pipeline.predict_proba(feature_vector.reshape(1, -1))[0]
            predicted_class = self.pipeline.predict(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to path name
            predicted_path = self.PATH_MAPPING.get(predicted_class, "Path_A")

            # Create probability distribution
            prob_distribution = {
                self.class_names[i]: float(prob)
                for i, prob in enumerate(probabilities)
            }

            # Calculate confidence (max probability)
            confidence = float(np.max(probabilities))

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("confidence_threshold", 0.7)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_path,
                    confidence=confidence,
                    probability_distribution=prob_distribution,
                    threshold_used=threshold_used
                )
            )

            # Determine final decision mode based on thresholds
            final_decision_mode = decision_mode
            if not passes_threshold:
                final_decision_mode = DecisionMode.ESCALATED

            # Create prediction
            prediction = self.create_prediction(
                prediction=predicted_path,
                confidence=confidence,
                probability_distribution=prob_distribution,
                top_features=top_features,
                threshold_used=threshold_used,
                decision_mode=final_decision_mode,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

            # Add prediction metadata
            prediction.model_metadata.update({
                'prediction_time_ms': prediction_time * 1000,
                'feature_vector_length': len(feature_vector),
                'preprocessing_steps': preprocessing_steps,
                'raw_prediction_class': int(predicted_class),
                'class_probabilities': [float(p) for p in probabilities],
                'thresholds_passed': passes_threshold
            })

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except Exception as e:
            # Prediction failed
            return self.create_prediction(
                prediction="Path_A",  # Safe fallback
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        if not self.is_loaded or not self.pipeline:
            return []

        try:
            # Get coefficients from logistic regression
            logistic_model = self.pipeline.named_steps['classifier']
            coefficients = logistic_model.coef_[0]  # First class for multiclass

            # Get feature names
            feature_names = self.feature_names or list(model_input.features.keys())

            # Calculate absolute importance (average across classes for multiclass)
            if len(coefficients.shape) > 1:
                # Multiclass - average absolute coefficients
                importance_scores = np.mean(np.abs(logistic_model.coef_), axis=0)
            else:
                # Binary classification
                importance_scores = np.abs(coefficients)

            # Create feature importance list
            feature_importance = []
            for i, (name, score) in enumerate(zip(feature_names, importance_scores)):
                if i < len(score):  # Ensure index is valid
                    feature_importance.append({
                        'feature_name': name,
                        'importance_score': float(score),
                        'coefficient_value': float(coefficients[i]) if i < len(coefficients) else 0.0,
                        'feature_value': model_input.features.get(name),
                        'rank': i + 1
                    })

            # Sort by importance
            feature_importance.sort(key=lambda x: x['importance_score'], reverse=True)

            # Update ranks
            for i, feature in enumerate(feature_importance):
                feature['rank'] = i + 1

            # Return top 10 features
            return feature_importance[:10]

        except Exception as e:
            # Failed to compute importance
            return []

    def _extract_feature_vector(self, features: dict[str, Any]) -> np.ndarray | None:
        """Extract features in the correct order for the model."""
        if not self.feature_names:
            return None

        try:
            feature_vector = []
            for feature_name in self.feature_names:
                value = features.get(feature_name, 0.0)  # Default to 0 if missing

                # Convert to numeric
                if isinstance(value, str):
                    if value.replace('.', '').isdigit():
                        value = float(value)
                    else:
                        # Handle categorical variables
                        value = 0.0  # Default for unknown categories

                feature_vector.append(float(value))

            return np.array(feature_vector)

        except Exception as e:
            return None

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for logistic regression."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for logistic regression
        for key, value in processed_features.items():
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
        training_data_digest: str = ""
    ) -> None:
        """
        Train the logistic regression model.

        Args:
            training_data: List of training examples with features and labels
            feature_names: Names of features to use
            training_data_digest: Digest of training data for provenance
        """
        # Extract features and labels
        X = []
        y = []

        for example in training_data:
            features = example['features']
            label = example['label']

            # Convert path name to class index
            if isinstance(label, str):
                label = self.REVERSE_PATH_MAPPING.get(label, 0)

            feature_vector = []
            for feature_name in feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            X.append(feature_vector)
            y.append(int(label))

        X = np.array(X)
        y = np.array(y)

        # Create pipeline with scaling and logistic regression
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(
                multi_class='multinomial',
                solver='lbfgs',
                max_iter=1000,
                random_state=42
            ))
        ])

        # Train model
        self.pipeline.fit(X, y)

        # Store feature names and training digest
        self.feature_names = feature_names
        self._training_data_digest = training_data_digest

        self.is_loaded = True

    def predict_from_context(
        self,
        context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.ADVISORY
    ) -> ModelPrediction:
        """
        Predict directly from context (convenience method).

        Args:
            context: Input context
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Route recommendation
        """
        # Extract features
        extraction_result = self.feature_extractor.extract_features(
            context=context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash
        )

        if not extraction_result.success:
            # Feature extraction failed
            return self.create_prediction(
                prediction="Path_A",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
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
            decision_mode=decision_mode
        )

    def get_path_recommendations_with_confidence(
        self,
        context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str
    ) -> dict[str, float]:
        """
        Get all path recommendations with confidence scores.

        Args:
            context: Input context
            trace_id: Trace ID
            replay_key: Replay key
            policy_hash: Policy hash

        Returns:
            Dictionary mapping path names to confidence scores
        """
        prediction = self.predict_from_context(
            context=context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash
        )

        if prediction.probability_distribution:
            return prediction.probability_distribution
        else:
            # Fallback: return equal probabilities
            return dict.fromkeys(self.class_names, 0.25)
