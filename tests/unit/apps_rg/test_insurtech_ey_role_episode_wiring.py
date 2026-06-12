"""W2 (apps-rg-insurtech-ey-unlock-a4c0f0) — InsurTech/EY registry + proof-pool wiring.

Deterministic, hermetic. Guards that the two new employer lanes resolve a NON-EMPTY proof pool
(closing REQUIRED_PROOF_ABSENT), with every bundle valid and every bound skill resolving.
"""
from __future__ import annotations

import pytest

from apps_rg.runtime.sections import (
    ey_graph_role_episode_registry as ey_reg,
    insurtech_graph_role_episode_registry as it_reg,
)
from apps_rg.runtime.sections.ey_role_episode_evidence import (
    EY_BULLET_SLOT_BUNDLE_MAP,
    attach_role_episode_bundles_to_proof_pool_metadata as attach_ey,
    build_ey_role_episode_section_packet,
)
from apps_rg.runtime.sections.insurtech_role_episode_evidence import (
    INSURTECH_BULLET_SLOT_BUNDLE_MAP,
    attach_role_episode_bundles_to_proof_pool_metadata as attach_it,
    build_insurtech_role_episode_section_packet,
)


@pytest.mark.parametrize("reg", [it_reg, ey_reg])
def test_all_bundles_pass_their_registry_validator(reg) -> None:
    bundles = reg.get_all_bundles()
    assert bundles, "registry returned no bundles"
    for b in bundles:
        ok, violations = reg.validate_bundle(b)
        assert ok, f"{b.get('role_episode_bundle_id')} invalid: {violations}"


@pytest.mark.parametrize(
    "build,section,n",
    [
        (build_insurtech_role_episode_section_packet, "insurtech_bullets", 12),
        (build_ey_role_episode_section_packet, "ey_bullets", 6),
    ],
)
def test_packet_nonempty_with_bound_skills(build, section, n) -> None:
    packet = build(section)
    assert len(packet["role_episode_bundles"]) == n
    # Every bundle must carry at least one resolved bound skill (grounding actually wired).
    for b in packet["role_episode_bundles"]:
        assert b["bound_skills"], f"{b['role_episode_bundle_id']} has no resolved bound skills"
    assert packet["consumption_mode"] == "role_episode_bundle_required"
    assert packet["base_resume_usage"] == "identity_spine_only"
    assert packet["graph_claim_authority_ids"] == packet["role_episode_bundle_ids"]
    assert packet["promotable_metric_outcome_ids"]
    assert packet["approved_metric_outcome_ids"] == packet["promotable_metric_outcome_ids"]
    for b in packet["role_episode_bundles"]:
        assert b["allowed_metric_outcome_ids"], (
            f"{b['role_episode_bundle_id']} dropped graph metric outcome IDs"
        )


@pytest.mark.parametrize(
    "attach,section",
    [
        (attach_it, "insurtech_bullets"),
        (attach_it, "insurtech_narrative"),
        (attach_ey, "ey_bullets"),
        (attach_ey, "ey_narrative"),
    ],
)
def test_proof_pool_metadata_populated(attach, section) -> None:
    meta = attach({}, section_id=section)
    assert meta.get("role_episode_bundle_consumption") is True
    assert meta.get("role_episode_bundles"), "proof pool still empty — REQUIRED_PROOF_ABSENT would fire"
    assert meta.get("role_episode_bundle_ids")
    assert meta.get("flat_skill_only_graph_context_forbidden") is True
    assert meta.get("approved_metric_outcome_ids")


def test_attach_is_noop_for_other_sections() -> None:
    # The InsurTech attacher must not touch EY/IBM sections and vice-versa.
    assert attach_it({"x": 1}, section_id="ey_bullets") == {"x": 1}
    assert attach_ey({"x": 1}, section_id="insurtech_bullets") == {"x": 1}
    assert attach_it({"x": 1}, section_id="ibm_bullets") == {"x": 1}


def test_slot_bundle_maps_cover_three_slots_and_reference_real_bundles() -> None:
    it_ids = {b["role_episode_bundle_id"] for b in it_reg.get_all_bundles()}
    ey_ids = {b["role_episode_bundle_id"] for b in ey_reg.get_all_bundles()}
    assert len(INSURTECH_BULLET_SLOT_BUNDLE_MAP) == 3
    assert set(INSURTECH_BULLET_SLOT_BUNDLE_MAP.values()) <= it_ids
    assert len(EY_BULLET_SLOT_BUNDLE_MAP) == 3
    assert set(EY_BULLET_SLOT_BUNDLE_MAP.values()) <= ey_ids
