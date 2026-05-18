"""North-star unify_narrative contract: schema, X2 targeting, allow-listed base facts, rubric."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

_MIN_JA = {
    "selected_jd_themes": ["synthetic theme"],
    "selected_briefing_themes": [],
    "targeting_rationale": "Synthetic rationale for tests.",
    "jd_used_as_proof": False,
    "briefing_used_as_proof": False,
    "targeting_only": True,
}


def _allow() -> set[str]:
    from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS

    return set(UNIFY_BULLET_IDS) | {"unify_narrative_base_001", "exp_unify_001"}


def test_base_resume_includes_north_star_role_narrative_for_gap_note_fixture() -> None:
    """Canonical base resume anchors north-star terms in exp_unify_001.role_narrative."""
    path = REPO / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    unify = None
    for emp in (doc.get("facts") or {}).get("employment") or []:
        if "unify" in str(emp.get("employer", "")).lower():
            unify = emp
            break
    assert unify is not None
    rn = str(unify.get("role_narrative") or "")
    for needle in (
        "platform roadmap",
        "core systems architecture",
        "commercialization",
        "Solution Accelerator",
        "consulting firm",
        "Fortune 500",
        "reusable IP",
    ):
        assert needle.lower() in rn.lower(), needle


def test_narrative_r0_requires_jd_alignment_targeting_fields() -> None:
    from apps_rg.runtime.dispatch.unify_ibm_pa_common import NARRATIVE_R0

    schema = json.loads(NARRATIVE_R0)
    ja = schema["properties"]["jd_alignment"]
    req = set(ja["required"])
    assert {"selected_jd_themes", "selected_briefing_themes", "targeting_rationale", "jd_used_as_proof", "briefing_used_as_proof"} <= req


def test_unify_narrative_x1d_rubric_mentions_north_star_alignment() -> None:
    from apps_rg.runtime.judges import unify_narrative_x1d as m

    assert "north_star_alignment" in m.NARRATIVE_RUBRIC.lower()


def test_x2_targeting_gate_fails_without_rationale() -> None:
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    bad_ja = {**_MIN_JA, "targeting_rationale": " \t "}
    led = [{"claim_text": "Led platform and commercialization.", "source_fact_ids": ["unify_narrative_base_001"]}]
    gates = run_unify_narrative_x2_gates(
        narrative_sentence="Led platform and commercialization at Unify Consulting.",
        parsed_output={"claim_ledger": led, "jd_alignment": bad_ja},
        claim_ledger=led,
        jd_text="jd text",
        briefing_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        x1d_judges=[],
        allowed_fact_ids=_allow(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert not by_id["x2_unify_narrative_targeting_inputs_used_but_not_proof"].pass_


def test_x2_targeting_gate_fails_jd_shaped_source_fact_id() -> None:
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    led = [{"claim_text": "Claim.", "source_fact_ids": ["jd_text"]}]
    gates = run_unify_narrative_x2_gates(
        narrative_sentence="One sentence only.",
        parsed_output={"claim_ledger": led, "jd_alignment": _MIN_JA},
        claim_ledger=led,
        jd_text="jd",
        briefing_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        x1d_judges=[],
        allowed_fact_ids=_allow(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert not by_id["x2_unify_narrative_targeting_inputs_used_but_not_proof"].pass_


def test_x2_bullet_label_gate_fails() -> None:
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    led = [{"claim_text": "x", "source_fact_ids": ["bul_unify_001"]}]
    gates = run_unify_narrative_x2_gates(
        narrative_sentence="Enterprise Agentic AI Platform Architecture is the focus.",
        parsed_output={"claim_ledger": led, "jd_alignment": _MIN_JA},
        claim_ledger=led,
        jd_text="jd",
        briefing_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        x1d_judges=[],
        allowed_fact_ids=_allow(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert not by_id["x2_no_bullet_label_repetition"].pass_


def test_x2_allows_unify_narrative_base_in_ledger() -> None:
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    led = [{"claim_text": "Capstone claim grounded in base anchor.", "source_fact_ids": ["unify_narrative_base_001"]}]
    gates = run_unify_narrative_x2_gates(
        narrative_sentence="Led roadmap and commercialization at Unify Consulting.",
        parsed_output={"claim_ledger": led, "jd_alignment": _MIN_JA},
        claim_ledger=led,
        jd_text="jd",
        briefing_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        x1d_judges=[],
        allowed_fact_ids=_allow(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_narrative_source_supported"].pass_


@pytest.mark.parametrize(
    "template_path",
    [REPO / "apps_rg" / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"],
)
def test_unify_narrative_yaml_word_budget_not_stale_250_cap(template_path: Path) -> None:
    text = template_path.read_text(encoding="utf-8")
    assert 'max_length: "250' not in text
    assert "58" in text and "360" in text
