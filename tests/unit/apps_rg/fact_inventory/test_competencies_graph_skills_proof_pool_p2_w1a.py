"""P2-W1A: competencies product authority is augmented_skills_graph only."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.competencies_graph_skills_proof_pool import (
    DEPRECATED_LEDGER_CODE_PATHS,
    P2_W1A_RECEIPT_JSON,
    build_competencies_graph_skills_proof_payload,
    validate_p2_w1a_default_graph_authority_receipt,
    write_p2_w1a_default_graph_authority_receipt,
    CompetenciesGraphProofPoolError,
)
from apps_rg.fact_inventory.track_weighted_graph_expansion import ROOT
from apps_rg.runtime.legacy_proof_sources import PROOF_SOURCE_BROAD_SKILLS_LEDGER
from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    resolve_section_proof_pool,
)
import apps_rg.runtime.proof_pool_resolver as proof_pool_resolver

REPO = ROOT
HYBRID_JD = (
    "SVP Engineering — Agentic AI platform leader for regulated financial services. "
    "Must show governed agentic runtime, GraphRAG, multi-agent orchestration, and policy gates. "
    "Also value actuarial rigor, derivatives risk, and Basel/CCAR lineage plus "
    "AWS cloud data platform and partner GTM co-sell experience."
)


@pytest.fixture(autouse=True)
def _proof_pool_fixture_dev_bypass() -> None:
    from apps_rg.runtime.spine.front_contracts import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


def test_default_competencies_resolves_augmented_skills_graph() -> None:
    pool = resolve_section_proof_pool(
        section="competencies",
        repo_root=REPO,
        target_role="SVP Engineering Agentic AI",
        jd_text=HYBRID_JD,
    )
    assert pool.proof_source == PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    assert pool.proof_pool_metadata.get("proof_pool_type") == "augmented_skills_graph"
    assert pool.broad_skills_ledger_present is False
    assert pool.proof_pool_metadata.get("broad_skills_ledger_used_as_authority") is False


def test_graph_proof_pool_supports_graph_10x6_product_shape() -> None:
    from apps_rg.runtime.sections.competencies_rigor import (
        CANDIDATE_CATEGORY_COUNT,
        MAX_CATEGORY_COUNT,
        MIN_CATEGORY_COUNT,
    )

    pool = resolve_section_proof_pool(
        section="competencies",
        repo_root=REPO,
        target_role="SVP Engineering Agentic AI",
        jd_text=HYBRID_JD,
    )
    assert MIN_CATEGORY_COUNT == MAX_CATEGORY_COUNT == 6
    # Variance-class alignment (2026-06): candidate pool 10 -> 8 (>= final 6).
    assert CANDIDATE_CATEGORY_COUNT == 8
    assert pool.proof_pool_metadata.get("proof_pool_type") == "augmented_skills_graph"
    assert isinstance(pool.proof_pool_metadata.get("selected_skill_rows"), list)


def test_no_path_selects_broad_skills_ledger_as_authority() -> None:
    pool = resolve_section_proof_pool(section="competencies", repo_root=REPO, jd_text=HYBRID_JD)
    assert pool.proof_source != PROOF_SOURCE_BROAD_SKILLS_LEDGER
    assert pool.proof_pool_metadata.get("proof_pool_type") != "broad_skills_ledger_competencies"


def test_legacy_broad_skills_flag_rejected() -> None:
    with pytest.raises(ValueError, match="legacy_broad_skills_ledger"):
        resolve_section_proof_pool(
            section="competencies",
            repo_root=REPO,
            legacy_broad_skills_ledger=True,
        )


def test_legacy_allocate_from_ledger_removed_from_product_resolver() -> None:
    assert not hasattr(proof_pool_resolver, "_allocate_from_ledger")


def test_graph_unavailable_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    def _blocked(*_a: object, **_k: object) -> dict:
        return {
            "skills_authority_status": "BLOCKED",
            "skills_authority_block_reason": "test_block",
        }

    monkeypatch.setattr(
        "apps_rg.runtime.proof_pool_resolver.resolve_augmented_skills_graph_authority",
        _blocked,
    )
    with pytest.raises(ValueError, match="BLOCKED|graph-skills"):
        resolve_section_proof_pool(section="competencies", repo_root=REPO, jd_text=HYBRID_JD)


def test_p2_w1a_receipt() -> None:
    out = write_p2_w1a_default_graph_authority_receipt(repo_root=REPO)
    assert P2_W1A_RECEIPT_JSON.is_file()
    receipt = json.loads(P2_W1A_RECEIPT_JSON.read_text(encoding="utf-8"))
    validate_p2_w1a_default_graph_authority_receipt(receipt)
    assert receipt["deprecated_ledger_code_reachable_from_product_path"] is False
    assert receipt["silent_fallback_possible"] is False
    assert len(receipt["deprecated_ledger_code_paths_remaining"]) >= 1


def test_every_skill_has_graph_support() -> None:
    payload = build_competencies_graph_skills_proof_payload(repo_root=REPO)
    for sk in payload.get("selected_skill_rows") or []:
        assert sk.get("fact_id_links")
        assert sk.get("graph_hop_path") or sk.get("graph_support_ref")
