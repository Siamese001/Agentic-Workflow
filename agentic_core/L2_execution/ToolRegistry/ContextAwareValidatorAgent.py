from __future__ import annotations
"""
ContextAwareValidatorAgent – Sovereign Agent Role Component (Phase 32 – Dec 30, 2025)

Purpose:
  Move validation from rigid rule enforcement to intelligent, context-sensitive judgment.
  Enables:
    - Detection of justified constitutional exceptions
    - Contextual fix suggestions
    - Auto-fix confidence scoring
  Critical for all 21 validators to reduce false positives and improve healing precision.

Constitutional Alignment:
  - Prevents over-enforcement of canon
  - Enables nuanced sovereignty interpretation
  - Improves healing success rate through better suggestions
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


class ContextAwareValidatorAgent(HealerMixin, MCPHardenedMixin):
    """
    Base class for intelligent validators.
    Subclasses implement rule-specific logic while inheriting context analysis.
    """

    def __init__(self) -> None:
        self.Logger = logging.getLogger(f"{self.__class__.__name__}.Context")

    async def validate_with_context(self, target: Path, rule: str) -> Dict[str, Any]:
        """
        Main entry point: intelligent validation with context.
        Returns enriched result with justification and fix suggestions.
        """
        # 1. Basic rule check
        basic_result = await self._basic_rule_check(target, rule)
        if basic_result["compliant"]:
            self.Logger.debug(f"Basic compliance passed for {target} on rule {rule}")
            return basic_result

        # 2. Context analysis for potential justified exception
        context = await self._analyze_violation_context(target, rule)
        if context.get("justified_exception", False):
            self.Logger.info(f"Justified exception found for {target}: {context['justification']}")
            return {
                "compliant": True,
                "exception": True,
                "justification": context["justification"],
                "context": context,
                "rule": rule,
                "target": str(target),
            }

        # 3. Generate intelligent fix suggestion
        fix = await self._generate_contextual_fix(target, rule, context)

        result = {
            "compliant": False,
            "rule": rule,
            "target": str(target),
            "violation_details": basic_result.get("details"),
            "context": context,
            "suggested_fix": fix,
            "auto_fixable": fix.get("confidence", 0.0) > 0.9,
            "fix_confidence": fix.get("confidence", 0.0),
        }

        self.Logger.info(
            f"Violation detected on {target} for {rule} — "
            f"auto_fixable={result['auto_fixable']} (confidence={result['fix_confidence']:.0%})"
        )

        return result

    async def _basic_rule_check(self, target: Path, rule: str) -> Dict[str, Any]:
        """
        REQUIRED OVERRIDE: Pure syntactic/semantic rule enforcement.
        Must return {"compliant": bool, "details": optional str}
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _basic_rule_check"
        )

    async def _analyze_violation_context(self, target: Path, rule: str) -> Dict[str, Any]:
        """
        Analyze why Violation occurred — look for justification patterns.
        Default: no justification (conservative).
        Override for rule-specific exceptions.
        """
        # Example patterns to override:
        # - Temporary migration files
        # - Approved exceptions in comments
        # - Known legacy code with TODO
        return {
            "justified_exception": False,
            "justification": None,
            "context_factors": {
                "file_age_days": self._get_file_age(target),
                "recent_modifications": self._has_recent_changes(target),
                "contains_todo": "# TODO:" in target.read_text(encoding="utf-8", errors="ignore"),
                "in_migration_path": "migration" in str(target),
            },
        }

    async def _generate_contextual_fix(self, target: Path, rule: str, context: Dict) -> Dict[str, Any]:
        """
        Generate intelligent, context-aware fix suggestion.
        Default: generic suggestion.
        Override for high-precision fixes.
        """
        return {
            "suggested_action": f"Manually review and correct {rule} Violation",
            "confidence": 0.5,
            "reason": "No specific contextual fix pattern matched",
            "example": None,
        }

    # === Helper utilities — can be overridden ===

    def _get_file_age(self, target: Path) -> int:
        """Days since file creation."""
        try:
            import time
            return int((time.time() - target.stat().st_ctime) / 86400)
        except:
            return 0

    def _has_recent_changes(self, target: Path) -> bool:
        """True if modified in last 7 days."""
        try:
            import time
            return (time.time() - target.stat().st_mtime) < (7 * 86400)
        except:
            return False

    async def health_check(self) -> Dict[str, bool]:
        """Standard interface for SelfDiagnosisMixin."""
        return {"healthy": True}

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
