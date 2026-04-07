"""
L2 Healer Selector

Logistic regression model for selecting optimal healing strategies
based on error characteristics, healer capabilities, and system context.
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
from ..features.l2_features import L2FeatureExtractor
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType


class L2HealerSelector(BaseMLModel):
    """
    Logistic regression model for L2 healer selection.

    Selects optimal healing strategies based on:
    - Healer compatibility with error type
    - Historical success rates and performance metrics
    - Resource availability and system load
    - Error severity and healing complexity
    - Escalation history and retry probability
    - Time sensitivity and rollback likelihood

    Always operates in advisory mode - L2 retains final execution authority.
    """

    # Healer type mapping
    HEALER_MAPPING = {
        0: "Retry",
        1: "Rollback",
        2: "Alternative_Path",
        3: "Circuit_Breaker",
        4: "Fallback_Service",
        5: "Manual_Intervention",
    }

    # Reverse mapping
    REVERSE_HEALER_MAPPING = {v: k for k, v in HEALER_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        super().__init__(
            model_name="l2_healer_selector",
            model_version="1.0",
            model_type="logistic_regression",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path,
        )

        # Initialize feature extractor
        self.feature_extractor = L2FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.pipeline = None
        self.feature_names = None
        self.class_names = list(self.HEALER_MAPPING.values())

        # Default thresholds
        self.threshold_config = {
            "confidence_threshold": 0.6,
            "selection_threshold": 0.5,
            "fallback_threshold": 0.3,
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
                'saved_at': datetime.now().isoformat(),
            },
        }

        with open(model_file_path, 'wb') as f:
            pickle.dump(model_data, f)

    def predict(
        self,
        model_input: ModelInput,
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.ADVISORY,
    ) -> ModelPrediction:
        """
        Predict optimal healer for error recovery.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Healer selection prediction with full metadata
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
                prediction="Retry",  # Default healer
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # Logistic regression prediction
            probabilities = self.pipeline.predict_proba(feature_vector.reshape(1, -1))[0]
            predicted_class = self.pipeline.predict(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to healer name
            predicted_healer = self.HEALER_MAPPING.get(int(predicted_class), "Retry")

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
            threshold_used = self.threshold_config.get("selection_threshold", 0.5)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_healer,
                    confidence=confidence,
                    probability_distribution=prob_distribution,
                    threshold_used=threshold_used,
                ),
            )

            # Determine final decision mode
            final_decision_mode = decision_mode
            if not passes_threshold or confidence < self.threshold_config.get("confidence_threshold", 0.6):
                final_decision_mode = DecisionMode.ESCALATED

            # Create prediction
            prediction = self.create_prediction(
                prediction=predicted_healer,
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
            prediction.model_metadata.update({
                'prediction_time_ms': prediction_time * 1000,
                'feature_vector_length': len(feature_vector),
                'preprocessing_steps': preprocessing_steps,
                'raw_prediction_class': int(predicted_class),
                'class_probabilities': [float(p) for p in probabilities],
                'thresholds_passed': passes_threshold,
                'selected_healer': predicted_healer,
                'requires_escalation': final_decision_mode == DecisionMode.ESCALATED,
            })

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except Exception as e:
            # Prediction failed
            return self.create_prediction(
                prediction="Retry",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

    def select_healer(
        self,
        error: dict[str, Any],
        available_healers: list[dict[str, Any]],
        context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Select optimal healer from available options.

        Args:
            error: Error information
            available_healers: List of available healers
            context: System and error context
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Healer selection with analysis
        """
        if not available_healers:
            # No healers available
            return {
                'selected_healer': None,
                'confidence': 0.0,
                'reason': 'No healers available',
                'recommendations': ['Add more healing strategies', 'Implement default retry mechanism'],
            }

        # Score each healer
        healer_scores = []

        for i, healer in enumerate(available_healers):
            # Create context for this healer
            healer_context = {
                "healer": healer,
                "error": error,
                "system_resources": context.get("system_resources", {}),
                "system_state": context.get("system_state", {}),
                "history": context.get("history", {}),
                "healing_context": context.get("healing_context", {}),
                "trace_id": f"{trace_id}_healer_{i}",
            }

            # Extract features
            extraction_result = self.feature_extractor.extract_features(
                context=healer_context,
                trace_id=f"{trace_id}_healer_{i}",
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

            if extraction_result.success:
                # Validate input
                model_input = self.validate_input(extraction_result.features)
                model_input.feature_provenance = extraction_result.provenance

                # Make prediction
                prediction = self.predict(
                    model_input=model_input,
                    trace_id=f"{trace_id}_healer_{i}",
                    replay_key=replay_key,
                    policy_hash=policy_hash,
                )

                healer_scores.append({
                    'healer': healer,
                    'healer_name': healer.get('name', f'Healer_{i}'),
                    'healer_type': healer.get('type', 'unknown'),
                    'selection_score': prediction.confidence,
                    'confidence': prediction.confidence,
                    'top_features': prediction.top_features,
                    'decision_mode': prediction.decision_mode,
                    'prediction_metadata': prediction.model_metadata,
                })
            else:
                # Feature extraction failed
                healer_scores.append({
                    'healer': healer,
                    'healer_name': healer.get('name', f'Healer_{i}'),
                    'healer_type': healer.get('type', 'unknown'),
                    'selection_score': 0.1,
                    'confidence': 0.0,
                    'top_features': [],
                    'decision_mode': DecisionMode.BLOCKED,
                    'prediction_metadata': {'error': 'Feature extraction failed'},
                })

        # Sort by selection score
        healer_scores.sort(key=lambda x: x['selection_score'], reverse=True)

        # Select best healer
        best_healer = healer_scores[0]

        # Generate recommendations
        recommendations = self._generate_healer_recommendations(
            best_healer=best_healer,
            error=error,
            available_healers=available_healers,
        )

        return {
            'selected_healer': best_healer['healer'],
            'healer_name': best_healer['healer_name'],
            'healer_type': best_healer['healer_type'],
            'confidence': best_healer['confidence'],
            'selection_score': best_healer['selection_score'],
            'top_factors': best_healer['top_features'],
            'decision_mode': best_healer['decision_mode'],
            'all_healer_scores': healer_scores,
            'recommendations': recommendations,
            'requires_escalation': best_healer['decision_mode'] == DecisionMode.ESCALATED,
        }

    def get_healing_strategy(
        self,
        error: dict[str, Any],
        context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Get comprehensive healing strategy recommendation.

        Args:
            error: Error information
            context: System context
            trace_id: Trace ID
            replay_key: Replay key
            policy_hash: Policy hash

        Returns:
            Comprehensive healing strategy
        """
        # Get error severity and characteristics
        error_severity = error.get('severity', 'medium')
        error_type = error.get('type', 'unknown')

        # Generate healing strategy based on error characteristics
        strategy = self._generate_healing_strategy(error, context)

        # Get healer recommendations
        available_healers = context.get('available_healers', [])
        healer_selection = self.select_healer(
            error=error,
            available_healers=available_healers,
            context=context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        # Combine into comprehensive strategy
        return {
            'error_analysis': {
                'type': error_type,
                'severity': error_severity,
                'impact': error.get('impact', 'unknown'),
                'recoverable': error.get('recoverable', True),
            },
            'healing_strategy': strategy,
            'recommended_healer': healer_selection,
            'fallback_options': self._get_fallback_options(error, context),
            'monitoring_requirements': self._get_monitoring_requirements(error),
            'success_probability': healer_selection.get('confidence', 0.5),
            'estimated_recovery_time': self._estimate_recovery_time(error, healer_selection),
            'resource_requirements': self._calculate_resource_requirements(error, healer_selection),
        }

    def _generate_healer_recommendations(
        self,
        best_healer: dict[str, Any],
        error: dict[str, Any],
        available_healers: list[dict[str, Any]],
    ) -> list[str]:
        """Generate healer-specific recommendations."""
        recommendations = []

        healer_type = best_healer.get('healer_type', 'unknown')
        confidence = best_healer.get('confidence', 0.0)

        # Base recommendations by confidence
        if confidence < 0.3:
            recommendations.append("Low confidence in healer selection - consider manual review")
        elif confidence < 0.6:
            recommendations.append("Moderate confidence - monitor healing progress closely")
        else:
            recommendations.append("High confidence - proceed with automated healing")

        # Healer-specific recommendations
        if healer_type == "Retry":
            recommendations.append("Implement exponential backoff for retry attempts")
            recommendations.append("Set maximum retry limit to prevent infinite loops")
        elif healer_type == "Rollback":
            recommendations.append("Ensure rollback points are available and valid")
            recommendations.append("Verify data integrity before rollback execution")
        elif healer_type == "Alternative_Path":
            recommendations.append("Validate alternative path compatibility")
            recommendations.append("Test alternative path with sample data")
        elif healer_type == "Circuit_Breaker":
            recommendations.append("Configure appropriate timeout thresholds")
            recommendations.append("Set up monitoring for circuit breaker state changes")
        elif healer_type == "Fallback_Service":
            recommendations.append("Verify fallback service availability")
            recommendations.append("Test fallback service functionality")
        elif healer_type == "Manual_Intervention":
            recommendations.append("Alert operations team immediately")
            recommendations.append("Provide detailed error context for manual resolution")

        # Error-specific recommendations
        error_type = error.get('type', '').lower()
        if 'timeout' in error_type:
            recommendations.append("Review and adjust timeout configurations")
        elif 'connection' in error_type:
            recommendations.append("Check network connectivity and service availability")
        elif 'memory' in error_type or 'resource' in error_type:
            recommendations.append("Monitor resource usage during healing")

        return recommendations

    def _generate_healing_strategy(self, error: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Generate healing strategy based on error characteristics."""
        error_severity = error.get('severity', 'medium')
        error_type = error.get('type', 'unknown')
        impact_scope = error.get('impact_scope', 'local')

        strategy = {
            'primary_approach': 'automated',
            'escalation_threshold': 'medium',
            'monitoring_level': 'standard',
            'rollback_plan': 'available',
        }

        # Adjust strategy based on error severity
        if error_severity == 'critical':
            strategy.update({
                'primary_approach': 'manual_intervention',
                'escalation_threshold': 'immediate',
                'monitoring_level': 'intensive',
                'rollback_plan': 'required',
            })
        elif error_severity == 'high':
            strategy.update({
                'primary_approach': 'supervised_automated',
                'escalation_threshold': 'low',
                'monitoring_level': 'enhanced',
                'rollback_plan': 'recommended',
            })

        # Adjust based on impact scope
        if impact_scope == 'global':
            strategy['escalation_threshold'] = 'immediate'
            strategy['monitoring_level'] = 'intensive'

        # Adjust based on error type
        if 'timeout' in error_type.lower():
            strategy['timeout_handling'] = 'exponential_backoff'
        elif 'connection' in error_type.lower():
            strategy['connection_handling'] = 'retry_with_circuit_breaker'
        elif 'data' in error_type.lower():
            strategy['data_integrity_checks'] = 'required'

        return strategy

    def _get_fallback_options(self, error: dict[str, Any], context: dict[str, Any]) -> list[str]:
        """Get fallback healing options."""
        fallbacks = ["Retry with exponential backoff"]

        error_type = error.get('type', '').lower()

        if 'connection' in error_type:
            fallbacks.append("Switch to alternative endpoint")
            fallbacks.append("Use cached response if available")

        if 'timeout' in error_type:
            fallbacks.append("Increase timeout and retry")
            fallbacks.append("Execute with reduced scope")

        if 'resource' in error_type:
            fallbacks.append("Scale down resource requirements")
            fallbacks.append("Queue for later execution")

        fallbacks.append("Manual intervention")
        fallbacks.append("Circuit breaker activation")

        return fallbacks

    def _get_monitoring_requirements(self, error: dict[str, Any]) -> list[str]:
        """Get monitoring requirements for healing."""
        requirements = ["Monitor healing success/failure"]

        error_severity = error.get('severity', 'medium')

        if error_severity in ['high', 'critical']:
            requirements.extend([
                "Real-time performance monitoring",
                "Resource usage tracking",
                "Error rate monitoring",
                "User impact assessment",
            ])

        requirements.append("Log all healing attempts")
        requirements.append("Track recovery time")

        return requirements

    def _estimate_recovery_time(self, error: dict[str, Any], healer_selection: dict[str, Any]) -> str:
        """Estimate recovery time based on error and healer."""
        healer_type = healer_selection.get('healer_type', 'unknown')
        error_severity = error.get('severity', 'medium')

        # Base recovery times by healer type (in minutes)
        base_times = {
            'Retry': 1,
            'Rollback': 5,
            'Alternative_Path': 3,
            'Circuit_Breaker': 2,
            'Fallback_Service': 4,
            'Manual_Intervention': 30,
        }

        base_time = base_times.get(healer_type, 5)

        # Adjust based on error severity
        severity_multipliers = {'low': 0.5, 'medium': 1.0, 'high': 2.0, 'critical': 5.0}
        multiplier = severity_multipliers.get(error_severity, 1.0)

        estimated_time = int(base_time * multiplier)

        if estimated_time < 5:
            return f"< {estimated_time} minutes"
        elif estimated_time < 60:
            return f"~ {estimated_time} minutes"
        else:
            hours = estimated_time // 60
            minutes = estimated_time % 60
            return f"~ {hours}h {minutes}m"

    def _calculate_resource_requirements(self, error: dict[str, Any], healer_selection: dict[str, Any]) -> dict[str, Any]:
        """Calculate resource requirements for healing."""
        healer_type = healer_selection.get('healer_type', 'unknown')

        requirements = {
            'cpu': 'low',
            'memory': 'low',
            'storage': 'minimal',
            'network': 'low',
            'human_intervention': 'none',
        }

        # Adjust based on healer type
        if healer_type == 'Rollback':
            requirements.update({
                'cpu': 'medium',
                'memory': 'medium',
                'storage': 'moderate',
            })
        elif healer_type == 'Manual_Intervention':
            requirements['human_intervention'] = 'required'
        elif healer_type == 'Fallback_Service':
            requirements['network'] = 'medium'

        # Adjust based on error severity
        error_severity = error.get('severity', 'medium')
        if error_severity in ['high', 'critical']:
            for resource in requirements:
                if requirements[resource] in ['low', 'medium']:
                    requirements[resource] = 'high'

        return requirements

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
                        'rank': i + 1,
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
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0.0

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
        training_data_digest: str = "",
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

            # Convert healer type string to class index
            if isinstance(label, str):
                label = self.REVERSE_HEALER_MAPPING.get(label, 0)  # Default to Retry
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

        # Create pipeline with scaling and logistic regression
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(
                multi_class='multinomial',
                solver='lbfgs',
                max_iter=1000,
                random_state=42,
            )),
        ])

        # Train model
        self.pipeline.fit(X, y)

        # Store feature names and training digest
        self.feature_names = feature_names
        self._training_data_digest = training_data_digest

        self.is_loaded = True
