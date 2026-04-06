"""
Severity Level SSOT — Single Source of Truth for severity classifications.

Canonical definition of severity levels used across:
- ADG violations and findings
- Pre-commit gate reporting
- Validation results
- Quality metrics

SEVERITY TAXONOMY
-----------------
Severity levels are defined by two dimensions:
1. IMPACT: What happens if this issue reaches production?
2. URGENCY: How quickly must this be addressed?

LEVEL DEFINITIONS
----------------
"""

from __future__ import annotations

from enum import Enum
from typing import Literal


class SeverityLevel(Enum):
    """
    Canonical severity levels for all systems.

    MAPPING TO OTHER SYSTEMS
    ------------------------
    Ruff:       P0 → CRITICAL, P1 → HIGH, P2 → MEDIUM, P3 → LOW
    ADG:        P1 → CRITICAL, P2 → HIGH, P3 → MEDIUM, P4 → LOW
    Pre-commit: CRITICAL/HIGH/MEDIUM/LOW/INFO → direct mapping

    SEMANTIC DEFINITIONS
    --------------------
    CRITICAL (P0/P1):
        - IMPACT: System-breaking, security breach, data loss, or constitutional violation
        - URGENCY: Immediate - MUST block commit until fixed
        - EXAMPLES: Layer boundary violations, security vulnerabilities, PowerShell usage,
                    missing critical dependencies, broken imports in production code

    HIGH (P1/P2):
        - IMPACT: Bugs that affect functionality, architectural violations, anti-patterns
        - URGENCY: High - should fix before commit, degrades quality significantly
        - EXAMPLES: Unused imports, global mutations, test coverage gaps, deprecated APIs,
                    silent exception swallowers, circular dependencies

    MEDIUM (P2/P3):
        - IMPACT: Code quality issues, maintainability concerns, style violations
        - URGENCY: Medium - consider fixing, technical debt accumulation
        - EXAMPLES: Long functions, complex cyclomatic complexity, inconsistent naming,
                    missing docstrings, TODO comments without owners

    LOW (P3/P4):
        - IMPACT: Minor style issues, formatting, informational
        - URGENCY: Low - nice to have, can be deferred
        - EXAMPLES: Line length violations, trailing whitespace, missing type hints in utility code,
                    unused variables in tests, debug print statements

    INFO:
        - IMPACT: No issue - informational or passed status
        - URGENCY: N/A
        - EXAMPLES: Hook passed successfully, hook skipped (no matching files)
    """

    CRITICAL = "critical"  # P0/P1 - Blocks commit
    HIGH = "high"          # P1/P2 - Should fix before commit
    MEDIUM = "medium"      # P2/P3 - Consider fixing
    LOW = "low"            # P3/P4 - Informational
    INFO = "info"          # Passed/clean status

    def __str__(self) -> str:
        return self.value

    @property
    def p_level(self) -> str:
        """Return the P-level designation (e.g., P0, P1, P2, P3, P4)."""
        mapping = {
            SeverityLevel.CRITICAL: "P0/P1",
            SeverityLevel.HIGH: "P1/P2",
            SeverityLevel.MEDIUM: "P2/P3",
            SeverityLevel.LOW: "P3/P4",
            SeverityLevel.INFO: "N/A",
        }
        return mapping[self]

    @property
    def blocks_commit(self) -> bool:
        """Return True if this severity should block commits."""
        return self in (SeverityLevel.CRITICAL, SeverityLevel.HIGH)

    @property
    def display_name(self) -> str:
        """Human-readable name for UI/display."""
        return self.name

    @property
    def description(self) -> str:
        """One-line description of this severity."""
        descriptions = {
            SeverityLevel.CRITICAL: "System-breaking or security-critical - blocks commit",
            SeverityLevel.HIGH: "Bugs or architectural violations - should fix before commit",
            SeverityLevel.MEDIUM: "Code quality issues - consider fixing",
            SeverityLevel.LOW: "Minor style issues - informational",
            SeverityLevel.INFO: "No issue - passed or skipped",
        }
        return descriptions[self]

    @property
    def ruff_category(self) -> str:
        """Map to Ruff's P0-P3 categories."""
        mapping = {
            SeverityLevel.CRITICAL: "P0",
            SeverityLevel.HIGH: "P1",
            SeverityLevel.MEDIUM: "P2",
            SeverityLevel.LOW: "P3",
            SeverityLevel.INFO: "N/A",
        }
        return mapping[self]

    @property
    def adg_category(self) -> str:
        """Map to ADG's P1-P4 categories."""
        mapping = {
            SeverityLevel.CRITICAL: "P1",
            SeverityLevel.HIGH: "P2",
            SeverityLevel.MEDIUM: "P3",
            SeverityLevel.LOW: "P4",
            SeverityLevel.INFO: "N/A",
        }
        return mapping[self]


# Backward compatibility aliases for existing code
FindingSeverity = SeverityLevel  # ADG query contracts
ValidationSeverity = SeverityLevel  # Validation config
PreCommitSeverity = SeverityLevel  # Pre-commit schema


def from_ruff_category(category: str) -> SeverityLevel:
    """
    Convert Ruff P0-P3 category to SeverityLevel.

    Args:
        category: Ruff category (P0, P1, P2, P3)

    Returns:
        Corresponding SeverityLevel
    """
    mapping = {
        "P0": SeverityLevel.CRITICAL,
        "P1": SeverityLevel.HIGH,
        "P2": SeverityLevel.MEDIUM,
        "P3": SeverityLevel.LOW,
    }
    return mapping.get(category.upper(), SeverityLevel.INFO)


def from_adg_category(category: str) -> SeverityLevel:
    """
    Convert ADG P1-P4 category to SeverityLevel.

    Args:
        category: ADG category (P1, P2, P3, P4)

    Returns:
        Corresponding SeverityLevel
    """
    mapping = {
        "P1": SeverityLevel.CRITICAL,
        "P2": SeverityLevel.HIGH,
        "P3": SeverityLevel.MEDIUM,
        "P4": SeverityLevel.LOW,
    }
    return mapping.get(category.upper(), SeverityLevel.INFO)


def from_legacy_string(value: str) -> SeverityLevel:
    """
    Convert legacy severity strings to canonical SeverityLevel.

    Handles case variations and alternate names for backward compatibility.

    Args:
        value: Legacy severity string (case-insensitive)

    Returns:
        Canonical SeverityLevel

    Examples:
        >>> from_legacy_string("CRITICAL")
        SeverityLevel.CRITICAL
        >>> from_legacy_string("critical")
        SeverityLevel.CRITICAL
        >>> from_legacy_string("WARNING")  # Legacy ValidationSeverity.WARNING
        SeverityLevel.MEDIUM
    """
    value = value.lower().strip()

    # Direct matches
    if value in ("critical", "p1", "p0"):
        return SeverityLevel.CRITICAL
    if value in ("high", "p2"):
        return SeverityLevel.HIGH
    if value in ("medium", "p3"):
        return SeverityLevel.MEDIUM
    if value in ("low", "p4"):
        return SeverityLevel.LOW
    if value in ("info", "passed", "skipped"):
        return SeverityLevel.INFO

    # Legacy mappings
    if value in ("warning",):  # Legacy ValidationSeverity.WARNING
        return SeverityLevel.MEDIUM
    if value in ("error",):  # Legacy ValidationSeverity.ERROR
        return SeverityLevel.HIGH

    # Default to INFO for unknown values
    return SeverityLevel.INFO


__all__ = [
    "SeverityLevel",
    "FindingSeverity",  # Backward compatibility
    "ValidationSeverity",  # Backward compatibility
    "PreCommitSeverity",  # Backward compatibility
    "from_ruff_category",
    "from_adg_category",
    "from_legacy_string",
]
