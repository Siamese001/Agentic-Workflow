"""Acceptance test: generic consulting substitution phrases must fail X2.

W5 acceptance test (Bullet Proof Bundle Redesign):
- Verifies x2_no_generic_consulting_substitution gate.
- Bullets with consulting-speak substitution fail even when source_fact_ids is valid.
- Bullets with specific mechanism vocabulary pass.
"""
from __future__ import annotations

import pytest

from apps_rg.runtime.validators.bullet_quality_floor_x2 import (
    GENERIC_CONSULTING_SUBSTITUTIONS,
    check_bullet_no_generic_consulting_substitution,
    check_bullet_technical_specificity_floor,
    run_bullet_quality_floor_gates,
)


class TestGenericConsultingSubstitutionBlocklist:
    def test_consulting_speak_phrases_fail(self) -> None:
        """Each consulting-speak phrase in the blocklist must fail the gate."""
        failing_bullets = [
            "drive strategic value",
            "ensure alignment",
            "stakeholder management",
            "leveraged best practices",
            "worked closely with",
            "delivered solutions",
        ]
        for phrase in failing_bullets:
            result = check_bullet_no_generic_consulting_substitution(
                "bul_ibm_001",
                f"The team worked to {phrase} across the enterprise to drive growth.",
            )
            assert not result.passed, f"Expected fail for phrase: {phrase!r}"
            assert phrase in result.signals or any(phrase in s for s in result.signals), (
                f"Phrase {phrase!r} should be in signals, got {result.signals}"
            )

    def test_specific_mechanism_vocabulary_passes(self) -> None:
        """Bullets with specific technical mechanisms should pass."""
        organic_bullets = [
            "Architected cloud-native AI and analytics platforms maintaining 99.9% uptime for regulated financial institutions.",
            "Engineered real-time data lineage and observability frameworks that reduced regulatory response latency by 50%.",
            "Deployed microservices migration from legacy on-prem environments, achieving 30% infrastructure overhead reduction.",
            "Structured multi-year hyperscaler alliances generating $15M in incremental co-sell revenue.",
            "Converted bespoke regulatory workflows into SaaS-like platforms improving renewal rates by 25%.",
        ]
        for i, text in enumerate(organic_bullets, 1):
            bid = f"bul_ibm_00{i}"
            result = check_bullet_no_generic_consulting_substitution(bid, text)
            assert result.passed, f"Expected pass for organic bullet: {text[:60]}. Signals: {result.signals}"

    def test_valid_source_fact_ids_do_not_override_consulting_gate(self) -> None:
        """Having valid source_fact_ids must NOT bypass the consulting substitution gate."""
        consulting_text = (
            "Leveraged best practices to drive strategic value for key stakeholders "
            "while ensuring alignment across the enterprise platform."
        )
        result = check_bullet_no_generic_consulting_substitution("bul_ibm_001", consulting_text)
        assert not result.passed, (
            "Gate must fail even when source_fact_ids would be valid — "
            "consulting substitution is a content quality gate, not a provenance gate"
        )

    def test_all_blocklist_phrases_are_in_frozenset(self) -> None:
        """Sanity check: GENERIC_CONSULTING_SUBSTITUTIONS must contain the plan-spec phrases."""
        required_phrases = [
            "drive strategic value",
            "ensure alignment",
            "stakeholder management",
            "delivered solutions",
            "managed the relationship",
            "worked closely with",
            "collaborated to deliver",
            "ensured the platform",
            "leveraged best practices",
        ]
        for phrase in required_phrases:
            assert phrase in GENERIC_CONSULTING_SUBSTITUTIONS, (
                f"Plan-spec phrase {phrase!r} missing from GENERIC_CONSULTING_SUBSTITUTIONS"
            )


class TestTechnicalSpecificityFloor:
    def test_known_tech_tokens_pass(self) -> None:
        tech_bullets = [
            ("bul_ibm_001", "Deployed Kubernetes and Kafka-based streaming architecture"),
            ("bul_ibm_002", "Implemented AWS Databricks Lakehouse with microservices"),
            ("bul_ibm_003", "Built LLM-based document intelligence with RAG retrieval"),
            ("bul_ibm_004", "Engineered data lineage and observability for Basel/CCAR compliance"),
            ("bul_ibm_005", "Structured hyperscaler alliances on Azure and AWS co-sell channels"),
            (
                "bul_ibm_004",
                "Owned cross-functional BI and data models for modernization portfolios, building governed BI views.",
            ),
        ]
        for bid, text in tech_bullets:
            r = check_bullet_technical_specificity_floor(bid, text)
            assert r.passed, f"Expected pass for: {text[:60]}, got: {r.failure_reason}"

    def test_generic_prose_fails_without_mechanism_vocab(self) -> None:
        r = check_bullet_technical_specificity_floor(
            "bul_ibm_001",
            "Managed the team to deliver successful business outcomes within budget constraints.",
        )
        assert not r.passed, f"Expected fail for pure generic prose. Got: {r.score}"

    def test_mechanism_vocab_override_passes(self) -> None:
        """Proof bundle mechanism_vocab allows non-standard terms to pass."""
        r = check_bullet_technical_specificity_floor(
            "bul_ibm_004",
            "Established near-real-time ingestion pipelines for lineage tracking.",
            mechanism_vocab=["lineage", "ingestion", "observability"],
        )
        assert r.passed, "Expected pass when mechanism_vocab term present in bullet text"


class TestBulletQualityFloorRunner:
    def test_all_five_ibm_slots_run_through_gates(self) -> None:
        bullets = [
            {"bullet_id": "bul_ibm_001",
             "bullet_text": "Architected cloud-native AI platforms achieving 99.9% uptime for regulated financial services."},
            {"bullet_id": "bul_ibm_002",
             "bullet_text": "Led cloud infrastructure modernization reducing overhead by 30% across enterprise deployments."},
            {"bullet_id": "bul_ibm_003",
             "bullet_text": "Converted regulatory workflows into SaaS platforms improving renewal rates by 25%."},
            {"bullet_id": "bul_ibm_004",
             "bullet_text": "Engineered data lineage and observability frameworks cutting latency by 50%."},
            {"bullet_id": "bul_ibm_005",
             "bullet_text": "Structured hyperscaler alliances generating $15M in incremental co-sell revenue."},
        ]
        from apps_rg.runtime.sections.ibm_bullets_graph_evidence import IBM_BULLET_MECHANISM_VOCAB

        sen_pass, _, tech_pass, _, cons_pass, cons_results = run_bullet_quality_floor_gates(
            bullets,
            section_id="ibm_bullets",
            mechanism_vocab_by_slot=IBM_BULLET_MECHANISM_VOCAB,
        )
        assert sen_pass, "All IBM bullets should pass seniority floor"
        assert tech_pass, "All IBM bullets should pass technical specificity floor"
        assert cons_pass, f"All IBM bullets should pass consulting gate; failures: {[r.failure_reason for r in cons_results if r.failure_reason]}"
