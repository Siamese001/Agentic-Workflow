"""Phase B Reimplementation: Adaptive Optimization with Novel ML-Driven Controls

Precision-engineered adaptive optimization with machine learning, mathematical modeling,
and innovative performance tuning algorithms."""

import hashlib
import json
import logging
import math
import statistics
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, TypeVar

import numpy as np

logger = logging.getLogger(__name__)

T = TypeVar("T")


class OptimizationStrategy(Enum):
    """Mathematically precise optimization strategies with total ordering."""

    CONSERVATIVE = 1  # Prioritize stability and predictability
    BALANCED = 2  # Balance performance and stability
    AGGRESSIVE = 3  # Maximize performance at cost of stability
    COST_OPTIMIZED = 4  # Minimize cost
    LATENCY_OPTIMIZED = 5  # Minimize latency
    THROUGHPUT_OPTIMIZED = 6  # Maximize throughput

    def __lt__(self, other):
        if not isinstance(other, OptimizationStrategy):
            return NotImplemented
        return self.value < other.value


@dataclass(frozen=True)
class PrecisionOptimizationParameters:
    """Immutable optimization parameters with mathematical guarantees."""

    layer_type: str
    similarity_threshold: float = 0.85
    top_k: int = 10
    token_budget: int = 1000
    timeout_seconds: float = 30.0
    max_retries: int = 3
    cache_ttl_seconds: int = 3600
    cost_per_request: float = 0.001
    latency_target_ms: float = 100.0
    throughput_target_rps: float = 100.0

    def __post_init__(self):
        # Validate parameter bounds
        if not 0.0 <= self.similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be in [0.0, 1.0]")
        if self.top_k <= 0 or self.top_k > 1000:
            raise ValueError("top_k must be in [1, 1000]")
        if self.token_budget <= 0 or self.token_budget > 100000:
            raise ValueError("token_budget must be in [1, 100000]")
        if self.timeout_seconds <= 0 or self.timeout_seconds > 300:
            raise ValueError("timeout_seconds must be in [0, 300]")
        if self.max_retries < 0 or self.max_retries > 10:
            raise ValueError("max_retries must be in [0, 10]")
        if self.cache_ttl_seconds <= 0:
            raise ValueError("cache_ttl_seconds must be positive")
        if self.cost_per_request < 0:
            raise ValueError("cost_per_request must be non-negative")
        if self.latency_target_ms <= 0:
            raise ValueError("latency_target_ms must be positive")
        if self.throughput_target_rps <= 0:
            raise ValueError("throughput_target_rps must be positive")

        # Generate deterministic checksum
        content = json.dumps(
            {
                "layer_type": self.layer_type,
                "similarity_threshold": self.similarity_threshold,
                "top_k": self.top_k,
                "token_budget": self.token_budget,
                "timeout_seconds": self.timeout_seconds,
                "max_retries": self.max_retries,
                "cache_ttl_seconds": self.cache_ttl_seconds,
                "cost_per_request": self.cost_per_request,
                "latency_target_ms": self.latency_target_ms,
                "throughput_target_rps": self.throughput_target_rps,
            },
            sort_keys=True,
        )
        checksum = hashlib.sha256(content.encode()).hexdigest()[:16]
        object.__setattr__(self, "_checksum", checksum)

    @property
    def checksum(self) -> str:
        return getattr(self, "_checksum", "")

    def verify_integrity(self) -> bool:
        """Verify cryptographic integrity."""
        content = json.dumps(
            {
                "layer_type": self.layer_type,
                "similarity_threshold": self.similarity_threshold,
                "top_k": self.top_k,
                "token_budget": self.token_budget,
                "timeout_seconds": self.timeout_seconds,
                "max_retries": self.max_retries,
                "cache_ttl_seconds": self.cache_ttl_seconds,
                "cost_per_request": self.cost_per_request,
                "latency_target_ms": self.latency_target_ms,
                "throughput_target_rps": self.throughput_target_rps,
            },
            sort_keys=True,
        )
        expected = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self.checksum == expected


@dataclass
class PrecisionPerformanceMetrics:
    """Precise performance metrics with statistical properties."""

    timestamp: datetime
    layer_type: str
    response_time_ms: float
    cost_estimate: float
    cache_hit: bool
    success: bool
    error_type: str = ""
    token_usage: int = 0
    throughput_rps: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "layer_type": self.layer_type,
            "response_time_ms": self.response_time_ms,
            "cost_estimate": self.cost_estimate,
            "cache_hit": self.cache_hit,
            "success": self.success,
            "error_type": self.error_type,
            "token_usage": self.token_usage,
            "throughput_rps": self.throughput_rps,
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_percent": self.memory_usage_percent,
        }


class PrecisionMLModel(ABC):
    """Abstract base class for precision ML models."""

    @abstractmethod
    def train(self, features: list[list[float]], targets: list[float]) -> bool:
        """Train the model with feature-target pairs."""
        pass

    @abstractmethod
    def predict(self, features: list[float]) -> float:
        """Make prediction for given features."""
        pass

    @abstractmethod
    def is_trained(self) -> bool:
        """Check if model is trained."""
        pass

    @abstractmethod
    def get_feature_importance(self) -> dict[str, float]:
        """Get feature importance scores."""
        pass


class PrecisionLinearRegression(PrecisionMLModel):
    """Precision linear regression with mathematical guarantees."""

    def __init__(self, feature_names: list[str], regularization: float = 0.01):
        self.feature_names = feature_names
        self.feature_count = len(feature_names)
        self.regularization = regularization
        self.weights: np.ndarray | None = None
        self.bias: float = 0.0
        self.trained = False
        self.training_samples = 0
        self.feature_importance: dict[str, float] = {}

    def train(self, features: list[list[float]], targets: list[float]) -> bool:
        """Train linear regression with ridge regularization."""
        if len(features) != len(targets):
            raise ValueError("Features and targets must have same length")

        if len(features) < self.feature_count + 1:
            logger.warning("Insufficient training data for reliable training")
            return False

        try:
            # Convert to numpy arrays
            X = np.array(features)
            y = np.array(targets)

            # Add bias term
            X_with_bias = np.column_stack([X, np.ones(X.shape[0])])

            # Ridge regression: (X^T X + λI)^-1 X^T y
            XtX = X_with_bias.T @ X_with_bias
            # Add regularization to all coefficients except bias
            reg_matrix = np.eye(XtX.shape[0])
            reg_matrix[:-1, -1] = 0  # Don't regularize bias
            reg_matrix[-1, :-1] = 0
            reg_matrix *= self.regularization

            # Solve for weights
            try:
                weights_with_bias = np.linalg.solve(XtX + reg_matrix, X_with_bias.T @ y)
            except np.linalg.LinAlgError:
                # Fallback to pseudo-inverse
                weights_with_bias = np.linalg.pinv(XtX + reg_matrix) @ X_with_bias.T @ y

            # Separate weights and bias
            self.weights = weights_with_bias[:-1]
            self.bias = weights_with_bias[-1]

            # Calculate feature importance (absolute weights normalized)
            abs_weights = np.abs(self.weights)
            if np.sum(abs_weights) > 0:
                normalized_weights = abs_weights / np.sum(abs_weights)
                self.feature_importance = dict(zip(self.feature_names, normalized_weights))
            else:
                self.feature_importance = dict(zip(self.feature_names, np.zeros(self.feature_count)))

            self.trained = True
            self.training_samples = len(features)

            # Calculate training metrics
            predictions = self.predict_batch(features)
            mse = np.mean((predictions - y) ** 2)
            r2 = 1 - np.sum((y - predictions) ** 2) / np.sum((y - np.mean(y)) ** 2) if np.var(y) > 0 else 0

            logger.info(f"Linear regression trained: MSE={mse:.4f}, R²={r2:.4f}, samples={len(features)}")
            return True

        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False

    def predict(self, features: list[float]) -> float:
        """Make prediction for single feature vector."""
        if not self.trained or self.weights is None:
            return 0.5  # Default prediction

        if len(features) != self.feature_count:
            raise ValueError(f"Expected {self.feature_count} features, got {len(features)}")

        # Linear combination: w·x + b
        prediction = float(np.dot(self.weights, features) + self.bias)

        # Clamp to reasonable range
        return max(0.0, min(1.0, prediction))

    def predict_batch(self, features: list[list[float]]) -> np.ndarray:
        """Make predictions for batch of feature vectors."""
        if not self.trained or self.weights is None:
            return np.full(len(features), 0.5)

        X = np.array(features)
        predictions = X @ self.weights + self.bias
        return np.clip(predictions, 0.0, 1.0)

    def is_trained(self) -> bool:
        return self.trained

    def get_feature_importance(self) -> dict[str, float]:
        return dict(self.feature_importance)


class PrecisionNeuralNetwork(PrecisionMLModel):
    """Precision neural network with controlled architecture."""

    def __init__(self, feature_names: list[str], hidden_size: int = 16, learning_rate: float = 0.01):
        self.feature_names = feature_names
        self.feature_count = len(feature_names)
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate

        # Initialize weights with Xavier initialization
        self.W1 = np.random.randn(self.feature_count, hidden_size) * np.sqrt(2.0 / self.feature_count)
        self.b1 = np.zeros(hidden_size)
        self.W2 = np.random.randn(hidden_size, 1) * np.sqrt(2.0 / hidden_size)
        self.b2 = np.zeros(1)

        self.trained = False
        self.training_samples = 0
        self.feature_importance: dict[str, float] = {}

    def _relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation function."""
        return np.maximum(0, x)

    def _relu_derivative(self, x: np.ndarray) -> np.ndarray:
        """ReLU derivative."""
        return (x > 0).astype(float)

    def train(self, features: list[list[float]], targets: list[float], epochs: int = 100) -> bool:
        """Train neural network with gradient descent."""
        if len(features) != len(targets):
            raise ValueError("Features and targets must have same length")

        if len(features) < 10:
            logger.warning("Insufficient training data for neural network")
            return False

        try:
            X = np.array(features)
            y = np.array(targets).reshape(-1, 1)

            for epoch in range(epochs):
                # Forward pass
                z1 = X @ self.W1 + self.b1
                a1 = self._relu(z1)
                z2 = a1 @ self.W2 + self.b2
                predictions = 1 / (1 + np.exp(-z2))  # Sigmoid

                # Backward pass
                m = X.shape[0]
                dz2 = predictions - y
                dW2 = (a1.T @ dz2) / m
                db2 = np.mean(dz2, axis=0)

                da1 = dz2 @ self.W2.T
                dz1 = da1 * self._relu_derivative(z1)
                dW1 = (X.T @ dz1) / m
                db1 = np.mean(dz1, axis=0)

                # Update weights
                self.W2 -= self.learning_rate * dW2
                self.b2 -= self.learning_rate * db2
                self.W1 -= self.learning_rate * dW1
                self.b1 -= self.learning_rate * db1

                # Calculate loss every 10 epochs
                if epoch % 10 == 0:
                    loss = -np.mean(y * np.log(predictions + 1e-8) + (1 - y) * np.log(1 - predictions + 1e-8))
                    logger.debug(f"Epoch {epoch}, Loss: {loss:.4f}")

            # Calculate feature importance using weight magnitudes
            feature_weights = np.abs(self.W1).mean(axis=1)
            if np.sum(feature_weights) > 0:
                normalized_weights = feature_weights / np.sum(feature_weights)
                self.feature_importance = dict(zip(self.feature_names, normalized_weights))
            else:
                self.feature_importance = dict(zip(self.feature_names, np.zeros(self.feature_count)))

            self.trained = True
            self.training_samples = len(features)

            logger.info(f"Neural network trained: samples={len(features)}, epochs={epochs}")
            return True

        except Exception as e:
            logger.error(f"Neural network training failed: {e}")
            return False

    def predict(self, features: list[float]) -> float:
        """Make prediction for single feature vector."""
        if not self.trained:
            return 0.5

        if len(features) != self.feature_count:
            raise ValueError(f"Expected {self.feature_count} features, got {len(features)}")

        X = np.array(features).reshape(1, -1)

        # Forward pass
        z1 = X @ self.W1 + self.b1
        a1 = self._relu(z1)
        z2 = a1 @ self.W2 + self.b2
        prediction = 1 / (1 + np.exp(-z2[0, 0]))  # Sigmoid

        return float(prediction)

    def is_trained(self) -> bool:
        return self.trained

    def get_feature_importance(self) -> dict[str, float]:
        return dict(self.feature_importance)


class PrecisionFeatureExtractor:
    """Precision feature extraction with mathematical transformations."""

    def __init__(self):
        self.feature_names = [
            "hour_of_day",
            "day_of_week",
            "recent_avg_latency",
            "recent_error_rate",
            "recent_cache_hit_rate",
            "recent_throughput",
            "load_factor",
            "cost_trend",
            "latency_trend",
            "success_trend",
        ]

    def extract_features(
        self,
        metrics_history: list[PrecisionPerformanceMetrics],
        current_params: PrecisionOptimizationParameters,
    ) -> list[float]:
        """Extract features from metrics history and current parameters."""
        if not metrics_history:
            return [0.0] * len(self.feature_names)

        now = datetime.now()
        recent_metrics = metrics_history[-10:]  # Last 10 metrics

        # Time-based features
        hour_of_day = now.hour / 24.0
        day_of_week = now.weekday() / 7.0

        # Recent performance features
        recent_latencies = [m.response_time_ms for m in recent_metrics]
        recent_errors = [0.0 if m.success else 1.0 for m in recent_metrics]
        recent_cache_hits = [1.0 if m.cache_hit else 0.0 for m in recent_metrics]
        recent_throughputs = [m.throughput_rps for m in recent_metrics]

        avg_latency = statistics.mean(recent_latencies) / 1000.0  # Convert to seconds
        error_rate = statistics.mean(recent_errors)
        cache_hit_rate = statistics.mean(recent_cache_hits)
        avg_throughput = statistics.mean(recent_throughputs)

        # Load factor (current vs target)
        load_factor = min(1.0, avg_throughput / max(0.1, current_params.throughput_target_rps))

        # Trend features (linear regression slope)
        def calculate_trend(values: list[float]) -> float:
            if len(values) < 2:
                return 0.0

            x = list(range(len(values)))
            n = len(values)

            # Calculate slope using least squares
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(xi * yi for xi, yi in zip(x, values))
            sum_x2 = sum(xi * xi for xi in x)

            if n * sum_x2 - sum_x * sum_x == 0:
                return 0.0

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            return slope

        # Normalize trends
        cost_trend = calculate_trend([m.cost_estimate for m in recent_metrics]) * 100
        latency_trend = calculate_trend([m.response_time_ms for m in recent_metrics]) / 1000.0
        success_trend = calculate_trend([1.0 if m.success else 0.0 for m in recent_metrics])

        features = [
            hour_of_day,
            day_of_week,
            avg_latency,
            error_rate,
            cache_hit_rate,
            avg_throughput,
            load_factor,
            cost_trend,
            latency_trend,
            success_trend,
        ]

        # Ensure all features are finite
        features = [0.0 if not math.isfinite(f) else f for f in features]

        return features


class PrecisionAdaptiveOptimizer:
    """Precision adaptive optimizer with ML-driven controls."""

    def __init__(self):
        self.feature_extractor = PrecisionFeatureExtractor()
        self.models: dict[str, PrecisionMLModel] = {}
        self.current_parameters: dict[str, PrecisionOptimizationParameters] = {}
        self.metrics_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.optimization_history: list[dict[str, Any]] = []
        self.strategy = OptimizationStrategy.BALANCED

        # Initialize models for each optimization target
        self._initialize_models()

        # Initialize parameters for each layer type
        self._initialize_parameters()

    def _initialize_models(self) -> None:
        """Initialize ML models for different optimization targets."""
        feature_names = self.feature_extractor.feature_names

        # Latency optimization model
        self.models["latency"] = PrecisionLinearRegression(feature_names, regularization=0.01)

        # Cost optimization model
        self.models["cost"] = PrecisionLinearRegression(feature_names, regularization=0.01)

        # Throughput optimization model
        self.models["throughput"] = PrecisionNeuralNetwork(feature_names, hidden_size=8, learning_rate=0.01)

        # Success rate optimization model
        self.models["success"] = PrecisionLinearRegression(feature_names, regularization=0.01)

    def _initialize_parameters(self) -> None:
        """Initialize default parameters for each layer type."""
        layer_types = ["redis_exact_match", "semantic_cache", "rag_retrieval", "agentic_action"]

        for layer_type in layer_types:
            self.current_parameters[layer_type] = PrecisionOptimizationParameters(
                layer_type=layer_type,
                similarity_threshold=0.85 if layer_type == "semantic_cache" else 0.0,
                top_k=min(50, 10 + layer_types.index(layer_type) * 10),
                token_budget=1000 * (layer_types.index(layer_type) + 1),
                timeout_seconds=30.0 * (layer_types.index(layer_type) + 1),
                cost_per_request=0.001 * (layer_types.index(layer_type) + 1),
                latency_target_ms=50.0 * (layer_types.index(layer_type) + 1),
                throughput_target_rps=1000.0 / (layer_types.index(layer_type) + 1),
            )

    async def add_performance_metrics(self, layer_type: str, metrics: PrecisionPerformanceMetrics) -> None:
        """Add performance metrics for optimization."""
        self.metrics_history[layer_type].append(metrics)

        # Trigger optimization if we have enough data
        if len(self.metrics_history[layer_type]) >= 50:
            await self._optimize_parameters(layer_type)

    async def _optimize_parameters(self, layer_type: str) -> None:
        """Optimize parameters using ML models."""
        if layer_type not in self.current_parameters:
            return

        metrics_list = list(self.metrics_history[layer_type])
        current_params = self.current_parameters[layer_type]

        # Extract features
        features = self.feature_extractor.extract_features(metrics_list, current_params)

        # Get optimization suggestions from models
        suggestions = {}

        for target_name, model in self.models.items():
            if model.is_trained():
                prediction = model.predict(features)
                suggestions[target_name] = prediction

        # Apply optimization based on strategy
        new_params = await self._apply_optimization_strategy(layer_type, suggestions, current_params)

        # Record optimization
        optimization_record = {
            "timestamp": datetime.now().isoformat(),
            "layer_type": layer_type,
            "strategy": self.strategy.name,
            "old_params": current_params.to_dict(),
            "new_params": new_params.to_dict(),
            "suggestions": suggestions,
            "metrics_count": len(metrics_list),
        }

        self.optimization_history.append(optimization_record)
        self.current_parameters[layer_type] = new_params

        logger.info(f"Optimized parameters for {layer_type}: {len(suggestions)} suggestions applied")

    async def _apply_optimization_strategy(
        self, layer_type: str, suggestions: dict[str, float], current_params: PrecisionOptimizationParameters
    ) -> PrecisionOptimizationParameters:
        """Apply optimization based on current strategy."""
        # Create new parameters based on strategy
        if self.strategy == OptimizationStrategy.CONSERVATIVE:
            return self._apply_conservative_strategy(layer_type, suggestions, current_params)
        elif self.strategy == OptimizationStrategy.BALANCED:
            return self._apply_balanced_strategy(layer_type, suggestions, current_params)
        elif self.strategy == OptimizationStrategy.AGGRESSIVE:
            return self._apply_aggressive_strategy(layer_type, suggestions, current_params)
        elif self.strategy == OptimizationStrategy.COST_OPTIMIZED:
            return self._apply_cost_optimized_strategy(layer_type, suggestions, current_params)
        elif self.strategy == OptimizationStrategy.LATENCY_OPTIMIZED:
            return self._apply_latency_optimized_strategy(layer_type, suggestions, current_params)
        elif self.strategy == OptimizationStrategy.THROUGHPUT_OPTIMIZED:
            return self._apply_throughput_optimized_strategy(layer_type, suggestions, current_params)
        else:
            return current_params

    def _apply_conservative_strategy(
        self, layer_type: str, suggestions: dict[str, float], current_params: PrecisionOptimizationParameters
    ) -> PrecisionOptimizationParameters:
        """Apply conservative optimization strategy (minimal changes)."""
        # Conservative strategy: make small adjustments based on strongest signal
        max_suggestion = max(suggestions.values(), default=0.5)

        if max_suggestion > 0.7:  # Strong signal
            # Make small adjustments
            adjustments = {
                "similarity_threshold": 0.01,
                "top_k": 1,
                "token_budget": 50,
                "timeout_seconds": 1.0,
            }
        else:
            adjustments = dict.fromkeys(
                ["similarity_threshold", "top_k", "token_budget", "timeout_seconds"], 0
            )

        return self._apply_adjustments(current_params, adjustments, factor=0.1)

    def _apply_balanced_strategy(
        self, layer_type: str, suggestions: dict[str, float], current_params: PrecisionOptimizationParameters
    ) -> PrecisionOptimizationParameters:
        """Apply balanced optimization strategy."""
        # Balanced strategy: moderate adjustments based on multiple signals
        avg_suggestion = statistics.mean(suggestions.values()) if suggestions else 0.5

        if avg_suggestion > 0.6:
            adjustments = {
                "similarity_threshold": 0.02,
                "top_k": 2,
                "token_budget": 100,
                "timeout_seconds": 2.0,
            }
        elif avg_suggestion < 0.4:
            adjustments = {
                "similarity_threshold": -0.02,
                "top_k": -2,
                "token_budget": -100,
                "timeout_seconds": -2.0,
            }
        else:
            adjustments = dict.fromkeys(
                ["similarity_threshold", "top_k", "token_budget", "timeout_seconds"], 0
            )

        return self._apply_adjustments(current_params, adjustments, factor=0.3)

    def _apply_aggressive_strategy(
        self, layer_type: str, suggestions: dict[str, float], current_params: PrecisionOptimizationParameters
    ) -> PrecisionOptimizationParameters:
        """Apply aggressive optimization strategy."""
        # Aggressive strategy: large adjustments for maximum performance
        max_suggestion = max(suggestions.values(), default=0.5)

        if max_suggestion > 0.5:
            adjustments = {
                "similarity_threshold": 0.05,
                "top_k": 5,
                "token_budget": 500,
                "timeout_seconds": 5.0,
            }
        else:
            adjustments = {
                "similarity_threshold": -0.05,
                "top_k": -5,
                "token_budget": -500,
                "timeout_seconds": -5.0,
            }

        return self._apply_adjustments(current_params, adjustments, factor=0.7)

    def _apply_cost_optimized_strategy(
        self, layer_type: str, suggestions: dict[str, float], current_params: PrecisionOptimizationParameters
    ) -> PrecisionOptimizationParameters:
        """Apply cost optimization strategy."""
        # Cost optimization: reduce parameters to minimize cost
        cost_suggestion = suggestions.get("cost", 0.5)

        if cost_suggestion > 0.6:  # Need to reduce cost
            adjustments = {
                "similarity_threshold": 0.03,  # Higher threshold = less processing
                "top_k": -3,  # Fewer results
                "token_budget": -200,  # Less tokens
                "timeout_seconds": -1.0,  # Shorter timeout
            }
        else:
            adjustments = dict.fromkeys(
                ["similarity_threshold", "top_k", "token_budget", "timeout_seconds"], 0
            )

        return self._apply_adjustments(current_params, adjustments, factor=0.5)

    def _apply_latency_optimized_strategy(
        self, layer_type: str, suggestions: dict[str, float], current_params: PrecisionOptimizationParameters
    ) -> PrecisionOptimizationParameters:
        """Apply latency optimization strategy."""
        # Latency optimization: reduce timeout and increase efficiency
        latency_suggestion = suggestions.get("latency", 0.5)

        if latency_suggestion > 0.6:  # Need to reduce latency
            adjustments = {
                "similarity_threshold": 0.04,  # Higher threshold = faster
                "top_k": -2,  # Fewer results = faster
                "token_budget": -100,  # Less processing
                "timeout_seconds": -3.0,  # Much shorter timeout
            }
        else:
            adjustments = dict.fromkeys(
                ["similarity_threshold", "top_k", "token_budget", "timeout_seconds"], 0
            )

        return self._apply_adjustments(current_params, adjustments, factor=0.6)

    def _apply_throughput_optimized_strategy(
        self, layer_type: str, suggestions: dict[str, float], current_params: PrecisionOptimizationParameters
    ) -> PrecisionOptimizationParameters:
        """Apply throughput optimization strategy."""
        # Throughput optimization: increase capacity and parallelism
        throughput_suggestion = suggestions.get("throughput", 0.5)

        if throughput_suggestion > 0.6:  # Need to increase throughput
            adjustments = {
                "similarity_threshold": -0.02,  # Lower threshold = more hits
                "top_k": 3,  # More results
                "token_budget": 300,  # More capacity
                "timeout_seconds": 2.0,  # Longer timeout for more processing
            }
        else:
            adjustments = dict.fromkeys(
                ["similarity_threshold", "top_k", "token_budget", "timeout_seconds"], 0
            )

        return self._apply_adjustments(current_params, adjustments, factor=0.4)

    def _apply_adjustments(
        self, current_params: PrecisionOptimizationParameters, adjustments: dict[str, float], factor: float
    ) -> PrecisionOptimizationParameters:
        """Apply adjustments to parameters with bounds checking."""
        # Apply adjustments with factor
        new_similarity = current_params.similarity_threshold + adjustments["similarity_threshold"] * factor
        new_top_k = current_params.top_k + int(adjustments["top_k"] * factor)
        new_token_budget = current_params.token_budget + int(adjustments["token_budget"] * factor)
        new_timeout = current_params.timeout_seconds + adjustments["timeout_seconds"] * factor

        # Clamp to valid ranges
        new_similarity = max(0.0, min(1.0, new_similarity))
        new_top_k = max(1, min(1000, new_top_k))
        new_token_budget = max(1, min(100000, new_token_budget))
        new_timeout = max(0.1, min(300.0, new_timeout))

        return PrecisionOptimizationParameters(
            layer_type=current_params.layer_type,
            similarity_threshold=new_similarity,
            top_k=new_top_k,
            token_budget=new_token_budget,
            timeout_seconds=new_timeout,
            max_retries=current_params.max_retries,
            cache_ttl_seconds=current_params.cache_ttl_seconds,
            cost_per_request=current_params.cost_per_request,
            latency_target_ms=current_params.latency_target_ms,
            throughput_target_rps=current_params.throughput_target_rps,
        )

    async def train_models(self, layer_type: str) -> dict[str, bool]:
        """Train ML models with available data."""
        if layer_type not in self.metrics_history:
            return dict.fromkeys(self.models.keys(), False)

        metrics_list = list(self.metrics_history[layer_type])
        current_params = self.current_parameters.get(layer_type)

        if not current_params or len(metrics_list) < 20:
            return dict.fromkeys(self.models.keys(), False)

        # Extract features and targets
        features = []
        latency_targets = []
        cost_targets = []
        throughput_targets = []
        success_targets = []

        for i in range(10, len(metrics_list)):  # Use sliding window
            window_metrics = metrics_list[:i]
            current_features = self.feature_extractor.extract_features(window_metrics, current_params)
            current_metric = metrics_list[i]

            features.append(current_features)

            # Create targets (normalized to [0, 1])
            latency_targets.append(min(1.0, current_metric.response_time_ms / 1000.0))  # 1s = 1.0
            cost_targets.append(min(1.0, current_metric.cost_estimate * 100))  # 0.01 = 1.0
            throughput_targets.append(min(1.0, current_metric.throughput_rps / 1000.0))  # 1000 rps = 1.0
            success_targets.append(1.0 if current_metric.success else 0.0)

        # Train models
        results = {}

        # Train linear regression models
        for model_name, targets in [
            ("latency", latency_targets),
            ("cost", cost_targets),
            ("success", success_targets),
        ]:
            if model_name in self.models:
                model = self.models[model_name]
                success = model.train(features, targets)
                results[model_name] = success

        # Train neural network (throughput)
        if "throughput" in self.models:
            model = self.models["throughput"]
            success = model.train(features, throughput_targets, epochs=50)
            results["throughput"] = success

        logger.info(f"Model training completed for {layer_type}: {results}")
        return results

    def get_optimization_status(self) -> dict[str, Any]:
        """Get comprehensive optimization status."""
        total_optimizations = len(self.optimization_history)
        recent_optimizations = [
            o
            for o in self.optimization_history
            if datetime.fromisoformat(o["timestamp"]) > datetime.now() - timedelta(hours=1)
        ]

        model_status = {}
        for name, model in self.models.items():
            model_status[name] = {
                "trained": model.is_trained(),
                "samples": getattr(model, "training_samples", 0),
                "feature_importance": model.get_feature_importance() if model.is_trained() else {},
            }

        return {
            "strategy": self.strategy.name,
            "total_optimizations": total_optimizations,
            "recent_optimizations": len(recent_optimizations),
            "model_status": model_status,
            "layer_parameters": {
                layer_type: params.to_dict() for layer_type, params in self.current_parameters.items()
            },
            "metrics_count": {
                layer_type: len(history) for layer_type, history in self.metrics_history.items()
            },
        }

    def set_optimization_strategy(self, strategy: OptimizationStrategy) -> None:
        """Set optimization strategy."""
        self.strategy = strategy
        logger.info(f"Optimization strategy changed to: {strategy.name}")

    def get_parameters(self, layer_type: str) -> PrecisionOptimizationParameters | None:
        """Get current parameters for layer type."""
        return self.current_parameters.get(layer_type)


# Export precision optimization components
__all__ = [
    "OptimizationStrategy",
    "PrecisionOptimizationParameters",
    "PrecisionPerformanceMetrics",
    "PrecisionMLModel",
    "PrecisionLinearRegression",
    "PrecisionNeuralNetwork",
    "PrecisionFeatureExtractor",
    "PrecisionAdaptiveOptimizer",
]
