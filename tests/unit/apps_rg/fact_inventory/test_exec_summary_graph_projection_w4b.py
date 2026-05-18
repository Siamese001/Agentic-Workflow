"""W4B: graph → SRFS → compiled prompt inspection (offline, no live generation)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.arsenal_graph_w4a_spec import AGENTIC_CAPABILITY_DOMAINS
from apps_rg.fact_inventory.exec_summary_graph_projection_w4b import (
    BANNED_PHRASES_PROMPT_CONTRACT,
    PARTNERSHIP_MEDIUM_PREFIX,
    ROLE_FAMILY_INSPECTION_KEYS,
    inspect_all_role_families,
    inspect_role_family_projection,
    write_w4b_audit_reports,
)
REPO = Path(__file__).resolve().parents[4]

DOMAIN_LABELS = {d["domain_id"]: d["label"] for d in AGENTIC_CAPABILITY_DOMAINS}

SVP_REQUIRED_DOMAIN_LABELS = frozenset(
    {
        "Agentic Systems Architecture",
        "Routing, Triage, and Workflow Selection",
        "Context Engineering and Evidence Grounding",
        "Runtime Gates, Evaluation, and Exit Control",
        "Security, Governance, Authority, and Compliance",
        "Productization, Reuse, and Enterprise Adoption",
    }
)

ARCHITECTURE_FACTS = frozenset(
    {
        "fact_engineering_platform_001",
        "fact_engineering_platform_002",
        "fact_engineering_platform_003",
        "fact_engineering_platform_004",
    }
)
def _gov_prefix(fid: str) -> bool:
    return "governance" in fid


@pytest.fixture(scope="module")
def w4b_bundle() -> dict:
    return inspect_all_role_families(repo_root=REPO)


@pytest.fixture(scope="module")
def svp_inspection() -> dict:
    return inspect_role_family_projection("SVP_ENGINEERING_AI_PLATFORM", repo_root=REPO)


def test_all_role_families_inspected(w4b_bundle: dict) -> None:
    assert set(w4b_bundle["role_families_inspected"]) == set(ROLE_FAMILY_INSPECTION_KEYS)
    for key in ROLE_FAMILY_INSPECTION_KEYS:
        row = w4b_bundle["inspections"][key]
        assert row["resolved_arsenal_role_family_key"] == key
        assert row["executive_summary_srfs_fact_ids"]
        assert row["graph_metadata_present"] is True


def test_svp_domains_include_required_capability_labels(svp_inspection: dict) -> None:
    labels = set(svp_inspection["selected_domain_labels"])
    missing = SVP_REQUIRED_DOMAIN_LABELS - labels
    assert not missing, f"SVP missing domains: {missing}"


def test_svp_facts_cover_architecture_governance_commercialization_actuarial(svp_inspection: dict) -> None:
    exec_ids = set(svp_inspection["executive_summary_srfs_fact_ids"])
    assert exec_ids & ARCHITECTURE_FACTS, "SVP exec should include platform/architecture facts"
    assert any(_gov_prefix(fid) for fid in exec_ids), "SVP exec should include governance/risk facts"
    assert "fact_exec_002" in exec_ids or any("exec_" in f for f in exec_ids), (
        "SVP exec should include commercialization/org-scale fact"
    )
    actuarial = {"fact_quant_hpc_003", "fact_certs_001"} & exec_ids
    assert actuarial or svp_inspection["actuarial_differentiator_in_projection"], (
        "SVP should surface actuarial/quant differentiator in facts or projection"
    )


def test_ai_financial_services_priorities(w4b_bundle: dict) -> None:
    row = w4b_bundle["inspections"]["AI_FINANCIAL_SERVICES"]
    labels = set(row["selected_domain_labels"])
    assert "Security, Governance, Authority, and Compliance" in labels
    assert "Context Engineering and Evidence Grounding" in labels
    assert "Replay, Observability, Audit, and Proof" in labels
    exec_ids = row["executive_summary_srfs_fact_ids"]
    assert any(_gov_prefix(fid) for fid in exec_ids)
    assert row["governance_risk_in_projection"]
    hitl_domain = DOMAIN_LABELS["domain_hitl_escalation"]
    assert hitl_domain in labels or row["actuarial_differentiator_in_projection"]


def test_anthropic_partnerships_priorities_without_medium_partner_high_proof(w4b_bundle: dict) -> None:
    row = w4b_bundle["inspections"]["ANTHROPIC_PARTNERSHIPS_APPLIED_AI"]
    labels = set(row["selected_domain_labels"])
    assert "Productization, Reuse, and Enterprise Adoption" in labels
    assert "Context Engineering and Evidence Grounding" in labels
    assert "Security, Governance, Authority, and Compliance" in labels
    assert row["partner_gtm_in_projection"]
    exec_ids = row["executive_summary_srfs_fact_ids"]
    assert not any(fid.startswith(PARTNERSHIP_MEDIUM_PREFIX) for fid in exec_ids)
    assert all(fid.startswith("fact_") for fid in exec_ids)


def test_field_cto_and_cao_have_graph_projection(w4b_bundle: dict) -> None:
    for key in ("FIELD_CTO", "CHIEF_AI_OFFICER"):
        row = w4b_bundle["inspections"][key]
        assert row["selected_domain_labels"]
        assert row["identity_node"]
        assert row["selected_epoch_nodes"]


def test_fact_id_only_proof_paths(svp_inspection: dict) -> None:
    for fid in svp_inspection["executive_summary_srfs_fact_ids"]:
        assert fid.startswith("fact_")
    for fid in svp_inspection["allowed_fact_packet_fact_ids"]:
        assert fid.startswith("fact_")
    assert svp_inspection["skill_id_source_fact_id_exclusion"]["excluded_ok"]


def test_jd_briefing_targeting_only(svp_inspection: dict) -> None:
    jd = svp_inspection["jd_briefing_proof_exclusion"]
    assert jd["jd_targeting_only_in_prompt"]
    assert jd["briefing_targeting_only_in_prompt"]


def test_banned_phrases_listed_in_compiled_prompt_contract(svp_inspection: dict) -> None:
    """W4B banned-phrase contract must be represented in compiled PA guardrails."""
    assert svp_inspection["prompt_forbidden_phrases_section_present"]
    enforced = svp_inspection["banned_phrases_enforced_in_prompt"]
    required_literal = ("applied depth", "documented credential training", "distributed systems training")
    for phrase in required_literal:
        assert enforced.get(phrase) is True, f"missing forbidden phrase contract: {phrase}"
    covered = sum(1 for v in enforced.values() if v)
    assert covered >= 5, f"expected >=5/8 banned-phrase guardrails in PA, got {covered}: {enforced}"
    from apps_rg.runtime.sections.exec_summary_srfs_judge_safe import _BANNED_PROSE_FRAGMENTS

    assert len(_BANNED_PROSE_FRAGMENTS) >= 8


def test_allowed_packet_matches_srfs_slice(svp_inspection: dict) -> None:
    assert set(svp_inspection["allowed_fact_packet_fact_ids"]) == set(
        svp_inspection["executive_summary_srfs_fact_ids"]
    )


def test_write_audit_reports(tmp_path: Path) -> None:
    md = tmp_path / "w4b.md"
    js = tmp_path / "w4b.json"
    write_w4b_audit_reports(repo_root=REPO, md_path=md, json_path=js)
    assert md.is_file()
    assert js.is_file()
    data = json.loads(js.read_text(encoding="utf-8"))
    assert data["schema_version"] == "exec_summary_graph_projection_w4b_v1"
    assert len(data["inspections"]) == 5
