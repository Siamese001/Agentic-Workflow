"""Synthesis-quality voice repair (Claude-fail antipatterns)."""

from __future__ import annotations

import re

from apps_rg.runtime.sections.executive_summary_voice_repair import (
    finalize_executive_summary_coherence,
    repair_generic_filler_prose,
    strip_unsupported_source_sensitive_prose,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    _resume_word_count,
    build_sentence_claim_coverage,
    check_claim_ledger_orphan_source_ids,
    has_jd_phrase_copy,
)

_BAD_S5_S6 = (
    "Technology strategy executive who aligns enterprise IT direction, governed AI platform delivery, "
    "and innovation programs for regulated enterprise scale. "
    "Building on that platform foundation, platform commercialization generated $22M in IP-led revenue. "
    "Through that operating model, Basel III frameworks cut regulatory reporting errors by 40%. "
    "That regulatory lineage work extended to re-architecting monolithic risk analytics with containerized HPC microservices. "
    "Built advanced quantitative foundation through derivatives pricing, multi-Greek hedging, capital modeling, and FSA credential rigor. "
    "Governed platform delivery, engineering scale, and regulatory-grade controls extend that arc toward enterprise architecture modernization."
)


_FACTS = [
    {
        "fact_id": "fact_quant_hpc_001",
        "claim_text": "Re-architected monolithic risk analytics, trimming stress-testing cycles by 40%.",
    },
    {
        "fact_id": "fact_quant_hpc_003",
        "claim_text": "FSA credential and capital modeling foundation.",
    },
    {
        "fact_id": "fact_governance_003",
        "claim_text": "Basel III / CCAR lineage cut regulatory reporting errors by 40%.",
    },
]


def test_repair_synthesis_quality_rewrites_s5_s6_and_s4_bridge() -> None:
    out, receipt = repair_generic_filler_prose(_BAD_S5_S6, selected_facts=_FACTS)
    assert receipt.get("repaired") is True
    assert "enterprise technology leader who unifies" in out.lower()
    assert "derivatives pricing" not in out.lower()
    assert "extend that arc toward" not in out.lower()
    assert "that regulatory lineage work extended to" not in out.lower()
    assert "governance discipline" not in out.lower()
    assert "rather than listing credential" not in out.lower()
    assert "re-architecting monolithic" not in out.lower() or "re-architected monolithic" in out.lower()
    assert "capital-markets rigor informs which platform investments" not in out.lower()
    assert "innovation incubation" in out.lower()
    assert re.search(r"\b40%|\$[\d,]+", out)


def test_strip_unsupported_audit_ready_when_facts_lack_audit() -> None:
    parsed = {
        "resume_display_text": (
            "Technology leader who scales innovation without sacrificing audit-ready delivery. "
            "Basel III lineage accelerates audit-ready velocity."
        ),
        "claim_ledger": [],
    }
    facts = [
        {
            "fact_id": "fact_governance_003",
            "claim_text": "Implemented Basel III / CCAR data lineage and automated validation frameworks.",
        }
    ]
    out, receipt = strip_unsupported_source_sensitive_prose(parsed, selected_facts=facts)
    text = str(out["resume_display_text"]).lower()
    assert receipt.get("repaired") is True
    assert "audit" not in text
    assert "lineage-ready" in text


# --- Ledger fact-loss regression (live shape exec_summary_20260611_145208) ---------------
# Model emitted 6 fully sourced claim_ledger rows. The deterministic judge polish
# (enforce_required_fact_slots + trim_paragraph_word_budget) rewrote S2 with the
# "Against that delivery foundation," canonical bridge and stripped " large-scale ",
# then _rebuild_claim_ledger_from_display's anchor heuristics missed the rewritten
# S2/S6 sentences and emitted rows WITHOUT source_fact_ids -> x2_claim_ledger_orphan_zero.
# The rebuild must re-bind each rewritten row's ids from the prior row it derives from.

_LIVE_MODEL_DISPLAY = (
    "Enterprise technology executive who aligns governed agentic AI platform delivery, "
    "regulatory lineage discipline, and quantitative rigor into one coherent AI strategy "
    "for regulated financial and insurance enterprises. "
    "Through that platform foundation, large-scale regulatory IT transformations and "
    "legacy-modernization programs across risk, compliance, data, and cloud domains "
    "established the operating model depth this role demands. "
    "Building on that foundation, productizing agentic AI primitives into governed platform "
    "services generated $22M in IP-led revenue and expanded gross margins by 20% while "
    "scaling the ML engineering organization from 8 to 28 specialists. "
    "In parallel, implementing Basel III and CCAR data lineage and automated validation "
    "frameworks reduced regulatory reporting errors by 40%, embedding audit-ready evidence "
    "discipline into the platform delivery model. "
    "That regulatory foundation is grounded in quantitative rigor established through "
    "FSA-chartered actuarial work in capital modeling and portfolio stress analytics, "
    "informing data governance and AI strategy at scale. "
    "That convergence of platform monetization, governance depth, and actuarial rigor "
    "positions this leader to scale enterprise agentic AI across underwriting, claims, "
    "and operations with measurable accuracy and productivity outcomes."
)

_LIVE_MODEL_LEDGER = [
    {
        "claim_text": (
            "Aligns governed agentic AI platform delivery, regulatory lineage discipline, and "
            "FSA-chartered quantitative rigor into one enterprise AI strategy for regulated "
            "financial and insurance enterprises."
        ),
        "source_fact_ids": ["fact_engineering_platform_001", "fact_quant_hpc_003"],
    },
    {
        "claim_text": (
            "Directed large-scale regulatory IT transformations and legacy-modernization "
            "programs for major financial institutions across risk, compliance, data, cloud, "
            "and architecture domains, establishing the operating model depth required for "
            "enterprise-wide agentic AI transformation."
        ),
        "source_fact_ids": ["fact_consulting_001"],
    },
    {
        "claim_text": (
            "Productized agentic AI primitives into governed platform services, generating "
            "$22M in IP-led revenue, expanding gross margins by 20%, and scaling the ML "
            "engineering organization from 8 to 28 specialists."
        ),
        "source_fact_ids": ["fact_engineering_platform_006", "fact_exec_002"],
    },
    {
        "claim_text": (
            "Implemented Basel III and CCAR data lineage, cataloging, and automated validation "
            "frameworks that cut regulatory reporting errors by 40%, embedding audit-ready "
            "evidence discipline into the platform delivery model."
        ),
        "source_fact_ids": ["fact_governance_003"],
    },
    {
        "claim_text": (
            "FSA-chartered actuarial work in capital modeling and portfolio stress analytics "
            "grounds the regulatory and governance foundation, informing data governance and "
            "AI strategy decisions at enterprise scale."
        ),
        "source_fact_ids": ["fact_quant_hpc_003", "fact_certs_001"],
    },
    {
        "claim_text": (
            "The convergence of platform IP monetization, regulatory data lineage discipline, "
            "and FSA-chartered quantitative rigor positions this leader to scale enterprise "
            "agentic AI across underwriting, claims, and operations with measurable accuracy "
            "and productivity outcomes."
        ),
        "source_fact_ids": [
            "fact_engineering_platform_006",
            "fact_governance_003",
            "fact_quant_hpc_003",
        ],
    },
]

_LIVE_POOL_FACTS = [
    {"fact_id": "fact_engineering_platform_001", "claim_text": "Governed agentic AI platform"},
    {"fact_id": "fact_consulting_001", "claim_text": "Directed regulatory IT transformations"},
    {"fact_id": "fact_engineering_platform_006", "claim_text": "$22M IP-led revenue, 20% margin"},
    {"fact_id": "fact_exec_002", "claim_text": "Scaled team 8 to 28"},
    {"fact_id": "fact_governance_003", "claim_text": "Basel III lineage cut errors 40%"},
    {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA actuarial capital modeling"},
    {"fact_id": "fact_certs_001", "claim_text": "Certifications"},
]


def test_polish_rebuild_carries_source_fact_ids_for_rewritten_rows(monkeypatch) -> None:
    """6 sourced model rows -> bridge rewriter -> every final row still sourced."""
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_UTILIZATION_WAIVE_FACT_IDS", raising=False)
    from apps_rg.runtime.sections.executive_summary_voice_repair import (
        polish_executive_summary_judge_alignment,
    )

    parsed = {
        "resume_display_text": _LIVE_MODEL_DISPLAY,
        "claim_ledger": [dict(r) for r in _LIVE_MODEL_LEDGER],
    }
    model_union = {sid for row in _LIVE_MODEL_LEDGER for sid in row["source_fact_ids"]}

    polished, receipt = polish_executive_summary_judge_alignment(
        parsed, selected_facts=_LIVE_POOL_FACTS
    )
    assert receipt.get("applied") is True
    ledger = list(polished.get("claim_ledger") or [])
    assert len(ledger) == 6

    for i, row in enumerate(ledger):
        ids = list(row.get("source_fact_ids") or [])
        assert ids, f"claim_ledger[{i}] lost its source_fact_ids: {row.get('claim_text')!r}"
        # Never fabricate: every carried id must come from the model-emitted rows.
        assert set(ids) <= model_union, f"claim_ledger[{i}] fabricated ids: {ids}"

    text = str(polished.get("resume_display_text") or "")
    # Rewritten bridge text is preserved (the fix re-binds ids; it must not undo the rewrite).
    joined = " ".join(str(r.get("claim_text") or "") for r in ledger).lower()
    if "against that delivery foundation" in text.lower():
        bridge_row = next(
            r for r in ledger
            if str(r.get("claim_text") or "").lower().startswith("against that delivery foundation")
        )
        assert bridge_row["source_fact_ids"] == ["fact_consulting_001"]
    assert "that convergence of" in joined
    convergence_row = next(
        r for r in ledger if "convergence" in str(r.get("claim_text") or "").lower()
    )
    assert convergence_row["source_fact_ids"] == [
        "fact_engineering_platform_006",
        "fact_governance_003",
        "fact_quant_hpc_003",
    ]


def test_rebind_source_fact_ids_fail_open_on_ambiguity() -> None:
    """Ambiguous or weak attribution must NOT bind ids (no guessing, gate verdict stands)."""
    from apps_rg.runtime.sections.executive_summary_voice_repair import (
        _rebind_source_fact_ids_from_prior_rows,
    )

    # Two prior rows with identical claim text -> tie -> ambiguous -> [].
    rows = [
        {"claim_text": "Directed regulatory transformations across risk and data domains", "source_fact_ids": ["fact_a"]},
        {"claim_text": "Directed regulatory transformations across risk and data domains", "source_fact_ids": ["fact_b"]},
    ]
    out = _rebind_source_fact_ids_from_prior_rows(
        "Against that foundation, directed regulatory transformations across risk and data domains.",
        rows,
    )
    assert out == []

    # Weak overlap -> [].
    assert (
        _rebind_source_fact_ids_from_prior_rows(
            "Innovation programs federate governed platform capabilities.",
            [{"claim_text": "Basel III lineage cut reporting errors by 40%", "source_fact_ids": ["fact_governance_003"]}],
        )
        == []
    )

    # No prior rows -> [].
    assert _rebind_source_fact_ids_from_prior_rows("Any sentence at all here.", []) == []


def test_rebuild_claim_ledger_binds_capstone_sentence_to_allowed_roots() -> None:
    from apps_rg.runtime.sections.executive_summary_voice_repair import (
        _rebuild_claim_ledger_from_display,
    )

    sentence = (
        "That governed foundation positions this leader to federate enterprise architecture "
        "standards, accelerate post-merger integration playbooks, and incubate AI-enabled "
        "innovation programs at scale."
    )
    out = _rebuild_claim_ledger_from_display(
        {
            "resume_display_text": sentence,
            "claim_ledger": [],
        }
    )
    ledger = list(out.get("claim_ledger") or [])
    assert len(ledger) == 1
    assert ledger[0]["claim_text"] == sentence
    assert ledger[0]["source_fact_ids"] == [
        "reb_ibm_aws_modernization_architecture",
        "reb_ibm_offering_accelerator_management",
        "reb_unify_distributed_ecosystem_engineering",
    ]


def test_rebuild_claim_ledger_binds_current_intro_and_capstone_variants() -> None:
    from apps_rg.runtime.sections.executive_summary_voice_repair import (
        _rebuild_claim_ledger_from_display,
    )

    intro = (
        "Technology strategy executive who aligns governed cloud modernization, "
        "enterprise architecture discipline, and innovation programs into IT direction "
        "for regulated, enterprises."
    )
    closer = (
        "Those proven capabilities in governed platform delivery, repeatable architecture "
        "playbooks, and regulated-enterprise controls position this leader to federate "
        "enterprise architecture standards."
    )
    out = _rebuild_claim_ledger_from_display(
        {
            "resume_display_text": f"{intro} {closer}",
            "claim_ledger": [],
        }
    )
    ledger = list(out.get("claim_ledger") or [])
    assert len(ledger) == 2
    assert ledger[0]["source_fact_ids"] == [
        "reb_ey_insurance_core_modernization",
        "reb_insurtech_aws_guidewire_core_modernization",
        "reb_ibm_aws_modernization_architecture",
    ]
    assert ledger[1]["source_fact_ids"] == [
        "reb_ibm_aws_modernization_architecture",
        "reb_ibm_offering_accelerator_management",
        "reb_unify_distributed_ecosystem_engineering",
    ]


def test_rebuild_claim_ledger_binds_live_intro_variant_to_allowed_roots() -> None:
    from apps_rg.runtime.sections.executive_summary_voice_repair import (
        _rebuild_claim_ledger_from_display,
    )

    intro = (
        "Technology strategy executive who aligns governed cloud modernization, "
        "insurance core architecture, and regulatory controls into enterprise IT direction "
        "for regulated, organizations."
    )
    out = _rebuild_claim_ledger_from_display(
        {
            "resume_display_text": intro,
            "claim_ledger": [],
        }
    )
    ledger = list(out.get("claim_ledger") or [])
    assert len(ledger) == 1
    assert ledger[0]["source_fact_ids"] == [
        "reb_ey_insurance_core_modernization",
        "reb_insurtech_aws_guidewire_core_modernization",
        "reb_ibm_aws_modernization_architecture",
    ]


def test_rebuild_claim_ledger_binds_live_intro_and_capstone_variants() -> None:
    from apps_rg.runtime.sections.executive_summary_voice_repair import (
        _rebuild_claim_ledger_from_display,
    )

    intro = (
        "Technology strategy executive who aligns governed cloud modernization, "
        "insurance core transformation, and regulatory lineage into enterprise IT direction "
        "for complex, organizations."
    )
    closer = (
        "That convergence of governed cloud delivery, insurance platform depth, and "
        "regulatory analytics positions this leader to federate enterprise architecture "
        "standards."
    )
    out = _rebuild_claim_ledger_from_display(
        {
            "resume_display_text": f"{intro} {closer}",
            "claim_ledger": [],
        }
    )
    ledger = list(out.get("claim_ledger") or [])
    assert len(ledger) == 2
    assert ledger[0]["source_fact_ids"] == [
        "reb_ey_insurance_core_modernization",
        "reb_insurtech_aws_guidewire_core_modernization",
        "reb_ibm_aws_modernization_architecture",
    ]
    assert ledger[1]["source_fact_ids"] == [
        "reb_insurtech_aws_migration_execution",
        "reb_insurtech_regulated_aws_control_implementation",
        "reb_ibm_aws_modernization_architecture",
        "reb_unify_distributed_ecosystem_engineering",
        "reb_insurtech_insurance_regulatory_cloud_adoption_standards",
    ]


def test_rebuild_claim_ledger_binds_post_polish_scrubbed_variants() -> None:
    from apps_rg.runtime.sections.executive_summary_voice_repair import (
        _rebuild_claim_ledger_from_display,
    )

    intro = (
        "Technology strategy executive who aligns governed cloud modernization, "
        "insurance core architecture, and regulatory control discipline into enterprise IT direction "
        "for regulated enterprises."
    )
    closer = (
        "That governed architecture and accelerator foundation positions the enterprise to "
        "federate innovation programs, standardize interoperability across acquired units, "
        "and advance a multi-year IT strategy roadmap."
    )
    out = _rebuild_claim_ledger_from_display(
        {
            "resume_display_text": f"{intro} {closer}",
            "claim_ledger": [],
        }
    )
    ledger = list(out.get("claim_ledger") or [])
    assert len(ledger) == 2
    assert ledger[0]["source_fact_ids"] == [
        "reb_ey_insurance_core_modernization",
        "reb_insurtech_aws_guidewire_core_modernization",
        "reb_ibm_aws_modernization_architecture",
    ]
    assert ledger[1]["source_fact_ids"] == [
        "reb_ibm_aws_modernization_architecture",
        "reb_ibm_offering_accelerator_management",
        "reb_unify_distributed_ecosystem_engineering",
        "reb_insurtech_aws_migration_execution",
        "reb_insurtech_insurance_regulatory_cloud_adoption_standards",
    ]


def test_rebuild_claim_ledger_binds_latest_scrubbed_variants() -> None:
    from apps_rg.runtime.sections.executive_summary_voice_repair import (
        _rebuild_claim_ledger_from_display,
    )

    intro = (
        "Technology strategy executive who aligns governed cloud modernization, "
        "insurance core architecture, and regulatory-grade controls into enterprise IT direction "
        "for distributed, regulated organizations."
    )
    closer = (
        "That convergence of cloud execution, core systems governance, and lineage-backed "
        "operating models positions this leader to federate architecture standards, "
        "accelerate post-merger integration programs."
    )
    out = _rebuild_claim_ledger_from_display(
        {
            "resume_display_text": f"{intro} {closer}",
            "claim_ledger": [],
        }
    )
    ledger = list(out.get("claim_ledger") or [])
    assert len(ledger) == 2
    assert ledger[0]["source_fact_ids"] == [
        "reb_ey_insurance_core_modernization",
        "reb_insurtech_aws_guidewire_core_modernization",
        "reb_ibm_aws_modernization_architecture",
    ]
    assert ledger[1]["source_fact_ids"] == [
        "reb_insurtech_aws_migration_execution",
        "reb_insurtech_regulated_aws_control_implementation",
        "reb_ibm_aws_modernization_architecture",
        "reb_unify_distributed_ecosystem_engineering",
        "reb_insurtech_insurance_regulatory_cloud_adoption_standards",
    ]


def test_graph_era_anthropic_exec_summary_repair_keeps_source_ids_and_budget() -> None:
    """Regression for live Anthropic run w2_3b: graph-era ids were stripped to empty rows."""
    display = (
        "Enterprise technology executive who aligns governed agentic AI platform architecture, "
        "partner alliance GTM execution, and cloud modernization depth into coherent strategy "
        "for regulated enterprise ecosystems. "
        "From that platform footprint, distributed cloud and data execution infrastructure was "
        "designed with runtime resilience controls and policy-gated agent execution surfaces "
        "that scale without sacrificing traceability. "
        "From that operating base, partner co-sell motions and joint solution development across "
        "hyperscaler alliances produced a 20% joint outcome and a multi-motion partner enablement "
        "asset set. "
        "IBM-AWS alliance architecture for regulated financial-services workloads established "
        "reference architecture reuse patterns and cloud modernization waves that accelerated "
        "client adoption readiness. "
        "That alliance and platform discipline translated into IP-led of and 20% expansion while "
        "the platform engineering team scaled from 8 to 28 specialists. "
        "The same governed platform and partner architecture foundation positions a Partner "
        "Solutions Architect team to embed with GSI and cloud partner ecosystems, enabling "
        "production-grade AI deployments at enterprise scale."
    )
    ledger = [
        {
            "claim_text": (
                "Enterprise technology executive aligning governed agentic AI platform architecture, "
                "partner co-sell channel and alliance GTM execution, and distributed cloud "
                "modernization depth into one regulated enterprise strategy."
            ),
            "source_fact_ids": [
                "reb_unify_agentic_platform_architecture",
                "reb_unify_partner_channel_cosell",
                "reb_unify_distributed_ecosystem_engineering",
            ],
        },
        {
            "claim_text": (
                "Designed and operated distributed cloud and data execution infrastructure with "
                "runtime resilience controls and policy-gated agent execution surfaces."
            ),
            "source_fact_ids": [
                "reb_unify_distributed_ecosystem_engineering",
                "skill_sr_cloud_data_platform_engineering",
                "skill_runtime_resilience_controls",
                "metric_unify_policy_gated_agent_execution_surface",
                "metric_unify_replayable_runtime_traceability",
            ],
        },
        {
            "claim_text": (
                "Led partner co-sell motions and joint solution development across hyperscaler "
                "alliances, producing a 20% joint revenue growth outcome."
            ),
            "source_fact_ids": [
                "reb_unify_partner_channel_cosell",
                "skill_partner_co_selling",
                "skill_partner_joint_solution_development",
                "skill_partner_cloud_vendor_joint_gtm",
                "metric_ibm_20pct_joint_revenue_growth",
                "metric_unify_partner_enablement_asset_set",
                "metric_unify_partner_cosell_solution_motion_count",
            ],
        },
        {
            "claim_text": (
                "Led IBM-AWS alliance co-sell motions and AWS modernization architecture for "
                "regulated financial-services workloads."
            ),
            "source_fact_ids": [
                "reb_ibm_aws_alliance_partner_cosell_gtm",
                "reb_ibm_aws_modernization_architecture",
                "metric_ibm_regulated_reference_architecture_reuse",
                "metric_ibm_onprem_to_aws_modernization_waves",
                "reb_ibm_customer_success_value_realization",
            ],
        },
        {
            "claim_text": (
                "Platform productization and IP-led revenue leadership generated $22M in IP-led "
                "revenue growth and 20% gross margin expansion while the platform engineering "
                "team scaled from 8 to 28 specialists."
            ),
            "source_fact_ids": [
                "reb_unify_platform_commercialization_leadership",
                "metric_unify_22m_ip_led_revenue",
                "metric_unify_20pct_gross_margin_expansion",
                "metric_unify_team_scaled_8_to_28",
            ],
        },
        {
            "claim_text": (
                "The governed agentic platform architecture, partner GTM enablement depth, and "
                "regulated cloud modernization lineage position a Partner Solutions Architect "
                "team to embed with GSI and cloud partner ecosystems."
            ),
            "source_fact_ids": [
                "reb_unify_agentic_platform_architecture",
                "skill_partner_gtm_enablement",
                "skill_partner_partner_led_ai_solutions",
                "reb_insurtech_aws_migration_execution",
                "reb_insurtech_insurance_regulatory_cloud_adoption_standards",
            ],
        },
    ]
    allowed = {sid for row in ledger for sid in row["source_fact_ids"]}
    parsed = {"resume_display_text": display, "claim_ledger": ledger, "gap_notes": []}

    out, receipt = finalize_executive_summary_coherence(
        parsed,
        selected_facts=[{"fact_id": fid} for fid in sorted(allowed)],
        target_role="Manager of Applied AI Architecture, Partnerships",
    )

    text = str(out.get("resume_display_text") or "")
    repaired_ledger = list(out.get("claim_ledger") or [])
    coverage = build_sentence_claim_coverage(text, repaired_ledger, allowed)
    orphan_ok, orphan_reason = check_claim_ledger_orphan_source_ids(repaired_ledger, allowed)
    jd_copy, phrase = has_jd_phrase_copy(text, "embed with GSI and cloud partner ecosystems")

    assert receipt["judge_polish"]["applied"] is True
    assert _resume_word_count(text) <= 140
    assert "IP-led of" not in text
    assert jd_copy is False, phrase
    assert orphan_ok is True, orphan_reason
    assert coverage["overall_pass"] is True
    assert repaired_ledger[0]["source_fact_ids"]
    assert repaired_ledger[4]["source_fact_ids"] == [
        "reb_unify_platform_commercialization_leadership",
        "metric_unify_22m_ip_led_revenue",
        "metric_unify_20pct_gross_margin_expansion",
        "metric_unify_team_scaled_8_to_28",
    ]


def test_graph_era_trim_repair_restores_metric_nouns_after_word_budget() -> None:
    """Regression for w2_3c_exec: trim must not leave malformed metric fragments."""
    display = (
        "Platform engineering executive who aligns governed agentic AI architecture, alliance "
        "co-sell programs, and regulated cloud modernization into partner-led growth agenda "
        "for enterprise scale. "
        "Distributed cloud and data infrastructure was designed with runtime resilience "
        "controls and policy-gated execution surfaces that keep agent behavior traceable and "
        "auditable. "
        "IBM-AWS alliance co-sell motions and joint GTM enablement assets accelerated "
        "financial-services modernization opportunities, contributing to 20% joint across "
        "the partner channel. "
        "In parallel, regulated cloud migration work engaged multiple insurance regulatory "
        "bodies on data security and cloud adoption standards, grounding the modernization "
        "program in controls-ready architecture patterns. "
        "That commercial and regulatory foundation translated into in IP-led and 20% "
        "expansion while the platform engineering team scaled from 8 to 28 specialists. "
        "The same foundation positions a Partner Solutions Architect team to guide integrator "
        "and hyperscaler ecosystems, codify reference architectures, and accelerate enterprise "
        "AI adoption at scale."
    )
    ledger = [
        {
            "claim_text": "Executive identity combines agentic AI architecture, alliance co-sell, and regulated cloud modernization.",
            "source_fact_ids": [
                "reb_unify_agentic_platform_architecture",
                "reb_unify_partner_channel_cosell",
                "reb_ibm_aws_modernization_architecture",
                "reb_insurtech_aws_migration_execution",
            ],
        },
        {
            "claim_text": "Distributed cloud and data infrastructure carried runtime resilience, policy-gated execution, and traceability.",
            "source_fact_ids": [
                "reb_unify_distributed_ecosystem_engineering",
                "skill_runtime_resilience_controls",
                "metric_unify_policy_gated_agent_execution_surface",
                "metric_unify_replayable_runtime_traceability",
            ],
        },
        {
            "claim_text": "IBM-AWS alliance co-sell motions and joint GTM enablement contributed to 20% joint revenue growth.",
            "source_fact_ids": [
                "reb_ibm_aws_alliance_partner_cosell_gtm",
                "metric_unify_partner_enablement_asset_set",
                "metric_ibm_alliance_cosell_operating_cadence",
                "metric_ibm_ai_driven_sales_frameworks",
                "metric_ibm_20pct_joint_revenue_growth",
            ],
        },
        {
            "claim_text": "Regulated cloud migration engaged multiple insurance regulatory bodies on data security and cloud adoption standards.",
            "source_fact_ids": [
                "reb_insurtech_aws_migration_execution",
                "reb_insurtech_insurance_regulatory_cloud_adoption_standards",
                "metric_insurtech_regulatory_bodies_engaged_count",
                "skill_naic_data_security_model_law_readiness",
            ],
        },
        {
            "claim_text": "Platform productization generated $22M in IP-led revenue and 20% gross margin expansion while scaling the team from 8 to 28.",
            "source_fact_ids": [
                "reb_unify_platform_commercialization_leadership",
                "metric_unify_22m_ip_led_revenue",
                "metric_unify_20pct_gross_margin_expansion",
                "metric_unify_team_scaled_8_to_28",
            ],
        },
        {
            "claim_text": "Partner architecture foundation positions Partner Solutions Architect leadership across integrator and hyperscaler ecosystems.",
            "source_fact_ids": [
                "reb_unify_agentic_platform_architecture",
                "reb_unify_partner_channel_cosell",
                "skill_partner_joint_solution_development",
                "skill_partner_gtm_enablement",
            ],
        },
    ]
    allowed = {sid for row in ledger for sid in row["source_fact_ids"]}
    out, _receipt = finalize_executive_summary_coherence(
        {"resume_display_text": display, "claim_ledger": ledger, "gap_notes": []},
        selected_facts=[{"fact_id": fid} for fid in sorted(allowed)],
        target_role="Manager of Applied AI Architecture, Partnerships",
    )

    text = str(out.get("resume_display_text") or "")
    repaired_ledger = list(out.get("claim_ledger") or [])
    coverage = build_sentence_claim_coverage(text, repaired_ledger, allowed)

    assert _resume_word_count(text) <= 140
    assert "20% joint across" not in text
    assert "20% joint revenue growth across" in text
    assert "translated into in IP-led" not in text
    assert "$22M in IP-led revenue and 20% gross margin expansion" in text
    assert "into a partner-led growth agenda" in text
    assert coverage["overall_pass"] is True


def test_finalize_preserves_allowed_source_ids_for_pinned_brown_summary() -> None:
    """Pinned narrative rewrites must not drop row-level proof ids on finalization."""
    display = (
        "Technology strategy executive who aligns governed cloud modernization, insurance core "
        "architecture, and regulatory-grade controls into enterprise IT direction for "
        "distributed, regulated organizations. "
        "AWS migration execution classified workloads by cloud fit and completed migration "
        "waves that moved core insurance platform workloads from monolithic on-premises "
        "constraints to cloud-native delivery. "
        "Guidewire-adjacent policy administration workflows and core insurance data models "
        "were decomposed into configurable, integration-ready components, connecting "
        "modernization execution to repeatable architecture patterns. "
        "Reusable solution accelerators packaged cloud, data, and AI modernization patterns "
        "for regulated financial-services workloads, enabling repeatable client pursuits "
        "across reference architecture frameworks. "
        "That regulatory foundation extended to BCBS 239-aligned risk-data aggregation, "
        "three-lines-of-defense accountability structures, and regulatory analytics lineage "
        "linking predictive risk use cases to audit-ready workflows. "
        "That convergence of cloud execution, core systems governance, and lineage-backed "
        "operating models positions this leader to federate architecture standards, "
        "accelerate post-merger integration programs."
    )
    ledger = [
        {
            "claim_text": (
                "Technology strategy executive who aligns governed cloud modernization, insurance "
                "core architecture, and regulatory-grade controls into enterprise IT direction for "
                "distributed, regulated organizations."
            ),
            "source_fact_ids": [
                "reb_insurtech_aws_migration_execution",
                "reb_insurtech_regulated_aws_control_implementation",
                "reb_ey_erm_risk_governance",
            ],
        },
        {
            "claim_text": (
                "AWS migration execution classified workloads by cloud fit and completed migration "
                "waves that moved core insurance platform workloads from monolithic on-premises "
                "constraints to cloud-native delivery."
            ),
            "source_fact_ids": [
                "reb_insurtech_aws_migration_execution",
                "metric_insurtech_workloads_classified_by_cloud_fit_count",
                "metric_insurtech_migration_waves_completed_count",
                "metric_insurtech_core_workloads_migrated_count",
                "reb_ibm_aws_modernization_architecture",
            ],
        },
        {
            "claim_text": (
                "Guidewire-adjacent policy administration workflows and core insurance data models "
                "were decomposed into configurable, integration-ready components, connecting "
                "modernization execution to repeatable architecture patterns."
            ),
            "source_fact_ids": [
                "reb_insurtech_aws_guidewire_core_modernization",
                "reb_ey_insurance_core_modernization",
                "metric_insurtech_guidewire_workflows_mapped_count",
                "metric_insurtech_core_data_entities_mapped_count",
            ],
        },
        {
            "claim_text": (
                "Reusable solution accelerators packaged cloud, data, and AI modernization patterns "
                "for regulated financial-services workloads, enabling repeatable client pursuits "
                "across reference architecture frameworks."
            ),
            "source_fact_ids": [
                "reb_ibm_offering_accelerator_management",
                "metric_ibm_offering_accelerator_package_reuse",
                "metric_ibm_client_facing_modernization_playbooks",
                "skill_p2_tech_reference_architecture",
                "metric_ibm_onprem_to_aws_modernization_waves",
            ],
        },
        {
            "claim_text": (
                "That regulatory foundation extended to BCBS 239-aligned risk-data aggregation, "
                "three-lines-of-defense accountability structures, and regulatory analytics lineage "
                "linking predictive risk use cases to audit-ready workflows."
            ),
            "source_fact_ids": [
                "reb_ey_erm_risk_governance",
                "metric_ey_bcbs239_risk_data_domain_count",
                "metric_ey_three_lines_control_owner_count",
                "reb_ey_regulatory_analytics_modernization",
                "metric_ey_regulatory_lineage_domains_count",
                "metric_ey_predictive_risk_use_cases_count",
            ],
        },
        {
            "claim_text": (
                "That convergence of cloud execution, core systems governance, and lineage-backed "
                "operating models positions this leader to federate architecture standards, "
                "accelerate post-merger integration programs."
            ),
            "source_fact_ids": [
                "reb_unify_distributed_ecosystem_engineering",
                "reb_insurtech_regulated_aws_control_implementation",
                "reb_insurtech_insurance_regulatory_cloud_adoption_standards",
            ],
        },
    ]
    allowed = {sid for row in ledger for sid in row["source_fact_ids"]}

    out, receipt = finalize_executive_summary_coherence(
        {"resume_display_text": display, "claim_ledger": ledger, "gap_notes": []},
        selected_facts=[{"fact_id": fid} for fid in sorted(allowed)],
        allowed_fact_ids=allowed,
        target_role="SVP IT Strategy & Innovation",
    )

    repaired_ledger = list(out.get("claim_ledger") or [])
    coverage = build_sentence_claim_coverage(
        str(out.get("resume_display_text") or ""),
        repaired_ledger,
        allowed,
    )
    orphan_ok, orphan_reason = check_claim_ledger_orphan_source_ids(repaired_ledger, allowed)

    assert receipt["judge_polish"]["applied"] is True
    assert len(repaired_ledger) == 6
    assert receipt["orphan_citations_stripped"] == []
    assert repaired_ledger[0]["source_fact_ids"] == ledger[0]["source_fact_ids"]
    assert repaired_ledger[5]["source_fact_ids"] == ledger[5]["source_fact_ids"]
    assert coverage["overall_pass"] is True, coverage
    assert orphan_ok is True, orphan_reason
