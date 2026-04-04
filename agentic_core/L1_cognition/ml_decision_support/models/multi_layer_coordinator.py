"""
Multi-Layer Coordinator

Ensemble model for coordinating decisions across multiple ML layers,
providing unified recommendations and conflict resolution.
"""

import pickle
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from ..config.feature_schemas import FeatureSchema
from ..config.model_registry import DecisionMode
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType


class MultiLayerCoordinator(BaseMLModel):
    """
    Ensemble model for multi-layer ML coordination.

    Coordinates decisions across all ML layers:
    - L0-L6 model recommendations aggregation
    - Conflict detection and resolution
    - Cross-layer optimization strategies
    - Unified decision synthesis
    - Performance impact assessment
    - Risk-based decision weighting
    - Consistency enforcement across layers
    """

    # Decision action mapping
    DECISION_MAPPING = {
        0: "Execute_All",
        1: "Execute_Partial",
        2: "Escalate",
        3: "Block_All",
        4: "Defer_Decision",
        5: "Manual_Review",
        6: "Optimize_First",
        7: "Monitor_Only"
    }

    # Reverse mapping
    REVERSE_DECISION_MAPPING = {v: k for k, v in DECISION_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        super().__init__(
            model_name="multi_layer_coordinator",
            model_version="1.0",
            model_type="ensemble",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path
        )

        # Create feature schema for coordinator
        self.feature_schema = self._create_coordinator_schema()

        # Model components
        self.model_weights = None
        self.feature_names = None
        self.class_names = list(self.DECISION_MAPPING.values())

        # Layer model references (for ensemble)
        self.layer_models = {}

        # Ensemble weights by layer
        self.layer_weights = {
            "L0": 0.15,  # Route recommendation
            "L1": 0.15,  # Capacity planning
            "L2": 0.15,  # Healer selection
            "L3": 0.15,  # DAG branch ranking
            "L4": 0.15,  # Performance optimization
            "L5": 0.15,  # Risk calibration
            "L6": 0.10   # Anomaly detection
        }

        # Default thresholds
        self.threshold_config = {
            "confidence_threshold": 0.7,
            "consensus_threshold": 0.6,
            "conflict_threshold": 0.3,
            "risk_threshold": 0.5
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def _create_coordinator_schema(self) -> FeatureSchema:
        """Create feature schema for multi-layer coordinator."""
        from ..config.feature_schemas import FeatureDefinition, FeatureSchema, FeatureType

        features = [
            FeatureDefinition(
                name="l0_confidence",
                feature_type=FeatureType.NUMERIC,
                description="L0 model confidence score",
                provenance="layer.l0.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="l1_confidence",
                feature_type=FeatureType.NUMERIC,
                description="L1 model confidence score",
                provenance="layer.l1.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="l2_confidence",
                feature_type=FeatureType.NUMERIC,
                description="L2 model confidence score",
                provenance="layer.l2.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="l3_confidence",
                feature_type=FeatureType.NUMERIC,
                description="L3 model confidence score",
                provenance="layer.l3.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="l4_confidence",
                feature_type=FeatureType.NUMERIC,
                description="L4 model confidence score",
                provenance="layer.l4.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="l5_confidence",
                feature_type=FeatureType.NUMERIC,
                description="L5 model confidence score",
                provenance="layer.l5.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="l6_confidence",
                feature_type=FeatureType.NUMERIC,
                description="L6 model confidence score",
                provenance="layer.l6.confidence",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="consensus_score",
                feature_type=FeatureType.NUMERIC,
                description="Consensus score across layers",
                provenance="ensemble.consensus",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="conflict_level",
                feature_type=FeatureType.NUMERIC,
                description="Level of conflict between layer recommendations",
                provenance="ensemble.conflict",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="overall_risk",
                feature_type=FeatureType.NUMERIC,
                description="Overall risk assessment",
                provenance="ensemble.risk",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            )
        ]

        return FeatureSchema(
            schema_name="multi_layer_coordinator",
            schema_version="1.0",
            description="Features for multi-layer ensemble coordination model",
            features=features
        )

    def load_model(self) -> None:
        """Load the ensemble model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            with open(self.model_file_path, 'rb') as f:
                model_data = pickle.load(f)

            self.model_weights = model_data.get('model_weights')
            self.feature_names = model_data.get('feature_names', [])
            self.threshold_config = model_data.get('threshold_config', self.threshold_config)
            self.layer_weights = model_data.get('layer_weights', self.layer_weights)
            self._training_data_digest = model_data.get('training_data_digest', '')

            self.is_loaded = True

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def save_model(self, model_file_path: Path) -> None:
        """Save the model to file."""
        model_data = {
            'model_weights': self.model_weights,
            'feature_names': self.feature_names,
            'threshold_config': self.threshold_config,
            'layer_weights': self.layer_weights,
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
        Predict coordinated decision across all layers.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Coordinated decision prediction with full metadata
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
                prediction="Monitor_Only",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # Ensemble prediction
            class_probabilities = self._predict_ensemble(feature_vector)
            predicted_class = np.argmax(class_probabilities)

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to decision action name
            predicted_decision = self.DECISION_MAPPING.get(int(predicted_class), "Monitor_Only")

            # Create probability distribution
            prob_distribution = {
                self.class_names[i]: float(prob)
                for i, prob in enumerate(class_probabilities)
            }

            # Calculate confidence (max probability)
            confidence = float(np.max(class_probabilities))

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("consensus_threshold", 0.6)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_decision,
                    confidence=confidence,
                    probability_distribution=prob_distribution,
                    threshold_used=threshold_used
                )
            )

            # Create prediction
            prediction = self.create_prediction(
                prediction=predicted_decision,
                confidence=confidence,
                probability_distribution=prob_distribution,
                top_features=top_features,
                threshold_used=threshold_used,
                decision_mode=decision_mode,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

            # Add prediction metadata
            prediction.model_metadata.update({
                'prediction_time_ms': prediction_time * 1000,
                'feature_vector_length': len(feature_vector),
                'preprocessing_steps': preprocessing_steps,
                'raw_prediction_class': predicted_class,
                'class_probabilities': [float(p) for p in class_probabilities],
                'thresholds_passed': passes_threshold,
                'coordinated_decision': predicted_decision,
                'requires_coordination': predicted_decision != "Monitor_Only"
            })

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except Exception as e:
            # Prediction failed
            return self.create_prediction(
                prediction="Monitor_Only",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

    def coordinate_layers(
        self,
        layer_predictions: dict[str, dict[str, Any]],
        trace_id: str,
        replay_key: str,
        policy_hash: str
    ) -> dict[str, Any]:
        """
        Coordinate decisions across all ML layers.

        Args:
            layer_predictions: Predictions from all layer models
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Coordinated decision with analysis
        """
        # Extract features from layer predictions
        coordinator_features = self._extract_coordinator_features(layer_predictions)

        # Validate input
        model_input = self.validate_input(coordinator_features)

        # Make prediction
        prediction = self.predict(
            model_input=model_input,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash
        )

        # Analyze conflicts
        conflict_analysis = self._analyze_conflicts(layer_predictions)

        # Generate coordinated recommendations
        recommendations = self._generate_coordinated_recommendations(
            decision=prediction.prediction,
            layer_predictions=layer_predictions,
            conflicts=conflict_analysis
        )

        # Calculate overall risk
        risk_assessment = self._assess_overall_risk(layer_predictions, conflict_analysis)

        # Determine execution plan
        execution_plan = self._create_execution_plan(
            decision=prediction.prediction,
            layer_predictions=layer_predictions,
            recommendations=recommendations
        )

        return {
            'coordinated_decision': prediction.prediction,
            'confidence': prediction.confidence,
            'probability_distribution': prediction.probability_distribution,
            'top_factors': prediction.top_features,
            'layer_predictions': layer_predictions,
            'conflict_analysis': conflict_analysis,
            'recommendations': recommendations,
            'risk_assessment': risk_assessment,
            'execution_plan': execution_plan,
            'consensus_score': coordinator_features.get('consensus_score', 0),
            'conflict_level': coordinator_features.get('conflict_level', 0)
        }

    def resolve_conflicts(
        self,
        conflicting_layers: list[str],
        layer_predictions: dict[str, dict[str, Any]],
        trace_id: str,
        replay_key: str,
        policy_hash: str
    ) -> dict[str, Any]:
        """
        Resolve conflicts between layer recommendations.

        Args:
            conflicting_layers: List of layers with conflicts
            layer_predictions: All layer predictions
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Conflict resolution strategy
        """
        resolution_strategies = []

        for layer in conflicting_layers:
            prediction = layer_predictions.get(layer, {})

            # Determine resolution strategy based on layer priority and confidence
            layer_priority = self.layer_weights.get(layer, 0.1)
            confidence = prediction.get('confidence', 0.0)

            if confidence > 0.8 and layer_priority > 0.1:
                strategy = {
                    'layer': layer,
                    'resolution': 'accept_recommendation',
                    'reason': f'High confidence ({confidence:.2f}) and priority ({layer_priority:.2f})',
                    'action': prediction.get('prediction', 'unknown')
                }
            elif confidence < 0.5:
                strategy = {
                    'layer': layer,
                    'resolution': 'override_with_default',
                    'reason': f'Low confidence ({confidence:.2f})',
                    'action': 'monitor_only'
                }
            else:
                strategy = {
                    'layer': layer,
                    'resolution': 'escalate_for_review',
                    'reason': f'Moderate confidence ({confidence:.2f}) requires review',
                    'action': 'manual_review'
                }

            resolution_strategies.append(strategy)

        # Determine overall resolution
        high_confidence_layers = [s for s in resolution_strategies if s['resolution'] == 'accept_recommendation']

        if len(high_confidence_layers) >= len(conflicting_layers) * 0.6:
            overall_resolution = 'execute_with_confidence'
        elif len(high_confidence_layers) >= len(conflicting_layers) * 0.3:
            overall_resolution = 'execute_with_monitoring'
        else:
            overall_resolution = 'escalate_all'

        return {
            'resolution_strategies': resolution_strategies,
            'overall_resolution': overall_resolution,
            'conflicting_layers': conflicting_layers,
            'recommended_actions': [s['action'] for s in resolution_strategies]
        }

    def _extract_coordinator_features(self, layer_predictions: dict[str, dict[str, Any]]) -> dict[str, float]:
        """Extract features for coordinator from layer predictions."""
        features = {}

        # Extract confidence scores from each layer
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            prediction = layer_predictions.get(layer, {})
            features[f"{layer.lower()}_confidence"] = prediction.get('confidence', 0.0)

        # Calculate consensus score
        confidences = [features[f"{l.lower()}_confidence"] for l in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]]
        features['consensus_score'] = np.mean(confidences)

        # Calculate conflict level (simplified)
        predictions = [layer_predictions.get(layer, {}).get('prediction', 'unknown') for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]]
        unique_predictions = len(set(predictions))
        total_predictions = len(predictions)

        if total_predictions > 0:
            features['conflict_level'] = (unique_predictions - 1) / total_predictions
        else:
            features['conflict_level'] = 0.0

        # Calculate overall risk
        risk_factors = []
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            prediction = layer_predictions.get(layer, {})
            # Risk is inverse of confidence for this simplified calculation
            risk = 1.0 - prediction.get('confidence', 0.0)
            risk_factors.append(risk)

        features['overall_risk'] = np.mean(risk_factors)

        return features

    def _predict_ensemble(self, feature_vector: np.ndarray) -> np.ndarray:
        """Simplified ensemble prediction."""
        if self.model_weights is None:
            # Initialize with default weights
            self.model_weights = np.random.rand(len(self.class_names))
            self.model_weights = self.model_weights / np.sum(self.model_weights)

        # Simplified ensemble calculation
        class_scores = np.zeros(len(self.class_names))

        # Feature influence on different decisions (simplified)
        feature_influence = {
            0: [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.3, -0.1, -0.2],  # Execute_All
            1: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.0, -0.1],  # Execute_Partial
            2: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.2, 0.1],   # Escalate
            3: [-0.2, -0.2, -0.2, -0.2, -0.2, -0.2, -0.2, -0.1, 0.3, 0.4], # Block_All
            4: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.2],   # Defer_Decision
            5: [-0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, 0.0, 0.2, 0.3], # Manual_Review
            6: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.0, -0.1],  # Optimize_First
            7: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]    # Monitor_Only
        }

        for class_idx, influences in feature_influence.items():
            score = 0.0
            for feat_idx, influence in enumerate(influences):
                if feat_idx < len(feature_vector):
                    score += influence * feature_vector[feat_idx]
            class_scores[class_idx] = score

        # Apply softmax to get probabilities
        exp_scores = np.exp(class_scores - np.max(class_scores))
        probabilities = exp_scores / np.sum(exp_scores)

        return probabilities

    def _analyze_conflicts(self, layer_predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Analyze conflicts between layer predictions."""
        conflicts = []

        # Group predictions by type
        action_groups = defaultdict(list)
        for layer, prediction in layer_predictions.items():
            action = prediction.get('prediction', 'unknown')
            action_groups[action].append(layer)

        # Identify conflicts (layers with different actions)
        if len(action_groups) > 1:
            for action, layers in action_groups.items():
                if len(layers) < len(layer_predictions):  # Minority action
                    conflicts.append({
                        'conflict_type': 'action_disagreement',
                        'conflicting_layers': layers,
                        'minority_action': action,
                        'majority_action': max(action_groups.items(), key=lambda x: len(x[1]))[0] if action_groups else 'unknown'
                    })

        # Analyze confidence conflicts
        confidences = {layer: pred.get('confidence', 0.0) for layer, pred in layer_predictions.items()}
        avg_confidence = np.mean(list(confidences.values()))

        low_confidence_layers = [layer for layer, conf in confidences.items() if conf < avg_confidence * 0.7]

        if low_confidence_layers:
            conflicts.append({
                'conflict_type': 'confidence_variance',
                'low_confidence_layers': low_confidence_layers,
                'average_confidence': avg_confidence
            })

        return {
            'conflicts': conflicts,
            'total_conflicts': len(conflicts),
            'has_conflicts': len(conflicts) > 0,
            'conflict_severity': 'high' if len(conflicts) > 2 else 'medium' if len(conflicts) > 0 else 'low'
        }

    def _generate_coordinated_recommendations(
        self,
        decision: str,
        layer_predictions: dict[str, dict[str, Any]],
        conflicts: dict[str, Any]
    ) -> list[str]:
        """Generate coordinated recommendations based on decision."""
        recommendations = []

        if decision == "Execute_All":
            recommendations.extend([
                "All layer recommendations can be executed safely",
                "Monitor execution for consistency",
                "Implement all suggested optimizations"
            ])
        elif decision == "Execute_Partial":
            recommendations.extend([
                "Execute high-confidence recommendations only",
                "Monitor partial execution impact",
                "Review low-confidence recommendations"
            ])
        elif decision == "Escalate":
            recommendations.extend([
                "Escalate to higher authority for review",
                "Document conflicting recommendations",
                "Seek human oversight for resolution"
            ])
        elif decision == "Block_All":
            recommendations.extend([
                "Block all ML recommendations due to conflicts",
                "Manual review required before execution",
                "Investigate underlying issues"
            ])
        elif decision == "Defer_Decision":
            recommendations.extend([
                "Defer execution pending further analysis",
                "Gather additional context",
                "Re-evaluate with updated information"
            ])
        elif decision == "Manual_Review":
            recommendations.extend([
                "Manual review recommended for all actions",
                "Human oversight required for execution",
                "Document review findings"
            ])
        elif decision == "Optimize_First":
            recommendations.extend([
                "Prioritize optimization recommendations",
                "Address performance issues first",
                "Execute optimization before other actions"
            ])
        else:  # Monitor_Only
            recommendations.extend([
                "Monitor current system state",
                "No immediate action required",
                "Continue observation for changes"
            ])

        # Add conflict-specific recommendations
        if conflicts.get('has_conflicts'):
            recommendations.append("Address identified conflicts before execution")

        return recommendations

    def _assess_overall_risk(
        self,
        layer_predictions: dict[str, dict[str, Any]],
        conflicts: dict[str, Any]
    ) -> dict[str, Any]:
        """Assess overall risk of coordinated decision."""
        risk_factors = {
            'confidence_risk': 0.0,
            'conflict_risk': 0.0,
            'layer_risk': 0.0
        }

        # Confidence risk (inverse of average confidence)
        confidences = [pred.get('confidence', 0.0) for pred in layer_predictions.values()]
        avg_confidence = np.mean(confidences)
        risk_factors['confidence_risk'] = 1.0 - avg_confidence

        # Conflict risk
        conflict_count = conflicts.get('total_conflicts', 0)
        risk_factors['conflict_risk'] = min(1.0, conflict_count / 5.0)  # Normalize to max 5 conflicts

        # Layer-specific risk (simplified)
        high_risk_layers = ["L5", "L6"]  # Risk and anomaly layers
        layer_risk_scores = []

        for layer in high_risk_layers:
            if layer in layer_predictions:
                pred = layer_predictions[layer]
                # Higher risk for low confidence in critical layers
                layer_risk = 1.0 - pred.get('confidence', 0.0)
                layer_risk_scores.append(layer_risk)

        risk_factors['layer_risk'] = np.mean(layer_risk_scores) if layer_risk_scores else 0.0

        # Overall risk (weighted average)
        overall_risk = (
            risk_factors['confidence_risk'] * 0.4 +
            risk_factors['conflict_risk'] * 0.4 +
            risk_factors['layer_risk'] * 0.2
        )

        return {
            'overall_risk': overall_risk,
            'risk_factors': risk_factors,
            'risk_level': 'high' if overall_risk > 0.7 else 'medium' if overall_risk > 0.4 else 'low'
        }

    def _create_execution_plan(
        self,
        decision: str,
        layer_predictions: dict[str, dict[str, Any]],
        recommendations: list[str]
    ) -> dict[str, Any]:
        """Create execution plan based on coordinated decision."""
        execution_steps = []

        if decision in ["Execute_All", "Execute_Partial"]:
            # Create execution steps for each layer
            for layer, prediction in layer_predictions.items():
                if decision == "Execute_All" or prediction.get('confidence', 0.0) > 0.6:
                    step = {
                        'layer': layer,
                        'action': prediction.get('prediction', 'unknown'),
                        'confidence': prediction.get('confidence', 0.0),
                        'priority': 'high' if prediction.get('confidence', 0.0) > 0.8 else 'medium',
                        'estimated_effort': self._estimate_layer_effort(layer, prediction.get('prediction'))
                    }
                    execution_steps.append(step)

        elif decision == "Optimize_First":
            # Prioritize optimization layers (L4, C1)
            optimization_layers = ["L4"]
            for layer in optimization_layers:
                if layer in layer_predictions:
                    prediction = layer_predictions[layer]
                    step = {
                        'layer': layer,
                        'action': prediction.get('prediction', 'unknown'),
                        'confidence': prediction.get('confidence', 0.0),
                        'priority': 'high',
                        'estimated_effort': self._estimate_layer_effort(layer, prediction.get('prediction'))
                    }
                    execution_steps.append(step)

        return {
            'execution_steps': execution_steps,
            'total_steps': len(execution_steps),
            'estimated_total_effort': sum(step.get('estimated_effort', 1) for step in execution_steps),
            'requires_monitoring': decision in ["Execute_Partial", "Monitor_Only"],
            'requires_approval': decision in ["Escalate", "Manual_Review", "Block_All"]
        }

    def _estimate_layer_effort(self, layer: str, action: str | None) -> int:
        """Estimate implementation effort for layer action."""
        effort_map = {
            "L0": 2,  # Route changes
            "L1": 3,  # Capacity planning
            "L2": 2,  # Healing selection
            "L3": 3,  # Branch ranking
            "L4": 4,  # Performance optimization
            "L5": 5,  # Risk calibration
            "L6": 3   # Anomaly detection
        }

        base_effort = effort_map.get(layer, 2)

        # Adjust based on action complexity
        if action in ["Scale_Up", "Add_Index", "Rewrite_Query"]:
            return base_effort + 1
        elif action in ["No_Action", "Monitor_Only"]:
            return max(1, base_effort - 1)

        return base_effort

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        # For ensemble model, use layer weights as importance
        feature_names = self.feature_names or list(model_input.features.keys())

        # Simplified importance based on feature names
        importance_weights = {
            'consensus_score': 0.25,
            'conflict_level': 0.20,
            'overall_risk': 0.15,
            'l5_confidence': 0.10,  # Risk layer
            'l6_confidence': 0.10,  # Anomaly layer
            'l4_confidence': 0.08,  # Performance layer
            'l3_confidence': 0.05,  # Orchestration layer
            'l2_confidence': 0.03,  # Healing layer
            'l1_confidence': 0.02,  # Capacity layer
            'l0_confidence': 0.02   # Routing layer
        }

        feature_importance = []
        for i, feature_name in enumerate(feature_names):
            importance = importance_weights.get(feature_name, 0.01)
            feature_importance.append({
                'feature_name': feature_name,
                'importance_score': importance,
                'feature_value': model_input.features.get(feature_name),
                'rank': i + 1
            })

        # Sort by importance
        feature_importance.sort(key=lambda x: x['importance_score'], reverse=True)

        # Update ranks
        for i, feature in enumerate(feature_importance):
            feature['rank'] = i + 1

        return feature_importance[:10]

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

        except Exception as e:
            return None

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for ensemble model."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for ensemble
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
        Train the ensemble model.

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

            # Convert decision type string to class index
            if isinstance(label, str):
                label = self.REVERSE_DECISION_MAPPING.get(label, 7)  # Default to Monitor_Only
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

        # Simple weight calculation (in real implementation, use proper ensemble model)
        self.model_weights = np.random.rand(len(self.class_names))
        self.model_weights = self.model_weights / np.sum(self.model_weights)

        # Store feature names and training digest
        self.feature_names = feature_names
        self._training_data_digest = training_data_digest

        self.is_loaded = True
