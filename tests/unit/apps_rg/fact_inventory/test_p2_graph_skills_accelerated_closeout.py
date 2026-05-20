"""P2-ACCELERATED-CLOSEOUT unit and receipt validators."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.p2_graph_skills_accelerated_closeout import (
    ALL_SECTIONS,
    CLOSEOUT_JSON,
    REBASELINE_JSON,
    W1A_JSON,
    W2_JSON,
    run_full_closeout,
    write_p2_rebaseline,
    write_p2_w1a_all_sections,
)
from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS
from apps_rg.fact_inventory.track_weighted_graph_expansion import ROOT
from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool
from apps_rg.runtime.validators.graph_skills_proof_common import (
    GraphSkillsProofError,
    assert_pool_not_ledger_authority,
    validate_section_graph_pool,
)

REPO = ROOT


@pytest.fixture(autouse=True)
def _proof_pool_fixture_dev_bypass() -> None:
    from apps_rg.runtime.section_front_spine_bridge import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


@pytest.mark.parametrize(
    "section_id",
    tuple(s for s in SECTION_KEYS if s != "executive_summary"),
)
def test_all_sections_default_graph_pool(section_id: str) -> None:
    pool = resolve_section_proof_pool(
        section=section_id,
        repo_root=REPO,
        product_visible=False,
    )
    summary = validate_section_graph_pool(pool)
    assert summary["proof_source"] == "augmented_skills_graph"
    assert summary["broad_skills_ledger_used_as_authority"] is False


def test_legacy_ledger_flag_rejected() -> None:
    with pytest.raises(ValueError, match="legacy_broad_skills_ledger"):
        resolve_section_proof_pool(
            section="headline",
            repo_root=REPO,
            legacy_broad_skills_ledger=True,
            product_visible=False,
        )


def test_p2_rebaseline_artifact() -> None:
    doc = write_p2_rebaseline(repo_root=REPO)
    assert doc["broad_skills_ledger_product_authority_prohibited"] is True
    assert doc["global_c03_bound_claimed"] is False
    assert REBASELINE_JSON.is_file()


def test_p2_w1a_all_sections_receipt() -> None:
    doc = write_p2_w1a_all_sections(repo_root=REPO)
    assert doc["all_sections_default_to_augmented_skills_graph"] is True
    assert doc["broad_skills_ledger_used_as_authority_anywhere"] is False
    assert W1A_JSON.is_file()


def test_accelerated_closeout_skip_live() -> None:
    out = run_full_closeout(repo_root=REPO, skip_live=True)
    assert out["status"] in ("PASS", "PARTIAL")
    assert CLOSEOUT_JSON.is_file()
    w2 = json.loads(W2_JSON.read_text(encoding="utf-8"))
    assert set(w2["sections"].keys()) == set(ALL_SECTIONS)


def test_false_c03_bound_rejected() -> None:
    from apps_rg.runtime.proof_pool_resolver import SectionProofPool

    pool = SectionProofPool(
        section="headline",
        proof_source="augmented_skills_graph",
        proof_pool_ref="g",
        proof_pool_digest="d",
        selected_fact_plan={},
        allowed_fact_ids_ordered=[],
        allowed_fact_ids=set(),
        bullet_rows=[],
        proof_pool_metadata={
            "c03_graph_bound_status": "BOUND",
            "c03_graph_hop_paths_count": 0,
            "non_graph_evidence_items_count": 0,
            "broad_skills_ledger_used_as_authority": False,
        },
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="",
        base_resume_json_hash="",
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=False,
    )
    from apps_rg.runtime.validators.graph_skills_proof_common import assert_c03_bound_claim_valid

    assert_pool_not_ledger_authority(pool)
    with pytest.raises(GraphSkillsProofError):
        assert_c03_bound_claim_valid(section_id="headline", meta=pool.proof_pool_metadata)
