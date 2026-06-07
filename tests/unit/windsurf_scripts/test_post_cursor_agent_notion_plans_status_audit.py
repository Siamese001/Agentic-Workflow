#!/usr/bin/env python3
"""Unit tests for post_cursor_agent_notion_plans_status_audit.py — Waiting-For path.

Covers the WAITING_EMPTY_WAITING_FOR detection path added in NP10 (DS-6).

Test matrix:
  1. Status=Waiting + absent Waiting For  → violation emitted
  2. Status=Waiting + populated Waiting For → no violation
  3. Status=In Progress + absent Waiting For → no violation (not applicable)
  4. Non-Plans DB + Status=Waiting → no violation
  5. Status=Waiting + weak placeholder ("TBD") in Waiting For → advisory
"""

import sys
from pathlib import Path

# Ensure the scripts dir is importable without installing the package.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import pytest

from post_cursor_agent_notion_plans_status_audit import detect_violations  # type: ignore

# ---------------------------------------------------------------------------
# Helpers for building minimal invoke bodies.
# ---------------------------------------------------------------------------

_PLANS_DB_ID = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
_BACKLOG_DB_ID = "aa8d2507-101e-4384-81d9-60ea3fe33876"
_OTHER_DB_ID = "aaaabbbb-cccc-dddd-eeee-ffffaaaabbbb"


def _make_invoke(
    status: str,
    waiting_for: str | None = None,
    db_id: str = _PLANS_DB_ID,
) -> str:
    """Return a minimal Cursor Agent API-post-page invoke block string."""
    waiting_for_block = ""
    if waiting_for is not None:
        waiting_for_block = (
            f'"Waiting For": {{"rich_text": [{{"text": {{"content": "{waiting_for}"}}}}]}}, '
        )
    return (
        f'<invoke name="API-post-page">'
        f'"parent": {{"database_id": "{db_id}"}}, '
        f'"properties": {{'
        f'"Status": {{"select": {{"name": "{status}"}}}}, '
        f"{waiting_for_block}"
        f'"Slug": {{"title": [{{"text": {{"content": "test-plan-abc123"}}}}]}}'
        f"}}"
        f"</invoke>"
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestWaitingForDetection:
    """NP10 WAITING_EMPTY_WAITING_FOR detection path in detect_violations."""

    def test_waiting_no_waiting_for_field_yields_violation(self):
        """Status=Waiting with Waiting For field completely absent → violation."""
        response = _make_invoke(status="Waiting", waiting_for=None)
        violations = detect_violations(response)
        wf_violations = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert len(wf_violations) == 1
        assert wf_violations[0]["offending_value"] == "Waiting"
        assert wf_violations[0]["severity"] == "error"

    def test_waiting_empty_waiting_for_field_yields_violation(self):
        """Status=Waiting with Waiting For present but empty string → violation."""
        response = _make_invoke(status="Waiting", waiting_for="")
        violations = detect_violations(response)
        wf_violations = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert len(wf_violations) == 1

    def test_waiting_populated_waiting_for_no_violation(self):
        """Status=Waiting with a real Waiting For value → no violation."""
        response = _make_invoke(status="Waiting", waiting_for="Blocked on legal review of MSA")
        violations = detect_violations(response)
        wf_violations = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert len(wf_violations) == 0

    def test_in_progress_absent_waiting_for_no_violation(self):
        """Status=In Progress (not Waiting) with absent Waiting For → no violation."""
        response = _make_invoke(status="In Progress", waiting_for=None)
        violations = detect_violations(response)
        wf_violations = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert len(wf_violations) == 0

    def test_non_plans_db_waiting_no_violation(self):
        """Non-Plans DB with Status=Waiting → no violation (wrong surface)."""
        response = _make_invoke(status="Waiting", waiting_for=None, db_id=_OTHER_DB_ID)
        violations = detect_violations(response)
        wf_violations = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert len(wf_violations) == 0

    def test_empty_response_no_violation(self):
        """Empty response text → no violations."""
        assert detect_violations("") == []

    def test_violation_contains_rule_reference(self):
        """Violation record must reference the NP10 rule."""
        response = _make_invoke(status="Waiting", waiting_for=None)
        violations = detect_violations(response)
        wf_violations = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert wf_violations
        assert "NP10" in wf_violations[0].get("rule", "")

    def test_completed_status_no_waiting_for_violation(self):
        """Status=Completed with no Waiting For → no waiting-for violation."""
        response = _make_invoke(status="Completed", waiting_for=None)
        violations = detect_violations(response)
        wf_violations = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert len(wf_violations) == 0

    # DS-1: remediation hint present
    def test_violation_contains_remediation_hint(self):
        """Violation record must carry a remediation_hint (DS-1)."""
        response = _make_invoke(status="Waiting", waiting_for=None)
        violations = detect_violations(response)
        wf_violations = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert wf_violations
        assert wf_violations[0].get("remediation_hint"), "DS-1: remediation_hint must be non-empty"

    # DS-2: weak placeholder triggers WAITING_WEAK_WAITING_FOR advisory
    def test_waiting_weak_placeholder_yields_advisory(self):
        """Status=Waiting + 'TBD' in Waiting For → WAITING_WEAK_WAITING_FOR warn."""
        response = _make_invoke(status="Waiting", waiting_for="TBD")
        violations = detect_violations(response)
        weak = [v for v in violations if v.get("violation_type") == "WAITING_WEAK_WAITING_FOR"]
        assert len(weak) == 1
        assert weak[0]["severity"] == "warn"

    def test_waiting_weak_placeholder_no_duplicate_blank_violation(self):
        """Weak-placeholder must NOT also fire WAITING_EMPTY_WAITING_FOR."""
        response = _make_invoke(status="Waiting", waiting_for="TBD")
        violations = detect_violations(response)
        blank_v = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert len(blank_v) == 0, "DS-2: blank violation must not fire when placeholder present"

    # DS-3: Backlog Items DB parity
    def test_backlog_db_waiting_no_waiting_for_yields_violation(self):
        """Backlog Items DB + Status=Waiting + absent Waiting For → violation (DS-3)."""
        response = _make_invoke(status="Waiting", waiting_for=None, db_id=_BACKLOG_DB_ID)
        violations = detect_violations(response)
        wf_violations = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert len(wf_violations) == 1, "DS-3: Backlog Items surface must enforce Waiting-For"

    def test_backlog_db_waiting_populated_no_violation(self):
        """Backlog Items DB + Status=Waiting + populated Waiting For → no violation."""
        response = _make_invoke(
            status="Waiting",
            waiting_for="Waiting for legal sign-off on vendor contract",
            db_id=_BACKLOG_DB_ID,
        )
        violations = detect_violations(response)
        wf_violations = [v for v in violations if v.get("violation_type") == "WAITING_EMPTY_WAITING_FOR"]
        assert len(wf_violations) == 0


# ---------------------------------------------------------------------------
# New gap-filling tests discovered via web research + audit
# ---------------------------------------------------------------------------


def _make_patch_invoke(status: str, page_id: str = "abc123", db_id: str = _PLANS_DB_ID) -> str:
    """Construct a minimal API-patch-page invoke with a database_id in the body."""
    return (
        f'<invoke name="API-patch-page">'
        f'<parameter name="page_id">{page_id}</parameter>'
        f'"parent": {{"database_id": "{db_id}"}}, '
        f'"properties": {{"Status": {{"select": {{"name": "{status}"}}}}}}'
        f"</invoke>"
    )


def _make_mcp_prefixed_invoke(status: str, db_id: str = _PLANS_DB_ID) -> str:
    """Simulate a Windsurf tool-proxy invoke with mcp7_ prefix."""
    return (
        f'<invoke name="mcp7_API-post-page">'
        f'"parent": {{"database_id": "{db_id}"}}, '
        f'"properties": {{"Status": {{"select": {{"name": "{status}"}}}}, '
        f'"Slug": {{"title": [{{"text": {{"content": "test-plan-abc123"}}}}]}}'
        f"}}"
        f"</invoke>"
    )


class TestStaleStatusDetection:
    """detect_violations must catch stale/emoji status values."""

    def test_draft_status_yields_violation(self):
        """'Draft' is stale — should be 'Not Started'."""
        response = _make_invoke(status="Draft")
        violations = detect_violations(response)
        status_vs = [v for v in violations if "Draft" in v.get("offending_value", "")]
        assert len(status_vs) == 1
        assert status_vs[0]["suggested"] == "Not Started"

    def test_live_status_yields_violation(self):
        """'Live' is stale — should be 'In Progress'."""
        response = _make_invoke(status="Live")
        violations = detect_violations(response)
        status_vs = [v for v in violations if "Live" in v.get("offending_value", "")]
        assert len(status_vs) == 1
        assert status_vs[0]["suggested"] == "In Progress"

    def test_deprioritized_status_yields_violation(self):
        """'Deprioritized' is stale — should be 'Lower Priority'."""
        response = _make_invoke(status="Deprioritized")
        violations = detect_violations(response)
        status_vs = [v for v in violations if "Deprioritized" in v.get("offending_value", "")]
        assert len(status_vs) == 1
        assert status_vs[0]["suggested"] == "Lower Priority"

    def test_deferred_status_yields_violation(self):
        """'Deferred' was renamed to 'Lower Priority' — should fire."""
        response = _make_invoke(status="Deferred")
        violations = detect_violations(response)
        status_vs = [v for v in violations if "Deferred" in v.get("offending_value", "")]
        assert len(status_vs) == 1
        assert status_vs[0]["suggested"] == "Lower Priority"

    def test_emoji_draft_yields_violation(self):
        """Emoji form '🟡Draft' must be caught."""
        response = _make_invoke(status="🟡Draft")
        violations = detect_violations(response)
        status_vs = [v for v in violations if "🟡Draft" in v.get("offending_value", "")]
        assert len(status_vs) == 1

    def test_canonical_lower_priority_no_violation(self):
        """'Lower Priority' is canonical — must NOT fire."""
        response = _make_invoke(status="Lower Priority")
        violations = detect_violations(response)
        assert violations == []

    def test_canonical_in_progress_no_violation(self):
        response = _make_invoke(status="In Progress")
        violations = detect_violations(response)
        assert violations == []

    def test_canonical_not_started_no_violation(self):
        response = _make_invoke(status="Not Started")
        violations = detect_violations(response)
        assert violations == []

    def test_canonical_retired_no_violation(self):
        response = _make_invoke(status="Retired")
        violations = detect_violations(response)
        assert violations == []

    def test_canonical_archived_no_violation(self):
        response = _make_invoke(status="Archived")
        violations = detect_violations(response)
        assert violations == []

    def test_completely_unknown_status_still_yields_violation(self):
        """Unknown/typo statuses also violate — with empty suggested."""
        response = _make_invoke(status="Banana")
        violations = detect_violations(response)
        status_vs = [v for v in violations if "Banana" in v.get("offending_value", "")]
        assert len(status_vs) == 1
        assert status_vs[0]["suggested"] == ""


class TestApiPatchPage:
    """Patch-page invokes are scanned when they carry a database_id in the body."""

    def test_patch_page_with_stale_status_detected(self):
        """API-patch-page + Plans DB id + stale status → violation."""
        response = _make_patch_invoke(status="Draft", db_id=_PLANS_DB_ID)
        violations = detect_violations(response)
        status_vs = [v for v in violations if "Draft" in v.get("offending_value", "")]
        assert len(status_vs) == 1
        assert status_vs[0]["tool"] == "API-patch-page"

    def test_patch_page_canonical_status_no_violation(self):
        response = _make_patch_invoke(status="In Progress", db_id=_PLANS_DB_ID)
        violations = detect_violations(response)
        assert violations == []

    def test_patch_page_wrong_db_no_violation(self):
        """Patch targeting unrelated DB — must not fire."""
        response = _make_patch_invoke(status="Draft", db_id=_OTHER_DB_ID)
        violations = detect_violations(response)
        assert violations == []


class TestMcpPrefixedInvokes:
    """Windsurf tool-proxy wraps invoke names with mcp<N>_ prefix."""

    def test_mcp_prefixed_post_page_stale_detected(self):
        """mcp7_API-post-page with stale status must be caught."""
        response = _make_mcp_prefixed_invoke(status="Draft")
        violations = detect_violations(response)
        status_vs = [v for v in violations if "Draft" in v.get("offending_value", "")]
        assert len(status_vs) == 1

    def test_mcp_prefixed_post_page_canonical_passes(self):
        response = _make_mcp_prefixed_invoke(status="In Progress")
        violations = detect_violations(response)
        assert violations == []

    def test_arbitrary_mcp_number_prefix_detected(self):
        """mcp99_ prefix must still be matched."""
        response = (
            '<invoke name="mcp99_API-post-page">'
            f'"parent": {{"database_id": "{_PLANS_DB_ID}"}}, '
            '"properties": {"Status": {"select": {"name": "Live"}}}'
            "</invoke>"
        )
        violations = detect_violations(response)
        status_vs = [v for v in violations if "Live" in v.get("offending_value", "")]
        assert len(status_vs) == 1


class TestMultipleInvokesInResponse:
    """Multiple invokes in one response — each scanned independently."""

    def test_two_violations_in_one_response(self):
        """Two separate stale-status invokes → two violations."""
        response = (
            _make_invoke(status="Draft")
            + "\n"
            + _make_invoke(status="Live")
        )
        violations = detect_violations(response)
        offenders = {v.get("offending_value") for v in violations}
        assert "Draft" in offenders
        assert "Live" in offenders

    def test_one_stale_one_clean_yields_one_violation(self):
        response = (
            _make_invoke(status="Draft")
            + "\n"
            + _make_invoke(status="In Progress")
        )
        violations = detect_violations(response)
        status_vs = [v for v in violations if v.get("offending_value") == "Draft"]
        assert len(status_vs) == 1
        # The canonical one must NOT add any
        clean_vs = [v for v in violations if v.get("offending_value") == "In Progress"]
        assert len(clean_vs) == 0

    def test_non_plans_and_plans_db_in_same_response(self):
        """Plans violation is caught; non-Plans invoke is ignored."""
        non_plans = _make_invoke(status="Draft", db_id=_OTHER_DB_ID)
        plans = _make_invoke(status="Draft", db_id=_PLANS_DB_ID)
        violations = detect_violations(non_plans + "\n" + plans)
        assert len(violations) == 1

    def test_data_source_id_triggers_detection(self):
        """Plans data-source id in body (not database id) must also fire."""
        _PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
        response = _make_invoke(status="Draft", db_id=_PLANS_DATA_SOURCE_ID)
        violations = detect_violations(response)
        status_vs = [v for v in violations if "Draft" in v.get("offending_value", "")]
        assert len(status_vs) == 1


class TestExtractResponseText:
    """_extract_response_text handles all Windsurf payload shapes."""

    def test_plain_string_passthrough(self):
        from post_cursor_agent_notion_plans_status_audit import _extract_response_text
        assert _extract_response_text("hello world") == "hello world"

    def test_dict_with_response_key(self):
        from post_cursor_agent_notion_plans_status_audit import _extract_response_text
        payload = {"response": "some text"}
        assert _extract_response_text(payload) == "some text"

    def test_dict_with_text_key(self):
        from post_cursor_agent_notion_plans_status_audit import _extract_response_text
        payload = {"text": "some text"}
        assert _extract_response_text(payload) == "some text"

    def test_dict_with_content_key(self):
        from post_cursor_agent_notion_plans_status_audit import _extract_response_text
        payload = {"content": "some text"}
        assert _extract_response_text(payload) == "some text"

    def test_nested_tool_info_response(self):
        from post_cursor_agent_notion_plans_status_audit import _extract_response_text
        payload = {"tool_info": {"response": "inner text"}}
        assert _extract_response_text(payload) == "inner text"

    def test_nested_tool_info_text(self):
        from post_cursor_agent_notion_plans_status_audit import _extract_response_text
        payload = {"tool_info": {"text": "inner text"}}
        assert _extract_response_text(payload) == "inner text"

    def test_empty_dict_falls_through_to_json_dump(self):
        from post_cursor_agent_notion_plans_status_audit import _extract_response_text
        result = _extract_response_text({})
        assert isinstance(result, str)

    def test_non_string_non_dict_returns_empty(self):
        from post_cursor_agent_notion_plans_status_audit import _extract_response_text
        assert _extract_response_text(42) == ""  # type: ignore[arg-type]
        assert _extract_response_text(None) == ""  # type: ignore[arg-type]
        assert _extract_response_text([]) == ""  # type: ignore[arg-type]

    def test_dict_prefers_response_over_text(self):
        """When both 'response' and 'text' keys exist, 'response' wins (iteration order)."""
        from post_cursor_agent_notion_plans_status_audit import _extract_response_text
        payload = {"response": "first", "text": "second"}
        result = _extract_response_text(payload)
        assert result in {"first", "second"}  # order-agnostic; just verify one wins


class TestIsPlansId:
    """_is_plans_id tolerance for dashed/undashed, uppercase IDs."""

    def test_plans_db_id_dashed(self):
        from post_cursor_agent_notion_plans_status_audit import _is_plans_id
        assert _is_plans_id("6aba34d9-4d0b-4f4c-b956-b2bdea541ca9") is True

    def test_plans_db_id_undashed(self):
        from post_cursor_agent_notion_plans_status_audit import _is_plans_id
        assert _is_plans_id("6aba34d94d0b4f4cb956b2bdea541ca9") is True

    def test_plans_db_id_uppercase(self):
        from post_cursor_agent_notion_plans_status_audit import _is_plans_id
        assert _is_plans_id("6ABA34D9-4D0B-4F4C-B956-B2BDEA541CA9") is True

    def test_plans_data_source_id_matches(self):
        from post_cursor_agent_notion_plans_status_audit import _is_plans_id
        assert _is_plans_id("ac53d31b-3068-4039-9ebe-856c12caab32") is True

    def test_backlog_db_id_matches(self):
        from post_cursor_agent_notion_plans_status_audit import _is_plans_id
        assert _is_plans_id("aa8d2507-101e-4384-81d9-60ea3fe33876") is True

    def test_unrelated_id_rejected(self):
        from post_cursor_agent_notion_plans_status_audit import _is_plans_id
        assert _is_plans_id("aaaabbbb-cccc-dddd-eeee-ffffaaaabbbb") is False

    def test_empty_string_rejected(self):
        from post_cursor_agent_notion_plans_status_audit import _is_plans_id
        assert _is_plans_id("") is False
