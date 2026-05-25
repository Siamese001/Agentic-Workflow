"""Regression tests for .cursor/scripts/_notion_canonical SSOT helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CURSOR_SCRIPTS = _REPO_ROOT / ".cursor" / "scripts"
if str(_CURSOR_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_CURSOR_SCRIPTS))

from _notion_canonical import (  # type: ignore  # noqa: E402
    CANONICAL_STATUSES,
    PLANS_DB_PROPERTIES,
    get_active_statuses,
    get_canonical_status,
    get_status_id,
    get_terminal_statuses,
    is_canonical_status,
    validate_status_for_write,
)
from _notion_plans_status_check import (  # type: ignore  # noqa: E402
    FORBIDDEN_PLANS_STATUSES,
    STALE_EQUIVALENTS,
    decide,
    PLANS_DB_ID,
)


@pytest.mark.parametrize(
    "status",
    sorted(CANONICAL_STATUSES),
)
def test_canonical_statuses_accept_writes(status: str) -> None:
    valid, canonical = validate_status_for_write(status)
    assert valid is True
    assert canonical == status
    assert is_canonical_status(status)


@pytest.mark.parametrize("stale,expected", list(STALE_EQUIVALENTS.items()))
def test_stale_statuses_rejected_with_migration_hint(stale: str, expected: str) -> None:
    valid, msg = validate_status_for_write(stale)
    assert valid is False
    assert msg is not None
    assert expected in msg
    assert get_canonical_status(stale) == expected


def test_active_and_deprioritized_map_to_canonical() -> None:
    """2026-05-25 leak closeout: legacy labels must not pass write validation."""
    for stale, expected in (("Active", "In Progress"), ("Deprioritized", "Lower Priority")):
        assert get_canonical_status(stale) == expected
        valid, _ = validate_status_for_write(stale)
        assert valid is False


def test_forbidden_statuses_not_canonical_and_blocked_by_decide() -> None:
    """Forbidden labels overlap stale equivalents — must still fail write validation."""
    for forbidden in FORBIDDEN_PLANS_STATUSES:
        assert forbidden not in CANONICAL_STATUSES
        valid, _ = validate_status_for_write(forbidden)
        assert valid is False
        assert decide(PLANS_DB_ID, "Status", forbidden) is not None


def test_validate_unknown_status_fails_closed() -> None:
    valid, msg = validate_status_for_write("InProgress")
    assert valid is False
    assert msg is not None
    assert "Invalid status" in msg


def test_status_ids_only_for_canonical() -> None:
    assert get_status_id("In Progress") is not None
    assert get_status_id("Bogus") is None
    assert get_status_id("Draft") == get_status_id("Not Started")


def test_active_and_terminal_partitions_disjoint() -> None:
    active = get_active_statuses()
    terminal = get_terminal_statuses()
    assert active & terminal == set()
    assert active | terminal <= CANONICAL_STATUSES


def test_ai_summary_property_trailing_space_ssot() -> None:
    assert PLANS_DB_PROPERTIES["ai_summary"] == "AI Summary "


def test_canonical_set_matches_plans_status_check_ssot() -> None:
    from _notion_plans_status_check import CANONICAL_STATUSES as check_ssot

    assert CANONICAL_STATUSES == set(check_ssot)
