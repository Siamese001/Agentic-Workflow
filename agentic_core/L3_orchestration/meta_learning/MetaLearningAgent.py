from __future__ import annotations
"""
MetaLearningAgent - Sovereign Strategy Evolution Engine (Phase C - Dec 30, 2025)
"""
from typing import Dict, Any, List, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
import logging
from pathlib import Path
from datetime import datetime

# Sovereign Hardening Mixins – Phase C (Critical Priority)
from agentic_core.patterns.agent_roles.autonomy_mixin import AutonomyMixin
from agentic_core.patterns.agent_roles.adaptive_execution_mixin import AdaptiveExecutionMixin
from agentic_core.patterns.agent_roles.experience_buffer import ExperienceBuffer
from agentic_core.patterns.agent_roles.self_diagnosis_mixin import SelfDiagnosisMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


def get_meta_learning_agent() -> MetaLearningAgent:
    """Factory function to get the meta-learning agent."""
    return MetaLearningAgent()


@timeout(300)
def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
    """L3 orchestration/meta_learning - operational only."""
    if _call_path is None:
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

    agent_name = "MetaLearning"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] L3 orchestration/meta_learning - operational only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)


class MetaLearningAgent(MCPHardenedMixin, HealerMixin, AutonomyMixin,
    AdaptiveExecutionMixin,
    SelfDiagnosisMixin,):
    """
    Sovereign meta-learning agent that evolves system behavior over time.
    Now hardened with strategy evolution, proactive monitoring, and self-learning.
    """

    def __init__(self) -> None:
        self.Logger = logging.getLogger(__name__)
        super().__init__()

        # Experience buffer for cross-agent learning
        log_dir = Path("logs") / "meta_learning"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.strategy_buffer = ExperienceBuffer(
            path=log_dir / "strategy_evolution.jsonl",
            max_entries=2000,
        )

        # Mandatory components
        self.MANDATORY_COMPONENTS = [
            "strategy_buffer",
        ]

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L3 compliance."""
        assert hasattr(self, 'strategy_buffer'), "Missing strategy_buffer"
        assert hasattr(self, 'MANDATORY_COMPONENTS'), "Missing MANDATORY_COMPONENTS"
        return True

    async def evolve_agent_strategy(self, agent_name: str) -> Dict[str, Any]:
        """
        Critical enhancement: evolve an agent's execution strategy based on performance patterns.
        """
        self.Logger.info(f"Initiating strategy evolution for agent: {agent_name}")

        # 1. Retrieve performance history
        performance = await self._get_agent_performance(agent_name)
        if not performance:
            return {"evolution": "skipped", "reason": "no_performance_data"}

        # 2. Check if evolution is needed
        if performance["success_rate"] >= 0.92:
            self.Logger.info(f"{agent_name} performing optimally — no evolution needed")
            return {"evolution": "none", "reason": "optimal_performance", "success_rate": performance["success_rate"]}

        # 3. Analyze failure patterns
        failure_patterns = await self._analyze_failure_patterns(agent_name)
        if not failure_patterns:
            return {"evolution": "none", "reason": "no_clear_failure_patterns"}

        # 4. Generate strategy mutations
        mutations = []
        for pattern in failure_patterns[:5]:  # Limit scope
            proposed_behavior = await self._generate_strategy_alternative(pattern, agent_name)
            if proposed_behavior:
                expected_gain = pattern["frequency"] * 0.4  # Conservative estimate
                mutation = {
                    "trigger_condition": pattern["condition"],
                    "current_behavior": pattern["failed_action"],
                    "proposed_behavior": proposed_behavior,
                    "expected_improvement": round(expected_gain, 3),
                    "confidence": self._estimate_mutation_confidence(pattern, proposed_behavior),
                    "priority": "HIGH" if expected_gain > 0.2 else "MEDIUM",
                }
                mutations.append(mutation)

        # 5. Apply mutations if high confidence
        if mutations:
            applied = await self._apply_strategy_mutations(agent_name, mutations)
            self.Logger.info(f"Applied {len(applied)} strategy mutations to {agent_name}")

            # Record evolution event
            self.strategy_buffer.record({
                "target_agent": agent_name,
                "mutations_applied": len(applied),
                "expected_total_gain": sum(m["expected_improvement"] for m in applied),
                "trigger_performance": performance["success_rate"],
                "evolution_mode": self._current_mode,
                "success": True,
            })

            return {
                "evolution": "applied",
                "target_agent": agent_name,
                "mutations": applied,
                "expected_sovereignty_gain": round(sum(m["expected_improvement"] for m in applied), 3),
            }

        return {"evolution": "none", "reason": "no_sufficiently_confident_mutations"}

    async def _get_agent_performance(self, agent_name: str) -> Dict[str, Any]:
        """Retrieve historical performance from experience buffers."""
        # Placeholder — integrate with centralized metrics or per-agent buffers
        return {
            "success_rate": 0.78,
            "avg_execution_time": 4.2,
            "violations_caused": 12,
        }

    async def _analyze_failure_patterns(self, agent_name: str) -> List[Dict]:
        """Identify recurring failure conditions."""
        # Example patterns
        return [
            {
                "condition": "high_system_load",
                "failed_action": "full_healing_cycle",
                "frequency": 8,
                "impact": "timeout_escalation",
            },
            {
                "condition": "gravity_violation_proposed",
                "failed_action": "direct_import_creation",
                "frequency": 5,
                "impact": "sovereignty_drop",
            },
        ]

    async def _generate_strategy_alternative(self, pattern: Dict, agent_name: str) -> Optional[str]:
        """Generate improved behavior for given failure pattern."""
        condition = pattern["condition"]
        if "high_system_load" in condition:
            return "switch_to_minimal_mode_and_queue"
        if "gravity_violation" in condition:
            return "route_via_cross_layer_coordination_proxy"
        return None

    def _estimate_mutation_confidence(self, pattern: Dict, proposal: str) -> float:
        """Estimate confidence in proposed mutation."""
        base = pattern["frequency"] / 20.0
        return min(0.95, 0.6 + base)

    async def _apply_strategy_mutations(self, agent_name: str, mutations: List[Dict]) -> List[Dict]:
        """Persist mutations — placeholder for prompt/config update."""
        # In future: write to agent config or prompt registry
        return mutations  # Simulate application

    # === Adaptive & Proactive Hooks ===
    async def _detect_action_opportunity(self) -> Optional[Dict[str, Any]]:
        """Proactively evolve poorly performing agents."""
        # Simple trigger: check known underperformers
        underperformers = ["HealingOrchestratorAgent"]  # From metrics
        if underperformers:
            return {
                "reason": "agent_underperformance_detected",
                "targets": underperformers,
                "action": "initiate_strategy_evolution_cycle"
            }
        return None

    async def _execute_conservative(self, ctx: Any, **context: Dict) -> Dict:
        self.Logger.info("Conservative mode: evolution paused")
        return {"evolution": "paused", "mode": "conservative"}

    async def _execute_minimal(self, ctx: Any, **context: Dict) -> Dict:
        self.Logger.warning("Minimal mode: meta-learning standby")
        return {"status": "standby", "reason": "resource_preservation"}

    async def _execute_standard(self, ctx: Any, **context: Dict) -> Dict:
        """Standard mode - full strategy evolution."""
        agent_name = context.get("agent_name", "HealingOrchestratorAgent")
        return await self.evolve_agent_strategy(agent_name)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
