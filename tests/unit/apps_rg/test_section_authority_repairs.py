"""Unit tests for section authority display repairs and X2 gate enumeration."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.sections.section_authority_repairs import (
    apply_exec_summary_display_authority_repairs,
    prune_competencies_rigor_failing_terms,
    repair_exec_summary_orphan_rows_with_unused_required_facts,
    sanitize_ibm_narrative_display_text,
    strip_exec_summary_credential_dump_sentences,
    strip_target_company_tailoring_sentences,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_no_credential_dump,
    check_exec_summary_meta_filler_patterns,
    check_exec_summary_paragraph_max_words,
    run_x2_gates,
)
from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates
from tests.unit.apps_rg.section_rigor.lane_registry import spec_for_lane


def test_strip_target_company_tailoring_removes_alignment_sentences() -> None:
    text = (
        "Engineering executive who builds governed agentic AI platforms for regulated workflows. "
        "He aligns with Acme Corp on enterprise architecture and innovation priorities. "
        "Platform lifecycle work ties architecture to commercial adoption and operating discipline."
    )
    repaired, removed = strip_target_company_tailoring_sentences(text, "Acme Corp")
    assert removed
    assert "acme corp" not in repaired.lower()
    assert "governed agentic ai" in repaired.lower()


def test_repair_orphan_rows_materializes_unused_required_fact() -> None:
    """Orphan ledger rows must cite unused required facts without fabricating prose."""
    orphan_bridge = (
        "That foundation informs data governance and AI strategy at scale."
    )
    text = (
        "Enterprise technology leader who unifies governed AI platforms for regulated enterprises. "
        "Designed and operationalized a governed agentic AI platform with deterministic routing. "
        f"{orphan_bridge} "
        "That regulatory foundation is grounded in FSA-chartered actuarial work in capital modeling. "
        "Directed large-scale regulatory IT transformations for major financial institutions. "
        "Software dependency graph intelligence enables accelerated legacy-system analysis."
    )
    facts = [
        {"fact_id": "fact_engineering_platform_001", "claim_text": "Governed agentic AI platform."},
        {
            "fact_id": "fact_engineering_platform_006",
            "claim_text": (
                "Platform commercialization generated $22M in IP-led revenue and expanded gross "
                "margins by 20%, while scaling the ML engineering organization from 8 to 28 specialists."
            ),
        },
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA-chartered actuarial work in capital modeling."},
        {"fact_id": "fact_consulting_001", "claim_text": "Directed large-scale regulatory IT transformations."},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Software dependency graph intelligence."},
        {"fact_id": "fact_exec_002", "claim_text": "Scaled ML engineering organization from 8 to 28."},
    ]
    parsed = {
        "resume_display_text": text,
        "claim_ledger": [
            {"claim_text": "a", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "b", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "c", "source_fact_ids": []},
            {"claim_text": "d", "source_fact_ids": ["fact_quant_hpc_003"]},
            {"claim_text": "e", "source_fact_ids": ["fact_consulting_001"]},
            {"claim_text": "f", "source_fact_ids": ["fact_engineering_platform_002", "fact_exec_002"]},
        ],
        "change_log": [],
    }
    allowed = {f["fact_id"] for f in facts}
    repairs = repair_exec_summary_orphan_rows_with_unused_required_facts(
        parsed,
        allowed_fact_ids=allowed,
        plan_facts=facts,
    )
    assert repairs
    assert parsed["claim_ledger"][2]["source_fact_ids"] == ["fact_engineering_platform_006"]
    assert "$22m" in str(parsed["resume_display_text"]).lower()
    assert orphan_bridge not in str(parsed["resume_display_text"])


def test_apply_authority_repairs_runs_orphan_repair_before_shape_check() -> None:
    text = (
        "Enterprise technology leader who unifies governed AI platforms for regulated enterprises. "
        "Designed and operationalized a governed agentic AI platform with deterministic routing. "
        "That foundation informs data governance and AI strategy at scale. "
        "That regulatory foundation is grounded in FSA-chartered actuarial work in capital modeling. "
        "Directed large-scale regulatory IT transformations for major financial institutions. "
        "Software dependency graph intelligence enables accelerated legacy-system analysis."
    )
    facts = [
        {"fact_id": "fact_engineering_platform_001", "claim_text": "Governed agentic AI platform."},
        {
            "fact_id": "fact_engineering_platform_006",
            "claim_text": (
                "Platform commercialization generated $22M in IP-led revenue and expanded gross "
                "margins by 20%, while scaling the ML engineering organization from 8 to 28 specialists."
            ),
        },
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA-chartered actuarial work in capital modeling."},
        {"fact_id": "fact_consulting_001", "claim_text": "Directed large-scale regulatory IT transformations."},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Software dependency graph intelligence."},
        {"fact_id": "fact_exec_002", "claim_text": "Scaled ML engineering organization from 8 to 28."},
    ]
    parsed = {
        "resume_display_text": text,
        "claim_ledger": [
            {"claim_text": "a", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "b", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "c", "source_fact_ids": []},
            {"claim_text": "d", "source_fact_ids": ["fact_quant_hpc_003"]},
            {"claim_text": "e", "source_fact_ids": ["fact_consulting_001"]},
            {"claim_text": "f", "source_fact_ids": ["fact_engineering_platform_002", "fact_exec_002"]},
        ],
        "change_log": [],
        "selected_fact_plan": {"facts": facts},
    }
    out = apply_exec_summary_display_authority_repairs(
        parsed,
        allowed_fact_ids={f["fact_id"] for f in facts},
        plan_facts=facts,
    )
    assert out["claim_ledger"][2]["source_fact_ids"] == ["fact_engineering_platform_006"]
    assert any(
        c.get("operation") == "repair_orphan_row_with_unused_required_fact"
        for c in out.get("change_log") or []
    )


def test_strip_credential_dump_removes_cert_sentence():
    text = (
        "Engineering executive who builds governed agentic AI platforms for regulated workflows. "
        "He designs platform operating systems that bind routing and orchestration into enterprise capability. "
        "He leads platform lifecycle work across architecture and engineering scale-out. "
        "AWS Certified Machine Learning Engineer, AWS Certified Solutions Architect, Databricks Lakehouse "
        "Fundamentals, and Fellow of the Society of Actuaries credentials reinforce senior IT strategy leadership."
    )
    repaired, removed = strip_exec_summary_credential_dump_sentences(text)
    assert removed
    ok, _ = check_exec_summary_no_credential_dump(repaired)
    assert ok is True


def test_exec_summary_authority_repairs_graph_only_fallback_on_bad_llm_shape() -> None:
    bad = (
        "This executive has extensive experience in designing governed agentic AI platforms. "
        "This expertise led to productization generating $22M in IP-led revenue. "
        "Additionally, Basel III/CCAR validation reduced reporting errors by 40%. "
        "The executive holds quantitative finance credentials including derivatives pricing."
    )
    facts = [
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": "Designed governed agentic AI platforms for regulated workflows.",
        },
        {
            "fact_id": "fact_engineering_platform_006",
            "claim_text": "Platform commercialization generated $22M in IP-led revenue.",
        },
        {"fact_id": "fact_governance_003", "claim_text": "Implemented Basel III/CCAR validation frameworks."},
        {"fact_id": "fact_exec_002", "claim_text": "Scaled ML engineering organization from 8 to 28."},
        {"fact_id": "fact_quant_hpc_001", "claim_text": "Delivered HPC quant pipelines for risk analytics."},
        {"fact_id": "fact_quant_hpc_003", "claim_text": "Applied stochastic calculus for derivatives pricing."},
        {"fact_id": "fact_partner_001", "claim_text": "Led joint GTM motions with cloud alliance partners."},
    ]
    parsed = {
        "resume_display_text": bad,
        "claim_ledger": [{"claim_text": "x", "source_fact_ids": ["fact_engineering_platform_001"]}],
        "change_log": [],
        "selected_fact_plan": {"facts": facts},
    }
    out = apply_exec_summary_display_authority_repairs(
        parsed,
        allowed_fact_ids={f["fact_id"] for f in facts},
        plan_facts=facts,
    )
    text = str(out["resume_display_text"])
    assert "this executive" not in text.lower()
    assert check_exec_summary_meta_filler_patterns(text)[0] is True
    assert check_exec_summary_paragraph_max_words(text, out)[0] is True
    assert any(
        c.get("operation") == "graph_only_display_authority_fallback" for c in out.get("change_log") or []
    )


def test_sanitize_ibm_meta_disclaimer():
    raw = (
        "At IBM, led enterprise-scale cloud foundations for regulated financial services, "
        "establishing reliability discipline without claiming IBM delivered modern agentic platform products."
    )
    cleaned, changed = sanitize_ibm_narrative_display_text(raw)
    assert changed is True
    assert "without claiming" not in cleaned.lower()


def test_sanitize_ibm_narrative_rewrites_forbidden_opener_and_adds_mechanism() -> None:
    raw = (
        "Led enterprise-scale cloud modernization, decision-support analytics, and AWS alliance co-sell programs "
        "for regulated financial clients at IBM, establishing governed delivery discipline and reusable platform "
        "architecture that accelerated partner-led adoption and joint revenue expansion."
    )
    cleaned, changed = sanitize_ibm_narrative_display_text(raw)
    assert changed is True
    assert cleaned.lower().startswith("drove")
    assert "runtime" in cleaned.lower()
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=cleaned,
        parsed_output={"narrative_sentence": cleaned, "jd_alignment": {"targeting_only": True}},
        claim_ledger=[{"claim_text": cleaned, "source_fact_ids": ["bul_ibm_001"]}],
        jd_text="enterprise modernization",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts="",
        allowed_fact_ids=["bul_ibm_001"],
        artifacts_dir=None,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_ibm_narrative_no_meta_disclaimer_in_display"].pass_ is True
    assert by_id["x2_narrative_technical_specificity_floor"].pass_ is True


def test_prune_low_rigor_competency_terms():
    parsed = {
        "competencies": [
            {
                "category_label": "ENGINEERING & PLATFORM COMPETENCIES",
                "terms": [
                    {"text": "data sales", "source_fact_id": "bul_unify_001", "source_fact_ids": ["bul_unify_001"]},
                    {
                        "text": "agentic platform orchestration",
                        "source_fact_id": "bul_unify_002",
                        "source_fact_ids": ["bul_unify_002"],
                    },
                ],
            }
        ],
        "change_log": [],
    }
    removed = prune_competencies_rigor_failing_terms(parsed)
    terms = [t["text"] for t in parsed["competencies"][0]["terms"]]
    assert "data sales" not in terms
    assert removed


def test_run_x2_gates_includes_rigor_critical_executive_summary_gates(tmp_path: Path):
    text = (
        "Engineering executive who builds governed agentic AI platforms for regulated enterprise workflows. "
        "The leader scales deterministic routing and orchestration across platform programs. "
        "Platform lifecycle work ties architecture to commercial adoption and operating discipline. "
        "Prior delivery outcomes stay grounded in selected executive facts only."
    )
    parsed = {
        "resume_display_text": text,
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
        "self_check": {"no_first_person": True},
        "input_payload_hash": "a" * 16,
        "output_payload_hash": "b" * 16,
    }
    (tmp_path / "prompt_selection_trace.json").write_text(
        '{"apps_rg_prompt_template_ref":"apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml",'
        '"compiler_template_id":"executive_summary.generate_scratch_v1"}',
        encoding="utf-8",
    )
    gates = run_x2_gates(
        resume_display_text=text,
        parsed_output=parsed,
        claim_ledger=[{"claim_text": "platform", "source_fact_ids": ["bul_unify_001"]}],
        text_claim_coverage={"sentences": [], "overall_pass": True},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Acme",
        jd_text="jd",
        temperature=0.4,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=True,
        artifacts_dir=tmp_path,
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        model_name="qwen-test",
        prompt_hash="c" * 16,
        compiled_prompt="x" * 32,
        raw_output='{"resume_display_text":"x"}',
        x1d_judges=[],
    )
    present = {g.gate_id for g in gates}
    crit = spec_for_lane("executive_summary").critical_gates
    c0 = {"x2_c0_metrics_artifact_present", "x2_c0_support_status_gate"}
    missing = sorted(g for g in crit if g not in present and g not in c0)
    assert not missing, f"missing rigor gates in run_x2_gates: {missing}"


def test_run_headline_x2_always_emits_text_claim_coverage_gate():
    from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates

    gates = run_headline_x2_gates(
        headline_line="SVP Engineering | Agentic Platforms | Cloud Scale | Governance",
        parsed_output={
            "headline_line": "SVP Engineering | Agentic Platforms | Cloud Scale | Governance",
            "claim_ledger": [
                {"claim_text": "Agentic Platforms", "source_fact_ids": ["bul_unify_001"]},
            ],
            "jd_alignment": {
                "targeting_only": True,
                "jd_used_as_proof": False,
                "briefing_used_as_proof": False,
                "companion_used_as_proof": False,
            },
        },
        claim_ledger=[{"claim_text": "Agentic Platforms", "source_fact_ids": ["bul_unify_001"]}],
        allowed_fact_ids={"bul_unify_001"},
        jd_text="",
        target_company="Acme",
        resume_support_blob="",
        employer_names_lower=[],
        runtime_generation_status="REAL_LLM",
        text_claim_coverage=None,
    )
    present = {g.gate_id for g in gates}
    assert "x2_headline_text_claim_coverage_integrity" in present
    cov_gate = next(g for g in gates if g.gate_id == "x2_headline_text_claim_coverage_integrity")
    assert cov_gate.pass_ is False


def test_run_ibm_narrative_x2_includes_meta_disclaimer_gate():
    narrative = "Led cloud and data foundations for regulated financial services at IBM."
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "jd_alignment": {"targeting_only": True}},
        claim_ledger=[{"claim_text": "cloud", "source_fact_ids": ["bul_ibm_001"]}],
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts=None,
        allowed_fact_ids=["bul_ibm_001"],
        artifacts_dir=None,
    )
    present = {g.gate_id for g in gates}
    assert "x2_ibm_narrative_no_meta_disclaimer_in_display" in present
    assert "x2_ibm_narrative_claim_ledger_clause_decomposition" in present
