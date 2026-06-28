"""Prompt/X2 SSOT alignment: executive summary exactly six sentences; no legacy bands."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_jd_alignment_proof_flags,
    check_exec_summary_sentence_count_6,
)

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = (
    REPO / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
)
PA_SLOTS = REPO / "apps_rg" / "prompt_assembly" / "templates" / "competency_selector_v2.pa_slots.yaml"


_LEGACY_DEFAULT_PATTERNS = (
    re.compile(r"2–3\s+dense\s+sentences\s+by\s+default", re.I),
    re.compile(r"default\s+2\s+or\s+3\s+sentences", re.I),
    re.compile(r"2–3\s+sentences\s+\(sovereign", re.I),
    re.compile(r"Hold to\s+2\s+or\s+3\s+sentences", re.I),
)


def test_executive_summary_template_rejects_legacy_2_3_default_band():
    raw = TEMPLATE.read_text(encoding="utf-8")
    for pat in _LEGACY_DEFAULT_PATTERNS:
        assert pat.search(raw) is None, f"legacy 2-3 default still present: {pat.pattern}"
    assert "exactly 6" in raw.lower() or "6 period-delimited" in raw.lower()
    assert "legacy" in raw.lower()


def test_competency_pa_slots_category_band_matches_x2():
    """Competency pa_slots must state the adaptive category band the X2 rigor SSOT enforces."""
    from apps_rg.runtime.sections.competencies_rigor import (
        MAX_CATEGORY_COUNT,
        MIN_CATEGORY_COUNT,
    )

    assert MIN_CATEGORY_COUNT == 6
    assert MAX_CATEGORY_COUNT == 8
    raw = PA_SLOTS.read_text(encoding="utf-8")
    assert "6-8" in raw or "6 to 8" in raw or "6–8" in raw
    assert "exactly 8" not in raw.lower()


def _jd_alignment_fixture() -> dict:
    return {
        "targeting_only": True,
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "companion_context_used_as_proof": False,
        "graph_targeting": {
            "projection_source": "sqlite_role_family_projection",
            "sqlite_projection_row_found": True,
            "fallback_pillar_bridge_used": False,
            "release_eligible_targeting_proof": True,
            "targeting_degraded_explicit": False,
        },
    }


def test_x2_jd_alignment_proof_flags_require_explicit_false_booleans():
    ok, _ = check_exec_summary_jd_alignment_proof_flags(
        {"jd_alignment": _jd_alignment_fixture()}
    )
    assert ok is True
    bad, reason = check_exec_summary_jd_alignment_proof_flags(
        {"jd_alignment": {"targeting_only": True, "jd_used_as_proof": False}}
    )
    assert bad is False
    assert reason is not None


def test_lane_registry_exec_summary_critical_gates_include_proof_flags():
    from tests.unit.apps_rg.section_rigor.lane_registry import spec_for_lane

    spec = spec_for_lane("executive_summary")
    assert "x2_exec_summary_sentence_count_6" in spec.critical_gates
    assert "x2_exec_summary_jd_alignment_proof_flags" in spec.critical_gates


@pytest.mark.parametrize(
    "text,expect_pass",
    [
        (
            "One. Two. Three. Four. Five. Six.",
            True,
        ),
        (
            "One. Two. Three. Four. Five.",
            False,
        ),
        (
            "One. Two.",
            False,
        ),
    ],
)
def test_sentence_count_gates(text: str, expect_pass: bool):
    ok, _ = check_exec_summary_sentence_count_6(text)
    assert ok is expect_pass
