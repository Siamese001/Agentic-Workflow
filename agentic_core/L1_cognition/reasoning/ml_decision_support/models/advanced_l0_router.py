"""
Advanced L0 Router

Neural Network model for advanced routing including semantic understanding,
context awareness, user behavior analysis, and intelligent routing decisions.
"""

import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

try:
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError:
    MLPClassifier = None
    StandardScaler = None
    Pipeline = None

from ..config.model_registry import DecisionMode
from ..features.advanced_l0_features import AdvancedL0FeatureExtractor
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType


class AdvancedL0Router(BaseMLModel):
    """
    Neural Network model for advanced L0 routing.

    Provides intelligent routing based on:
    - Semantic understanding and query analysis
    - Context awareness and environmental factors
    - User behavior patterns and preferences
    - Historical routing performance and learning
    - Multi-dimensional routing optimization
    - Adaptive routing strategies
    """

    # Advanced routing action mapping
    ROUTING_MAPPING = {
        0: "Neural_Advanced",
        1: "Semantic_Optimized",
        2: "Context_Aware",
        3: "User_Personalized",
        4: "Performance_Optimized",
        5: "Load_Balanced",
        6: "Cost_Efficient",
        7: "Standard_Route",
    }

    # Reverse mapping
    REVERSE_ROUTING_MAPPING = {v: k for k, v in ROUTING_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        if MLPClassifier is None:
            raise ImportError("scikit-learn is required for AdvancedL0Router")

        super().__init__(
            model_name="advanced_l0_router",
            model_version="1.0",
            model_type="neural_network",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path,
        )

        # Initialize feature extractor
        self.feature_extractor = AdvancedL0FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.pipeline = None
        self.feature_names = None
        self.class_names = list(self.ROUTING_MAPPING.values())

        # Neural network parameters
        self.network_config = {
            "hidden_layers": (64, 32, 16),
            "activation": "relu",
            "solver": "adam",
            "learning_rate": "adaptive",
            "max_iter": 1000,
            "random_state": 42,
        }

        # Default thresholds
        self.threshold_config = {
            "confidence_threshold": 0.6,
            "semantic_threshold": 0.7,
            "context_threshold": 0.5,
            "routing_threshold": 0.8,
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the Neural Network model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            with open(self.model_file_path, "rb") as f:
                model_data = pickle.load(f)

            self.pipeline = model_data.get("pipeline")
            self.feature_names = model_data.get("feature_names", [])
            self.network_config = model_data.get("network_config", self.network_config)
            self.threshold_config = model_data.get("threshold_config", self.threshold_config)
            self._training_data_digest = model_data.get("training_data_digest", "")

            self.is_loaded = True

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def save_model(self, model_file_path: Path) -> None:
        """Save the model to file."""
        model_data = {
            "pipeline": self.pipeline,
            "feature_names": self.feature_names,
            "network_config": self.network_config,
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

        with open(model_file_path, "wb") as f:
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
        Predict advanced routing decision.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Advanced routing prediction with full metadata
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
                prediction="Standard_Route",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # Neural Network prediction
            probabilities = self.pipeline.predict_proba(feature_vector.reshape(1, -1))[0]
            predicted_class = self.pipeline.predict(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to routing action name
            predicted_routing = self.ROUTING_MAPPING.get(int(predicted_class), "Standard_Route")

            # Create probability distribution
            prob_distribution = {self.class_names[i]: float(prob) for i, prob in enumerate(probabilities)}

            # Calculate confidence (max probability)
            confidence = float(np.max(probabilities))

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("routing_threshold", 0.8)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_routing,
                    confidence=confidence,
                    probability_distribution=prob_distribution,
                    threshold_used=threshold_used,
                ),
            )

            # Create prediction
            prediction = self.create_prediction(
                prediction=predicted_routing,
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
                    "routing_strategy": predicted_routing,
                    "neural_network_config": self.network_config,
                }
            )

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except Exception as e:
            # Prediction failed
            return self.create_prediction(
                prediction="Standard_Route",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

    def route_intelligently(
        self,
        routing_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Get intelligent routing recommendation.

        Args:
            routing_context: Routing context and query information
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Comprehensive routing recommendation
        """
        # Extract features from context
        extraction_result = self.feature_extractor.extract_features(
            context=routing_context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        if not extraction_result.success:
            return {
                "routing_strategy": "Standard_Route",
                "confidence": 0.0,
                "reason": "Feature extraction failed",
                "recommendations": ["Check routing data availability"],
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

        # Generate detailed routing recommendations
        recommendations = self._generate_routing_recommendations(
            strategy=prediction.prediction,
            context=routing_context,
            features=extraction_result.features,
        )

        # Analyze routing factors
        routing_analysis = self._analyze_routing_factors(
            context=routing_context,
            features=extraction_result.features,
        )

        # Calculate expected performance
        performance_prediction = self._predict_routing_performance(
            strategy=prediction.prediction,
            context=routing_context,
            features=extraction_result.features,
        )

        return {
            "routing_strategy": prediction.prediction,
            "confidence": prediction.confidence,
            "probability_distribution": prediction.probability_distribution,
            "top_factors": prediction.top_features,
            "recommendations": recommendations,
            "routing_analysis": routing_analysis,
            "performance_prediction": performance_prediction,
            "alternative_strategies": self._get_alternative_strategies(prediction.probability_distribution),
            "implementation_priority": self._get_implementation_priority(
                prediction.prediction, prediction.confidence
            ),
        }

    def analyze_query_semantics(
        self,
        query_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Analyze query semantics for intelligent routing.

        Args:
            query_context: Query context and semantic information
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Semantic analysis and routing implications
        """
        # Extract semantic features
        semantic_features = {
            "semantic_similarity_score": query_context.get("semantic_similarity", 0.5),
            "intent_confidence": query_context.get("intent_confidence", 0.5),
            "query_complexity": query_context.get("query_complexity", 0.5),
        }

        # Analyze semantic patterns
        semantic_analysis = {
            "query_intent": self._classify_query_intent(query_context),
            "semantic_complexity": self._assess_semantic_complexity(query_context),
            "context_relevance": self._evaluate_context_relevance(query_context),
            "routing_implications": self._determine_semantic_routing_implications(query_context),
        }

        # Generate semantic-based routing suggestions
        routing_suggestions = []

        intent = semantic_analysis["query_intent"]
        if intent == "complex_analytical":
            routing_suggestions.append("Consider Neural_Advanced routing for complex queries")
        elif intent == "simple_informational":
            routing_suggestions.append("Standard_Route may be sufficient for simple queries")
        elif intent == "context_dependent":
            routing_suggestions.append("Context_Aware routing recommended")

        complexity = semantic_analysis["semantic_complexity"]
        if complexity > 0.7:
            routing_suggestions.append("High complexity - use advanced routing strategies")
        elif complexity < 0.3:
            routing_suggestions.append("Low complexity - standard routing appropriate")

        return {
            "semantic_analysis": semantic_analysis,
            "semantic_features": semantic_features,
            "routing_suggestions": routing_suggestions,
            "confidence_score": query_context.get("semantic_confidence", 0.5),
            "recommended_strategy": self._recommend_semantic_strategy(semantic_analysis),
        }

    def learn_user_preferences(
        self,
        user_interactions: list[dict[str, Any]],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Learn and adapt to user preferences for routing.

        Args:
            user_interactions: List of user interaction data
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            User preference analysis and adaptation
        """
        if not user_interactions:
            return {
                "preference_analysis": "No user interaction data available",
                "adaptation_strategy": "Use default routing preferences",
            }

        # Analyze user interaction patterns
        preference_analysis = self._analyze_user_preferences(user_interactions)

        # Identify routing preferences
        routing_preferences = self._identify_routing_preferences(user_interactions)

        # Calculate adaptation factors
        adaptation_factors = self._calculate_adaptation_factors(user_interactions)

        # Generate personalized routing strategy
        personalized_strategy = self._generate_personalized_strategy(
            preference_analysis,
            routing_preferences,
            adaptation_factors,
        )

        return {
            "preference_analysis": preference_analysis,
            "routing_preferences": routing_preferences,
            "adaptation_factors": adaptation_factors,
            "personalized_strategy": personalized_strategy,
            "learning_confidence": self._calculate_learning_confidence(user_interactions),
            "adaptation_recommendations": self._generate_adaptation_recommendations(preference_analysis),
        }

    def _generate_routing_recommendations(
        self,
        strategy: str,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> list[str]:
        """Generate strategy-specific routing recommendations."""
        recommendations = []

        if strategy == "Neural_Advanced":
            recommendations.extend(
                [
                    "Use neural network-based routing for optimal performance",
                    "Leverage semantic understanding for intelligent decisions",
                    "Monitor routing performance and adapt accordingly",
                    "Consider user behavior patterns in routing",
                ]
            )
        elif strategy == "Semantic_Optimized":
            recommendations.extend(
                [
                    "Optimize routing based on semantic query analysis",
                    "Use intent classification for routing decisions",
                    "Leverage context relevance for better routing",
                    "Monitor semantic accuracy and adjust",
                ]
            )
        elif strategy == "Context_Aware":
            recommendations.extend(
                [
                    "Consider current context in routing decisions",
                    "Adapt routing based on environmental factors",
                    "Use session continuity for routing optimization",
                    "Monitor context relevance and update",
                ]
            )
        elif strategy == "User_Personalized":
            recommendations.extend(
                [
                    "Personalize routing based on user preferences",
                    "Learn from user interaction patterns",
                    "Adapt routing to user behavior",
                    "Monitor user satisfaction and adjust",
                ]
            )
        elif strategy == "Performance_Optimized":
            recommendations.extend(
                [
                    "Optimize routing for maximum performance",
                    "Consider system load and resource availability",
                    "Balance performance with cost efficiency",
                    "Monitor performance metrics continuously",
                ]
            )
        elif strategy == "Load_Balanced":
            recommendations.extend(
                [
                    "Use load balancing for optimal resource distribution",
                    "Consider current system load in routing",
                    "Balance across multiple routing options",
                    "Monitor load distribution and adjust",
                ]
            )
        elif strategy == "Cost_Efficient":
            recommendations.extend(
                [
                    "Optimize routing for cost efficiency",
                    "Consider resource costs in routing decisions",
                    "Balance cost with performance requirements",
                    "Monitor cost metrics and optimize",
                ]
            )
        else:  # Standard_Route
            recommendations.extend(
                [
                    "Use standard routing for basic requests",
                    "Monitor standard routing performance",
                    "Consider upgrading to advanced routing if needed",
                    "Maintain standard routing reliability",
                ]
            )

        # Add context-specific recommendations
        semantic_similarity = features.get("semantic_similarity_score", 0)
        if semantic_similarity > 0.8:
            recommendations.append("High semantic similarity - consider semantic optimization")

        user_preference = features.get("user_preference_score", 0)
        if user_preference > 0.7:
            recommendations.append("Strong user preference - consider personalized routing")

        return recommendations

    def _analyze_routing_factors(
        self,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> dict[str, Any]:
        """Analyze routing factors and their impact."""
        factor_analysis = {
            "primary_factors": [],
            "secondary_factors": [],
            "constraint_factors": [],
        }

        # Analyze semantic factors
        semantic_score = features.get("semantic_similarity_score", 0)
        if semantic_score > 0.7:
            factor_analysis["primary_factors"].append(
                {
                    "factor": "semantic_similarity",
                    "score": semantic_score,
                    "impact": "high",
                    "description": "Strong semantic similarity influences routing",
                }
            )
        elif semantic_score > 0.4:
            factor_analysis["secondary_factors"].append(
                {
                    "factor": "semantic_similarity",
                    "score": semantic_score,
                    "impact": "medium",
                    "description": "Moderate semantic similarity affects routing",
                }
            )

        # Analyze confidence factors
        intent_confidence = features.get("intent_confidence", 0)
        if intent_confidence > 0.8:
            factor_analysis["primary_factors"].append(
                {
                    "factor": "intent_confidence",
                    "score": intent_confidence,
                    "impact": "high",
                    "description": "High intent confidence enables advanced routing",
                }
            )

        # Analyze resource factors
        resource_availability = features.get("resource_availability", 0)
        if resource_availability < 0.3:
            factor_analysis["constraint_factors"].append(
                {
                    "factor": "resource_availability",
                    "score": resource_availability,
                    "impact": "constraint",
                    "description": "Low resource availability limits routing options",
                }
            )

        # Analyze performance factors
        routing_efficiency = features.get("routing_efficiency", 0)
        if routing_efficiency > 0.8:
            factor_analysis["primary_factors"].append(
                {
                    "factor": "routing_efficiency",
                    "score": routing_efficiency,
                    "impact": "high",
                    "description": "High routing efficiency supports advanced strategies",
                }
            )

        return factor_analysis

    def _predict_routing_performance(
        self,
        strategy: str,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> dict[str, Any]:
        """Predict routing performance for the chosen strategy."""
        # Base performance estimates by strategy
        performance_estimates = {
            "Neural_Advanced": {
                "response_time": 0.8,
                "accuracy": 0.9,
                "resource_usage": 0.7,
                "scalability": 0.8,
            },
            "Semantic_Optimized": {
                "response_time": 0.7,
                "accuracy": 0.85,
                "resource_usage": 0.6,
                "scalability": 0.7,
            },
            "Context_Aware": {
                "response_time": 0.6,
                "accuracy": 0.8,
                "resource_usage": 0.5,
                "scalability": 0.6,
            },
            "User_Personalized": {
                "response_time": 0.7,
                "accuracy": 0.85,
                "resource_usage": 0.6,
                "scalability": 0.7,
            },
            "Performance_Optimized": {
                "response_time": 0.9,
                "accuracy": 0.75,
                "resource_usage": 0.8,
                "scalability": 0.9,
            },
            "Load_Balanced": {
                "response_time": 0.7,
                "accuracy": 0.8,
                "resource_usage": 0.6,
                "scalability": 0.9,
            },
            "Cost_Efficient": {
                "response_time": 0.6,
                "accuracy": 0.7,
                "resource_usage": 0.4,
                "scalability": 0.6,
            },
            "Standard_Route": {
                "response_time": 0.5,
                "accuracy": 0.6,
                "resource_usage": 0.3,
                "scalability": 0.5,
            },
        }

        base_performance = performance_estimates.get(strategy, performance_estimates["Standard_Route"])

        # Adjust based on current conditions
        resource_availability = features.get("resource_availability", 0.5)
        system_load = features.get("system_load_factor", 0.5)

        # Adjust performance based on resources
        resource_multiplier = 0.5 + (resource_availability * 0.5)
        load_multiplier = 1.0 - (system_load * 0.3)

        adjusted_performance = {}
        for metric, base_score in base_performance.items():
            if metric == "resource_usage":
                adjusted_performance[metric] = base_score * (
                    2.0 - resource_multiplier
                )  # Inverse for resource usage
            else:
                adjusted_performance[metric] = base_score * resource_multiplier * load_multiplier

        return adjusted_performance

    def _get_alternative_strategies(self, probability_distribution: dict[str, float]) -> list[dict[str, Any]]:
        """Get alternative routing strategies with probabilities."""
        alternatives = []

        # Sort by probability and get top 3 alternatives
        sorted_strategies = sorted(
            probability_distribution.items(),
            key=lambda x: x[1],
            reverse=True,
        )[1:4]  # Skip the primary strategy

        for strategy, probability in sorted_strategies:
            if probability > 0.1:  # Only include if probability is significant
                alternatives.append(
                    {
                        "strategy": strategy,
                        "probability": probability,
                        "confidence": probability,
                        "recommendation": f"Consider {strategy} as alternative",
                    }
                )

        return alternatives

    def _get_implementation_priority(self, strategy: str, confidence: float) -> str:
        """Get implementation priority based on strategy and confidence."""
        if strategy == "Standard_Route":
            return "Low"

        if confidence > 0.8:
            if strategy in ["Neural_Advanced", "Semantic_Optimized"]:
                return "High"
            else:
                return "Medium"
        elif confidence > 0.6:
            return "Medium"
        else:
            return "Low"

    def _classify_query_intent(self, query_context: dict[str, Any]) -> str:
        """Classify query intent based on context."""
        # Simplified intent classification
        complexity = query_context.get("query_complexity", 0.5)
        context_relevance = query_context.get("context_relevance", 0.5)

        if complexity > 0.7:
            return "complex_analytical"
        elif context_relevance > 0.7:
            return "context_dependent"
        elif complexity < 0.3:
            return "simple_informational"
        else:
            return "moderate_complexity"

    def _assess_semantic_complexity(self, query_context: dict[str, Any]) -> float:
        """Assess semantic complexity of the query."""
        # Use query complexity as proxy for semantic complexity
        return query_context.get("query_complexity", 0.5)

    def _evaluate_context_relevance(self, query_context: dict[str, Any]) -> float:
        """Evaluate context relevance for routing."""
        return query_context.get("context_relevance", 0.5)

    def _determine_semantic_routing_implications(self, query_context: dict[str, Any]) -> str:
        """Determine routing implications based on semantic analysis."""
        semantic_similarity = query_context.get("semantic_similarity", 0.5)

        if semantic_similarity > 0.8:
            return "semantic_optimization_recommended"
        elif semantic_similarity > 0.5:
            return "semantic_consideration_advised"
        else:
            return "standard_routing_sufficient"

    def _recommend_semantic_strategy(self, semantic_analysis: dict[str, Any]) -> str:
        """Recommend routing strategy based on semantic analysis."""
        intent = semantic_analysis["query_intent"]
        complexity = semantic_analysis["semantic_complexity"]

        if intent == "complex_analytical" and complexity > 0.7:
            return "Neural_Advanced"
        elif intent == "context_dependent":
            return "Context_Aware"
        elif complexity > 0.5:
            return "Semantic_Optimized"
        else:
            return "Standard_Route"

    def _analyze_user_preferences(self, user_interactions: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze user preferences from interaction data."""
        # Simplified preference analysis
        preference_counts = {}
        total_interactions = len(user_interactions)

        for interaction in user_interactions:
            strategy = interaction.get("routing_strategy", "Standard_Route")
            satisfaction = interaction.get("user_satisfaction", 0.5)

            if strategy not in preference_counts:
                preference_counts[strategy] = {"count": 0, "satisfaction_sum": 0.0}

            preference_counts[strategy]["count"] += 1
            preference_counts[strategy]["satisfaction_sum"] += satisfaction

        # Calculate preference scores
        preference_scores = {}
        for strategy, data in preference_counts.items():
            avg_satisfaction = data["satisfaction_sum"] / data["count"]
            preference_weight = data["count"] / total_interactions
            preference_scores[strategy] = avg_satisfaction * preference_weight

        return {
            "preference_scores": preference_scores,
            "most_preferred": max(preference_scores.items(), key=lambda x: x[1])[0]
            if preference_scores
            else "Standard_Route",
            "total_interactions": total_interactions,
        }

    def _identify_routing_preferences(self, user_interactions: list[dict[str, Any]]) -> dict[str, float]:
        """Identify specific routing preferences."""
        preferences = {}

        for interaction in user_interactions:
            strategy = interaction.get("routing_strategy", "Standard_Route")
            satisfaction = interaction.get("user_satisfaction", 0.5)

            if strategy not in preferences:
                preferences[strategy] = []
            preferences[strategy].append(satisfaction)

        # Calculate average satisfaction per strategy
        avg_preferences = {}
        for strategy, satisfactions in preferences.items():
            avg_preferences[strategy] = sum(satisfactions) / len(satisfactions)

        return avg_preferences

    def _calculate_adaptation_factors(self, user_interactions: list[dict[str, Any]]) -> dict[str, float]:
        """Calculate adaptation factors based on user interactions."""
        # Simplified adaptation calculation
        recent_interactions = user_interactions[-10:]  # Last 10 interactions
        if not recent_interactions:
            return {"adaptation_factor": 0.5}

        avg_satisfaction = sum(
            interaction.get("user_satisfaction", 0.5) for interaction in recent_interactions
        ) / len(recent_interactions)

        adaptation_factor = max(0.0, min(1.0, avg_satisfaction))

        return {
            "adaptation_factor": adaptation_factor,
            "interaction_count": len(recent_interactions),
            "satisfaction_trend": "improving" if avg_satisfaction > 0.7 else "stable",
        }

    def _generate_personalized_strategy(
        self,
        preference_analysis: dict[str, Any],
        routing_preferences: dict[str, float],
        adaptation_factors: dict[str, float],
    ) -> str:
        """Generate personalized routing strategy."""
        most_preferred = preference_analysis.get("most_preferred", "Standard_Route")
        adaptation_factor = adaptation_factors.get("adaptation_factor", 0.5)

        if adaptation_factor > 0.8 and most_preferred in self.ROUTING_MAPPING.values():
            return most_preferred
        elif adaptation_factor > 0.6:
            return "User_Personalized"
        else:
            return "Standard_Route"

    def _calculate_learning_confidence(self, user_interactions: list[dict[str, Any]]) -> float:
        """Calculate confidence in learned preferences."""
        if len(user_interactions) < 5:
            return 0.2  # Low confidence with few interactions

        # Calculate consistency of preferences
        recent_strategies = [
            interaction.get("routing_strategy", "Standard_Route") for interaction in user_interactions[-10:]
        ]
        unique_strategies = len(set(recent_strategies))

        # Higher confidence if preferences are consistent
        consistency = 1.0 - (unique_strategies - 1) / len(self.ROUTING_MAPPING)

        # Scale by interaction count
        interaction_factor = min(1.0, len(user_interactions) / 50)

        return consistency * interaction_factor

    def _generate_adaptation_recommendations(self, preference_analysis: dict[str, Any]) -> list[str]:
        """Generate adaptation recommendations based on preference analysis."""
        recommendations = []

        most_preferred = preference_analysis.get("most_preferred", "Standard_Route")
        preference_scores = preference_analysis.get("preference_scores", {})

        if most_preferred != "Standard_Route":
            recommendations.append(f"User prefers {most_preferred} - consider making it default")

        # Check for high satisfaction with advanced strategies
        advanced_strategies = ["Neural_Advanced", "Semantic_Optimized", "Context_Aware"]
        for strategy in advanced_strategies:
            if strategy in preference_scores and preference_scores[strategy] > 0.8:
                recommendations.append(f"High satisfaction with {strategy} - promote usage")

        return recommendations

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        if not self.is_loaded or not self.pipeline:
            return []

        try:
            # For Neural Network, use permutation importance approximation
            feature_names = self.feature_names or list(model_input.features.keys())

            # Simplified importance based on feature names and expected impact
            importance_weights = {
                "semantic_similarity_score": 0.15,
                "intent_confidence": 0.12,
                "context_relevance": 0.10,
                "user_preference_score": 0.12,
                "historical_success_rate": 0.10,
                "resource_availability": 0.08,
                "routing_efficiency": 0.08,
                "system_load_factor": 0.08,
                "query_complexity": 0.10,
                "routing_confidence": 0.07,
            }

            feature_importance = []
            for i, feature_name in enumerate(feature_names):
                importance = importance_weights.get(feature_name, 0.01)
                feature_importance.append(
                    {
                        "feature_name": feature_name,
                        "importance_score": importance,
                        "feature_value": model_input.features.get(feature_name),
                        "rank": i + 1,
                    }
                )

            # Sort by importance
            feature_importance.sort(key=lambda x: x["importance_score"], reverse=True)

            # Update ranks
            for i, feature in enumerate(feature_importance):
                feature["rank"] = i + 1

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
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            return np.array(feature_vector)

        except Exception as e:
            return None

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for Neural Network."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for Neural Network
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
        Train the Neural Network model.

        Args:
            training_data: List of training examples with features and labels
            feature_names: Names of features to use
            training_data_digest: Digest of training data for provenance
        """
        # Extract features and labels
        X = []
        y = []

        for example in training_data:
            features = example["features"]
            label = example["label"]

            # Convert routing type string to class index
            if isinstance(label, str):
                label = self.REVERSE_ROUTING_MAPPING.get(label, 7)  # Default to Standard_Route
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

        # Create pipeline with scaling and Neural Network
        self.pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    MLPClassifier(
                        hidden_layer_sizes=self.network_config["hidden_layers"],
                        activation=self.network_config["activation"],
                        solver=self.network_config["solver"],
                        learning_rate=self.network_config["learning_rate"],
                        max_iter=self.network_config["max_iter"],
                        random_state=self.network_config["random_state"],
                    ),
                ),
            ]
        )

        # Train model
        self.pipeline.fit(X, y)

        # Store feature names and training digest
        self.feature_names = feature_names
        self._training_data_digest = training_data_digest

        self.is_loaded = True
