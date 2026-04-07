"""Core types for ADG Repair Orchestrator.

Defines deficiency categorization, fix categories, and data structures
for the repair system.

SEVERITY ↔ FIX-CATEGORY BRIDGE
--------------------------------
FixCategory maps onto SeverityLevel as follows:

    ADG:CRITICAL  (SeverityLevel.CRITICAL)  → BLOCK_FIX    (human engineering required)
    ADG:HIGH      (SeverityLevel.HIGH)       → SUGGEST_FIX  (HITL approval before applying)
    ADG:MEDIUM    (SeverityLevel.MEDIUM)     → AUTO_FIX     (safe deterministic fix)
    ADG:LOW       (SeverityLevel.LOW)        → AUTO_FIX     (auto-fix or skip)

Use FixCategory.from_severity() to translate at runtime.
"""

from __future__ import annotations

import enum
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


class FixCategory(enum.Enum):
    """Categorization of deficiencies by fixability.

    AUTO_FIX: Safe to apply automatically without human review.
        Corresponds to: ADG:MEDIUM, ADG:LOW  (SeverityLevel.MEDIUM / LOW)
        Examples: Missing __all__, wrong guardian format, import order, unused imports

    SUGGEST_FIX: Needs human-in-the-loop approval before applying.
        Corresponds to: ADG:HIGH  (SeverityLevel.HIGH)
        Examples: Layer reassignment, import reordering, docstring additions

    BLOCK_FIX: Requires human engineering — cannot be auto-fixed.
        Corresponds to: ADG:CRITICAL  (SeverityLevel.CRITICAL)
        Examples: Architecture violations, missing critical edges, design flaws
    """

    AUTO_FIX = "auto_fix"
    SUGGEST_FIX = "suggest_fix"
    BLOCK_FIX = "block_fix"

    @classmethod
    def from_severity(cls, severity: object) -> "FixCategory":
        """Translate a SeverityLevel into the corresponding FixCategory.

        Args:
            severity: A SeverityLevel instance from
                      agentic_core.L5_safety.config.severity.

        Returns:
            FixCategory matching the severity's repair disposition.
        """
        from agentic_core.L5_safety.config.severity import SeverityLevel

        mapping = {
            SeverityLevel.CRITICAL: cls.BLOCK_FIX,
            SeverityLevel.HIGH: cls.SUGGEST_FIX,
            SeverityLevel.MEDIUM: cls.AUTO_FIX,
            SeverityLevel.LOW: cls.AUTO_FIX,
            SeverityLevel.INFO: cls.AUTO_FIX,
        }
        return mapping.get(severity, cls.BLOCK_FIX)


@dataclass
class Deficiency:
    """Represents a single deficiency found in ADG analysis.

    Attributes:
        id: Unique deterministic identifier for this deficiency
        category: FixCategory assignment
        file_path: Path to the file containing the deficiency
        line_no: Line number (1-indexed), None if file-level
        issue_type: Machine-readable issue type (e.g., "missing_all", "guardian_format")
        description: Human-readable description
        suggested_fix: Suggested code fix (if applicable)
        confidence: Confidence score 0.0-1.0 (below 0.8 escalates to SUGGEST/BLOCK)
        metadata: Additional context-specific data
    """

    id: str
    category: FixCategory
    file_path: str
    line_no: int | None
    issue_type: str
    description: str
    suggested_fix: str | None = None
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate confidence and auto-escalate if too low."""
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")

        # Auto-escalate category if confidence is too low
        if self.confidence < 0.8 and self.category == FixCategory.AUTO_FIX:
            self.category = FixCategory.SUGGEST_FIX


@dataclass
class FixResult:
    """Result of applying a fix.

    Attributes:
        deficiency_id: ID of the deficiency that was fixed
        success: Whether the fix was applied successfully
        original_content: Original file content (for rollback)
        new_content: New file content after fix
        error_message: Error message if fix failed
        backup_path: Path to backup file (if created)
    """

    deficiency_id: str
    success: bool
    original_content: str | None = None
    new_content: str | None = None
    error_message: str | None = None
    backup_path: str | None = None


@dataclass
class RepairRunResult:
    """Overall result of a repair orchestrator run.

    Attributes:
        timestamp: Run timestamp
        deficiencies_found: Total deficiencies detected
        fixes_applied: Number of AUTO_FIX deficiencies fixed
        fixes_suggested: Number of SUGGEST_FIX items
        fixes_blocked: Number of BLOCK_FIX items
        failed_fixes: Number of fixes that failed to apply
        fix_results: List of individual fix results
        git_checkpoint: Git branch/tag created for rollback
        log_path: Path to detailed execution log
    """

    timestamp: str
    deficiencies_found: int
    fixes_applied: int
    fixes_suggested: int
    fixes_blocked: int
    failed_fixes: int
    fix_results: list[FixResult] = field(default_factory=list)
    git_checkpoint: str | None = None
    log_path: str | None = None


@dataclass
class RuleMatch:
    """Result of matching a deficiency against repair rules.

    Attributes:
        rule_id: ID of the matching rule
        rule_priority: Priority (lower = higher priority)
        can_apply: Whether the rule can apply to this deficiency
        confidence_adjusted: Potentially adjusted confidence based on rule
    """

    rule_id: str
    rule_priority: int
    can_apply: bool
    confidence_adjusted: float
