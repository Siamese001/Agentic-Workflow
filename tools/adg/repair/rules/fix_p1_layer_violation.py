"""Repair rule for P1 layer violations.

Adds guardian exemptions for known-safe violations only.
All other violations require human refactoring.
"""

from __future__ import annotations

from pathlib import Path

from tools.adg.repair.base_rule import BaseRepairRule
from tools.adg.repair.rule_engine import repair_rule
from tools.adg.repair.types import Deficiency, FixResult


@repair_rule("fix_p1_layer_violation", priority=5)
class FixP1LayerViolationRule(BaseRepairRule):
    """Repair rule for P1 layer violations.

    This rule only applies guardian exemptions to known-safe violations.
    All other layer violations require human refactoring.
    """

    rule_id = "fix_p1_layer_violation"
    rule_name = "Fix P1 Layer Violation"
    rule_description = "Add guardian exemption for known-safe P1 layer violations"
    rule_priority = 5

    # Known-safe violations that can be auto-exempted
    KNOWN_SAFE_VIOLATIONS: dict[str, str] = {}

    def match(self, deficiency: Deficiency) -> bool:
        """Check if this rule applies to the deficiency."""
        return deficiency.issue_type == "layer_violation"

    def can_fix(self, deficiency: Deficiency) -> tuple[bool, str]:
        """Determine if the fix can be safely applied."""
        file_path = str(deficiency.file_path)

        # Only auto-fix if in known-safe list
        if file_path in self.KNOWN_SAFE_VIOLATIONS:
            return True, "Known-safe violation with documented justification"

        return False, "Layer violation requires human refactoring"

    def apply_fix(self, deficiency: Deficiency) -> FixResult:
        """Apply the fix by adding a guardian exemption comment."""
        file_path = Path(deficiency.file_path)

        if not file_path.exists():
            return FixResult(
                success=False,
                deficiency_id=deficiency.id,
                error_message=f"File not found: {file_path}",
            )

        justification = self.KNOWN_SAFE_VIOLATIONS.get(str(file_path))
        if not justification:
            return FixResult(
                success=False,
                deficiency_id=deficiency.id,
                error_message="No justification available for this violation",
            )

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)

            # Find the import line (from the violation metadata)
            line_no = deficiency.line_no
            if line_no is None or line_no < 1 or line_no > len(lines):
                return FixResult(
                    success=False,
                    deficiency_id=deficiency.id,
                    error_message=f"Invalid line number: {line_no}",
                )

            # Insert guardian comment before the import line
            guardian_comment = f"# guardian: allow-layer-violation -- {justification}\n"
            lines[line_no - 1] = guardian_comment + lines[line_no - 1]

            file_path.write_text("".join(lines), encoding="utf-8")

            return FixResult(
                success=True,
                deficiency_id=deficiency.id,
            )
        except Exception as e:
            return FixResult(
                success=False,
                deficiency_id=deficiency.id,
                error_message=f"Failed to apply fix: {e}",
            )

    def verify_fix(self, deficiency: Deficiency, result: FixResult) -> bool:
        """Verify the fix was applied correctly."""
        if not result.success:
            return False

        file_path = Path(deficiency.file_path)
        if not file_path.exists():
            return False

        try:
            content = file_path.read_text(encoding="utf-8")
            justification = self.KNOWN_SAFE_VIOLATIONS.get(str(file_path))
            if not justification:
                return False

            # Check if guardian comment exists
            guardian_line = f"# guardian: allow-layer-violation -- {justification}"
            return guardian_line in content
        except Exception:
            return False
