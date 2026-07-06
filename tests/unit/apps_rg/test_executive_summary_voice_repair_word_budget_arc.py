"""Regression tests for exec-summary word-budget trim and canonical arc rebuild (X3_ALLOW fixes)."""

from __future__ import annotations

import re

from apps_rg.runtime.sections.executive_summary_voice_repair import (
    finalize_executive_summary_coherence,
    _rebuild_canonical_six_sentence_arc,
    _trim_paragraph_word_budget,
    polish_executive_summary_judge_alignment,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    _resume_word_count,
    check_exec_summary_allowed_fact_utilization,
    check_exec_summary_no_sentence_fragment,
    check_exec_summary_robotic_transition_stack,
)


def _word_count(sentences: list[str]) -> int:
    return len(re.findall(r"\S+", " ".join(sentences)))


def test_trim_paragraph_word_budget_removes_established_through_on_fsa_sentence() -> None:
    """Strategy 1 trim must fire when polish pushes prose over the paragraph ceiling."""
    sentences = [
        "Enterprise technology leader who unifies governed AI platforms for regulated enterprises.",
        "Applied across enterprise programs, Basel III and CCAR data lineage cut regulatory reporting errors by 40%.",
        "Software dependency graph intelligence enables accelerated legacy-system analysis across enterprise complexity.",
        (
            "That regulatory foundation is grounded in quantitative rigor established through "
            "FSA-chartered actuarial work in capital modeling and portfolio stress analytics, "
            "informing data governance and AI strategy at scale."
        ),
        (
            "Against that delivery foundation, directed large-scale regulatory IT transformations "
            "and legacy-modernization programs for major financial institutions across enterprise "
            "risk, compliance, data, cloud, and architecture domains."
        ),
        (
            "Innovation incubation and architecture standards will federate governed platform "
            "capabilities across autonomous business units without weakening lineage discipline."
        ),
    ]
    before_wc = _word_count(sentences)
    assert before_wc > 100
    assert "established through" in sentences[3].lower()
    trimmed = _trim_paragraph_word_budget(sentences, max_words=100)
    after_wc = _word_count(trimmed)
    assert after_wc < before_wc
    fsa_sentence = trimmed[3].lower()
    assert "established through" not in fsa_sentence
    assert "through fsa-chartered" in fsa_sentence


def test_trim_paragraph_word_budget_noop_when_under_cap() -> None:
    sentences = [
        "Short executive summary sentence one.",
        "Short executive summary sentence two.",
        "Short executive summary sentence three.",
        "Short executive summary sentence four.",
        "Short executive summary sentence five.",
        "Short executive summary sentence six.",
    ]
    trimmed = _trim_paragraph_word_budget(sentences, max_words=140)
    assert trimmed == sentences


def test_trim_paragraph_word_budget_preserves_runtime_control_finite_verb() -> None:
    """Regression for pinned Anthropic AI-partnership exec summary patch run."""
    sentences = [
        (
            "An AI partnerships and platform architecture leader builds alliance co-sell "
            "channel motions and governed runtime engineering into one enterprise adoption "
            "strategy for partner-led AI deployment."
        ),
        (
            "Through that partnership foundation, distributed cloud and data execution "
            "infrastructure pairs with a standardized AI systems lifecycle that accelerates "
            "lab-to-production adoption across partner and cloud ecosystems."
        ),
        (
            "Building on that platform base, reusable solution accelerators package cloud, "
            "data, and AI modernization patterns into repeatable client pursuits, while "
            "founder-led GTM motions have owned insurer AWS modernization opportunities "
            "directly with executive buyers."
        ),
        (
            "In parallel, runtime reliability, governance, telemetry, evaluation, and "
            "rollback discipline anchor an AWS shared-responsibility operating model that "
            "maps cloud control ownership for regulated deployments."
        ),
        (
            "That operating foundation also drives IBM-AWS alliance co-sell motions for "
            "financial-services modernization, embedding release automation and security "
            "scanning into regulated delivery paths alongside technical discovery and "
            "solution mapping for enterprise pursuits."
        ),
        (
            "This partnership and platform leadership can scale partner enablement, joint "
            "solution development, and presales technical guidance across cloud and GSI "
            "ecosystems to accelerate indirect revenue and enterprise AI adoption."
        ),
    ]

    trimmed = _trim_paragraph_word_budget(sentences, max_words=140)
    text = " ".join(trimmed)
    fragment_ok, fragment_reason = check_exec_summary_no_sentence_fragment(text)

    assert _resume_word_count(text) <= 140
    assert fragment_ok is True, fragment_reason
    assert "rollback discipline anchor" in text.lower()
    assert "Runtime reliability, governance, telemetry, evaluation." not in text


def test_trim_paragraph_word_budget_handles_anthropic_partnership_live_phrasing() -> None:
    sentences = [
        (
            "Enterprise technology executive aligning AWS modernization execution, governed "
            "agentic platform architecture, and hyperscaler alliance co-sell into one "
            "applied-AI partnership operating model for regulated enterprises."
        ),
        (
            "Through that migration foundation, policy administration and insurance platform "
            "workloads were classified by cloud fit and moved into AWS-native modernization "
            "waves reused across regulated reference architectures."
        ),
        (
            "Building on that base, a governed agentic control plane pairs route selection "
            "with controlled execution and auditable runtime traceability, while a dependency "
            "graph accelerator gives refactor teams blast-radius visibility and drift detection."
        ),
        (
            "In parallel, insurer and regulatory cloud-adoption standards were engaged directly, "
            "working through NAIC data-security model law readiness across multiple regulatory bodies."
        ),
        (
            "That operating foundation also drove IBM-AWS alliance co-sell with reusable offering "
            "accelerators and demoable playbooks, producing a 20% joint-revenue growth cadence and "
            "AI-driven sales frameworks."
        ),
        (
            "Partner channel co-sell and joint solution development built on that discipline, "
            "positioning this leader to scale a partner solutions architecture practice across GSI "
            "and hyperscaler ecosystems."
        ),
    ]

    assert _word_count(sentences) > 140
    trimmed = _trim_paragraph_word_budget(sentences, max_words=140)
    text = " ".join(trimmed)
    fragment_ok, fragment_reason = check_exec_summary_no_sentence_fragment(text)

    assert _resume_word_count(text) <= 140
    assert fragment_ok is True, fragment_reason
    assert "applied-AI partnership model" in text
    assert "partner solutions architecture across hyperscaler ecosystems" in text


def test_finalize_repairs_live_anthropic_partnership_transition_and_b4_fact() -> None:
    text = (
        "Engineering executive who leads AWS modernization and regulated cloud adoption for "
        "insurance platform workloads, aligning delivery with regulatory standards bodies. "
        "Through that migration foundation, distributed cloud and data execution infrastructure "
        "combines with a governed agentic AI control-plane architecture into one operating model. "
        "Building on that architecture, IBM-AWS alliance co-sell motions and offering accelerators "
        "packaged modernization patterns into reusable client pursuits. "
        "In parallel, regulatory engagement addressed insurer and NAIC-aligned cloud adoption "
        "standards across engaged regulatory bodies, keeping migration waves lineage-ready. "
        "That operating foundation also drove partner channel co-sell, scaling platform "
        "commercialization that grew IP-led revenue by $22M and margins by 20% while scaling "
        "the team from 8 to 28. "
        "This alliance-GTM foundation positions the leader to extend governed platform adoption "
        "across partner ecosystems at enterprise scale."
    )
    parsed = {
        "resume_display_text": text,
        "claim_ledger": [
            {
                "claim_text": (
                    "Engineering executive who leads AWS modernization and regulated cloud "
                    "adoption for insurance platform workloads, aligning delivery with "
                    "regulatory standards bodies."
                ),
                "source_fact_ids": ["reb_insurtech_aws_migration_execution"],
            },
            {
                "claim_text": (
                    "Through that migration foundation, distributed cloud and data execution "
                    "infrastructure combines with a governed agentic AI control-plane "
                    "architecture into one operating model."
                ),
                "source_fact_ids": [
                    "reb_unify_distributed_ecosystem_engineering",
                    "reb_unify_agentic_platform_architecture",
                ],
            },
            {
                "claim_text": (
                    "Building on that architecture, IBM-AWS alliance co-sell motions and "
                    "offering accelerators packaged modernization patterns into reusable "
                    "client pursuits."
                ),
                "source_fact_ids": [
                    "reb_ibm_aws_alliance_partner_cosell_gtm",
                    "reb_ibm_offering_accelerator_management",
                ],
            },
            {
                "claim_text": (
                    "In parallel, regulatory engagement addressed insurer and NAIC-aligned "
                    "cloud adoption standards across engaged regulatory bodies, keeping "
                    "migration waves lineage-ready."
                ),
                "source_fact_ids": [
                    "reb_insurtech_insurance_regulatory_cloud_adoption_standards",
                    "metric_insurtech_regulatory_bodies_engaged_count",
                ],
            },
            {
                "claim_text": (
                    "That operating foundation also drove partner channel co-sell, scaling "
                    "platform commercialization that grew IP-led revenue by $22M and margins "
                    "by 20% while scaling the team from 8 to 28."
                ),
                "source_fact_ids": [
                    "reb_unify_partner_channel_cosell",
                    "metric_unify_22m_ip_led_revenue",
                    "metric_unify_20pct_gross_margin_expansion",
                ],
            },
            {
                "claim_text": (
                    "This alliance-GTM foundation positions the leader to extend governed "
                    "platform adoption across partner ecosystems at enterprise scale."
                ),
                "source_fact_ids": [
                    "reb_unify_partner_channel_cosell",
                    "reb_ibm_aws_modernization_architecture",
                ],
            },
        ],
    }
    selected_facts = [
        {"fact_id": "reb_insurtech_aws_migration_execution", "claim_text": "AWS migration execution"},
        {
            "fact_id": "reb_unify_distributed_ecosystem_engineering",
            "claim_text": "distributed cloud and data execution infrastructure",
        },
        {
            "fact_id": "reb_unify_agentic_platform_architecture",
            "claim_text": "governed agentic AI control-plane architecture",
        },
        {
            "fact_id": "reb_ibm_aws_alliance_partner_cosell_gtm",
            "claim_text": "IBM-AWS alliance co-sell motions",
        },
        {
            "fact_id": "reb_ibm_offering_accelerator_management",
            "claim_text": "offering accelerators packaged modernization patterns",
        },
        {
            "fact_id": "reb_insurtech_insurance_regulatory_cloud_adoption_standards",
            "claim_text": "insurance regulatory cloud adoption standards",
        },
        {
            "fact_id": "metric_insurtech_regulatory_bodies_engaged_count",
            "claim_text": "engaged regulatory bodies",
        },
        {
            "fact_id": "reb_unify_partner_channel_cosell",
            "claim_text": "partner channel co-sell",
        },
        {
            "fact_id": "reb_unify_platform_commercialization_leadership",
            "claim_text": "platform commercialization leadership grew IP-led revenue and margins",
        },
        {"fact_id": "metric_unify_22m_ip_led_revenue", "claim_text": "$22M IP-led revenue"},
        {
            "fact_id": "metric_unify_20pct_gross_margin_expansion",
            "claim_text": "20% gross margin expansion",
        },
        {
            "fact_id": "reb_ibm_aws_modernization_architecture",
            "claim_text": "AWS modernization architecture",
        },
    ]
    allowed = {str(row["fact_id"]) for row in selected_facts}

    repaired, receipt = finalize_executive_summary_coherence(
        parsed,
        selected_facts=selected_facts,
        allowed_fact_ids=allowed,
        target_role="Manager of Applied AI Architecture, Partnerships",
    )

    repaired_text = str(repaired.get("resume_display_text") or "")
    transition_ok, transition_reason = check_exec_summary_robotic_transition_stack(repaired_text)
    assert transition_ok is True, transition_reason
    assert receipt["judge_polish"]["applied"] is True
    assert "reduce_formulaic_bridges" in receipt["judge_polish"]["actions"]

    row5 = repaired["claim_ledger"][4]
    assert "reb_unify_platform_commercialization_leadership" in row5["source_fact_ids"]
    assert len(row5["source_fact_ids"]) <= 3
    util_ok, util_reason, _receipt = check_exec_summary_allowed_fact_utilization(
        repaired["claim_ledger"],
        allowed,
        required_brushstroke_groups=[
            ["reb_insurtech_aws_migration_execution"],
            [
                "reb_unify_distributed_ecosystem_engineering",
                "reb_unify_agentic_platform_architecture",
            ],
            ["reb_insurtech_insurance_regulatory_cloud_adoption_standards"],
            ["reb_unify_platform_commercialization_leadership"],
        ],
    )
    assert util_ok is True, util_reason


def test_rebuild_canonical_six_sentence_arc_preserves_identity_thesis() -> None:
    s1 = "Enterprise technology leader who unifies governed AI platforms for regulated enterprises."
    degenerate = [s1] * 5
    facts = [
        {"fact_id": "fact_governance_003", "claim_text": "Basel III cut errors 40%"},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Dependency graph intelligence"},
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA-chartered actuarial work"},
        {"fact_id": "fact_consulting_001", "claim_text": "Directed regulatory IT transformations"},
        {"fact_id": "fact_exec_002", "claim_text": "Scaled ML engineering organization"},
    ]
    rebuilt = _rebuild_canonical_six_sentence_arc(degenerate, selected_facts=facts)
    assert len(rebuilt) == 6
    assert rebuilt[0] == s1
    assert "basel iii" in rebuilt[1].lower()
    assert "dependency graph" in rebuilt[2].lower()
    assert "8 to 28" in rebuilt[5].lower()


def test_polish_rebuilds_canonical_arc_when_llm_returns_five_sentences() -> None:
    """Regression: graph_only_repair collapsing to 5 sentences must not silently skip polish."""
    parsed = {
        "resume_display_text": (
            "Enterprise technology leader who unifies governed AI platforms for regulated enterprises. "
            "Designed and operationalized a governed agentic AI platform with deterministic routing. "
            "Platform commercialization generated $22M in IP-led revenue. "
            "Implemented Basel III and CCAR lineage frameworks that reduced regulatory reporting errors by 40%. "
            "Innovation incubation will extend governed platform capabilities across business units."
        ),
        "claim_ledger": [],
    }
    facts = [
        {"fact_id": "fact_engineering_platform_001", "claim_text": "Governed agentic AI platform"},
        {"fact_id": "fact_governance_003", "claim_text": "Basel III cut errors 40%"},
        {"fact_id": "fact_engineering_platform_002", "claim_text": "Dependency graph intelligence"},
        {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA-chartered actuarial work"},
        {"fact_id": "fact_consulting_001", "claim_text": "Directed regulatory IT transformations"},
        {"fact_id": "fact_exec_002", "claim_text": "Scaled ML engineering organization"},
    ]
    polished, receipt = polish_executive_summary_judge_alignment(parsed, selected_facts=facts)
    text = str(polished.get("resume_display_text") or "")
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    assert len(sents) == 6
    assert "canonical_arc_rebuild" in (receipt.get("actions") or [])
    assert receipt.get("applied") is True
