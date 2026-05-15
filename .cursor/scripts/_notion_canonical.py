"""
_notion_canonical.py
Pure extraction: Notion Plans DB canonical values and status handling.

This module centralizes the canonical status values, property IDs, and
validation logic for Notion Plans DB integration. Extracted from existing
code in .cursor/scripts/_notion_plans_status_check.py and related files.

W1 SCOPE: Pure extraction only. No new statuses. No policy changes.
"""

from typing import Set, Dict, List, Optional


# ============================================================================
# CANONICAL STATUS VALUES (from notion-plans-taxonomy.md)
# ============================================================================

CANONICAL_STATUSES: Set[str] = {
    "In Progress",
    "Not Started",
    "Deferred",  # Renamed from "Deprioritized" 2026-05-10
    "Waiting",
    "Completed",
    "Retired",
    "Archived",
}

# Status option IDs (from API introspection)
STATUS_IDS: Dict[str, str] = {
    "In Progress": "521256be-2c96-4522-809e-f3dcb6843af9",
    "Not Started": "503df59f-85d4-4ac0-baae-e457d0354b6f",
    "Deferred": "~nZH",  # ID preserved across rename
    "Waiting": "dOTb",
    "Completed": "3a59faae-e327-4258-a4d3-82c835ff830d",
    "Retired": "3f684881-e5f5-4104-9c28-54e836e71305",
    "Archived": "a33b8816-b222-4db7-922e-f09c260058bf",
}

# STALE statuses that should not be used (auto-mapped)
STALE_EQUIVALENTS: Dict[str, str] = {
    "Draft": "Not Started",  # 🟡Draft -> Not Started
    "🟡Draft": "Not Started",
    "Live": "In Progress",  # 🟢Live -> In Progress
    "🟢Live": "In Progress",
    "Deprioritized": "Deferred",  # Legacy -> new name
}

# Color mapping for display (not for API writes)
STATUS_COLORS: Dict[str, str] = {
    "In Progress": "green",
    "Not Started": "gray",
    "Deferred": "yellow",
    "Waiting": "orange",
    "Completed": "blue",
    "Retired": "purple",
    "Archived": "gray",
}


# ============================================================================
# PLANS DB PROPERTY IDs
# ============================================================================

PLANS_DB_PROPERTIES: Dict[str, str] = {
    # Title property (important: NOT "Name", it's "Slug")
    "slug": "title",
    "slug_id": "title",
    
    # Status select
    "status": "Status",
    "status_id": "Status",
    
    # AI Summary with trailing space
    "ai_summary": "AI Summary ",  # NOTE: trailing space is intentional
    "ai_summary_id": "lNTq",
    
    # Other properties
    "exists_on_disk": "Exists On Disk",
    "plan_file_path": "Plan File Path",
    "summary": "Summary",
}


# ============================================================================
# DATABASE IDs
# ============================================================================

# Plans DB (reads and writes)
PLANS_DB_DATA_SOURCE_ID: str = "ac53d31b-3068-4039-9ebe-856c12caab32"
PLANS_DB_DATABASE_ID: str = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"

# Backlog Items DB (reads)
BACKLOG_DB_DATA_SOURCE_ID: str = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"


# ============================================================================
# PURE FUNCTIONS (extraction only)
# ============================================================================

def is_canonical_status(status: str) -> bool:
    """
    Check if status is canonical (exact match, case-sensitive).
    
    Pure extraction from _notion_plans_status_check.py.
    """
    return status in CANONICAL_STATUSES


def get_canonical_status(status: str) -> Optional[str]:
    """
    Get canonical status, mapping stale equivalents if needed.
    
    Returns None if status is not recognized.
    Pure extraction from existing migration logic.
    """
    # Already canonical
    if status in CANONICAL_STATUSES:
        return status
    
    # Check stale equivalents
    if status in STALE_EQUIVALENTS:
        return STALE_EQUIVALENTS[status]
    
    # Not recognized
    return None


def validate_status_for_write(status: str) -> tuple[bool, Optional[str]]:
    """
    Validate status for API write.
    
    Returns (is_valid, canonical_status_or_error).
    Pure extraction — enforces canonical values without
    introducing new statuses.
    """
    canonical = get_canonical_status(status)
    
    if canonical is None:
        return False, f"Invalid status: '{status}'. Use canonical values only."
    
    if status != canonical:
        # Stale status — caller should migrate
        return False, f"Stale status: '{status}' -> use '{canonical}'"
    
    return True, canonical


def get_status_id(status: str) -> Optional[str]:
    """
    Get status option ID for API calls.
    
    Pure extraction — returns ID only for canonical statuses.
    """
    canonical = get_canonical_status(status)
    if canonical:
        return STATUS_IDS.get(canonical)
    return None


def get_active_statuses() -> Set[str]:
    """
    Get statuses indicating active/living plans.
    
    Pure extraction of semantics from notion-plans-taxonomy.md:
    - Live = In Progress (green)
    - Draft = Not Started (gray) — NOT "Draft" stale option
    """
    return {"In Progress", "Not Started", "Waiting", "Deferred"}


def get_terminal_statuses() -> Set[str]:
    """
    Get terminal/final statuses.
    
    Pure extraction: Completed, Retired, Archived.
    """
    return {"Completed", "Retired", "Archived"}


# ============================================================================
# WAIVER/BYPASS CONSTANTS
# ============================================================================

NOTION_PLANS_STATUS_BYPASS: str = "NOTION_PLANS_STATUS_BYPASS"
NOTION_PLANS_STATUS_FAIL_CLOSED: str = "NOTION_PLANS_STATUS_FAIL_CLOSED"


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    # Test canonical status validation
    tests = [
        ("In Progress", True, "In Progress"),
        ("Not Started", True, "Not Started"),
        ("Draft", False, "Not Started"),  # Stale, should migrate
        ("🟡Draft", False, "Not Started"),  # Stale emoji form
        ("Invalid", False, None),  # Not recognized
    ]
    
    all_pass = True
    for input_status, expected_valid, expected_canonical in tests:
        is_valid, result = validate_status_for_write(input_status)
        
        if is_valid != expected_valid:
            print(f"FAIL: '{input_status}' valid={is_valid}, expected={expected_valid}")
            all_pass = False
        elif not is_valid and expected_canonical:
            # For invalid cases, check the error message suggests correct value
            if expected_canonical not in result:
                print(f"FAIL: '{input_status}' error missing '{expected_canonical}': {result}")
                all_pass = False
    
    # Test property name with trailing space
    if PLANS_DB_PROPERTIES["ai_summary"] != "AI Summary ":
        print(f"FAIL: AI Summary property missing trailing space")
        all_pass = False
    
    if all_pass:
        print("_notion_canonical: All self-tests passed")
    else:
        print("_notion_canonical: Self-tests FAILED")
        exit(1)
