"""W14b — senior-role taxonomy IDs wired to projection track weights."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from apps_rg.fact_inventory.selected_role_fact_set import infer_role_family_priorities
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    ROLE_FAMILY_TRACK_WEIGHTS,
    SENIOR_ROLE_TAXONOMY_IDS,
    TAXONOMY_TO_PROJECTION_ROLE,
    infer_projection_role_family_key,
    resolve_career_track_weights,
)

REPO = Path(__file__).resolve().parents[4]
FIXTURE_ROOT = REPO / "docs/reports/apps_rg/fixtures/senior_roles"
MANIFEST = json.loads((FIXTURE_ROOT / "senior_role_fixture_manifest.json").read_text(encoding="utf-8"))
TAXONOMY = yaml.safe_load(
    (REPO / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml").read_text(encoding="utf-8")
)


@pytest.mark.parametrize(
    "taxonomy_id,profile_key",
    [
        ("INSURANCE_CARRIER_TRANSFORMATION", "INSURANCE_CARRIER_TRANSFORMATION"),
        ("INSURER_IT_AI_ENABLEMENT", "INSURER_IT_AI_ENABLEMENT"),
        ("INSURANCE_BROKERAGE_IT_INNOVATION", "INSURANCE_BROKERAGE_IT_INNOVATION"),
        ("BANKING_PLATFORM_AI", "BANKING_PLATFORM_AI"),
        ("REGULATED_AI_GOVERNANCE", "REGULATED_AI_GOVERNANCE"),
        ("PARTNER_APPLIED_AI_ARCHITECTURE", "PARTNER_APPLIED_AI_ARCHITECTURE"),
        ("HYPERSCALER_MARKETPLACE_GTM", "HYPERSCALER_MARKETPLACE_GTM"),
        ("CONSULTING_DELIVERY_LEADERSHIP", "CONSULTING_DELIVERY_LEADERSHIP"),
        ("PARTNERSHIPS_GTM", "ANTHROPIC_PARTNERSHIPS_APPLIED_AI"),
    ],
)
def test_taxonomy_maps_to_projection_profile(taxonomy_id: str, profile_key: str) -> None:
    assert TAXONOMY_TO_PROJECTION_ROLE[taxonomy_id] == profile_key
    assert profile_key in ROLE_FAMILY_TRACK_WEIGHTS
    weights = ROLE_FAMILY_TRACK_WEIGHTS[profile_key]
    assert sum(weights.values()) == pytest.approx(1.0, abs=0.02)


def test_senior_taxonomy_ids_subset_of_mapping() -> None:
    for tid in SENIOR_ROLE_TAXONOMY_IDS:
        assert tid in TAXONOMY_TO_PROJECTION_ROLE
        assert TAXONOMY_TO_PROJECTION_ROLE[tid] in ROLE_FAMILY_TRACK_WEIGHTS


def test_carrier_fixture_infers_carrier_projection() -> None:
    entry = next(a for a in MANIFEST["archetypes"] if a["slug"] == "aig_carrier_agentic")
    jd = (FIXTURE_ROOT / "aig_carrier_agentic_jd.txt").read_text(encoding="utf-8")
    brief = (FIXTURE_ROOT / "aig_carrier_agentic_brief.txt").read_text(encoding="utf-8")
    key = infer_projection_role_family_key(
        target_role=jd.split("\n", 1)[0],
        jd_text=jd,
        briefing_text=brief,
        taxonomy=TAXONOMY,
    )
    assert key == "INSURANCE_CARRIER_TRANSFORMATION"
    w = resolve_career_track_weights(role_family_key=key, jd_text=jd)
    assert w["track_actuarial_risk_derivatives"] == pytest.approx(0.35, abs=0.02)
    assert w["track_genai_agentic"] == pytest.approx(0.40, abs=0.02)


def test_consulting_fixture_infers_consulting_projection() -> None:
    entry = next(a for a in MANIFEST["archetypes"] if a["slug"] == "ai_data_platform_professional_services")
    jd = (FIXTURE_ROOT / "ai_data_platform_professional_services_jd.txt").read_text(encoding="utf-8")
    brief = (FIXTURE_ROOT / "ai_data_platform_professional_services_brief.txt").read_text(encoding="utf-8")
    key = infer_projection_role_family_key(
        target_role=jd.split("\n", 1)[0],
        jd_text=jd,
        briefing_text=brief,
        taxonomy=TAXONOMY,
    )
    assert key == "CONSULTING_DELIVERY_LEADERSHIP"
    priorities = infer_role_family_priorities(
        target_role=jd.split("\n", 1)[0],
        jd_text=jd,
        briefing_text=brief,
        taxonomy=TAXONOMY,
    )
    assert any(p.role_family == "CONSULTING_DELIVERY_LEADERSHIP" and p.score > 0 for p in priorities)


def test_manifest_override_matches_inferred_weights_for_all_archetypes() -> None:
    for entry in MANIFEST["archetypes"]:
        slug = entry["slug"]
        jd_path = entry["jd_path"]
        if jd_path.startswith("artifacts/"):
            jd = (REPO / jd_path).read_text(encoding="utf-8")
            brief = (REPO / entry["brief_path"]).read_text(encoding="utf-8")
        else:
            jd = (REPO / jd_path).read_text(encoding="utf-8")
            brief = (REPO / entry["brief_path"]).read_text(encoding="utf-8")
        key = infer_projection_role_family_key(
            target_role=jd.split("\n", 1)[0],
            jd_text=jd,
            briefing_text=brief,
            taxonomy=TAXONOMY,
        )
        inferred = resolve_career_track_weights(role_family_key=key, jd_text="")
        manifest_ov = entry.get("weight_override") or {}
        for track in ("track_actuarial_risk_derivatives", "track_data_tech_cloud_ml", "track_genai_agentic"):
            assert inferred[track] == pytest.approx(float(manifest_ov[track]), abs=0.02), (
                f"{slug} track {track}: inferred={inferred[track]} manifest={manifest_ov.get(track)} key={key}"
            )
