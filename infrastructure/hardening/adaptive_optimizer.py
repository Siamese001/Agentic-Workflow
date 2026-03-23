"""Opportunity 3: Adaptive Performance Optimization Engine

Implements ML-based optimization with dynamic thresholds, cost-aware routing,
and automatic parameter tuning for the 4-layer retrieval pattern.
"""

import asyncio
import logging
import math
import random
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .implementation_plan import LayerResponse, LayerType

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategies."""

    COST_MINIMIZATION = "cost_minimization"
    LATENCY_MINIMIZATION = "latency_minimization"
    QUALITY_MAXIMIZATION = "quality_maximization"
    BALANCED = "balanced"


class ModelType(Enum):
    """ML model types."""

    THRESHOLD_OPTIMIZER = "threshold_optimizer"
    COST_PREDICTOR = "cost_predictor"
    PERFORMANCE_PREDICTOR = "performance_predictor"
    QUALITY_ESTIMATOR = "quality_estimator"


@dataclass
class PerformanceMetrics:
    """Performance metrics for optimization."""

    layer_type: LayerType
    timestamp: datetime
    latency_ms: float
    cost_estimate: float
    success_rate: float
    cache_hit_rate: float
    throughput: float
    quality_score: float
    resource_usage: dict[str, float] = field(default_factory=dict)


@dataclass
class OptimizationParameters:
    """Optimization parameters for each layer."""

    layer_type: LayerType
    similarity_threshold: float = 0.95
    top_k: int = 5
    token_budget: int = 1000
    timeout_seconds: int = 30
    cache_ttl_seconds: int = 3600
    max_retries: int = 3
    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "similarity_threshold": self.similarity_threshold,
            "top_k": self.top_k,
            "token_budget": self.token_budget,
            "timeout_seconds": self.timeout_seconds,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "max_retries": self.max_retries,
            "weight": self.weight,
        }


@dataclass
class OptimizationResult:
    """Result of optimization process."""

    layer_type: LayerType
    strategy: OptimizationStrategy
    old_parameters: OptimizationParameters
    new_parameters: OptimizationParameters
    expected_improvement: dict[str, float]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


class SimpleMLModel:
    """Simple ML model for optimization predictions."""

    def __init__(self, model_type: ModelType):
        self.model_type = model_type
        self.feature_history: list[list[float]] = []
        self.target_history: list[float] = []
        self.weights: list[float] = []
        self.bias = 0.0
        self.trained = False

    def add_training_data(self, features: list[float], target: float):
        """Add training data."""
        self.feature_history.append(features)
        self.target_history.append(target)

    def train(self) -> bool:
        """Train the model using simple linear regression."""
        if len(self.feature_history) < 10:
            return False

        try:
            # Simple linear regression using gradient descent
            num_features = len(self.feature_history[0])
            self.weights = [random.uniform(-0.1, 0.1) for _ in range(num_features)]
            self.bias = 0.0

            learning_rate = 0.01
            epochs = 100

            for epoch in range(epochs):
                total_error = 0.0

                for features, target in zip(self.feature_history, self.target_history):
                    prediction = self.predict(features)
                    error = prediction - target
                    total_error += error**2

                    # Update weights
                    for i, feature in enumerate(features):
                        self.weights[i] -= learning_rate * error * feature
                    self.bias -= learning_rate * error

                if epoch % 20 == 0:
                    avg_error = total_error / len(self.feature_history)
                    logger.debug(f"Epoch {epoch}, Error: {avg_error}")

            self.trained = True
            logger.info(f"Trained {self.model_type.value} model")
            return True

        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False

    def predict(self, features: list[float]) -> float:
        """Make prediction."""
        if not self.trained or len(features) != len(self.weights):
            return 0.5  # Default prediction

        prediction = self.bias
        for feature, w in zip(features, self.weights):
            prediction += feature * w

        return max(0.0, min(1.0, prediction))  # Clamp to [0, 1]


class ModelRegistry(dict):
    """Dictionary-like model registry with compatibility attributes."""

    ModelType = ModelType


class PerformanceAnalyzer:
    """Analyzes performance data and extracts features for ML models."""

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history: dict[LayerType, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.trends: dict[LayerType, dict[str, float]] = defaultdict(dict)

    def add_metrics(self, metrics: PerformanceMetrics):
        """Add performance metrics."""
        self.metrics_history[metrics.layer_type].append(metrics)
        self._update_trends(metrics.layer_type)

    def _update_trends(self, layer_type: LayerType):
        """Update performance trends."""
        history = list(self.metrics_history[layer_type])
        if len(history) < 10:
            return

        # Calculate trends
        recent = history[-10:]
        older = history[-20:-10] if len(history) >= 20 else history[:-10]

        if older:
            # Latency trend
            recent_latency = sum(m.latency_ms for m in recent) / len(recent)
            older_latency = sum(m.latency_ms for m in older) / len(older)
            self.trends[layer_type]["latency_trend"] = (recent_latency - older_latency) / older_latency

            # Cost trend
            recent_cost = sum(m.cost_estimate for m in recent) / len(recent)
            older_cost = sum(m.cost_estimate for m in older) / len(older)
            self.trends[layer_type]["cost_trend"] = (
                (recent_cost - older_cost) / older_cost if older_cost > 0 else 0
            )

            # Quality trend
            recent_quality = sum(m.quality_score for m in recent) / len(recent)
            older_quality = sum(m.quality_score for m in older) / len(older)
            self.trends[layer_type]["quality_trend"] = (
                (recent_quality - older_quality) / older_quality if older_quality > 0 else 0
            )

    def extract_features(self, layer_type: LayerType) -> list[float]:
        """Extract features for ML models."""
        history = list(self.metrics_history[layer_type])
        if len(history) < 5:
            return [0.5] * 10  # Default features

        recent = history[-10:]

        features = [
            # Current performance
            sum(m.latency_ms for m in recent[-5:]) / 5,  # Avg latency
            sum(m.cost_estimate for m in recent[-5:]) / 5,  # Avg cost
            sum(m.success_rate for m in recent[-5:]) / 5,  # Avg success rate
            sum(m.cache_hit_rate for m in recent[-5:]) / 5,  # Avg cache hit rate
            sum(m.quality_score for m in recent[-5:]) / 5,  # Avg quality
            # Trends
            self.trends[layer_type].get("latency_trend", 0.0),
            self.trends[layer_type].get("cost_trend", 0.0),
            self.trends[layer_type].get("quality_trend", 0.0),
            # Variability
            math.sqrt(
                sum((m.latency_ms - sum(m.latency_ms for m in recent) / len(recent)) ** 2 for m in recent)
                / len(recent)
            ),
            len(recent) / self.history_size,  # Utilization
        ]

        return features

    def get_performance_summary(self, layer_type: LayerType) -> dict[str, float]:
        """Get performance summary for layer."""
        history = list(self.metrics_history[layer_type])
        if not history:
            return {}

        return {
            "avg_latency_ms": sum(m.latency_ms for m in history) / len(history),
            "avg_cost": sum(m.cost_estimate for m in history) / len(history),
            "avg_success_rate": sum(m.success_rate for m in history) / len(history),
            "avg_cache_hit_rate": sum(m.cache_hit_rate for m in history) / len(history),
            "avg_quality_score": sum(m.quality_score for m in history) / len(history),
            "total_requests": len(history),
            "trends": self.trends[layer_type],
        }


class CostAnalyzer:
    """Analyzes costs and provides cost-aware routing recommendations."""

    def __init__(self):
        self.cost_per_operation = {
            LayerType.REDIS_EXACT_MATCH: 0.001,  # $0.001 per operation
            LayerType.SEMANTIC_CACHE: 0.01,  # $0.01 per operation
            LayerType.RAG_RETRIEVAL: 0.05,  # $0.05 per operation
            LayerType.AGENTIC_ACTION: 0.10,  # $0.10 per operation
        }
        self.cost_history: dict[LayerType, deque] = defaultdict(lambda: deque(maxlen=1000))

    def add_cost_data(self, layer_type: LayerType, cost: float):
        """Add cost data."""
        self.cost_history[layer_type].append({"cost": cost, "timestamp": datetime.now()})

    def predict_cost(self, layer_type: LayerType, parameters: OptimizationParameters) -> float:
        """Predict cost for layer with given parameters."""
        base_cost = self.cost_per_operation[layer_type]

        # Adjust cost based on parameters
        cost_multiplier = 1.0

        if layer_type == LayerType.SEMANTIC_CACHE:
            cost_multiplier *= 2.0 - parameters.similarity_threshold  # Lower threshold = higher cost
        elif layer_type == LayerType.RAG_RETRIEVAL:
            cost_multiplier *= parameters.top_k / 5.0  # More documents = higher cost
            cost_multiplier *= parameters.token_budget / 1000.0  # More tokens = higher cost
        elif layer_type == LayerType.AGENTIC_ACTION:
            cost_multiplier *= parameters.timeout_seconds / 30.0  # Longer timeout = potentially higher cost

        return base_cost * cost_multiplier

    def get_cost_optimization_suggestions(self, layer_type: LayerType) -> list[dict[str, Any]]:
        """Get cost optimization suggestions."""
        suggestions = []

        history = list(self.cost_history[layer_type])
        if len(history) < 10:
            return suggestions

        recent_costs = [h["cost"] for h in history[-10:]]
        avg_cost = sum(recent_costs) / len(recent_costs)

        # Generate suggestions based on cost patterns
        if layer_type == LayerType.SEMANTIC_CACHE and avg_cost > 0.015:
            suggestions.append(
                {
                    "type": "increase_threshold",
                    "description": "Increase similarity threshold to reduce false positives",
                    "expected_savings": "15-25%",
                }
            )

        elif layer_type == LayerType.RAG_RETRIEVAL and avg_cost > 0.07:
            suggestions.append(
                {
                    "type": "reduce_top_k",
                    "description": "Reduce Top-K to limit document retrieval",
                    "expected_savings": "10-20%",
                }
            )

        elif layer_type == LayerType.AGENTIC_ACTION and avg_cost > 0.15:
            suggestions.append(
                {
                    "type": "optimize_timeout",
                    "description": "Optimize timeout to reduce unnecessary processing",
                    "expected_savings": "5-15%",
                }
            )

        return suggestions


class AdaptiveOptimizer:
    """Main adaptive performance optimizer."""

    def __init__(self):
        self.performance_analyzer = PerformanceAnalyzer()
        self.cost_analyzer = CostAnalyzer()
        self.models: ModelRegistry = ModelRegistry()
        self.current_parameters: dict[LayerType, OptimizationParameters] = {}
        self.optimization_history: list[OptimizationResult] = []
        self.strategy = OptimizationStrategy.BALANCED

        # Initialize models
        for model_type in ModelType:
            self.models[model_type] = SimpleMLModel(model_type)

        # Initialize parameters
        for layer_type in LayerType:
            self.current_parameters[layer_type] = OptimizationParameters(layer_type=layer_type)

        self._training_task = None
        self._optimization_task = None

    async def start_optimization(self):
        """Start adaptive optimization."""
        self._training_task = asyncio.create_task(self._periodic_training())
        self._optimization_task = asyncio.create_task(self._periodic_optimization())
        logger.info("Started adaptive optimization")

    async def stop_optimization(self):
        """Stop adaptive optimization."""
        if self._training_task:
            self._training_task.cancel()
        if self._optimization_task:
            self._optimization_task.cancel()
        logger.info("Stopped adaptive optimization")

    async def _periodic_training(self):
        """Periodically train ML models."""
        while True:
            try:
                await asyncio.sleep(300)  # Train every 5 minutes
                await self._train_models()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic training: {e}")

    async def _periodic_optimization(self):
        """Periodically optimize parameters."""
        while True:
            try:
                await asyncio.sleep(600)  # Optimize every 10 minutes
                await self._optimize_all_layers()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic optimization: {e}")

    async def add_performance_data(self, layer_type: LayerType, response: LayerResponse):
        """Add performance data for optimization."""
        metrics = PerformanceMetrics(
            layer_type=layer_type,
            timestamp=datetime.now(),
            latency_ms=response.processing_time_ms,
            cost_estimate=response.cost_estimate,
            success_rate=1.0 if response.status.value == "completed" else 0.0,
            cache_hit_rate=1.0 if response.cache_hit else 0.0,
            quality_score=0.8,  # Mock quality score
            throughput=1.0,  # Mock throughput
        )

        self.performance_analyzer.add_metrics(metrics)
        self.cost_analyzer.add_cost_data(layer_type, response.cost_estimate)

    async def _train_models(self):
        """Train ML models with current data."""
        for layer_type in LayerType:
            features = self.performance_analyzer.extract_features(layer_type)

            # Train threshold optimizer
            current_params = self.current_parameters[layer_type]
            target = self._calculate_optimization_target(layer_type, current_params)

            threshold_model = self.models[ModelType.THRESHOLD_OPTIMIZER]
            threshold_model.add_training_data(features, target)

        # Train all models
        for model_type, model in self.models.items():
            if model.train():
                logger.info(f"Trained {model_type.value} model")

    def _calculate_optimization_target(self, layer_type: LayerType, params: OptimizationParameters) -> float:
        """Calculate optimization target for ML training."""
        summary = self.performance_analyzer.get_performance_summary(layer_type)

        if not summary:
            return 0.5

        if self.strategy == OptimizationStrategy.COST_MINIMIZATION:
            # Target lower cost
            return max(0.0, 1.0 - summary["avg_cost"] / 0.1)

        elif self.strategy == OptimizationStrategy.LATENCY_MINIMIZATION:
            # Target lower latency
            return max(0.0, 1.0 - summary["avg_latency_ms"] / 1000.0)

        elif self.strategy == OptimizationStrategy.QUALITY_MAXIMIZATION:
            # Target higher quality
            return summary["avg_quality_score"]

        else:  # BALANCED
            # Balanced optimization
            cost_score = max(0.0, 1.0 - summary["avg_cost"] / 0.1)
            latency_score = max(0.0, 1.0 - summary["avg_latency_ms"] / 1000.0)
            quality_score = summary["avg_quality_score"]
            return (cost_score + latency_score + quality_score) / 3.0

    async def _optimize_all_layers(self):
        """Optimize parameters for all layers."""
        for layer_type in LayerType:
            try:
                result = await self._optimize_layer(layer_type)
                if result:
                    self.optimization_history.append(result)
                    logger.info(f"Optimized {layer_type.value}: {result.expected_improvement}")
            except Exception as e:
                logger.error(f"Error optimizing {layer_type}: {e}")

    async def _optimize_layer(self, layer_type: LayerType) -> OptimizationResult | None:
        """Optimize parameters for a specific layer."""
        current_params = self.current_parameters[layer_type]
        features = self.performance_analyzer.extract_features(layer_type)

        # Get model predictions
        threshold_model = self.models[ModelType.THRESHOLD_OPTIMIZER]
        cost_model = self.models[ModelType.COST_PREDICTOR]
        performance_model = self.models[ModelType.PERFORMANCE_PREDICTOR]

        if not threshold_model.trained:
            return None

        # Generate parameter variations
        variations = self._generate_parameter_variations(current_params)

        best_params = current_params
        best_score = self._evaluate_parameters(current_params, layer_type)

        for variation in variations:
            score = self._evaluate_parameters(variation, layer_type)
            if score > best_score:
                best_score = score
                best_params = variation

        # Calculate expected improvement
        expected_improvement = self._calculate_improvement(current_params, best_params, layer_type)

        result = OptimizationResult(
            layer_type=layer_type,
            strategy=self.strategy,
            old_parameters=current_params,
            new_parameters=best_params,
            expected_improvement=expected_improvement,
            confidence=threshold_model.predict(features),
        )

        # Update current parameters
        self.current_parameters[layer_type] = best_params

        return result

    def _generate_parameter_variations(self, params: OptimizationParameters) -> list[OptimizationParameters]:
        """Generate parameter variations for optimization."""
        variations = []

        # Similarity threshold variations (for semantic cache)
        if params.layer_type == LayerType.SEMANTIC_CACHE:
            for threshold in [0.90, 0.92, 0.94, 0.96, 0.98]:
                new_params = OptimizationParameters(
                    layer_type=params.layer_type,
                    similarity_threshold=threshold,
                    top_k=params.top_k,
                    token_budget=params.token_budget,
                    timeout_seconds=params.timeout_seconds,
                    cache_ttl_seconds=params.cache_ttl_seconds,
                    max_retries=params.max_retries,
                    weight=params.weight,
                )
                variations.append(new_params)

        # Top-K variations (for RAG)
        elif params.layer_type == LayerType.RAG_RETRIEVAL:
            for top_k in [3, 5, 7, 10]:
                new_params = OptimizationParameters(
                    layer_type=params.layer_type,
                    similarity_threshold=params.similarity_threshold,
                    top_k=top_k,
                    token_budget=params.token_budget,
                    timeout_seconds=params.timeout_seconds,
                    cache_ttl_seconds=params.cache_ttl_seconds,
                    max_retries=params.max_retries,
                    weight=params.weight,
                )
                variations.append(new_params)

        # Token budget variations (for RAG and agentic)
        elif params.layer_type in [LayerType.RAG_RETRIEVAL, LayerType.AGENTIC_ACTION]:
            for budget in [500, 750, 1000, 1500, 2000]:
                new_params = OptimizationParameters(
                    layer_type=params.layer_type,
                    similarity_threshold=params.similarity_threshold,
                    top_k=params.top_k,
                    token_budget=budget,
                    timeout_seconds=params.timeout_seconds,
                    cache_ttl_seconds=params.cache_ttl_seconds,
                    max_retries=params.max_retries,
                    weight=params.weight,
                )
                variations.append(new_params)

        # Timeout variations
        for timeout in [15, 30, 45, 60]:
            new_params = OptimizationParameters(
                layer_type=params.layer_type,
                similarity_threshold=params.similarity_threshold,
                top_k=params.top_k,
                token_budget=params.token_budget,
                timeout_seconds=timeout,
                cache_ttl_seconds=params.cache_ttl_seconds,
                max_retries=params.max_retries,
                weight=params.weight,
            )
            variations.append(new_params)

        return variations

    def _evaluate_parameters(self, params: OptimizationParameters, layer_type: LayerType) -> float:
        """Evaluate parameters using ML models."""
        features = [
            params.similarity_threshold,
            params.top_k / 10.0,  # Normalize
            params.token_budget / 2000.0,  # Normalize
            params.timeout_seconds / 60.0,  # Normalize
            params.cache_ttl_seconds / 7200.0,  # Normalize
            params.max_retries / 5.0,  # Normalize
            params.weight,
        ]

        # Get predictions from models
        threshold_model = self.models[ModelType.THRESHOLD_OPTIMIZER]
        cost_model = self.models[ModelType.COST_PREDICTOR]
        performance_model = self.models[ModelType.PERFORMANCE_PREDICTOR]

        score = 0.0
        weight_sum = 0.0

        if threshold_model.trained:
            score += threshold_model.predict(features) * 0.4
            weight_sum += 0.4

        if cost_model.trained:
            cost_prediction = cost_model.predict(features)
            # For cost minimization, lower cost prediction should be better
            cost_score = 1.0 - cost_prediction
            score += cost_score * 0.3
            weight_sum += 0.3

        if performance_model.trained:
            score += performance_model.predict(features) * 0.3
            weight_sum += 0.3

        return score / weight_sum if weight_sum > 0 else 0.5

    def _calculate_improvement(
        self, old_params: OptimizationParameters, new_params: OptimizationParameters, layer_type: LayerType
    ) -> dict[str, float]:
        """Calculate expected improvement."""
        old_cost = self.cost_analyzer.predict_cost(layer_type, old_params)
        new_cost = self.cost_analyzer.predict_cost(layer_type, new_params)

        cost_improvement = (old_cost - new_cost) / old_cost if old_cost > 0 else 0.0

        # Estimate other improvements based on parameter changes
        latency_improvement = 0.0
        quality_improvement = 0.0

        if layer_type == LayerType.SEMANTIC_CACHE:
            if new_params.similarity_threshold > old_params.similarity_threshold:
                latency_improvement = 0.1  # Higher threshold = faster
                quality_improvement = -0.05  # Potentially lower quality
            else:
                latency_improvement = -0.05
                quality_improvement = 0.1

        elif layer_type == LayerType.RAG_RETRIEVAL:
            if new_params.top_k < old_params.top_k:
                latency_improvement = 0.15  # Fewer documents = faster
                cost_improvement += 0.1  # Lower cost
                quality_improvement = -0.05  # Potentially lower quality
            else:
                latency_improvement = -0.1
                quality_improvement = 0.1

        return {
            "cost_improvement": cost_improvement,
            "latency_improvement": latency_improvement,
            "quality_improvement": quality_improvement,
            "overall_improvement": (cost_improvement + latency_improvement + quality_improvement) / 3.0,
        }

    def get_optimization_status(self) -> dict[str, Any]:
        """Get optimization status."""
        return {
            "strategy": self.strategy.value,
            "current_parameters": {
                layer.value: params.to_dict() for layer, params in self.current_parameters.items()
            },
            "performance_summary": {
                layer.value: self.performance_analyzer.get_performance_summary(layer) for layer in LayerType
            },
            "optimization_history": [
                result.__dict__ for result in self.optimization_history[-20:]
            ],  # Last 20 optimizations
            "model_status": {model_type.value: model.trained for model_type, model in self.models.items()},
            "cost_suggestions": {
                layer.value: self.cost_analyzer.get_cost_optimization_suggestions(layer)
                for layer in LayerType
            },
        }

    def set_optimization_strategy(self, strategy: OptimizationStrategy):
        """Set optimization strategy."""
        self.strategy = strategy
        logger.info(f"Changed optimization strategy to {strategy.value}")

    def get_parameters(self, layer_type: LayerType) -> OptimizationParameters:
        """Get current parameters for layer."""
        return self.current_parameters[layer_type]
