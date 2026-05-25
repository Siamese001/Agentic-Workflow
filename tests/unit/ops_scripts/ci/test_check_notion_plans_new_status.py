#!/usr/bin/env python3
"""
Unit tests for check_notion_plans_new_status.py (NP6 gate).

Uses mocking for Notion API responses and datetime to ensure deterministic tests.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "ops_scripts" / "ci"))

from check_notion_plans_new_status import (
    CANONICAL_NEW_PLAN_STATUS,
    DETECTION_WINDOW_HOURS,
    STALE_NEW_PLAN_STATUSES,
    VIOLATION_STATUSES,
    _is_newly_created,
    _now_utc,
    _parse_iso8601,
    check_new_plans_status,
    main,
)


class TestIso8601Parsing:
    def test_with_microseconds_and_z(self):
        result = _parse_iso8601("2026-05-10T18:14:00.000Z")
        assert result is not None
        assert result.year == 2026
        assert result.hour == 18
        assert result.tzinfo is not None

    def test_without_microseconds(self):
        result = _parse_iso8601("2026-05-10T18:14:00Z")
        assert result is not None
        assert result.year == 2026

    def test_invalid_returns_none(self):
        assert _parse_iso8601("invalid") is None
        assert _parse_iso8601("") is None


class TestIsNewlyCreated:
    def test_within_window_is_new(self):
        now = datetime(2026, 5, 10, 18, 0, 0, tzinfo=timezone.utc)
        created = (now - timedelta(hours=12)).isoformat()
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            assert _is_newly_created(created) is True

    def test_at_boundary_is_new(self):
        now = datetime(2026, 5, 10, 18, 0, 0, tzinfo=timezone.utc)
        created = (now - timedelta(hours=DETECTION_WINDOW_HOURS)).isoformat()
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            assert _is_newly_created(created) is True

    def test_outside_window_is_old(self):
        now = datetime(2026, 5, 10, 18, 0, 0, tzinfo=timezone.utc)
        created = (now - timedelta(hours=DETECTION_WINDOW_HOURS + 1)).isoformat()
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            assert _is_newly_created(created) is False

    def test_future_time_is_new(self):
        # Clock skew case - treat as new
        now = datetime(2026, 5, 10, 18, 0, 0, tzinfo=timezone.utc)
        created = (now + timedelta(hours=1)).isoformat()
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            assert _is_newly_created(created) is True


class TestCheckNewPlansStatus:
    def test_no_token_returns_error(self):
        report = check_new_plans_status(None)
        assert "errors" in report
        assert any("NOTION_TOKEN" in e for e in report["errors"])

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_new_plan_with_not_started_passes(self, mock_query):
        now = _now_utc()
        created = now.isoformat()
        
        mock_query.return_value = [
            {
                "id": "page-123",
                "created_time": created,
                "properties": {
                    "Slug": {"title": [{"text": {"content": "test-plan-abc123"}}]},
                    "Status": {"select": {"name": CANONICAL_NEW_PLAN_STATUS}},
                },
            }
        ]
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        
        assert report["violation_count"] == 0
        assert report["passed_count"] == 1
        assert len(report["passed"]) == 1
        assert report["passed"][0]["slug"] == "test-plan-abc123"

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_new_plan_with_deferred_is_violation(self, mock_query):
        now = _now_utc()
        created = now.isoformat()
        
        mock_query.return_value = [
            {
                "id": "page-456",
                "created_time": created,
                "properties": {
                    "Slug": {"title": [{"text": {"content": "bad-plan-def456"}}]},
                    "Status": {"select": {"name": "Deferred"}},
                },
            }
        ]
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        
        assert report["violation_count"] == 1
        assert len(report["violations"]) == 1
        assert report["violations"][0]["slug"] == "bad-plan-def456"
        assert report["violations"][0]["status"] == "Deferred"
        assert report["violations"][0]["violation_type"] == "NEW_PLAN_WRONG_STATUS"

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_new_plan_with_waiting_is_violation(self, mock_query):
        now = _now_utc()
        created = now.isoformat()
        
        mock_query.return_value = [
            {
                "id": "page-789",
                "created_time": created,
                "properties": {
                    "Slug": {"title": [{"text": {"content": "wait-plan-wait789"}}]},
                    "Status": {"select": {"name": "Waiting"}},
                },
            }
        ]
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        
        assert report["violation_count"] == 1
        assert report["violations"][0]["status"] == "Waiting"

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_old_plan_with_deferred_is_skipped(self, mock_query):
        now = datetime(2026, 5, 10, 18, 0, 0, tzinfo=timezone.utc)
        created = (now - timedelta(hours=25)).isoformat()  # Outside 24h window
        
        mock_query.return_value = [
            {
                "id": "page-old",
                "created_time": created,
                "properties": {
                    "Slug": {"title": [{"text": {"content": "old-plan-old123"}}]},
                    "Status": {"select": {"name": "Deferred"}},
                },
            }
        ]
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        
        assert report["violation_count"] == 0
        assert len(report["skipped"]) == 1
        assert report["skipped"][0]["reason"] == "outside_detection_window"

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_missing_slug_is_skipped(self, mock_query):
        now = _now_utc()
        
        mock_query.return_value = [
            {
                "id": "page-noslug",
                "created_time": now.isoformat(),
                "properties": {
                    # No Slug property
                    "Status": {"select": {"name": CANONICAL_NEW_PLAN_STATUS}},
                },
            }
        ]
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        
        assert report["violation_count"] == 0
        assert len(report["skipped"]) == 1
        assert report["skipped"][0]["reason"] == "no_slug"

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_api_error_fail_open(self, mock_query):
        mock_query.return_value = []
        
        report = check_new_plans_status("fake-token")
        
        assert "errors" in report
        assert any("No results" in e for e in report["errors"])


class TestMain:
    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_main_with_violations_advisory(self, mock_query):
        now = _now_utc()
        
        mock_query.return_value = [
            {
                "id": "page-bad",
                "created_time": now.isoformat(),
                "properties": {
                    "Slug": {"title": [{"text": {"content": "bad-plan"}}]},
                    "Status": {"select": {"name": "Deferred"}},
                },
            }
        ]
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            exit_code = main([])
        
        assert exit_code == 0  # Advisory mode

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_main_with_violations_fail_closed(self, mock_query):
        now = _now_utc()
        
        mock_query.return_value = [
            {
                "id": "page-bad",
                "created_time": now.isoformat(),
                "properties": {
                    "Slug": {"title": [{"text": {"content": "bad-plan"}}]},
                    "Status": {"select": {"name": "Deferred"}},
                },
            }
        ]
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            exit_code = main(["--fail-closed"])
        
        assert exit_code == 1

    def test_bypass_returns_0(self):
        with mock.patch.dict("os.environ", {"NOTION_PLANS_NEW_STATUS_BYPASS": "1"}):
            exit_code = main([])
        assert exit_code == 0

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_pass_no_violations(self, mock_query):
        now = _now_utc()
        
        mock_query.return_value = [
            {
                "id": "page-good",
                "created_time": now.isoformat(),
                "properties": {
                    "Slug": {"title": [{"text": {"content": "good-plan"}}]},
                    "Status": {"select": {"name": CANONICAL_NEW_PLAN_STATUS}},
                },
            }
        ]
        
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            exit_code = main([])
        
        assert exit_code == 0


class TestViolationStatuses:
    def test_violation_statuses_set(self):
        assert "Lower Priority" in VIOLATION_STATUSES
        assert "Waiting" in VIOLATION_STATUSES
        assert "In Progress" in VIOLATION_STATUSES
        assert "Completed" in VIOLATION_STATUSES
        assert CANONICAL_NEW_PLAN_STATUS not in VIOLATION_STATUSES
        assert "Deferred" in STALE_NEW_PLAN_STATUSES

    def test_retired_NOT_in_violation_statuses(self):
        """Retired is not checked by the new-plan gate (it's a terminal status
        not produced by PLAN_CREATED markers)."""
        assert "Retired" not in VIOLATION_STATUSES

    def test_archived_NOT_in_violation_statuses(self):
        """Archived is not checked by the new-plan gate."""
        assert "Archived" not in VIOLATION_STATUSES

    def test_violation_statuses_exhaustiveness(self):
        """Canonical wrong-at-creation statuses (excludes stale legacy names)."""
        assert VIOLATION_STATUSES == frozenset({
            "Lower Priority",
            "Waiting",
            "In Progress",
            "Completed",
        })


class TestEdgeCasePlans:
    """Edge cases for plan properties that deviate from the happy path."""

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_missing_status_property_is_skipped(self, mock_query):
        """Plan without a Status property is skipped, not flagged."""
        now = _now_utc()
        mock_query.return_value = [
            {
                "id": "page-nostatus",
                "created_time": now.isoformat(),
                "properties": {
                    "Slug": {"title": [{"text": {"content": "no-status-plan-abc123"}}]},
                    # No "Status" key
                },
            }
        ]
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        assert report["violation_count"] == 0
        skipped_reasons = [s.get("reason") for s in report.get("skipped", [])]
        assert any("status" in (r or "").lower() for r in skipped_reasons)

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_null_select_value_is_skipped(self, mock_query):
        """Plan with Status.select == null is skipped gracefully."""
        now = _now_utc()
        mock_query.return_value = [
            {
                "id": "page-nullstatus",
                "created_time": now.isoformat(),
                "properties": {
                    "Slug": {"title": [{"text": {"content": "null-status-plan-abc123"}}]},
                    "Status": {"select": None},
                },
            }
        ]
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        assert report["violation_count"] == 0

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_mixed_pass_and_fail_in_same_batch(self, mock_query):
        """One good + one bad in same response → exactly one violation."""
        now = _now_utc()
        mock_query.return_value = [
            {
                "id": "page-good",
                "created_time": now.isoformat(),
                "properties": {
                    "Slug": {"title": [{"text": {"content": "good-plan-aaa111"}}]},
                    "Status": {"select": {"name": CANONICAL_NEW_PLAN_STATUS}},
                },
            },
            {
                "id": "page-bad",
                "created_time": now.isoformat(),
                "properties": {
                    "Slug": {"title": [{"text": {"content": "bad-plan-bbb222"}}]},
                    "Status": {"select": {"name": "In Progress"}},
                },
            },
        ]
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        assert report["violation_count"] == 1
        assert report["passed_count"] == 1
        assert report["violations"][0]["slug"] == "bad-plan-bbb222"

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_in_progress_on_new_plan_is_violation(self, mock_query):
        """In Progress is not the canonical new-plan status — must flag."""
        now = _now_utc()
        mock_query.return_value = [
            {
                "id": "page-inprog",
                "created_time": now.isoformat(),
                "properties": {
                    "Slug": {"title": [{"text": {"content": "inprog-plan-abc123"}}]},
                    "Status": {"select": {"name": "In Progress"}},
                },
            }
        ]
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        assert report["violation_count"] == 1
        assert report["violations"][0]["status"] == "In Progress"

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_completed_on_new_plan_is_violation(self, mock_query):
        """Completed on a brand-new plan → violation."""
        now = _now_utc()
        mock_query.return_value = [
            {
                "id": "page-comp",
                "created_time": now.isoformat(),
                "properties": {
                    "Slug": {"title": [{"text": {"content": "comp-plan-abc123"}}]},
                    "Status": {"select": {"name": "Completed"}},
                },
            }
        ]
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        assert report["violation_count"] == 1

    @mock.patch("check_notion_plans_new_status._query_plans_db")
    def test_multiple_violations_counted_correctly(self, mock_query):
        """Three new plans each with a wrong status → violation_count == 3."""
        now = _now_utc()
        mock_query.return_value = [
            {
                "id": f"page-{i}",
                "created_time": now.isoformat(),
                "properties": {
                    "Slug": {"title": [{"text": {"content": f"bad-plan-{i}aabb{i}c"}}]},
                    "Status": {"select": {"name": status}},
                },
            }
            for i, status in enumerate(["In Progress", "Completed", "Waiting"])
        ]
        with mock.patch("check_notion_plans_new_status._now_utc", return_value=now):
            report = check_new_plans_status("fake-token")
        assert report["violation_count"] == 3

    def test_parse_iso8601_with_timezone_offset(self):
        """ISO8601 with explicit +00:00 offset must parse."""
        result = _parse_iso8601("2026-05-10T18:14:00+00:00")
        assert result is not None
        assert result.year == 2026

    def test_parse_iso8601_with_negative_offset(self):
        """ISO8601 with -04:00 timezone offset must parse without crashing."""
        result = _parse_iso8601("2026-05-10T14:14:00-04:00")
        # Either parses or returns None — must not raise
        assert result is None or result.year == 2026


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
