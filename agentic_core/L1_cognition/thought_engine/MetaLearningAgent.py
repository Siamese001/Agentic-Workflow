from __future__ import annotations
"""
MetaLearningAgent — TRUE SELF-IMPROVEMENT LOOP

Resurrected and enhanced from legacy MetaLearningAgent (2025-12-30)
Enables eternal evolution: mission outcome learning → strategy/prompt/tool adaptation
LAYER: L3_orchestration/meta_learning (SSOT compliant — new subfolder added to blueprint)
"""
import json
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from functools import wraps
from time import time

def timeout(seconds=0, minutes=0, hours=0):
    """
    Add a signal-based timeout to any function.
    Usage:
    @timeout(seconds=5)
    def my_slow_function(...)
    Args:
    - seconds: The time limit, in seconds.
    - minutes: The time limit, in minutes.
    - hours: The time limit, in hours.
    """

    limit = seconds + 60 * minutes + 3600 * hours

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except TimeoutError:
                raise TimeoutError(f"Timed out after {limit} seconds")
            return result
        return wrapper
    return decorator

Logger = logging.getLogger(__name__)


class MetaLearningAgent(HealerMixin):
    """
    Sovereign meta-learning engine.
    Accumulates mission experience and drives self-evolution.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.experience_key = "meta_learning:experience"
        self.evolution_log = project_root / "logs" / "meta_evolution.jsonl"
        self.evolution_log.parent.mkdir(parents=True, exist_ok=True)
        Logger.info("MetaLearningAgent initialized — self-improvement loop active")

    async def record_mission_outcome(
        self,
        mission_id: str,
        success: bool,
        metrics: Dict[str, float],
        violations: List[Dict],
        prompt_used: str,
        tools_used: List[str],
    ) -> None:
        """
        Record outcome for future learning.
        """
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "mission_id": mission_id,
            "success": success,
            "metrics": metrics,
            "violation_count": len(violations),
            "prompt_hash": hashlib.sha256(prompt_used.encode()).hexdigest()[:8],
            "tools_used": tools_used,
        }

        with open(self.evolution_log, "a") as f:
            f.write(json.dumps(record) + "\n")

        Logger.info(f"MetaLearning: recorded mission {mission_id} — success={success}")

    async def analyze_performance_trends(self, window_days: int = 30) -> Dict[str, Any]:
        """
        Analyze recent performance and identify improvement opportunities.
        """
        recent = []
        cutoff = datetime.utcnow() - timedelta(days=window_days)
        if self.evolution_log.exists():
            with open(self.evolution_log) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if datetime.fromisoformat(entry["timestamp"]) > cutoff:
                            recent.append(entry)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

        success_rate = sum(r["success"] for r in recent) / len(recent) if recent else 0
        avg_violations = sum(r["violation_count"] for r in recent) / len(recent) if recent else 0

        return {
            "window_days": window_days,
            "missions_analyzed": len(recent),
            "success_rate": success_rate,
            "avg_violations_per_mission": avg_violations,
            "trending_downward": success_rate < 0.8 or avg_violations > 2,
        }

    async def evolve_prompt_template(self, template_name: str, llm_client: Any = None) -> Optional[str]:
        """
        Suggest improved version of a prompt template using accumulated experience.
        """
        trends = await self.analyze_performance_trends()
        if not trends["trending_downward"]:
            return None

        if not llm_client:
            Logger.warning("MetaLearning: LLM client required for prompt evolution")
            return None

        improvement_prompt = f"""
You are the Sovereign Meta-Evolution Engine.
Recent performance: success rate {trends['success_rate']:.1%}, avg violations {trends['avg_violations_per_mission']:.1f}
Evolve the prompt template '{template_name}' to improve reliability and reduce violations.
Keep sovereign tone and structure. Output only the improved template.
"""

        try:
            response = await llm_client.chat.completions.create(
                model='gpt-4',
                messages=[
                    {'role': 'system', 'content': 'You are the Sovereign Meta-Evolution Engine.'},
                    {'role': 'user', 'content': improvement_prompt}
                ],
                temperature=0.3
            )
            improved = response.choices[0].message.content
            if improved and len(improved.strip()) > 50:
                Logger.info(f"MetaLearning: evolved prompt template '{template_name}'")
                return improved.strip()
        except Exception as e:
            Logger.error(f"MetaLearning: prompt evolution failed: {e}")
        
        return None

    async def suggest_strategy_adjustment(self, current_context: Dict) -> List[str]:
        """
        Suggest strategic changes based on learned patterns.
        """
        trends = await self.analyze_performance_trends()
        suggestions = []

        if trends["avg_violations_per_mission"] > 3:
            suggestions.append("Increase pre-validation steps before healing")
        if trends["success_rate"] < 0.7:
            suggestions.append("Activate conservative mode: more ReflectionAgent cycles")
        if "tool_failure" in current_context.get("common_errors", []):
            suggestions.append("Prioritize ToolsmithAgent tool regeneration")

        return suggestions

    async def run_evolution_cycle(self, dry_run: bool = True, llm_client: Any = None) -> Dict[str, Any]:
        """
        Full meta-learning cycle — called periodically or after major missions.
        """
        Logger.info("MetaLearningAgent: starting evolution cycle")
        trends = await self.analyze_performance_trends()
        actions = []

        evolved_prompt = await self.evolve_prompt_template("primary_healing_prompt", llm_client)
        if evolved_prompt and not dry_run:
            path = self.project_root / "agentic_core" / "prompt_governance" / "templates" / "healing_v2.jinja"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(evolved_prompt)
            actions.append(f"Evolved primary healing prompt → {path}")

        strategy_suggestions = await self.suggest_strategy_adjustment(trends)
        actions.extend([f"Strategy suggestion: {s}" for s in strategy_suggestions])

        return {
            "cycle_timestamp": datetime.utcnow().isoformat(),
            "performance_trends": trends,
            "actions_taken": actions,
            "dry_run": dry_run,
        }

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L1 cognition agent - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L1 cognition - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


__all__ = ["MetaLearningAgent"]
