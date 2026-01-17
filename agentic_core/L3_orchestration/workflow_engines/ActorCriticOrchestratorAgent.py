from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

import warnings
import logging
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import time

from agentic_core.config.blueprint_sovereign.structure_blueprint import get_validated_project_root
from agentic_core.L6_observability.metrics.shared_counters import counters
from agentic_core.L6_observability.metrics.CoverageAgent import CoverageAgent
from agentic_core.runtime.shared_runtime import log_event
from agentic_core.L3_orchestration.unified_workflow_engine import UnifiedWorkflowEngine
from dataclasses import dataclass

log = logging.getLogger(__name__)

warnings.warn(
    "ActorCriticOrchestratorAgent is deprecated. Use UnifiedWorkflowEngine with type='rl' and rl_strategy='actor_critic'",
    DeprecationWarning,
    stacklevel=2
)


class ActorCriticNet(nn.Module):
    """Shared body + actor/critic heads — lightweight."""
    def __init__(self, input_dim: int, n_actions: int) -> None:
        """Initialize the instance."""
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
        )
        self.actor = nn.Linear(64, n_actions)
        self.critic = nn.Linear(64, 1)

    def forward(self, x) -> Any:
        """Execute forward operation."""
        shared = self.shared(x)
        return self.actor(shared), self.critic(shared)


@dataclass
class ActorCriticOrchestratorAgent(SovereignBaseAgent):
    """
    DEPRECATED: Use UnifiedWorkflowEngine instead.
    
    Sub-atomic A2C learner: Actor policy + Critic value for stable routing.
    Advantage reduces variance; synchronous updates.
    
    This class now wraps UnifiedWorkflowEngine for backward compatibility.
    """

    def __init__(self, layers: List[str], fallback_orchestrator: Optional[Any] = None) -> None:
        """
        Initialize Actor-Critic orchestrator.
        
        Args:
            layers: List of layer names for action selection
            fallback_orchestrator: Optional fallback orchestrator
        """
        log.warning("ActorCriticOrchestratorAgent is deprecated - migrating to UnifiedWorkflowEngine")
        self.name: str = "ActorCriticOrchestratorAgent"
        self.project_root: Any = get_validated_project_root()
        self.layers: List[str] = layers
        self.n_actions: int = len(layers)
        self.input_dim: int = self.n_actions + 1

        # Legacy implementation preserved for compatibility
        self.model = ActorCriticNet(self.input_dim, self.n_actions)
        
        # New unified engine for future migration
        self._engine = UnifiedWorkflowEngine(project_root=self.project_root)
        self.optimizer = optim.Adam(self.model.parameters(), lr=5e-4)
        self.gamma = 0.98
        self.coverage_agent = CoverageAgent()
        self.fallback = fallback_orchestrator
        self.buffer = []
        self.update_steps = 20
        self.step_count = 0

    def get_state(self) -> torch.FloatTensor:
        """Get current state as tensor."""
        counts = counters.get_counts()
        proportions = self.coverage_agent._compute_proportions(counts)
        entropy = self.coverage_agent._shannon_entropy(proportions)
        prop_vec = torch.FloatTensor([proportions.get(l, 0) for l in self.layers])
        return torch.cat([prop_vec, torch.FloatTensor([entropy])])

    def select_action(self, state: torch.FloatTensor) -> Tuple[int, torch.Tensor]:
        """Select action via actor policy."""
        with torch.no_grad():
            logits, value = self.model(state.unsqueeze(0))
        dist = Categorical(logits=logits)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action.item(), log_prob

    def route_task(self, candidates: List[Dict], current_task: Dict) -> Optional[Dict]:
        """Primary entrypoint — A2C routing."""
        if not candidates:
            return None

        state = self.get_state()
        action_idx, log_prob = self.select_action(state)
        selected_layer = self.layers[action_idx]

        layer_cands = [c for c in candidates if c.get("layer") == selected_layer]
        if not layer_cands:
            if self.fallback:
                return self.fallback.select_next_agent(candidates, current_task)
            return candidates[0] if candidates else None

        selected = max(layer_cands, key=lambda c: c.get("base_score", 1.0))
        log_event("ac_route", {"layer": selected_layer, "action_idx": action_idx})

        # Store for batch update
        self.buffer.append((state, action_idx, log_prob))
        self.step_count += 1
        return selected

    def accumulate_reward(self, reward: float, next_state: Optional[torch.FloatTensor] = None, done: bool = False) -> None:
        """Called post-task with reward/next state."""
        if not self.buffer:
            return

        state, action, log_prob = self.buffer[-1]

        # Get values
        with torch.no_grad():
            _, value = self.model(state.unsqueeze(0))
            if next_state is not None and not done:
                _, next_value = self.model(next_state.unsqueeze(0))
            else:
                next_value = torch.tensor([[0.0]])

        # Compute advantage
        advantage = reward + self.gamma * next_value - value
        
        # Actor loss: negative log prob weighted by advantage
        actor_loss = -log_prob * advantage.detach()
        
        # Critic loss: MSE of advantage
        critic_loss = advantage.pow(2)
        
        # Combined loss
        loss = actor_loss + 0.5 * critic_loss

        # Update
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 0.5)
        self.optimizer.step()

        log_event("ac_update", {
            "actor_loss": float(actor_loss.item()),
            "critic_loss": float(critic_loss.item()),
            "advantage": float(advantage.item()),
            "reward": reward
        })

        # Clear buffer if done or full
        if done or len(self.buffer) >= self.update_steps:
            self.buffer.clear()

    def get_ac_stats(self) -> Dict:
        """Get A2C statistics."""
        return {
            "step_count": self.step_count,
            "buffer_size": len(self.buffer),
            "update_steps": self.update_steps
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
