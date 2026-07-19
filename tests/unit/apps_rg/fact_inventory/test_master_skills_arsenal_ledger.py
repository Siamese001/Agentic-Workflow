"""Arsenal ledger load, validation, and executive_summary projection (no live generation)."""
from __future__ import annotations

# apps-test-model: APP CONTRACT
import copy
from pathlib import Path

import pytest

from apps_rg.fact_inventory.executive_summary_arsenal_projection import (
    project_executive_summary_arsenal,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    REGISTERED_GRAPH_EDGE_SIGNATURES,
    REGISTERED_GRAPH_EDGE_TYPES,
    REQUIRED_SKILL_ROW_FIELDS,
    REQUIRED_TOP_LEVEL,
    arsenal_skill_ids,
    classify_derived_graph_endpoint,
    collect_canonical_graph_issues,
    derive_registered_graph_endpoint_types,
    graph_node_requires_source_refs,
    load_master_skills_arsenal_ledger,
    skill_row_eligible_for_external_claim,
    validate_arsenal_ledger_shape,
    validate_skill_row_for_external_output,
)

REPO = Path(__file__).resolve().parents[4]
LEDGER_PATH = REPO / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"


@pytest.fixture
def ledger() -> dict:
    return load_master_skills_arsenal_ledger(path=LEDGER_PATH)


def test_arsenal_ledger_loads_and_top_level_keys(ledger: dict) -> None:
    validate_arsenal_ledger_shape(ledger)
    for key in REQUIRED_TOP_LEVEL:
        assert key in ledger
    assert ledger["metadata"]["schema_version"] == "master_skills_arsenal_graph_v1"
    assert ledger["metadata"].get("w4a_hardened") is True
    assert len(ledger["pillars"]) == 29
    assert len(ledger["skill_rows"]) >= 162
    assert len(ledger["actuarial_career_matrix"]) == 22
    assert len(ledger["partner_gtm_matrix"]) == 16
    # 9 -> 18: dynamic functional-scoring model added a pillar-weight profile for every
    # classifier-emittable projection key (2026-06-11).
    assert len(ledger["role_family_projection_profiles"]) == 18
    # 65 -> 58: operator-authorized removal of 16 internal-agentic skills (matrix 78 -> 62).
    assert len(ledger["agentic_runtime_matrix"]) >= 58
    assert len(arsenal_skill_ids(ledger)) == len(ledger["skill_rows"])


def test_skill_row_required_fields_present(ledger: dict) -> None:
    for row in ledger["skill_rows"]:
        for field in REQUIRED_SKILL_ROW_FIELDS:
            assert field in row, f"{row.get('skill_id')} missing {field}"


def _has_issue(issues: list[str], code: str) -> bool:
    return any(issue.startswith(f"{code}:") for issue in issues)


def test_canonical_graph_issue_collector_exposes_current_provenance_gaps(ledger: dict) -> None:
    issues = collect_canonical_graph_issues(ledger)
    assert _has_issue(issues, "GRAPH_NODE_REQUIRED_SOURCE_REFS_MISSING")
    assert not _has_issue(issues, "GRAPH_EDGE_ENDPOINT_UNREGISTERED")
    assert not _has_issue(issues, "GRAPH_EDGE_SIGNATURE_INVALID")
    assert ledger["graph_metadata"]["node_count"] == len(ledger["graph_nodes"]) == 371
    assert ledger["graph_metadata"]["edge_count"] == len(ledger["graph_edges"]) == 1908


def test_canonical_graph_issue_collector_rejects_duplicate_ids_and_logical_triples(
    ledger: dict,
) -> None:
    broken = copy.deepcopy(ledger)
    broken["graph_nodes"].append(copy.deepcopy(broken["graph_nodes"][0]))
    duplicate_edge = copy.deepcopy(broken["graph_edges"][0])
    broken["graph_edges"].append(duplicate_edge)
    issues = collect_canonical_graph_issues(broken)
    assert _has_issue(issues, "GRAPH_NODE_ID_DUPLICATE")
    assert _has_issue(issues, "GRAPH_EDGE_ID_DUPLICATE")
    assert _has_issue(issues, "GRAPH_EDGE_TRIPLE_DUPLICATE")


@pytest.mark.parametrize(
    ("mutation", "issue_code"),
    [
        (lambda payload: payload["graph_nodes"][0].__setitem__("node_id", " "), "GRAPH_NODE_ID_BLANK"),
        (lambda payload: payload["graph_edges"][0].__setitem__("edge_id", ""), "GRAPH_EDGE_ID_BLANK"),
        (
            lambda payload: payload["graph_nodes"][0].__setitem__("node_type", "unknown_node_type"),
            "GRAPH_NODE_TYPE_UNREGISTERED",
        ),
        (
            lambda payload: payload["graph_edges"][0].__setitem__("edge_type", "unknown_edge_type"),
            "GRAPH_EDGE_TYPE_UNREGISTERED",
        ),
        (
            lambda payload: payload["graph_edges"][0].__setitem__("target_node_id", "mystery_endpoint"),
            "GRAPH_EDGE_ENDPOINT_UNREGISTERED",
        ),
        (
            lambda payload: payload["graph_nodes"][0].__setitem__("support_level", "UNREGISTERED"),
            "GRAPH_NODE_SUPPORT_LEVEL_UNREGISTERED",
        ),
        (
            lambda payload: payload["graph_nodes"][0].__setitem__("visibility_rule", "UNREGISTERED"),
            "GRAPH_NODE_VISIBILITY_RULE_UNREGISTERED",
        ),
        (
            lambda payload: payload["graph_nodes"][0].__setitem__("activation_status", "UNREGISTERED"),
            "GRAPH_NODE_ACTIVATION_STATUS_UNREGISTERED",
        ),
        (
            lambda payload: payload["graph_nodes"][0].__setitem__("evidence_risk", "UNREGISTERED"),
            "GRAPH_NODE_EVIDENCE_RISK_UNREGISTERED",
        ),
        (
            lambda payload: payload["graph_nodes"][0].__setitem__(
                "external_claim_policy", "UNREGISTERED"
            ),
            "GRAPH_NODE_EXTERNAL_CLAIM_POLICY_UNREGISTERED",
        ),
        (
            lambda payload: payload["graph_nodes"][0].__setitem__("description", ""),
            "GRAPH_NODE_EVIDENCE_FIELD_MISSING",
        ),
        (
            lambda payload: payload["graph_edges"][0].__setitem__("rationale", "  "),
            "GRAPH_EDGE_EVIDENCE_FIELD_MISSING",
        ),
        (
            lambda payload: payload["graph_edges"][0].__setitem__(
                "external_claim_policy", "UNREGISTERED"
            ),
            "GRAPH_EDGE_EXTERNAL_CLAIM_POLICY_UNREGISTERED",
        ),
        (
            lambda payload: payload["graph_edges"][0].__setitem__(
                "validation_status", "UNREGISTERED"
            ),
            "GRAPH_EDGE_VALIDATION_STATUS_UNREGISTERED",
        ),
        (
            lambda payload: payload["graph_nodes"][0].__setitem__("source_refs", "not-a-list"),
            "GRAPH_NODE_SOURCE_REFS_INVALID",
        ),
        (
            lambda payload: payload["graph_metadata"].__setitem__("edge_count", 1),
            "GRAPH_METADATA_EDGE_COUNT_MISMATCH",
        ),
        (
            lambda payload: payload["graph_metadata"].__setitem__("node_count", 1),
            "GRAPH_METADATA_NODE_COUNT_MISMATCH",
        ),
    ],
)
def test_canonical_graph_issue_collector_rejects_adversarial_mutations(
    ledger: dict,
    mutation,
    issue_code: str,
) -> None:
    broken = copy.deepcopy(ledger)
    mutation(broken)
    assert _has_issue(collect_canonical_graph_issues(broken), issue_code)


def test_canonical_graph_issue_collector_rejects_invalid_direction_signature(
    ledger: dict,
) -> None:
    broken = copy.deepcopy(ledger)
    edge = next(
        item
        for item in broken["graph_edges"]
        if item["edge_type"] == "career_track_contains_epoch"
    )
    identity = next(
        node["node_id"]
        for node in broken["graph_nodes"]
        if node["node_type"] == "identity_north_star"
    )
    edge["source_node_id"] = identity
    issues = collect_canonical_graph_issues(broken)
    assert _has_issue(issues, "GRAPH_EDGE_SIGNATURE_INVALID")


def test_every_registered_edge_type_has_an_explicit_signature_rule() -> None:
    assert set(REGISTERED_GRAPH_EDGE_SIGNATURES) == set(REGISTERED_GRAPH_EDGE_TYPES)


def test_prefix_only_endpoint_is_not_a_registered_canonical_derivation(ledger: dict) -> None:
    broken = copy.deepcopy(ledger)
    edge = next(
        row
        for row in broken["graph_edges"]
        if row["edge_type"] == "skill_supported_by_source_concept"
    )
    edge["target_node_id"] = "concept_forged_prefix_only"
    edge["edge_id"] = f"edge_forged_{edge['source_node_id']}"
    issues = collect_canonical_graph_issues(broken)
    assert _has_issue(issues, "GRAPH_EDGE_ENDPOINT_UNREGISTERED")


def test_derived_graph_endpoint_registry_is_closed(
    ledger: dict,
) -> None:
    registry = derive_registered_graph_endpoint_types(ledger)
    expected = {
        "concept_GovernedAgenticRuntime": "source_concept",
        "repo_8c2730": "repository_evidence",
        "fact_engineering_platform_001": "atomic_proof_fact",
        "domain_agentic_systems_architecture": "capability_domain",
        "section_executive_summary": "resume_section_projection",
        "section:experience": "resume_section_projection",
        "bul_insurtech_001": "bullet_fact",
        "policy_pending_source_internal_only": "policy_rule",
        "cert_databricks_lakehouse_001": "certification_evidence",
        "exp_insurtech_001": "experience_evidence",
        "atomic_fact_default_external_proof": "external_claim_policy",
        "cross_career": "career_epoch",
        "jd_text": "targeting_input",
    }
    for endpoint_id, endpoint_type in expected.items():
        assert classify_derived_graph_endpoint(endpoint_id, registry) == endpoint_type
    assert classify_derived_graph_endpoint("concept_prefix_only_forgery", registry) is None
    assert classify_derived_graph_endpoint("repo_ffffff", registry) is None
    assert classify_derived_graph_endpoint("unregistered_endpoint", registry) is None


def test_required_source_refs_are_policy_aware(ledger: dict) -> None:
    externally_claimable = next(
        node
        for node in ledger["graph_nodes"]
        if node.get("source_refs")
        and node.get("external_claim_policy") == "derived_supported_with_fact"
    )
    internal = next(
        node
        for node in ledger["graph_nodes"]
        if node.get("external_claim_policy") == "internal_traversal_only"
    )
    assert graph_node_requires_source_refs(externally_claimable)
    assert not graph_node_requires_source_refs(internal)

    broken = copy.deepcopy(ledger)
    current_missing = sum(
        graph_node_requires_source_refs(node) and not node.get("source_refs")
        for node in broken["graph_nodes"]
    )
    target = next(node for node in broken["graph_nodes"] if node["node_id"] == externally_claimable["node_id"])
    target["source_refs"] = []
    assert current_missing == 84
    assert sum(
        graph_node_requires_source_refs(node) and not node.get("source_refs")
        for node in broken["graph_nodes"]
    ) == current_missing + 1


def test_pending_source_blocked_from_external_claim(ledger: dict) -> None:
    pending = [
        r
        for r in ledger["skill_rows"]
        if r["support_level"] == "USER_CONFIRMED_PENDING_SOURCE"
    ]
    assert pending, "fixture must include pending-source rows"
    for row in pending:
        assert not skill_row_eligible_for_external_claim(row)
        violations = validate_skill_row_for_external_output(row)
        assert violations


def test_direct_archive_skill_can_be_external_eligible(ledger: dict) -> None:
    direct = [
        r
        for r in ledger["skill_rows"]
        if r["support_level"] == "DIRECT_FROM_RESUME_ARCHIVE" and r.get("source_snippets")
    ]
    assert direct
    eligible = [r for r in direct if skill_row_eligible_for_external_claim(r)]
    assert eligible, "at least one archive-supported row should be externally eligible"


def test_targeting_only_and_style_only_not_proof() -> None:
    targeting = {
        "skill_id": "skill_test_targeting",
        "fact_id_links": [],
        "pillar": "pillar_agentic_ai_platforms",
        "subpillar": "t",
        "career_stage": "cross_career",
        "source_resume_files": [],
        "source_snippets": ["jd emphasis only"],
        "user_confirmed": False,
        "support_level": "TARGETING_ONLY",
        "role_family_weights": {},
        "allowed_phrases": ["emphasis"],
        "forbidden_phrases": [],
        "allowed_sections": ["executive_summary"],
        "visibility_rule": "never_external",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
    }
    assert not skill_row_eligible_for_external_claim(targeting)
    style = {**targeting, "skill_id": "skill_test_style", "support_level": "STYLE_ONLY"}
    assert not skill_row_eligible_for_external_claim(style)


def test_blocked_not_selectable() -> None:
    blocked = {
        "skill_id": "skill_test_blocked",
        "fact_id_links": ["fact_engineering_platform_001"],
        "pillar": "pillar_agentic_ai_platforms",
        "subpillar": "t",
        "career_stage": "cross_career",
        "source_resume_files": [],
        "source_snippets": ["x"],
        "user_confirmed": False,
        "support_level": "BLOCKED",
        "role_family_weights": {},
        "allowed_phrases": [],
        "forbidden_phrases": [],
        "allowed_sections": [],
        "visibility_rule": "never_external",
        "evidence_risk": "high",
        "activation_status": "RETIRED",
        "human_confirmation_required": True,
    }
    assert not skill_row_eligible_for_external_claim(blocked)


def test_no_fact_links_internal_only_for_external_claim() -> None:
    row = {
        "skill_id": "skill_test_no_facts",
        "fact_id_links": [],
        "pillar": "pillar_actuarial_foundation",
        "subpillar": "t",
        "career_stage": "cross_career",
        "source_resume_files": [],
        "source_snippets": [],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {"ENGINEERING_PLATFORM": 1.0},
        "allowed_phrases": ["x"],
        "forbidden_phrases": [],
        "allowed_sections": ["executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
    }
    assert not skill_row_eligible_for_external_claim(row)


def test_derived_requires_fact_links() -> None:
    row = {
        "skill_id": "skill_test_derived",
        "fact_id_links": [],
        "pillar": "pillar_actuarial_foundation",
        "subpillar": "t",
        "career_stage": "cross_career",
        "source_resume_files": [],
        "source_snippets": ["Derived phrase supported by quant_hpc fact anchor in ledger."],
        "user_confirmed": False,
        "support_level": "DERIVED_SUPPORTED",
        "role_family_weights": {},
        "allowed_phrases": ["derived"],
        "forbidden_phrases": [],
        "allowed_sections": ["executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
    }
    assert not skill_row_eligible_for_external_claim(row)
    row["fact_id_links"] = ["fact_quant_hpc_003"]
    assert skill_row_eligible_for_external_claim(row)


def test_jd_briefing_not_in_fact_id_links() -> None:
    row = {
        "skill_id": "skill_test_jd",
        "fact_id_links": ["jd_targeting_snippet"],
        "pillar": "pillar_agentic_ai_platforms",
        "subpillar": "t",
        "career_stage": "cross_career",
        "source_resume_files": [],
        "source_snippets": ["ok"],
        "user_confirmed": False,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {},
        "allowed_phrases": ["ok"],
        "forbidden_phrases": [],
        "allowed_sections": ["executive_summary"],
        "visibility_rule": "role_family_match",
        "evidence_risk": "low",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
    }
    assert not skill_row_eligible_for_external_claim(row)


def test_svp_projection_actuarial_differentiator(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("SVP_ENGINEERING_AI_PLATFORM", ledger=ledger)
    assert "pillar_actuarial_foundation" in proj.selected_pillar_ids
    assert "pillar_agentic_ai_platforms" in proj.selected_pillar_ids
    assert proj.actuarial_differentiator_included
    assert proj.internal_ranked_skill_ids


def test_anthropic_partnerships_projection_partner_gtm(ledger: dict) -> None:
    proj = project_executive_summary_arsenal(
        "ANTHROPIC_PARTNERSHIPS_APPLIED_AI", ledger=ledger
    )
    assert "pillar_partner_gtm_alliances" in proj.selected_pillar_ids
    assert "pillar_cosell_partner_engineering" in proj.selected_pillar_ids
    assert "pillar_presales_solutioning" in proj.selected_pillar_ids
    assert "pillar_cloud_data_aws" in proj.selected_pillar_ids
    assert proj.partner_gtm_included


def test_ai_financial_services_governance_actuarial_derivatives(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("AI_FINANCIAL_SERVICES", ledger=ledger)
    assert proj.governance_risk_included
    pillars = set(proj.selected_pillar_ids)
    assert "pillar_regulatory_governance" in pillars
    assert "pillar_actuarial_foundation" in pillars
    greek_or_deriv = pillars & {
        "pillar_greeks_hedging",
        "pillar_derivatives_structured",
    }
    assert greek_or_deriv or any(
        sid.startswith("skill_greeks_") or sid.startswith("skill_derivatives_")
        for sid in proj.internal_ranked_skill_ids
    )


def test_pending_source_not_in_svp_external_eligible(ledger: dict) -> None:
    proj = project_executive_summary_arsenal("SVP_ENGINEERING_AI_PLATFORM", ledger=ledger)
    pending_ids = {
        r["skill_id"]
        for r in ledger["skill_rows"]
        if r["support_level"] == "USER_CONFIRMED_PENDING_SOURCE"
    }
    assert not pending_ids & set(proj.external_eligible_skill_ids)


def test_agentic_core_diff_empty() -> None:
    import os
    import subprocess

    result = subprocess.run(
        ["git", "diff", "HEAD", "--", "agentic_core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    if result.stdout.strip() and os.environ.get("CI") != "true":
        pytest.skip("agentic_core has local diff vs HEAD; assert on clean CI tree")
    assert result.stdout.strip() == ""
