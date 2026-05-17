"""Default targeting briefing loads from committed SSOT file."""

from __future__ import annotations

from apps_rg.runtime.briefing_ssot import (
    DEFAULT_TARGETING_BRIEFING_PATH,
    default_targeting_briefing_text,
)


def test_default_targeting_briefing_path_exists() -> None:
    assert DEFAULT_TARGETING_BRIEFING_PATH.is_file(), DEFAULT_TARGETING_BRIEFING_PATH


def test_default_targeting_briefing_text_matches_file() -> None:
    expected = DEFAULT_TARGETING_BRIEFING_PATH.read_text(encoding="utf-8").strip()
    default_targeting_briefing_text.cache_clear()
    assert default_targeting_briefing_text() == expected
    assert "regulated enterprise" in default_targeting_briefing_text().lower()
