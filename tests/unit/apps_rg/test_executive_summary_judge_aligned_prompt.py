"""Judge-aligned base prompt contracts (thesis-first generation, not slot-fill)."""

from __future__ import annotations

from pathlib import Path

from apps_rg.prompt_assembly.e0_examples import build_executive_summary_e0
from apps_rg.runtime.sections.executive_summary_pa import (
    compile_executive_summary_prompt,
    is_strategy_executive_target_title,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_executive_strategy_thesis,
    run_x2_gates,
)

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = (
    REPO / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
)


def _strategy_payload() -> dict:
    return {
        "run_id": "judge_aligned_prompt_run",
        "target_title": "SVP, IT Strategy & Innovation",
        "target_company": "Brown & Brown",
        "jd_text": "enterprise architecture innovation incubation",
        "briefing": "insurance brokerage IT strategy",
        "allowed_fact_ids": ["fact_engineering_platform_001", "fact_governance_003"],
        "proof_pool_metadata": {
            "proof_pool_type": "augmented_skills_graph",
            "graph_skills_proof_pool": True,
        },
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "fact_engineering_platform_001",
                    "claim_text": "Architected governed agentic AI platforms.",
                },
                {
                    "fact_id": "fact_governance_003",
                    "claim_text": "Implemented Basel III lineage frameworks.",
                },
            ],
        },
    }


def test_template_v15_judge_aligned_markers():
    raw = TEMPLATE.read_text(encoding="utf-8")
    assert "EXEC_SUMMARY_PROMPT_JUDGE_ALIGNED_V10" in raw
    assert "display_metric_weave_contract" in raw
    assert "leadership-first" in raw.lower()
    assert "claude_synthesis_pass_contract" not in raw
    assert "connective_variety_contract" not in raw
    assert "<third_person_voice_contract>" in raw
    assert "<six_sentence_period_contract>" in raw
    assert "proof-safe narrative order" not in raw
    assert "executive_strategy_thesis" in raw
    assert "judge_alignment_contract" in raw


def test_strategy_e0_single_svp_positive():
    e0 = build_executive_summary_e0(strategy_executive=True)
    assert e0.count("<positive_example ") == 1
    assert "exec_summary_pos_svp_it_strategy_001" in e0
    assert "$[X]M" in e0
    assert "[Y]%" in e0
    assert "exec_summary_neg_employer_inventory_001" in e0
    assert "exec_summary_neg_thin_s6_recap_001" in e0
    assert "exec_summary_neg_first_person_001" in e0


def test_strategy_compile_includes_thesis_and_narrative_arc_weights():
    payload = _strategy_payload()
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = "\n".join(str(m.get("content") or "") for m in out.artifact.messages)
    assert "executive_strategy_thesis" in content
    assert "LEADERSHIP_FIRST_EXEC_SUMMARY" in content
    assert "narrative_arc_weights" in content
    assert "TARGETING_CONCEPT_MAP" in content
    assert "must follow index order" not in content


def test_x2_executive_strategy_thesis_gate_strategy_lane_only():
    assert is_strategy_executive_target_title("SVP, IT Strategy & Innovation")
    ok, _ = check_executive_strategy_thesis(
        {
            "executive_strategy_thesis": (
                "Technology strategy executive aligning governed AI platforms and regulatory lineage "
                "into one enterprise IT direction for regulated programs."
            ),
        }
    )
    assert ok is True
    gates = run_x2_gates(
        resume_display_text="One. Two. Three. Four. Five. Six.",
        parsed_output={
            "executive_strategy_thesis": (
                "Technology strategy executive aligning governed AI platforms and regulatory lineage "
                "into one enterprise IT direction for regulated programs."
            ),
            "resume_display_text": "One. Two. Three. Four. Five. Six.",
            "claim_ledger": [{"claim_text": "c", "source_fact_ids": ["fact_engineering_platform_001"]}],
            "jd_alignment": {"jd_used_as_proof": False, "briefing_used_as_proof": False},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
            "text_claim_coverage": {"sentences": [], "overall_pass": True},
            "selected_fact_plan": {"facts": []},
        },
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["fact_engineering_platform_001"]}],
        text_claim_coverage={"sentences": [{"sentence_index": 1}], "overall_pass": True},
        allowed_fact_ids={"fact_engineering_platform_001", "fact_governance_003"},
        target_company="Brown",
        jd_text="jd",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        target_role="SVP, IT Strategy & Innovation",
    )
    ids = {g.gate_id for g in gates}
    assert "x2_executive_strategy_thesis_present" in ids
