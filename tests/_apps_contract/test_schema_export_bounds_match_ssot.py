"""JSON schema export caps align with section_product_shape_export_bounds."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.sections.section_product_shape_export_bounds import (
    EXEC_SUMMARY_EXPORT_MAX_CHARS,
    EXEC_SUMMARY_EXPORT_MAX_WORDS,
    RG_BULLET_MAX_CHARS,
    RG_HEADLINE_MAX_CHARS,
    RG_ROLE_NARRATIVE_MAX_CHARS,
)


def _schema() -> dict:
    path = Path(__file__).resolve().parents[2] / "apps_rg" / "rg_output_schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_schema_headline_max_length_matches_ssot() -> None:
    props = _schema()["properties"]
    assert props["headline_line"]["maxLength"] == RG_HEADLINE_MAX_CHARS


def test_schema_summary_bounds_match_ssot() -> None:
    summary = _schema()["properties"]["sections"]["properties"]["summary"]["properties"]
    assert summary["word_count"]["maximum"] == EXEC_SUMMARY_EXPORT_MAX_WORDS
    assert summary["text"]["maxLength"] == EXEC_SUMMARY_EXPORT_MAX_CHARS


def test_schema_role_narrative_max_length_matches_ssot() -> None:
    exp = _schema()["properties"]["sections"]["properties"]["experience"]["items"]["allOf"][0]
    assert exp["properties"]["role_narrative"]["maxLength"] == RG_ROLE_NARRATIVE_MAX_CHARS


def test_schema_bullet_max_length_matches_export() -> None:
    exp = _schema()["properties"]["sections"]["properties"]["experience"]["items"]["allOf"][0]
    bullet = exp["properties"]["bullets"]["items"]["properties"]["text"]
    assert bullet["maxLength"] == RG_BULLET_MAX_CHARS
