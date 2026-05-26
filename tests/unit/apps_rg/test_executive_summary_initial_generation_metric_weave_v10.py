"""V10 initial-generation prompt: display metric weave (S3–S5) aligned with judge executive_signal."""

from __future__ import annotations

from pathlib import Path

from apps_rg.prompt_assembly.e0_examples import build_executive_summary_e0
from apps_rg.runtime.sections.executive_summary_composition import (
    build_executive_summary_composition_plan,
    format_composition_plan_for_pa,
)
from apps_rg.runtime.sections.executive_summary_generation_grade_contract import (
    generation_law_digest_text,
)
from apps_rg.runtime.sections.executive_summary_pa import (
    compile_executive_summary_prompt,
    load_executive_summary_template_slots,
)
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    SENTENCE_ARC_SVP_STRATEGY,
)

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = (
    REPO / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
)


def test_template_v10_metric_weave_slots():
    raw = TEMPLATE.read_text(encoding="utf-8")
    assert "EXEC_SUMMARY_PROMPT_JUDGE_ALIGNED_V10" in raw
    assert 'version: "2.0"' in raw
    assert "display_metric_weave_contract" in raw
    assert "material_metrics_surfaced_in_display_rows_3_4_5" in raw
    assert "not metric inventory coverage" not in raw


def test_svp_sentence_arc_requires_display_metrics():
    s3 = SENTENCE_ARC_SVP_STRATEGY[2]["guidance"]
    s4 = SENTENCE_ARC_SVP_STRATEGY[3]["guidance"]
    s5 = SENTENCE_ARC_SVP_STRATEGY[4]["guidance"]
    assert "$22M" in s3 or "22M" in s3
    assert "40%" in s4 or "reporting-error" in s4
    assert "imply quantitative rigor" not in s5
    assert "stress-testing" in s5 or "cycle-reduction" in s5


def test_strategy_compile_includes_display_ledger_parity_and_metric_weave():
    payload = {
        "run_id": "v10_metric_weave_run",
        "target_title": "SVP, IT Strategy & Innovation",
        "target_company": "Brown & Brown",
        "jd_text": "enterprise architecture innovation",
        "briefing": "insurance brokerage IT strategy",
        "allowed_fact_ids": [
            "fact_engineering_platform_006",
            "fact_governance_003",
            "fact_quant_hpc_001",
        ],
        "proof_pool_metadata": {
            "proof_pool_type": "augmented_skills_graph",
            "graph_skills_proof_pool": True,
        },
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "fact_engineering_platform_006",
                    "claim_text": "Productized platform services, $22M IP-led revenue, 20% margin.",
                },
                {
                    "fact_id": "fact_governance_003",
                    "claim_text": "Cut regulatory reporting errors by 40%.",
                },
                {
                    "fact_id": "fact_quant_hpc_001",
                    "claim_text": "Trimmed stress-testing cycles by 40%.",
                },
            ],
        },
    }
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = "\n".join(str(m.get("content") or "") for m in out.artifact.messages)
    assert "display_metric_weave_contract" in content
    assert "DISPLAY_LEDGER_PARITY" in content
    assert "material dollar/percent" in content.lower() or "dollar/percent" in content


def test_composition_plan_block_includes_display_ledger_parity():
    plan = build_executive_summary_composition_plan(
        selected_facts=[
            {"fact_id": "fact_engineering_platform_006", "claim_text": "$22M revenue."},
        ],
        allowed_fact_ids={"fact_engineering_platform_006"},
        target_role="SVP IT Strategy & Innovation",
        target_company="Brown & Brown",
        proof_pool_metadata={"graph_skills_proof_pool": True},
    )
    block = format_composition_plan_for_pa(plan)
    assert "DISPLAY_LEDGER_PARITY" in block


def test_generation_law_digest_mentions_display_metric_weave():
    digest = generation_law_digest_text()
    assert "Display metric weave" in digest or "display metric weave" in digest.lower()
    assert "ledger-only" in digest.lower()
