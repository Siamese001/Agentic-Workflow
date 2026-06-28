"""apps-test-model: APP CONTRACT.

Hardening ratchet: unify_bullets graph-compose must not leak legacy six-bullet template.
"""
from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    default_taxonomy_path,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.runtime.section_graph_skills_proof_pool import (
    _graph_substrate_company_hint_plan,
    allocate_section_facts_from_graph_substrate,
)
from apps_rg.runtime.sections.unify_bullets_graph_evidence import (
    FORBIDDEN_C0_PROMPT_SUBSTRINGS,
    LEGACY_SIX_PACK_LEDGER_ORDER,
    TRACK_RANKED_SELECTION_METHOD,
    append_unify_path_framing_to_messages,
    assert_c0_pack_has_no_forbidden_template_leaks,
    format_unify_graph_bullet_evidence_pack,
    is_allowed_unify_selection_method,
    is_legacy_six_pack_ledger_order,
    max_consecutive_word_overlap,
)
from apps_rg.runtime.sections.unify_bullets_lane import normalize_unify_parsed_without_ledger_synthesis
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.validators.bullet_quality_floor_x2 import check_bullet_technical_specificity_floor
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS, run_unify_bullets_x2_gates
from apps_rg.runtime.sections.role_episode_metric_registry import metric_outcome_nodes_from_path
from apps_rg.runtime.sections.unify_graph_role_episode_registry import BUNDLES_PATH as UNIFY_BUNDLES_PATH
from apps_rg.runtime.sections.unify_role_episode_evidence import (
    attach_role_episode_bundles_to_proof_pool_metadata,
)
from apps_rg.runtime.validators.unify_role_episode_x2 import (
    run_unify_bullets_role_episode_x2_gates,
)
from apps_rg.runtime.product_evidence_authority import build_evidence_authority

REPO = Path(__file__).resolve().parents[3]
JD = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt").read_text(encoding="utf-8")
BRIEF = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md").read_text(
    encoding="utf-8"
)


@pytest.fixture(autouse=True)
def _fixture_bypass():
    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


def _brown_allocate() -> dict:
    ledger = load_master_candidate_fact_ledger(repo_root=REPO)
    taxonomy = load_master_role_family_taxonomy(repo_root=REPO)
    plan, _, _ = allocate_section_facts_from_graph_substrate(
        ledger=ledger,
        taxonomy=taxonomy,
        section_id="unify_bullets",
        target_company="Brown & Brown",
        target_role="SVP IT Strategy & Innovation",
        jd_text=JD,
        briefing_text=BRIEF,
        ledger_path=default_ledger_path(repo_root=REPO),
        taxonomy_path=default_taxonomy_path(repo_root=REPO),
    )
    return plan


def _partner_role_episode_meta() -> dict:
    graph_ref = "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
    ledger_ref = "apps_rg/fact_inventory/candidate_fact_ledger.json"
    return attach_role_episode_bundles_to_proof_pool_metadata(
        {
            "proof_pool_type": "augmented_skills_graph",
            "graph_ref": graph_ref,
            "skills_authority_status": "PASS",
            "evidence_authority": build_evidence_authority(
                graph_ref=graph_ref,
                ledger_ref=ledger_ref,
                skills_authority_status="PASS",
            ),
            "selected_graph_evidence_plan": {
                "role_family_key": "PARTNER_APPLIED_AI_ARCHITECTURE",
                "target_role_profile": "PARTNER_APPLIED_AI_ARCHITECTURE",
            }
        },
        section_id="unify_bullets",
        repo_root=REPO,
    )


def _partner_metric_surface_payload() -> tuple[list[dict], dict, dict]:
    meta = _partner_role_episode_meta()
    slot_map = meta["unify_bullet_slot_bundle_map_resolved"]
    bundle_by_id = {b["role_episode_bundle_id"]: b for b in meta["role_episode_bundles"]}
    metric_nodes = metric_outcome_nodes_from_path(UNIFY_BUNDLES_PATH)
    bullets: list[dict] = []
    ledger: list[dict] = []
    change_log: list[dict] = []
    for bid in UNIFY_BULLET_IDS:
        bundle = bundle_by_id[slot_map[bid]]
        mid = str(bundle["linked_metric_outcome_ids"][0])
        token = str((metric_nodes[mid].get("surface_tokens") or [metric_nodes[mid]["metric"]])[0])
        text = (
            f"Owned {token} across governed enterprise AI platform work, tying architecture "
            f"execution to measurable adoption outcomes."
        )
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "has_metric": True,
                "metric_raw": mid,
                "source_fact_ids": [bid],
            }
        )
        ledger.append({"claim_text": text, "source_fact_ids": [bid]})
        change_log.append(
            {
                "bullet_id": bid,
                "role_episode_bundle_id": bundle["role_episode_bundle_id"],
                "graph_skill_node_ids": list(bundle["graph_skill_node_ids"])[:3],
                "fact_ids_used": [bid, *list(bundle["linked_source_fact_ids"])[:1]],
                "metric_outcome_ids": [mid],
            }
        )
    parsed = {
        "bullets": bullets,
        "selected_fact_plan": {"selection_method": TRACK_RANKED_SELECTION_METHOD, "facts": []},
        "claim_ledger": ledger,
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "gap_notes": [],
        "change_log": change_log,
        "self_check": {"bullets_composed_from_graph_evidence": True},
    }
    return bullets, parsed, meta


def test_unify_x1d_outputs_are_written_once_after_adjudication() -> None:
    source = (REPO / "apps_rg/runtime/sections/unify_bullets_lane.py").read_text(encoding="utf-8")
    write_call = 'write_json(artifact_dir / "x1d_llm_judge_outputs.json"'

    assert source.count(write_call) == 1
    assert source.find(write_call) > source.find("if _should_adjudicate and _panel_keys:")
    assert source.find(write_call) < source.find("run_bullet_judge_reselection(")


def test_legacy_six_pack_detector() -> None:
    assert is_legacy_six_pack_ledger_order(list(LEGACY_SIX_PACK_LEDGER_ORDER))
    assert not is_legacy_six_pack_ledger_order(
        [
            "fact_engineering_platform_004",
            "fact_engineering_platform_006",
            "fact_engineering_platform_003",
            "fact_engineering_platform_001",
            "fact_exec_002",
            "fact_engineering_platform_002",
        ]
    )


def test_selection_method_guard_rejects_company_hint() -> None:
    assert is_allowed_unify_selection_method(TRACK_RANKED_SELECTION_METHOD)
    assert not is_allowed_unify_selection_method("augmented_skills_graph_unify_bullets_company_hint")
    assert not is_allowed_unify_selection_method("hydrate_unify_bullets_from_canonical_resume")


def test_company_hint_plan_raises_for_unify_bullets() -> None:
    ledger = load_master_candidate_fact_ledger(repo_root=REPO)
    with pytest.raises(ValueError, match="forbidden for unify_bullets"):
        _graph_substrate_company_hint_plan(ledger, section_id="unify_bullets", hints=("unify",), limit=6)


def test_brown_allocation_not_legacy_six_pack() -> None:
    plan = _brown_allocate()
    assert plan["selection_method"] == TRACK_RANKED_SELECTION_METHOD
    ledger_ids = [
        str(f.get("ledger_candidate_fact_id") or f.get("candidate_fact_id") or "")
        for f in plan.get("facts") or []
    ]
    assert not is_legacy_six_pack_ledger_order(ledger_ids)
    assert ledger_ids == [
        "fact_engineering_platform_002",
        "fact_engineering_platform_001",
        "fact_engineering_platform_003",
        "fact_engineering_platform_004",
        "fact_engineering_platform_005",
        "fact_engineering_platform_006",
    ]


def test_c0_pack_forbidden_substrings_blocked() -> None:
    with pytest.raises(ValueError, match="forbidden template leakage"):
        assert_c0_pack_has_no_forbidden_template_leaks(
            "CANONICAL UNIFY FACTS\nbul_unify_001 | theme: Agentic AI"
        )


def test_c0_pack_format_has_compose_slots_and_skills() -> None:
    plan = _brown_allocate()
    body = format_unify_graph_bullet_evidence_pack(
        {
            "selected_fact_plan": plan,
            "proof_pool_metadata": {
                "selected_skill_rows": [
                    {
                        "skill_id": "skill_agentic_platform_productization",
                        "allowed_phrases": ["agentic platform productization"],
                        "fact_id_links": ["fact_engineering_platform_006"],
                    }
                ]
            },
        },
        allowed_block="ALLOWED_SOURCE_FACT_IDS: [bul_unify_001]\n",
        unify_id_hygiene="",
    )
    for forbidden in FORBIDDEN_C0_PROMPT_SUBSTRINGS:
        assert forbidden not in body
    assert "compose_one_bullet_from" in body
    assert TRACK_RANKED_SELECTION_METHOD in body or "track_ranked" in body


def test_role_episode_gates_pass_deep_metric_outcome_surfaces() -> None:
    bullets, parsed, meta = _partner_metric_surface_payload()
    gates = run_unify_bullets_role_episode_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        proof_pool_metadata=meta,
        jd_text=JD,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_each_bullet_approved_metric_outcome_lineage"].passed is True
    assert by_id["x2_unify_each_bullet_metric_outcome_surface_visible"].passed is True
    assert by_id["x2_unify_metric_outcomes_distributed_by_slot"].passed is True
    assert by_id["x2_unify_graph_traversal_sufficiency"].passed is True
    assert by_id["x2_unify_graph_granularity_gates"].passed is True


def test_role_episode_gates_fail_when_metric_outcome_not_visible() -> None:
    bullets, parsed, meta = _partner_metric_surface_payload()
    bullets[1]["bullet_text"] = (
        "Owned alliance execution across governed enterprise AI platform work, tying architecture "
        "execution to measurable adoption outcomes."
    )
    parsed["claim_ledger"][1]["claim_text"] = bullets[1]["bullet_text"]
    gates = run_unify_bullets_role_episode_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        proof_pool_metadata=meta,
        jd_text=JD,
    )
    gate = next(g for g in gates if g.gate_id == "x2_unify_each_bullet_metric_outcome_surface_visible")
    assert gate.passed is False
    assert "bul_unify_002" in str(gate.observed_value)


def test_unify_normalization_repairs_metric_surface_visibility_from_registry() -> None:
    _bullets, parsed, meta = _partner_metric_surface_payload()
    parsed["bullets"][1]["bullet_text"] = (
        "Built partner co-sell motions around reusable AI platform services, packaging enablement "
        "material for strategic channels."
    )
    parsed["claim_ledger"][1]["claim_text"] = parsed["bullets"][1]["bullet_text"]
    parsed["change_log"][1]["metric_outcome_ids"] = ["metric_unify_partner_enablement_asset_set"]

    parsed["bullets"][2]["bullet_text"] = (
        "Drove CFO-aligned enterprise adoption motions and renewal instrumentation to strengthen "
        "platform commercialization."
    )
    parsed["claim_ledger"][2]["claim_text"] = parsed["bullets"][2]["bullet_text"]
    parsed["change_log"][2]["metric_outcome_ids"] = [
        "metric_unify_consumption_renewal_signal_instrumentation"
    ]

    runtime_payload = {
        "allowed_fact_ids": list(UNIFY_BULLET_IDS),
        "selected_fact_plan": {"facts": []},
        "proof_pool_metadata": meta,
    }
    normalized = normalize_unify_parsed_without_ledger_synthesis(parsed, runtime_payload)
    assert normalized is not None

    gates = run_unify_bullets_role_episode_x2_gates(
        bullets=normalized["bullets"],
        parsed_output=normalized,
        proof_pool_metadata=meta,
        jd_text=JD,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_each_bullet_metric_outcome_surface_visible"].passed is True
    assert by_id["x2_unify_metric_outcomes_distributed_by_slot"].passed is True


def test_agentic_runtime_terms_count_for_bullet_technical_specificity() -> None:
    result = check_bullet_technical_specificity_floor(
        "bul_unify_001",
        "Set the control plane for governed agentic enterprise workflows with L0 route-policy "
        "dispatch, GraphRAG grounding, and replayable runtime traceability.",
    )
    assert result.passed is True


def test_role_episode_gates_fail_shallow_traversal_receipt() -> None:
    bullets, parsed, meta = _partner_metric_surface_payload()
    meta = dict(meta)
    meta["unify_graph_traversal_sufficiency_receipt"] = {
        "candidate_conservation": {"pass": False},
        "selected_role_episode_root_count": 1,
        "selected_unique_leaf_skill_count": 1,
        "selected_unique_metric_count": 1,
        "rejected_sibling_skill_count": 0,
        "rejected_sibling_metric_count": 0,
        "role_specific_axis_coverage": {"missing_axes": ["partner_channel_cosell"]},
        "frontier_size_by_hop_depth": {
            "hop_0_role_episode_roots": 1,
            "hop_1_graph_skill_nodes": 1,
            "hop_2_metric_outcome_nodes": 1,
        },
    }
    gates = run_unify_bullets_role_episode_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        proof_pool_metadata=meta,
        jd_text=JD,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_graph_traversal_sufficiency"].passed is False
    assert by_id["x2_unify_graph_granularity_gates"].passed is False


def test_unify_x2_graph_mode_delegates_legacy_metric_cluster_to_positive_contract() -> None:
    bullets, parsed, meta = _partner_metric_surface_payload()
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text=JD,
        runtime_generation_status="MOCKED",
        proof_pool_metadata=meta,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_protected_bullet_metrics_preserved"].pass_ is True
    assert by_id["x2_unify_protected_bullet_metrics_preserved"].observed_value == (
        "delegated_to_role_episode_metric_outcome_contract"
    )
    assert by_id["x2_unify_each_bullet_metric_outcome_surface_visible"].pass_ is True


def test_unify_metric_source_gate_accepts_approved_metric_outcome_id_lists() -> None:
    bullets, parsed, meta = _partner_metric_surface_payload()
    for bullet, change in zip(bullets, parsed["change_log"]):
        bullet["metric_raw"] = list(change["metric_outcome_ids"])

    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text=JD,
        runtime_generation_status="MOCKED",
        proof_pool_metadata=meta,
    )

    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_metric_source_required"].pass_ is True


def test_unify_metric_source_gate_rejects_bare_canonical_metric_without_outcome_id() -> None:
    bullets, parsed, meta = _partner_metric_surface_payload()
    bullets[0]["metric_raw"] = "$22M"
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text=JD,
        runtime_generation_status="MOCKED",
        proof_pool_metadata=meta,
    )

    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_metric_source_required"].pass_ is False
    assert "bul_unify_001" in str(by_id["x2_unify_metric_source_required"].observed_value)


def test_path_framing_has_no_legacy_theme_angles() -> None:
    msgs = append_unify_path_framing_to_messages(
        [{"role": "user", "content": "base"}],
        path_index=2,
        temperature=0.4,
        runtime_payload={"jd_text": JD, "briefing": BRIEF},
    )
    text = msgs[-1]["content"]
    assert "PATH_FRAMING" in text
    assert "Dependency graph intelligence" not in text
    assert "legacy resume themes" in text.lower()


def test_max_consecutive_word_overlap_detects_archive_copy() -> None:
    archive = (
        "Designed and operationalized governed agentic AI platform capabilities for regulated "
        "enterprise workflows, including deterministic routing."
    )
    bullet = (
        "Designed and operationalized governed agentic AI platform capabilities for regulated "
        "enterprises, enhancing compliance."
    )
    assert max_consecutive_word_overlap(archive, bullet) >= 8


def test_x2_fails_on_company_hint_selection_method() -> None:
    bullets = [
        {"bullet_id": bid, "bullet_text": f"Outcome for {bid}.", "source_fact_ids": [bid]}
        for bid in UNIFY_BULLET_IDS
    ]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    po = {
        "bullets": bullets,
        "selected_fact_plan": {
            "selection_method": "augmented_skills_graph_unify_bullets_company_hint",
            "facts": [{"fact_id": bid, "claim_text": "archive prose " * 5} for bid in UNIFY_BULLET_IDS],
        },
        "claim_ledger": ledger,
        "jd_alignment": {},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=po,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text=JD,
        runtime_generation_status="MOCKED",
    )
    gate = next(g for g in gates if g.gate_id == "x2_unify_track_ranked_selection_method")
    assert gate.pass_ is False


def test_x2_fails_on_legacy_six_pack_allocation() -> None:
    bullets = [
        {"bullet_id": bid, "bullet_text": f"Outcome for {bid}.", "source_fact_ids": [bid]}
        for bid in UNIFY_BULLET_IDS
    ]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    facts = [
        {
            "fact_id": bid,
            "ledger_candidate_fact_id": lid,
            "claim_text": f"Ledger claim for {lid}.",
        }
        for bid, lid in zip(UNIFY_BULLET_IDS, LEGACY_SIX_PACK_LEDGER_ORDER, strict=True)
    ]
    po = {
        "bullets": bullets,
        "selected_fact_plan": {
            "selection_method": TRACK_RANKED_SELECTION_METHOD,
            "facts": facts,
        },
        "claim_ledger": ledger,
        "jd_alignment": {},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=po,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text=JD,
        runtime_generation_status="MOCKED",
    )
    gate = next(g for g in gates if g.gate_id == "x2_unify_not_legacy_six_pack_allocation")
    assert gate.pass_ is False


def test_x2_fails_on_archive_verbatim_bullet() -> None:
    archive = (
        "Designed and operationalized governed agentic AI platform capabilities for regulated "
        "enterprise workflows with deterministic routing and orchestration."
    )
    bullets = [
        {
            "bullet_id": "bul_unify_001",
            "bullet_text": (
                "Designed and operationalized governed agentic AI platform capabilities for regulated "
                "enterprises, enhancing compliance."
            ),
            "source_fact_ids": ["bul_unify_001"],
        },
        *[
            {"bullet_id": bid, "bullet_text": f"Distinct outcome {bid}.", "source_fact_ids": [bid]}
            for bid in UNIFY_BULLET_IDS[1:]
        ],
    ]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    po = {
        "bullets": bullets,
        "selected_fact_plan": {
            "selection_method": TRACK_RANKED_SELECTION_METHOD,
            "facts": [
                {"fact_id": "bul_unify_001", "claim_text": archive},
                *[{"fact_id": bid, "claim_text": "other"} for bid in UNIFY_BULLET_IDS[1:]],
            ],
        },
        "claim_ledger": ledger,
        "jd_alignment": {},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=po,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text=JD,
        runtime_generation_status="MOCKED",
    )
    gate = next(g for g in gates if g.gate_id == "x2_unify_no_archive_claim_verbatim")
    assert gate.pass_ is False


def test_graph_ranked_empty_expansion_not_legacy_six_pack() -> None:
    """Zero graph scores must not yield sorted engineering_platform_001..006 only."""
    from apps_rg.runtime.section_graph_skills_proof_pool import _graph_ranked_unify_bullets_plan

    ledger = load_master_candidate_fact_ledger(repo_root=REPO)

    def _empty_expansion(**_kwargs: object) -> dict:
        return {"selected_facts": [], "selected_skills": []}

    with patch(
        "apps_rg.fact_inventory.track_weighted_graph_expansion.build_track_weighted_expansion",
        side_effect=_empty_expansion,
    ):
        result = _graph_ranked_unify_bullets_plan(
            ledger,
            section_id="unify_bullets",
            target_role="SVP IT Strategy & Innovation",
            jd_text=JD,
            briefing_text=BRIEF,
            limit=6,
            repo_root=REPO,
        )
    assert result is not None
    plan, _, _ = result
    ledger_ids = list(plan.get("ledger_pick_order") or [])
    assert ledger_ids
    assert not is_legacy_six_pack_ledger_order(ledger_ids)


def test_graph_ranked_fail_closed_when_only_legacy_pack() -> None:
    from apps_rg.runtime.section_graph_skills_proof_pool import _graph_ranked_unify_bullets_plan

    ledger = load_master_candidate_fact_ledger(repo_root=REPO)
    with patch(
        "apps_rg.runtime.sections.unify_bullets_graph_evidence.is_legacy_six_pack_ledger_order",
        return_value=True,
    ):
        result = _graph_ranked_unify_bullets_plan(
            ledger,
            section_id="unify_bullets",
            target_role="SVP IT Strategy & Innovation",
            jd_text=JD,
            briefing_text=BRIEF,
            limit=6,
            repo_root=REPO,
        )
    assert result is None
