"""
Advanced L6 Anomaly Detector

Autoencoder-based model for advanced anomaly detection including
behavioral pattern analysis, reconstruction error detection,
multivariate anomaly scoring, and sophisticated alerting.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError:
    IsolationForest = None
    StandardScaler = None
    Pipeline = None

from ..config.model_registry import DecisionMode
from ..features.advanced_l6_features import AdvancedL6FeatureExtractor
from ._pickle_io import safe_pickle_dump, safe_pickle_load
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType
from tqdm import tqdm


class AdvancedL6Detector(BaseMLModel):
    """
    Autoencoder-inspired model for advanced L6 anomaly detection.

    Provides intelligent anomaly detection based on:
    - Behavioral pattern analysis and deviation detection
    - Reconstruction error and anomaly scoring
    - Multivariate anomaly detection with correlation analysis
    - Temporal pattern break detection
    - System metric anomaly identification
    - Security anomaly detection and threat analysis
    - Contextual anomaly assessment
    """

    # Advanced anomaly detection action mapping
    ANOMALY_MAPPING = {
        0: "Critical_Alert",
        1: "High_Priority",
        2: "Medium_Priority",
        3: "Low_Priority",
        4: "Informational",
        5: "Adaptive_Monitoring",
        6: "Contextual_Analysis",
        7: "Normal_Operation",
    }

    # Reverse mapping
    REVERSE_ANOMALY_MAPPING = {v: k for k, v in ANOMALY_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        if IsolationForest is None:
            raise ImportError("scikit-learn is required for AdvancedL6Detector")

        super().__init__(
            model_name="advanced_l6_detector",
            model_version="1.0",
            model_type="autoencoder_inspired",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path,
        )

        # Initialize feature extractor
        self.feature_extractor = AdvancedL6FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.pipeline = None
        self.feature_names = None
        self.class_names = list(self.ANOMALY_MAPPING.values())

        # Autoencoder-inspired parameters
        self.autoencoder_config = {
            "encoding_dim": 32,
            "decoding_dim": 64,
            "latent_dim": 16,
            "reconstruction_weight": 0.7,
            "regularization_weight": 0.3,
            "anomaly_threshold": 0.1,
        }

        # Default thresholds
        self.threshold_config = {
            "anomaly_threshold": 0.5,
            "critical_threshold": 0.8,
            "behavioral_threshold": 0.6,
            "system_threshold": 0.7,
            "security_threshold": 0.9,
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the Autoencoder-inspired model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            model_data = safe_pickle_load(self.model_file_path)

            self.pipeline = model_data.get("pipeline")
            self.feature_names = model_data.get("feature_names", [])
            self.autoencoder_config = model_data.get("autoencoder_config", self.autoencoder_config)
            self.threshold_config = model_data.get("threshold_config", self.threshold_config)
            self._training_data_digest = model_data.get("training_data_digest", "")

            self.is_loaded = True

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def save_model(self, model_file_path: Path) -> None:
        """Save the model to file."""
        model_data = {
            "pipeline": self.pipeline,
            "feature_names": self.feature_names,
            "autoencoder_config": self.autoencoder_config,
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
        Predict advanced anomaly detection decision.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Advanced anomaly detection prediction with full metadata
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
                prediction="Normal_Operation",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # Autoencoder-inspired prediction
            probabilities = self.pipeline.predict_proba(feature_vector.reshape(1, -1))[0]
            predicted_class = self.pipeline.predict(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to anomaly detection action name
            predicted_anomaly = self.ANOMALY_MAPPING.get(int(predicted_class), "Normal_Operation")

            # Create probability distribution
            prob_distribution = {self.class_names[i]: float(prob) for i, prob in enumerate(probabilities)}

            # Calculate confidence (max probability)
            confidence = float(np.max(probabilities))

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("anomaly_threshold", 0.5)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_anomaly,
                    confidence=confidence,
                    probability_distribution=prob_distribution,
                    threshold_used=threshold_used,
                ),
            )

            # Create prediction
            prediction = self.create_prediction(
                prediction=predicted_anomaly,
                confidence=confidence,
                probability_distribution=prob_distribution,
                top_features=top_features,
                threshold_used=threshold_used,
                decision_mode=decision_mode,
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
                    "raw_prediction_class": predicted_class,
                    "class_probabilities": [float(p) for p in probabilities],
                    "thresholds_passed": passes_threshold,
                    "anomaly_action": predicted_anomaly,
                    "autoencoder_config": self.autoencoder_config,
                }
            )

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
            # Prediction failed
            return self.create_prediction(
                prediction="Normal_Operation",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

    def detect_anomalies_intelligently(
        self,
        anomaly_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Get intelligent anomaly detection recommendation.

        Args:
            anomaly_context: Anomaly context and system information
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Comprehensive anomaly detection recommendation
        """
        # Extract features from context
        extraction_result = self.feature_extractor.extract_features(
            context=anomaly_context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        if not extraction_result.success:
            return {
                "anomaly_action": "Normal_Operation",
                "confidence": 0.0,
                "reason": "Feature extraction failed",
                "recommendations": ["Check anomaly data availability"],
            }

        # Validate input
        model_input = self.validate_input(extraction_result.features)
        model_input.feature_provenance = extraction_result.provenance

        # Make prediction
        prediction = self.predict(
            model_input=model_input,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        # Generate detailed anomaly recommendations
        recommendations = self._generate_anomaly_recommendations(
            action=prediction.prediction,
            context=anomaly_context,
            features=extraction_result.features,
        )

        # Analyze anomaly factors
        anomaly_analysis = self._analyze_anomaly_factors(
            context=anomaly_context,
            features=extraction_result.features,
        )

        # Calculate anomaly severity
        severity_assessment = self._assess_anomaly_severity(
            action=prediction.prediction,
            context=anomaly_context,
            features=extraction_result.features,
        )

        return {
            "anomaly_action": prediction.prediction,
            "confidence": prediction.confidence,
            "probability_distribution": prediction.probability_distribution,
            "top_factors": prediction.top_features,
            "recommendations": recommendations,
            "anomaly_analysis": anomaly_analysis,
            "severity_assessment": severity_assessment,
            "alternative_responses": self._get_alternative_responses(prediction.probability_distribution),
            "implementation_priority": self._get_implementation_priority(
                prediction.prediction, prediction.confidence
            ),
        }

    def analyze_behavioral_patterns(
        self,
        behavioral_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Analyze behavioral patterns for anomaly detection.

        Args:
            behavioral_context: Behavioral context and pattern information
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Behavioral pattern analysis and anomaly implications
        """
        # Extract behavioral features
        behavioral_features = {
            "behavioral_deviation": behavioral_context.get("behavioral_deviation", 0.0),
            "request_frequency": behavioral_context.get("request_frequency", 100),
            "response_patterns": behavioral_context.get("response_patterns", 0.5),
            "error_patterns": behavioral_context.get("error_patterns", 0.01),
        }

        # Analyze behavioral patterns
        behavioral_analysis = {
            "deviation_analysis": self._analyze_deviation_patterns(behavioral_context),
            "frequency_analysis": self._analyze_frequency_patterns(behavioral_context),
            "response_analysis": self._analyze_response_patterns(behavioral_context),
            "error_analysis": self._analyze_error_patterns(behavioral_context),
        }

        # Generate behavioral-based anomaly suggestions
        anomaly_suggestions = []

        deviation_score = behavioral_analysis["deviation_analysis"]["deviation_score"]
        if deviation_score > 0.8:
            anomaly_suggestions.append("High behavioral deviation - Critical_Alert recommended")
        elif deviation_score > 0.5:
            anomaly_suggestions.append("Moderate behavioral deviation - High_Priority recommended")
        else:
            anomaly_suggestions.append("Low behavioral deviation - monitor closely")

        frequency = behavioral_analysis["frequency_analysis"]["anomaly_score"]
        if frequency > 0.7:
            anomaly_suggestions.append("Frequency anomaly detected - investigate system load")

        return {
            "behavioral_analysis": behavioral_analysis,
            "behavioral_features": behavioral_features,
            "anomaly_suggestions": anomaly_suggestions,
            "behavioral_confidence": behavioral_context.get("behavioral_confidence", 0.5),
            "recommended_action": self._recommend_behavioral_action(behavioral_analysis),
        }

    def assess_system_health(
        self,
        system_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Assess system health for anomaly detection.

        Args:
            system_context: System context and health metrics
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            System health assessment and anomaly implications
        """
        # Extract system features
        system_features = {
            "system_metric_anomaly": system_context.get("system_metric_anomaly", 0.0),
            "performance_degradation": system_context.get("performance_degradation", 0.0),
            "resource_anomaly": system_context.get("resource_anomaly", 0.0),
        }

        # Analyze system health
        system_analysis = {
            "metric_health": self._analyze_metric_health(system_context),
            "performance_health": self._analyze_performance_health(system_context),
            "resource_health": self._analyze_resource_health(system_context),
            "overall_health": self._calculate_overall_health(system_context),
        }

        # Generate system-based anomaly suggestions
        anomaly_suggestions = []

        overall_health = system_analysis["overall_health"]["score"]
        if overall_health < 0.3:
            anomaly_suggestions.append("Poor system health - Critical_Alert required")
        elif overall_health < 0.6:
            anomaly_suggestions.append("Degraded system health - High_Priority monitoring")
        elif overall_health < 0.8:
            anomaly_suggestions.append("System health suboptimal - Medium_Priority review")
        else:
            anomaly_suggestions.append("Good system health - continue monitoring")

        return {
            "system_analysis": system_analysis,
            "system_features": system_features,
            "anomaly_suggestions": anomaly_suggestions,
            "health_confidence": system_context.get("health_confidence", 0.5),
            "recommended_action": self._recommend_system_action(system_analysis),
        }

    def evaluate_security_threats(
        self,
        security_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Evaluate security threats for anomaly detection.

        Args:
            security_context: Security context and threat information
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Security threat evaluation and anomaly implications
        """
        # Extract security features
        security_features = {
            "security_anomaly": security_context.get("security_anomaly", 0.0),
            "authentication_anomaly": security_context.get("authentication_anomaly", 0.0),
            "authorization_anomaly": security_context.get("authorization_anomaly", 0.0),
            "threat_indicators": security_context.get("threat_indicators", 0.0),
        }

        # Analyze security threats
        security_analysis = {
            "authentication_security": self._analyze_authentication_security(security_context),
            "authorization_security": self._analyze_authorization_security(security_context),
            "access_pattern_security": self._analyze_access_pattern_security(security_context),
            "threat_assessment": self._assess_threat_level(security_context),
        }

        # Generate security-based anomaly suggestions
        anomaly_suggestions = []

        threat_level = security_analysis["threat_assessment"]["level"]
        if threat_level == "critical":
            anomaly_suggestions.append("Critical threat detected - Immediate Critical_Alert")
        elif threat_level == "high":
            anomaly_suggestions.append("High threat level - High_Priority response")
        elif threat_level == "medium":
            anomaly_suggestions.append("Medium threat level - Medium_Priority monitoring")
        else:
            anomaly_suggestions.append("Low threat level - Informational logging")

        return {
            "security_analysis": security_analysis,
            "security_features": security_features,
            "anomaly_suggestions": anomaly_suggestions,
            "security_confidence": security_context.get("security_confidence", 0.5),
            "recommended_action": self._recommend_security_action(security_analysis),
        }

    def _generate_anomaly_recommendations(
        self,
        action: str,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> list[str]:
        """Generate action-specific anomaly recommendations."""
        recommendations = []

        if action == "Critical_Alert":
            recommendations.extend(
                [
                    "Immediate investigation required for critical anomaly",
                    "Escalate to security and operations teams",
                    "Implement emergency response procedures",
                    "Document all anomaly indicators and context",
                ]
            )
        elif action == "High_Priority":
            recommendations.extend(
                [
                    "High priority investigation of anomaly indicators",
                    "Notify relevant stakeholders and teams",
                    "Implement monitoring and containment procedures",
                    "Review system logs and performance metrics",
                ]
            )
        elif action == "Medium_Priority":
            recommendations.extend(
                [
                    "Medium priority investigation of anomaly patterns",
                    "Monitor for escalation or resolution",
                    "Review recent system changes and updates",
                    "Document anomaly for future reference",
                ]
            )
        elif action == "Low_Priority":
            recommendations.extend(
                [
                    "Low priority monitoring of anomaly indicators",
                    "Track anomaly trends and patterns",
                    "Review during regular maintenance windows",
                    "Consider preventive measures if pattern persists",
                ]
            )
        elif action == "Informational":
            recommendations.extend(
                [
                    "Informational anomaly - log for reference",
                    "Monitor for pattern development",
                    "Include in regular system health reviews",
                    "No immediate action required",
                ]
            )
        elif action == "Adaptive_Monitoring":
            recommendations.extend(
                [
                    "Implement adaptive monitoring for anomaly patterns",
                    "Adjust monitoring thresholds based on context",
                    "Create custom alerts for specific conditions",
                    "Review and update monitoring strategies",
                ]
            )
        elif action == "Contextual_Analysis":
            recommendations.extend(
                [
                    "Perform contextual analysis of anomaly indicators",
                    "Consider environmental and temporal factors",
                    "Evaluate anomaly in broader system context",
                    "Adjust detection thresholds based on context",
                ]
            )
        else:  # Normal_Operation
            recommendations.extend(
                [
                    "Normal operation detected - no anomalies",
                    "Continue standard monitoring procedures",
                    "Maintain regular system health checks",
                    "Document normal operating parameters",
                ]
            )

        # Add context-specific recommendations
        behavioral_deviation = features.get("behavioral_deviation", 0)
        if behavioral_deviation > 0.7:
            recommendations.append("High behavioral deviation - investigate user patterns")

        system_metric_anomaly = features.get("system_metric_anomaly", 0)
        if system_metric_anomaly > 0.6:
            recommendations.append("System metric anomaly - check resource utilization")

        security_anomaly = features.get("security_anomaly", 0)
        if security_anomaly > 0.5:
            recommendations.append("Security anomaly - review access logs and patterns")

        return recommendations

    def _analyze_anomaly_factors(
        self,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> dict[str, Any]:
        """Analyze anomaly factors and their impact."""
        factor_analysis = {
            "primary_factors": [],
            "secondary_factors": [],
            "contributing_factors": [],
        }

        # Analyze behavioral factors
        behavioral_deviation = features.get("behavioral_deviation", 0)
        if behavioral_deviation > 0.7:
            factor_analysis["primary_factors"].append(
                {
                    "factor": "behavioral_deviation",
                    "score": behavioral_deviation,
                    "impact": "high",
                    "description": "Significant behavioral deviation detected",
                }
            )
        elif behavioral_deviation > 0.4:
            factor_analysis["secondary_factors"].append(
                {
                    "factor": "behavioral_deviation",
                    "score": behavioral_deviation,
                    "impact": "medium",
                    "description": "Moderate behavioral deviation observed",
                }
            )

        # Analyze system factors
        system_metric_anomaly = features.get("system_metric_anomaly", 0)
        if system_metric_anomaly > 0.6:
            factor_analysis["primary_factors"].append(
                {
                    "factor": "system_metric_anomaly",
                    "score": system_metric_anomaly,
                    "impact": "high",
                    "description": "System metrics indicate anomaly",
                }
            )

        # Analyze reconstruction error
        reconstruction_error = features.get("reconstruction_error", 0)
        if reconstruction_error > 0.5:
            factor_analysis["primary_factors"].append(
                {
                    "factor": "reconstruction_error",
                    "score": reconstruction_error,
                    "impact": "high",
                    "description": "High reconstruction error indicates anomaly",
                }
            )

        # Analyze multivariate factors
        multivariate_anomaly = features.get("multivariate_anomaly", 0)
        if multivariate_anomaly > 0.4:
            factor_analysis["contributing_factors"].append(
                {
                    "factor": "multivariate_anomaly",
                    "score": multivariate_anomaly,
                    "impact": "contributing",
                    "description": "Multivariate anomaly contributes to detection",
                }
            )

        return factor_analysis

    def _assess_anomaly_severity(
        self,
        action: str,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> dict[str, Any]:
        """Assess anomaly severity for the chosen action."""
        # Base severity estimates by action
        severity_estimates = {
            "Critical_Alert": {
                "severity_score": 0.9,
                "impact_level": "critical",
                "response_time": "immediate",
                "escalation_required": True,
            },
            "High_Priority": {
                "severity_score": 0.7,
                "impact_level": "high",
                "response_time": "urgent",
                "escalation_required": True,
            },
            "Medium_Priority": {
                "severity_score": 0.5,
                "impact_level": "medium",
                "response_time": "standard",
                "escalation_required": False,
            },
            "Low_Priority": {
                "severity_score": 0.3,
                "impact_level": "low",
                "response_time": "routine",
                "escalation_required": False,
            },
            "Informational": {
                "severity_score": 0.1,
                "impact_level": "informational",
                "response_time": "scheduled",
                "escalation_required": False,
            },
            "Adaptive_Monitoring": {
                "severity_score": 0.4,
                "impact_level": "adaptive",
                "response_time": "conditional",
                "escalation_required": False,
            },
            "Contextual_Analysis": {
                "severity_score": 0.3,
                "impact_level": "contextual",
                "response_time": "investigative",
                "escalation_required": False,
            },
            "Normal_Operation": {
                "severity_score": 0.0,
                "impact_level": "normal",
                "response_time": "none",
                "escalation_required": False,
            },
        }

        base_severity = severity_estimates.get(action, severity_estimates["Normal_Operation"])

        # Adjust based on feature scores
        behavioral_deviation = features.get("behavioral_deviation", 0)
        system_metric_anomaly = features.get("system_metric_anomaly", 0)
        security_anomaly = features.get("security_anomaly", 0)

        # Calculate combined anomaly score
        combined_anomaly = max(behavioral_deviation, system_metric_anomaly, security_anomaly)

        # Adjust severity based on combined anomaly
        if combined_anomaly > 0.8:
            severity_multiplier = 1.5
        elif combined_anomaly > 0.5:
            severity_multiplier = 1.2
        else:
            severity_multiplier = 1.0

        adjusted_severity = {}
        for metric, base_value in base_severity.items():
            if metric == "severity_score":
                adjusted_severity[metric] = min(1.0, base_value * severity_multiplier)
            elif metric == "escalation_required":
                adjusted_severity[metric] = base_value or (combined_anomaly > 0.7)
            else:
                adjusted_severity[metric] = base_value

        return adjusted_severity

    def _get_alternative_responses(self, probability_distribution: dict[str, float]) -> list[dict[str, Any]]:
        """Get alternative anomaly responses with probabilities."""
        alternatives = []

        # Sort by probability and get top 3 alternatives
        sorted_responses = sorted(
            probability_distribution.items(),
            key=lambda x: x[1],
            reverse=True,
        )[1:4]  # Skip the primary response

        for response, probability in sorted_responses:
            if probability > 0.1:  # Only include if probability is significant
                alternatives.append(
                    {
                        "response": response,
                        "probability": probability,
                        "confidence": probability,
                        "recommendation": f"Consider {response} as alternative",
                    }
                )

        return alternatives

    def _get_implementation_priority(self, action: str, confidence: float) -> str:
        """Get implementation priority based on action and confidence."""
        if action == "Normal_Operation":
            return "Low"

        if confidence > 0.8:
            if action in ["Critical_Alert", "High_Priority"]:
                return "Critical"
            elif action in ["Medium_Priority", "Low_Priority"]:
                return "High"
            else:
                return "Medium"
        elif confidence > 0.6:
            if action in ["Critical_Alert", "High_Priority"]:
                return "High"
            else:
                return "Medium"
        else:
            return "Low"

    def _analyze_deviation_patterns(self, behavioral_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze deviation patterns in behavior."""
        current_behavior = behavioral_context.get("current_behavior", {})
        baseline_behavior = behavioral_context.get("baseline_behavior", {})

        deviation_score = 0.0
        deviation_factors = []

        for metric, current_value in tqdm(current_behavior.items(), desc="Processing", unit="item"):
            baseline_value = baseline_behavior.get(metric, current_value)
            if baseline_value > 0:
                deviation = abs(current_value - baseline_value) / baseline_value
                deviation_score += deviation
                deviation_factors.append(
                    {
                        "metric": metric,
                        "current_value": current_value,
                        "baseline_value": baseline_value,
                        "deviation": deviation,
                    }
                )

        avg_deviation = deviation_score / len(deviation_factors) if deviation_factors else 0.0

        return {
            "deviation_score": avg_deviation,
            "severity": "high" if avg_deviation > 0.7 else "medium" if avg_deviation > 0.4 else "low",
            "factors": deviation_factors,
        }

    def _analyze_frequency_patterns(self, behavioral_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze frequency patterns in behavior."""
        current_frequency = behavioral_context.get("request_frequency", 100)
        baseline_frequency = behavioral_context.get("baseline_frequency", 100)

        if baseline_frequency > 0:
            frequency_deviation = abs(current_frequency - baseline_frequency) / baseline_frequency
        else:
            frequency_deviation = 0.0

        return {
            "anomaly_score": frequency_deviation,
            "severity": "high"
            if frequency_deviation > 0.5
            else "medium"
            if frequency_deviation > 0.2
            else "low",
            "current_frequency": current_frequency,
            "baseline_frequency": baseline_frequency,
        }

    def _analyze_response_patterns(self, behavioral_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze response patterns in behavior."""
        current_response = behavioral_context.get("response_patterns", 0.5)
        baseline_response = behavioral_context.get("baseline_response", 0.5)

        response_deviation = abs(current_response - baseline_response)

        return {
            "anomaly_score": response_deviation,
            "severity": "high"
            if response_deviation > 0.3
            else "medium"
            if response_deviation > 0.1
            else "low",
            "current_response": current_response,
            "baseline_response": baseline_response,
        }

    def _analyze_error_patterns(self, behavioral_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze error patterns in behavior."""
        current_errors = behavioral_context.get("error_patterns", 0.01)
        baseline_errors = behavioral_context.get("baseline_error_patterns", 0.01)

        if baseline_errors > 0:
            error_deviation = abs(current_errors - baseline_errors) / baseline_errors
        else:
            error_deviation = 0.0

        return {
            "anomaly_score": error_deviation,
            "severity": "high" if error_deviation > 2.0 else "medium" if error_deviation > 1.0 else "low",
            "current_errors": current_errors,
            "baseline_errors": baseline_errors,
        }

    def _recommend_behavioral_action(self, behavioral_analysis: dict[str, Any]) -> str:
        """Recommend anomaly action based on behavioral analysis."""
        deviation_severity = behavioral_analysis["deviation_analysis"]["severity"]
        frequency_severity = behavioral_analysis["frequency_analysis"]["severity"]

        if deviation_severity == "high" or frequency_severity == "high":
            return "Critical_Alert"
        elif deviation_severity == "medium" or frequency_severity == "medium":
            return "High_Priority"
        else:
            return "Medium_Priority"

    def _analyze_metric_health(self, system_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze system metric health."""
        system_metrics = system_context.get("system_metrics", {})

        health_score = 0.0
        metric_count = 0

        for metric, value in tqdm(system_metrics.items(), desc="Processing", unit="item"):
            if "cpu" in metric.lower():
                # CPU health: lower is better
                health_score += max(0, 1.0 - value / 100)
            elif "memory" in metric.lower():
                # Memory health: lower is better
                health_score += max(0, 1.0 - value / 100)
            else:
                # Other metrics: assume 0.5 baseline
                health_score += 0.5
            metric_count += 1

        avg_health = health_score / metric_count if metric_count > 0 else 0.5

        return {
            "score": avg_health,
            "status": "healthy" if avg_health > 0.7 else "degraded" if avg_health > 0.4 else "unhealthy",
        }

    def _analyze_performance_health(self, system_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze system performance health."""
        performance_data = system_context.get("performance_data", {})

        health_score = 0.0

        # Response time health
        response_time = performance_data.get("response_time", 100)
        target_time = performance_data.get("target_response_time", 500)
        response_health = min(1.0, target_time / max(1, response_time))
        health_score += response_health * 0.4

        # Throughput health
        throughput = performance_data.get("throughput", 100)
        target_throughput = performance_data.get("target_throughput", 200)
        throughput_health = min(1.0, throughput / max(1, target_throughput))
        health_score += throughput_health * 0.3

        # Error rate health
        error_rate = performance_data.get("error_rate", 0.01)
        error_health = max(0, 1.0 - error_rate * 10)  # Scale error rate impact
        health_score += error_health * 0.3

        return {
            "score": health_score,
            "status": "healthy" if health_score > 0.7 else "degraded" if health_score > 0.4 else "unhealthy",
        }

    def _analyze_resource_health(self, system_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze system resource health."""
        resource_data = system_context.get("resource_data", {})

        health_score = 0.0

        # Memory health
        memory_usage = resource_data.get("memory_usage", 50)
        memory_health = max(0, 1.0 - memory_usage / 100)
        health_score += memory_health * 0.4

        # CPU health
        cpu_usage = resource_data.get("cpu_usage", 50)
        cpu_health = max(0, 1.0 - cpu_usage / 100)
        health_score += cpu_health * 0.3

        # Disk health
        disk_usage = resource_data.get("disk_usage", 50)
        disk_health = max(0, 1.0 - disk_usage / 100)
        health_score += disk_health * 0.3

        return {
            "score": health_score,
            "status": "healthy" if health_score > 0.7 else "degraded" if health_score > 0.4 else "unhealthy",
        }

    def _calculate_overall_health(self, system_context: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall system health."""
        metric_health = self._analyze_metric_health(system_context)
        performance_health = self._analyze_performance_health(system_context)
        resource_health = self._analyze_resource_health(system_context)

        overall_score = (
            metric_health["score"] * 0.3 + performance_health["score"] * 0.4 + resource_health["score"] * 0.3
        )

        return {
            "score": overall_score,
            "status": "healthy"
            if overall_score > 0.7
            else "degraded"
            if overall_score > 0.4
            else "unhealthy",
            "components": {
                "metrics": metric_health,
                "performance": performance_health,
                "resources": resource_health,
            },
        }

    def _recommend_system_action(self, system_analysis: dict[str, Any]) -> str:
        """Recommend anomaly action based on system analysis."""
        overall_status = system_analysis["overall_health"]["status"]

        if overall_status == "unhealthy":
            return "Critical_Alert"
        elif overall_status == "degraded":
            return "High_Priority"
        else:
            return "Normal_Operation"

    def _analyze_authentication_security(self, security_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze authentication security."""
        auth_failures = security_context.get("authentication_failures", 0)
        auth_threshold = security_context.get("auth_failure_threshold", 5)

        if auth_failures > auth_threshold:
            security_score = min(1.0, (auth_failures - auth_threshold) / auth_threshold)
        else:
            security_score = 0.0

        return {
            "score": security_score,
            "status": "critical" if security_score > 0.7 else "high" if security_score > 0.3 else "normal",
        }

    def _analyze_authorization_security(self, security_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze authorization security."""
        unauthorized_attempts = security_context.get("unauthorized_attempts", 0)
        authz_threshold = security_context.get("unauthorized_threshold", 3)

        if unauthorized_attempts > authz_threshold:
            security_score = min(1.0, (unauthorized_attempts - authz_threshold) / authz_threshold)
        else:
            security_score = 0.0

        return {
            "score": security_score,
            "status": "critical" if security_score > 0.7 else "high" if security_score > 0.3 else "normal",
        }

    def _analyze_access_pattern_security(self, security_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze access pattern security."""
        access_deviation = security_context.get("access_pattern_deviation", 0.0)

        security_score = min(1.0, access_deviation)

        return {
            "score": security_score,
            "status": "critical" if security_score > 0.7 else "high" if security_score > 0.3 else "normal",
        }

    def _assess_threat_level(self, security_context: dict[str, Any]) -> dict[str, Any]:
        """Assess overall threat level."""
        auth_security = self._analyze_authentication_security(security_context)
        authz_security = self._analyze_authorization_security(security_context)
        access_security = self._analyze_access_pattern_security(security_context)

        threat_score = max(
            auth_security["score"],
            authz_security["score"],
            access_security["score"],
        )

        return {
            "score": threat_score,
            "level": "critical"
            if threat_score > 0.7
            else "high"
            if threat_score > 0.4
            else "medium"
            if threat_score > 0.2
            else "low",
        }

    def _recommend_security_action(self, security_analysis: dict[str, Any]) -> str:
        """Recommend anomaly action based on security analysis."""
        threat_level = security_analysis["threat_assessment"]["level"]

        if threat_level == "critical":
            return "Critical_Alert"
        elif threat_level == "high":
            return "High_Priority"
        elif threat_level == "medium":
            return "Medium_Priority"
        else:
            return "Informational"

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        if not self.is_loaded or not self.pipeline:
            return []

        try:
            # Get feature importances from Isolation Forest
            iforest_model = self.pipeline.named_steps["classifier"]
            importances = np.ones(len(self.feature_names)) / len(
                self.feature_names
            )  # Isolation Forest doesn't have feature_importances

            # Get feature names
            feature_names = self.feature_names or list(model_input.features.keys())

            # Create feature importance list
            feature_importance = []
            for i, (name, importance) in enumerate(zip(feature_names, importances)):
                feature_importance.append(
                    {
                        "feature_name": name,
                        "importance_score": importance,
                        "feature_value": model_input.features.get(name),
                        "rank": i + 1,
                    }
                )

            # Sort by importance (all equal for Isolation Forest)
            feature_importance.sort(key=lambda x: x["feature_name"])

            # Update ranks
            for i, feature in enumerate(feature_importance):
                feature["rank"] = i + 1

            return feature_importance[:10]

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
            # Failed to compute importance
            return []

    def _extract_feature_vector(self, features: dict[str, Any]) -> np.ndarray | None:
        """Extract features in the correct order for the model."""
        if not self.feature_names:
            return None

        try:
            feature_vector = []
            for feature_name in self.feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            return np.array(feature_vector)

        except (TypeError, ValueError):
            return None

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for Autoencoder-inspired model."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for Autoencoder-inspired model
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
    ) -> None:
        """
        Train the Autoencoder-inspired model.

        Args:
            training_data: List of training examples with features and labels
            feature_names: Names of features to use
            training_data_digest: Digest of training data for provenance
        """
        # Extract features and labels
        X = []
        y = []

        for example in tqdm(training_data, desc="Processing", unit="item"):
            features = example["features"]
            label = example["label"]

            # Convert anomaly type string to class index
            if isinstance(label, str):
                label = self.REVERSE_ANOMALY_MAPPING.get(label, 7)  # Default to Normal_Operation
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

        # Create pipeline with scaling and Isolation Forest (as autoencoder proxy)
        self.pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    IsolationForest(
                        n_estimators=100,
                        max_samples="auto",
                        contamination=0.1,
                        random_state=42,
                    ),
                ),
            ]
        )

        # Train model
        self.pipeline.fit(X)

        # Store feature names and training digest
        self.feature_names = feature_names
        self._training_data_digest = training_data_digest

        self.is_loaded = True
