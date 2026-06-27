"""Section CLI provider defaults for apps_rg lanes."""
from __future__ import annotations

from apps_rg.runtime.section_cli_defaults import (
    CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_CLAUDE,
    CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI,
    default_lane_provider_for_section,
    resolve_cli_lane_provider_with_source,
)


def test_openai_backed_sections_default_to_external_openai() -> None:
    for section_id in ("unify_narrative", "ibm_narrative", "insurtech_narrative", "ey_narrative"):
        assert default_lane_provider_for_section(section_id) == "external_openai", section_id


def test_claude_backed_sections_default_to_external_claude() -> None:
    for section_id in (
        "competencies",
        "headline",
        "executive_summary",
        "unify_bullets",
        "ibm_bullets",
        "insurtech_bullets",
        "ey_bullets",
    ):
        assert default_lane_provider_for_section(section_id) == "external_claude", section_id


def test_default_resolution_source_tracks_section_default() -> None:
    provider, source = resolve_cli_lane_provider_with_source(None, section_id="competencies")
    assert provider == "external_claude"
    assert source == CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_CLAUDE

    provider, source = resolve_cli_lane_provider_with_source(None, section_id="unify_narrative")
    assert provider == "external_openai"
    assert source == CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_EXTERNAL_OPENAI
