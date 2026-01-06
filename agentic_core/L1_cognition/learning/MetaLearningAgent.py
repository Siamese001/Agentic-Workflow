"""
Meta Learning Agent - Experience Replay & Pattern Extraction

Implements learning feedback loop for adaptive reasoning with:
- Experience replay buffer for state-action-outcome tracking
- Strategy weight adjustment based on rewards
- Pattern extraction from clustered experiences
- Adaptive capability improvement over missions
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional, Deque
from collections import deque
from dataclasses import dataclass, field
import time
import random
import hashlib


@dataclass
class Experience:
    """Single experience entry for replay."""
    experience_id: str
    state: Dict[str, Any]
    thought_type: str  # "cot", "tot", "react", "reflection"
    action: Dict[str, Any]
    outcome: Dict[str, Any]
    reward: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class Pattern:
    """Extracted pattern from experiences."""
    pattern_id: str
    pattern_type: str  # "success", "failure", "common"
    description: str
    frequency: int
    avg_reward: float
    examples: List[str] = field(default_factory=list)


class MetaLearningAgent:
    """
    Meta Learning Agent - Adaptive strategy learning through experience replay.
    
    Provides:
    - Experience replay buffer (1000 experiences)
    - Strategy weight adjustment based on rewards
    - Pattern extraction from experience clusters
    - Adaptive strategy biasing for future reasoning
    """
    
    def __init__(self, replay_capacity: int = 1000):
        """
        Initialize meta learning agent.
        
        Args:
            replay_capacity: Maximum experiences in replay buffer
        """
        self.replay_buffer: Deque[Experience] = deque(maxlen=replay_capacity)
        self.replay_capacity = replay_capacity
        
        # Strategy weights (initial uniform)
        self.strategy_weights: Dict[str, float] = {
            "cot": 1.0,      # Chain of Thought
            "tot": 1.0,      # Tree of Thoughts
            "react": 1.0,    # ReAct
            "reflection": 1.0,  # Self-reflection
            "direct": 1.0,   # Direct answer
        }
        
        # Extracted patterns
        self.patterns: List[Pattern] = []
        
        # Statistics
        self.total_experiences = 0
        self.total_replays = 0
        self.weight_updates = 0
        self.patterns_extracted = 0
        
        # Learning parameters
        self.learning_rate = 0.1
        self.min_weight = 0.1
        self.replay_batch_size = 32
        self.pattern_extraction_interval = 200
    
    def store_experience(
        self,
        state: Dict[str, Any],
        thought_type: str,
        outcome: Dict[str, Any],
        reward: float,
        action: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store experience in replay buffer.
        
        Args:
            state: State/context when action was taken
            thought_type: Type of reasoning strategy used
            outcome: Outcome of the action
            reward: Reward signal (-1 to 1)
            action: Optional action details
            
        Returns:
            Experience ID
        """
        # Generate ID
        exp_id = f"exp_{self.total_experiences}_{int(time.time())}"
        
        experience = Experience(
            experience_id=exp_id,
            state=state,
            thought_type=thought_type,
            action=action or {},
            outcome=outcome,
            reward=reward
        )
        
        self.replay_buffer.append(experience)
        self.total_experiences += 1
        
        # Trigger pattern extraction periodically
        if self.total_experiences % self.pattern_extraction_interval == 0:
            self._extract_patterns()
        
        return exp_id
    
    def replay_and_learn(self, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Replay experiences and update strategy weights.
        
        Args:
            batch_size: Number of experiences to sample (default: replay_batch_size)
            
        Returns:
            Learning results with weight updates
        """
        batch_size = batch_size or self.replay_batch_size
        
        if len(self.replay_buffer) < batch_size:
            return {"status": "insufficient_data", "buffer_size": len(self.replay_buffer)}
        
        self.total_replays += 1
        
        # Sample batch
        indices = random.sample(range(len(self.replay_buffer)), batch_size)
        batch = [self.replay_buffer[i] for i in indices]
        
        # Calculate reward per strategy type
        type_rewards: Dict[str, List[float]] = {}
        for exp in batch:
            if exp.thought_type not in type_rewards:
                type_rewards[exp.thought_type] = []
            type_rewards[exp.thought_type].append(exp.reward)
        
        # Update weights based on average rewards
        old_weights = self.strategy_weights.copy()
        
        for thought_type, rewards in type_rewards.items():
            if thought_type in self.strategy_weights:
                avg_reward = sum(rewards) / len(rewards)
                # Update weight: increase for positive rewards, decrease for negative
                delta = avg_reward * self.learning_rate
                self.strategy_weights[thought_type] = max(
                    self.min_weight,
                    self.strategy_weights[thought_type] + delta
                )
        
        # Normalize weights
        total = sum(self.strategy_weights.values())
        if total > 0:
            for k in self.strategy_weights:
                self.strategy_weights[k] /= total
        
        self.weight_updates += 1
        
        return {
            "status": "success",
            "batch_size": batch_size,
            "old_weights": old_weights,
            "new_weights": self.strategy_weights.copy(),
            "type_rewards": {k: sum(v)/len(v) for k, v in type_rewards.items()}
        }
    
    def get_strategy_bias(self) -> Dict[str, float]:
        """
        Get current strategy weights for biased selection.
        
        Returns:
            Dictionary of strategy weights (sum to 1)
        """
        return self.strategy_weights.copy()
    
    def select_strategy(self) -> str:
        """
        Select strategy using weighted random selection.
        
        Returns:
            Selected strategy type
        """
        strategies = list(self.strategy_weights.keys())
        weights = list(self.strategy_weights.values())
        
        # Weighted random selection
        total = sum(weights)
        r = random.random() * total
        cumulative = 0.0
        
        for strategy, weight in zip(strategies, weights):
            cumulative += weight
            if r <= cumulative:
                return strategy
        
        return strategies[-1]  # Fallback
    
    def _extract_patterns(self) -> None:
        """Extract patterns from experience clusters."""
        if len(self.replay_buffer) < 50:
            return
        
        # Group by outcome type
        success_exps = [e for e in self.replay_buffer if e.reward > 0.5]
        failure_exps = [e for e in self.replay_buffer if e.reward < -0.3]
        
        # Extract success patterns
        if len(success_exps) >= 10:
            # Find common thought types in successes
            type_counts: Dict[str, int] = {}
            for exp in success_exps:
                type_counts[exp.thought_type] = type_counts.get(exp.thought_type, 0) + 1
            
            most_common = max(type_counts.items(), key=lambda x: x[1])
            
            pattern = Pattern(
                pattern_id=f"pattern_success_{self.patterns_extracted}",
                pattern_type="success",
                description=f"Strategy '{most_common[0]}' leads to success",
                frequency=most_common[1],
                avg_reward=sum(e.reward for e in success_exps) / len(success_exps),
                examples=[e.experience_id for e in success_exps[:5]]
            )
            self.patterns.append(pattern)
            self.patterns_extracted += 1
        
        # Extract failure patterns
        if len(failure_exps) >= 10:
            type_counts = {}
            for exp in failure_exps:
                type_counts[exp.thought_type] = type_counts.get(exp.thought_type, 0) + 1
            
            most_common = max(type_counts.items(), key=lambda x: x[1])
            
            pattern = Pattern(
                pattern_id=f"pattern_failure_{self.patterns_extracted}",
                pattern_type="failure",
                description=f"Strategy '{most_common[0]}' often fails",
                frequency=most_common[1],
                avg_reward=sum(e.reward for e in failure_exps) / len(failure_exps),
                examples=[e.experience_id for e in failure_exps[:5]]
            )
            self.patterns.append(pattern)
            self.patterns_extracted += 1
    
    def get_patterns(self, pattern_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get extracted patterns.
        
        Args:
            pattern_type: Filter by type ("success", "failure", "common")
            
        Returns:
            List of pattern dictionaries
        """
        patterns = self.patterns
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        
        return [
            {
                "id": p.pattern_id,
                "type": p.pattern_type,
                "description": p.description,
                "frequency": p.frequency,
                "avg_reward": p.avg_reward,
                "examples": p.examples
            }
            for p in patterns
        ]
    
    def get_success_patterns(self) -> List[Dict[str, Any]]:
        """Get patterns associated with success."""
        return self.get_patterns("success")
    
    def get_failure_patterns(self) -> List[Dict[str, Any]]:
        """Get patterns associated with failure."""
        return self.get_patterns("failure")
    
    def reset_weights(self) -> None:
        """Reset strategy weights to uniform."""
        for k in self.strategy_weights:
            self.strategy_weights[k] = 1.0 / len(self.strategy_weights)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics."""
        return {
            "replay_capacity": self.replay_capacity,
            "buffer_size": len(self.replay_buffer),
            "total_experiences": self.total_experiences,
            "total_replays": self.total_replays,
            "weight_updates": self.weight_updates,
            "patterns_extracted": self.patterns_extracted,
            "current_weights": self.strategy_weights.copy(),
            "learning_rate": self.learning_rate
        }

    def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# Global instance
meta_learner = MetaLearningAgent()
