"""Unit tests for apps_rg targeting brief prompt SSOT."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from apps_research.prompt_assembly.apps_rg_targeting_brief import (
    apps_rg_targeting_brief_enabled,
    build_targeting_brief_prompt,
    extract_jd_text,
    format_research_findings,
    load_targeting_brief_prompt_template,
)


def test_prompt_template_loads_and_contains_sections() -> None:
    text = load_targeting_brief_prompt_template()
    assert "=== STRATEGIC MANDATE ===" in text
    assert "{{jd_text}}" in text
    assert "{{research_notes}}" in text


def test_build_targeting_brief_prompt_replaces_placeholders() -> None:
    out = build_targeting_brief_prompt(
        jd_text="VP Agentic AI at AIG",
        research_notes="- Q1 NPW $5.6B",
        target_entity="AIG",
    )
    assert "VP Agentic AI at AIG" in out
    assert "- Q1 NPW $5.6B" in out
    assert "AIG" in out
    assert "{{jd_text}}" not in out


def test_apps_rg_targeting_brief_enabled_from_jd_context() -> None:
    assert apps_rg_targeting_brief_enabled(
        jd_context={"output_format": "apps_rg_targeting_brief_v1"}
    )
    assert not apps_rg_targeting_brief_enabled(jd_context={})


def test_extract_jd_text_from_context_and_file(tmp_path: Path) -> None:
    assert extract_jd_text(jd_context={"content": "Full JD body"}) == "Full JD body"
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("File JD", encoding="utf-8")
    assert extract_jd_text(jd_context={}, jd_anchor=jd_file) == "File JD"


def test_format_research_findings_skips_empty() -> None:
    blob = format_research_findings({"overview": "x", "empty": ""})
    assert "### overview" in blob
    assert "empty" not in blob


def test_format_research_findings_truncates_at_max_chars() -> None:
    long = "word " * 5000
    blob = format_research_findings({"overview": long}, max_chars=100)
    assert len(blob) <= 100
    assert blob.endswith("...")


@pytest.mark.parametrize(
    ("env_value", "expected"),
    [
        ("1", True),
        ("true", True),
        ("0", False),
        ("off", False),
    ],
)
def test_apps_rg_targeting_brief_enabled_env_override(
    monkeypatch: pytest.MonkeyPatch, env_value: str, expected: bool
) -> None:
    monkeypatch.setenv("APPS_RESEARCH_APPS_RG_TARGETING_BRIEF", env_value)
    assert apps_rg_targeting_brief_enabled(jd_context={}) is expected
