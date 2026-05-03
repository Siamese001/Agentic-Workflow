"""Unit tests for _notion_plans_status_check helper."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS = _REPO_ROOT / ".windsurf" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _notion_plans_status_check import (  # type: ignore  # noqa: E402
    CANONICAL_STATUSES,
    PLANS_DATA_SOURCE_ID,
    PLANS_DB_ID,
    STALE_EQUIVALENTS,
    Violation,
    check,
    decide,
)


# ---------------------------------------------------------------------------
# Canonical pass cases.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", sorted(CANONICAL_STATUSES))
def test_canonical_values_pass(value: str) -> None:
    assert decide(PLANS_DB_ID, "Status", value) is None


def test_canonical_via_data_source_id() -> None:
    assert decide(PLANS_DATA_SOURCE_ID, "Status", "Draft") is None


def test_canonical_lowercase_and_undashed_ids_still_match_plans() -> None:
    # Tolerant matching: dashed vs un-dashed, upper vs lower.
    assert decide(PLANS_DB_ID.upper(), "Status", "Live") is None
    assert decide(PLANS_DB_ID.replace("-", ""), "Status", "Live") is None


# ---------------------------------------------------------------------------
# Stale-emoji blocks with canonical suggestion.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("stale,canonical", list(STALE_EQUIVALENTS.items()))
def test_stale_emoji_blocked_with_suggestion(stale: str, canonical: str) -> None:
    v = decide(PLANS_DB_ID, "Status", stale)
    assert isinstance(v, Violation)
    assert v.suggested == canonical
    assert canonical in v.message


def test_unknown_string_blocked_no_suggestion() -> None:
    v = decide(PLANS_DB_ID, "Status", "InProgress")
    assert isinstance(v, Violation)
    assert v.suggested == ""
    assert "Unknown" in v.message or "InProgress" in v.message


def test_empty_string_blocked() -> None:
    # Empty Status is not canonical; treat as unknown.
    v = decide(PLANS_DB_ID, "Status", "")
    assert isinstance(v, Violation)


# ---------------------------------------------------------------------------
# Narrow-scope: non-Plans DB + non-Status property must pass.
# ---------------------------------------------------------------------------

def test_non_plans_db_ignored() -> None:
    other_db = "aa8d2507-101e-4384-81d9-60ea3fe33876"  # Backlog Items
    assert decide(other_db, "Status", "🟡Draft") is None


def test_non_status_property_on_plans_ignored() -> None:
    # Writing Priority or any other field on Plans must NOT be flagged.
    assert decide(PLANS_DB_ID, "Priority", "🟡Draft") is None


def test_empty_db_id_ignored() -> None:
    assert decide("", "Status", "🟡Draft") is None
    assert decide(None, "Status", "🟡Draft") is None


def test_none_value_blocked() -> None:
    # None value is not canonical -- coerced to "" -> Violation.
    v = decide(PLANS_DB_ID, "Status", None)
    assert isinstance(v, Violation)


# ---------------------------------------------------------------------------
# Tuple alias.
# ---------------------------------------------------------------------------

def test_check_tuple_alias_pass() -> None:
    assert check(PLANS_DB_ID, "Status", "Draft") == (False, None, None)


def test_check_tuple_alias_stale() -> None:
    blocked, msg, suggested = check(PLANS_DB_ID, "Status", "🟡Draft")
    assert blocked is True
    assert suggested == "Draft"
    assert msg is not None and "Draft" in msg


def test_case_sensitive_canonical() -> None:
    # "draft" (lowercase) is NOT canonical -- Notion option names are
    # case-sensitive.
    v = decide(PLANS_DB_ID, "Status", "draft")
    assert isinstance(v, Violation)


def test_message_lists_canonical_set() -> None:
    v = decide(PLANS_DB_ID, "Status", "Bogus")
    assert v is not None
    for canonical in CANONICAL_STATUSES:
        assert canonical in v.message
