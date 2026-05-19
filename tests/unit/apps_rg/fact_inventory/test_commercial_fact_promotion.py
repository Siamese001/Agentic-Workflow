"""Commercial MEDIUM claim-eligibility seam — registry + SRFS lane pools only."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from apps_rg.fact_inventory.commercial_claim_eligibility import (
    eligibility_config_path,
    is_claim_eligible_medium,
    load_claim_eligibility_registry,
    verify_archive_source_trace,
)
from apps_rg.fact_inventory.selected_role_fact_set import (
    ledger_row_to_slice,
    select_candidate_facts_for_role,
)
from apps_rg.fact_inventory.validate_commercial_srfs_projection import (
    MEDIUM_COMMERCIAL_FACT_IDS,
    REJECTED_FACT_IDS,
    build_validation_payload,
)
from apps_rg.runtime.sections import selected_role_fact_set as runtime_srfs

REPO = Path(__file__).resolve().parents[4]


@pytest.fixture(scope="module")
def taxonomy() -> dict:
    return yaml.safe_load(
        (REPO / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml").read_text(
            encoding="utf-8"
        )
    )


@pytest.fixture(scope="module")
def candidate_ledger() -> dict:
    from apps_rg.fact_inventory.candidate_fact_ledger import load_master_candidate_fact_ledger

    return load_master_candidate_fact_ledger()


def test_eligibility_registry_present() -> None:
    path = eligibility_config_path(REPO)
    assert path.is_file(), "run apply_commercial_fact_promotion.py to materialize registry"
    reg = load_claim_eligibility_registry(str(REPO))
    facts = reg.get("facts") or {}
    assert facts, "registry must list promoted facts"
    for fid in facts:
        assert fid in MEDIUM_COMMERCIAL_FACT_IDS


def test_never_promote_facts_not_in_registry() -> None:
    for fid in REJECTED_FACT_IDS:
        assert not is_claim_eligible_medium(fid, repo_root=REPO)


def test_unpromoted_medium_stays_human_review(candidate_ledger: dict, taxonomy: dict) -> None:
    row = next(
        r
        for r in candidate_ledger["candidate_facts"]
        if r["candidate_fact_id"] == "fact_sales_accounts_004"
    )
    sl = ledger_row_to_slice(row, taxonomy=taxonomy)
    assert sl.verification_status == "blocked_needs_verification"


def test_claim_eligible_slice_has_source_trace(candidate_ledger: dict, taxonomy: dict) -> None:
    fid = "fact_partnerships_gtm_001"
    if not is_claim_eligible_medium(fid, repo_root=REPO):
        pytest.skip("registry not populated")
    row = next(r for r in candidate_ledger["candidate_facts"] if r["candidate_fact_id"] == fid)
    sl = ledger_row_to_slice(row, taxonomy=taxonomy)
    assert sl.verification_status == "eligible_medium_with_source_trace"
    assert sl.source_trace_archive_relpaths


def test_medium_not_in_headline_pool(candidate_ledger: dict, taxonomy: dict) -> None:
    if not is_claim_eligible_medium("fact_sales_accounts_001", repo_root=REPO):
        pytest.skip("registry not populated")
    srfs = select_candidate_facts_for_role(
        target_company="Acme Revenue Corp",
        target_role="Chief Revenue Officer revenue operations Salesforce partnerships",
        jd_text="RevOps Salesforce partnerships IBM AWS",
        briefing_text="",
        ledger=candidate_ledger,
        taxonomy=taxonomy,
        now_slug="test_commercial_promo_headline",
        repo_root=REPO,
    )
    headline_ids = {s.candidate_fact_id for s in srfs.selected_facts_by_section["headline"]}
    exec_ids = {s.candidate_fact_id for s in srfs.selected_facts_by_section["executive_summary"]}
    assert not (headline_ids & MEDIUM_COMMERCIAL_FACT_IDS)
    assert not (exec_ids & MEDIUM_COMMERCIAL_FACT_IDS)


def test_runtime_accepts_claim_eligible_medium_plan_fact() -> None:
    row = {
        "candidate_fact_id": "fact_partnerships_gtm_001",
        "claim_text": "Built a global AI channel program",
        "confidence": "MEDIUM",
        "verification_status": "eligible_medium_with_source_trace",
        "claim_eligible_medium": True,
        "source_trace_archive_relpaths": [
            "artifacts/apps_rg/fact_inventory/phase_i_resumes_archive_extracted/Amit_Ayer_Resume_-_Partner_Development_Manager.txt"
        ],
        "metric_values": [],
        "role_families_supported": [],
        "company_lane": "unify",
    }
    plan = runtime_srfs.slice_row_to_plan_fact(row, section_id="unify_bullets")
    assert plan["confidence"] == "MEDIUM"
    assert plan["source_trace_archive_relpaths"]


def test_archive_trace_verifier_passes_for_promoted_fact(candidate_ledger: dict) -> None:
    row = next(
        r
        for r in candidate_ledger["candidate_facts"]
        if r["candidate_fact_id"] == "fact_sales_accounts_002"
    )
    audit = verify_archive_source_trace(row)
    assert audit["passed"]


def test_validation_payload_passes_with_registry() -> None:
    payload = build_validation_payload()
    assert payload["status"] == "PASS", payload.get("violations")
    assert payload.get("authoritative_commercial_fact_ids"), "expected commercial facts in SRFS"
    assert not set(payload["medium_confirmation_queue_fact_ids"]) & set(
        payload.get("claim_eligible_medium_registry_ids") or []
    )


def test_closeout_report_on_disk() -> None:
    path = REPO / "docs/reports/apps_rg/commercial_fact_promotion_closeout.json"
    if not path.is_file():
        pytest.skip("closeout not generated yet")
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["status"] in ("PASS", "PARTIAL")
    assert doc["claim_eligible_medium"]
