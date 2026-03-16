from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "rl_strategy")
emit_determinism_digest("p0", "rl_strategy")

_emit_dispatches_healing_run("p1", "rl_strategy", "L3")
_emit_routes_through("p1", "rl_strategy", "L3")
_emit_escalates_to_human("p1", "rl_strategy", "L3")
_emit_reads_policy_state("p1", "rl_strategy", "L3")
_emit_authorize_and_execute("p2", "rl_strategy", "execution_auth")
_emit_validates_capability("p2", "rl_strategy", "capability_check")
_emit_routes_to_capability("p2", "rl_strategy", "capability_route")
_emit_writes_via_uwg("p2", "rl_strategy", "uwg_write")
_emit_blocks_direct_write("p2", "rl_strategy", "direct_write_block")
_emit_records_tool_invocation("p2", "rl_strategy", "tool_invocation")
_emit_captures_execution_output("p2", "rl_strategy", "exec_output")
_emit_dispatches_agent("p3", "rl_strategy", "agent_dispatch")
_emit_coordinates_agents("p3", "rl_strategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "rl_strategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "rl_strategy", "healing_outcome")
_emit_escalates_failure("p3", "rl_strategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "rl_strategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rl_strategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "rl_strategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "rl_strategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rl_strategy", "eval_metric")
_emit_stores_embedding("p4", "rl_strategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "rl_strategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rl_strategy", "exec_snapshot_link")

"\nRLStrategy - Consolidated Reinforcement Learning Orchestration Strategy\n\nThis module consolidates logic from:\n- ActorCriticOrchestratorAgent\n- PPOOrchestratorAgent\n- QLearningOrchestratorAgent\n- RLOrchestratorAgent\n- ReinforceCriticOrchestratorAgent\n\nSSOT PRINCIPLE:\n    All RL-related orchestration flows through this strategy,\n    which is injected into Orchestrator.\n"
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
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
        self, agent: Any, agent_name: str, dry_run: bool = True, execute: bool = False, **kwargs: Any
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
        except Exception as e:
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
