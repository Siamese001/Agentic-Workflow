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
