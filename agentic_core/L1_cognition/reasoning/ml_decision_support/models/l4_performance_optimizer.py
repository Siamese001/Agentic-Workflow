"""
L4 Performance Optimizer

Random Forest model for performance optimization including
bottleneck identification, resource allocation, and performance tuning recommendations.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError:
    RandomForestClassifier = None
    StandardScaler = None
    Pipeline = None

from ..config.model_registry import DecisionMode
from ..features.l4_features import L4FeatureExtractor
from ._pickle_io import safe_pickle_dump, safe_pickle_load
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType
from tqdm import tqdm


class L4PerformanceOptimizer(BaseMLModel):
    """
    Random Forest model for L4 performance optimization.

    Optimizes system performance based on:
    - Response time trends and throughput variance
    - Resource utilization patterns and bottlenecks
    - Optimization opportunities and SLA compliance
    - Cost efficiency and resource waste
    - Performance prediction and tuning recommendations

    Always operates in advisory mode - provides optimization recommendations.
    """

    # Optimization action mapping
    OPTIMIZATION_MAPPING = {
        0: "Scale_Up",
        1: "Scale_Down",
        2: "Optimize_Resources",
        3: "Tune_Configuration",
        4: "Add_Caching",
        5: "Load_Balance",
        6: "No_Action",
    }

    # Reverse mapping
    REVERSE_OPTIMIZATION_MAPPING = {v: k for k, v in OPTIMIZATION_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        if RandomForestClassifier is None:
            raise ImportError("scikit-learn is required for L4PerformanceOptimizer")

        super().__init__(
            model_name="l4_performance_optimizer",
            model_version="1.0",
            model_type="random_forest",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path,
        )

        # Initialize feature extractor
        self.feature_extractor = L4FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.pipeline = None
        self.feature_names = None
        self.class_names = list(self.OPTIMIZATION_MAPPING.values())

        # Default thresholds
        self.threshold_config = {
            "confidence_threshold": 0.6,
            "optimization_threshold": 0.5,
            "action_threshold": 0.7,
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the Random Forest model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            model_data = safe_pickle_load(self.model_file_path)

            self.pipeline = model_data.get("pipeline")
            self.feature_names = model_data.get("feature_names", [])
            self.threshold_config = model_data.get("threshold_config", self.threshold_config)
            self._training_data_digest = model_data.get("training_data_digest", "")

            self.is_loaded = True

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            raise RuntimeError(f'Failed to load model: {e}') from e

    def save_model(self, model_file_path: Path) -> None:
        """Save the model to file."""
        model_data = {
            "pipeline": self.pipeline,
            "feature_names": self.feature_names,
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
        Predict optimization action for performance improvement.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Optimization action prediction with full metadata
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
                prediction="No_Action",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # Random Forest prediction
            probabilities = self.pipeline.predict_proba(feature_vector.reshape(1, -1))[0]
            predicted_class = self.pipeline.predict(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to optimization action name
            predicted_action = self.OPTIMIZATION_MAPPING.get(int(predicted_class), "No_Action")

            # Create probability distribution
            prob_distribution = {self.class_names[i]: float(prob) for i, prob in enumerate(probabilities)}

            # Calculate confidence (max probability)
            confidence = float(np.max(probabilities))

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("optimization_threshold", 0.5)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_action,
                    confidence=confidence,
                    probability_distribution=prob_distribution,
                    threshold_used=threshold_used,
                ),
            )

            # Create prediction
            prediction = self.create_prediction(
                prediction=predicted_action,
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
                    "optimization_action": predicted_action,
                    "requires_implementation": predicted_action != "No_Action",
                }
            )

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as e:
            # Prediction failed
            return self.create_prediction(
                prediction="No_Action",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

    def optimize_performance(
        self,
        performance_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Get comprehensive performance optimization recommendations.

        Args:
            performance_context: Performance metrics and context
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Comprehensive optimization recommendations
        """
        # Extract features from context
        extraction_result = self.feature_extractor.extract_features(
            context=performance_context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        if not extraction_result.success:
            return {
                "optimization_action": "No_Action",
                "confidence": 0.0,
                "reason": "Feature extraction failed",
                "recommendations": ["Check performance data availability"],
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

        # Generate detailed recommendations
        recommendations = self._generate_optimization_recommendations(
            action=prediction.prediction,
            context=performance_context,
            features=extraction_result.features,
        )

        # Calculate expected impact
        expected_impact = self._calculate_expected_impact(
            action=prediction.prediction,
            context=performance_context,
        )

        return {
            "optimization_action": prediction.prediction,
            "confidence": prediction.confidence,
            "probability_distribution": prediction.probability_distribution,
            "top_factors": prediction.top_features,
            "recommendations": recommendations,
            "expected_impact": expected_impact,
            "implementation_priority": self._get_implementation_priority(
                prediction.prediction, prediction.confidence
            ),
            "estimated_effort": self._estimate_implementation_effort(prediction.prediction),
            "risk_level": self._assess_implementation_risk(prediction.prediction, performance_context),
        }

    def get_performance_insights(
        self,
        performance_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Get detailed performance insights and analysis.

        Args:
            performance_context: Performance metrics and context
            trace_id: Trace ID
            replay_key: Replay key
            policy_hash: Policy hash

        Returns:
            Comprehensive performance insights
        """
        # Extract features
        extraction_result = self.feature_extractor.extract_features(
            context=performance_context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        if not extraction_result.success:
            return {
                "insights": [],
                "analysis": "Feature extraction failed",
                "recommendations": [],
            }

        features = extraction_result.features

        # Generate insights based on feature values
        insights = []

        # Response time trend insight
        response_trend = features.get("response_time_trend", 0)
        if response_trend > 0.2:
            insights.append(
                {
                    "type": "performance_degradation",
                    "severity": "high",
                    "description": "Response times are increasing significantly",
                    "impact": "User experience and SLA compliance",
                }
            )
        elif response_trend < -0.2:
            insights.append(
                {
                    "type": "performance_improvement",
                    "severity": "low",
                    "description": "Response times are improving",
                    "impact": "Positive trend in performance",
                }
            )

        # Resource utilization insight
        cpu_util = features.get("cpu_utilization_avg", 0)
        memory_util = features.get("memory_utilization_avg", 0)

        if cpu_util > 80:
            insights.append(
                {
                    "type": "resource_bottleneck",
                    "severity": "high",
                    "description": f"High CPU utilization ({cpu_util:.1f}%)",
                    "impact": "System performance and scalability",
                }
            )

        if memory_util > 80:
            insights.append(
                {
                    "type": "resource_bottleneck",
                    "severity": "high",
                    "description": f"High memory utilization ({memory_util:.1f}%)",
                    "impact": "System stability and performance",
                }
            )

        # SLA compliance insight
        sla_compliance = features.get("sla_compliance_rate", 1.0)
        if sla_compliance < 0.95:
            insights.append(
                {
                    "type": "sla_violation",
                    "severity": "high" if sla_compliance < 0.9 else "medium",
                    "description": f"SLA compliance rate is {sla_compliance:.1%}",
                    "impact": "Service level agreement compliance",
                }
            )

        # Optimization potential insight
        optimization_potential = features.get("optimization_potential", 0)
        if optimization_potential > 0.7:
            insights.append(
                {
                    "type": "optimization_opportunity",
                    "severity": "medium",
                    "description": "High optimization potential detected",
                    "impact": "Significant performance improvements possible",
                }
            )

        # Cost efficiency insight
        cost_efficiency = features.get("cost_efficiency_score", 0.5)
        if cost_efficiency < 0.5:
            insights.append(
                {
                    "type": "cost_inefficiency",
                    "severity": "medium",
                    "description": "Low cost efficiency detected",
                    "impact": "Operational costs and resource utilization",
                }
            )

        # Generate analysis summary
        analysis = self._generate_performance_analysis(features, insights)

        return {
            "insights": insights,
            "analysis": analysis,
            "feature_analysis": {
                "response_time_trend": response_trend,
                "cpu_utilization": cpu_util,
                "memory_utilization": memory_util,
                "sla_compliance": sla_compliance,
                "optimization_potential": optimization_potential,
                "cost_efficiency": cost_efficiency,
            },
            "recommendations": [
                insight["description"] for insight in insights if insight["severity"] in ["high", "medium"]
            ],
        }

    def _generate_optimization_recommendations(
        self,
        action: str,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> list[str]:
        """Generate action-specific optimization recommendations."""
        recommendations = []

        if action == "Scale_Up":
            recommendations.extend(
                [
                    "Increase CPU and memory resources",
                    "Consider vertical scaling for better performance",
                    "Monitor resource utilization after scaling",
                    "Update capacity planning forecasts",
                ]
            )
        elif action == "Scale_Down":
            recommendations.extend(
                [
                    "Reduce allocated resources to save costs",
                    "Implement auto-scaling policies",
                    "Monitor performance after scaling down",
                    "Ensure SLA compliance is maintained",
                ]
            )
        elif action == "Optimize_Resources":
            recommendations.extend(
                [
                    "Analyze resource utilization patterns",
                    "Implement resource pooling",
                    "Optimize container configurations",
                    "Consider right-sizing instances",
                ]
            )
        elif action == "Tune_Configuration":
            recommendations.extend(
                [
                    "Review and optimize system configurations",
                    "Adjust timeout and retry policies",
                    "Optimize database connection pools",
                    "Fine-tune caching parameters",
                ]
            )
        elif action == "Add_Caching":
            recommendations.extend(
                [
                    "Implement application-level caching",
                    "Add CDN for static content",
                    "Optimize cache hit rates",
                    "Consider distributed caching",
                ]
            )
        elif action == "Load_Balance":
            recommendations.extend(
                [
                    "Implement load balancing across instances",
                    "Configure health checks",
                    "Optimize load balancing algorithms",
                    "Consider geographic load distribution",
                ]
            )
        else:  # No_Action
            recommendations.extend(
                [
                    "Current performance is optimal",
                    "Continue monitoring for changes",
                    "Maintain current configuration",
                    "Regular performance reviews recommended",
                ]
            )

        # Add context-specific recommendations
        bottleneck_severity = features.get("bottleneck_severity", 0)
        if bottleneck_severity > 0.7:
            recommendations.append("Address identified bottlenecks immediately")

        return recommendations

    def _calculate_expected_impact(
        self,
        action: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate expected impact of optimization action."""
        # Base impact estimates by action type
        impact_estimates = {
            "Scale_Up": {
                "performance_improvement": 0.4,
                "cost_increase": 0.3,
                "complexity_change": 0.2,
            },
            "Scale_Down": {
                "performance_improvement": -0.1,
                "cost_increase": -0.4,
                "complexity_change": -0.1,
            },
            "Optimize_Resources": {
                "performance_improvement": 0.3,
                "cost_increase": 0.0,
                "complexity_change": 0.1,
            },
            "Tune_Configuration": {
                "performance_improvement": 0.2,
                "cost_increase": 0.0,
                "complexity_change": 0.1,
            },
            "Add_Caching": {
                "performance_improvement": 0.5,
                "cost_increase": 0.1,
                "complexity_change": 0.2,
            },
            "Load_Balance": {
                "performance_improvement": 0.3,
                "cost_increase": 0.2,
                "complexity_change": 0.3,
            },
            "No_Action": {
                "performance_improvement": 0.0,
                "cost_increase": 0.0,
                "complexity_change": 0.0,
            },
        }

        base_impact = impact_estimates.get(action, impact_estimates["No_Action"])

        # Adjust based on current performance
        current_performance = context.get("performance", {})
        sla_compliance = current_performance.get("sla_compliance_rate", 1.0)

        # Higher impact if performance is poor
        if sla_compliance < 0.9:
            performance_multiplier = 1.5
        elif sla_compliance < 0.95:
            performance_multiplier = 1.2
        else:
            performance_multiplier = 1.0

        # Adjust performance improvement
        adjusted_impact = base_impact.copy()
        adjusted_impact["performance_improvement"] *= performance_multiplier

        return adjusted_impact

    def _get_implementation_priority(self, action: str, confidence: float) -> str:
        """Get implementation priority based on action and confidence."""
        if action == "No_Action":
            return "Low"

        if confidence > 0.8:
            if action in ["Scale_Up", "Add_Caching"]:
                return "High"
            else:
                return "Medium"
        elif confidence > 0.6:
            return "Medium"
        else:
            return "Low"

    def _estimate_implementation_effort(self, action: str) -> str:
        """Estimate implementation effort for optimization action."""
        effort_estimates = {
            "Scale_Up": "Low",
            "Scale_Down": "Low",
            "Optimize_Resources": "Medium",
            "Tune_Configuration": "Medium",
            "Add_Caching": "High",
            "Load_Balance": "High",
            "No_Action": "None",
        }

        return effort_estimates.get(action, "Medium")

    def _assess_implementation_risk(self, action: str, context: dict[str, Any]) -> str:
        """Assess implementation risk for optimization action."""
        # Base risk levels
        risk_levels = {
            "Scale_Up": "Low",
            "Scale_Down": "Medium",
            "Optimize_Resources": "Low",
            "Tune_Configuration": "Medium",
            "Add_Caching": "Low",
            "Load_Balance": "Medium",
            "No_Action": "None",
        }

        base_risk = risk_levels.get(action, "Medium")

        # Adjust risk based on system criticality
        system_criticality = context.get("system", {}).get("criticality", "medium")

        if system_criticality == "high" and action not in ["No_Action", "Tune_Configuration"]:
            return "High"
        elif system_criticality == "low":
            return "Low"

        return base_risk

    def _generate_performance_analysis(
        self, features: dict[str, float], insights: list[dict[str, Any]]
    ) -> str:
        """Generate performance analysis summary."""
        analysis_parts = []

        # Overall performance status
        sla_compliance = features.get("sla_compliance_rate", 1.0)
        if sla_compliance >= 0.95:
            analysis_parts.append("System performance is healthy with good SLA compliance.")
        elif sla_compliance >= 0.9:
            analysis_parts.append("System performance is acceptable but could be improved.")
        else:
            analysis_parts.append("System performance requires attention due to SLA violations.")

        # Resource utilization
        cpu_util = features.get("cpu_utilization_avg", 0)
        memory_util = features.get("memory_utilization_avg", 0)

        if cpu_util > 80 or memory_util > 80:
            analysis_parts.append("High resource utilization detected, potential bottlenecks present.")
        elif cpu_util < 30 and memory_util < 30:
            analysis_parts.append("Low resource utilization indicates potential over-provisioning.")
        else:
            analysis_parts.append("Resource utilization is within optimal range.")

        # Optimization opportunities
        optimization_potential = features.get("optimization_potential", 0)
        if optimization_potential > 0.7:
            analysis_parts.append("Significant optimization opportunities available.")
        elif optimization_potential > 0.4:
            analysis_parts.append("Moderate optimization opportunities exist.")
        else:
            analysis_parts.append("System is well-optimized.")

        # Cost efficiency
        cost_efficiency = features.get("cost_efficiency_score", 0.5)
        if cost_efficiency < 0.5:
            analysis_parts.append("Cost efficiency could be improved.")
        else:
            analysis_parts.append("Cost efficiency is acceptable.")

        return " ".join(analysis_parts)

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        if not self.is_loaded or not self.pipeline:
            return []

        try:
            # Get feature importances from Random Forest
            rf_model = self.pipeline.named_steps["classifier"]
            importances = rf_model.feature_importances_

            # Get feature names
            feature_names = self.feature_names or list(model_input.features.keys())

            # Create feature importance list
            feature_importance = []
            for i, (name, importance) in tqdm(
                enumerate(zip(feature_names, importances)), desc="Processing", unit="item"
            ):
                feature_importance.append(
                    {
                        "feature_name": name,
                        "importance_score": float(importance),
                        "feature_value": model_input.features.get(name),
                        "rank": i + 1,
                        "relative_importance": float(importance / max(importances))
                        if max(importances) > 0
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

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as e:
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

        except (
            TypeError,
            ValueError,
        ) as _fe:  # guardian: allow-return-none-swallow -- _extract_feature_vector: Optional return by contract, callers explicitly handle None, warning now logged
            logging.getLogger(__name__).warning("Feature vector construction failed: %s", _fe)
            return None

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for Random Forest."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for Random Forest
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
        Train the Random Forest model.

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

            # Convert action type string to class index
            if isinstance(label, str):
                label = self.REVERSE_OPTIMIZATION_MAPPING.get(label, 6)  # Default to No_Action
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

        # Create pipeline with scaling and Random Forest
        self.pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=100,
                        max_depth=10,
                        min_samples_split=5,
                        min_samples_leaf=2,
                        random_state=42,
                        n_jobs=-1,
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
