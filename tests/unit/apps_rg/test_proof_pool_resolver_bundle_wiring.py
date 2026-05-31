"""Regression: graph bundle metadata is attached for rigor lanes (proof-pool resolver seam).

Uses attach_* helpers directly so tests stay deterministic without artifacts ledger fixtures.
Full resolve_section_proof_pool integration is covered in tests/_apps_contract when ledger exists.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    ("section_id", "attach_callable", "meta_key"),
    [
        (
            "ibm_bullets",
            "apps_rg.runtime.sections.ibm_role_episode_evidence.attach_role_episode_bundles_to_proof_pool_metadata",
            "role_episode_bundles",
        ),
        (
            "unify_bullets",
            "apps_rg.runtime.sections.unify_role_episode_evidence.attach_role_episode_bundles_to_proof_pool_metadata",
            "role_episode_bundles",
        ),
        (
            "headline",
            "apps_rg.runtime.sections.headline_positioning_evidence.attach_headline_positioning_bundles_to_proof_pool_metadata",
            "headline_positioning_bundles",
        ),
        (
            "competencies",
            "apps_rg.runtime.sections.competency_capability_evidence.attach_competency_bundles_to_proof_pool_metadata",
            "competency_capability_bundles",
        ),
    ],
)
def test_bundle_attach_helpers_populate_proof_pool_metadata(
    section_id: str, attach_callable: str, meta_key: str
) -> None:
    import importlib

    mod_path, fn_name = attach_callable.rsplit(".", 1)
    attach = getattr(importlib.import_module(mod_path), fn_name)
    meta = attach({}, section_id=section_id, repo_root=REPO)
    bundles = meta.get(meta_key)
    assert isinstance(bundles, list) and bundles, (
        f"{section_id}: expected non-empty {meta_key} after attach"
    )
