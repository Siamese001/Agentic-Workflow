"""Unit tests for check_notion_plans_status_canonical (NP2 gate)."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "ops_scripts" / "ci"))

from check_notion_plans_status_canonical import (  # noqa: E402
    CANONICAL_STATUSES,
    STALE_STATUSES,
    _age_days,
    _calculate_oldest_age_days,
    _check_schema_validity,
    main,
)


class TestSchemaValidity:
    def test_no_canonical_stale_overlap(self) -> None:
        assert _check_schema_validity() == []

    def test_active_and_deprioritized_are_stale_not_canonical(self) -> None:
        assert "Active" in STALE_STATUSES
        assert "Deprioritized" in STALE_STATUSES
        assert "Active" not in CANONICAL_STATUSES
        assert "Deprioritized" not in CANONICAL_STATUSES
        assert "Lower Priority" in CANONICAL_STATUSES
        assert "In Progress" in CANONICAL_STATUSES


class TestAgeHelpers:
    def test_age_days_from_iso_z(self) -> None:
        past = (datetime.now(timezone.utc) - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        age = _age_days(past)
        assert age is not None
        assert 9 <= age <= 11

    def test_age_days_invalid_returns_none(self) -> None:
        assert _age_days(None) is None
        assert _age_days("not-a-date") is None

    def test_oldest_deferred_age_days(self) -> None:
        now = datetime.now(timezone.utc)
        older = (now - timedelta(days=12)).isoformat()
        newer = (now - timedelta(days=3)).isoformat()
        age = _calculate_oldest_age_days(
            [
                {"event_time_utc": newer},
                {"event_time_utc": older},
            ]
        )
        assert age is not None
        assert 11 <= age <= 13


def test_main_schema_only_passes_without_notion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NOTION_PLANS_STATUS_CANONICAL_BYPASS", raising=False)
    monkeypatch.setattr(sys, "argv", ["check_notion_plans_status_canonical.py"])
    assert main() == 0
