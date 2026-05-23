"""P2-W1 competencies graph-skills proof pool."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from apps_rg.fact_inventory.competencies_graph_skills_proof_pool import (
    C03_STATUS_COMPETENCIES_GRAPH_PROOF,
    P2_W1_RECEIPT_JSON,
    build_competencies_graph_skills_proof_payload,
    validate_competencies_graph_skills_proof_payload,
    write_p2_w1_competencies_graph_proof_pool_receipt,
    CompetenciesGraphProofPoolError,
)
from apps_rg.fact_inventory.track_weighted_graph_expansion import ROOT
from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    PROOF_SOURCE_BROAD_SKILLS_LEDGER,
    resolve_section_proof_pool,
)

REPO = ROOT


@pytest.fixture(autouse=True)
def _proof_pool_fixture_dev_bypass() -> None:
    from apps_rg.runtime.spine.front_contracts import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


HYBRID_JD = (
    "SVP Engineering — Agentic AI platform leader for regulated financial services. "
    "Must show governed agentic runtime, GraphRAG, multi-agent orchestration, and policy gates. "
    "Also value actuarial rigor, derivatives risk, and Basel/CCAR lineage plus "
    "AWS cloud data platform and partner GTM co-sell experience."
)


def test_graph_proof_pool_resolves_augmented_skills_graph() -> None:
    pool = resolve_section_proof_pool(
        section="competencies",
        repo_root=REPO,
        target_role="SVP Engineering Agentic AI",
        jd_text=HYBRID_JD,
    )
    assert pool.proof_source == PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    meta = pool.proof_pool_metadata
    assert meta.get("proof_pool_type") == "augmented_skills_graph"
    assert meta.get("broad_skills_ledger_used_as_authority") is False
    assert meta.get("graph_skills_proof_pool") is True
    c03 = str(meta.get("c03_graph_bound_status") or "")
    if c03 == "BOUND":
        assert int(meta.get("c03_graph_hop_paths_count") or 0) > 0


def test_broad_skills_authority_fails_on_graph_payload() -> None:
    payload = build_competencies_graph_skills_proof_payload(repo_root=REPO)
    bad = {**payload, "broad_skills_ledger_used_as_authority": True}
    with pytest.raises(CompetenciesGraphProofPoolError):
        validate_competencies_graph_skills_proof_payload(bad)


def test_every_skill_has_fact_links_and_graph_support() -> None:
    payload = build_competencies_graph_skills_proof_payload(repo_root=REPO)
    for sk in payload.get("selected_skill_rows") or []:
        assert sk.get("fact_id_links"), sk.get("skill_id")
        assert sk.get("graph_hop_path") or sk.get("graph_support_ref")


def test_p2_w1_receipt_written_and_validates() -> None:
    out = write_p2_w1_competencies_graph_proof_pool_receipt(repo_root=REPO)
    assert P2_W1_RECEIPT_JSON.is_file()
    receipt = json.loads(P2_W1_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert receipt["proof_pool_type"] == "augmented_skills_graph"
    assert receipt["section_id"] == "competencies"
    assert receipt["every_skill_has_fact_id_links"] is True
    assert receipt["every_skill_has_graph_support"] is True
    assert receipt["broad_skills_ledger_used_as_authority"] is False
    assert receipt["c03_graph_bound_status"] in (C03_STATUS_COMPETENCIES_GRAPH_PROOF, "BOUND")
    assert receipt.get("broad_skills_ledger_default") is False
    assert (REPO / receipt["p1_w4_closeout_receipt_ref"]).is_file()
    assert (REPO / receipt["p1_w5_projection_receipt_ref"]).is_file()
