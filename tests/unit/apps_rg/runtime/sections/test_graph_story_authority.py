"""Graph-only story authority — no base-resume bullet hydration."""
from __future__ import annotations

from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    SectionProofPool,
)
from apps_rg.runtime.sections.graph_story_authority import (
    forbid_base_resume_bullet_hydration,
    require_augmented_skills_graph_pool,
    verbatim_base_resume_bullet_ids,
)


def _pool() -> SectionProofPool:
    from apps_rg.runtime.product_evidence_authority import finalize_product_section_proof_pool

    raw = SectionProofPool(
        section="unify_bullets",
        proof_source=PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        proof_pool_ref="graph.json",
        proof_pool_digest="abc",
        selected_fact_plan={"facts": [{"fact_id": "bul_unify_001", "claim_text": "From ledger."}]},
        allowed_fact_ids_ordered=["bul_unify_001"],
        allowed_fact_ids={"bul_unify_001"},
        bullet_rows=[],
        proof_pool_metadata={
            "proof_pool_type": "augmented_skills_graph",
            "skills_authority_status": "PASS",
            "graph_ref": "graph.json",
            "claim_evidence_substrate_ref": "ledger.json",
            "base_resume_claim_authority": False,
        },
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="",
        base_resume_json_hash="",
        broad_skills_ledger_ref="ledger.json",
        broad_skills_ledger_digest="d",
        srfs_ref="",
        base_resume_override_used=False,
        targeting_inputs_used={},
    )
    return finalize_product_section_proof_pool(raw)


def test_require_augmented_skills_graph_pool_passes() -> None:
    require_augmented_skills_graph_pool(_pool(), section_id="unify_bullets")


def test_forbid_verbatim_base_resume_bullet_text() -> None:
    base = {
        "facts": {
            "employment": [
                {
                    "fact_id": "exp_unify_001",
                    "bullets": [{"bullet_id": "bul_unify_001", "text": "Legacy base bullet text here."}],
                }
            ]
        }
    }
    parsed = {
        "bullets": [{"bullet_id": "bul_unify_001", "bullet_text": "Legacy base bullet text here."}],
        "change_log": [],
    }

    def _never_hydrate(_rp: dict, _p: dict) -> bool:
        return False

    import pytest

    with pytest.raises(ValueError, match="verbatim-matches base resume"):
        forbid_base_resume_bullet_hydration(
            section_id="unify_bullets",
            runtime_payload={"proof_pool_metadata": {"proof_pool_type": "augmented_skills_graph"}},
            parsed=parsed,
            base_resume=base,
            would_hydrate_fn=_never_hydrate,
        )


def test_verbatim_detection_finds_match() -> None:
    base = {
        "facts": {
            "employment": [
                {
                    "fact_id": "exp_unify_001",
                    "bullets": [{"text": "Same words."}],
                }
            ]
        }
    }
    parsed = {"bullets": [{"bullet_id": "bul_unify_001", "bullet_text": "Same words."}]}
    assert verbatim_base_resume_bullet_ids(
        parsed, base_resume=base, section_id="unify_bullets"
    ) == ["bul_unify_001"]


def test_x2_gate_graph_only_rejects_srfs() -> None:
    from apps_rg.runtime.sections.graph_story_authority import x2_gate_graph_only_proof_pool

    ok, obs, exp, _detail = x2_gate_graph_only_proof_pool(
        {
            "evidence_authority": {
                "authority": "selected_role_fact_set",
                "graph_ref": "g.json",
                "ledger_ref": "l.json",
                "skills_authority_status": "PASS",
            },
        },
        section_id="unify_bullets",
    )
    assert ok is False
    assert obs == "selected_role_fact_set"
    assert exp == "augmented_skills_graph"


def test_x2_gate_graph_only_passes() -> None:
    from apps_rg.runtime.sections.graph_story_authority import x2_gate_graph_only_proof_pool

    ok, _, _, _ = x2_gate_graph_only_proof_pool(
        {
            "evidence_authority": {
                "authority": "augmented_skills_graph",
                "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
                "ledger_ref": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger.json",
                "skills_authority_status": "PASS",
            },
            "skills_authority_status": "PASS",
            "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
            "claim_evidence_substrate_ref": "artifacts/apps_rg/fact_inventory/ledger.json",
            "evidence_authority": {
                "authority": "augmented_skills_graph",
                "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
                "ledger_ref": "artifacts/apps_rg/fact_inventory/ledger.json",
                "skills_authority_status": "PASS",
            },
        },
        section_id="ibm_bullets",
    )
    assert ok is True
