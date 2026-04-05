"""
L1 Capacity Planner

Time series forecasting model for capacity planning including
demand prediction, resource allocation, scaling recommendations,
and capacity optimization strategies.
"""

import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from ..config.model_registry import DecisionMode
from ..features.l1_features import L1FeatureExtractor
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType


class L1CapacityPlanner(BaseMLModel):
    """
    Time series forecasting model for L1 capacity planning.

    Plans capacity based on:
    - Traffic growth patterns and demand forecasting
    - Resource utilization trends and scaling requirements
    - Seasonal patterns and anomaly detection
    - Cost optimization and efficiency analysis
    - Capacity buffer management and provisioning
    - Performance impact prediction
    """

    # Capacity action mapping
    CAPACITY_MAPPING = {
        0: "Scale_Up_Aggressive",
        1: "Scale_Up_Moderate",
        2: "Scale_Up_Conservative",
        3: "Maintain_Current",
        4: "Scale_Down_Conservative",
        5: "Scale_Down_Moderate",
        6: "Scale_Down_Aggressive",
        7: "Reallocate_Resources"
    }

    # Reverse mapping
    REVERSE_CAPACITY_MAPPING = {v: k for k, v in CAPACITY_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        super().__init__(
            model_name="l1_capacity_planner",
            model_version="1.0",
            model_type="time_series",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path
        )

        # Initialize feature extractor
        self.feature_extractor = L1FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components (simplified time series model)
        self.model_weights = None
        self.feature_names = None
        self.class_names = list(self.CAPACITY_MAPPING.values())

        # Time series parameters
        self.lookback_window = 30  # days
        self.forecast_horizon = 7  # days

        # Default thresholds
        self.threshold_config = {
            "high_utilization_threshold": 0.8,
            "low_utilization_threshold": 0.3,
            "growth_rate_threshold": 0.1,
            "volatility_threshold": 0.3
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the time series model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            with open(self.model_file_path, 'rb') as f:
                model_data = pickle.load(f)

            self.model_weights = model_data.get('model_weights')
            self.feature_names = model_data.get('feature_names', [])
            self.threshold_config = model_data.get('threshold_config', self.threshold_config)
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
            'training_data_digest': getattr(self, '_training_data_digest', ''),
            'model_metadata': {
                'model_name': self.model_name,
                'model_version': self.model_version,
                'model_type': self.model_type,
                'prediction_type': self.prediction_type.value,
                'class_names': self.class_names,
                'feature_schema_digest': self.feature_schema.schema_digest,
                'saved_at': datetime.now().isoformat(),
                'lookback_window': self.lookback_window,
                'forecast_horizon': self.forecast_horizon
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
        Predict capacity planning action.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Capacity planning prediction with full metadata
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
                prediction="Maintain_Current",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # Time series prediction (simplified)
            class_probabilities = self._predict_time_series(feature_vector)
            predicted_class = np.argmax(class_probabilities)

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to capacity action name
            predicted_action = self.CAPACITY_MAPPING.get(int(predicted_class), "Maintain_Current")

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
            threshold_used = self.threshold_config.get("high_utilization_threshold", 0.8)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_action,
                    confidence=confidence,
                    probability_distribution=prob_distribution,
                    threshold_used=threshold_used
                )
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
                'capacity_action': predicted_action,
                'requires_scaling': predicted_action != "Maintain_Current"
            })

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except Exception as e:
            # Prediction failed
            return self.create_prediction(
                prediction="Maintain_Current",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

    def plan_capacity(
        self,
        capacity_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str
    ) -> dict[str, Any]:
        """
        Get comprehensive capacity planning recommendations.

        Args:
            capacity_context: Capacity metrics and context
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Comprehensive capacity planning recommendations
        """
        # Extract features from context
        extraction_result = self.feature_extractor.extract_features(
            context=capacity_context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash
        )

        if not extraction_result.success:
            return {
                'capacity_action': 'Maintain_Current',
                'confidence': 0.0,
                'reason': 'Feature extraction failed',
                'recommendations': ['Check capacity data availability']
            }

        # Validate input
        model_input = self.validate_input(extraction_result.features)
        model_input.feature_provenance = extraction_result.provenance

        # Make prediction
        prediction = self.predict(
            model_input=model_input,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash
        )

        # Generate detailed recommendations
        recommendations = self._generate_capacity_recommendations(
            action=prediction.prediction,
            context=capacity_context,
            features=extraction_result.features
        )

        # Generate demand forecast
        demand_forecast = self._generate_demand_forecast(capacity_context, extraction_result.features)

        # Calculate resource requirements
        resource_requirements = self._calculate_resource_requirements(
            action=prediction.prediction,
            context=capacity_context,
            forecast=demand_forecast
        )

        # Assess cost implications
        cost_analysis = self._analyze_cost_impact(
            action=prediction.prediction,
            context=capacity_context,
            requirements=resource_requirements
        )

        return {
            'capacity_action': prediction.prediction,
            'confidence': prediction.confidence,
            'probability_distribution': prediction.probability_distribution,
            'top_factors': prediction.top_features,
            'recommendations': recommendations,
            'demand_forecast': demand_forecast,
            'resource_requirements': resource_requirements,
            'cost_analysis': cost_analysis,
            'implementation_timeline': self._estimate_implementation_timeline(prediction.prediction),
            'risk_assessment': self._assess_capacity_risks(prediction.prediction, capacity_context)
        }

    def forecast_demand(
        self,
        historical_data: list[dict[str, Any]],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        forecast_days: int = 7
    ) -> dict[str, Any]:
        """
        Generate demand forecast using time series analysis.

        Args:
            historical_data: Historical demand data points
            forecast_days: Number of days to forecast
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Demand forecast with confidence intervals
        """
        if len(historical_data) < 7:
            return {
                'error': 'Insufficient historical data',
                'minimum_required': 7,
                'provided': len(historical_data)
            }

        # Extract demand values
        demand_values = [point.get('demand', 0) for point in historical_data]
        timestamps = [point.get('timestamp') for point in historical_data]

        # Simple time series forecasting (moving average with trend)
        if len(demand_values) >= 14:
            # Use 14-day moving average for trend
            ma_period = 14
        else:
            ma_period = len(demand_values) // 2

        # Calculate moving average and trend
        moving_avg = []
        for i in range(ma_period, len(demand_values)):
            avg = sum(demand_values[i-ma_period:i]) / ma_period
            moving_avg.append(avg)

        # Calculate trend
        if len(moving_avg) >= 2:
            trend = (moving_avg[-1] - moving_avg[0]) / len(moving_avg)
        else:
            trend = 0.0

        # Generate forecast
        last_demand = demand_values[-1]
        forecast = []

        for day in range(1, forecast_days + 1):
            # Apply trend and some randomness
            forecast_demand = last_demand + (trend * day)

            # Add seasonal adjustment (simplified)
            seasonal_factor = 1.0 + 0.1 * np.sin(2 * np.pi * day / 7)  # Weekly pattern
            forecast_demand *= seasonal_factor

            # Ensure non-negative
            forecast_demand = max(0, forecast_demand)

            forecast.append({
                'day': day,
                'forecast_demand': forecast_demand,
                'confidence': max(0.5, 1.0 - (day * 0.1))  # Decreasing confidence
            })

        return {
            'forecast': forecast,
            'trend': trend,
            'method': 'moving_average_with_trend',
            'data_points_used': len(demand_values),
            'forecast_period_days': forecast_days
        }

    def _predict_time_series(self, feature_vector: np.ndarray) -> np.ndarray:
        """Simplified time series prediction."""
        if self.model_weights is None:
            # Initialize with default weights
            self.model_weights = np.random.rand(len(self.class_names))
            self.model_weights = self.model_weights / np.sum(self.model_weights)

        # Simple linear combination with feature weights
        # In a real implementation, this would be a proper time series model
        class_scores = np.zeros(len(self.class_names))

        # Feature influence on different classes (simplified)
        feature_influence = {
            0: [0.3, 0.1, 0.0, -0.1, -0.2, -0.3, -0.4, -0.2],  # Scale_Up_Aggressive
            1: [0.2, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.1],  # Scale_Up_Moderate
            2: [0.1, 0.2, 0.2, 0.1, 0.0, -0.1, -0.2, 0.0],   # Scale_Up_Conservative
            3: [0.0, 0.1, 0.2, 0.2, 0.2, 0.1, 0.0, 0.1],   # Maintain_Current
            4: [-0.1, 0.0, 0.1, 0.2, 0.2, 0.2, 0.1, 0.2],  # Scale_Down_Conservative
            5: [-0.2, -0.1, 0.0, 0.1, 0.2, 0.2, 0.2, 0.3],  # Scale_Down_Moderate
            6: [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4],  # Scale_Down_Aggressive
            7: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]    # Reallocate_Resources
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

    def _generate_capacity_recommendations(
        self,
        action: str,
        context: dict[str, Any],
        features: dict[str, float]
    ) -> list[str]:
        """Generate action-specific capacity recommendations."""
        recommendations = []

        if action.startswith("Scale_Up"):
            recommendations.extend([
                "Increase resource allocation to meet demand",
                "Monitor utilization after scaling",
                "Update capacity planning forecasts",
                "Consider auto-scaling policies"
            ])

            if "Aggressive" in action:
                recommendations.append("Implement aggressive scaling for high growth")
            elif "Moderate" in action:
                recommendations.append("Moderate scaling with buffer capacity")
            else:  # Conservative
                recommendations.append("Conservative scaling with minimal buffer")

        elif action.startswith("Scale_Down"):
            recommendations.extend([
                "Reduce resource allocation to optimize costs",
                "Monitor performance after scaling down",
                "Ensure SLA compliance is maintained",
                "Consider rightsizing instances"
            ])

            if "Aggressive" in action:
                recommendations.append("Aggressive cost optimization")
            elif "Moderate" in action:
                recommendations.append("Balanced cost and performance")
            else:  # Conservative
                recommendations.append("Conservative cost reduction")

        elif action == "Maintain_Current":
            recommendations.extend([
                "Current capacity is optimal",
                "Continue monitoring for changes",
                "Maintain current configuration",
                "Regular capacity reviews"
            ])

        elif action == "Reallocate_Resources":
            recommendations.extend([
                "Reallocate resources for better efficiency",
                "Optimize resource distribution",
                "Consider workload-specific allocation",
                "Monitor reallocation impact"
            ])

        # Add context-specific recommendations
        growth_rate = features.get('traffic_growth_rate', 0)
        if growth_rate > 0.2:
            recommendations.append("High growth rate detected - consider proactive scaling")
        elif growth_rate < -0.1:
            recommendations.append("Negative growth detected - plan for downsizing")

        volatility = features.get('demand_volatility', 0)
        if volatility > 0.5:
            recommendations.append("High demand volatility - implement flexible scaling")

        return recommendations

    def _generate_demand_forecast(self, context: dict[str, Any], features: dict[str, float]) -> dict[str, Any]:
        """Generate demand forecast based on context and features."""
        current_demand = context.get("demand", {}).get("current_demand", 1000)
        growth_rate = features.get('traffic_growth_rate', 0)

        # Simple forecast based on growth rate
        forecast_days = 7
        forecast = []

        for day in range(1, forecast_days + 1):
            # Compound growth
            forecast_demand = current_demand * ((1 + growth_rate) ** (day / 30))  # Daily growth
            forecast.append({
                'day': day,
                'forecast_demand': forecast_demand,
                'confidence': max(0.3, 1.0 - (day * 0.1))
            })

        return {
            'forecast': forecast,
            'current_demand': current_demand,
            'growth_rate': growth_rate,
            'forecast_period': forecast_days
        }

    def _calculate_resource_requirements(
        self,
        action: str,
        context: dict[str, Any],
        forecast: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate resource requirements for the action."""
        current_resources = context.get("resources", {})
        current_cpu = current_resources.get("cpu", 4)
        current_memory = current_resources.get("memory", 8192)

        # Get forecasted demand
        forecast_data = forecast.get('forecast', [])
        if forecast_data:
            peak_demand = max(point['forecast_demand'] for point in forecast_data)
            current_demand = forecast.get('current_demand', 1000)
        else:
            peak_demand = current_demand

        # Calculate scaling factor
        if current_demand > 0:
            scaling_factor = peak_demand / current_demand
        else:
            scaling_factor = 1.0

        # Apply action-specific scaling
        if action.startswith("Scale_Up"):
            if "Aggressive" in action:
                scaling_factor *= 1.5
            elif "Moderate" in action:
                scaling_factor *= 1.2
            else:  # Conservative
                scaling_factor *= 1.1
        elif action.startswith("Scale_Down"):
            if "Aggressive" in action:
                scaling_factor *= 0.6
            elif "Moderate" in action:
                scaling_factor *= 0.8
            else:  # Conservative
                scaling_factor *= 0.9
        elif action == "Maintain_Current":
            scaling_factor = 1.0
        else:  # Reallocate_Resources
            scaling_factor = 1.0  # Reallocation doesn't change total resources

        # Calculate required resources
        required_cpu = max(1, int(current_cpu * scaling_factor))
        required_memory = max(1024, int(current_memory * scaling_factor))

        return {
            'required_cpu': required_cpu,
            'required_memory': required_memory,
            'current_cpu': current_cpu,
            'current_memory': current_memory,
            'scaling_factor': scaling_factor,
            'peak_demand': peak_demand
        }

    def _analyze_cost_impact(
        self,
        action: str,
        context: dict[str, Any],
        requirements: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze cost impact of capacity action."""
        current_cost = context.get("cost", {}).get("monthly_cost", 1000)

        # Cost per unit resource
        cpu_cost_per_unit = current_cost / (context.get("resources", {}).get("cpu", 4) * 0.6)
        memory_cost_per_unit = current_cost / (context.get("resources", {}).get("memory", 8192) * 0.4)

        # Calculate new cost
        new_cpu = requirements.get('required_cpu', 4)
        new_memory = requirements.get('required_memory', 8192)

        new_cpu_cost = new_cpu * cpu_cost_per_unit
        new_memory_cost = new_memory * memory_cost_per_unit
        new_total_cost = new_cpu_cost + new_memory_cost

        cost_change = new_total_cost - current_cost
        cost_change_percent = (cost_change / current_cost) * 100 if current_cost > 0 else 0

        return {
            'current_monthly_cost': current_cost,
            'projected_monthly_cost': new_total_cost,
            'cost_change': cost_change,
            'cost_change_percent': cost_change_percent,
            'cost_per_request': new_total_cost / requirements.get('peak_demand', 1000)
        }

    def _estimate_implementation_timeline(self, action: str) -> str:
        """Estimate implementation timeline for capacity action."""
        timelines = {
            "Scale_Up_Aggressive": "1-2 hours",
            "Scale_Up_Moderate": "2-4 hours",
            "Scale_Up_Conservative": "4-8 hours",
            "Maintain_Current": "No action needed",
            "Scale_Down_Conservative": "4-8 hours",
            "Scale_Down_Moderate": "2-4 hours",
            "Scale_Down_Aggressive": "1-2 hours",
            "Reallocate_Resources": "2-6 hours"
        }

        return timelines.get(action, "4-8 hours")

    def _assess_capacity_risks(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Assess risks associated with capacity action."""
        risks = {
            "performance_risk": "Low",
            "availability_risk": "Low",
            "cost_risk": "Low",
            "scalability_risk": "Low"
        }

        if action.startswith("Scale_Down"):
            risks["performance_risk"] = "Medium"
            risks["availability_risk"] = "Medium"
        elif action.startswith("Scale_Up"):
            risks["cost_risk"] = "Medium"

        # Adjust based on system criticality
        criticality = context.get("system", {}).get("criticality", "medium")
        if criticality == "high":
            for risk in risks:
                if risks[risk] == "Low":
                    risks[risk] = "Medium"
                elif risks[risk] == "Medium":
                    risks[risk] = "High"

        return risks

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        # For time series model, use feature correlation with action
        feature_names = self.feature_names or list(model_input.features.keys())

        # Simplified importance based on feature names
        importance_weights = {
            'traffic_growth_rate': 0.25,
            'current_capacity_utilization': 0.20,
            'demand_volatility': 0.15,
            'peak_demand_ratio': 0.10,
            'scaling_frequency': 0.10,
            'seasonal_pattern_strength': 0.08,
            'forecast_accuracy': 0.05,
            'resource_efficiency': 0.04,
            'cost_per_request': 0.02,
            'capacity_buffer': 0.01
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
        """Preprocess features for time series model."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for time series
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
        Train the time series model.

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

            # Convert action type string to class index
            if isinstance(label, str):
                label = self.REVERSE_CAPACITY_MAPPING.get(label, 3)  # Default to Maintain_Current
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

        # Simple weight calculation (in real implementation, use proper time series model)
        self.model_weights = np.random.rand(len(self.class_names))
        self.model_weights = self.model_weights / np.sum(self.model_weights)

        # Store feature names and training digest
        self.feature_names = feature_names
        self._training_data_digest = training_data_digest

        self.is_loaded = True
