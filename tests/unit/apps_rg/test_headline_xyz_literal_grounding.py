"""Tests for x2_headline_xyz_literal_grounding (closes Bug:HeadlineXYZPhrasesNotGroundedInFactText).

Mirrors the Brown SVP failing case (full_resume_183cf9252e02 headline X3_BLOCK):
- RetiredProvider emitted ``SVP Engineering | Governed Agentic Platforms | Distributed AI Infrastructure | Enterprise Data Lineage``
- claim_ledger correctly cited fact_engineering_platform_005, fact_quant_hpc_002, fact_engineering_platform_004
- But the X/Y/Z phrases share ZERO content nouns with the cited facts' literal claim_text
- OpenAI judge: ``Unsupported: Governed Agentic Platforms`` (2.0 decisive)
- Claude judge: ``HPC trading platform latency \u2014 not the same as distributed AI infrastructure`` (3.2 soft)

This gate enforces the lexical grounding the X1D rubric was already implicitly checking,
catching the failure at the deterministic layer before the X1D judges get involved.
"""

from __future__ import annotations

from apps_rg.runtime.validators.headline_x2 import (
    _tokenize_for_grounding,
    check_headline_xyz_literal_grounding,
    recite_canonical_segments_to_bundle_facts,
)


def _positioning_bundles() -> list[dict[str, object]]:
    """Subset of apps_rg/fact_inventory/headline_positioning_bundles.json display->facts."""
    return [
        {
            "headline_positioning_bundle_id": "hpb_agentic_ai_platforms",
            "display_phrase_candidate": "Agentic AI Platforms",
            "linked_source_fact_ids": ["fact_engineering_platform_001"],
        },
        {
            "headline_positioning_bundle_id": "hpb_distributed_ai_infrastructure",
            "display_phrase_candidate": "Distributed AI Infrastructure",
            "linked_source_fact_ids": ["fact_engineering_platform_002"],
        },
        {
            "headline_positioning_bundle_id": "hpb_runtime_governance",
            "display_phrase_candidate": "Runtime Governance",
            "linked_source_fact_ids": ["fact_engineering_platform_001"],
        },
    ]


def _brown_svp_fact_pool() -> dict[str, str]:
    """Exact fact pool from full_resume_183cf9252e02/lanes/headline/selected_fact_plan.json."""
    return {
        "fact_engineering_platform_005": (
            "Architected cloud-native microservices across AWS and Databricks Lakehouse, "
            "integrating enterprise data pipelines, vector services, API gateways, identity "
            "controls, and highly available execution layers."
        ),
        "fact_engineering_platform_004": (
            "Standardized AI lifecycle practices across intake, validation, execution, "
            "monitoring, and remediation, reducing lab-to-production cycle time from six "
            "months to three weeks while preserving auditability and runtime stability."
        ),
        "fact_quant_hpc_002": (
            "Engineered an AI-driven automated trading platform using parallel HPC workflows, "
            "reducing end-to-end latency by 50% while enabling real-time ML insights and "
            "dynamic risk monitoring."
        ),
    }


def test_failing_brown_svp_headline_is_caught_by_grounding_gate() -> None:
    """The exact headline that broke Brown SVP must now fail-closed at X2 (not slip to X1D)."""
    headline = (
        "SVP Engineering | Governed Agentic Platforms | "
        "Distributed AI Infrastructure | Enterprise Data Lineage"
    )
    claim_ledger = [
        {"claim_text": "Governed Agentic Platforms", "source_fact_ids": ["fact_engineering_platform_005"]},
        {"claim_text": "Distributed AI Infrastructure", "source_fact_ids": ["fact_quant_hpc_002"]},
        {"claim_text": "Enterprise Data Lineage", "source_fact_ids": ["fact_engineering_platform_004"]},
    ]
    ok, observed, failure = check_headline_xyz_literal_grounding(
        headline_line=headline,
        claim_ledger=claim_ledger,
        fact_id_to_text=_brown_svp_fact_pool(),
    )
    assert ok is False, "Brown SVP headline must fail grounding gate (closes the regression)"
    assert failure is not None
    assert "Governed Agentic Platforms" in failure or "Distributed AI Infrastructure" in failure or "Enterprise Data Lineage" in failure
    assert observed["checked"] == 3
    assert any(seg["ground_pass"] is False for seg in observed["segments"])


def test_grounded_headline_passes_when_each_segment_shares_specific_nouns() -> None:
    headline = (
        "SVP Engineering | Lakehouse Microservices | "
        "AI Lifecycle Standardization | HPC Trading Workflows"
    )
    claim_ledger = [
        {"claim_text": "Lakehouse Microservices", "source_fact_ids": ["fact_engineering_platform_005"]},
        {"claim_text": "AI Lifecycle Standardization", "source_fact_ids": ["fact_engineering_platform_004"]},
        {"claim_text": "HPC Trading Workflows", "source_fact_ids": ["fact_quant_hpc_002"]},
    ]
    ok, observed, failure = check_headline_xyz_literal_grounding(
        headline_line=headline,
        claim_ledger=claim_ledger,
        fact_id_to_text=_brown_svp_fact_pool(),
    )
    assert ok is True, f"grounded headline should pass, got failure={failure!r}"
    assert failure is None
    assert observed["checked"] == 3
    assert all(seg["ground_pass"] for seg in observed["segments"])


def test_partial_grounding_fails_when_one_segment_is_pure_generic() -> None:
    """Two grounded + one generic still fails (closes the loophole)."""
    headline = (
        "SVP Engineering | Lakehouse Microservices | "
        "AI Lifecycle Standardization | Governed Agentic Platforms"
    )
    claim_ledger = [
        {"claim_text": "Lakehouse Microservices", "source_fact_ids": ["fact_engineering_platform_005"]},
        {"claim_text": "AI Lifecycle Standardization", "source_fact_ids": ["fact_engineering_platform_004"]},
        {"claim_text": "Governed Agentic Platforms", "source_fact_ids": ["fact_quant_hpc_002"]},
    ]
    ok, _observed, failure = check_headline_xyz_literal_grounding(
        headline_line=headline,
        claim_ledger=claim_ledger,
        fact_id_to_text=_brown_svp_fact_pool(),
    )
    assert ok is False
    assert "Governed Agentic Platforms" in (failure or "")


def test_graph_skill_semantics_ground_all_stoplist_headline_segment() -> None:
    """Graph skill text can ground a canonical all-stoplist headline phrase."""
    headline = (
        "SVP Engineering | Governed Runtime Architecture | "
        "Partner Co-Sell Motions | Lakehouse Retrieval"
    )
    claim_ledger = [
        {
            "claim_text": "Governed Runtime Architecture",
            "source_fact_ids": [
                "skill_provider_and_egress_governance",
                "skill_sr_cloud_data_platform_engineering",
            ],
        },
        {"claim_text": "Partner Co-Sell Motions", "source_fact_ids": ["reb_ibm_aws_alliance_partner_cosell_gtm"]},
        {"claim_text": "Lakehouse Retrieval", "source_fact_ids": ["skill_dense_sparse_exact_retrieval_design"]},
    ]
    fact_text = {
        "skill_provider_and_egress_governance": "provider and egress governance",
        "skill_sr_cloud_data_platform_engineering": "cloud data platform engineering",
        "reb_ibm_aws_alliance_partner_cosell_gtm": "Led IBM-AWS alliance co-sell motions",
        "skill_dense_sparse_exact_retrieval_design": "dense sparse exact retrieval design",
    }

    ok, observed, failure = check_headline_xyz_literal_grounding(
        headline_line=headline,
        claim_ledger=claim_ledger,
        fact_id_to_text=fact_text,
    )

    assert ok is True, f"graph-skill semantic grounding should pass, got {failure!r}"
    first = observed["segments"][0]
    assert first["ground_pass"] is True
    assert first["semantic_support"]["semantic_grounding_pass"] is True


def test_stoplist_excludes_role_family_generics_from_grounding_credit() -> None:
    """Generic words like 'platforms', 'infrastructure', 'ai' must not earn grounding credit alone."""
    tokens = _tokenize_for_grounding("Governed Agentic Platforms Infrastructure AI")
    assert tokens == set(), (
        f"all words should be stoplisted as generic role-family; got {tokens}"
    )

    tokens2 = _tokenize_for_grounding("Lakehouse Microservices Databricks Lineage")
    assert {"lakehouse", "microservices", "databricks", "lineage"}.issubset(tokens2)


def test_segment_without_ledger_row_fails_gate() -> None:
    headline = (
        "SVP Engineering | Lakehouse Microservices | "
        "AI Lifecycle Standardization | Uncited Phrase Here"
    )
    claim_ledger = [
        {"claim_text": "Lakehouse Microservices", "source_fact_ids": ["fact_engineering_platform_005"]},
        {"claim_text": "AI Lifecycle Standardization", "source_fact_ids": ["fact_engineering_platform_004"]},
    ]
    ok, _observed, failure = check_headline_xyz_literal_grounding(
        headline_line=headline,
        claim_ledger=claim_ledger,
        fact_id_to_text=_brown_svp_fact_pool(),
    )
    assert ok is False
    assert "no claim_ledger row" in (failure or "")


def test_metric_suffixed_fact_id_still_resolves_to_base_fact_text() -> None:
    headline = (
        "SVP Engineering | Lakehouse Microservices | "
        "AI Lifecycle Standardization | HPC Trading Workflows"
    )
    claim_ledger = [
        {"claim_text": "Lakehouse Microservices", "source_fact_ids": ["fact_engineering_platform_005"]},
        {"claim_text": "AI Lifecycle Standardization", "source_fact_ids": ["fact_engineering_platform_004_metric_abc"]},
        {"claim_text": "HPC Trading Workflows", "source_fact_ids": ["fact_quant_hpc_002"]},
    ]
    ok, _observed, failure = check_headline_xyz_literal_grounding(
        headline_line=headline,
        claim_ledger=claim_ledger,
        fact_id_to_text=_brown_svp_fact_pool(),
    )
    assert ok is True, f"metric-suffixed fact_id should resolve to base text, got failure={failure!r}"


def test_canonical_positioning_headline_grounded_via_bundle_registry() -> None:
    """All-stoplisted canonical display phrases ground via registry bundle binding."""
    headline = (
        "SVP Engineering | Agentic AI Platforms | "
        "Distributed AI Infrastructure | Runtime Governance"
    )
    claim_ledger = [
        {"claim_text": "Agentic AI Platforms", "source_fact_ids": ["fact_engineering_platform_001"]},
        {"claim_text": "Distributed AI Infrastructure", "source_fact_ids": ["fact_engineering_platform_002"]},
        {"claim_text": "Runtime Governance", "source_fact_ids": ["fact_engineering_platform_001"]},
    ]
    allowed = {"fact_engineering_platform_001", "fact_engineering_platform_002"}
    ok, observed, failure = check_headline_xyz_literal_grounding(
        headline_line=headline,
        claim_ledger=claim_ledger,
        fact_id_to_text={},
        positioning_bundles=_positioning_bundles(),
        allowed_fact_ids=allowed,
    )
    assert ok is True, f"canonical positioning headline should ground via registry, failure={failure!r}"
    assert all(seg["ground_pass"] for seg in observed["segments"])
    assert all(
        seg.get("reason") == "grounded_via_positioning_bundle_registry"
        for seg in observed["segments"]
    )


def test_registered_phrase_with_wrong_citation_still_fails_via_lexical_floor() -> None:
    """A canonical display phrase that does NOT cite its bundle's linked facts must not get a free pass."""
    headline = (
        "SVP Engineering | Agentic AI Platforms | "
        "Distributed AI Infrastructure | Runtime Governance"
    )
    # 'Agentic AI Platforms' cited to the wrong fact (not its bundle's linked fact)
    claim_ledger = [
        {"claim_text": "Agentic AI Platforms", "source_fact_ids": ["fact_quant_hpc_002"]},
        {"claim_text": "Distributed AI Infrastructure", "source_fact_ids": ["fact_engineering_platform_002"]},
        {"claim_text": "Runtime Governance", "source_fact_ids": ["fact_engineering_platform_001"]},
    ]
    allowed = {
        "fact_engineering_platform_001",
        "fact_engineering_platform_002",
        "fact_quant_hpc_002",
    }
    ok, _observed, failure = check_headline_xyz_literal_grounding(
        headline_line=headline,
        claim_ledger=claim_ledger,
        fact_id_to_text=_brown_svp_fact_pool(),
        positioning_bundles=_positioning_bundles(),
        allowed_fact_ids=allowed,
    )
    assert ok is False, "registered phrase missing its bundle's linked fact must fall to lexical floor and fail"
    assert "Agentic AI Platforms" in (failure or "")


def test_recite_canonical_segments_to_bundle_facts_repairs_citation_drift() -> None:
    """Model citation drift (each segment shifted one slot) is repaired to registry facts."""
    headline = (
        "SVP Engineering | Agentic AI Platforms | "
        "Distributed AI Infrastructure | Runtime Governance"
    )
    drifted = [
        {"claim_text": "Agentic AI Platforms", "source_fact_ids": ["fact_engineering_platform_002"]},
        {"claim_text": "Distributed AI Infrastructure", "source_fact_ids": ["fact_engineering_platform_003"]},
        {"claim_text": "Runtime Governance", "source_fact_ids": ["fact_quant_hpc_001"]},
    ]
    allowed = {"fact_engineering_platform_001", "fact_engineering_platform_002"}
    repaired, receipt = recite_canonical_segments_to_bundle_facts(
        headline_line=headline,
        claim_ledger=drifted,
        positioning_bundles=_positioning_bundles(),
        allowed_fact_ids=allowed,
    )
    assert receipt["any_changed"] is True
    by_seg = {r["claim_text"]: r["source_fact_ids"] for r in repaired}
    assert by_seg["Agentic AI Platforms"] == ["fact_engineering_platform_001"]
    assert by_seg["Distributed AI Infrastructure"] == ["fact_engineering_platform_002"]
    assert by_seg["Runtime Governance"] == ["fact_engineering_platform_001"]


def test_recite_does_not_touch_non_canonical_segments() -> None:
    """Free-synthesized phrases are left for the lexical floor, not re-cited."""
    headline = (
        "SVP Engineering | Lakehouse Microservices | "
        "AI Lifecycle Standardization | HPC Trading Workflows"
    )
    ledger = [
        {"claim_text": "Lakehouse Microservices", "source_fact_ids": ["fact_engineering_platform_005"]},
        {"claim_text": "AI Lifecycle Standardization", "source_fact_ids": ["fact_engineering_platform_004"]},
        {"claim_text": "HPC Trading Workflows", "source_fact_ids": ["fact_quant_hpc_002"]},
    ]
    repaired, receipt = recite_canonical_segments_to_bundle_facts(
        headline_line=headline,
        claim_ledger=ledger,
        positioning_bundles=_positioning_bundles(),
        allowed_fact_ids={"fact_engineering_platform_005"},
    )
    assert receipt["any_changed"] is False
    assert repaired == ledger
