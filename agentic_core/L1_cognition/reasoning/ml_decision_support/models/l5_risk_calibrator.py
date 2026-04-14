"""
L5 Risk Calibrator

XGBoost model for calibrating risk levels for policy decisions,
balancing compliance requirements with business impact and operational efficiency.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

try:
    import xgboost as xgb
except ImportError:
    xgb = None

from ..config.model_registry import DecisionMode
from ..features.l5_features import L5FeatureExtractor
from ._pickle_io import safe_pickle_dump, safe_pickle_load
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType
from tqdm import tqdm


class L5RiskCalibrator(BaseMLModel):
    """
    XGBoost model for L5 risk calibration.

    Calibrates risk levels based on:
    - Policy complexity and compliance requirements
    - Historical false positive/negative rates
    - Business impact and stakeholder criticality
    - Audit requirements and regulatory change frequency
    - Risk mitigation effectiveness and precedent strength

    Always operates in advisory mode - L5 retains final policy certification authority.
    """

    # Risk level mapping
    RISK_MAPPING = {
        0: "Low",
        1: "Medium",
        2: "High",
        3: "Critical",
    }

    # Reverse mapping
    REVERSE_RISK_MAPPING = {v: k for k, v in RISK_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        if xgb is None:
            raise ImportError("XGBoost is required for L5RiskCalibrator")

        super().__init__(
            model_name="l5_risk_calibrator",
            model_version="1.0",
            model_type="xgboost",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path,
        )

        # Initialize feature extractor
        self.feature_extractor = L5FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.model = None
        self.feature_names = None
        self.feature_importances = None
        self.class_names = list(self.RISK_MAPPING.values())

        # Default thresholds
        self.threshold_config = {
            "confidence_threshold": 0.7,
            "high_risk_threshold": 0.8,
            "critical_risk_threshold": 0.9,
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the XGBoost model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            model_data = safe_pickle_load(self.model_file_path)

            self.model = model_data.get("model")
            self.feature_names = model_data.get("feature_names", [])
            self.feature_importances = model_data.get("feature_importances", [])
            self.threshold_config = model_data.get("threshold_config", self.threshold_config)
            self._training_data_digest = model_data.get("training_data_digest", "")

            if self.model is None:
                raise ValueError("No model found in saved file")

            self.is_loaded = True

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def save_model(self, model_file_path: Path) -> None:
        """Save the model to file."""
        if self.model is None:
            raise RuntimeError("No model to save")

        model_data = {
            "model": self.model,
            "feature_names": self.feature_names,
            "feature_importances": self.feature_importances,
            "threshold_config": self.threshold_config,
            "training_data_digest": getattr(self, "_training_data_digest", ""),
            "model_metadata": {
                "model_name": self.model_name,
                "model_version": self.model_version,
                "model_type": self.model_type,
                "prediction_type": self.prediction_type.value,
                "class_names": self.class_names,
                "feature_schema_digest": self.feature_schema.schema_digest,
                "saved_at": datetime.now().isoformat(),
                "xgboost_params": getattr(self.model, "params", {}),
            },
        }

        safe_pickle_dump(model_data, model_file_path)

    def predict(
        self,
        model_input: ModelInput,
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.ADVISORY,
    ) -> ModelPrediction:
        """
        Predict risk level for policy certification.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Risk level prediction with full metadata
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
                prediction="Medium",  # Default risk level
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # XGBoost prediction
            probabilities = self.model.predict_proba(feature_vector.reshape(1, -1))[0]
            predicted_class = self.model.predict(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to risk level name
            predicted_risk = self.RISK_MAPPING.get(int(predicted_class), "Medium")

            # Create probability distribution
            prob_distribution = {self.class_names[i]: float(prob) for i, prob in enumerate(probabilities)}

            # Calculate confidence (max probability)
            confidence = float(np.max(probabilities))

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("confidence_threshold", 0.7)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_risk,
                    confidence=confidence,
                    probability_distribution=prob_distribution,
                    threshold_used=threshold_used,
                ),
            )

            # Determine final decision mode based on risk level
            final_decision_mode = decision_mode
            if not passes_threshold:
                final_decision_mode = DecisionMode.ESCALATED
            elif predicted_risk in ["High", "Critical"]:
                final_decision_mode = DecisionMode.ESCALATED

            # Create prediction
            prediction = self.create_prediction(
                prediction=predicted_risk,
                confidence=confidence,
                probability_distribution=prob_distribution,
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
                    "raw_prediction_class": int(predicted_class),
                    "class_probabilities": [float(p) for p in probabilities],
                    "thresholds_passed": passes_threshold,
                    "risk_level": predicted_risk,
                    "requires_escalation": predicted_risk in ["High", "Critical"],
                }
            )

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except Exception as e:
            # Prediction failed
            return self.create_prediction(
                prediction="Medium",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

    def calibrate_policy_risk(
        self,
        policy: dict[str, Any],
        context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> ModelPrediction:
        """
        Calibrate risk level for a specific policy.

        Args:
            policy: Policy to evaluate
            context: Additional context for evaluation
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Risk level calibration with full analysis
        """
        # Create evaluation context
        evaluation_context = {
            "policy": policy,
            "regulations": context.get("regulations", {}),
            "history": context.get("history", {}),
            "environment": context.get("environment", {}),
            "trace_id": trace_id,
        }

        # Extract features
        extraction_result = self.feature_extractor.extract_features(
            context=evaluation_context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        if not extraction_result.success:
            # Feature extraction failed
            return self.create_prediction(
                prediction="Medium",
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
        )

    def get_risk_recommendations(
        self,
        policy: dict[str, Any],
        context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Get comprehensive risk recommendations for policy decisions.

        Args:
            policy: Policy to evaluate
            context: Evaluation context
            trace_id: Trace ID
            replay_key: Replay key
            policy_hash: Policy hash

        Returns:
            Comprehensive risk analysis and recommendations
        """
        # Get base risk calibration
        prediction = self.calibrate_policy_risk(
            policy=policy,
            context=context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        # Extract features for analysis
        evaluation_context = {
            "policy": policy,
            "regulations": context.get("regulations", {}),
            "history": context.get("history", {}),
            "environment": context.get("environment", {}),
            "trace_id": trace_id,
        }

        extraction_result = self.feature_extractor.extract_features(
            context=evaluation_context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        # Generate recommendations based on risk level and features
        recommendations = self._generate_risk_recommendations(
            prediction=prediction,
            features=extraction_result.features if extraction_result.success else {},
            policy=policy,
        )

        return {
            "risk_level": prediction.prediction,
            "confidence": prediction.confidence,
            "probability_distribution": prediction.probability_distribution,
            "top_risk_factors": prediction.top_features,
            "recommendations": recommendations,
            "requires_additional_review": prediction.prediction in ["High", "Critical"],
            "escalation_required": prediction.decision_mode == DecisionMode.ESCALATED,
            "prediction_metadata": prediction.model_metadata,
        }

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        if not self.is_loaded or not self.feature_importances:
            return []

        try:
            # Get feature names
            feature_names = self.feature_names or list(model_input.features.keys())

            # Create feature importance list
            feature_importance = []
            for i, (name, importance) in tqdm(
                enumerate(zip(feature_names, self.feature_importances)), desc="Processing", unit="item"
            ):
                feature_importance.append(
                    {
                        "feature_name": name,
                        "importance_score": float(importance),
                        "feature_value": model_input.features.get(name),
                        "rank": i + 1,
                        "relative_importance": float(importance / max(self.feature_importances))
                        if max(self.feature_importances) > 0
                        else 0.0,
                    }
                )

            # Sort by importance
            feature_importance.sort(key=lambda x: x["importance_score"], reverse=True)

            # Update ranks
            for i, feature in enumerate(feature_importance):
                feature["rank"] = i + 1

            # Return top 10 features
            return feature_importance[:10]

        except Exception as e:
            # Failed to compute importance
            return []

    def _generate_risk_recommendations(
        self,
        prediction: ModelPrediction,
        features: dict[str, Any],
        policy: dict[str, Any],
    ) -> list[str]:
        """Generate risk-based recommendations."""
        recommendations = []
        risk_level = prediction.prediction

        # Base recommendations by risk level
        if risk_level == "Critical":
            recommendations.extend(
                [
                    "Immediate executive review required",
                    "Implement additional risk mitigations before approval",
                    "Consider policy redesign to reduce risk exposure",
                    "Document comprehensive risk assessment and mitigation plan",
                ]
            )
        elif risk_level == "High":
            recommendations.extend(
                [
                    "Senior management review required",
                    "Additional compliance checks needed",
                    "Implement monitoring and reporting requirements",
                    "Consider phased implementation approach",
                ]
            )
        elif risk_level == "Medium":
            recommendations.extend(
                [
                    "Standard review process sufficient",
                    "Implement basic monitoring requirements",
                    "Document risk assessment findings",
                ]
            )
        else:  # Low
            recommendations.extend(
                [
                    "Standard approval process appropriate",
                    "Minimal additional controls required",
                    "Proceed with normal implementation",
                ]
            )

        # Feature-specific recommendations
        if features.get("policy_complexity_score", 0) > 0.7:
            recommendations.append("Consider simplifying policy structure to reduce complexity")

        if features.get("compliance_risk_level", 0) > 0.6:
            recommendations.append("Engage legal/compliance teams for detailed review")

        if features.get("business_impact_score", 0) > 0.8:
            recommendations.append("Develop comprehensive business impact assessment")

        if features.get("historical_false_positive_rate", 0) > 0.3:
            recommendations.append("Review and refine policy criteria to reduce false positives")

        if features.get("historical_false_negative_rate", 0) > 0.2:
            recommendations.append("Strengthen policy coverage to reduce false negatives")

        if features.get("audit_requirement_level", 0) > 0.7:
            recommendations.append("Prepare comprehensive audit documentation and procedures")

        return recommendations

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

        except Exception as e:
            return None

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for XGBoost."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for XGBoost
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
        xgb_params: dict[str, Any] | None = None,
    ) -> None:
        """
        Train the XGBoost model.

        Args:
            training_data: List of training examples with features and labels
            feature_names: Names of features to use
            training_data_digest: Digest of training data for provenance
            xgb_params: XGBoost hyperparameters
        """
        # Extract features and labels
        X = []
        y = []

        for example in tqdm(training_data, desc="Processing", unit="item"):
            features = example["features"]
            label = example["label"]

            # Convert risk level string to class index
            if isinstance(label, str):
                label = self.REVERSE_RISK_MAPPING.get(label, 1)  # Default to Medium
            else:
                label = int(label)

            feature_vector = []
            for feature_name in feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            X.append(feature_vector)
            y.append(label)

        X = np.array(X)
        y = np.array(y)

        # Default XGBoost parameters
        default_params = {
            "objective": "multi:softprob",
            "num_class": 4,  # Low, Medium, High, Critical
            "eval_metric": "mlogloss",
            "max_depth": 6,
            "learning_rate": 0.1,
            "n_estimators": 100,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
        }

        # Merge with provided parameters
        params = {**default_params, **(xgb_params or {})}

        # Train model
        self.model = xgb.XGBClassifier(**params)
        self.model.fit(X, y)

        # Store feature names and importance
        self.feature_names = feature_names
        self.feature_importances = self.model.feature_importances_

        # Store training digest
        self._training_data_digest = training_data_digest

        self.is_loaded = True
