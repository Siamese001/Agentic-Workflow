"""Wave 6: section specs keep graph as routing support, not default claim proof."""
from __future__ import annotations

from pathlib import Path

import yaml

from apps_rg.runtime.sections.section_spec import (
    CANONICAL_SECTION_IDS,
    SourceAuthoritySpec,
    get_section_spec,
    load_section_specs,
)

REPO = Path(__file__).resolve().parents[5]
PROFILE = REPO / "apps_rg" / "config" / "domain_contract" / "section_retrieval_profile.yaml"


def test_source_authority_defaults_match_wave6_policy() -> None:
    spec = SourceAuthoritySpec()
    assert spec.candidate_facts_as_proof is False
    assert spec.candidate_fact_lineage_allowed is True
    assert spec.graph_as_claim_proof is False
    assert spec.graph_as_routing_support is True
    assert spec.graph_claim_proof_allowed_only_when_fact_bound is True
    assert spec.jd_as_proof_allowed is False
    assert spec.briefing_as_proof_allowed is False
    assert spec.companion_context_authority is False


def test_effective_claim_proof_requires_graphdb_backed_proof_by_default() -> None:
    spec = SourceAuthoritySpec()
    assert spec.candidate_facts_may_prove_claim(fact_bound=True) is False
    assert spec.graph_may_prove_claim(fact_bound=True) is False
    assert spec.effective_claim_proof(fact_bound=True) is False
    assert spec.effective_claim_proof(fact_bound=False) is False


def test_candidate_facts_as_proof_true_is_deprecated_and_forced_closed() -> None:
    spec = SourceAuthoritySpec.from_mapping({"candidate_facts_as_proof": True})
    assert spec.candidate_facts_as_proof is False
    assert spec.candidate_fact_lineage_allowed is True
    assert spec.candidate_facts_may_prove_claim(fact_bound=True) is False


def test_graph_claim_proof_opt_in_still_requires_fact_bound() -> None:
    spec = SourceAuthoritySpec(graph_as_claim_proof=True)
    assert spec.graph_may_prove_claim(fact_bound=True) is True
    assert spec.graph_may_prove_claim(fact_bound=False) is False


def test_all_canonical_sections_have_wave6_source_authority_yaml() -> None:
    raw = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
    sections = {
        str(row.get("section_id")): row
        for row in raw.get("sections", [])
        if isinstance(row, dict)
    }
    assert set(CANONICAL_SECTION_IDS).issubset(sections)
    for section_id in CANONICAL_SECTION_IDS:
        authority = sections[section_id].get("source_authority")
        assert authority == {
            "candidate_facts_as_proof": False,
            "candidate_fact_lineage_allowed": True,
            "graph_as_claim_proof": False,
            "graph_as_routing_support": True,
            "graph_claim_proof_allowed_only_when_fact_bound": True,
            "jd_as_proof_allowed": False,
            "briefing_as_proof_allowed": False,
            "companion_context_authority": False,
        }


def test_loaded_section_specs_preserve_graph_routing_support_for_all_sections() -> None:
    specs = load_section_specs(PROFILE)
    assert tuple(specs) == CANONICAL_SECTION_IDS
    for section_id in CANONICAL_SECTION_IDS:
        spec = specs[section_id]
        assert spec.graph_expansion_allowed is True
        assert spec.graph_supports_routing() is True
        assert spec.source_authority.candidate_facts_as_proof is False
        assert spec.source_authority.candidate_fact_lineage_allowed is True
        assert spec.source_authority.graph_as_claim_proof is False
        assert spec.source_authority.graph_as_routing_support is True


def test_get_section_spec_resolves_single_lane() -> None:
    spec = get_section_spec("executive_summary", PROFILE)
    assert spec.section_id == "executive_summary"
    assert spec.graph_supports_routing() is True
    assert spec.source_authority.jd_as_proof_allowed is False
