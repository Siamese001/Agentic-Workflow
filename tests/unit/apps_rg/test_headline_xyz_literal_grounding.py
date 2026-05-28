"""Tests for x2_headline_xyz_literal_grounding (closes Bug:HeadlineXYZPhrasesNotGroundedInFactText).

Mirrors the Brown SVP failing case (full_resume_183cf9252e02 headline X3_BLOCK):
- Qwen emitted ``SVP Engineering | Governed Agentic Platforms | Distributed AI Infrastructure | Enterprise Data Lineage``
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
)


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
