"""Prompt↔gate consistency for narrative openers (typed-edge guardrails, W2.3).

A narrative PA prompt MUST NOT *suggest* an opener that the deterministic
``check_narrative_forbidden_opener`` gate forbids. The unify_narrative prompt previously
recommended "Scaled" and "Productized" as substantive openers while the gate's
``EXEC_SUMMARY_MECHANICAL_OPENERS`` set forbids both — so the model followed the prompt and
the lane blocked at X3 on ``x2_unify_narrative_forbidden_opener`` ("Productized"). This guards
the whole class: any future PA prompt that suggests a forbidden opener fails here.
"""
from __future__ import annotations

import re
from pathlib import Path

from apps_rg.runtime.judges.ibm_narrative_x1d import NARRATIVE_RUBRIC as IBM_NARRATIVE_RUBRIC
from apps_rg.runtime.judges.unify_narrative_x1d import NARRATIVE_RUBRIC
from apps_rg.runtime.sections import ibm_narrative_pa, unify_narrative_pa
from apps_rg.runtime.validators.narrative_mechanical_x2 import EXEC_SUMMARY_MECHANICAL_OPENERS
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

_FORBIDDEN = {w.lower() for w in EXEC_SUMMARY_MECHANICAL_OPENERS}


def _suggested_openers(source_text: str) -> set[str]:
    """Capitalized opener words in any 'openers instead:' / 'prefer ...' suggestion clause."""
    suggested: set[str] = set()
    for m in re.finditer(r"(?:openers instead:|prefer)\s*([^.\n]*)", source_text, re.IGNORECASE):
        suggested.update(w.lower() for w in re.findall(r"\b[A-Z][a-z]+\b", m.group(1)))
    return suggested


def test_narrative_pa_prompts_do_not_suggest_forbidden_openers() -> None:
    for module in (unify_narrative_pa, ibm_narrative_pa):
        text = Path(module.__file__).read_text(encoding="utf-8")
        suggested = _suggested_openers(text)
        assert suggested, f"{Path(module.__file__).name}: no suggested-opener clause found"
        bad = sorted(suggested & _FORBIDDEN)
        assert not bad, (
            f"{Path(module.__file__).name} suggests gate-forbidden opener(s): {bad} "
            f"(forbidden set: {sorted(_FORBIDDEN)})"
        )


def test_ibm_narrative_pa_names_deterministic_gate_ids() -> None:
    text = Path(ibm_narrative_pa.__file__).read_text(encoding="utf-8")
    assert "x2_ibm_narrative_forbidden_opener" in text
    assert "x2_narrative_technical_specificity_floor" in text


def test_unify_narrative_pa_is_companion_bullet_synthesis_step() -> None:
    text = Path(unify_narrative_pa.__file__).read_text(encoding="utf-8")
    assert "lightweight synthesis step" in text
    assert "role thesis" in text
    assert "The narrative states why the role mattered; the bullets prove what was delivered." in text
    assert "finalized bullets already carry the hard proof work" in text
    assert '"partner co-sell motions"' in text
    assert "partner-channel enablement" in text
    assert "not bullet recap" not in text


def test_unify_narrative_template_matches_product_quality_dependency_design() -> None:
    template = Path("apps_rg/prompt_assembly/templates/unify_position_narrative_v1.yaml").read_text(
        encoding="utf-8"
    )
    assert "primary synthesis context" in template
    assert "C0 remains proof/provenance" in template
    assert "x3_disposition X3_ALLOW evidence" not in template
    assert "provider-quota judge blocks do not invalidate narrative dependency" in template
    assert "Do not reuse companion four-grams" in template
    assert "partner co-sell motions" in template
    assert "read-only anti-repetition context" not in template


def test_unify_narrative_judge_rubric_enforces_thesis_not_sideways_spin() -> None:
    assert "executive thesis" in NARRATIVE_RUBRIC
    assert "bullets prove" in NARRATIVE_RUBRIC
    assert "spins a different role story not entailed" in NARRATIVE_RUBRIC
    assert "comma-packed mechanism list" in NARRATIVE_RUBRIC


def test_ibm_narrative_pa_is_companion_bullet_synthesis_step() -> None:
    text = Path(ibm_narrative_pa.__file__).read_text(encoding="utf-8")
    assert "lightweight synthesis step" in text
    assert "role thesis" in text
    assert "The narrative states why the role mattered; the bullets prove what was delivered." in text
    assert "finalized bullets already carry the hard proof work" in text
    assert "primary synthesis context" in text
    assert "comma-packed mechanism list" in text
    assert "Do not enumerate four" in text
    assert "Drove <family-A> and <family-B> programs" not in text


def test_ibm_narrative_template_matches_product_quality_dependency_design() -> None:
    template = Path("apps_rg/prompt_assembly/templates/ibm_position_narrative_v1.yaml").read_text(
        encoding="utf-8"
    )
    assert "primary synthesis context" in template
    assert "C0 remains proof/provenance" in template
    assert "x3_disposition X3_ALLOW evidence" not in template
    assert "provider-quota judge blocks do not invalidate narrative dependency" in template
    assert "read-only anti-repetition context" not in template.lower()
    assert "The narrative states why the IBM role" in template
    assert "Drove governed AWS reference-architecture work" in template
    assert "Mechanical recap of companion bullet topics" in template


def test_ibm_narrative_judge_rubric_enforces_thesis_not_sideways_spin() -> None:
    assert "executive thesis" in IBM_NARRATIVE_RUBRIC
    assert "bullets prove" in IBM_NARRATIVE_RUBRIC
    assert "spins a different role story not entailed" in IBM_NARRATIVE_RUBRIC
    assert "comma-packed mechanism list" in IBM_NARRATIVE_RUBRIC


def test_clean_unify_role_thesis_sentence_passes_shape_gates() -> None:
    narrative = (
        "Owned the mandate to turn Unify Consulting's governed agentic AI platform into reusable "
        "commercial infrastructure, connecting control-plane architecture and partner enablement "
        "to regulated-enterprise adoption."
    )
    companion = "\n".join(
        [
            "- bul_unify_001: Owned governed agentic systems architecture for enterprise AI workflows, using L0 route-policy dispatch and replayable runtime traceability to keep execution policy-gated and auditable.",
            "- bul_unify_002: Built partner co-sell motions around reusable AI platform services, packaging enablement assets that supported indirect adoption and solution commercialization.",
            "- bul_unify_003: Drove CFO-aligned enterprise adoption motions by tying consumption and renewal signals to reusable AI platform commercialization.",
            "- bul_unify_004: Standardized the AI systems lifecycle from intake through production monitoring, compressing lab-to-production cycle time from six months to three weeks.",
            "- bul_unify_005: Architected cloud data/runtime integration patterns across Databricks, vector services, and API gateways to support high-availability distributed service patterns for enterprise AI platforms.",
            "- bul_unify_006: Scaled platform commercialization from reusable AI services, growing IP-led revenue to $22M while expanding gross margin by 20% and scaling the engineering team from 8 to 28.",
        ]
    )
    claim_ledger = [
        {
            "claim_text": "Governed agentic AI platform control-plane ownership for enterprise workflows.",
            "source_fact_ids": [
                "reb_unify_agentic_platform_architecture",
                "metric_unify_policy_gated_agent_execution_surface",
            ],
        },
        {
            "claim_text": "Partner co-sell enablement around reusable AI platform services.",
            "source_fact_ids": [
                "reb_unify_partner_channel_cosell",
                "metric_unify_partner_enablement_asset_set",
            ],
        },
    ]
    parsed = {
        "narrative_sentence": narrative,
        "claim_ledger": claim_ledger,
        "jd_alignment": {
            "selected_jd_themes": ["partner-led enterprise AI deployment"],
            "selected_briefing_themes": ["repeatable partner execution"],
            "targeting_rationale": "Targeting only.",
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
        "text_claim_coverage": {"overall_pass": True},
    }
    allowed = {
        "reb_unify_agentic_platform_architecture",
        "metric_unify_policy_gated_agent_execution_surface",
        "reb_unify_partner_channel_cosell",
        "metric_unify_partner_enablement_asset_set",
    }
    gates = run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output=parsed,
        claim_ledger=claim_ledger,
        jd_text="partner-led enterprise AI deployment",
        briefing_text="repeatable partner execution",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=companion,
        companion_bullets_status="ACCEPTED_FINALIZED",
        companion_bullets_reason="ok",
        provider_requested="external_openai",
        provider_attempted="external_openai",
        x1d_judges=[
            {
                "provider_key": "gemini_pro",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "score": 5.0,
                "threshold": 4.0,
                "pass": True,
            }
        ],
        allowed_fact_ids=allowed,
        proof_pool_metadata={"proof_pool_type": "selected_role_fact_set"},
    )
    by_id = {g.gate_id: g for g in gates}
    for gate_id in (
        "x2_unify_narrative_exactly_one_sentence",
        "x2_no_six_bullet_summary",
        "x2_no_companion_ngram_copy",
        "x2_unify_narrative_word_budget",
        "x2_narrative_not_bullet_recap",
        "x2_narrative_technical_specificity_floor",
    ):
        assert by_id[gate_id].pass_, gate_id
