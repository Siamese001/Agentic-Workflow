"""W4A hardened skills graph — structure, domains, policies, projection."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.executive_summary_arsenal_projection import (
    project_executive_summary_arsenal,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    W4A_TOP_LEVEL,
    load_master_skills_arsenal_ledger,
    skill_row_eligible_for_external_claim,
    validate_arsenal_ledger_shape,
    validate_w4a_graph_shape,
)

REPO = Path(__file__).resolve().parents[4]
LEDGER_PATH = REPO / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"

EXPECTED_DOMAINS = {
    "domain_agentic_systems_architecture",
    "domain_reasoning_planning_decomposition",
    "domain_routing_triage_workflow",
    "domain_orchestration_managed_workflows",
    "domain_context_engineering_grounding",
    "domain_prompt_assembly_boundaries",
    "domain_execution_tool_sandbox",
    "domain_healing_retry_resilience",
    "domain_runtime_gates_exit",
    "domain_security_governance_compliance",
    "domain_replay_observability_audit",
    "domain_learning_calibration",
    "domain_hitl_escalation",
    "domain_productization_enterprise_adoption",
}

RESUME_HARDENING_FIELDS = (
    "ats_keywords",
    "achievement_framing_guidance",
    "quantification_policy",
    "narrative_synthesis_guidance",
    "claim_verification_policy",
    "zero_hallucination_guardrail",
)


@pytest.fixture
def ledger() -> dict:
    return load_master_skills_arsenal_ledger(path=LEDGER_PATH)


def test_w4a_graph_top_level_and_layers(ledger: dict) -> None:
    validate_arsenal_ledger_shape(ledger)
    validate_w4a_graph_shape(ledger)
    for key in W4A_TOP_LEVEL:
        assert key in ledger
    assert ledger["metadata"]["w4a_hardened"] is True
    assert len(ledger["graph_layers"]) == 13
    assert any(layer.get("layer_id") == "career_track" for layer in ledger["graph_layers"])
    assert ledger["graph_metadata"]["primary_taxonomy"] == "capability_domain"
    assert ledger["graph_metadata"]["source_coded_taxonomy_forbidden_as_primary"] is True


def test_fourteen_capability_domains(ledger: dict) -> None:
    domains = {d["domain_id"] for d in ledger["agentic_capability_domains"]}
    assert domains == EXPECTED_DOMAINS
    # Floor lowered 65 -> 58 after the operator-authorized 2026-06-11 curation that removed
    # 16 inward/meta internal-agentic-runtime skills from the matrix (78 -> 62), keeping the
    # externally-meaningful agentic-platform skills. The 14 capability domains are unchanged.
    assert len(ledger["agentic_runtime_matrix"]) >= 58


def test_deep_agentic_rows_have_domain_metadata(ledger: dict) -> None:
    agentic_ids = {r["skill_id"] for r in ledger["agentic_runtime_matrix"]}
    for row in ledger["agentic_runtime_matrix"]:
        assert row.get("domain_id") in EXPECTED_DOMAINS
        assert row.get("source_concepts")
        assert row.get("repo_evidence_files")
        assert row.get("source_snippets")
        assert row.get("career_epoch") == "epoch_agentic_ai_runtime_architecture"
        for field in RESUME_HARDENING_FIELDS:
            assert field in row, f"{row['skill_id']} missing {field}"
    assert "skill_governed_agentic_systems_architecture" in agentic_ids
    assert "skill_context_engineering" in agentic_ids


def test_no_source_doc_top_level_taxonomy(ledger: dict) -> None:
    forbidden = ("spine_architecture", "l5_governance", "00c_runtime", "production_mechanisms")
    top_keys = set(ledger.keys())
    for bad in forbidden:
        assert bad not in top_keys


def test_graph_edges_counts(ledger: dict) -> None:
    edges = ledger["graph_edges"]
    types = {e["edge_type"] for e in edges}
    assert "capability_domain_contains_skill" in types
    assert "skill_supported_by_source_concept" in types
    assert "skill_supported_by_fact" in types
    assert "projection_excludes_blocked_skill" in types
    assert "jd_briefing_targeting_only" in types
    assert "srfs_requires_fact_id_only" in types
    domain_skill = sum(1 for e in edges if e["edge_type"] == "capability_domain_contains_skill")
    concept = sum(1 for e in edges if e["edge_type"] == "skill_supported_by_source_concept")
    assert domain_skill >= 65
    assert concept >= 50


def test_identity_and_epochs(ledger: dict) -> None:
    node_ids = {n["node_id"] for n in ledger["graph_nodes"]}
    assert "identity_amit_ayer_governed_ai_platform_leader" in node_ids
    for ep in (
        "epoch_actuarial_financial_engineering",
        "epoch_partner_gtm_revenue_leadership",
        "epoch_agentic_ai_runtime_architecture",
    ):
        assert ep in node_ids


def test_actuarial_graph_chain(ledger: dict) -> None:
    pending = [
        r
        for r in ledger["skill_rows"]
        if r["support_level"] == "USER_CONFIRMED_PENDING_SOURCE"
        and r.get("career_epoch") == "epoch_actuarial_financial_engineering"
    ]
    for row in pending:
        assert not skill_row_eligible_for_external_claim(row)
    archive = [
        r
        for r in ledger["skill_rows"]
        if r["skill_id"] == "skill_actuarial_fsa_fellowship"
    ]
    assert archive
    assert archive[0].get("career_epoch") == "epoch_actuarial_financial_engineering"


def test_partner_pending_and_repo_portfolio(ledger: dict) -> None:
    pe = [r for r in ledger["skill_rows"] if r["skill_id"] == "skill_partner_partner_engineering"]
    assert pe and not skill_row_eligible_for_external_claim(pe[0])
    # REPO_EVIDENCE_PORTFOLIO support level retired by the operator-authorized 2026-06-11 removal
    # of the 16 internal-agentic-runtime skills (they WERE exactly the repo-evidence-portfolio
    # rows). The invariant — repo-evidence rows must never be externally claimable — still holds
    # for any that exist; it is vacuous when the category is empty.
    repo_rows = [
        r for r in ledger["agentic_runtime_matrix"] if r["support_level"] == "REPO_EVIDENCE_PORTFOLIO"
    ]
    for repo_row in repo_rows:
        assert not skill_row_eligible_for_external_claim(repo_row)


def test_external_claim_policies_present(ledger: dict) -> None:
    pol = ledger["external_claim_policies"]
    for pid in (
        "skill_projection_not_proof",
        "jd_briefing_targeting_only",
        "pending_source_internal_only",
        "repo_evidence_portfolio_not_resume_default",
        "skill_id_never_source_fact_id",
        "ats_keywords_not_claims",
    ):
        assert pid in pol


def test_graph_aware_projection_fields(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("SVP_ENGINEERING_AI_PLATFORM", ledger=ledger)
    assert proj.identity_node
    assert proj.selected_domain_nodes
    assert proj.claim_verification_summary
    assert proj.external_claim_policy_summary
    assert any("domain_" in d for d in proj.selected_domain_nodes)
    assert proj.actuarial_differentiator_included


def test_chief_ai_officer_governance_domains(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("CHIEF_AI_OFFICER", ledger=ledger)
    doms = set(proj.selected_domain_nodes)
    assert "domain_security_governance_compliance" in doms or "domain_runtime_gates_exit" in doms
    assert "domain_learning_calibration" in doms or "domain_productization_enterprise_adoption" in doms


def test_anthropic_productization_handoff(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("ANTHROPIC_PARTNERSHIPS_APPLIED_AI", ledger=ledger)
    doms = set(proj.selected_domain_nodes)
    assert "domain_productization_enterprise_adoption" in doms
    assert "domain_hitl_escalation" in doms or "domain_context_engineering_grounding" in doms


def test_ai_financial_services_risk_audit(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("AI_FINANCIAL_SERVICES", ledger=ledger)
    assert proj.governance_risk_included
    doms = set(proj.selected_domain_nodes)
    assert (
        "domain_security_governance_compliance" in doms
        or "domain_replay_observability_audit" in doms
    )


def test_field_cto_architecture_context(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("FIELD_CTO", ledger=ledger)
    doms = set(proj.selected_domain_nodes)
    assert "domain_agentic_systems_architecture" in doms
    assert "domain_context_engineering_grounding" in doms
