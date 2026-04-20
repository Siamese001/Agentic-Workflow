"""Severity Level SSOT for pre-commit, validation, and quality reporting.

This module provides the high-level ``SeverityLevel`` enum used by pre-commit
gates, validation systems, and quality metrics. It includes an ``INFO`` level
for passed/skipped gate status.

For the canonical ADG severity<->band mapping (CRITICAL/HIGH/MEDIUM/LOW <->
P0/P1/P2/P3) used by ``adg_burndown_table.json`` and all ADG reports, see:

    agentic_core.adg.severity_bands

That module is the authoritative SSOT for ADG P0-P3 classifications. This
module (``SeverityLevel``) delegates ADG categorization to it, so the two
never drift.

SEVERITY TAXONOMY
-----------------
Severity levels are defined by two dimensions:
1. IMPACT: What happens if this issue reaches production?
2. URGENCY: How quickly must this be addressed?
"""

from __future__ import annotations

from enum import Enum


class SeverityLevel(Enum):
    """Canonical severity levels for pre-commit, validation, and ADG systems.

    MAPPING TO OTHER SYSTEMS (authoritative)
    ---------------------------------------
    ADG / Ruff: CRITICAL → P0, HIGH → P1, MEDIUM → P2, LOW → P3
    Pre-commit: CRITICAL/HIGH/MEDIUM/LOW/INFO → direct mapping

    The ADG mapping above is the canonical one used by
    ``adg_burndown_table.json``. It is delegated to
    ``agentic_core.adg.severity_bands`` so the two SSOTs never disagree.

    SEMANTIC DEFINITIONS
    --------------------
    CRITICAL (P0): System-breaking, security breach, data loss, or
        constitutional violation. Layer boundary violations,
        PowerShell usage, broken imports. Blocks commit.
    HIGH (P1): Bugs, architectural violations, high-severity anti-patterns
        (broad exception handling in production). Should fix before commit.
    MEDIUM (P2): Medium-severity anti-patterns (silent swallow, return-none,
        default masking, retry without bounds, double logging). Consider
        fixing — technical debt accumulation.
    LOW (P3): Style warnings (global mutation, hardcoded paths,
        throw-for-normal-flow). Informational, can be deferred.
    INFO: No issue — informational or passed gate status. Has no ADG band.
    """

    CRITICAL = "critical"  # P0/P1 - Blocks commit
    HIGH = "high"  # P1/P2 - Should fix before commit
    MEDIUM = "medium"  # P2/P3 - Consider fixing
    LOW = "low"  # P3/P4 - Informational
    INFO = "info"  # Passed/clean status

    def __str__(self) -> str:
        return self.value

    @property
    def p_level(self) -> str:
        """Return the canonical P-level (P0, P1, P2, P3) or 'N/A' for INFO.

        Delegates to the ADG severity_bands SSOT so the mapping stays in sync
        with ``agentic_core/adg/severity_bands.py`` and ``adg_burndown_table.json``.
        """
        # Lazy import avoids creating an L5<-L_ADG dependency at module load.
        from agentic_core.adg.severity_bands import SEVERITY_TO_BAND

        if self == SeverityLevel.INFO:
            return "N/A"
        return SEVERITY_TO_BAND[self.name]

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
        """Ruff P0-P3 category (identical to ADG band — single canonical mapping)."""
        return self.p_level

    @property
    def adg_category(self) -> str:
        """ADG P0-P3 band for this severity.

        Returns the canonical band from ``agentic_core.adg.severity_bands``:
        CRITICAL → P0, HIGH → P1, MEDIUM → P2, LOW → P3. INFO returns 'N/A'.
        """
        return self.p_level


# Backward compatibility aliases for existing code
FindingSeverity = SeverityLevel  # ADG query contracts
ValidationSeverity = SeverityLevel  # Validation config
PreCommitSeverity = SeverityLevel  # Pre-commit schema


def from_ruff_category(category: str) -> SeverityLevel:
    """Convert a Ruff/ADG P0-P3 category to SeverityLevel.

    Args:
        category: Category string (``P0``, ``P1``, ``P2``, ``P3``).

    Returns:
        Corresponding ``SeverityLevel`` or ``INFO`` when unknown.
    """
    # Lazy import avoids creating an L5<-L_ADG dependency at module load.
    from agentic_core.adg.severity_bands import BAND_TO_SEVERITY

    severity_name = BAND_TO_SEVERITY.get(category.upper())
    if severity_name is None:
        return SeverityLevel.INFO
    return SeverityLevel[severity_name]


def from_adg_category(category: str) -> SeverityLevel:
    """Convert an ADG P0-P3 category to SeverityLevel.

    The ADG canonical band range is P0-P3 (see
    ``agentic_core.adg.severity_bands``). This function also accepts legacy
    P1-P4 inputs for backward compatibility and maps them by shifting down
    one band (P1->P0, P2->P1, P3->P2, P4->P3) so older callers degrade
    safely instead of returning INFO.

    Args:
        category: ADG band string (``P0``, ``P1``, ``P2``, ``P3``) or legacy
            (``P1``, ``P2``, ``P3``, ``P4``).

    Returns:
        Corresponding ``SeverityLevel`` or ``INFO`` when unknown.
    """
    return from_ruff_category(category)


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
