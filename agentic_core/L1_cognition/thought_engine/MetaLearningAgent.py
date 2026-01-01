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

from agentic_core.common.healing.healer_mixin import HealerMixin

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


__all__ = ["MetaLearningAgent"]
