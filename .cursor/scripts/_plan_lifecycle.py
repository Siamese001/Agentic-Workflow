"""
_plan_lifecycle.py
Pure extraction: Plan state transitions and lifecycle constants.

This module centralizes plan lifecycle management extracted from
.cursor/plans/ execution patterns and wave state management.

W1 SCOPE: Pure extraction only. No new states. No policy changes.
"""

from typing import Set, Dict, List, Optional, Tuple
from enum import Enum


# ============================================================================
# PLAN STATUSES (from notion-plans-taxonomy.md)
# ============================================================================

class PlanStatus:
    """Canonical plan statuses. Pure extraction — no new statuses."""
    
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    WAITING = "Waiting"
    DEFERRED = "Deferred"
    COMPLETED = "Completed"
    RETIRED = "Retired"
    ARCHIVED = "Archived"
    
    ALL = {
        NOT_STARTED,
        IN_PROGRESS,
        WAITING,
        DEFERRED,
        COMPLETED,
        RETIRED,
        ARCHIVED,
    }
    
    # Active statuses (plan is "live" in some form)
    ACTIVE = {NOT_STARTED, IN_PROGRESS, WAITING, DEFERRED}
    
    # Terminal statuses (no further work expected)
    TERMINAL = {COMPLETED, RETIRED, ARCHIVED}
    
    # Blocked/waiting statuses
    BLOCKED = {WAITING, DEFERRED}


# ============================================================================
# WAVE STATUSES (extracted from wave execution patterns)
# ============================================================================

class WaveStatus:
    """Wave execution statuses. Pure extraction."""
    
    TODO = "🔲 TODO"
    IN_PROGRESS = "🟡 IN_PROGRESS"
    DONE = "✅ DONE"
    FAILED = "❌ FAILED"
    BLOCKED = "⛔ BLOCKED"
    
    ALL = {TODO, IN_PROGRESS, DONE, FAILED, BLOCKED}


# ============================================================================
# PHASE STATUSES (extracted from phase execution patterns)
# ============================================================================

class PhaseStatus:
    """Phase execution statuses. Pure extraction."""
    
    TODO = "🔲 TODO"
    IN_PROGRESS = "🟡 IN_PROGRESS"
    DONE = "✅ DONE"
    FAILED = "❌ FAILED"
    
    ALL = {TODO, IN_PROGRESS, DONE, FAILED}


# ============================================================================
# LIFECYCLE TRANSITIONS (valid state changes)
# ============================================================================

VALID_PLAN_TRANSITIONS: Dict[str, Set[str]] = {
    # From -> To set
    PlanStatus.NOT_STARTED: {
        PlanStatus.IN_PROGRESS,
        PlanStatus.DEFERRED,
        PlanStatus.RETIRED,
    },
    PlanStatus.IN_PROGRESS: {
        PlanStatus.WAITING,
        PlanStatus.DEFERRED,
        PlanStatus.COMPLETED,
        PlanStatus.RETIRED,
    },
    PlanStatus.WAITING: {
        PlanStatus.IN_PROGRESS,
        PlanStatus.DEFERRED,
        PlanStatus.RETIRED,
    },
    PlanStatus.DEFERRED: {
        PlanStatus.IN_PROGRESS,
        PlanStatus.NOT_STARTED,  # Undefer
        PlanStatus.RETIRED,
    },
    PlanStatus.COMPLETED: {
        PlanStatus.ARCHIVED,
        # No going back from completed
    },
    PlanStatus.RETIRED: {
        PlanStatus.ARCHIVED,
        # No going back from retired
    },
    PlanStatus.ARCHIVED: set(),  # Terminal
}


# ============================================================================
# PURE FUNCTIONS
# ============================================================================

def is_valid_transition(from_status: str, to_status: str) -> bool:
    """
    Check if plan status transition is valid.
    
    Pure extraction of state machine from existing plan management.
    """
    if from_status not in VALID_PLAN_TRANSITIONS:
        return False
    
    if to_status == from_status:
        return True  # No change is always valid
    
    return to_status in VALID_PLAN_TRANSITIONS[from_status]


def get_valid_transitions(status: str) -> Set[str]:
    """Get set of valid target statuses from current status."""
    return VALID_PLAN_TRANSITIONS.get(status, set()).copy()


def is_active_status(status: str) -> bool:
    """Check if status indicates an active plan."""
    return status in PlanStatus.ACTIVE


def is_terminal_status(status: str) -> bool:
    """Check if status is terminal (no more work)."""
    return status in PlanStatus.TERMINAL


def is_blocked_status(status: str) -> bool:
    """Check if status indicates plan is blocked/waiting."""
    return status in PlanStatus.BLOCKED


def validate_status(status: str) -> Tuple[bool, Optional[str]]:
    """
    Validate status string.
    
    Returns (is_valid, error_message).
    """
    if status in PlanStatus.ALL:
        return True, None
    
    # Check for common stale values
    stale_map = {
        "Draft": PlanStatus.NOT_STARTED,
        "Live": PlanStatus.IN_PROGRESS,
        "Deprioritized": PlanStatus.DEFERRED,
    }
    
    if status in stale_map:
        canonical = stale_map[status]
        return False, f"Stale status '{status}': use '{canonical}'"
    
    return False, f"Unknown status: '{status}'. Valid: {', '.join(sorted(PlanStatus.ALL))}"


# ============================================================================
# WAVE/PHASE HELPERS
# ============================================================================

def wave_can_start(current_status: str) -> bool:
    """Check if a wave can start from current status."""
    return current_status in {WaveStatus.TODO, WaveStatus.BLOCKED}


def phase_can_start(current_status: str) -> bool:
    """Check if a phase can start from current status."""
    return current_status in {PhaseStatus.TODO}


def is_wave_complete(status: str) -> bool:
    """Check if wave status indicates completion."""
    return status == WaveStatus.DONE


def is_phase_complete(status: str) -> bool:
    """Check if phase status indicates completion."""
    return status == PhaseStatus.DONE


# ============================================================================
# PLAN FILE PATH CONVENTIONS
# ============================================================================

PLAN_FILE_PATTERN: str = r"^[a-z0-9-]+-[a-f0-9]{6}\.md$"
PLAN_DIR: str = ".cursor/plans"
PLAN_TEMPLATE: str = ".cursor/templates/execution-plan-template.md"


def is_valid_plan_slug(slug: str) -> bool:
    """
    Validate plan slug format.
    
    Format: <descriptive-name>-<6hex>
    Example: cursor-governance-consolidation-a7c3e9
    """
    import re
    return bool(re.match(PLAN_FILE_PATTERN.replace("\\.md$", ""), slug))


def build_plan_filename(slug: str) -> str:
    """Build plan filename from slug."""
    if not slug.endswith(".md"):
        return f"{slug}.md"
    return slug


def parse_plan_slug(filename: str) -> Optional[str]:
    """Extract slug from plan filename."""
    if filename.endswith(".md"):
        return filename[:-3]
    return filename


# ============================================================================
# MARKER CONSTANTS (from constitutional enforcement)
# ============================================================================

class Markers:
    """Plan/wave/phase markers. Pure extraction."""
    
    WAVE_START = "WAVE_START:"
    WAVE_COMPLETE = "WAVE_COMPLETE:"
    PHASE_COMPLETE = "PHASE_COMPLETE:"
    PLAN_COMPLETE = "PLAN_COMPLETE:"
    PLAN_CREATED = "PLAN_CREATED:"
    SCOPE_EXPANSION = "SCOPE_EXPANSION:"
    DISCOVERED_SCOPE = "DISCOVERED_SCOPE:"
    AUTHORIZATION_DECISION = "AUTHORIZATION_DECISION:"
    DEFERRED_SCOPE = "DEFERRED_SCOPE:"
    NEXT_STEP = "NEXT_STEP:"
    SCOPE_RESET = "SCOPE_RESET:"


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    # Test status validation
    tests = [
        ("In Progress", True, None),
        ("Not Started", True, None),
        ("Completed", True, None),
        ("Draft", False, "Not Started"),
        ("Invalid", False, None),
    ]
    
    all_pass = True
    for status, expected_valid, expected_canonical in tests:
        is_valid, error = validate_status(status)
        if is_valid != expected_valid:
            print(f"FAIL: '{status}' valid={is_valid}, expected={expected_valid}")
            all_pass = False
        elif not is_valid and expected_canonical and expected_canonical not in (error or ""):
            print(f"FAIL: '{status}' error missing canonical: {error}")
            all_pass = False
    
    # Test transitions
    if not is_valid_transition("Not Started", "In Progress"):
        print("FAIL: Not Started -> In Progress should be valid")
        all_pass = False
    
    if is_valid_transition("Completed", "In Progress"):
        print("FAIL: Completed -> In Progress should be invalid")
        all_pass = False
    
    # Test slug validation
    if not is_valid_plan_slug("test-plan-a1b2c3"):
        print("FAIL: 'test-plan-a1b2c3' should be valid")
        all_pass = False
    
    if is_valid_plan_slug("invalid_slug"):
        print("FAIL: 'invalid_slug' should be invalid (no hex)")
        all_pass = False
    
    if all_pass:
        print("_plan_lifecycle: All self-tests passed")
    else:
        print("_plan_lifecycle: Self-tests FAILED")
        exit(1)
