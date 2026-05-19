"""CRO composite projection hardening — no standalone CRO role family; RevOps skills proof-bound."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    load_master_skills_arsenal_ledger,
    validate_arsenal_ledger_shape,
    validate_skill_row_for_external_output,
)

REPO = Path(__file__).resolve().parents[4]
LEDGER_PATH = REPO / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
TAXONOMY_PATH = REPO / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml"
COMPOSITE_PATH = REPO / "apps_rg/config/domain_contract/composite_projection_profiles.yaml"
GAP_JSON = REPO / "docs/reports/apps_rg/cro_projection_profile_gap_analysis.json"

PROFILE_ID = "CHIEF_REVENUE_OFFICER_COMPOSITE"
REVOPS_SKILL_IDS = (
    "skill_revops_salesforce_pipeline_analytics",
    "skill_revops_salesforce_forecast_pipeline",
    "skill_revops_usage_based_subscription_forecasting",
    "skill_revops_sales_forecasting_frameworks",
    "skill_revops_multi_channel_gtm_alignment",
)


@pytest.fixture
def ledger() -> dict:
    return load_master_skills_arsenal_ledger(path=LEDGER_PATH)


def test_taxonomy_has_no_standalone_cro_role_family() -> None:
    raw = TAXONOMY_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    ids = [rf["id"] for rf in data.get("role_families") or []]
    assert "CRO" not in ids
    assert "CHIEF_REVENUE_OFFICER" not in ids
    assert not any(re.search(r"\bCRO\b", str(rf.get("id", ""))) for rf in data.get("role_families") or [])


def test_composite_profile_registered_in_config_and_ledger(ledger: dict) -> None:
    composite = yaml.safe_load(COMPOSITE_PATH.read_text(encoding="utf-8"))
    profile_ids = [p["id"] for p in composite.get("composite_profiles") or []]
    assert PROFILE_ID in profile_ids
    profiles = ledger.get("role_family_projection_profiles") or {}
    assert PROFILE_ID in profiles
    prof = profiles[PROFILE_ID]
    assert prof.get("profile_kind") == "composite_role_family_projection"
    assert "REVENUE_OPERATIONS" in prof.get("taxonomy_ids") or []
    assert prof.get("role_family_weights", {}).get("REVENUE_OPERATIONS") == 1.0


def test_projection_profile_count_includes_cro_composite(ledger: dict) -> None:
    assert len(ledger["role_family_projection_profiles"]) == 9


def test_revops_pillar_exists_with_supported_facts(ledger: dict) -> None:
    pillars = {p["pillar_id"]: p for p in ledger.get("pillars") or []}
    assert "pillar_revenue_operations" in pillars
    links = set(pillars["pillar_revenue_operations"].get("linked_fact_ids") or [])
    assert "fact_revenue_ops_001" in links
    assert "fact_revenue_ops_002" in links
    assert "fact_revenue_ops_003" in links


@pytest.mark.parametrize("skill_id", REVOPS_SKILL_IDS)
def test_new_revops_skill_rows_have_role_family_weights_and_refs(ledger: dict, skill_id: str) -> None:
    rows = {r["skill_id"]: r for r in ledger.get("skill_rows") or []}
    assert skill_id in rows
    row = rows[skill_id]
    assert row.get("role_family_weights"), f"{skill_id} missing role_family_weights"
    assert row.get("pillar") == "pillar_revenue_operations"
    snippets = row.get("source_snippets") or []
    facts = row.get("fact_id_links") or []
    assert snippets or facts, f"{skill_id} must have source_snippets or fact_id_links"
    if skill_id in (
        "skill_revops_salesforce_pipeline_analytics",
        "skill_revops_salesforce_forecast_pipeline",
        "skill_revops_usage_based_subscription_forecasting",
    ):
        assert facts, f"{skill_id} DERIVED row requires fact_id_links"


def test_derived_revops_skills_link_medium_facts_only(ledger: dict) -> None:
    candidate = json.loads(
        (
            REPO
            / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
        ).read_text(encoding="utf-8")
    )
    conf = {
        f["candidate_fact_id"]: f.get("confidence")
        for f in candidate.get("candidate_facts") or []
    }
    derived_ids = (
        "skill_revops_salesforce_pipeline_analytics",
        "skill_revops_salesforce_forecast_pipeline",
        "skill_revops_usage_based_subscription_forecasting",
    )
    rows = {r["skill_id"]: r for r in ledger.get("skill_rows") or []}
    for sid in derived_ids:
        row = rows[sid]
        assert row["support_level"] == "DERIVED_SUPPORTED"
        for fid in row["fact_id_links"]:
            assert conf.get(fid) in ("MEDIUM", "HIGH"), f"{fid} confidence too weak for {sid}"


def test_gap_analysis_report_exists_with_rejections() -> None:
    assert GAP_JSON.is_file()
    gap = json.loads(GAP_JSON.read_text(encoding="utf-8"))
    assert gap.get("standalone_cro_role_family_present") is False
    rejected_ids = {r["candidate_fact_id"] for r in gap.get("facts_rejected") or []}
    assert "fact_customer_success_001" in rejected_ids
    assert "fact_sales_accounts_004" in rejected_ids


def test_ledger_still_validates(ledger: dict) -> None:
    validate_arsenal_ledger_shape(ledger)
