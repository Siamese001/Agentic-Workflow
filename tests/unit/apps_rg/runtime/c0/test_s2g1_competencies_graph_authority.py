"""apps-test-model: LAW. S2G1 competencies graph-authority closure."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

from apps_rg.runtime.c0.competencies_graph_authority import (
    build_competencies_graph_authority_discrepancy_ledger,
    reconcile_competencies_allocation_claim_units,
)
from apps_rg.runtime.c0.resume_graph_allocation import (
    allocate_candidate_sets,
    canonical_allocation_digest,
    slice_section_plan_for_allocation,
)
from apps_rg.runtime.c0.resume_graph_claim_binding import (
    bind_final_claims_to_resume_graph_allocation,
)
from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    normalize_exec_summary_claim_ledger,
)
from apps_rg.runtime.spine.c0_fec_compose import (
    SectionFecBridge,
    _bind_allocation_authority_fields,
)
from apps_rg.runtime.validators.competencies_quality_x2 import _role_axis_coverage


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def _allocation_bundle() -> tuple[dict[str, object], dict[str, object]]:
    slots: list[dict[str, object]] = []
    candidates: dict[str, list[dict[str, object]]] = {}
    for index in range(1, 9):
        slot_id = f"competencies:skill:{index:02d}"
        root_id = "root_partner_cosell_04" if index == 4 else f"root_{index:02d}"
        skill_id = f"skill_domain_{index:02d}"
        fact_id = f"fact_{index:02d}"
        slots.append(
            {"slot_id": slot_id, "section_id": "competencies", "metric_required": False}
        )
        candidates[slot_id] = [
            {
                "candidate_id": f"candidate_{index:02d}",
                "section_id": "competencies",
                "claim_unit_id": slot_id,
                "skill_id": skill_id,
                "fact_id": fact_id,
                "metric_outcome_id": "",
                "root_id": root_id,
                "authority_pass": True,
                "proof_strength_raw": 1.0,
                "target_alignment_score": 1.0,
                "claim_entailment_score": 1.0,
                "path_confidence_raw": 1.0,
                "source_independence_score": 1.0,
                "employer_lane": "unify",
                "source_family": "unify",
                "graph_path_ids": [
                    f"root:{root_id}",
                    f"root:{root_id}/skill:{skill_id}",
                    f"root:{root_id}/fact:{fact_id}",
                ],
                "edge_ids": [f"edge:{root_id}:{skill_id}"],
                "citation_refs": [f"source:{fact_id}"],
            }
        ]
    allocation = allocate_candidate_sets(
        candidate_sets=candidates,
        slot_specs=slots,
        graph_digest="g" * 64,
        policy_digest="p" * 64,
        max_fact_reuse=1,
        max_source_family_share=1.0,
    )
    section_plan: dict[str, object] = {
        "section_id": "competencies",
        "facts": [],
        "selected_skills": [],
        "selected_skill_ids": [],
        "selected_metrics_detail": [],
        "selected_metrics": [],
        "selected_edges": [],
        "graph_candidate_decision_ledger": [],
        "target_role_profile": "ai_partnerships_gtm",
    }
    for index in range(1, 9):
        root_id = "root_partner_cosell_04" if index == 4 else f"root_{index:02d}"
        skills = [f"skill_domain_{index:02d}", f"skill_sibling_{index:02d}"]
        if index == 4:
            skills[1] = "skill_sr_w12_hyperscaler_alliance_co_sell"
        metric_id = f"metric_{index:02d}"
        section_plan["facts"].append(
            {
                "fact_id": root_id,
                "role_episode_bundle_id": root_id,
                "graph_skill_node_ids": skills,
                "metric_outcome_ids": [metric_id],
                "linked_source_fact_ids": [f"fact_{index:02d}"],
            }
        )
        for skill_id in skills:
            section_plan["selected_skills"].append(
                {"skill_id": skill_id, "role_episode_bundle_id": root_id}
            )
            section_plan["selected_skill_ids"].append(skill_id)
        section_plan["selected_metrics_detail"].append(
            {
                "metric_outcome_id": metric_id,
                "role_episode_bundle_id": root_id,
                "metric": f"authorized outcome {index:02d}",
            }
        )
        section_plan["selected_metrics"].append(metric_id)
        section_plan["graph_candidate_decision_ledger"].append(
            {
                "candidate_id": skills[0],
                "candidate_type": "leaf_skill",
                "root_id": root_id,
                "candidate_path_id": f"root:{root_id}/skill:{skills[0]}",
                "path_signature": f"{root_id}->contains->{skills[0]}",
                "decision": "selected",
                "authority_pass": True,
                "reason_codes": ["selected_by_authority"],
                "linked_source_fact_ids": [f"fact_{index:02d}"],
            }
        )
    return allocation, section_plan


def _slice(monkeypatch: object) -> dict[str, object]:
    from apps_rg.runtime.c0 import c03_resume_graph_contracts

    monkeypatch.setattr(c03_resume_graph_contracts, "finalize_canonical_section_plan", dict)
    allocation, section_plan = _allocation_bundle()
    contract = {
        "section_id": "competencies",
        "allocation_plan_digest": allocation["allocation_plan_digest"],
    }
    return slice_section_plan_for_allocation(
        section_plan=section_plan,
        allocation_plan=allocation,
        final_evidence_contract=contract,
        section_id="competencies",
    )


def _parsed_for_plan(plan: dict[str, object]) -> dict[str, object]:
    categories = []
    for assignment in plan["allocation_assignments"]:
        categories.append(
            {
                "category_id": assignment["claim_unit_id"],
                "source_fact_ids": [assignment["fact_id"]],
                "graph_skill_node_ids": [assignment["skill_id"]],
                "terms": [
                    {
                        "text": str(assignment["skill_id"]).replace("skill_", "").replace("_", " "),
                        "source_fact_id": assignment["fact_id"],
                        "source_fact_ids": [assignment["fact_id"]],
                    }
                ],
            }
        )
    return {"competencies": categories, "claim_ledger": []}


def test_stale_nested_seals_do_not_change_canonical_allocation_digest() -> None:
    allocation, _ = _allocation_bundle()
    baseline = canonical_allocation_digest(allocation)
    mutated = copy.deepcopy(allocation)
    mutated["selection_policy"] = {
        "policy": "same",
        "prior_seal": {"allocation_plan_digest": "stale"},
        "downstream_receipt": {"status": "stale"},
    }
    without_receipts = copy.deepcopy(mutated)
    without_receipts["selection_policy"] = {"policy": "same"}
    assert canonical_allocation_digest(mutated) == canonical_allocation_digest(without_receipts)
    assert baseline != canonical_allocation_digest(without_receipts)


def test_exact_rehydration_preserves_sixteen_skills_and_eight_metrics(monkeypatch: object) -> None:
    plan = _slice(monkeypatch)
    assert len(plan["selected_skill_ids"]) == 16
    assert len(plan["selected_metrics"]) == 8
    assert "skill_sr_w12_hyperscaler_alliance_co_sell" in plan["selected_skill_ids"]


def test_ineligible_candidate_is_not_added_to_numeric_floors(monkeypatch: object) -> None:
    allocation, section_plan = _allocation_bundle()
    section_plan["graph_candidate_decision_ledger"].append(
        {
            "candidate_id": "skill_ineligible",
            "candidate_type": "leaf_skill",
            "root_id": "root_01",
            "decision": "rejected",
            "authority_pass": False,
        }
    )
    from apps_rg.runtime.c0 import c03_resume_graph_contracts

    monkeypatch.setattr(c03_resume_graph_contracts, "finalize_canonical_section_plan", dict)
    plan = slice_section_plan_for_allocation(
        section_plan=section_plan,
        allocation_plan=allocation,
        final_evidence_contract={
            "section_id": "competencies",
            "allocation_plan_digest": allocation["allocation_plan_digest"],
        },
        section_id="competencies",
    )
    assert "skill_ineligible" not in plan["selected_skill_ids"]


def test_role_axis_normalizes_cosell_root_identity() -> None:
    coverage = _role_axis_coverage(
        {
            "target_role_profile": "ai_partnerships_gtm",
            "selected_nodes": ["reb_ibm_aws_alliance_partner_cosell_gtm"],
            "selected_skill_ids": [
                "skill_partner_hyperscaler_cosell",
                "skill_partner_cloud_vendor_joint_gtm",
                "skill_partner_gtm_enablement",
                "skill_partner_solution_architecture",
            ],
        }
    )
    assert "co_sell" in coverage["covered_axes"]


def test_reconciliation_consumes_every_allocation_once(monkeypatch: object) -> None:
    plan = _slice(monkeypatch)
    parsed = _parsed_for_plan(plan)
    allowed = set(plan["allowed_graph_evidence_ids"])
    receipt = reconcile_competencies_allocation_claim_units(
        parsed,
        selected_plan=plan,
        allowed_fact_ids=allowed,
    )
    explicit = [row["claim_unit_id"] for row in parsed["claim_ledger"]]
    assert receipt["pass"] is True
    assert len(explicit) == len(set(explicit)) == 8


def test_reconciliation_fails_closed_with_complete_unmatched_ledger(monkeypatch: object) -> None:
    plan = _slice(monkeypatch)
    parsed = {"competencies": [{"terms": [{"text": "unrelated"}]}]}
    receipt = reconcile_competencies_allocation_claim_units(
        parsed,
        selected_plan=plan,
        allowed_fact_ids=set(plan["allowed_graph_evidence_ids"]),
    )
    assert receipt["pass"] is False
    assert len(receipt["unmatched_claim_unit_ids"]) == 8


def test_assertion_skill_fact_and_claim_unit_ids_remain_distinct(monkeypatch: object) -> None:
    plan = _slice(monkeypatch)
    parsed = _parsed_for_plan(plan)
    allowed = set(plan["allowed_graph_evidence_ids"])
    receipt = reconcile_competencies_allocation_claim_units(
        parsed, selected_plan=plan, allowed_fact_ids=allowed
    )
    ledger = build_competencies_graph_authority_discrepancy_ledger(
        selected_plan=plan,
        proof_pool_metadata={
            "graph_skill_embedding_assertion_bindings": [
                {
                    "assertion_id": "assertion_01",
                    "skill_id": "skill_domain_01",
                    "rank": 1,
                }
            ]
        },
        parsed=parsed,
        reconciliation_receipt=receipt,
    )
    row = next(row for row in ledger["rows"] if row["assertion_id"] == "assertion_01")
    assert row["assertion_id"] not in row["skill_ids"]
    assert row["assertion_id"] not in row["fact_ids"]
    assert all(unit not in row["skill_ids"] for unit in row["allocation_claim_unit_ids"])


def test_final_evidence_contract_receives_canonical_digest_at_top_level() -> None:
    digest = "a" * 64
    bridge = SectionFecBridge(section_id="competencies", bridge_doc={})
    pool = SimpleNamespace(
        proof_pool_metadata={
            "resume_graph_allocation_scope": "WHOLE_RESUME",
            "resume_graph_allocation_plan_id": "resume_graph_allocation:test",
            "resume_graph_allocation_plan_digest": digest,
            "resume_graph_global_uniqueness_claimed": True,
        }
    )
    bound = _bind_allocation_authority_fields(bridge, pool=pool)
    assert bound.bridge_doc["resume_graph_allocation_plan_digest"] == digest


def test_canonical_claim_ledger_preserves_allocation_claim_unit_identity() -> None:
    rows = normalize_exec_summary_claim_ledger(
        [
            {
                "claim_text": "governed systems architecture",
                "source_fact_ids": ["fact_01"],
                "claim_unit_id": "competencies:skill:01",
            }
        ]
    )
    payload = build_canonical_claim_ledger_v2_payload(rows, parse_status="OK")
    assert payload["claims"][0]["claim_unit_id"] == "competencies:skill:01"


def test_graph_claim_binding_requires_exactly_once_consumption(
    monkeypatch: object, tmp_path: Path
) -> None:
    plan = _slice(monkeypatch)
    parsed = _parsed_for_plan(plan)
    allowed = set(plan["allowed_graph_evidence_ids"])
    receipt = reconcile_competencies_allocation_claim_units(
        parsed, selected_plan=plan, allowed_fact_ids=allowed
    )
    assert receipt["pass"] is True
    claims = normalize_exec_summary_claim_ledger(parsed["claim_ledger"])
    canonical = build_canonical_claim_ledger_v2_payload(
        claims, parse_status="OK", claim_id_prefix="competencies_claim"
    )
    display = "\n".join(row["claim_text"] for row in claims)
    digest = str(plan["allocation_plan_digest"])
    _write_json(tmp_path / "l2_output.json", {"claim_ledger": claims})
    _write_json(tmp_path / "claim_ledger.json", claims)
    _write_json(tmp_path / "canonical_claim_ledger_v2.json", canonical)
    _write_json(tmp_path / "selected_fact_plan.json", plan)
    _write_json(
        tmp_path / "final_evidence_contract.json",
        {"resume_graph_allocation_plan_digest": digest},
    )
    _write_json(
        tmp_path / "compiled_prompt_artifact.json",
        {"resume_graph_allocation_plan_digest": digest},
    )
    (tmp_path / "command_output.txt").write_text(display, encoding="utf-8")
    binding = bind_final_claims_to_resume_graph_allocation(
        tmp_path, section_id="competencies"
    )
    assert binding["pass"] is True
    assert binding["orphan_allocation_claim_unit_ids"] == []
    assert binding["allocation_claim_unit_consumption_exactly_once_pass"] is True
    assert set(binding["allocation_claim_unit_consumption_counts"].values()) == {1}
