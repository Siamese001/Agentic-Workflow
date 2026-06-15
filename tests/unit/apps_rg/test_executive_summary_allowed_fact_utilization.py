"""Unit tests: x2_exec_summary_allowed_fact_utilization gate."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_composition import (
    _infer_graph_skill_refs,
    _skill_ids_for_facts_from_track_expansion,
    build_executive_summary_composition_plan,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    brushstroke_required_groups_from_composition_plan,
    check_exec_summary_allowed_fact_utilization,
    default_allowed_fact_utilization_waivers,
    resolve_utilization_waived_fact_ids,
)


def test_cert_facts_waived_by_default() -> None:
    allowed = {"fact_certs_001", "fact_governance_003", "fact_exec_002"}
    waived = resolve_utilization_waived_fact_ids(allowed)
    assert waived == {"fact_certs_001"}
    assert default_allowed_fact_utilization_waivers(allowed) == frozenset({"fact_certs_001"})


def test_allowed_fact_utilization_passes_when_only_cert_unused() -> None:
    allowed = {"fact_certs_001", "fact_governance_003"}
    ledger = [
        {"claim_text": "governance", "source_fact_ids": ["fact_governance_003"]},
    ]
    ok, reason, receipt = check_exec_summary_allowed_fact_utilization(ledger, allowed)
    assert ok is True
    assert reason == "ok"
    assert receipt["waived_fact_ids"] == ["fact_certs_001"]
    assert receipt["unused_required_fact_ids"] == []


def test_allowed_fact_utilization_fails_missing_non_waived() -> None:
    allowed = {"fact_governance_003", "fact_quant_hpc_001"}
    ledger = [{"claim_text": "gov", "source_fact_ids": ["fact_governance_003"]}]
    ok, reason, receipt = check_exec_summary_allowed_fact_utilization(ledger, allowed)
    assert ok is False
    assert reason is not None and "fact_quant_hpc_001" in reason
    assert receipt["unused_required_fact_ids"] == ["fact_quant_hpc_001"]


def test_skill_refs_scoped_to_role_facts_via_track_expansion() -> None:
    facts = [
        {"fact_id": "fact_governance_003", "claim_text": "Basel III CCAR lineage"},
    ]
    meta = {
        "track_weighted_graph_expansion": {
            "selected_skills": [
                {"skill_id": "skill_sr_basel_ccar_lineage_regulatory", "fact_id": "fact_governance_003"},
                {"skill_id": "skill_p2_gtm_executive_buyer_alignment", "fact_id": "fact_partnerships_gtm_002"},
            ],
        },
        "c03_selected_skill_ids": [
            "skill_sr_basel_ccar_lineage_regulatory",
            "skill_p2_gtm_executive_buyer_alignment",
        ],
    }
    refs = _skill_ids_for_facts_from_track_expansion(facts, meta)
    assert refs == ["skill_sr_basel_ccar_lineage_regulatory"]
    brush_refs = _infer_graph_skill_refs(facts, proof_pool_metadata=meta)
    assert brush_refs == ["skill_sr_basel_ccar_lineage_regulatory"]


def test_composition_plan_brushstroke_skills_not_global_pool_dump() -> None:
    facts = [
        {"fact_id": "fact_governance_003", "claim_text": "Basel III CCAR"},
        {"fact_id": "fact_engineering_platform_001", "claim_text": "governed platform"},
    ]
    meta = {
        "track_weighted_graph_expansion": {
            "selected_skills": [
                {"skill_id": "skill_sr_basel_ccar_lineage_regulatory", "fact_id": "fact_governance_003"},
                {"skill_id": "skill_governed_agentic_systems_architecture", "fact_id": "fact_engineering_platform_001"},
                {"skill_id": "skill_p2_gtm_executive_buyer_alignment", "fact_id": "fact_partnerships_gtm_002"},
            ],
        },
        "c03_selected_skill_ids": [
            "skill_sr_basel_ccar_lineage_regulatory",
            "skill_governed_agentic_systems_architecture",
            "skill_p2_gtm_executive_buyer_alignment",
        ],
    }
    plan = build_executive_summary_composition_plan(
        selected_facts=facts,
        allowed_fact_ids={"fact_governance_003", "fact_engineering_platform_001"},
        target_role="SVP IT Strategy",
        target_company="Acme",
        proof_pool_metadata=meta,
    )
    b3 = next(b for b in plan["brushstrokes"] if b["brushstroke_role"] == "B3_control_evidence_discipline")
    assert "skill_sr_basel_ccar" in str(b3.get("allowed_graph_skill_ids"))
    assert "skill_p2_gtm" not in str(b3.get("allowed_graph_skill_ids"))


# --- Brushstroke COVERAGE mode (graph-era utilization scoping; W2.3->W3 bridge) ---

_PLAN = {
    "brushstrokes": [
        {"brushstroke_role": "B1", "required_fact_ids": ["reb_a", "reb_b"]},
        {"brushstroke_role": "B2", "required_fact_ids": ["reb_c", "reb_d", "reb_e"]},
        {"brushstroke_role": "B3", "required_fact_ids": ["reb_f"]},
        {"brushstroke_role": "B4_business_role_fit", "required_fact_ids": []},
    ]
}


def test_brushstroke_groups_extractor_drops_empty() -> None:
    groups = brushstroke_required_groups_from_composition_plan(_PLAN)
    # B4 (empty) is dropped; B1/B2/B3 kept
    assert sorted(len(g) for g in groups) == [1, 2, 3]


def test_coverage_passes_when_each_brushstroke_represented() -> None:
    groups = brushstroke_required_groups_from_composition_plan(_PLAN)
    # one fact cited per brushstroke (not all facts) — a summary-satisfiable bar
    ledger = [
        {"claim_text": "s1", "source_fact_ids": ["reb_a"]},
        {"claim_text": "s2", "source_fact_ids": ["reb_c"]},
        {"claim_text": "s3", "source_fact_ids": ["reb_f"]},
    ]
    ok, reason, receipt = check_exec_summary_allowed_fact_utilization(
        ledger, set(), required_brushstroke_groups=groups
    )
    assert ok is True
    assert receipt["policy"] == "brushstroke_coverage"
    assert receipt["uncovered_brushstroke_groups"] == []


def test_coverage_fails_when_a_brushstroke_is_uncovered() -> None:
    groups = brushstroke_required_groups_from_composition_plan(_PLAN)
    # B2 (reb_c/d/e) entirely uncited -> must FAIL (meaningful bar preserved)
    ledger = [
        {"claim_text": "s1", "source_fact_ids": ["reb_a"]},
        {"claim_text": "s3", "source_fact_ids": ["reb_f"]},
    ]
    ok, reason, receipt = check_exec_summary_allowed_fact_utilization(
        ledger, set(), required_brushstroke_groups=groups
    )
    assert ok is False
    assert reason is not None and "uncovered_required_brushstrokes" in reason
    assert ["reb_c", "reb_d", "reb_e"] in receipt["uncovered_brushstroke_groups"]
