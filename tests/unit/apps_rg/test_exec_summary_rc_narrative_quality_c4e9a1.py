"""Unit tests for plan exec-summary-rc-narrative-quality-c4e9a1 (RC-H through RC-K)."""

from __future__ import annotations

from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
    _flags_display_metric_echo_only,
    _sanitize_deprecated_commercialization_thread,
    _sanitize_unsupported_percent_tokens,
    _sanitize_unsupported_style_metric_echoes,
    apply_graph_only_generation_quality_repair,
)
from apps_rg.runtime.sections.executive_summary_voice_repair import (
    ensure_required_allowed_fact_utilization,
    polish_executive_summary_judge_alignment,
)
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    FACT_C0_DISPLAY_OVERRIDES,
    FSA_CREDENTIAL_FACT_ID,
    SENTENCE_ARC_SVP_STRATEGY,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_display_override_compliance,
    check_exec_summary_no_sentence_fragment,
    check_exec_summary_strategy_no_commercialization_thread,
)


def test_s3_guidance_no_literal_22m_or_20_percent() -> None:
    guidance = SENTENCE_ARC_SVP_STRATEGY[2]["guidance"].lower()
    assert "$22m" not in guidance
    assert "20%" not in guidance
    assert "metric_raw" in guidance


def test_fsa_display_override_has_strategic_connector() -> None:
    text = FACT_C0_DISPLAY_OVERRIDES[FSA_CREDENTIAL_FACT_ID]
    # Opener must be a strategic "That <noun>" connector. Avoid "governance discipline"
    # because EXEC_SUMMARY_FORBIDDEN_META_PHRASES bans it as meta-filler scaffolding,
    # which would trigger synthesis regen and strip the anchor on re-attempt.
    assert text.lower().startswith("that regulatory foundation"), (
        "Override opener must avoid the forbidden meta-filler phrase 'governance discipline' "
        "to keep RetiredProvider synthesis from getting rejected on attempt 1 and dropping the X2 anchor."
    )
    assert "governance discipline" not in text.lower()
    assert "informing data governance" in text.lower()


def test_fsa_display_override_is_complete_sentence() -> None:
    ok, reason = check_exec_summary_no_sentence_fragment(
        FACT_C0_DISPLAY_OVERRIDES[FSA_CREDENTIAL_FACT_ID]
    )
    assert ok, reason


def test_flags_display_metric_echo_only() -> None:
    assert _flags_display_metric_echo_only({"unsupported_percent_tokens": ["20%"]}) is True
    assert (
        _flags_display_metric_echo_only(
            {
                "unsupported_percent_tokens": ["20%"],
                "had_unsupported_gross_margin": True,
            }
        )
        is True
    )
    assert (
        _flags_display_metric_echo_only(
            {
                "unsupported_percent_tokens": ["20%"],
                "mechanical_opener_stack": True,
            }
        )
        is False
    )


def test_sanitize_unsupported_percent_preserves_connective_opener() -> None:
    before = (
        "Enterprise technology leader who aligns governed AI platforms. "
        "Building on that foundation, supply-chain modernization generated $22M "
        "in efficiency capture and expanded operating margins by 20% while growing the team."
    )
    after = _sanitize_unsupported_percent_tokens(before, ["20%"])
    assert "building on that foundation" in after.lower()
    assert "20%" not in after


def test_sanitize_style_metric_echoes_strips_22m_when_unsupported() -> None:
    resume = (
        "Technology leader aligning platforms. "
        "Building on that foundation, modernization generated $22M in revenue."
    )
    facts = [{"fact_id": "fact_governance_003", "claim_text": "Cut errors by 40%"}]
    cleaned = _sanitize_unsupported_style_metric_echoes(resume, plan_facts=facts)
    assert "$22m" not in cleaned.lower()
    assert "building on that foundation" in cleaned.lower()


def test_apply_repair_percent_sanitize_only_skips_full_rewrite() -> None:
    allowed = {
        "fact_engineering_platform_001",
        "fact_governance_003",
        "fact_governance_003_metric_e5abeb74",
        "fact_exec_002",
    }
    parsed = {
        "resume_display_text": (
            "Technology strategy executive who aligns enterprise IT direction. "
            "Through that operating model, platform work cut regulatory reporting errors by 40%. "
            "In parallel, the ML engineering organization grew from 8 to 28 specialists. "
            "That governance discipline is grounded in quantitative rigor established through "
            "FSA-chartered actuarial work in capital modeling and portfolio stress analytics. "
            "Against that delivery foundation, large-scale regulatory IT transformations advanced "
            "legacy-modernization programs for major institutions. "
            "Software dependency graph intelligence enables accelerated legacy-system analysis."
        ),
        "claim_ledger": [
            {"claim_text": "x", "source_fact_ids": ["fact_governance_003"]},
            {"claim_text": "y", "source_fact_ids": ["fact_exec_002"]},
            {"claim_text": "z", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "a", "source_fact_ids": ["fact_quant_hpc_003"]},
            {"claim_text": "b", "source_fact_ids": ["fact_consulting_001"]},
            {"claim_text": "c", "source_fact_ids": ["fact_engineering_platform_002"]},
        ],
    }
    # Inject unsupported 20% in one sentence only
    parsed["resume_display_text"] = parsed["resume_display_text"].replace(
        "by 40%", "by 40% and expanded margins by 20%"
    )
    plan_facts = [
        {"fact_id": "fact_governance_003", "claim_text": "Cut errors by 40%", "metric_raw": "40%"},
        {"fact_id": "fact_exec_002", "claim_text": "Scaled team 8 to 28", "metric_raw": "8 to 28"},
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": "Governed agentic AI platform",
        },
    ]
    repaired, meta = apply_graph_only_generation_quality_repair(
        parsed,
        allowed_fact_ids=allowed,
        plan_facts=plan_facts,
    )
    assert meta.get("repair_kind") == "display_metric_echo_sanitize_only"
    assert "20%" not in str(repaired.get("resume_display_text") or "")
    assert "through that operating model" in str(repaired.get("resume_display_text") or "").lower()


def test_display_override_compliance_passes_with_anchor() -> None:
    override = FACT_C0_DISPLAY_OVERRIDES[FSA_CREDENTIAL_FACT_ID]
    ok, reason = check_exec_summary_display_override_compliance(
        override,
        [{"claim_text": "x", "source_fact_ids": [FSA_CREDENTIAL_FACT_ID]}],
    )
    assert ok, reason


def test_display_override_compliance_fails_without_anchor() -> None:
    ok, reason = check_exec_summary_display_override_compliance(
        "Established quantitative rigor through FSA work only.",
        [{"claim_text": "x", "source_fact_ids": [FSA_CREDENTIAL_FACT_ID]}],
    )
    assert not ok
    assert reason and "DISPLAY_OVERRIDE" in reason


def test_display_override_compliance_allows_regulator_foundation_paraphrase() -> None:
    override = FACT_C0_DISPLAY_OVERRIDES[FSA_CREDENTIAL_FACT_ID]
    paraphrase = override.replace("governance discipline", "regulatory foundation")
    ok, reason = check_exec_summary_display_override_compliance(
        paraphrase,
        [{"claim_text": "x", "source_fact_ids": [FSA_CREDENTIAL_FACT_ID]}],
    )
    assert ok, reason


def test_sanitize_commercialization_thread_replaces_platform_phrase() -> None:
    before = (
        "Enterprise leader aligning platforms. Building on that foundation, "
        "platform commercialization generated significant revenue."
    )
    after = _sanitize_deprecated_commercialization_thread(before)
    assert "commercialization" not in after.lower()
    assert "platform revenue outcomes" in after.lower()
    assert "building on that foundation" in after.lower()


def test_apply_repair_commercialization_sanitize_when_no_other_flags() -> None:
    parsed = {
        "resume_display_text": (
            "Technology strategy executive who aligns enterprise IT direction. "
            "Building on that foundation, platform commercialization generated revenue."
        ),
        "claim_ledger": [],
    }
    repaired, meta = apply_graph_only_generation_quality_repair(
        parsed,
        allowed_fact_ids=set(),
        plan_facts=[],
    )
    assert meta.get("repair_kind") == "commercialization_thread_sanitize_only"
    assert "commercialization" not in str(repaired.get("resume_display_text") or "").lower()


def test_ensure_governance_fact_utilization_inserts_basel_sentence() -> None:
    parsed = {
        "resume_display_text": (
            "Enterprise technology leader who aligns governed AI platforms. "
            "Designs and operates platform runtimes with deterministic controls. "
            "Directed large-scale regulatory IT transformations across institutions. "
            "Software dependency graph intelligence enables legacy analysis. "
            "FSA-chartered actuarial work informs data governance at scale. "
            "Federated platform capabilities preserve lineage discipline at scale."
        ),
        "claim_ledger": [
            {"claim_text": "a", "source_fact_ids": ["fact_exec_002"]},
            {"claim_text": "b", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "c", "source_fact_ids": ["fact_consulting_001"]},
            {"claim_text": "d", "source_fact_ids": ["fact_engineering_platform_002"]},
            {"claim_text": "e", "source_fact_ids": ["fact_quant_hpc_003"]},
            {"claim_text": "f", "source_fact_ids": ["fact_engineering_platform_002"]},
        ],
    }
    facts = [
        {"fact_id": "fact_exec_002", "claim_text": "Scaled team"},
        {"fact_id": "fact_engineering_platform_001", "claim_text": "Platform"},
        {"fact_id": "fact_consulting_001", "claim_text": "Consulting"},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Graph"},
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA work"},
        {"fact_id": "fact_governance_003", "claim_text": "Basel III cut errors 40%"},
        {"fact_id": "fact_certs_001", "claim_text": "Certs"},
    ]
    patched, receipt = ensure_required_allowed_fact_utilization(parsed, selected_facts=facts)
    assert "fact_governance_003" in receipt.get("patched_fact_ids", [])
    assert "basel iii" in str(patched.get("resume_display_text") or "").lower()
    assert "40%" in str(patched.get("resume_display_text") or "")
    cited = {
        fid
        for row in patched.get("claim_ledger") or []
        for fid in (row.get("source_fact_ids") or [])
    }
    assert "fact_governance_003" in cited


def test_polish_dedupes_dependency_graph_and_weaves_team_metric() -> None:
    duplicate_resume = (
        "Enterprise technology leader who unifies governed AI platforms. "
        "Through that operating model, Basel III and CCAR data lineage cut regulatory reporting errors by 40%. "
        "Software dependency graph intelligence enables accelerated legacy-system analysis, "
        "exposes architecture dependency chains, and improves transformation visibility across enterprise complexity. "
        "That regulatory foundation is grounded in FSA-chartered actuarial work in capital modeling. "
        "Directed large-scale regulatory IT transformations and legacy-modernization programs for major institutions. "
        "Built and applied software dependency graph intelligence to accelerate legacy-system analysis."
    )
    parsed = {
        "resume_display_text": duplicate_resume,
        "claim_ledger": [
            {"claim_text": "a", "source_fact_ids": ["fact_exec_002"]},
            {"claim_text": "b", "source_fact_ids": ["fact_governance_003"]},
            {"claim_text": "c", "source_fact_ids": ["fact_engineering_platform_002"]},
            {"claim_text": "d", "source_fact_ids": ["fact_quant_hpc_003"]},
            {"claim_text": "e", "source_fact_ids": ["fact_consulting_001"]},
            {"claim_text": "f", "source_fact_ids": ["fact_engineering_platform_002"]},
        ],
    }
    facts = [
        {"fact_id": "fact_exec_002", "claim_text": "Scaled team 8 to 28"},
        {"fact_id": "fact_governance_003", "claim_text": "Basel cut errors 40%"},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Graph intelligence"},
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA work"},
        {"fact_id": "fact_consulting_001", "claim_text": "Consulting"},
    ]
    polished, receipt = polish_executive_summary_judge_alignment(parsed, selected_facts=facts)
    text = str(polished.get("resume_display_text") or "").lower()
    assert receipt.get("applied") is True
    assert text.count("dependency graph") == 1
    assert "8 to 28" in text
    cited = {
        fid
        for row in polished.get("claim_ledger") or []
        for fid in (row.get("source_fact_ids") or [])
    }
    assert "fact_engineering_platform_002" in cited


def test_polish_restores_graph_override_when_team_displaced_slot() -> None:
    """Regression: platform weave must not replace dependency-graph DISPLAY_OVERRIDE."""
    parsed = {
        "resume_display_text": (
            "Enterprise technology leader who unifies governed AI platforms. "
            "Through that operating model, Basel III and CCAR data lineage cut regulatory reporting errors by 40%. "
            "Scaled the ML engineering organization from 8 to 28 specialists. "
            "That regulatory foundation is grounded in FSA-chartered actuarial work in capital modeling. "
            "Directed large-scale regulatory IT transformations for major financial institutions. "
            "Designs and operates platform runtimes with deterministic controls and traceable execution."
        ),
        "claim_ledger": [],
    }
    facts = [
        {"fact_id": "fact_exec_002", "claim_text": "Scaled team 8 to 28"},
        {"fact_id": "fact_governance_003", "claim_text": "Basel cut errors 40%"},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Graph intelligence"},
        {"fact_id": "fact_engineering_platform_001", "claim_text": "Agentic AI platform"},
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA work"},
        {"fact_id": "fact_consulting_001", "claim_text": "Consulting"},
    ]
    polished, receipt = polish_executive_summary_judge_alignment(parsed, selected_facts=facts)
    text = str(polished.get("resume_display_text") or "").lower()
    assert receipt.get("applied") is True
    assert "dependency graph intelligence enables accelerated" in text
    cited = {
        fid
        for row in polished.get("claim_ledger") or []
        for fid in (row.get("source_fact_ids") or [])
    }
    assert "fact_engineering_platform_002" in cited


def test_strategy_lane_blocks_commercialization_thread() -> None:
    ok, reason = check_exec_summary_strategy_no_commercialization_thread(
        "Leader aligning commercialization into one IT strategy agenda.",
        target_role="SVP IT Strategy & Innovation",
    )
    assert not ok
    assert reason and "commercialization" in reason.lower()
