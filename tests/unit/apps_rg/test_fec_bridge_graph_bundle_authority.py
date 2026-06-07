"""FEC bridge must preserve graph bundle authority keys for all rigor lanes (June 2026)."""
from __future__ import annotations

import importlib

import pytest

from apps_rg.runtime.proof_pool_resolver import SectionProofPool


def _minimal_pool(*, section: str, pp_meta: dict) -> SectionProofPool:
    return SectionProofPool(
        section=section,
        proof_source="augmented_skills_graph",
        proof_pool_ref="apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        proof_pool_digest="digest-test",
        selected_fact_plan={"facts": [{"fact_id": "bul_test_001", "claim_text": "x"}]},
        allowed_fact_ids_ordered=["bul_test_001"],
        allowed_fact_ids={"bul_test_001"},
        bullet_rows=[],
        proof_pool_metadata=pp_meta,
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="base.json",
        base_resume_json_hash="hash",
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=False,
    )


@pytest.mark.parametrize(
    ("section_id", "attach_fn", "expected_keys"),
    [
        (
            "headline",
            "apps_rg.runtime.sections.headline_positioning_evidence.attach_headline_positioning_bundles_to_proof_pool_metadata",
            (
                "headline_positioning_bundle_consumption",
                "headline_positioning_bundles",
                "headline_positioning_bundle_ids",
                "graph_expansion_consumes_headline_positioning_bundles",
            ),
        ),
        (
            "ibm_bullets",
            "apps_rg.runtime.sections.ibm_role_episode_evidence.attach_role_episode_bundles_to_proof_pool_metadata",
            (
                "role_episode_bundle_consumption",
                "role_episode_bundles",
                "role_episode_bundle_ids",
                "ibm_role_episode_section_packet",
                "flat_skill_only_graph_context_forbidden",
            ),
        ),
        (
            "unify_narrative",
            "apps_rg.runtime.sections.unify_role_episode_evidence.attach_role_episode_bundles_to_proof_pool_metadata",
            (
                "role_episode_bundle_consumption",
                "role_episode_bundles",
                "unify_role_episode_section_packet",
            ),
        ),
    ],
)
def test_fec_bridge_preserves_graph_bundle_authority(
    section_id: str,
    attach_fn: str,
    expected_keys: tuple[str, ...],
) -> None:
    mod_path, fn_name = attach_fn.rsplit(".", 1)
    attach = getattr(importlib.import_module(mod_path), fn_name)
    pp_meta = attach(
        {
            "proof_pool_type": "augmented_skills_graph",
            "augmented_skills_graph_present": True,
            "c03_graphrag_bound": {"support_status": "SUPPORTED"},
        },
        section_id=section_id,
    )
    from apps_rg.runtime.spine.c0_fec_compose import _build_pa_proof_authority_metadata

    pool = _minimal_pool(section=section_id, pp_meta=pp_meta)
    pa_meta = _build_pa_proof_authority_metadata(
        pp_meta,
        pool=pool,
        route_contract_ref="route:test",
    )
    for key in expected_keys:
        assert key in pa_meta, f"missing {key} in PA metadata for {section_id}"
        assert pa_meta[key] == pp_meta[key], f"PA metadata dropped or mutated {key}"
