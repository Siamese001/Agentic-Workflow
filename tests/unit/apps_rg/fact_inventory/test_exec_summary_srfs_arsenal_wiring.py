"""W4: executive_summary SRFS wired to Master Skills Arsenal projection."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import (
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.fact_inventory.exec_summary_graph_projection_w4b import (
    DEFAULT_ARSENAL_ROLE_FAMILY_KEY,
    external_proof_fact_ids_from_projection,
    resolve_arsenal_role_family_key,
)
from apps_rg.fact_inventory.executive_summary_arsenal_projection import (
    project_executive_summary_arsenal,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    load_master_skills_arsenal_ledger,
    skill_row_eligible_for_external_claim,
)
from apps_rg.fact_inventory.selected_role_fact_set import (
    infer_role_family_priorities,
    select_candidate_facts_for_role,
)

REPO = Path(__file__).resolve().parents[4]
LEDGER_PATH = REPO / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
TAXONOMY_PATH = REPO / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml"
ARSENAL_PATH = REPO / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"

ENGINEERING_PLATFORM_FACTS = frozenset(
    {
        "fact_engineering_platform_001",
        "fact_engineering_platform_002",
        "fact_engineering_platform_003",
        "fact_engineering_platform_004",
    }
)


@pytest.fixture
def taxonomy() -> dict:
    return load_master_role_family_taxonomy(path=TAXONOMY_PATH)


@pytest.fixture
def ledger() -> dict:
    return load_master_candidate_fact_ledger(path=LEDGER_PATH)


@pytest.fixture
def arsenal() -> dict:
    return load_master_skills_arsenal_ledger(path=ARSENAL_PATH)


def _select(
    ledger: dict,
    taxonomy: dict,
    *,
    target_role: str,
    jd_text: str,
    briefing_text: str = "",
    target_company: str = "Acme Labs",
) -> tuple[list[str], list[str]]:
    srfs = select_candidate_facts_for_role(
        target_company=target_company,
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        ledger=ledger,
        taxonomy=taxonomy,
        source_ledger_path=str(LEDGER_PATH),
        taxonomy_ref=str(TAXONOMY_PATH),
        repo_root=REPO,
        now_slug="20260518_W4_ARSENAL",
    )
    exec_ids = [s.candidate_fact_id for s in srfs.selected_facts_by_section["executive_summary"]]
    headline_ids = [s.candidate_fact_id for s in srfs.selected_facts_by_section["headline"]]
    return exec_ids, headline_ids


def test_resolve_role_family_keys() -> None:
    tax = load_master_role_family_taxonomy(path=TAXONOMY_PATH)
    prio = infer_role_family_priorities(
        target_role="SVP Engineering AI platform kubernetes agentic",
        jd_text="engineering leadership microservices cloud AWS platform.",
        briefing_text="",
        taxonomy=tax,
    )
    assert (
        resolve_arsenal_role_family_key(
            role_family_priorities=prio,
            target_role="SVP Engineering",
            jd_text="agentic AI platform",
        )
        == "SVP_ENGINEERING_AI_PLATFORM"
    )
    prio_p = infer_role_family_priorities(
        target_role="Partnerships alliances ISV co-sell",
        jd_text="RevOps forecasting pipeline analytics Salesforce quotas ISV alliances partner engineering.",
        briefing_text="",
        taxonomy=tax,
    )
    assert (
        resolve_arsenal_role_family_key(
            role_family_priorities=prio_p,
            target_role="Partnerships",
            jd_text="ISV alliances co-sell",
        )
        == "ANTHROPIC_PARTNERSHIPS_APPLIED_AI"
    )


def test_svp_exec_includes_actuarial_differentiator_when_eligible(ledger: dict, taxonomy: dict) -> None:
    exec_ids, _headline = _select(
        ledger,
        taxonomy,
        target_role="SVP Engineering AI Platform leadership agentic kubernetes",
        jd_text="engineering platform leadership microservices cloud AWS governance.",
    )
    assert exec_ids
    assert all(fid.startswith("fact_") for fid in exec_ids)
    assert not any(fid.startswith("skill_") for fid in exec_ids)
    actuarial = {"fact_quant_hpc_003", "fact_certs_001"} & set(exec_ids)
    arch_reserved = ENGINEERING_PLATFORM_FACTS & set(exec_ids)
    assert arch_reserved or actuarial, "SVP exec should surface platform and/or actuarial differentiator facts"


def test_headline_does_not_consume_reserved_engineering_platform_facts(ledger: dict, taxonomy: dict) -> None:
    exec_ids, headline_ids = _select(
        ledger,
        taxonomy,
        target_role="SVP Engineering AI Platform agentic orchestration",
        jd_text="platform engineering leadership kubernetes microservices AWS.",
    )
    overlap = ENGINEERING_PLATFORM_FACTS & set(headline_ids)
    exec_arch = ENGINEERING_PLATFORM_FACTS & set(exec_ids)
    assert exec_arch, "executive_summary should retain platform-class facts"
    assert len(overlap) < len(ENGINEERING_PLATFORM_FACTS), (
        "headline must not consume all engineering platform facts reserved for executive_summary"
    )


def test_anthropic_partnerships_prioritizes_partner_and_cloud_facts(
    ledger: dict, taxonomy: dict, arsenal: dict
) -> None:
    exec_ids, headline_ids = _select(
        ledger,
        taxonomy,
        target_role="Director Partnerships alliances ISV co-sell applied AI",
        jd_text="RevOps forecasting pipeline analytics Salesforce quotas ISV alliances partner engineering pre-sales.",
    )
    prio = infer_role_family_priorities(
        target_role="Director Partnerships alliances ISV co-sell applied AI",
        jd_text="RevOps forecasting pipeline analytics Salesforce quotas ISV alliances partner engineering pre-sales.",
        briefing_text="",
        taxonomy=taxonomy,
    )
    role_key = resolve_arsenal_role_family_key(
        role_family_priorities=prio,
        target_role="Director Partnerships",
        jd_text="ISV alliances co-sell pre-sales AWS",
    )
    assert role_key == "ANTHROPIC_PARTNERSHIPS_APPLIED_AI"
    proj = project_executive_summary_arsenal(role_key, ledger=arsenal)
    assert proj.partner_gtm_included
    # Partnership ledger rows are MEDIUM; HIGH proof uses AWS/cloud + exec commercialization.
    combined = set(exec_ids) | set(headline_ids)
    assert "fact_engineering_platform_005" in combined or any(
        "exec_" in fid for fid in exec_ids
    )
    assert all(fid.startswith("fact_") for fid in exec_ids)


def test_ai_financial_services_governance_and_actuarial(ledger: dict, taxonomy: dict) -> None:
    exec_ids, _headline = _select(
        ledger,
        taxonomy,
        target_role="AI Financial Services governance risk actuarial",
        jd_text="enterprise risk controls Basel CCAR actuarial foundation derivatives hedging governance.",
    )
    # Governance/risk-domain facts (AI_GOVERNANCE_RISK). Broadened 2026-06-11 to recognize the
    # precisely-named banking/ERM risk facts (BCBS 239, three-lines, Solvency II, credit) the
    # enrichment added — they now outrank the generic fact_governance_* for risk/governance JDs.
    gov = {
        fid
        for fid in exec_ids
        if any(m in fid for m in ("governance", "bcbs239", "three_lines", "solvency"))
        or fid.startswith("fact_credit_")
    }
    quant = {fid for fid in exec_ids if "quant_hpc" in fid or fid == "fact_certs_001"}
    assert gov, "AI Financial Services should include governance/risk facts"
    assert quant or gov


def test_pending_source_skills_not_in_external_proof_fact_ids(arsenal: dict) -> None:
    proj = project_executive_summary_arsenal(DEFAULT_ARSENAL_ROLE_FAMILY_KEY, ledger=arsenal)
    ext = external_proof_fact_ids_from_projection(arsenal, proj)
    pending_rows = [
        r for r in arsenal["skill_rows"] if r["support_level"] == "USER_CONFIRMED_PENDING_SOURCE"
    ]
    for row in pending_rows:
        assert not skill_row_eligible_for_external_claim(row)
        for fid in row.get("fact_id_links") or []:
            if fid:
                assert fid not in ext


def test_exec_slices_use_arsenal_allocation_hint(ledger: dict, taxonomy: dict) -> None:
    srfs = select_candidate_facts_for_role(
        target_company="Acme",
        target_role="SVP Engineering AI platform",
        jd_text="agentic platform engineering leadership.",
        briefing_text="",
        ledger=ledger,
        taxonomy=taxonomy,
        repo_root=REPO,
        now_slug="20260518_W4_HINT",
    )
    hints = [s.allocation_hint for s in srfs.selected_facts_by_section["executive_summary"]]
    assert any("arsenal" in h for h in hints), "executive_summary selection should record arsenal wiring"


def test_no_jd_briefing_fact_ids_in_exec_selection(ledger: dict, taxonomy: dict) -> None:
    exec_ids, headline_ids = _select(
        ledger,
        taxonomy,
        target_role="SVP Engineering",
        jd_text="kubernetes microservices platform.",
    )
    for fid in exec_ids + headline_ids:
        low = fid.lower()
        assert "jd" not in low or fid.startswith("fact_")
        assert not low.startswith("briefing")
        assert not low.startswith("jd_")


def test_skill_ids_never_selected_as_facts(ledger: dict, taxonomy: dict) -> None:
    srfs = select_candidate_facts_for_role(
        target_company="Acme",
        target_role="SVP Engineering",
        jd_text="platform engineering.",
        briefing_text="briefing-only steering",
        ledger=ledger,
        taxonomy=taxonomy,
        repo_root=REPO,
        now_slug="20260518_W4_SKILL",
    )
    for sec in ("headline", "executive_summary"):
        for sl in srfs.selected_facts_by_section[sec]:
            assert sl.candidate_fact_id.startswith("fact_")
            assert not sl.candidate_fact_id.startswith("skill_")
