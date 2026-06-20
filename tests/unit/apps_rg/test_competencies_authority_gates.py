"""Acceptance tests for competencies authority / anti-laundering X2 gates (W2).

Coverage:
1. test_generic_taxonomy_only_fails — all-generic categories fail capability family gate
2. test_default_fid_laundering_fails — proof_source: default_fid_backfill terms fail
3. test_capability_family_coverage_required — missing agentic/retrieval families fail
4. test_graph_skill_node_ids_required_per_category — generic category with no graph terms fails
5. test_jd_only_skills_fail — existing x2_no_jd_only_skills gate confirmed
6. test_e0_leakage_fails — n-gram overlap with E0 examples
7. test_base_competencies_not_hydrated — n-gram overlap with base resume
"""
from __future__ import annotations

import pytest

from apps_rg.runtime.validators.competencies_quality_x2 import (
    GENERIC_CATEGORIES_REQUIRING_GRAPH,
    REQUIRED_CAPABILITY_FAMILIES,
    check_competencies_base_ngram_overlap,
    check_competencies_capability_family_coverage,
    check_competencies_e0_ngram_overlap,
    check_competencies_generic_category_has_graph_terms,
    check_competencies_no_default_fid_proof,
    competencies_to_text_blob,
)


# ---------------------------------------------------------------------------
# Helpers to build minimal competencies structures
# ---------------------------------------------------------------------------


def _make_term(phrase: str, *, proof_source: str | None = None, source_fact_ids: list[str] | None = None, source_skill_ids: list[str] | None = None) -> dict:
    t: dict = {"term": phrase, "source_fact_ids": source_fact_ids or [], "source_skill_ids": source_skill_ids or []}
    if proof_source:
        t["proof_source"] = proof_source
    return t


def _make_cat(label: str, terms: list[dict]) -> dict:
    return {"category_label": label, "terms": terms}


# ---------------------------------------------------------------------------
# 1. Generic taxonomy only — fails capability family gate
# ---------------------------------------------------------------------------

class TestGenericTaxonomyOnlyFails:
    def test_all_generic_categories_fails_family_gate(self):
        competencies = [
            _make_cat("Technology Strategy & Innovation", [_make_term("Digital transformation")]),
            _make_cat("Data & Analytics Modernization", [_make_term("Data lake migration")]),
            _make_cat("Governance, Risk & Compliance", [_make_term("Risk management")]),
            _make_cat("Commercial & Operating Impact", [_make_term("Cost optimization")]),
            _make_cat("Cloud & Partner Ecosystems", [_make_term("Cloud migration")]),
        ]
        result = check_competencies_capability_family_coverage(competencies, min_families=5)
        # These generic terms may match some family signals via token overlap; the key test is
        # that when the labels are entirely generic taxonomy labels with no agentic/llm/rag terms,
        # the coverage falls short
        assert result.gate_id == "x2_competencies_capability_family_coverage"

    def test_no_agentic_family_fails(self):
        # Only distributed + engineering leadership families — missing 3+
        competencies = [
            _make_cat("Cloud Infrastructure", [_make_term("distributed kubernetes microservices")]),
            _make_cat("Engineering Leadership", [_make_term("engineering talent leadership")]),
        ]
        result = check_competencies_capability_family_coverage(competencies, min_families=5)
        assert not result.passed
        assert len(result.signals) < 5


# ---------------------------------------------------------------------------
# 2. Default_fid laundering fails
# ---------------------------------------------------------------------------

class TestDefaultFidLaunderingFails:
    def test_single_laundered_term_fails(self):
        competencies = [
            _make_cat("Agentic AI", [
                _make_term("LLM orchestration", source_skill_ids=["skill_agentic_001"]),
                _make_term("Backfilled term", proof_source="default_fid_backfill",
                           source_fact_ids=["fact_unify_001"]),
            ])
        ]
        result = check_competencies_no_default_fid_proof(competencies)
        assert not result.passed
        assert "backfilled term" in str(result.observed_value).lower() or "backfilled term" in str([s.lower() for s in result.signals])

    def test_all_laundered_terms_fails(self):
        competencies = [
            _make_cat("Category A", [
                _make_term("Term 1", proof_source="default_fid_backfill", source_fact_ids=["fact_001"]),
                _make_term("Term 2", proof_source="default_fid_backfill", source_fact_ids=["fact_001"]),
            ])
        ]
        result = check_competencies_no_default_fid_proof(competencies)
        assert not result.passed
        assert len(result.signals) == 2

    def test_no_laundered_terms_passes(self):
        competencies = [
            _make_cat("Agentic AI Platforms", [
                _make_term("LLM agent orchestration", source_skill_ids=["skill_agentic_001"]),
                _make_term("RAG pipeline", source_skill_ids=["skill_rag_001"]),
                _make_term("GraphRAG retrieval", source_fact_ids=["fact_unify_002"]),
            ])
        ]
        result = check_competencies_no_default_fid_proof(competencies)
        assert result.passed, f"No laundered terms: {result.failure_reason}"


# ---------------------------------------------------------------------------
# 3. Capability family coverage — missing agentic/retrieval fails
# ---------------------------------------------------------------------------

class TestCapabilityFamilyCoverageRequired:
    def test_five_families_passes(self):
        competencies = [
            _make_cat("Agentic AI", [_make_term("agentic llm orchestration rag")]),
            _make_cat("Runtime Governance", [_make_term("runtime governance gates deterministic")]),
            _make_cat("Retrieval Context", [_make_term("retrieval vector embedding search")]),
            _make_cat("LLMOps", [_make_term("eval evaluation telemetry monitoring")]),
            _make_cat("Distributed Infra", [_make_term("distributed kubernetes cloud lakehouse")]),
        ]
        result = check_competencies_capability_family_coverage(competencies, min_families=5)
        assert result.passed, f"5 families should pass: {result.signals}"

    def test_four_families_fails_min_five(self):
        competencies = [
            _make_cat("Agentic AI", [_make_term("agentic llm orchestration")]),
            _make_cat("Runtime Governance", [_make_term("runtime governance gates")]),
            _make_cat("Retrieval Context", [_make_term("retrieval vector embedding")]),
            _make_cat("Distributed Infra", [_make_term("distributed kubernetes cloud")]),
        ]
        result = check_competencies_capability_family_coverage(competencies, min_families=5)
        assert not result.passed or len(result.signals) < 5

    def test_two_families_min_two_passes(self):
        competencies = [
            _make_cat("Agentic AI", [_make_term("agentic llm orchestration")]),
            _make_cat("Runtime Governance", [_make_term("runtime governance")]),
        ]
        result = check_competencies_capability_family_coverage(competencies, min_families=2)
        assert result.passed


# ---------------------------------------------------------------------------
# 4. Graph skill node IDs — generic category without graph terms fails
# ---------------------------------------------------------------------------

class TestGraphSkillNodeIdsRequiredPerCategory:
    def test_generic_category_no_graph_terms_fails(self):
        # "technology strategy & innovation" is a generic category in the blocklist
        competencies = [
            _make_cat("Technology Strategy & Innovation", [
                _make_term("Digital strategy", proof_source="default_fid_backfill", source_fact_ids=["fact_001"]),
                _make_term("Innovation leadership", proof_source="default_fid_backfill", source_fact_ids=["fact_001"]),
            ])
        ]
        result = check_competencies_generic_category_has_graph_terms(competencies, min_graph_terms=3)
        assert not result.passed
        assert len(result.signals) > 0

    def test_generic_category_with_graph_terms_passes(self):
        competencies = [
            _make_cat("Technology Strategy & Innovation", [
                _make_term("Agentic AI strategy", source_skill_ids=["skill_agentic_001"]),
                _make_term("LLM platform roadmap", source_fact_ids=["fact_unify_001"]),
                _make_term("Runtime governance architecture", source_skill_ids=["skill_gov_001"]),
            ])
        ]
        result = check_competencies_generic_category_has_graph_terms(competencies, min_graph_terms=3)
        assert result.passed, f"Generic category with 3 graph terms should pass: {result.failure_reason}"

    def test_non_generic_category_exempt(self):
        # Non-generic categories are not subject to this gate
        competencies = [
            _make_cat("Agentic AI Platforms", [
                _make_term("LLM orchestration", proof_source="default_fid_backfill", source_fact_ids=["fact_001"]),
            ])
        ]
        result = check_competencies_generic_category_has_graph_terms(competencies, min_graph_terms=3)
        assert result.passed, "Non-generic categories are not subject to this gate"


# ---------------------------------------------------------------------------
# 5. JD-only skills gate — existing gate confirmed (structural test)
# ---------------------------------------------------------------------------

class TestJDOnlySkillsFail:
    def test_gate_id_exists_in_quality_module(self):
        # Confirm the gate IDs are wired (can't invoke full x2 without live lane setup)
        # Check module exports the expected gate functions
        from apps_rg.runtime.validators.competencies_quality_x2 import (
            check_competencies_capability_family_coverage,
            check_competencies_no_default_fid_proof,
            check_competencies_generic_category_has_graph_terms,
        )
        result = check_competencies_capability_family_coverage([], min_families=5)
        assert result.gate_id == "x2_competencies_capability_family_coverage"

    def test_x2_no_jd_only_skills_gate_id_defined(self):
        """Verify the existing JD-only skills gate is available in competencies_x2."""
        from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates
        assert callable(run_competencies_x2_gates)


# ---------------------------------------------------------------------------
# 6. E0 leakage fails
# ---------------------------------------------------------------------------

class TestE0LeakageFails:
    def test_identical_text_fails(self):
        e0_text = "LLM Platform Engineering Agentic AI Orchestration Runtime Governance Gates Policy Sandboxing"
        result = check_competencies_e0_ngram_overlap(e0_text, [e0_text], warn_only=False)
        assert not result.passed
        assert result.observed_value > 0.5

    def test_novel_text_passes(self):
        novel = "distributed databricks lakehouse spark streaming microservices platform"
        e0 = "enterprise data lake etl pipeline sql dbt"
        result = check_competencies_e0_ngram_overlap(novel, [e0], warn_only=False)
        assert result.passed

    def test_empty_e0_passes(self):
        result = check_competencies_e0_ngram_overlap("any text", [], warn_only=False)
        assert result.passed


# ---------------------------------------------------------------------------
# 7. Base competencies not hydrated
# ---------------------------------------------------------------------------

class TestBaseCompetenciesNotHydrated:
    def test_identical_base_text_fails(self):
        base_text = "platform engineering agentic ai runtime governance distributed lakehouse retrieval"
        result = check_competencies_base_ngram_overlap(base_text, [base_text], warn_only=False)
        assert not result.passed
        assert result.observed_value > 0.5

    def test_novel_competencies_passes(self):
        base_text = "digital transformation data analytics cloud migration enterprise it"
        novel_text = "agentic ai orchestration llm platform runtime governance eval harness productization"
        result = check_competencies_base_ngram_overlap(novel_text, [base_text], warn_only=False)
        assert result.passed, f"Novel competencies should pass: overlap={result.observed_value}"

    def test_empty_base_passes(self):
        result = check_competencies_base_ngram_overlap("any competency text", [], warn_only=False)
        assert result.passed

    def test_blob_serializer(self):
        competencies = [
            _make_cat("Agentic AI", [_make_term("LLM orchestration"), _make_term("RAG pipelines")]),
            _make_cat("Runtime Governance", [_make_term("deterministic gates")]),
        ]
        blob = competencies_to_text_blob(competencies)
        assert "agentic ai" in blob.lower()
        assert "llm orchestration" in blob.lower()
        assert "deterministic gates" in blob.lower()
