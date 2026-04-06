"""
Contextual Bandit Implementation for L0 Routing - Wave 2.1

Implements LinUCB algorithm for online learning in routing decisions.
Balances exploration vs exploitation while maintaining confidence estimates.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_records_execution_trace,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_updates_routing_strategy,
)

logger = logging.getLogger(__name__)

@dataclass
class BanditContext:
    """Context features for bandit decision making"""

    # Intent features
    intent_embedding: np.ndarray
    intent_length: int
    intent_complexity: float

    # User features
    user_history_score: float
    user_success_rate: float

    # System features
    current_load: float
    time_of_day: int
    day_of_week: int

    # ADG features
    adg_territory_score: float
    confidence_tiers: dict[str, int]

    def to_vector(self) -> np.ndarray:
        """Convert context to feature vector"""
        return np.concatenate([
            self.intent_embedding,
            [self.intent_length, self.intent_complexity],
            [self.user_history_score, self.user_success_rate],
            [self.current_load, self.time_of_day, self.day_of_week],
            [self.adg_territory_score],
            list(self.confidence_tiers.values())
        ])

@dataclass
class BanditArm:
    """Represents a routing option (agent) as a bandit arm"""

    arm_id: str
    agent_name: str
    capability_match: float
    current_load: float
    success_rate: float

    # Bandit parameters (will be initialized in add_arm)
    A: np.ndarray = field(default=None)
    b: np.ndarray = field(default=None)
    theta: np.ndarray = field(default=None)

    def update_parameters(self, context: np.ndarray, reward: float):
        """Update bandit parameters with observed reward"""
        self.A += np.outer(context, context)
        self.b += reward * context
        self.theta = np.linalg.inv(self.A) @ self.b

@dataclass
class BanditDecision:
    """Result of bandit decision making"""

    selected_arm: str
    agent_name: str
    confidence: float
    uncertainty: float
    expected_reward: float
    context_used: BanditContext
    all_arm_scores: dict[str, float]

class LinUCBBandit:
    """
    LinUCB (Linear Upper Confidence Bound) contextual bandit implementation.

    Uses linear models to estimate expected rewards and upper confidence bounds
    for balanced exploration and exploitation in routing decisions.
    """

    def __init__(
        self,
        context_dim: int = 50,
        alpha: float = 1.0,
        arms: list[str] | None = None,
        decay_factor: float = 0.99
    ):
        """
        Initialize LinUCB bandit.

        Args:
            context_dim: Dimension of context feature vector
            alpha: Exploration parameter (higher = more exploration)
            arms: List of available routing arms (agents)
            decay_factor: Decay factor for historical data
        """
        self.context_dim = context_dim
        self.alpha = alpha
        self.decay_factor = decay_factor

        # Initialize arms
        self.arms: dict[str, BanditArm] = {}
        if arms:
            for arm_id in arms:
                self.arms[arm_id] = BanditArm(
                    arm_id=arm_id,
                    agent_name=arm_id,
                    capability_match=1.0,
                    current_load=0.0,
                    success_rate=0.5
                )

        # Learning state
        self.round_count = 0
        self.total_reward = 0.0
        self.reward_history: list[float] = []
        self.decision_history: list[BanditDecision] = []

        # Metrics
        self.regret_history: list[float] = []
        self.exploration_rate = 0.1

        _emit_stores_learning_state("linucb_bandit", "initialization", {
            "context_dim": context_dim,
            "alpha": alpha,
            "arms_count": len(self.arms)
        })

    def add_arm(self, arm_id: str, agent_name: str, capability_match: float = 1.0):
        """Add a new routing arm"""
        self.arms[arm_id] = BanditArm(
            arm_id=arm_id,
            agent_name=agent_name,
            capability_match=capability_match,
            current_load=0.0,
            success_rate=0.5,
            A=np.eye(self.context_dim),
            b=np.zeros(self.context_dim)
        )

        _emit_records_learning_event("linucb_bandit", "arm_added", {
            "arm_id": arm_id,
            "agent_name": agent_name,
            "capability_match": capability_match
        })

    def select_arm(self, context: BanditContext) -> BanditDecision:
        """
        Select arm using LinUCB algorithm.

        Args:
            context: Context features for decision

        Returns:
            BanditDecision with selected arm and metadata
        """
        if not self.arms:
            raise ValueError("No arms available for selection")

        context_vector = context.to_vector()

        # Validate dimension compatibility
        if len(context_vector) != self.context_dim:
            raise ValueError(f"Context dimension mismatch: expected {self.context_dim}, got {len(context_vector)}")

        # Calculate UCB for each arm
        arm_scores = {}
        for arm_id, arm in self.arms.items():
            # Expected reward
            expected_reward = float(arm.theta @ context_vector)

            # Uncertainty (confidence interval width)
            A_inv = np.linalg.inv(arm.A)
            uncertainty = self.alpha * np.sqrt(context_vector @ A_inv @ context_vector)

            # UCB score
            ucb_score = expected_reward + uncertainty

            # Adjust for current load and capability
            load_penalty = arm.current_load * 0.1
            capability_bonus = arm.capability_match * 0.2

            final_score = ucb_score - load_penalty + capability_bonus
            arm_scores[arm_id] = final_score

        # Select best arm
        selected_arm_id = max(arm_scores.keys(), key=lambda k: arm_scores[k])
        selected_arm = self.arms[selected_arm_id]

        # Calculate confidence and uncertainty
        confidence = 1.0 / (1.0 + np.exp(-arm_scores[selected_arm_id]))
        uncertainty = self.alpha * np.sqrt(
            context_vector @ np.linalg.inv(selected_arm.A) @ context_vector
        )

        decision = BanditDecision(
            selected_arm=selected_arm_id,
            agent_name=selected_arm.agent_name,
            confidence=confidence,
            uncertainty=uncertainty,
            expected_reward=float(selected_arm.theta @ context_vector),
            context_used=context,
            all_arm_scores=arm_scores
        )

        # Record decision
        self.decision_history.append(decision)
        self.round_count += 1

        # Emit trace events
        _emit_records_execution_trace("linucb_bandit", "arm_selection", {
            "selected_arm": selected_arm_id,
            "confidence": confidence,
            "uncertainty": uncertainty,
            "round": self.round_count
        })

        _emit_emits_metric_event("linucb_bandit", "decision", {
            "confidence": confidence,
            "uncertainty": uncertainty,
            "exploration_rate": self.exploration_rate
        })

        return decision

    def update(self, decision: BanditDecision, reward: float):
        """
        Update bandit with observed reward.

        Args:
            decision: The decision that was made
            reward: Observed reward (0.0 to 1.0)
        """
        context_vector = decision.context_used.to_vector()

        # Update selected arm
        selected_arm = self.arms[decision.selected_arm]
        selected_arm.update_parameters(context_vector, reward)

        # Update global metrics
        self.total_reward += reward
        self.reward_history.append(reward)

        # Calculate and track regret
        max_expected = max(
            float(arm.theta @ context_vector)
            for arm in self.arms.values()
        )
        actual_reward = float(selected_arm.theta @ context_vector)
        regret = max_expected - actual_reward
        self.regret_history.append(regret)

        # Update exploration rate (decay over time)
        self.exploration_rate = max(0.01, 0.1 * np.exp(-self.round_count / 1000))

        # Apply decay to historical data
        for arm in self.arms.values():
            arm.A *= self.decay_factor
            arm.b *= self.decay_factor

        # Emit learning events
        _emit_records_learning_event("linucb_bandit", "reward_observed", {
            "reward": reward,
            "cumulative_reward": self.total_reward,
            "regret": regret,
            "round": self.round_count
        })

        _emit_feeds_meta_learning("linucb_bandit", "reward_update", {
            "arm_id": decision.selected_arm,
            "reward": reward,
            "context_features": context_vector.tolist()[:10]  # First 10 features
        })

        _emit_updates_routing_strategy("linucb_bandit", "bandit_update", {
            "selected_arm": decision.selected_arm,
            "new_success_rate": reward,
            "exploration_rate": self.exploration_rate
        })

    def get_arm_statistics(self) -> dict[str, dict[str, float]]:
        """Get statistics for all arms"""
        stats = {}
        for arm_id, arm in self.arms.items():
            # Estimate success rate from theta parameters
            estimated_success_rate = float(np.mean(arm.theta))

            # Calculate confidence in estimate
            A_inv = np.linalg.inv(arm.A)
            confidence = 1.0 / (1.0 + np.trace(A_inv))

            stats[arm_id] = {
                "success_rate": estimated_success_rate,
                "confidence": confidence,
                "current_load": arm.current_load,
                "capability_match": arm.capability_match,
                "samples_tracked": int(np.trace(arm.A) / self.decay_factor)
            }

        return stats

    def save_state(self, filepath: str):
        """Save bandit state to file"""
        state = {
            "context_dim": self.context_dim,
            "alpha": self.alpha,
            "decay_factor": self.decay_factor,
            "round_count": self.round_count,
            "total_reward": self.total_reward,
            "exploration_rate": self.exploration_rate,
            "arms": {
                arm_id: {
                    "arm_id": arm.arm_id,
                    "agent_name": arm.agent_name,
                    "capability_match": arm.capability_match,
                    "current_load": arm.current_load,
                    "success_rate": arm.success_rate,
                    "A": arm.A.tolist(),
                    "b": arm.b.tolist(),
                    "theta": arm.theta.tolist()
                }
                for arm_id, arm in self.arms.items()
            },
            "reward_history": self.reward_history,
            "regret_history": self.regret_history
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        _emit_stores_learning_state("linucb_bandit", "state_saved", {
            "filepath": filepath,
            "round_count": self.round_count,
            "total_reward": self.total_reward
        })

    def load_state(self, filepath: str):
        """Load bandit state from file"""
        with open(filepath) as f:
            state = json.load(f)

        self.context_dim = state["context_dim"]
        self.alpha = state["alpha"]
        self.decay_factor = state["decay_factor"]
        self.round_count = state["round_count"]
        self.total_reward = state["total_reward"]
        self.exploration_rate = state["exploration_rate"]
        self.reward_history = state["reward_history"]
        self.regret_history = state["regret_history"]

        # Restore arms
        self.arms = {}
        for arm_id, arm_data in state["arms"].items():
            arm = BanditArm(
                arm_id=arm_data["arm_id"],
                agent_name=arm_data["agent_name"],
                capability_match=arm_data["capability_match"],
                current_load=arm_data["current_load"],
                success_rate=arm_data["success_rate"]
            )
            arm.A = np.array(arm_data["A"])
            arm.b = np.array(arm_data["b"])
            arm.theta = np.array(arm_data["theta"])
            self.arms[arm_id] = arm

        _emit_stores_learning_state("linucb_bandit", "state_loaded", {
            "filepath": filepath,
            "round_count": self.round_count,
            "arms_count": len(self.arms)
        })

    def reset(self):
        """Reset bandit to initial state"""
        for arm in self.arms.values():
            arm.A = np.eye(self.context_dim)
            arm.b = np.zeros(self.context_dim)
            arm.theta = np.zeros(self.context_dim)

        self.round_count = 0
        self.total_reward = 0.0
        self.reward_history = []
        self.decision_history = []
        self.regret_history = []
        self.exploration_rate = 0.1

        _emit_stores_learning_state("linucb_bandit", "reset", {
            "arms_reset": len(self.arms)
        })

# Utility functions for context creation
def create_bandit_context(
    intent_embedding: np.ndarray,
    intent_text: str,
    user_history: dict[str, Any],
    system_metrics: dict[str, Any],
    adg_metrics: dict[str, Any]
) -> BanditContext:
    """Create bandit context from various inputs"""

    # Calculate intent features
    intent_length = len(intent_text.split())
    intent_complexity = min(1.0, len(intent_text) / 500.0)  # Normalize by 500 chars

    # Extract user features
    user_history_score = user_history.get("success_rate", 0.5)
    user_success_rate = user_history.get("avg_reward", 0.5)

    # System features
    current_load = system_metrics.get("cpu_usage", 0.5)
    time_of_day = int(time.strftime("%H"))
    day_of_week = int(time.strftime("%w"))  # 0 = Sunday

    # ADG features
    adg_territory_score = adg_metrics.get("territory_score", 0.5)
    confidence_tiers = adg_metrics.get("confidence_tiers", {
        "C0": 100, "C1": 200, "C2": 300, "C3": 400
    })

    return BanditContext(
        intent_embedding=intent_embedding,
        intent_length=intent_length,
        intent_complexity=intent_complexity,
        user_history_score=user_history_score,
        user_success_rate=user_success_rate,
        current_load=current_load,
        time_of_day=time_of_day,
        day_of_week=day_of_week,
        adg_territory_score=adg_territory_score,
        confidence_tiers=confidence_tiers
    )

def calculate_routing_reward(
    selected_agent: str,
    task_completed: bool,
    completion_time: float,
    user_satisfaction: float | None = None
) -> float:
    """Calculate reward for routing decision"""

    base_reward = 1.0 if task_completed else 0.0

    # Time penalty (faster is better)
    time_penalty = max(0.0, 1.0 - completion_time / 300.0)  # 5 min max
    time_reward = base_reward * time_penalty

    # User satisfaction bonus
    if user_satisfaction is not None:
        satisfaction_bonus = (user_satisfaction - 0.5) * 0.2
        time_reward += satisfaction_bonus

    # Ensure reward is in [0, 1] range
    reward = max(0.0, min(1.0, time_reward))

    return reward

__all__ = [
    "LinUCBBandit",
    "BanditContext",
    "BanditArm",
    "BanditDecision",
    "create_bandit_context",
    "calculate_routing_reward"
]
