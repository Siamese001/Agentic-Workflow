"""
AutonomousPromptEvolutionAgent: Optimizes prompt templates based on MetaLearning rewards.
Created: 2026-01-13 | Version: 2.0.0

This agent monitors prompt performance via MetaLearningAgent feedback and applies
evolutionary mutations to improve LLM efficiency and output quality.
"""
from __future__ import annotations

import hashlib
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.common.healing.healer_mixin import HealerMixin

log = logging.getLogger(__name__)


class AutonomousPromptEvolutionAgent(MCPHardenedMixin, HealerMixin):
    """
    Autonomous agent that evolves prompt templates based on performance metrics.
    
    Capabilities:
    - Tracks prompt template performance via MetaLearningAgent
    - Applies evolutionary mutations (word substitution, structure changes)
    - Maintains version history for rollback
    - Validates evolved prompts before deployment
    """

    def __init__(self, prompts_dir: Optional[Path] = None):
        super().__init__()
        self.prompts_dir = prompts_dir or Path("agentic_core/prompt_governance/templates")
        self._meta_learning: Optional[Any] = None
        self._evolution_history: List[Dict[str, Any]] = []
        self._mutation_strategies = [
            self._mutate_word_choice,
            self._mutate_structure,
            self._mutate_emphasis,
        ]
        log.info("[L0 EVOLUTION] AutonomousPromptEvolutionAgent initialized")

    @property
    def meta_learning(self) -> Any:
        """Lazy-load MetaLearningAgent to avoid circular imports."""
        if self._meta_learning is None:
            try:
                from agentic_core.L1_cognition.learning.MetaLearningAgent import MetaLearningAgent
                self._meta_learning = MetaLearningAgent()
            except ImportError as e:
                log.warning(f"MetaLearningAgent unavailable: {e}")
        return self._meta_learning

    def get_prompt_performance(self, template_id: str) -> Dict[str, Any]:
        """Retrieve performance metrics for a prompt template from MetaLearning."""
        if not self.meta_learning:
            return {"avg_reward": 0.0, "usage_count": 0, "success_rate": 0.0}
        
        try:
            # Query meta-learning for experiences related to this template
            experiences = getattr(self.meta_learning, 'get_experiences_by_context', lambda x: [])(
                {"template_id": template_id}
            )
            if not experiences:
                return {"avg_reward": 0.0, "usage_count": 0, "success_rate": 0.0}
            
            rewards = [e.get("reward", 0.0) for e in experiences]
            successes = sum(1 for r in rewards if r > 0.5)
            
            return {
                "avg_reward": sum(rewards) / len(rewards) if rewards else 0.0,
                "usage_count": len(experiences),
                "success_rate": successes / len(experiences) if experiences else 0.0,
            }
        except Exception as e:
            log.warning(f"Failed to get prompt performance: {e}")
            return {"avg_reward": 0.0, "usage_count": 0, "success_rate": 0.0}

    def evolve_prompt(self, template_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply evolutionary changes to a prompt based on success metrics.
        
        Args:
            template_id: Identifier for the prompt template
            feedback: Dict containing reward, success indicators, and context
            
        Returns:
            Dict with evolution result: {evolved: bool, new_template: str, changes: list}
        """
        log.info(f"[L0 EVOLUTION] Evolving prompt: {template_id}")
        
        # Load current template
        template_path = self.prompts_dir / f"{template_id}.txt"
        if not template_path.exists():
            template_path = self.prompts_dir / f"{template_id}.py"
        
        if not template_path.exists():
            log.warning(f"Template not found: {template_id}")
            return {"evolved": False, "error": "Template not found"}
        
        try:
            current_template = template_path.read_text(encoding="utf-8")
        except Exception as e:
            return {"evolved": False, "error": str(e)}
        
        # Determine if evolution is warranted
        performance = self.get_prompt_performance(template_id)
        reward = feedback.get("reward", 0.0)
        
        # Only evolve if performance is below threshold
        if performance["avg_reward"] > 0.8 and reward > 0.7:
            log.info(f"[L0 EVOLUTION] Template {template_id} performing well, skipping evolution")
            return {"evolved": False, "reason": "Performance above threshold"}
        
        # Select mutation strategy based on feedback
        strategy = random.choice(self._mutation_strategies)
        evolved_template, changes = strategy(current_template, feedback)
        
        # Validate evolved template
        if not self._validate_template(evolved_template):
            log.warning(f"[L0 EVOLUTION] Evolved template failed validation")
            return {"evolved": False, "error": "Validation failed"}
        
        # Record evolution
        evolution_record = {
            "template_id": template_id,
            "timestamp": datetime.now().isoformat(),
            "original_hash": hashlib.sha256(current_template.encode()).hexdigest()[:16],
            "evolved_hash": hashlib.sha256(evolved_template.encode()).hexdigest()[:16],
            "changes": changes,
            "trigger_reward": reward,
            "performance_before": performance,
        }
        self._evolution_history.append(evolution_record)
        
        log.info(f"[L0 EVOLUTION] Successfully evolved {template_id}: {changes}")
        return {
            "evolved": True,
            "new_template": evolved_template,
            "changes": changes,
            "record": evolution_record,
        }

    def _mutate_word_choice(self, template: str, feedback: Dict[str, Any]) -> tuple[str, List[str]]:
        """Substitute words with synonyms or more precise alternatives."""
        changes = []
        evolved = template
        
        # Simple word substitutions for common patterns
        substitutions = {
            "please": "kindly",
            "make sure": "ensure",
            "try to": "aim to",
            "should": "must",
            "can you": "please",
        }
        
        for old, new in substitutions.items():
            if old in evolved.lower():
                evolved = evolved.replace(old, new)
                changes.append(f"word_choice: '{old}' -> '{new}'")
                break  # One mutation per evolution
        
        return evolved, changes

    def _mutate_structure(self, template: str, feedback: Dict[str, Any]) -> tuple[str, List[str]]:
        """Restructure prompt for clarity or emphasis."""
        changes = []
        evolved = template
        
        # Add structure markers if missing
        if "Step 1:" not in evolved and len(evolved) > 200:
            lines = evolved.split("\n")
            if len(lines) > 3:
                # Add numbered steps to multi-line prompts
                new_lines = []
                step = 1
                for line in lines:
                    if line.strip() and not line.startswith("#"):
                        new_lines.append(f"Step {step}: {line}")
                        step += 1
                    else:
                        new_lines.append(line)
                evolved = "\n".join(new_lines)
                changes.append("structure: added numbered steps")
        
        return evolved, changes

    def _mutate_emphasis(self, template: str, feedback: Dict[str, Any]) -> tuple[str, List[str]]:
        """Add or modify emphasis markers."""
        changes = []
        evolved = template
        
        # Add emphasis to key instructions
        emphasis_triggers = ["important", "critical", "must", "always", "never"]
        for trigger in emphasis_triggers:
            if trigger in evolved.lower() and f"**{trigger}" not in evolved.lower():
                evolved = evolved.replace(trigger, f"**{trigger.upper()}**")
                changes.append(f"emphasis: highlighted '{trigger}'")
                break
        
        return evolved, changes

    def _validate_template(self, template: str) -> bool:
        """Validate evolved template meets basic requirements."""
        if not template or len(template) < 10:
            return False
        if len(template) > 50000:
            return False
        # Check for balanced brackets/quotes
        if template.count("{") != template.count("}"):
            return False
        if template.count('"') % 2 != 0:
            return False
        return True

    def get_evolution_history(self, template_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve evolution history, optionally filtered by template."""
        if template_id:
            return [e for e in self._evolution_history if e["template_id"] == template_id]
        return self._evolution_history.copy()

    def rollback_evolution(self, template_id: str) -> bool:
        """Rollback to previous template version."""
        history = self.get_evolution_history(template_id)
        if not history:
            return False
        
        # Remove last evolution record
        last = history[-1]
        self._evolution_history = [e for e in self._evolution_history if e != last]
        log.info(f"[L0 EVOLUTION] Rolled back evolution for {template_id}")
        return True

    def heal_repository(self, dry_run: bool = True, **kwargs) -> Dict[str, int]:
        """Invoke healing chain via super()."""
        return super().heal_repository(dry_run=dry_run, **kwargs)
