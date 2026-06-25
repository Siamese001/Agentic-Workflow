"""InsurTech/EY JD-tailoring uplift: the role_episode prompt now injects the
bound graph skills + a JD-targeting block when role-episode bundles are attached,
instead of the legacy fact-only / "do not use JD" prompt. Identity stays locked.
"""
from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.sections.role_episode_lane import (
    _ROLE_LANES,
    _compiled_prompt,
    _role_episode_evidence_block,
)

_PAYLOAD_BASE = {
    "run_id": "test_run",
    "target_title": "VP Global Head of Agentic AI Solutions",
    "target_company": "AIG",
    "jd_text": "Lead enterprise agentic AI; regulated insurer; capital and risk modeling a plus.",
    "briefing": "Surface quantitative/actuarial depth.",
    "selected_fact_plan": {
        "facts": [{"fact_id": "bul_ey_003", "claim_text": "Directed a $15M regulatory analytics program."}]
    },
}

_BUNDLES = [
    {
        "role_episode_bundle_id": "reb_ey_capital_optimization_solvency",
        "bullet_intent": "actuarial/capital optimization leadership",
        "bound_skills": [
            {
                "skill_id": "skill_capital_regulatory_capital",
                "allowed_phrases": ["regulatory capital", "Basel", "CCAR"],
                "activation_status": "ACTIVE_CONFIRMED",
            },
            {
                "skill_id": "skill_capital_pricing_actuarial",
                "allowed_phrases": ["pricing of complex derivatives"],
                "activation_status": "DRAFT",
            },
        ],
    }
]


def _payload(*, with_bundles: bool) -> dict:
    p = dict(_PAYLOAD_BASE)
    ppm: dict = {}
    if with_bundles:
        ppm = {"role_episode_bundle_consumption": True, "role_episode_bundles": _BUNDLES}
    p["proof_pool_metadata"] = ppm
    return p


def test_targeted_prompt_injects_jd_and_graph_skills() -> None:
    prompt = _compiled_prompt(_ROLE_LANES["ey_bullets"], _payload(with_bundles=True))
    # JD targeting now present (was forbidden before)
    assert "TARGET_TITLE" in prompt
    assert "VP Global Head of Agentic AI Solutions" in prompt
    assert "Do not use JD or briefing as claim proof." not in prompt
    # graph-skill arsenal surfaced
    assert "GRAPH_SKILL_EVIDENCE" in prompt
    assert "regulatory capital" in prompt and "Basel" in prompt
    # proof contract intact: facts still the claim anchor
    assert "bul_ey_003" in prompt
    assert "jd_used_as_proof=false" in prompt
    assert "Bullets do the hard proof work" in prompt
    assert "each bullet must carry one evidence-bound achievement" in prompt


def test_activation_tiering_primary_vs_optional() -> None:
    block = _role_episode_evidence_block(_payload(with_bundles=True))
    primary_idx = block.index("primary_skills")
    optional_idx = block.index("optional_skills")
    # ACTIVE_CONFIRMED skill is foregrounded; DRAFT skill is optional
    assert block.index("skill_capital_regulatory_capital") > primary_idx
    assert block.index("skill_capital_regulatory_capital") < optional_idx
    assert block.index("skill_capital_pricing_actuarial") > optional_idx


def test_legacy_prompt_when_no_bundles() -> None:
    prompt = _compiled_prompt(_ROLE_LANES["ey_bullets"], _payload(with_bundles=False))
    # falls back to the legacy fact-only contract
    assert "Do not use JD or briefing as claim proof." in prompt
    assert "GRAPH_SKILL_EVIDENCE" not in prompt
    assert "TARGET_TITLE" not in prompt
    assert "Bullets do the hard proof work" in prompt


def test_evidence_block_empty_without_bundles() -> None:
    assert _role_episode_evidence_block(_payload(with_bundles=False)) == ""


def test_insurtech_and_ey_narrative_prompts_are_role_thesis_not_recap() -> None:
    for section_id in ("insurtech_narrative", "ey_narrative"):
        prompt = _compiled_prompt(_ROLE_LANES[section_id], _payload(with_bundles=True))
        assert "Narratives are the lightweight synthesis step above finalized bullets" in prompt
        assert "accepted bullet themes into one higher-level role thesis" in prompt
        assert "The narrative states why the role mattered; the bullets prove what was delivered." in prompt
        assert "not a recap of all three bullets" in prompt
        assert "claim_ledger remain the only proof authority" in prompt
        assert "jd_used_as_proof=false" in prompt


def test_insurtech_ey_templates_match_unify_ibm_methodology_contract() -> None:
    template_paths = [
        Path("apps_rg/prompt_assembly/templates/insurtech_bullets_tailor_v1.yaml"),
        Path("apps_rg/prompt_assembly/templates/ey_bullets_tailor_v1.yaml"),
        Path("apps_rg/prompt_assembly/templates/insurtech_narrative_v1.yaml"),
        Path("apps_rg/prompt_assembly/templates/ey_narrative_v1.yaml"),
    ]
    texts = {path.name: path.read_text(encoding="utf-8") for path in template_paths}

    for name in ("insurtech_bullets_tailor_v1.yaml", "ey_bullets_tailor_v1.yaml"):
        text = texts[name]
        assert "PROOF_HEAVY_BULLETS" in text
        assert "bullets_prove_what_was_delivered: true" in text
        assert "JD or briefing used as claim evidence" in text

    for name in ("insurtech_narrative_v1.yaml", "ey_narrative_v1.yaml"):
        text = texts[name]
        assert "ROLE_THESIS_NARRATIVE" in text
        assert "finalized_bullets_are_primary_synthesis_context: true" in text
        assert "companion bullets prove what was delivered" in text
        assert "three-bullet recap" in text
        assert "active_proof_pool_and_claim_ledger_only" in text
