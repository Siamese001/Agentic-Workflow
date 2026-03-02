"""
Shared constants for Location Validation and Healing.

Extracted from LocationAgent.py during SRP fission.
All location-related agents should import from this module.
"""

# Archive subfolder mapping for violation types
ARCHIVE_SUBFOLDERS: dict[str, str] = {
    "VOID VIOLATION": "void_violations",
    "GRAVITY": "void_violations",
    "LAYER PREFIX VIOLATION": "naming_violations",
}

# Default archive subfolder for unclassified violations
DEFAULT_ARCHIVE_SUBFOLDER: str = "location_violations"

# Healing strategy mapping (violation type → method name)
# CRITICAL: VOID VIOLATION must be handled BEFORE falling back to archiving
# The correct flow is: relocate → propose new subfolder → update SSOT → archive (last resort)
HEALING_STRATEGY_MAP: dict[str, str] = {
    "BROKEN BACKUP": "_heal_broken_backup",
    "APP-SPECIFIC IN CORE": "_heal_app_specific_violation",
    "TERRITORY MISMATCH": "_heal_territory_mismatch",
    "DEEP VIOLATION": "_heal_depth_violation",
    "SHALLOW VIOLATION": "_heal_depth_violation",
    "PASCAL_IN_NON_AGENT_FOLDER": "_heal_app_specific_violation",
    "VOID VIOLATION": "_heal_void_violation",  # NEW: Handle void violations properly
}

# Default app healing target subfolder
DEFAULT_APP_HEALING_TARGET: str = "reasoning"

# Violation severity thresholds
VIOLATION_THRESHOLDS: dict[str, int] = {
    "critical": 10,
    "high": 25,
    "medium": 50,
}

# Default report path
DEFAULT_REPORT_PATH: str = "reports/location_audit.json"
