"""Modular lane argv derives JD title, description, and briefing from L2 recipe context."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.l2_recipe.modular_lane_adapter import (
    ModularLaneTargeting,
    build_modular_lane_argv,
    modular_lane_targeting_from_recipe_context,
)
from apps_rg.runtime.briefing_resolution import BriefingSource
from apps_rg.runtime.briefing_ssot import default_targeting_briefing_text
from apps_rg.runtime.jd_resolution import JdSource


def test_modular_lane_targeting_parses_jd_data_json() -> None:
    jd = {"title": "Director, AI Platform", "description": "Lead agentic systems and governance."}
    ctx = {
        "target_company": "Acme Corp",
        "target_role": "VP Engineering",
        "jd_data": json.dumps(jd),
        "manual_brief": "",
    }
    t = modular_lane_targeting_from_recipe_context(ctx)
    assert t.target_company == "Acme Corp"
    assert t.target_title == "Director, AI Platform"
    assert "agentic systems" in t.jd_text
    assert t.jd_source == JdSource.RUN_SPECIFIC.value
    assert t.jd_digest
    assert t.jd_ref_used == "inline:jd_data"
    assert t.briefing_text == default_targeting_briefing_text()
    assert t.briefing_source == BriefingSource.DEFAULT_SSOT.value
    assert t.briefing_digest
    assert "DEFAULT_SSOT" in t.briefing_ref_used


def test_build_modular_lane_argv_includes_targeting_flags() -> None:
    tgt = ModularLaneTargeting(
        target_company="Acme Corp",
        target_title="Director, AI Platform",
        jd_text="Do the thing.",
        briefing_text="Culture note.",
    )
    argv = build_modular_lane_argv(provider="external_claude", targeting=tgt)
    assert argv[:4] == [
        "--provider",
        "external_claude",
        "--allow-non-allow-exit-zero",
        "--target-company",
    ]
    assert argv[argv.index("--target-company") + 1] == "Acme Corp"
    assert argv[argv.index("--jd-text") + 1] == "Do the thing."
    assert argv[argv.index("--briefing") + 1] == "Culture note."


def test_build_modular_lane_argv_rejects_retired_retired_provider_provider() -> None:
    with pytest.raises(ValueError, match="Unsupported modular lane provider"):
        build_modular_lane_argv(provider="retired_provider_profile", targeting=None)


def test_modular_lane_targeting_loads_manual_brief_file(tmp_path: Path) -> None:
    brief_path = tmp_path / "brief.md"
    brief_path.write_text("Strategic priorities for this quarter.\n", encoding="utf-8")
    ctx = {
        "target_company": "Acme Corp",
        "target_role": "VP Engineering",
        "jd_data": "",
        "manual_brief": str(brief_path),
    }
    t = modular_lane_targeting_from_recipe_context(ctx)
    assert "Strategic priorities" in t.briefing_text
    assert t.briefing_source == BriefingSource.RUN_SPECIFIC.value
    assert t.briefing_ref_used


def test_modular_lane_targeting_job_description_ref_file(tmp_path: Path) -> None:
    jd_path = tmp_path / "role.txt"
    jd_path.write_text("Own reliability for the inference stack.\n", encoding="utf-8")
    ctx = {
        "target_company": "Acme Corp",
        "target_role": "VP Engineering",
        "jd_data": "",
        "job_description_ref": str(jd_path),
        "job_description_text": "",
        "manual_brief": "",
    }
    t = modular_lane_targeting_from_recipe_context(ctx)
    assert "inference stack" in t.jd_text
    assert t.jd_source == JdSource.RUN_SPECIFIC.value
    assert t.jd_digest
    assert jd_path.resolve().as_posix() in t.jd_ref_used or str(jd_path) in t.jd_ref_used


def test_modular_lane_targeting_briefing_artifact_ref_alias(tmp_path: Path) -> None:
    brief_path = tmp_path / "via_ref.txt"
    brief_path.write_text("From briefing_artifact_ref key.\n", encoding="utf-8")
    ctx = {
        "target_company": "Acme Corp",
        "target_role": "VP Engineering",
        "jd_data": "",
        "briefing_artifact_ref": str(brief_path),
    }
    t = modular_lane_targeting_from_recipe_context(ctx)
    assert "From briefing_artifact_ref" in t.briefing_text
    assert t.briefing_source == BriefingSource.RUN_SPECIFIC.value
