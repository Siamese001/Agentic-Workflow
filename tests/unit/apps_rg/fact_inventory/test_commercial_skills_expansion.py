"""Commercial skills graph expansion — evidence-backed rows; no standalone CRO taxonomy."""
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
CLOSEOUT_JSON = REPO / "docs/reports/apps_rg/skills_graph_commercial_expansion_closeout.json"

NEW_COMMERCIAL_SKILL_IDS = (
    "skill_sales_modernization_deals_15m",
    "skill_sales_global_financial_institutions_leadership",
    "skill_partner_ibm_aws_alliance_joint_revenue",
    "skill_partner_cloud_vendor_joint_gtm",
    "skill_finance_cost_optimization_dashboards",
    "skill_finance_ma_synergy_due_diligence",
    "skill_customer_nrr_predictive_analytics_20pct",
    "skill_customer_satisfaction_nps_25pct",
    "skill_commercial_board_level_stakeholder_alignment",
    "skill_commercial_gtm_investment_pipeline",
)

DERIVED_COMMERCIAL_IDS = (
    "skill_sales_modernization_deals_15m",
    "skill_sales_global_financial_institutions_leadership",
    "skill_partner_ibm_aws_alliance_joint_revenue",
    "skill_partner_cloud_vendor_joint_gtm",
    "skill_finance_cost_optimization_dashboards",
    "skill_finance_ma_synergy_due_diligence",
)


@pytest.fixture
def ledger() -> dict:
    return load_master_skills_arsenal_ledger(path=LEDGER_PATH)


def test_taxonomy_has_no_standalone_cro_role_family() -> None:
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    ids = [rf["id"] for rf in data.get("role_families") or []]
    assert "CRO" not in ids
    assert "CHIEF_REVENUE_OFFICER" not in ids
    assert not any(re.search(r"\bCRO\b", str(rf.get("id", ""))) for rf in data.get("role_families") or [])


def test_closeout_report_exists(ledger: dict) -> None:
    assert CLOSEOUT_JSON.is_file()
    closeout = json.loads(CLOSEOUT_JSON.read_text(encoding="utf-8"))
    assert closeout.get("standalone_cro_role_family_added") is False
    after = closeout["before_after_counts"]["after"]
    assert after["skill_row_count"] == len(ledger.get("skill_rows") or [])


@pytest.mark.parametrize("skill_id", NEW_COMMERCIAL_SKILL_IDS)
def test_new_commercial_skill_rows_present_with_refs(ledger: dict, skill_id: str) -> None:
    rows = {r["skill_id"]: r for r in ledger.get("skill_rows") or []}
    assert skill_id in rows
    row = rows[skill_id]
    assert row.get("pillar"), f"{skill_id} missing pillar"
    assert row.get("role_family_weights"), f"{skill_id} missing role_family_weights"
    snippets = row.get("source_snippets") or []
    facts = row.get("fact_id_links") or []
    assert snippets or facts, f"{skill_id} must have source_snippets or fact_id_links"


@pytest.mark.parametrize("skill_id", DERIVED_COMMERCIAL_IDS)
def test_derived_commercial_skills_link_medium_or_high_facts_only(ledger: dict, skill_id: str) -> None:
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
    row = next(r for r in ledger["skill_rows"] if r["skill_id"] == skill_id)
    assert row["support_level"] == "DERIVED_SUPPORTED"
    for fid in row["fact_id_links"]:
        assert conf.get(fid) in ("MEDIUM", "HIGH"), f"{fid} too weak for {skill_id}"


def test_low_customer_success_fact_not_on_new_cs_skills(ledger: dict) -> None:
    rows = {r["skill_id"]: r for r in ledger.get("skill_rows") or []}
    for sid in (
        "skill_customer_nrr_predictive_analytics_20pct",
        "skill_customer_satisfaction_nps_25pct",
    ):
        assert "fact_customer_success_001" not in (rows[sid].get("fact_id_links") or [])


def test_partner_revenue_3m_wired_to_partnerships_fact(ledger: dict) -> None:
    rows = {r["skill_id"]: r for r in ledger.get("skill_rows") or []}
    row = rows["skill_partner_partner_revenue_3m"]
    assert "fact_partnerships_gtm_001" in (row.get("fact_id_links") or [])


def test_ledger_still_validates(ledger: dict) -> None:
    validate_arsenal_ledger_shape(ledger)
