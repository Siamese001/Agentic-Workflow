"""Unit tests for apps_rg.runtime.jd_resolution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from apps_rg.runtime.dispatch import competencies_dispatch
from apps_rg.runtime.jd_resolution import (
    JdResolutionError,
    JdSource,
    default_jd_targeting_text,
    resolve_jd_for_lanes,
)


def test_resolve_default_ssot_when_all_empty() -> None:
    r = resolve_jd_for_lanes()
    assert r.jd_source == JdSource.DEFAULT_SSOT
    assert r.description == default_jd_targeting_text()
    assert r.jd_digest
    assert "DEFAULT_SSOT" in r.ref_used


def test_require_run_specific_fails_closed() -> None:
    with pytest.raises(JdResolutionError, match="required job description"):
        resolve_jd_for_lanes(require_run_specific=True)


def test_inline_job_description_text() -> None:
    r = resolve_jd_for_lanes(
        job_description_text="Build scalable retrieval for our platform.",
        target_company="Acme",
        target_role="Staff Engineer",
    )
    assert r.jd_source == JdSource.RUN_SPECIFIC
    assert r.description == "Build scalable retrieval for our platform."
    assert r.ref_used == "inline:job_description_text"
    assert r.company == "Acme"
    assert r.title == "Staff Engineer"
    assert r.jd_digest


def test_ref_only_loads_file(tmp_path: Path) -> None:
    jd = tmp_path / "posting.md"
    jd.write_text("Own the ML platform roadmap.\n", encoding="utf-8")
    r = resolve_jd_for_lanes(
        job_description_ref=str(jd),
        target_company="Co",
        target_role="MLE",
    )
    assert r.jd_source == JdSource.RUN_SPECIFIC
    assert "roadmap" in r.description
    assert r.jd_digest == _expected_digest(r.title, r.description, r.company)


def test_json_title_description_company() -> None:
    blob = json.dumps(
        {
            "title": "Director, Platform",
            "description": "Lead agentic systems.",
            "company": "Contoso Ltd",
        }
    )
    r = resolve_jd_for_lanes(
        job_description_text=blob,
        target_company="Ignored Co",
        target_role="VP",
    )
    assert r.title == "Director, Platform"
    assert r.description == "Lead agentic systems."
    assert r.company == "Contoso Ltd"
    expect = hashlib.sha256(
        json.dumps(
            {"title": r.title, "description": r.description, "company": r.company},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    assert r.jd_digest == expect


def test_inline_text_wins_over_ref(tmp_path: Path) -> None:
    f = tmp_path / "jd.txt"
    f.write_text("from file", encoding="utf-8")
    r = resolve_jd_for_lanes(
        job_description_ref=str(f),
        job_description_text="from inline",
        target_company="",
        target_role="Role",
    )
    assert r.description == "from inline"
    assert r.ref_used == "inline:job_description_text"


def test_jd_data_fallback_when_no_inline_or_ref() -> None:
    r = resolve_jd_for_lanes(
        jd_data="Plain JD paragraph without JSON.",
        target_company="Acme",
        target_role="Eng",
    )
    assert r.jd_source == JdSource.RUN_SPECIFIC
    assert "without JSON" in r.description
    assert r.ref_used == "inline:jd_data"


def test_dispatch_default_hint_matches_ssot() -> None:
    assert competencies_dispatch.JD_TEXT_DEFAULT == default_jd_targeting_text()


def test_no_legacy_jd_hint_literal_in_dispatch_modules() -> None:
    needle = (
        "LLMOps, retrieval, production reliability, engineering leadership"
    )
    root = Path(competencies_dispatch.__file__).resolve().parent
    offenders = [p for p in root.glob("*.py") if needle in p.read_text(encoding="utf-8")]
    assert not offenders, f"legacy embedded JD hint found in: {offenders}"


def _expected_digest(title: str, description: str, company: str) -> str:
    blob = json.dumps(
        {"title": title, "description": description, "company": company},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
