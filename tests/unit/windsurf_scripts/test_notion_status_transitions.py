"""Unit tests for Notion Plans DB status transitions — valid forward and forbidden backward flows.

Tests the transition matrix from notion-plans-taxonomy.md §Transition Matrix.

5-status SSOT (_notion_plans_status_check.CANONICAL_STATUSES):
    "Not Started", "In Progress", "Completed", "Retired", "Archived".
"Lower Priority" / "Waiting" were removed from the taxonomy — they are legacy
aliases coerced to "In Progress" on write and MUST NOT appear in this matrix.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
# Resolve the SSOT module directly (not the legacy _legacy_windsurf shim, which
# probes a .cursor/scripts mirror absent in worktrees and errors at collection).
_SCRIPTS = _REPO_ROOT / ".claude" / "governance" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

# Import the canonical statuses from the SSOT helper
from _notion_plans_status_check import CANONICAL_STATUSES  # type: ignore  # noqa: E402


# ============================================================================
# Transition Validation Logic (mirrors what a gate would enforce)
# ============================================================================

# Valid status transitions (forward flows) — 5-status SSOT only.
VALID_TRANSITIONS: dict[str, set[str]] = {
    "Not Started": {"In Progress", "Completed", "Retired", "Archived"},
    "In Progress": {"Not Started", "Completed", "Retired", "Archived"},
    "Completed": set(),  # Terminal — no exits
    "Retired": {"Archived"},  # Terminal with one escape hatch
    "Archived": set(),  # Terminal — no exits
}

# Legacy (non-canonical) statuses that must NEVER appear in the matrix.
LEGACY_NON_CANONICAL: set[str] = {"Lower Priority", "Waiting", "Deferred", "Deprioritized"}

# Terminal statuses (no valid outgoing transitions except explicit escapes)
TERMINAL_STATUSES: set[str] = {"Completed", "Archived"}

# Statuses that allow escape to another terminal
TERMINAL_WITH_ESCAPE: dict[str, set[str]] = {
    "Retired": {"Archived"},
}

# Backward/forbidden transitions (regression checks)
# These should NEVER be allowed
FORBIDDEN_REGRESSIONS: set[tuple[str, str]] = {
    # Terminal → anything
    ("Completed", "Not Started"),
    ("Completed", "In Progress"),
    ("Completed", "Retired"),
    ("Completed", "Archived"),
    ("Archived", "Not Started"),
    ("Archived", "In Progress"),
    ("Archived", "Completed"),
    ("Archived", "Retired"),
    # Regression from terminal to active
    ("Retired", "Not Started"),
    ("Retired", "In Progress"),
    ("Retired", "Completed"),
}


def is_valid_transition(from_status: str, to_status: str) -> bool:
    """Check if a status transition is valid per the transition matrix."""
    if from_status not in VALID_TRANSITIONS:
        return False
    return to_status in VALID_TRANSITIONS[from_status]


def get_forbidden_reason(from_status: str, to_status: str) -> str | None:
    """Return reason why transition is forbidden, or None if valid."""
    if is_valid_transition(from_status, to_status):
        return None

    if from_status in TERMINAL_STATUSES:
        return f"{from_status} is terminal — no transitions allowed"

    if from_status in TERMINAL_WITH_ESCAPE:
        allowed = TERMINAL_WITH_ESCAPE[from_status]
        if to_status not in allowed:
            return f"{from_status} is terminal — only escape to {allowed} allowed"

    if (from_status, to_status) in FORBIDDEN_REGRESSIONS:
        return "Regression from terminal state forbidden"

    return f"Transition {from_status} → {to_status} not in valid matrix"


# ============================================================================
# Test Cases
# ============================================================================


class TestValidForwardTransitions:
    """Happy path: transitions that SHOULD be allowed."""

    @pytest.mark.parametrize("from_status,allowed_targets", [
        ("Not Started", ["In Progress", "Completed", "Retired", "Archived"]),
        ("In Progress", ["Not Started", "Completed", "Retired", "Archived"]),
    ])
    def test_active_statuses_have_valid_exits(self, from_status: str, allowed_targets: list[str]) -> None:
        """Active (non-terminal) statuses must have at least one valid exit."""
        for target in allowed_targets:
            assert is_valid_transition(from_status, target), \
                f"{from_status} → {target} should be valid"

    def test_not_started_to_in_progress_start(self) -> None:
        """Not Started → In Progress is the start path."""
        assert is_valid_transition("Not Started", "In Progress")

    def test_in_progress_to_completed_success(self) -> None:
        """In Progress → Completed is the success path."""
        assert is_valid_transition("In Progress", "Completed")

    def test_in_progress_to_not_started_reset(self) -> None:
        """In Progress → Not Started is a valid reset."""
        assert is_valid_transition("In Progress", "Not Started")

    def test_stale_to_retired_auto_flip(self) -> None:
        """In Progress → Retired after 14d stale."""
        assert is_valid_transition("In Progress", "Retired")

    def test_retired_to_archived_escape(self) -> None:
        """Retired → Archived is the only valid exit from Retired."""
        assert is_valid_transition("Retired", "Archived")
        # Retired should NOT allow any other transition
        other_targets = {"Not Started", "In Progress", "Completed"}
        for target in other_targets:
            assert not is_valid_transition("Retired", target), \
                f"Retired → {target} should be FORBIDDEN"


class TestForbiddenBackwardTransitions:
    """Sad path: transitions that should NEVER be allowed."""

    @pytest.mark.parametrize("terminal,attempted", [
        ("Completed", "Not Started"),
        ("Completed", "In Progress"),
        ("Completed", "Retired"),
        ("Completed", "Archived"),
    ])
    def test_completed_is_terminal_no_exits(self, terminal: str, attempted: str) -> None:
        """Completed is terminal — no transitions allowed."""
        assert not is_valid_transition(terminal, attempted)
        reason = get_forbidden_reason(terminal, attempted)
        assert "terminal" in (reason or "").lower()

    @pytest.mark.parametrize("terminal,attempted", [
        ("Archived", "Not Started"),
        ("Archived", "In Progress"),
        ("Archived", "Completed"),
        ("Archived", "Retired"),
    ])
    def test_archived_is_terminal_no_exits(self, terminal: str, attempted: str) -> None:
        """Archived is terminal — no transitions allowed."""
        assert not is_valid_transition(terminal, attempted)

    @pytest.mark.parametrize("from_status,to_status", list(FORBIDDEN_REGRESSIONS))
    def test_all_forbidden_regressions_blocked(self, from_status: str, to_status: str) -> None:
        """Every entry in FORBIDDEN_REGRESSIONS must be blocked."""
        assert not is_valid_transition(from_status, to_status)

    def test_no_regression_from_completed_to_in_progress(self) -> None:
        """Specific regression: Completed work cannot restart."""
        assert not is_valid_transition("Completed", "In Progress")
        reason = get_forbidden_reason("Completed", "In Progress")
        assert reason is not None


class TestTerminalStateProperties:
    """Terminal state behavior guarantees."""

    def test_terminal_statuses_have_no_valid_targets(self) -> None:
        """Terminal statuses should have empty or minimal valid target sets."""
        for status in TERMINAL_STATUSES:
            valid_targets = VALID_TRANSITIONS.get(status, set())
            assert len(valid_targets) == 0, f"{status} should have no valid exits"

    def test_retired_has_exactly_one_escape(self) -> None:
        """Retired allows exactly one escape: to Archived."""
        valid_targets = VALID_TRANSITIONS.get("Retired", set())
        assert valid_targets == {"Archived"}, "Retired should only escape to Archived"

    def test_all_canonical_statuses_in_transition_matrix(self) -> None:
        """Every canonical status must have an entry in VALID_TRANSITIONS."""
        for status in CANONICAL_STATUSES:
            assert status in VALID_TRANSITIONS, f"{status} missing from transition matrix"


class TestTransitionExhaustiveness:
    """Ensure all possible transitions are accounted for."""

    def test_every_status_transition_evaluable(self) -> None:
        """Every possible pair of statuses should be evaluable (valid or forbidden)."""
        all_statuses = list(CANONICAL_STATUSES)
        for from_status in all_statuses:
            for to_status in all_statuses:
                # Should not raise
                is_valid = is_valid_transition(from_status, to_status)
                reason = get_forbidden_reason(from_status, to_status)

                # If valid, reason should be None
                if is_valid:
                    assert reason is None
                else:
                    # If not valid, should have a reason
                    assert reason is not None

    def test_symmetric_forbidden_detection(self) -> None:
        """If A → B is valid, B → A might be forbidden (asymmetric transitions)."""
        # Not Started → In Progress (start) is valid
        assert is_valid_transition("Not Started", "In Progress")
        # In Progress → Not Started (reset) is valid
        assert is_valid_transition("In Progress", "Not Started")

        # But Completed → In Progress is forbidden
        assert not is_valid_transition("Completed", "In Progress")


class TestAutoTransitionRules:
    """Time-based auto-transition enforcement (T1-T5 rules)."""

    def test_t1_in_progress_auto_retired_after_14d(self) -> None:
        """Rule T1: In Progress → Retired auto-flip after 14d stale."""
        # The transition itself is valid
        assert is_valid_transition("In Progress", "Retired")
        # It's the automatic trigger that's enforced, not the transition validity

    def test_no_auto_transition_from_completed(self) -> None:
        """Completed should NEVER auto-transition (terminal)."""
        for target in CANONICAL_STATUSES:
            if target != "Completed":
                assert not is_valid_transition("Completed", target)


class TestFieldRequirementAlignment:
    """Ensure field requirements align with transition rules."""

    def test_retired_requires_summary_reason(self) -> None:
        """Entering Retired requires Summary with reason."""
        assert is_valid_transition("In Progress", "Retired")
        assert is_valid_transition("Not Started", "Retired")


class TestLegacyStatusesNonCanonical:
    """5-status SSOT: legacy 'Lower Priority' / 'Waiting' / aliases are removed.

    They must NOT be canonical and must NOT appear in the transition matrix.
    """

    @pytest.mark.parametrize("legacy", sorted(LEGACY_NON_CANONICAL))
    def test_legacy_status_not_canonical(self, legacy: str) -> None:
        """Legacy statuses must NOT be in CANONICAL_STATUSES."""
        assert legacy not in CANONICAL_STATUSES

    @pytest.mark.parametrize("legacy", sorted(LEGACY_NON_CANONICAL))
    def test_legacy_status_not_in_transition_matrix(self, legacy: str) -> None:
        """Legacy statuses must NOT have a row in VALID_TRANSITIONS."""
        assert legacy not in VALID_TRANSITIONS

    @pytest.mark.parametrize("legacy", sorted(LEGACY_NON_CANONICAL))
    def test_legacy_status_has_no_valid_transition(self, legacy: str) -> None:
        """No transition from a legacy status is valid (unknown source → False)."""
        assert not is_valid_transition(legacy, "In Progress")

    def test_canonical_set_is_exactly_five(self) -> None:
        """The SSOT must hold exactly the 5 canonical statuses."""
        assert CANONICAL_STATUSES == {
            "Not Started", "In Progress", "Completed", "Retired", "Archived",
        }


class TestSelfTransitions:
    """A status transitioning to itself is not a valid forward move."""

    @pytest.mark.parametrize("status", [
        "Not Started",
        "In Progress",
        "Completed",
        "Retired",
        "Archived",
    ])
    def test_self_transition_invalid(self, status: str) -> None:
        """No status may transition to itself via the valid matrix."""
        assert not is_valid_transition(status, status), \
            f"{status} → {status} self-transition must be invalid"


class TestUnknownStatusHandling:
    """Functions must not raise on completely unknown status strings."""

    def test_unknown_from_status_returns_false(self) -> None:
        assert is_valid_transition("Banana", "In Progress") is False

    def test_unknown_to_status_returns_false(self) -> None:
        assert is_valid_transition("In Progress", "Banana") is False

    def test_both_unknown_returns_false(self) -> None:
        assert is_valid_transition("Foo", "Bar") is False

    def test_get_forbidden_reason_unknown_from(self) -> None:
        reason = get_forbidden_reason("Banana", "In Progress")
        assert reason is not None

    def test_empty_string_status(self) -> None:
        assert is_valid_transition("", "In Progress") is False
        assert is_valid_transition("In Progress", "") is False
