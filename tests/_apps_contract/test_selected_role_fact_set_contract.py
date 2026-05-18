"""Contract: bounded SelectedRoleFactSet selection seam (apps_rg; no résumé generation)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from apps_rg.fact_inventory.candidate_fact_ledger import (
    assert_selection_bounded_to_ledger,
    ledger_fact_ids,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.fact_inventory.selected_role_fact_set import (
    SelectedRoleFactSet,
    infer_role_family_priorities,
    select_candidate_facts_for_role,
    selected_role_fact_set_to_json_dict,
    write_selected_role_fact_set_artifacts,
)

REPO = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
TAXONOMY_PATH = REPO / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml"


@pytest.fixture
def taxonomy() -> dict:
    return load_master_role_family_taxonomy(path=TAXONOMY_PATH)


@pytest.fixture
def ledger() -> dict:
    return load_master_candidate_fact_ledger(path=LEDGER_PATH)


def _minimal_srfs_kwargs(ledger: dict, taxonomy: dict, **overrides) -> dict:
    jd = overrides.pop(
        "jd_text",
        "Lead alliances and partnerships with ISV ecosystem; drive RevOps forecasting and Salesforce pipeline analytics for enterprise quotas.",
    )
    briefing = overrides.pop("briefing_text", "Executive steering for C-suite alignment on platform modernization.")
    return {
        "target_company": overrides.pop("target_company", "Acme Labs"),
        "target_role": overrides.pop(
            "target_role",
            "SVP Strategic Alliances · engineering leadership kubernetes microservices alliances",
        ),
        "jd_text": jd,
        "briefing_text": briefing,
        "ledger": ledger,
        "taxonomy": taxonomy,
        "source_ledger_path": str(LEDGER_PATH),
        "taxonomy_ref": str(TAXONOMY_PATH),
        "repo_root": REPO,
        "now_slug": overrides.pop("now_slug", "20260518_TESTFIXTUREZ"),
        **overrides,
    }


def test_infer_role_family_priorities_deterministic(taxonomy: dict) -> None:
    prio = infer_role_family_priorities(
        target_role="engineering leadership kubernetes microservices alliances",
        jd_text="RevOps forecasting pipeline analytics Salesforce quotas channel co-sell ISV alliances.",
        briefing_text="CFO budgeting synergy M&A synergy planning.",
        taxonomy=taxonomy,
    )
    p1 = prio
    p2 = infer_role_family_priorities(
        target_role="engineering leadership kubernetes microservices alliances",
        jd_text="RevOps forecasting pipeline analytics Salesforce quotas channel co-sell ISV alliances.",
        briefing_text="CFO budgeting synergy M&A synergy planning.",
        taxonomy=taxonomy,
    )
    assert p1 == p2
    rf_ids = tuple(x.role_family for x in prio)
    assert len(rf_ids) == len(set(rf_ids))
    assert "ENGINEERING_PLATFORM" in rf_ids
    assert "PARTNERSHIPS_GTM" in rf_ids
    assert "REVENUE_OPERATIONS" in rf_ids

    prio2 = infer_role_family_priorities(
        target_role="Chief Financial Officer synergy modeling budgeting",
        jd_text="M&A synergy forecasting model.",
        briefing_text="",
        taxonomy=taxonomy,
    )
    labels2 = tuple(p.role_family for p in prio2)
    assert "STRATEGIC_FINANCE" in labels2


def test_select_sets_assertions_schema_and_bounded_ids(ledger: dict, taxonomy: dict) -> None:
    srfs = select_candidate_facts_for_role(**_minimal_srfs_kwargs(ledger, taxonomy))
    assert isinstance(srfs, SelectedRoleFactSet)
    assert srfs.no_jd_fact_minting_assertion is True
    assert srfs.candidate_not_canonical_assertion is True
    d = selected_role_fact_set_to_json_dict(srfs)
    for req in (
        "selection_id",
        "blocked_facts",
        "facts_requiring_human_confirmation",
        "unsupported_jd_needs",
        "selected_facts_by_section",
        "role_family_priorities",
        "competencies_capability_tags_ordered",
        "confidence_policy",
    ):
        assert req in d
    merged = []
    for _sec, lst in srfs.selected_facts_by_section.items():
        if _sec == "competencies":
            assert lst == [], "competencies fact rows intentionally empty until future wiring"
            continue
        merged.extend(lst)
        for sl in lst:
            assert sl.confidence == "HIGH"
    assert_selection_bounded_to_ledger([sl.candidate_fact_id for sl in merged], ledger)
    qs = srfs.facts_requiring_human_confirmation
    assert qs, "fixture ledger must include MEDIUM rows"
    for q in qs:
        assert q.fact.confidence == "MEDIUM"
    banned = {bf.candidate_fact_id for bf in srfs.blocked_facts}
    assert "fact_sales_accounts_004" in banned
    assert "fact_sales_accounts_005" in banned
    assert "fact_customer_success_001" in banned


def test_sections_lane_separation_ibm_vs_unify(ledger: dict, taxonomy: dict) -> None:
    srfs = select_candidate_facts_for_role(**_minimal_srfs_kwargs(ledger, taxonomy))
    for sl in srfs.selected_facts_by_section["unify_bullets"] + srfs.selected_facts_by_section["unify_narrative"]:
        assert sl.company_lane == "unify", sl.candidate_fact_id
    for sl in srfs.selected_facts_by_section["ibm_bullets"] + srfs.selected_facts_by_section["ibm_narrative"]:
        assert sl.company_lane == "ibm_only", sl.candidate_fact_id


def test_competency_tags_derive_only_from_selected_high_facts(ledger: dict, taxonomy: dict) -> None:
    bogus = (
        "We require unicorn_blockchain_proof_engineering_deeply proprietary zzzzzz_not_in_ledger_capabilities zzzzzz."
    )
    srfs = select_candidate_facts_for_role(
        **_minimal_srfs_kwargs(ledger, taxonomy, jd_text=bogus, briefing_text=""),
    )
    tags = srfs.competencies_capability_tags_ordered
    union = []
    for _sec in ("headline", "executive_summary", "unify_bullets", "unify_narrative", "ibm_bullets", "ibm_narrative"):
        for sl in srfs.selected_facts_by_section[_sec]:
            union.extend(sl.capability_tags)
    uniq = sorted(set(union))
    assert tags == tuple(uniq), "tags must derive from curated HIGH allocations only."
    assert "unicorn_blockchain_proof_engineering" not in "".join(tags)
    assert ("blockchain" not in tags)


def test_unsupported_jd_needs_logged(taxonomy: dict) -> None:
    jd = (
        "We need zero knowledge cryptography innovation for unicorn trading desks. "
        "Also alliances ISV forecasting pipeline Salesforce analytics quotas."
    )
    prio = infer_role_family_priorities(
        target_role="alliances forecasting",
        jd_text=jd,
        briefing_text="",
        taxonomy=taxonomy,
    )
    from apps_rg.fact_inventory.selected_role_fact_set import build_unsupported_jd_needs

    un = build_unsupported_jd_needs(
        jd_text=jd,
        taxonomy=taxonomy,
        role_family_priorities=prio,
        high_rows=[],
    )
    kinds = {u.kind for u in un}
    assert "jd_sentence_no_matching_taxonomy_keywords" in kinds


def test_write_selected_role_fact_set_roundtrip_schema(tmp_path: Path, ledger: dict, taxonomy: dict) -> None:
    srfs = select_candidate_facts_for_role(
        **_minimal_srfs_kwargs(ledger, taxonomy, now_slug="20260518T999999Z_ROUNDTRIP"),
    )
    j_path, md_path = write_selected_role_fact_set_artifacts(srfs, repo_root=tmp_path)
    blob = json.loads(j_path.read_text(encoding="utf-8"))
    assert blob["candidate_not_canonical_assertion"] is True
    assert blob["selection_policy"] == "role_family_keyword_v1_bounded_ledger"
    md = md_path.read_text(encoding="utf-8")
    assert "HIGH-confidence external-validation candidates" in md


def test_external_selection_bounded_to_existing_ledger_fact_ids(
    ledger: dict,
    taxonomy: dict,
) -> None:
    universe = ledger_fact_ids(ledger)
    srfs = select_candidate_facts_for_role(**_minimal_srfs_kwargs(ledger, taxonomy))
    for sl in _all_selected_slices(srfs):
        assert sl.candidate_fact_id in universe


def _all_selected_slices(srfs: SelectedRoleFactSet):
    lst = []
    for k, vals in srfs.selected_facts_by_section.items():
        if k == "competencies":
            continue
        lst.extend(vals)
    return lst
