from __future__ import annotations
"""
GovernanceAgent - Sovereign Constitutional Decision Maker (Phase B - Dec 30, 2025)
"""
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import logging

# Sovereign Hardening Mixins – Phase B (High Priority)
from agentic_core.patterns.agent_roles.autonomy_mixin import AutonomyMixin
from agentic_core.patterns.agent_roles.adaptive_execution_mixin import AdaptiveExecutionMixin
from agentic_core.patterns.agent_roles.experience_buffer import ExperienceBuffer
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout, HealTimeoutError


class GovernanceAgent(MCPHardenedMixin, SubatomicTestingMixin, 
    AutonomyMixin,
    AdaptiveExecutionMixin,
    HealerMixin,
):
    """
    Sovereign governance agent that makes constitutional decisions.
    Now hardened with intelligent confidence-based decision making.
    """

    def __init__(self) -> None:
        self.Logger = logging.getLogger(__name__)
        super().__init__()

        # Experience buffer for learning from past decisions
        log_dir = Path("logs") / "governance"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.experience_buffer = ExperienceBuffer(
            path=log_dir / "decision_experience.jsonl",
            max_entries=1500,
        )

    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make intelligent decision with confidence scoring and autonomous threshold.
        """
        self.Logger.info(f"Initiating decision for context: {context.get('issue_type', 'unknown')}")

        # 1. Generate multiple viable options
        options = await self._generate_options(context)
        if not options:
            return {
                "decision": "no_action",
                "autonomous": False,
                "confidence": 0.0,
                "reason": "no_viable_options_generated"
            }

        # 2. Score each option
        scored_options = []
        for option in options:
            confidence = await self._evaluate_option_confidence(option, context)
            risk = await self._assess_option_risk(option, context)
            net_score = confidence * (1.0 - risk)

            scored_options.append({
                "option": option,
                "confidence": confidence,
                "risk": risk,
                "net_score": net_score,
                "justification": await self._justify_option(option, context)
            })

        # 3. Select best option
        best = max(scored_options, key=lambda x: x["net_score"])

        # 4. Autonomous execution threshold
        autonomous = best["confidence"] >= 0.80 and best["risk"] <= 0.30

        # 5. Record decision for learning
        self.experience_buffer.record({
            "issue_type": context.get("issue_type"),
            "target": context.get("target"),
            "options_evaluated": len(options),
            "best_confidence": best["confidence"],
            "best_risk": best["risk"],
            "autonomous": autonomous,
            "selected_option": best["option"]["action"],
            "mode": self._current_mode,
        })

        return {
            "decision": best["option"],
            "autonomous": autonomous,
            "confidence": round(best["confidence"], 3),
            "risk": round(best["risk"], 3),
            "justification": best["justification"],
            "all_options": scored_options,
            "mode": self._current_mode,
        }

    async def _generate_options(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate 3-5 viable response options."""
        issue_type = context.get("issue_type", "unknown")
        options = []

        # Base options
        options.append({
            "action": "enforce_strict_compliance",
            "description": "Immediately correct Violation per canon",
        })
        options.append({
            "action": "grant_temporary_exception",
            "description": "Allow with monitoring and expiration",
        })
        options.append({
            "action": "escalate_to_human",
            "description": "Request sovereign review",
        })

        # Context-specific
        if "migration" in str(context.get("target", "")).lower():
            options.append({
                "action": "approve_migration_exception",
                "description": "Temporary allowance during refactor"
            })

        return options

    async def _evaluate_option_confidence(self, option: Dict, context: Dict) -> float:
        """Score option confidence based on historical success and alignment."""
        action = option["action"]

        # Historical success rate
        historical = self.experience_buffer.predict_success_probability(
            action=action,
            target=str(context.get("target", ""))
        )

        # Constitutional alignment bonus
        alignment_bonus = 0.3 if "enforce" in action else 0.1 if "exception" in action else 0.0

        return min(1.0, historical + alignment_bonus)

    async def _assess_option_risk(self, option: Dict, context: Dict) -> float:
        """Assess sovereignty risk of option."""
        action = option["action"]

        if "exception" in action:
            return 0.6  # High risk of drift
        if "escalate" in action:
            return 0.1  # Low risk
        return 0.3  # Standard enforcement

    async def _justify_option(self, option: Dict, context: Dict) -> str:
        """Generate human-readable justification."""
        return f"Selected {option['action']} based on historical patterns and constitutional alignment"

    # === AutonomyMixin Override ===
    async def _detect_action_opportunity(self) -> Optional[Dict[str, Any]]:
        """Proactively review recent decisions for patterns."""
        recent = self.experience_buffer.find_similar(limit=10)
        if recent:
            low_confidence = [e for e in recent if e.get("best_confidence", 1.0) < 0.7]
            if len(low_confidence) > 3:
                return {
                    "reason": "high_uncertainty_pattern_detected",
                    "pending_decisions": len(self.decision_queue)
                }
                return {"pending_decisions": len(self.decision_queue)}

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[Set] = None) -> Dict[str, int]:
        """L5 safety agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # === Adaptive Execution ===
    async def _execute_conservative(self, ctx: Any, **context: Dict) -> Dict:
        self.Logger.info("Conservative mode: always escalate")
        return {
            "decision": {"action": "escalate_to_human"},
            "autonomous": False,
            "confidence": 1.0,
            "reason": "conservative_mode_forced_escalation"
        }

    async def _execute_minimal(self, ctx: Any, **context: Dict) -> Dict:
        self.Logger.warning("Minimal mode: no governance action")
        return {"decision": "standby", "autonomous": True, "reason": "resource_preservation"}

    async def _execute_standard(self, ctx: Any, **context: Dict) -> Dict:
        """Standard mode - full decision making."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        return await self.make_decision(context)
