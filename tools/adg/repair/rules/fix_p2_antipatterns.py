"""Repair rule for P2 exception antipatterns.

This is a pure classifier - it never applies code changes.
All P2 antipatterns require human classification and review.
"""

from __future__ import annotations

from tools.adg.repair.base_rule import BaseRepairRule
from tools.adg.repair.rule_engine import repair_rule
from tools.adg.repair.types import Deficiency, FixResult


@repair_rule("fix_p2_antipatterns", priority=15)
class FixP2AntipatternsRule(BaseRepairRule):
    """Repair rule for P2 exception antipatterns.

    This rule is a pure classifier - it never applies code changes.
    All P2 antipatterns require human classification and review.
    """

    rule_id = "fix_p2_antipatterns"
    rule_name = "Fix P2 Exception Antipatterns"
    rule_description = "Classify P2 antipatterns for human review (no auto-fix)"
    rule_priority = 15

    # P2 antipattern types
    P2_ANTIPATTERNS = {
        "silent_exception_swallow",
        "broad_exception_catch",
        "log_and_swallow",
        "return_none_swallow",
    }

    def match(self, deficiency: Deficiency) -> bool:
        """Check if this rule applies to the deficiency."""
        return deficiency.issue_type in self.P2_ANTIPATTERNS

    def can_fix(self, deficiency: Deficiency) -> tuple[bool, str]:
        """Determine if the fix can be safely applied.

        P2 antipatterns always require human classification - no auto-fix.
        """
        return False, "P2 antipatterns require human classification and review"

    _REMEDIATION_HINTS: dict[str, str] = {
        "return_none_swallow": "Replace 'return None' with structured error dict or re-raise",
        "log_and_swallow": "Add 'raise' after log statement, or return structured error dict",
        "silent_exception_swallow": "Add logging + raise, or structured error return; use guardian exemption for cleanup/teardown with HITL approval",
        "broad_exception_catch": "Narrow exception type, or add re-raise; guardian exemption requires HITL approval per §8",
    }

    def apply_fix(self, deficiency: Deficiency) -> FixResult:
        """Apply the fix.

        This rule never applies code changes. Returns a structured classification
        report with the file, line, antipattern type, and remediation hint.
        """
        hint = self._REMEDIATION_HINTS.get(deficiency.issue_type, "Requires human review")
        return FixResult(
            success=False,
            deficiency_id=deficiency.id,
            error_message=(
                f"[P2-CLASSIFY] {deficiency.issue_type} | "
                f"{deficiency.file_path}:{deficiency.line_no} | "
                f"Hint: {hint}"
            ),
        )

    def verify_fix(self, deficiency: Deficiency, result: FixResult) -> bool:
        """Verify the fix.

        Since this rule never applies fixes, verification always returns True
        (no-op verifier).
        """
        return True
