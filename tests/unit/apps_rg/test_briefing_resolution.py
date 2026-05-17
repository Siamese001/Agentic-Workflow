"""Unit tests for apps_rg.runtime.briefing_resolution."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from apps_rg.runtime.briefing_resolution import (
    BriefingResolutionError,
    BriefingSource,
    resolve_briefing_for_lanes,
)
from apps_rg.runtime.briefing_ssot import default_targeting_briefing_text


def test_resolve_default_ssot_when_ref_empty() -> None:
    r = resolve_briefing_for_lanes(briefing_artifact_ref=None)
    assert r.briefing_source == BriefingSource.DEFAULT_SSOT
    assert r.text == default_targeting_briefing_text()
    assert r.briefing_digest == hashlib.sha256(r.text.encode("utf-8")).hexdigest()
    assert "DEFAULT_SSOT" in r.ref_used


def test_require_run_specific_fails_closed() -> None:
    with pytest.raises(BriefingResolutionError, match="required briefing"):
        resolve_briefing_for_lanes(briefing_artifact_ref=None, require_run_specific=True)


def test_local_file_rejects_disallowed_suffix(tmp_path: Path) -> None:
    p = tmp_path / "x.exe"
    p.write_text("nope", encoding="utf-8")
    with pytest.raises(BriefingResolutionError, match="extension"):
        resolve_briefing_for_lanes(briefing_artifact_ref=str(p))


def test_local_file_rejects_missing_path(tmp_path: Path) -> None:
    missing = tmp_path / "nope.txt"
    with pytest.raises(BriefingResolutionError, match="does not exist"):
        resolve_briefing_for_lanes(briefing_artifact_ref=str(missing))


def test_inline_text_when_not_path_like() -> None:
    r = resolve_briefing_for_lanes(briefing_artifact_ref="plain briefing phrase")
    assert r.briefing_source == BriefingSource.RUN_SPECIFIC
    assert r.text == "plain briefing phrase"
    assert r.ref_used == "inline:text"
