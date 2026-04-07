from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_signs_execution_trace,
)

"\nRLStrategy - Consolidated Reinforcement Learning Orchestration Strategy\n\nThis module consolidates logic from:\n- ActorCriticOrchestratorAgent\n- PPOOrchestratorAgent\n- QLearningOrchestratorAgent\n- RLOrchestratorAgent\n- ReinforceCriticOrchestratorAgent\n\nSSOT PRINCIPLE:\n    All RL-related orchestration flows through this strategy,\n    which is injected into Orchestrator.\n"
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)

Logger = logging.getLogger(__name__)


@dataclass
class RLStrategy:
    """
    Strategy for reinforcement learning orchestration missions.

    Consolidates:
    - Actor-Critic methods (from ActorCriticOrchestratorAgent)
    - PPO optimization (from PPOOrchestratorAgent)
    - Q-Learning (from QLearningOrchestratorAgent)
    - General RL (from RLOrchestratorAgent)
    - REINFORCE with critic (from ReinforceCriticOrchestratorAgent)

    Usage:
        strategy = RLStrategy(project_root=Path.cwd())
        orchestrator = Orchestrator(strategy=strategy)
        result = orchestrator.run_mission({"dry_run": True})
    """

    project_root: Path = field(default_factory=Path.cwd)
    algorithm: str = "actor_critic"

    @property
    def name(self) -> str:
        """Return the strategy name."""
        return f"RLStrategy({self.algorithm})"

    def get_tiers(self) -> dict[str, list[str]]:
        """
        Return the tiered execution plan for RL missions.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "RLStrategy.get_tiers", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RLStrategy.get_tiers", "p0_governance")
        return {
            "Tier 0: Environment Setup": ["EnvironmentValidatorAgent"],
            "Tier 1: Policy Evaluation": ["PolicyEvaluatorAgent"],
            "Tier 2: Optimization": [self._get_optimizer_agent()],
            "Tier 3: Validation": ["RewardValidatorAgent"],
        }

    def _get_optimizer_agent(self) -> str:
        """Get the optimizer agent based on algorithm."""
        algorithm_map = {
            "actor_critic": "ActorCriticOptimizerAgent",
            "ppo": "PPOOptimizerAgent",
            "q_learning": "QLearningOptimizerAgent",
            "reinforce": "ReinforceOptimizerAgent",
        }
        return algorithm_map.get(self.algorithm, "ActorCriticOptimizerAgent")

    def get_agent(self, agent_name: str) -> Any | None:
        """
        Get or create an agent instance by name.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            Agent instance or None if not available
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RLStrategy.get_agent")

        Logger.debug(f"[RLStrategy] Agent {agent_name} requested (stub)")
        return None

    def execute_agent(
        self, agent: Any, agent_name: str, dry_run: bool = True, execute: bool = False, **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute a single agent and return results.

        Args:
            agent: The agent instance to execute
            agent_name: Name of the agent (for logging)
            dry_run: If True, only report violations
            execute: If True, apply fixes
            **kwargs: Additional agent-specific parameters

        Returns:
            Dictionary with execution results
        """
        if agent is None:
            return {
                "status": "SKIPPED",
                "violations_found": 0,
                "violations_fixed": 0,
                "execution_time_ms": 0,
                "error_message": f"{agent_name} not implemented",
            }
        start_time = get_clock().now_epoch()
        try:
            if hasattr(agent, "heal_repository"):
                result = agent.heal_repository(dry_run=dry_run, execute=execute)
                execution_time_ms = (get_clock().now_epoch() - start_time) * 1000
                return {
                    "status": "PASS" if result.get("errors", 0) == 0 else "FAIL",
                    "violations_found": result.get("violations", 0),
                    "violations_fixed": result.get("fixed", 0),
                    "execution_time_ms": execution_time_ms,
                    "error_message": None,
                }
            else:
                return {
                    "status": "ERROR",
                    "violations_found": 0,
                    "violations_fixed": 0,
                    "execution_time_ms": 0,
                    "error_message": f"{agent_name} has no heal_repository method",
                }
        except (ValueError, TypeError) as e:
            execution_time_ms = (get_clock().now_epoch() - start_time) * 1000
            return {
                "status": "ERROR",
                "violations_found": 0,
                "violations_fixed": 0,
                "execution_time_ms": execution_time_ms,
                "error_message": str(e),
            }

    def should_abort_tier(self, tier_name: str, tier_results: list[dict[str, Any]], execute: bool) -> bool:
        """
        Determine if execution should abort after a tier.

        Args:
            tier_name: Name of the completed tier
            tier_results: Results from all agents in the tier
            execute: Whether we're in execute mode

        Returns:
            True if execution should abort, False to continue
        """
        if "Tier 0" in tier_name:
            for result in tier_results:
                if result.get("status") == "FAIL":
                    return True
        return False
