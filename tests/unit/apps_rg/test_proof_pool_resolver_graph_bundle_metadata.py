"""Regression tests: proof_pool_resolver attaches graph bundle metadata per section.

Validates wiring from commit 914f6dff9a (headline positioning, competency capability,
IBM/unify role-episode bundles) through ``resolve_section_proof_pool`` metadata.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

REPO = Path(__file__).resolve().parents[3]
LEDGER_PATH = default_ledger_path(REPO)

_BUNDLE_CASES: tuple[tuple[str, str], ...] = (
    ("headline", "headline_positioning_bundle_consumption"),
    ("competencies", "competency_capability_bundle_consumption"),
    ("ibm_bullets", "role_episode_bundle_consumption"),
    ("ibm_narrative", "role_episode_bundle_consumption"),
    ("unify_bullets", "role_episode_bundle_consumption"),
    ("unify_narrative", "role_episode_bundle_consumption"),
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


@pytest.mark.parametrize("section_id,consumption_key", _BUNDLE_CASES)
def test_resolve_section_proof_pool_attaches_bundle_consumption_flags(
    section_id: str,
    consumption_key: str,
) -> None:
    if not LEDGER_PATH.is_file():
        pytest.skip(f"ledger missing: {LEDGER_PATH}")
    pool = resolve_section_proof_pool(
        section=section_id,
        repo_root=REPO,
        product_visible=False,
        jd_text="Lead agentic AI platform engineering for regulated enterprise.",
        briefing_text="Emphasize governed runtime and GraphRAG.",
    )
    meta = pool.proof_pool_metadata or {}
    assert meta.get(consumption_key) is True, (
        f"{section_id}: expected {consumption_key}=True in proof_pool_metadata"
    )


@pytest.mark.parametrize(
    "section_id,bundles_key,ids_key",
    [
        ("headline", "headline_positioning_bundles", "headline_positioning_bundle_ids"),
        ("competencies", "competency_capability_bundles", "competency_bundle_ids"),
        ("ibm_bullets", "role_episode_bundles", "role_episode_bundle_ids"),
        ("unify_narrative", "role_episode_bundles", "role_episode_bundle_ids"),
    ],
)
def test_resolve_section_proof_pool_includes_non_empty_bundle_lists(
    section_id: str,
    bundles_key: str,
    ids_key: str,
) -> None:
    if not LEDGER_PATH.is_file():
        pytest.skip(f"ledger missing: {LEDGER_PATH}")
    pool = resolve_section_proof_pool(section=section_id, repo_root=REPO, product_visible=False)
    meta = pool.proof_pool_metadata or {}
    bundles = meta.get(bundles_key)
    bundle_ids = meta.get(ids_key)
    assert isinstance(bundles, list) and bundles, f"{section_id}: missing {bundles_key}"
    assert isinstance(bundle_ids, list) and bundle_ids, f"{section_id}: missing {ids_key}"
