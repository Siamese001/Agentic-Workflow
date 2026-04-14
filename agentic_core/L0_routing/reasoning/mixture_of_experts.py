"""
Mixture of Experts Implementation for L0 Routing - Wave 3.1

Implements Mixture of Experts (MoE) architecture with specialized experts
for different routing domains, intelligent gating network, and load balancing.
"""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_feeds_meta_learning,
    _emit_records_execution_trace,
    _emit_records_learning_event,
    _emit_stores_learning_state,
)
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class ExpertSpecialization:
    """Defines the specialization domain of an expert"""

    domain_name: str
    keywords: list[str]
    capability_score: float
    confidence_threshold: float
    load_factor: float = 1.0
    last_used: float = field(default_factory=time.time)

    def matches_query(self, query: str) -> float:
        """Calculate how well this expert matches the query"""
        query_lower = query.lower()
        keyword_matches = sum(1 for kw in self.keywords if kw.lower() in query_lower)
        match_ratio = keyword_matches / len(self.keywords) if self.keywords else 0.0
        return match_ratio * self.capability_score


@dataclass
class ExpertPrediction:
    """Prediction from a single expert"""

    expert_id: str
    agent_name: str
    confidence: float
    uncertainty: float
    specialization_match: float
    processing_time: float
    reasoning: str | None = None
    features_used: dict[str, float] | None = None


@dataclass
class MoEDecision:
    """Final routing decision from Mixture of Experts"""

    selected_expert: str
    selected_agent: str
    confidence: float
    uncertainty: float
    gating_scores: dict[str, float]
    expert_predictions: dict[str, ExpertPrediction]
    load_balancing_applied: bool
    reasoning: str
    decision_time: float


class BaseExpert(ABC):
    """Abstract base class for routing experts"""

    def __init__(self, expert_id: str, specialization: ExpertSpecialization):
        self.expert_id = expert_id
        self.specialization = specialization
        self.prediction_count = 0
        self.success_count = 0
        self.total_processing_time = 0.0
        self.last_update = time.time()

    @abstractmethod
    def predict(self, query: str, context: dict[str, Any]) -> ExpertPrediction:
        """Make routing prediction"""
        pass

    @abstractmethod
    def update_performance(self, prediction: ExpertPrediction, success: bool):
        """Update expert performance based on outcome"""
        pass

    def get_reliability(self) -> float:
        """Get current reliability score"""
        if self.prediction_count == 0:
            return 0.5
        return self.success_count / self.prediction_count

    def get_average_processing_time(self) -> float:
        """Get average processing time"""
        if self.prediction_count == 0:
            return 0.0
        return self.total_processing_time / self.prediction_count

    def update_load_factor(self, new_factor: float):
        """Update load factor for load balancing"""
        self.specialization.load_factor = new_factor
        self.specialization.last_used = time.time()


class CodeReviewExpert(BaseExpert):
    """Specialized expert for code review tasks"""

    def __init__(self, expert_id: str):
        specialization = ExpertSpecialization(
            domain_name="code_review",
            keywords=["code", "review", "python", "javascript", "bug", "fix", "refactor"],
            capability_score=0.9,
            confidence_threshold=0.7,
        )
        super().__init__(expert_id, specialization)

    def predict(self, query: str, context: dict[str, Any]) -> ExpertPrediction:
        """Predict for code review tasks"""
        start_time = time.time()

        # Calculate specialization match
        match_score = self.specialization.matches_query(query)

        # Simple confidence calculation based on keyword matching
        confidence = min(0.95, match_score * 1.2)
        uncertainty = 1.0 - confidence

        # Agent selection based on code type
        agent_name = "code_reviewer"
        if "python" in query.lower():
            agent_name = "python_reviewer"
        elif "javascript" in query.lower():
            agent_name = "js_reviewer"

        processing_time = time.time() - start_time

        return ExpertPrediction(
            expert_id=self.expert_id,
            agent_name=agent_name,
            confidence=confidence,
            uncertainty=uncertainty,
            specialization_match=match_score,
            processing_time=processing_time,
            reasoning=f"Code review expert: {match_score:.2f} match",
            features_used={"keyword_match": match_score, "confidence": confidence},
        )

    def update_performance(self, prediction: ExpertPrediction, success: bool):
        """Update performance metrics"""
        self.prediction_count += 1
        self.total_processing_time += prediction.processing_time
        if success:
            self.success_count += 1
        self.last_update = time.time()


class ResumeExpert(BaseExpert):
    """Specialized expert for resume and career tasks"""

    def __init__(self, expert_id: str):
        specialization = ExpertSpecialization(
            domain_name="resume_career",
            keywords=["resume", "cv", "career", "job", "interview", "hiring"],
            capability_score=0.85,
            confidence_threshold=0.6,
        )
        super().__init__(expert_id, specialization)

    def predict(self, query: str, context: dict[str, Any]) -> ExpertPrediction:
        """Predict for resume/career tasks"""
        start_time = time.time()

        match_score = self.specialization.matches_query(query)
        confidence = min(0.9, match_score * 1.3)
        uncertainty = 1.0 - confidence

        # Agent selection based on task type
        agent_name = "resume_writer"
        if "interview" in query.lower():
            agent_name = "interview_coach"
        elif "career" in query.lower():
            agent_name = "career_advisor"

        processing_time = time.time() - start_time

        return ExpertPrediction(
            expert_id=self.expert_id,
            agent_name=agent_name,
            confidence=confidence,
            uncertainty=uncertainty,
            specialization_match=match_score,
            processing_time=processing_time,
            reasoning=f"Resume expert: {match_score:.2f} match",
            features_used={"keyword_match": match_score, "confidence": confidence},
        )

    def update_performance(self, prediction: ExpertPrediction, success: bool):
        """Update performance metrics"""
        self.prediction_count += 1
        self.total_processing_time += prediction.processing_time
        if success:
            self.success_count += 1
        self.last_update = time.time()


class DataAnalysisExpert(BaseExpert):
    """Specialized expert for data analysis tasks"""

    def __init__(self, expert_id: str):
        specialization = ExpertSpecialization(
            domain_name="data_analysis",
            keywords=["data", "analysis", "chart", "graph", "statistics", "visualization"],
            capability_score=0.8,
            confidence_threshold=0.65,
        )
        super().__init__(expert_id, specialization)

    def predict(self, query: str, context: dict[str, Any]) -> ExpertPrediction:
        """Predict for data analysis tasks"""
        start_time = time.time()

        match_score = self.specialization.matches_query(query)
        confidence = min(0.85, match_score * 1.25)
        uncertainty = 1.0 - confidence

        # Agent selection based on analysis type
        agent_name = "data_analyst"
        if "chart" in query.lower() or "graph" in query.lower():
            agent_name = "visualization_expert"
        elif "statistics" in query.lower():
            agent_name = "statistician"

        processing_time = time.time() - start_time

        return ExpertPrediction(
            expert_id=self.expert_id,
            agent_name=agent_name,
            confidence=confidence,
            uncertainty=uncertainty,
            specialization_match=match_score,
            processing_time=processing_time,
            reasoning=f"Data analysis expert: {match_score:.2f} match",
            features_used={"keyword_match": match_score, "confidence": confidence},
        )

    def update_performance(self, prediction: ExpertPrediction, success: bool):
        """Update performance metrics"""
        self.prediction_count += 1
        self.total_processing_time += prediction.processing_time
        if success:
            self.success_count += 1
        self.last_update = time.time()


class GatingNetwork:
    """Neural gating network for expert selection"""

    def __init__(self, input_dim: int = 100, hidden_dim: int = 50, num_experts: int = 3):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_experts = num_experts

        # Initialize weights (simplified neural network)
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.1
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, num_experts) * 0.1
        self.b2 = np.zeros(num_experts)

        self.learning_rate = 0.01
        self.training_count = 0

        _emit_stores_learning_state(
            "gating_network",
            "initialization",
            {
                "input_dim": input_dim,
                "hidden_dim": hidden_dim,
                "num_experts": num_experts,
            },
        )

    def forward(self, query_embedding: np.ndarray, expert_features: list[dict[str, float]]) -> np.ndarray:
        """Forward pass through gating network"""
        # Combine query embedding with expert features
        expert_feature_vector = np.array(
            [list(features.values())[: self.input_dim - len(query_embedding)] for features in expert_features]
        ).flatten()

        # Pad or truncate to match input dimension
        combined_input = np.concatenate([query_embedding, expert_feature_vector])
        if len(combined_input) > self.input_dim:
            combined_input = combined_input[: self.input_dim]
        elif len(combined_input) < self.input_dim:
            combined_input = np.pad(combined_input, (0, self.input_dim - len(combined_input)))

        # Neural network forward pass
        z1 = combined_input @ self.W1 + self.b1
        a1 = np.tanh(z1)
        z2 = a1 @ self.W2 + self.b2

        # Softmax for expert selection probabilities
        exp_scores = np.exp(z2 - np.max(z2))
        probabilities = exp_scores / np.sum(exp_scores)

        return probabilities

    def update(
        self,
        query_embedding: np.ndarray,
        expert_features: list[dict[str, float]],
        selected_expert_idx: int,
        reward: float,
    ):
        """Update gating network with reinforcement learning"""
        # Get current probabilities
        current_probs = self.forward(query_embedding, expert_features)

        # Calculate loss (simplified REINFORCE loss)
        loss = -np.log(current_probs[selected_expert_idx] + 1e-8) * reward

        # Backward pass (simplified gradient computation)
        grad = current_probs.copy()
        grad[selected_expert_idx] -= 1.0
        grad *= reward

        # Update weights (simplified)
        combined_input = np.concatenate(
            [
                query_embedding,
                np.array([list(f.values()) for f in expert_features]).flatten()[
                    : self.input_dim - len(query_embedding)
                ],
            ]
        )

        if len(combined_input) > self.input_dim:
            combined_input = combined_input[: self.input_dim]
        elif len(combined_input) < self.input_dim:
            combined_input = np.pad(combined_input, (0, self.input_dim - len(combined_input)))

        # Gradient updates (simplified)
        self.W2 -= self.learning_rate * np.outer(np.tanh(combined_input @ self.W1 + self.b1), grad)
        self.b2 -= self.learning_rate * grad

        self.training_count += 1

        _emit_records_learning_event(
            "gating_network",
            "weight_update",
            {
                "training_count": self.training_count,
                "loss": float(loss),
                "selected_expert": selected_expert_idx,
                "reward": reward,
            },
        )


class LoadBalancer:
    """Load balancer for expert selection"""

    def __init__(self, load_balance_strategy: str = "least_loaded"):
        self.load_balance_strategy = load_balance_strategy
        self.expert_loads: dict[str, float] = {}
        self.expert_capacities: dict[str, float] = {}

    def register_expert(self, expert_id: str, capacity: float = 1.0):
        """Register an expert with capacity"""
        self.expert_loads[expert_id] = 0.0
        self.expert_capacities[expert_id] = capacity

    def update_load(self, expert_id: str, load_delta: float):
        """Update expert load"""
        if expert_id in self.expert_loads:
            self.expert_loads[expert_id] += load_delta
            self.expert_loads[expert_id] = max(0.0, self.expert_loads[expert_id])

    def get_load_balance_weights(self, expert_ids: list[str]) -> dict[str, float]:
        """Get load balancing weights for experts"""
        weights = {}

        for expert_id in tqdm(expert_ids, desc="Processing", unit="item"):
            if expert_id not in self.expert_loads:
                weights[expert_id] = 1.0
                continue

            current_load = self.expert_loads[expert_id]
            capacity = self.expert_capacities.get(expert_id, 1.0)

            if self.load_balance_strategy == "least_loaded":
                # Inverse load weighting
                load_ratio = current_load / capacity if capacity > 0 else 1.0
                weights[expert_id] = 1.0 / (1.0 + load_ratio)
            elif self.load_balance_strategy == "capacity_based":
                # Capacity-based weighting
                weights[expert_id] = capacity
            else:
                weights[expert_id] = 1.0

        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}

        return weights


class MixtureOfExperts:
    """
    Mixture of Experts (MoE) routing system with specialized experts,
    intelligent gating network, and load balancing.
    """

    def __init__(
        self,
        experts: list[BaseExpert] | None = None,
        gating_network: GatingNetwork | None = None,
        load_balancer: LoadBalancer | None = None,
        max_concurrent_experts: int = 3,
    ):
        """
        Initialize Mixture of Experts.

        Args:
            experts: List of specialized experts
            gating_network: Neural gating network for expert selection
            load_balancer: Load balancer for expert selection
            max_concurrent_experts: Maximum experts to evaluate concurrently
        """
        self.experts = {expert.expert_id: expert for expert in (experts or [])}
        self.gating_network = gating_network or GatingNetwork(num_experts=len(self.experts))
        self.load_balancer = load_balancer or LoadBalancer()
        self.max_concurrent_experts = max_concurrent_experts

        # Performance tracking
        self.prediction_count = 0
        self.success_count = 0
        self.decision_history: list[MoEDecision] = []

        # Initialize load balancer with experts
        for expert_id in self.experts:
            self.load_balancer.register_expert(expert_id, capacity=1.0)

        # Thread pool for concurrent expert evaluation
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_experts)

        _emit_stores_learning_state(
            "mixture_of_experts",
            "initialization",
            {
                "experts_count": len(self.experts),
                "max_concurrent": max_concurrent_experts,
                "load_balance_strategy": self.load_balancer.load_balance_strategy,
            },
        )

    def add_expert(self, expert: BaseExpert):
        """Add a new expert to the mixture"""
        self.experts[expert.expert_id] = expert
        self.load_balancer.register_expert(expert.expert_id, capacity=1.0)

        # Reinitialize gating network if needed
        if len(self.experts) != self.gating_network.num_experts:
            self.gating_network = GatingNetwork(num_experts=len(self.experts))

        _emit_records_learning_event(
            "mixture_of_experts",
            "expert_added",
            {
                "expert_id": expert.expert_id,
                "domain": expert.specialization.domain_name,
                "total_experts": len(self.experts),
            },
        )

    def route(self, query: str, context: dict[str, Any]) -> MoEDecision:
        """
        Make routing decision using Mixture of Experts.

        Args:
            query: User query or task description
            context: Additional context for routing

        Returns:
            MoEDecision with final routing choice
        """
        start_time = time.time()

        # Create mock query embedding (in production, use actual embedding)
        query_embedding = np.random.randn(50)

        # Get expert predictions concurrently
        expert_predictions = self._get_expert_predictions(query, context)

        # Prepare expert features for gating network
        expert_features = []
        for expert_id, prediction in expert_predictions.items():
            expert = self.experts[expert_id]
            features = {
                "specialization_match": prediction.specialization_match,
                "reliability": expert.get_reliability(),
                "avg_processing_time": expert.get_average_processing_time(),
                "load_factor": expert.specialization.load_factor,
                "confidence": prediction.confidence,
            }
            expert_features.append(features)

        # Get gating network scores
        gating_scores = self.gating_network.forward(query_embedding, expert_features)

        # Apply load balancing
        load_balance_weights = self.load_balancer.get_load_balance_weights(list(self.experts.keys()))

        # Combine gating scores with load balancing
        final_scores = {}
        expert_ids = list(self.experts.keys())
        for i, expert_id in enumerate(expert_ids):
            if i < len(gating_scores):
                gating_score = gating_scores[i]
                load_weight = load_balance_weights.get(expert_id, 1.0)
                final_scores[expert_id] = gating_score * load_weight

        # Select best expert
        selected_expert_id = max(final_scores.keys(), key=lambda k: final_scores[k])
        selected_expert = self.experts[selected_expert_id]
        selected_prediction = expert_predictions[selected_expert_id]

        # Update load balancer
        self.load_balancer.update_load(selected_expert_id, 0.1)

        # Calculate final confidence with minimum threshold
        base_confidence = selected_prediction.confidence * final_scores[selected_expert_id]
        confidence = max(0.1, base_confidence)  # Minimum confidence threshold
        uncertainty = max(0.0, 1.0 - confidence)

        # Create reasoning
        reasoning_parts = [
            f"Selected expert: {selected_expert.specialization.domain_name}",
            f"Specialization match: {selected_prediction.specialization_match:.2f}",
            f"Gating score: {final_scores[selected_expert_id]:.3f}",
            f"Load balanced: {True}",
        ]
        reasoning = "; ".join(reasoning_parts)

        decision = MoEDecision(
            selected_expert=selected_expert_id,
            selected_agent=selected_prediction.agent_name,
            confidence=confidence,
            uncertainty=uncertainty,
            gating_scores=final_scores,
            expert_predictions=expert_predictions,
            load_balancing_applied=True,
            reasoning=reasoning,
            decision_time=time.time() - start_time,
        )

        # Record decision
        self.decision_history.append(decision)
        self.prediction_count += 1

        # Emit trace events
        _emit_records_execution_trace(
            "mixture_of_experts",
            "routing_decision",
            {
                "selected_expert": selected_expert_id,
                "selected_agent": selected_prediction.agent_name,
                "confidence": confidence,
                "domain": selected_expert.specialization.domain_name,
            },
        )

        _emit_dispatches_agent(
            "mixture_of_experts",
            selected_prediction.agent_name,
            {
                "expert_id": selected_expert_id,
                "confidence": confidence,
                "specialization": selected_expert.specialization.domain_name,
            },
        )

        _emit_coordinates_agents(
            "mixture_of_experts",
            "expert_coordination",
            {
                "selected_expert": selected_expert_id,
                "all_experts": list(self.experts.keys()),
                "load_balanced": True,
            },
        )

        return decision

    def _get_expert_predictions(self, query: str, context: dict[str, Any]) -> dict[str, ExpertPrediction]:
        """Get predictions from all experts concurrently"""
        expert_predictions = {}

        # Submit prediction tasks to thread pool
        future_to_expert = {
            self.executor.submit(expert.predict, query, context): expert_id
            for expert_id, expert in self.experts.items()
        }

        # Collect results
        for future in tqdm(as_completed(future_to_expert), desc="Processing", unit="item"):
            expert_id = future_to_expert[future]
            try:
                prediction = future.result(timeout=5.0)  # 5 second timeout
                expert_predictions[expert_id] = prediction
            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Expert {expert_id} prediction failed: {e}")
                # Create fallback prediction
                expert = self.experts[expert_id]
                expert_predictions[expert_id] = ExpertPrediction(
                    expert_id=expert_id,
                    agent_name="fallback_agent",
                    confidence=0.1,
                    uncertainty=0.9,
                    specialization_match=0.0,
                    processing_time=5.0,
                    reasoning=f"Expert error: {str(e)}",
                )

        return expert_predictions

    def update_outcome(self, decision: MoEDecision, success: bool):
        """Update MoE based on routing outcome"""
        self.prediction_count += 1
        if success:
            self.success_count += 1

        # Update selected expert
        selected_expert = self.experts[decision.selected_expert]
        selected_prediction = decision.expert_predictions[decision.selected_expert]
        selected_expert.update_performance(selected_prediction, success)

        # Update gating network
        query_embedding = np.random.randn(50)  # Mock embedding
        expert_features = []
        expert_ids = list(self.experts.keys())

        for expert_id, prediction in decision.expert_predictions.items():
            expert = self.experts[expert_id]
            features = {
                "specialization_match": prediction.specialization_match,
                "reliability": expert.get_reliability(),
                "avg_processing_time": expert.get_average_processing_time(),
                "load_factor": expert.specialization.load_factor,
                "confidence": prediction.confidence,
            }
            expert_features.append(features)

        selected_expert_idx = expert_ids.index(decision.selected_expert)
        reward = 1.0 if success else -0.5
        self.gating_network.update(query_embedding, expert_features, selected_expert_idx, reward)

        # Update load balancer (decrease load for successful routing)
        self.load_balancer.update_load(decision.selected_expert, -0.05)

        # Emit learning events
        _emit_records_learning_event(
            "mixture_of_experts",
            "outcome_update",
            {
                "success": success,
                "selected_expert": decision.selected_expert,
                "confidence": decision.confidence,
                "success_rate": self.get_success_rate(),
            },
        )

        _emit_feeds_meta_learning(
            "mixture_of_experts",
            "feedback",
            {
                "expert_id": decision.selected_expert,
                "success": success,
                "reward": reward,
                "specialization": selected_expert.specialization.domain_name,
            },
        )

    def get_success_rate(self) -> float:
        """Get current success rate"""
        if self.prediction_count == 0:
            return 0.0
        return self.success_count / self.prediction_count

    def get_expert_performance(self) -> dict[str, dict[str, float]]:
        """Get performance metrics for all experts"""
        performance = {}
        for expert_id, expert in self.experts.items():
            performance[expert_id] = {
                "domain": expert.specialization.domain_name,
                "reliability": expert.get_reliability(),
                "predictions": expert.prediction_count,
                "successes": expert.success_count,
                "avg_processing_time": expert.get_average_processing_time(),
                "load_factor": expert.specialization.load_factor,
                "capability_score": expert.specialization.capability_score,
            }
        return performance

    def save_state(self, filepath: str):
        """Save MoE state to file"""
        state = {
            "prediction_count": self.prediction_count,
            "success_count": self.success_count,
            "experts": {
                expert_id: {
                    "domain": expert.specialization.domain_name,
                    "predictions": expert.prediction_count,
                    "successes": expert.success_count,
                    "avg_processing_time": expert.get_average_processing_time(),
                    "load_factor": expert.specialization.load_factor,
                }
                for expert_id, expert in self.experts.items()
            },
            "gating_network": {
                "training_count": self.gating_network.training_count,
                "learning_rate": self.gating_network.learning_rate,
            },
            "load_balancer": {
                "strategy": self.load_balancer.load_balance_strategy,
                "expert_loads": self.load_balancer.expert_loads,
                "expert_capacities": self.load_balancer.expert_capacities,
            },
        }

        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

        _emit_stores_learning_state(
            "mixture_of_experts",
            "state_saved",
            {
                "filepath": filepath,
                "success_rate": self.get_success_rate(),
            },
        )

    def shutdown(self):
        """Shutdown thread pool and cleanup"""
        self.executor.shutdown(wait=True)


# Utility functions
def create_default_moe() -> MixtureOfExperts:
    """Create a default Mixture of Experts with common specialists"""

    # Create specialized experts
    experts = [
        CodeReviewExpert("code_review_expert"),
        ResumeExpert("resume_expert"),
        DataAnalysisExpert("data_analysis_expert"),
    ]

    # Create MoE system
    moe = MixtureOfExperts(
        experts=experts,
        max_concurrent_experts=3,
    )

    return moe


__all__ = [
    "MixtureOfExperts",
    "BaseExpert",
    "CodeReviewExpert",
    "ResumeExpert",
    "DataAnalysisExpert",
    "GatingNetwork",
    "LoadBalancer",
    "ExpertSpecialization",
    "ExpertPrediction",
    "MoEDecision",
    "create_default_moe",
]
