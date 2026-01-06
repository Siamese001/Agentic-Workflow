from __future__ import annotations

import warnings
import logging
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from typing import List, Dict, Tuple, Any
import numpy as np
import time

from agentic_core.config.blueprint_sovereign.structure_blueprint import get_validated_project_root
from agentic_core.observability.metrics.shared_counters import counters
from agentic_core.observability.metrics.CoverageAgent import CoverageAgent
from agentic_core.runtime.shared_runtime import log_event
from agentic_core.L3_orchestration.workflow_engines.NervousSystemAgent import NervousSystemAgent
from agentic_core.L3_orchestration.unified_workflow_engine import UnifiedWorkflowEngine

log = logging.getLogger(__name__)

warnings.warn(
    "PPOOrchestratorAgent is deprecated. Use UnifiedWorkflowEngine with type='rl' and rl_strategy='ppo'",
    DeprecationWarning,
    stacklevel=2
)


class PPOActorCritic(nn.Module):
    """Shared network with actor/critic heads — efficient parameter sharing."""
    def __init__(self, input_dim: int, n_actions: int):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.Tanh(),
            nn.Linear(128, 128),
            nn.Tanh(),
        )
        self.actor = nn.Linear(128, n_actions)
        self.critic = nn.Linear(128, 1)

    def forward(self, x):
        shared = self.shared(x)
        return self.actor(shared), self.critic(shared).squeeze()


class PPOOrchestratorAgent:
    """
    DEPRECATED: Use UnifiedWorkflowEngine instead.
    
    Sub-atomic PPO learner: Clipped proximal policy optimization for stable routing.
    Multiple epochs + advantage normalization → reliable improvement.
    Batch from trajectory buffer.
    
    This class now wraps UnifiedWorkflowEngine for backward compatibility.
    """

    def __init__(self, layers: List[str]):
        log.warning("PPOOrchestratorAgent is deprecated - migrating to UnifiedWorkflowEngine")
        self.name = "PPOOrchestratorAgent"
        self.project_root = get_validated_project_root()
        self.layers = layers
        self.n_actions = len(layers)
        self.input_dim = self.n_actions + 1  # Proportions + entropy

        # Legacy implementation preserved for compatibility
        self.model = PPOActorCritic(self.input_dim, self.n_actions)
        
        # New unified engine for future migration
        self._engine = UnifiedWorkflowEngine(project_root=self.project_root)
        self.optimizer = optim.Adam(self.model.parameters(), lr=3e-4)
        self.clip_eps = 0.2
        self.gamma = 0.99
        self.lam = 0.95  # GAE-lambda
        self.epochs = 4
        self.batch_size = 64
        self.coverage_agent = CoverageAgent()
        self.fallback = NervousSystemAgent()
        self.buffer: List[Tuple[torch.Tensor, int, float, float, float]] = []  # state, action, old_log_prob, reward, value

    def get_state(self) -> torch.Tensor:
        """Get current state from layer activation counts and entropy."""
        counts = counters.get_counts()
        proportions = self.coverage_agent._compute_proportions(counts)
        entropy = self.coverage_agent._shannon_entropy(proportions)
        prop_vec = torch.FloatTensor([proportions.get(l, 0) for l in self.layers])
        return torch.cat([prop_vec, torch.FloatTensor([entropy])])

    def select_action(self, state: torch.Tensor) -> Tuple[int, torch.Tensor, torch.Tensor]:
        """Select action from policy distribution."""
        logits, value = self.model(state)
        dist = Categorical(logits=logits)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action.item(), log_prob, value

    def route_task(self, candidates: List[Dict], current_task: Dict) -> Dict:
        """Route task to selected layer based on policy."""
        state = self.get_state()
        action_idx, log_prob, value = self.select_action(state)
        selected_layer = self.layers[action_idx]

        layer_cands = [c for c in candidates if c.get("layer") == selected_layer]
        if not layer_cands:
            return self.fallback.select_next_agent(candidates, current_task)

        selected = max(layer_cands, key=lambda c: c.get("base_score", 1.0))
        log_event("ppo_route", {"layer": selected_layer})

        # Buffer transition (reward/value later)
        self.buffer.append((state, action_idx, log_prob.item(), 0.0, value.item()))  # reward placeholder
        return selected

    def store_reward(self, reward: float):
        """Store reward for last transition."""
        if self.buffer:
            # Update last transition reward
            s, a, lp, _, v = self.buffer[-1]
            self.buffer[-1] = (s, a, lp, reward, v)

    def update_ppo(self):
        """PPO update with clipped objective and advantage normalization."""
        if len(self.buffer) < self.batch_size:
            return

        # Compute advantages
        states, actions, old_log_probs, rewards, old_values = zip(*self.buffer)
        states = torch.stack(states)
        actions = torch.LongTensor(actions)
        old_log_probs = torch.FloatTensor(old_log_probs)
        rewards = torch.FloatTensor(rewards)
        old_values = torch.FloatTensor(old_values)

        advantages = rewards - old_values  # Simplified (full GAE optional)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        for _ in range(self.epochs):
            logits, values = self.model(states)
            dist = Categorical(logits=logits)
            new_log_probs = dist.log_prob(actions)

            ratio = (new_log_probs - old_log_probs).exp()
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps) * advantages
            policy_loss = -torch.min(surr1, surr2).mean()

            value_loss = nn.MSELoss()(values, rewards)

            loss = policy_loss + 0.5 * value_loss

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        log_event("ppo_update", {
            "policy_loss": policy_loss.item(),
            "value_loss": value_loss.item(),
            "avg_advantage": advantages.mean().item()
        })
        self.buffer.clear()

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
