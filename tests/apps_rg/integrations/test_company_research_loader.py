"""Tests for apps_rg.integrations.company_research_loader."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from apps_rg.integrations.company_research_loader import (
    CompanyResearchLoadOptions,
    load_company_brief,
)
from apps_rg.types.company_research import (
    CompanyBrief,
    CompanyBriefMissingError,
    CompanyBriefSource,
)


def _valid_brief_payload(company: str = "TestCo") -> dict:
    return {
        "company": company,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "user_uploaded",
        "freshness_ttl_days": 30,
        "overview": {
            "tagline": "We build things",
            "core_offerings": ["consulting", "engineering"],
        },
        "strategic_priorities": [
            "scale consulting",
            "grow managed services",
        ],
        "language_to_mirror": ["consulting", "delivery", "outcomes"],
    }


# ----------------------------------------------------------------- mode 1


def test_load_manual_brief_succeeds(tmp_path: Path) -> None:
    brief_path = tmp_path / "company_research.json"
    brief_path.write_text(json.dumps(_valid_brief_payload()), encoding="utf-8")
    opts = CompanyResearchLoadOptions(manual_path=brief_path)
    brief = load_company_brief(opts)
    assert isinstance(brief, CompanyBrief)
    assert brief.company == "TestCo"
    assert brief.source == CompanyBriefSource.USER_UPLOADED


def test_load_manual_invalid_json_raises_missing(tmp_path: Path) -> None:
    brief_path = tmp_path / "company_research.json"
    brief_path.write_text("{not valid", encoding="utf-8")
    opts = CompanyResearchLoadOptions(
        manual_path=brief_path,
        target_company=None,  # no other modes -> hard fail
    )
    with pytest.raises(CompanyBriefMissingError):
        load_company_brief(opts)


def test_no_manual_no_target_raises(tmp_path: Path) -> None:
    opts = CompanyResearchLoadOptions(
        manual_path=tmp_path / "missing.json",
        target_company=None,
    )
    with pytest.raises(CompanyBriefMissingError) as excinfo:
        load_company_brief(opts)
    assert "no --target-company" in str(excinfo.value).lower() or "no manual" in str(excinfo.value).lower()


# ----------------------------------------------------------------- mode 4


def test_no_modes_enabled_with_target_still_raises(tmp_path: Path) -> None:
    """When manual missing AND no research-via AND no auto flags: fail loudly."""
    opts = CompanyResearchLoadOptions(
        manual_path=tmp_path / "missing.json",
        target_company="Blend360",
        research_via=None,
        auto_research_internal=False,
    )
    with pytest.raises(CompanyBriefMissingError):
        load_company_brief(opts)


def test_manual_invalid_schema_does_not_pollute_load(tmp_path: Path) -> None:
    brief_path = tmp_path / "company_research.json"
    # Missing required language_to_mirror with min_length=3
    bad = _valid_brief_payload()
    bad["language_to_mirror"] = ["only one"]
    brief_path.write_text(json.dumps(bad), encoding="utf-8")
    opts = CompanyResearchLoadOptions(
        manual_path=brief_path, target_company=None
    )
    with pytest.raises(CompanyBriefMissingError):
        load_company_brief(opts)


# ---------------------------------------------------------- staleness


def test_stale_brief_loads_with_warning(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    payload = _valid_brief_payload()
    payload["fetched_at"] = (
        datetime.now(timezone.utc) - timedelta(days=120)
    ).isoformat()
    payload["freshness_ttl_days"] = 30
    brief_path = tmp_path / "company_research.json"
    brief_path.write_text(json.dumps(payload), encoding="utf-8")

    opts = CompanyResearchLoadOptions(manual_path=brief_path)
    with caplog.at_level("WARNING"):
        brief = load_company_brief(opts)
    assert brief.is_stale()
    assert any("stale" in m.lower() for m in caplog.messages)
