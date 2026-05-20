"""Fail-closed executive_summary CLI targeting validation."""

from __future__ import annotations

import argparse
from types import SimpleNamespace

import pytest

from apps_rg.runtime.section_cli_defaults import (
    SectionCliConfigError,
    collect_executive_summary_mandatory_missing,
    validate_executive_summary_mandatory_inputs,
)
from apps_rg.runtime.targeting_input_freshness import (
    is_stale_default_targeting_briefing,
    is_stale_default_targeting_jd,
    validate_executive_summary_targeting_inputs_updated,
)


def test_collect_mandatory_missing_all_four_flags() -> None:
    args = argparse.Namespace(
        target_company="",
        target_role="",
        jd="",
        manual_brief="",
    )
    assert collect_executive_summary_mandatory_missing(args) == [
        "--target-company",
        "--target-role",
        "--jd",
        "--manual-brief",
    ]


def test_validate_passes_when_all_present() -> None:
    args = SimpleNamespace(
        target_company="Acme Corp",
        target_role="VP Engineering",
        jd="Lead agentic platforms.",
        manual_brief="Regulated enterprise context.",
    )
    validate_executive_summary_mandatory_inputs(args)


def test_validate_fails_closed_when_jd_missing() -> None:
    args = SimpleNamespace(
        target_company="Acme Corp",
        target_role="VP Engineering",
        jd="",
        manual_brief="Briefing text.",
    )
    with pytest.raises(SectionCliConfigError, match="--jd"):
        validate_executive_summary_mandatory_inputs(args)


def test_stale_default_jd_and_briefing_detected() -> None:
    from apps_rg.runtime.briefing_ssot import default_targeting_briefing_text
    from apps_rg.runtime.jd_resolution import default_jd_targeting_text

    assert is_stale_default_targeting_jd(default_jd_targeting_text())
    assert is_stale_default_targeting_briefing(default_targeting_briefing_text())
    assert not is_stale_default_targeting_jd("Updated JD body with role-specific requirements.")
    assert not is_stale_default_targeting_briefing("Updated briefing with company research themes.")


def test_validate_fails_when_default_ssot_paths_used(monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    repo = Path(__file__).resolve().parents[3]
    args = SimpleNamespace(
        target_company="Unify Consulting",
        target_role="SVP Engineering",
        jd=str(repo / "apps_rg" / "config" / "default_jd_targeting.txt"),
        manual_brief=str(repo / "apps_rg" / "config" / "default_targeting_briefing.txt"),
    )
    monkeypatch.delenv("APPS_RG_ALLOW_STALE_TARGETING_SSOT", raising=False)
    with pytest.raises(SectionCliConfigError, match="not updated"):
        validate_executive_summary_targeting_inputs_updated(args)


def test_validate_allows_stale_when_env_waiver_set(monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    repo = Path(__file__).resolve().parents[3]
    args = SimpleNamespace(
        target_company="Unify Consulting",
        target_role="SVP Engineering",
        jd=str(repo / "apps_rg" / "config" / "default_jd_targeting.txt"),
        manual_brief=str(repo / "apps_rg" / "config" / "default_targeting_briefing.txt"),
    )
    monkeypatch.setenv("APPS_RG_ALLOW_STALE_TARGETING_SSOT", "1")
    validate_executive_summary_targeting_inputs_updated(args)
