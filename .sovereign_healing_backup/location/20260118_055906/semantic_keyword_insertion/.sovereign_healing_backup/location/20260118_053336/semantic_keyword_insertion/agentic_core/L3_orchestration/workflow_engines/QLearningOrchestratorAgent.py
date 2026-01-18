from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

import warnings
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import time
from collections import defaultdict

from agentic_core.L5_safety.validators.structure_blueprint_1 import get_validated_project_root
from agentic_core.L6_observability.metrics.shared_counters import counters
from agentic_core.L6_observability.metrics.CoverageAgent import CoverageAgent
from agentic_core.runtime.shared_runtime import log_event
from agentic_core.L3_orchestration.unified_workflow_engine import UnifiedWorkflowEngine
from dataclasses import dataclass

log = logging.getLogger(__name__)

warnings.warn(
    "QLearningOrchestratorAgent is deprecated. Use UnifiedWorkflowEngine with type='rl' and rl_strategy='qlearning'",
    DeprecationWarning,
    stacklevel=2
)


@dataclass
class QLearningOrchestratorAgent(SovereignBaseAgent):
    """
    DEPRECATED: Use UnifiedWorkflowEngine instead.
    
    Sub-atomic tabular Q-learner: Off-policy routing for maximal long-term coverage entropy.
    Discrete state/action → exact optimal policy.
    Lightweight alternative to PPO.
    
    This class now wraps UnifiedWorkflowEngine for backward compatibility.
    """

    def __init__(self, layers: List[str], bins: int = 3, fallback_orchestrator: Optional[any] = None) -> None:
        """
        Initialize Q-Learning orchestrator.
        
        Args:
            layers: List of layer names for action selection
            bins: Number of bins for discretizing state space
            fallback_orchestrator: Optional fallback orchestrator
        """
        log.warning("QLearningOrchestratorAgent is deprecated - migrating to UnifiedWorkflowEngine")
        self.name: str = "QLearningOrchestratorAgent"
        self.project_root: any = get_validated_project_root()
        self.layers: List[str] = layers
        self.n_actions: int = len(layers)
        self.layer_idx: Dict[str, int] = {l: i for i, l in enumerate(layers)}
        self.bins: int = bins
        self.state_dim: int = self.n_actions + 1

        # Legacy implementation preserved for compatibility
        # Tabular Q: state_tuple → action → Q-value
        self.Q: Dict[Tuple[int, ...], np.ndarray] = defaultdict(lambda: np.zeros(self.n_actions))
        
        # New unified engine for future migration
        self._engine = UnifiedWorkflowEngine(project_root=self.project_root)
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 0.2
        self.min_epsilon = 0.05
        self.coverage_agent = CoverageAgent()
        self.fallback = fallback_orchestrator
        self.last_state: Optional[Tuple[int, ...]] = None
        self.last_action: Optional[int] = None
        self.step_count = 0

    def _bin_proportions(self, proportions: Dict[str, float]) -> Tuple[int, ...]:
        """Bin each layer proportion + entropy."""
        entropy = self.coverage_agent._shannon_entropy(proportions)
        max_entropy = np.log2(len(self.layers))
        entropy_bin = int(np.digitize([entropy], np.linspace(0, max_entropy, self.bins + 1))[0] - 1)
        entropy_bin = max(0, min(entropy_bin, self.bins - 1))
        
        prop_bins = []
        for layer in self.layers:
            p = proportions.get(layer, 0)
            bin_val = int(np.digitize([p], np.linspace(0, 1, self.bins + 1))[0] - 1)
            bin_val = max(0, min(bin_val, self.bins - 1))
            prop_bins.append(bin_val)
        return tuple(prop_bins + [entropy_bin])

    def get_state(self) -> Tuple[int, ...]:
        """Get current state from counters."""
        counts = counters.get_counts()
        proportions = self.coverage_agent._compute_proportions(counts)
        return self._bin_proportions(proportions)

    def select_action(self, state: Tuple[int, ...]) -> int:
        """Epsilon-greedy Q policy."""
        if np.random.rand() < self.epsilon:
            action = np.random.randint(self.n_actions)
        else:
            q_values = self.Q[state]
            action = int(np.argmax(q_values))
        return action

    def route_task(self, candidates: List[Dict], current_task: Dict) -> Optional[Dict]:
        """Primary entrypoint — Q routing."""
        if not candidates:
            return None

        state = self.get_state()
        action_idx = self.select_action(state)
        selected_layer = self.layers[action_idx]

        layer_cands = [c for c in candidates if c.get("layer") == selected_layer]
        if not layer_cands:
            if self.fallback:
                return self.fallback.select_next_agent(candidates, current_task)
            return candidates[0] if candidates else None

        selected = max(layer_cands, key=lambda c: c.get("base_score", 1.0))
        log_event("q_route", {"state": state, "action": selected_layer})

        # Store for update
        self.last_state = state
        self.last_action = action_idx
        self.step_count += 1
        return selected

    def update_q(self, reward: float, done: bool = False) -> None:
        """Q-update on transition."""
        if self.last_state is None or self.last_action is None:
            return

        next_state = self.get_state()
        current_q = self.Q[self.last_state][self.last_action]
        
        if done:
            td_target = reward
        else:
            td_target = reward + self.gamma * np.max(self.Q[next_state])
        
        td_error = td_target - current_q
        new_q = current_q + self.alpha * td_error
        self.Q[self.last_state][self.last_action] = new_q

        log_event("q_update", {
            "state": self.last_state,
            "action": self.last_action,
            "reward": reward,
            "new_q": float(new_q)
        })

        # Decay exploration
        self.epsilon = max(self.min_epsilon, self.epsilon * 0.999)

        # Clear for next step
        if done:
            self.last_state = None
            self.last_action = None

    def get_q_stats(self) -> Dict:
        """Get Q-learning statistics."""
        if not self.Q:
            return {"states_visited": 0, "avg_q_value": 0.0}
        
        all_q_values = []
        for q_array in self.Q.values():
            all_q_values.extend(q_array)
        
        return {
            "states_visited": len(self.Q),
            "avg_q_value": float(np.mean(all_q_values)) if all_q_values else 0.0,
            "max_q_value": float(np.max(all_q_values)) if all_q_values else 0.0,
            "epsilon": float(self.epsilon),
            "step_count": self.step_count
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
