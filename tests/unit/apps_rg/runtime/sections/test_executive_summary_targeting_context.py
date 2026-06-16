"""Freeze-stage targeting bundle for executive_summary."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.sections.executive_summary_briefing import prepare_briefing_for_executive_summary
from apps_rg.runtime.sections.executive_summary_targeting_context import (
    freeze_executive_summary_targeting_context,
)
from apps_rg.runtime.targeting_context_authority import (
    frozen_briefing_text,
    frozen_jd_text,
    require_material_targeting_bundle,
)

REPO = Path(__file__).resolve().parents[5]


@pytest.fixture
def brown_material() -> tuple[str, str]:
    jd = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt").read_text(
        encoding="utf-8"
    )
    brief = (
        REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
    ).read_text(encoding="utf-8")
    return jd, brief


def test_freeze_stores_material_targeting_bundle(brown_material: tuple[str, str]) -> None:
    jd, brief = brown_material
    selected, _ = prepare_briefing_for_executive_summary(
        brief,
        role_family_key="INSURANCE_BROKERAGE_IT_INNOVATION",
    )
    payload = {
        "jd_text": jd,
        "briefing": selected,
        "target_title": "SVP",
        "target_company": "Brown & Brown",
    }
    receipt = freeze_executive_summary_targeting_context(payload)
    assert receipt["targeting_context_frozen"] is True
    bundle = require_material_targeting_bundle(payload)
    assert frozen_jd_text(payload) == bundle.jd_text_frozen
    assert frozen_briefing_text(payload) == bundle.briefing_text_frozen
    assert receipt["bundle_digest"] == bundle.bundle_digest


def test_insurance_briefing_selection_keeps_compact_brown_ssot_whole(brown_material: tuple[str, str]) -> None:
    _jd, brief = brown_material
    selected, receipt = prepare_briefing_for_executive_summary(
        brief,
        role_family_key="INSURANCE_BROKERAGE_IT_INNOVATION",
    )
    included = receipt.get("included_section_ids") or []
    assert included == ["full_document"]
    assert selected == brief
    assert "integration" in selected.lower()
