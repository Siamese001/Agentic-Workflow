"""
Ensemble Router Implementation for L0 Routing - Wave 2.2

Implements ensemble of routing models with meta-learner for improved
accuracy and confidence estimation through model combination.
"""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import numpy as np

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_dispatches_agent,
    _emit_feeds_meta_learning,
    _emit_records_execution_trace,
    _emit_records_learning_event,
    _emit_stores_learning_state,
)

logger = logging.getLogger(__name__)

@dataclass
class RoutingPrediction:
    """Prediction from a single routing model"""

    agent_name: str
    confidence: float
    uncertainty: float
    reasoning: str | None = None
    features_used: dict[str, float] | None = None
    model_metadata: dict[str, Any] | None = None

@dataclass
class EnsembleFeatures:
    """Features extracted from base model predictions for meta-learner"""

    # Confidence features
    mean_confidence: float
    std_confidence: float
    max_confidence: float
    min_confidence: float

    # Agent agreement features
    agent_agreement_score: float
    top_agent_consensus: float
    agent_diversity: float

    # Uncertainty features
    mean_uncertainty: float
    std_uncertainty: float
    uncertainty_correlation: float

    # Model-specific features
    model_weights: dict[str, float]
    model_reliability: dict[str, float]

    def to_vector(self) -> np.ndarray:
        """Convert features to vector for meta-learner"""
        return np.array([
            self.mean_confidence,
            self.std_confidence,
            self.max_confidence,
            self.min_confidence,
            self.agent_agreement_score,
            self.top_agent_consensus,
            self.agent_diversity,
            self.mean_uncertainty,
            self.std_uncertainty,
            self.uncertainty_correlation
        ])

@dataclass
class EnsembleDecision:
    """Final routing decision from ensemble"""

    selected_agent: str
    confidence: float
    uncertainty: float
    ensemble_features: EnsembleFeatures
    base_predictions: list[RoutingPrediction]
    meta_confidence: float
    reasoning: str
    decision_time: float

class BaseRoutingModel(ABC):
    """Abstract base class for routing models"""

    def __init__(self, model_name: str, weight: float = 1.0):
        self.model_name = model_name
        self.weight = weight
        self.reliability_score = 1.0
        self.prediction_count = 0
        self.success_count = 0

    @abstractmethod
    def predict(self, query: str, context: dict[str, Any]) -> RoutingPrediction:
        """Make routing prediction"""
        pass

    @abstractmethod
    def update_reliability(self, prediction: RoutingPrediction, success: bool):
        """Update model reliability based on outcome"""
        pass

    def get_reliability(self) -> float:
        """Get current reliability score"""
        if self.prediction_count == 0:
            return 1.0
        return self.success_count / self.prediction_count

class IntentEmbeddingModel(BaseRoutingModel):
    """Wrapper for existing IntentEmbeddingClassifier"""

    def __init__(self, classifier, weight: float = 1.0):
        super().__init__("intent_embedding", weight)
        self.classifier = classifier

    def predict(self, query: str, context: dict[str, Any]) -> RoutingPrediction:
        """Predict using embedding classifier"""
        try:
            result = self.classifier.classify(query)
            if result:
                agent_name, confidence = result
                uncertainty = 1.0 - confidence
                return RoutingPrediction(
                    agent_name=agent_name,
                    confidence=confidence,
                    uncertainty=uncertainty,
                    reasoning=f"Embedding similarity: {confidence:.3f}",
                    features_used={"embedding_confidence": confidence},
                    model_metadata={"model_type": "embedding"}
                )
            else:
                # Fallback prediction
                return RoutingPrediction(
                    agent_name="default_agent",
                    confidence=0.3,
                    uncertainty=0.7,
                    reasoning="No embedding match found",
                    features_used={"fallback": True},
                    model_metadata={"model_type": "embedding_fallback"}
                )
        except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallow -- embedding prediction error returns fallback
            logger.error(f"IntentEmbeddingModel prediction error: {e}")
            return RoutingPrediction(
                agent_name="error_fallback",
                confidence=0.1,
                uncertainty=0.9,
                reasoning=f"Prediction error: {str(e)}",
                features_used={"error": True},
                model_metadata={"model_type": "embedding_error"}
            )

    def update_reliability(self, prediction: RoutingPrediction, success: bool):
        """Update reliability based on prediction outcome"""
        self.prediction_count += 1
        if success:
            self.success_count += 1
            self.reliability_score = self.get_reliability()

class RuleBasedModel(BaseRoutingModel):
    """Rule-based routing model"""

    def __init__(self, rules: dict[str, Any], weight: float = 0.8):
        super().__init__("rule_based", weight)
        self.rules = rules

    def predict(self, query: str, context: dict[str, Any]) -> RoutingPrediction:
        """Predict using rule-based logic"""
        query_lower = query.lower()

        # Simple keyword-based rules
        agent_scores = defaultdict(float)

        for agent, keywords in self.rules.get("agent_keywords", {}).items():
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    agent_scores[agent] += 1.0

        if agent_scores:
            # Normalize scores
            total_score = sum(agent_scores.values())
            for agent in agent_scores:
                agent_scores[agent] /= total_score

            # Select top agent
            top_agent = max(agent_scores.keys(), key=lambda k: agent_scores[k])
            confidence = agent_scores[top_agent]
            uncertainty = 1.0 - confidence

            return RoutingPrediction(
                agent_name=top_agent,
                confidence=confidence * 0.8,  # Slightly lower confidence for rules
                uncertainty=uncertainty,
                reasoning=f"Rule-based match: {list(agent_scores.keys())}",
                features_used=dict(agent_scores),
                model_metadata={"model_type": "rule_based"}
            )
        else:
            return RoutingPrediction(
                agent_name="default_agent",
                confidence=0.4,
                uncertainty=0.6,
                reasoning="No rule match found",
                features_used={"fallback": True},
                model_metadata={"model_type": "rule_fallback"}
            )

    def update_reliability(self, prediction: RoutingPrediction, success: bool):
        """Update reliability based on prediction outcome"""
        self.prediction_count += 1
        if success:
            self.success_count += 1
            self.reliability_score = self.get_reliability()

class MetaLearner:
    """Meta-learner for combining base model predictions"""

    def __init__(self, input_dim: int = 10, hidden_dim: int = 20):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim

        # Simple neural network weights (would use proper ML library in production)
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.1
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, 1) * 0.1
        self.b2 = np.zeros(1)

        self.learning_rate = 0.01
        self.training_count = 0

        _emit_stores_learning_state("meta_learner", "initialization", {
            "input_dim": input_dim,
            "hidden_dim": hidden_dim
        })

    def forward(self, features: EnsembleFeatures) -> float:
        """Forward pass through meta-learner"""
        x = features.to_vector()

        # Hidden layer
        z1 = x @ self.W1 + self.b1
        a1 = np.tanh(z1)

        # Output layer
        z2 = a1 @ self.W2 + self.b2
        output = 1.0 / (1.0 + np.exp(-z2[0]))  # Sigmoid

        return output

    def update(self, features: EnsembleFeatures, target: float):
        """Update meta-learner with new training example"""
        # Simple gradient descent (would use proper optimizer in production)
        x = features.to_vector()

        # Forward pass
        z1 = x @ self.W1 + self.b1
        a1 = np.tanh(z1)
        z2 = a1 @ self.W2 + self.b2
        output = 1.0 / (1.0 + np.exp(-z2[0]))

        # Backward pass (simplified)
        error = output - target

        # Update output layer
        dW2 = error * a1.reshape(-1, 1)
        self.W2 -= self.learning_rate * dW2
        self.b2 -= self.learning_rate * error

        # Update hidden layer
        dW1 = error * self.W2.flatten() * (1 - a1**2) * x.reshape(-1, 1)
        self.W1 -= self.learning_rate * dW1
        self.b1 -= self.learning_rate * error * self.W2.flatten() * (1 - a1**2)

        self.training_count += 1

        _emit_records_learning_event("meta_learner", "weight_update", {
            "training_count": self.training_count,
            "error": float(error),
            "output": float(output),
            "target": target
        })

class EnsembleRouter:
    """
    Ensemble router that combines multiple base models with meta-learner.

    Uses weighted voting and meta-learning to improve routing accuracy
    and provide reliable confidence estimates.
    """

    def __init__(
        self,
        base_models: list[BaseRoutingModel] | None = None,
        meta_learner: MetaLearner | None = None,
        ensemble_strategy: str = "weighted_voting"
    ):
        """
        Initialize ensemble router.

        Args:
            base_models: List of base routing models
            meta_learner: Meta-learner for combining predictions
            ensemble_strategy: Strategy for combining predictions
        """
        self.base_models = base_models or []
        self.meta_learner = meta_learner or MetaLearner()
        self.ensemble_strategy = ensemble_strategy

        # Performance tracking
        self.prediction_count = 0
        self.success_count = 0
        self.decision_history: list[EnsembleDecision] = []

        # Model weights (dynamic)
        self.model_weights: dict[str, float] = {}
        self._update_model_weights()

        _emit_stores_learning_state("ensemble_router", "initialization", {
            "base_models": len(self.base_models),
            "ensemble_strategy": ensemble_strategy
        })

    def add_model(self, model: BaseRoutingModel):
        """Add a base model to the ensemble"""
        self.base_models.append(model)
        self._update_model_weights()

        _emit_records_learning_event("ensemble_router", "model_added", {
            "model_name": model.model_name,
            "weight": model.weight,
            "total_models": len(self.base_models)
        })

    def _update_model_weights(self):
        """Update model weights based on reliability"""
        total_weight = sum(model.weight for model in self.base_models)

        for model in self.base_models:
            reliability = model.get_reliability()
            self.model_weights[model.model_name] = (model.weight * reliability) / total_weight

    def _extract_ensemble_features(self, predictions: list[RoutingPrediction]) -> EnsembleFeatures:
        """Extract features from base model predictions"""

        if not predictions:
            raise ValueError("No predictions to extract features from")

        # Confidence features
        confidences = [p.confidence for p in predictions]
        mean_confidence = np.mean(confidences)

        # Safe standard deviation calculation
        if len(confidences) > 1:
            std_confidence = np.std(confidences)
        else:
            std_confidence = 0.0

        max_confidence = np.max(confidences)
        min_confidence = np.min(confidences)

        # Agent agreement features
        agent_counts = defaultdict(int)
        for pred in predictions:
            agent_counts[pred.agent_name] += 1

        total_predictions = len(predictions)
        agent_agreement_score = max(agent_counts.values()) / total_predictions

        top_agent = max(agent_counts.keys(), key=lambda k: agent_counts[k])
        top_agent_consensus = agent_counts[top_agent] / total_predictions

        agent_diversity = len(agent_counts) / total_predictions

        # Uncertainty features
        uncertainties = [p.uncertainty for p in predictions]
        mean_uncertainty = np.mean(uncertainties)

        # Safe standard deviation calculation
        if len(uncertainties) > 1:
            std_uncertainty = np.std(uncertainties)
        else:
            std_uncertainty = 0.0

        # Calculate uncertainty correlation (simplified)
        if len(confidences) > 1 and len(uncertainties) > 1:
            try:
                correlation_matrix = np.corrcoef(confidences, uncertainties)
                if not np.isnan(correlation_matrix[0, 1]):
                    uncertainty_correlation = correlation_matrix[0, 1]
                else:
                    uncertainty_correlation = 0.0
            except (ValueError, TypeError):  # correlation calculation failure
                uncertainty_correlation = 0.0
        else:
            uncertainty_correlation = 0.0

        return EnsembleFeatures(
            mean_confidence=mean_confidence,
            std_confidence=std_confidence,
            max_confidence=max_confidence,
            min_confidence=min_confidence,
            agent_agreement_score=agent_agreement_score,
            top_agent_consensus=top_agent_consensus,
            agent_diversity=agent_diversity,
            mean_uncertainty=mean_uncertainty,
            std_uncertainty=std_uncertainty,
            uncertainty_correlation=uncertainty_correlation,
            model_weights=self.model_weights.copy(),
            model_reliability={m.model_name: m.get_reliability() for m in self.base_models}
        )

    def route(self, query: str, context: dict[str, Any]) -> EnsembleDecision:
        """
        Make routing decision using ensemble.

        Args:
            query: User query or task description
            context: Additional context for routing

        Returns:
            EnsembleDecision with final routing choice
        """
        start_time = time.time()

        # Get predictions from all base models
        base_predictions = []
        for model in self.base_models:
            try:
                prediction = model.predict(query, context)
                base_predictions.append(prediction)
            except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallow -- model prediction failure adds fallback
                logger.error(f"Model {model.model_name} prediction failed: {e}")
                # Add fallback prediction
                base_predictions.append(RoutingPrediction(
                    agent_name="error_fallback",
                    confidence=0.1,
                    uncertainty=0.9,
                    reasoning=f"Model error: {str(e)}",
                    model_metadata={"model_type": "error"}
                ))

        # Extract ensemble features
        ensemble_features = self._extract_ensemble_features(base_predictions)

        # Make ensemble decision based on strategy
        if self.ensemble_strategy == "weighted_voting":
            selected_agent, confidence = self._weighted_voting(base_predictions)
        elif self.ensemble_strategy == "meta_learning":
            selected_agent, confidence = self._meta_learning_decision(base_predictions, ensemble_features)
        else:
            selected_agent, confidence = self._simple_voting(base_predictions)

        # Calculate ensemble uncertainty
        uncertainties = [p.uncertainty for p in base_predictions]
        ensemble_uncertainty = np.mean(uncertainties)

        # Get meta-learner confidence
        meta_confidence = self.meta_learner.forward(ensemble_features)

        # Create reasoning string
        reasoning_parts = [
            f"Strategy: {self.ensemble_strategy}",
            f"Models used: {len(base_predictions)}",
            f"Agent agreement: {ensemble_features.agent_agreement_score:.2f}",
            f"Mean confidence: {ensemble_features.mean_confidence:.2f}"
        ]
        reasoning = "; ".join(reasoning_parts)

        decision = EnsembleDecision(
            selected_agent=selected_agent,
            confidence=confidence,
            uncertainty=ensemble_uncertainty,
            ensemble_features=ensemble_features,
            base_predictions=base_predictions,
            meta_confidence=meta_confidence,
            reasoning=reasoning,
            decision_time=time.time() - start_time
        )

        # Record decision
        self.decision_history.append(decision)
        self.prediction_count += 1

        # Emit trace events
        _emit_records_execution_trace("ensemble_router", "routing_decision", {
            "selected_agent": selected_agent,
            "confidence": confidence,
            "strategy": self.ensemble_strategy,
            "models_used": len(base_predictions)
        })

        _emit_dispatches_agent("ensemble_router", selected_agent, {
            "confidence": confidence,
            "uncertainty": ensemble_uncertainty,
            "decision_time": decision.decision_time
        })

        return decision

    def _weighted_voting(self, predictions: list[RoutingPrediction]) -> tuple[str, float]:
        """Weighted voting based on model reliability"""
        agent_scores = defaultdict(float)

        for pred in predictions:
            model_weight = self.model_weights.get(
                pred.model_metadata.get("model_type", "unknown"),
                1.0
            )
            agent_scores[pred.agent_name] += pred.confidence * model_weight

        # Select top agent
        top_agent = max(agent_scores.keys(), key=lambda k: agent_scores[k])
        confidence = agent_scores[top_agent] / sum(agent_scores.values())

        return top_agent, confidence

    def _meta_learning_decision(self, predictions: list[RoutingPrediction], features: EnsembleFeatures) -> tuple[str, float]:
        """Use meta-learner for final decision"""
        # Get meta-learner confidence
        meta_confidence = self.meta_learner.forward(features)

        # Combine with weighted voting
        agent_scores = defaultdict(float)
        for pred in predictions:
            model_weight = self.model_weights.get(
                pred.model_metadata.get("model_type", "unknown"),
                1.0
            )
            agent_scores[pred.agent_name] += pred.confidence * model_weight

        # Apply meta-learner weighting
        for agent in agent_scores:
            agent_scores[agent] *= meta_confidence

        # Select top agent
        top_agent = max(agent_scores.keys(), key=lambda k: agent_scores[k])
        confidence = agent_scores[top_agent] / sum(agent_scores.values())

        return top_agent, confidence

    def _simple_voting(self, predictions: list[RoutingPrediction]) -> tuple[str, float]:
        """Simple majority voting"""
        agent_counts = defaultdict(int)
        for pred in predictions:
            agent_counts[pred.agent_name] += 1

        top_agent = max(agent_counts.keys(), key=lambda k: agent_counts[k])
        confidence = agent_counts[top_agent] / len(predictions)

        return top_agent, confidence

    def update_outcome(self, decision: EnsembleDecision, success: bool):
        """Update ensemble based on routing outcome"""
        self.prediction_count += 1
        if success:
            self.success_count += 1

        # Update base model reliabilities
        for pred in decision.base_predictions:
            for model in self.base_models:
                if model.model_name == pred.model_metadata.get("model_type"):
                    model.update_reliability(pred, success)

        # Update meta-learner
        target = 1.0 if success else 0.0
        self.meta_learner.update(decision.ensemble_features, target)

        # Update model weights
        self._update_model_weights()

        # Emit learning events
        _emit_records_learning_event("ensemble_router", "outcome_update", {
            "success": success,
            "selected_agent": decision.selected_agent,
            "confidence": decision.confidence,
            "success_rate": self.get_success_rate()
        })

        _emit_feeds_meta_learning("ensemble_router", "feedback", {
            "decision_features": decision.ensemble_features.to_vector().tolist()[:5],
            "success": success,
            "target": target
        })

    def get_success_rate(self) -> float:
        """Get current success rate"""
        if self.prediction_count == 0:
            return 0.0
        return self.success_count / self.prediction_count

    def get_model_performance(self) -> dict[str, dict[str, float]]:
        """Get performance metrics for all models"""
        performance = {}
        for model in self.base_models:
            performance[model.model_name] = {
                "reliability": model.get_reliability(),
                "predictions": model.prediction_count,
                "successes": model.success_count,
                "weight": model.weight
            }
        return performance

    def save_state(self, filepath: str):
        """Save ensemble state to file"""
        state = {
            "ensemble_strategy": self.ensemble_strategy,
            "prediction_count": self.prediction_count,
            "success_count": self.success_count,
            "model_weights": self.model_weights,
            "base_models": [
                {
                    "name": model.model_name,
                    "weight": model.weight,
                    "reliability": model.get_reliability(),
                    "predictions": model.prediction_count,
                    "successes": model.success_count
                }
                for model in self.base_models
            ],
            "meta_learner": {
                "training_count": self.meta_learner.training_count,
                "learning_rate": self.meta_learner.learning_rate
            }
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        _emit_stores_learning_state("ensemble_router", "state_saved", {
            "filepath": filepath,
            "success_rate": self.get_success_rate()
        })

# Utility functions
def create_default_ensemble(embedding_classifier) -> EnsembleRouter:
    """Create a default ensemble with common models"""

    # Create base models
    embedding_model = IntentEmbeddingModel(embedding_classifier, weight=1.0)

    # Simple rule-based model
    rules = {
        "agent_keywords": {
            "code_reviewer": ["code", "review", "python", "javascript"],
            "resume_writer": ["resume", "cv", "career", "job"],
            "data_analyst": ["data", "analysis", "chart", "graph"],
            "writer": ["write", "article", "blog", "content"]
        }
    }
    rule_model = RuleBasedModel(rules, weight=0.8)

    # Create ensemble
    ensemble = EnsembleRouter(
        base_models=[embedding_model, rule_model],
        ensemble_strategy="weighted_voting"
    )

    return ensemble

__all__ = [
    "EnsembleRouter",
    "BaseRoutingModel",
    "IntentEmbeddingModel",
    "RuleBasedModel",
    "MetaLearner",
    "RoutingPrediction",
    "EnsembleFeatures",
    "EnsembleDecision",
    "create_default_ensemble"
]
