"""Unit tests for _notion_plans_status_check helper."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
# Canonical path — _notion_plans_status_check.py lives in governance/scripts/, not _legacy_windsurf/
_SCRIPTS = _REPO_ROOT / ".claude" / "governance" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _notion_plans_status_check import (  # type: ignore  # noqa: E402
    BACKLOG_DATA_SOURCE_ID,
    BACKLOG_DB_ID,
    CANONICAL_STATUSES,
    PLANS_DATA_SOURCE_ID,
    PLANS_DB_ID,
    STALE_EQUIVALENTS,
    Violation,
    WaitingForViolation,
    check,
    decide,
    decide_waiting_for,
    decide_waiting_for_quality,
)


# ---------------------------------------------------------------------------
# Canonical pass cases.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", sorted(CANONICAL_STATUSES))
def test_canonical_values_pass(value: str) -> None:
    assert decide(PLANS_DB_ID, "Status", value) is None


def test_canonical_via_data_source_id() -> None:
    assert decide(PLANS_DATA_SOURCE_ID, "Status", "Not Started") is None


def test_canonical_lowercase_and_undashed_ids_still_match_plans() -> None:
    # Tolerant matching: dashed vs un-dashed, upper vs lower.
    assert decide(PLANS_DB_ID.upper(), "Status", "In Progress") is None
    assert decide(PLANS_DB_ID.replace("-", ""), "Status", "In Progress") is None


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
    assert check(PLANS_DB_ID, "Status", "Not Started") == (False, None, None)


def test_check_tuple_alias_stale() -> None:
    blocked, msg, suggested = check(PLANS_DB_ID, "Status", "🟡Draft")
    assert blocked is True
    assert suggested == "Not Started"
    assert msg is not None and "Not Started" in msg


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


# ---------------------------------------------------------------------------
# decide_waiting_for — Waiting status + blank Waiting For.
# ---------------------------------------------------------------------------

def test_waiting_with_blank_waiting_for_is_violation() -> None:
    v = decide_waiting_for(PLANS_DB_ID, "Waiting", "")
    assert isinstance(v, WaitingForViolation)
    assert "Waiting For" in v.message


def test_waiting_with_none_waiting_for_is_violation() -> None:
    v = decide_waiting_for(PLANS_DB_ID, "Waiting", None)
    assert isinstance(v, WaitingForViolation)


def test_waiting_with_whitespace_only_waiting_for_is_violation() -> None:
    v = decide_waiting_for(PLANS_DB_ID, "Waiting", "   ")
    assert isinstance(v, WaitingForViolation)


def test_waiting_with_populated_waiting_for_passes() -> None:
    v = decide_waiting_for(PLANS_DB_ID, "Waiting", "ADR-085 approval from Amit")
    assert v is None


def test_non_waiting_status_with_blank_waiting_for_passes() -> None:
    for status in ("In Progress", "Not Started", "Lower Priority", "Completed"):
        assert decide_waiting_for(PLANS_DB_ID, status, "") is None


def test_non_plans_db_ignored_by_waiting_for_check() -> None:
    unrelated_db = "00000000-0000-0000-0000-000000000099"
    assert decide_waiting_for(unrelated_db, "Waiting", "") is None


def test_backlog_db_is_also_enforced_surface_for_waiting_for() -> None:
    """Backlog Items DB shares the Waiting enforcement (DS-3 parity)."""
    v = decide_waiting_for(BACKLOG_DB_ID, "Waiting", "")
    assert isinstance(v, WaitingForViolation)


def test_backlog_data_source_id_also_enforced() -> None:
    v = decide_waiting_for(BACKLOG_DATA_SOURCE_ID, "Waiting", "")
    assert isinstance(v, WaitingForViolation)


def test_waiting_for_check_uses_data_source_id() -> None:
    v = decide_waiting_for(PLANS_DATA_SOURCE_ID, "Waiting", "")
    assert isinstance(v, WaitingForViolation)


def test_waiting_for_check_empty_db_id_ignored() -> None:
    assert decide_waiting_for("", "Waiting", "") is None
    assert decide_waiting_for(None, "Waiting", "") is None


def test_waiting_for_violation_db_id_normalized() -> None:
    v = decide_waiting_for(PLANS_DB_ID.upper(), "Waiting", "")
    assert isinstance(v, WaitingForViolation)
    assert v.db_id == PLANS_DB_ID.lower()


def test_waiting_for_violation_message_contains_guidance() -> None:
    v = decide_waiting_for(PLANS_DB_ID, "Waiting", None)
    assert v is not None
    assert "blocker" in v.message.lower() or "waiting for" in v.message.lower()


# ---------------------------------------------------------------------------
# Hardened: canonical taxonomy — Lower Priority (renamed from Deferred/Deprioritized)
# ---------------------------------------------------------------------------


def test_lower_priority_is_canonical() -> None:
    """2026-05-10 rename: 'Deferred' → 'Lower Priority'. Must be accepted."""
    assert decide(PLANS_DB_ID, "Status", "Lower Priority") is None


def test_deferred_is_stale_with_suggestion() -> None:
    """'Deferred' is stale — canonical is 'Lower Priority'."""
    v = decide(PLANS_DB_ID, "Status", "Deferred")
    assert isinstance(v, Violation)
    assert v.suggested == "Lower Priority"


def test_deprioritized_is_stale_with_suggestion() -> None:
    """'Deprioritized' is stale — canonical is 'Lower Priority'."""
    v = decide(PLANS_DB_ID, "Status", "Deprioritized")
    assert isinstance(v, Violation)
    assert v.suggested == "Lower Priority"


def test_active_is_stale_with_suggestion() -> None:
    """'Active' is stale (pre-Live schema) — canonical is 'In Progress'."""
    v = decide(PLANS_DB_ID, "Status", "Active")
    assert isinstance(v, Violation)
    assert v.suggested == "In Progress"


def test_forbidden_statuses_not_canonical() -> None:
    from _notion_plans_status_check import FORBIDDEN_PLANS_STATUSES

    for forbidden in FORBIDDEN_PLANS_STATUSES:
        assert forbidden not in CANONICAL_STATUSES
        assert decide(PLANS_DB_ID, "Status", forbidden) is not None


def test_draft_is_stale_maps_to_not_started() -> None:
    """Regression for 2026-05-05 incident: 'Draft' was written to Plans DB.
    It must be flagged and suggest 'Not Started'."""
    v = decide(PLANS_DB_ID, "Status", "Draft")
    assert isinstance(v, Violation)
    assert v.suggested == "Not Started"


def test_live_is_stale_maps_to_in_progress() -> None:
    """'Live' was the old name for 'In Progress' — must flag + suggest."""
    v = decide(PLANS_DB_ID, "Status", "Live")
    assert isinstance(v, Violation)
    assert v.suggested == "In Progress"


def test_all_emoji_stale_forms_are_covered() -> None:
    """Every entry in STALE_EQUIVALENTS must produce a Violation on Plans DB."""
    for stale, canonical in STALE_EQUIVALENTS.items():
        v = decide(PLANS_DB_ID, "Status", stale)
        assert isinstance(v, Violation), f"Expected Violation for stale form {stale!r}"
        assert v.suggested == canonical, f"Wrong suggestion for {stale!r}"


# ---------------------------------------------------------------------------
# Hardened: Backlog Items surface parity with Plans DB
# ---------------------------------------------------------------------------


def test_backlog_db_canonical_values_pass() -> None:
    """Backlog Items shares the same Status taxonomy — canonical values must pass."""
    for status in CANONICAL_STATUSES:
        assert decide(BACKLOG_DB_ID, "Status", status) is None, (
            f"Backlog DB should accept canonical status {status!r}"
        )


def test_backlog_db_stale_emoji_not_enforced() -> None:
    """Backlog DB does not enforce stale Status taxonomy — only Plans DB does."""
    v = decide(BACKLOG_DB_ID, "Status", "🟡Draft")
    assert v is None


def test_backlog_data_source_id_stale_not_enforced() -> None:
    """Backlog Data Source ID also does not enforce stale Status — only Plans DB surface."""
    v = decide(BACKLOG_DATA_SOURCE_ID, "Status", "🔵Completed")
    assert v is None


# ---------------------------------------------------------------------------
# Hardened: decide_waiting_for_quality (placeholder detection)
# ---------------------------------------------------------------------------


def test_quality_fires_on_tbd() -> None:
    v = decide_waiting_for_quality(PLANS_DB_ID, "Waiting", "TBD")
    assert isinstance(v, WaitingForViolation)
    assert "TBD" in v.message or "placeholder" in v.message.lower()


def test_quality_fires_on_unknown() -> None:
    v = decide_waiting_for_quality(PLANS_DB_ID, "Waiting", "unknown")
    assert isinstance(v, WaitingForViolation)


def test_quality_fires_on_na() -> None:
    v = decide_waiting_for_quality(PLANS_DB_ID, "Waiting", "N/A")
    assert isinstance(v, WaitingForViolation)


def test_quality_fires_on_placeholder() -> None:
    v = decide_waiting_for_quality(PLANS_DB_ID, "Waiting", "placeholder")
    assert isinstance(v, WaitingForViolation)


def test_quality_passes_for_real_blocker() -> None:
    v = decide_waiting_for_quality(PLANS_DB_ID, "Waiting", "ADR-085 approval from Amit")
    assert v is None


def test_quality_does_not_double_fire_on_blank() -> None:
    """When Waiting For is blank, decide_waiting_for fires — quality must stay silent."""
    assert decide_waiting_for_quality(PLANS_DB_ID, "Waiting", "") is None
    assert decide_waiting_for_quality(PLANS_DB_ID, "Waiting", None) is None


def test_quality_ignores_non_waiting_status() -> None:
    for status in ("In Progress", "Not Started", "Completed"):
        assert decide_waiting_for_quality(PLANS_DB_ID, status, "TBD") is None


def test_quality_ignores_unrelated_db() -> None:
    unrelated = "00000000-0000-0000-0000-000000000099"
    assert decide_waiting_for_quality(unrelated, "Waiting", "TBD") is None


def test_quality_backlog_db_also_enforced() -> None:
    v = decide_waiting_for_quality(BACKLOG_DB_ID, "Waiting", "pending")
    assert isinstance(v, WaitingForViolation)


# ---------------------------------------------------------------------------
# Hardened: Notion auto-creates unknown names silently — prove the guard works
# ---------------------------------------------------------------------------


def test_notion_silent_autocreate_guard_mixed_case() -> None:
    """Notion silently creates 'in progress' (lowercase) as a new option.
    The guard must flag it even though it looks canonical."""
    v = decide(PLANS_DB_ID, "Status", "in progress")
    assert isinstance(v, Violation), "Lowercase 'in progress' must be blocked (case-sensitive)"


def test_notion_silent_autocreate_guard_trailing_space() -> None:
    """A trailing space in the value would create a new Notion option silently."""
    v = decide(PLANS_DB_ID, "Status", "Completed ")
    assert isinstance(v, Violation), "Trailing-space value must be blocked"


def test_notion_silent_autocreate_guard_leading_space() -> None:
    v = decide(PLANS_DB_ID, "Status", " In Progress")
    assert isinstance(v, Violation), "Leading-space value must be blocked"
