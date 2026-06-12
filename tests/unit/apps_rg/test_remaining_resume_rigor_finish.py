"""Tests for the remaining resume-rigor architecture finish wave.

Covers headline positioning bundles, Unify graph gap fill + role episode bundles,
Unify bullets / narrative role-episode consumption X2 gates, and config enablement.
Non-runtime: validates registry/evidence/gate logic only (no live LLM).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]


def _gate_map(results):
    return {r.gate_id: r for r in results}


# ---------------------------------------------------------------------------
# PART A — Headline positioning bundles
# ---------------------------------------------------------------------------


def test_headline_positioning_bundles_validate_and_cover_families():
    from apps_rg.runtime.sections.headline_positioning_registry import (
        REQUIRED_POSITIONING_FAMILIES,
        get_all_bundles,
        validate_bundle,
    )

    bundles = get_all_bundles()
    families = {b["positioning_family"] for b in bundles}
    assert set(REQUIRED_POSITIONING_FAMILIES) <= families
    for b in bundles:
        ok, violations = validate_bundle(b)
        assert ok, f"{b.get('headline_positioning_bundle_id')}: {violations}"
        assert b["allowed_sections"] == ["headline"]
        assert b["graph_skill_node_ids"]
        assert b["source_competency_bundle_ids"]


def _headline_proof_meta():
    from apps_rg.runtime.sections.headline_positioning_evidence import (
        attach_headline_positioning_bundles_to_proof_pool_metadata,
    )

    return attach_headline_positioning_bundles_to_proof_pool_metadata(
        {"proof_pool_type": "augmented_skills_graph", "graph_skills_proof_pool": True},
        section_id="headline",
    )


def _good_headline_output():
    return {
        "headline_line": "SVP Engineering | Agentic AI Platforms | Regulated Enterprise AI | Runtime Governance",
        "change_log": [
            {
                "segment": "X",
                "headline_positioning_bundle_id": "hpb_agentic_ai_platforms",
                "graph_skill_node_ids": ["skill_governed_agentic_systems_architecture"],
                "source_fact_ids": ["fact_engineering_platform_001"],
            },
            {
                "segment": "Z",
                "headline_positioning_bundle_id": "hpb_runtime_governance",
                "graph_skill_node_ids": ["skill_runtime_gate_mesh_design"],
                "graph_lineage_refs": ["ccb_runtime_governance"],
            },
        ],
    }


def test_headline_positioning_gates_pass_on_good_output():
    from apps_rg.runtime.validators.headline_positioning_x2 import (
        run_headline_positioning_x2_gates,
    )

    out = _good_headline_output()
    gates = _gate_map(
        run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata=_headline_proof_meta(),
            jd_text="enterprise platform leadership",
        )
    )
    for gid in (
        "x2_headline_positioning_bundles_in_proof_pool",
        "x2_headline_positioning_bundle_id_required",
        "x2_headline_graph_skill_node_ids_required",
        "x2_headline_source_fact_or_graph_lineage_required",
        "x2_headline_svp_engineering_seniority_required",
        "x2_headline_platform_or_runtime_signal_required",
        "x2_headline_governance_or_regulated_ai_signal_required",
        "x2_headline_generic_it_strategy_demote_forbidden",
        "x2_headline_jd_only_phrase_forbidden",
        "x2_headline_seniority_floor_met",
        "x2_headline_technical_specificity_floor_met",
        "x2_headline_e0_ngram_overlap_forbidden",
    ):
        assert gid in gates, f"missing gate {gid}"
        assert gates[gid].passed, f"{gid} should pass: {gates[gid].failure_reason}"


def test_headline_requires_bundle_id_binding():
    from apps_rg.runtime.validators.headline_positioning_x2 import (
        run_headline_positioning_x2_gates,
    )

    out = _good_headline_output()
    out["change_log"] = [{"segment": "X", "graph_skill_node_ids": ["skill_x"]}]  # no bundle id
    gates = _gate_map(
        run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata=_headline_proof_meta(),
        )
    )
    assert not gates["x2_headline_positioning_bundle_id_required"].passed


def test_headline_binding_derived_from_cited_facts():
    """derive_from_cited_facts (Author-Gate dec_19e9c91073ae4b5ab): a positioning bundle is bound
    when the model cites one of its linked_source_fact_ids — no explicit bundle id echo required."""
    from apps_rg.runtime.sections.headline_positioning_registry import get_all_bundles
    from apps_rg.runtime.validators.headline_positioning_x2 import (
        run_headline_positioning_x2_gates,
    )

    bundle = next(b for b in get_all_bundles() if b.get("linked_source_fact_ids"))
    linked_fact = bundle["linked_source_fact_ids"][0]

    out = {
        "headline_line": "SVP Engineering | Agentic AI Platforms | Regulated Enterprise AI | Runtime Governance",
        "claim_ledger": [{"claim_text": "Agentic AI Platforms", "source_fact_ids": [linked_fact]}],
        "change_log": [],
    }
    gates = _gate_map(
        run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata=_headline_proof_meta(),
        )
    )
    assert gates["x2_headline_positioning_bundle_id_required"].passed
    assert gates["x2_headline_graph_skill_node_ids_required"].passed
    assert gates["x2_headline_source_fact_or_graph_lineage_required"].passed


def test_headline_binding_fails_when_cited_fact_not_bundle_linked():
    from apps_rg.runtime.validators.headline_positioning_x2 import (
        run_headline_positioning_x2_gates,
    )

    out = {
        "headline_line": "SVP Engineering | Agentic AI Platforms | Regulated Enterprise AI | Runtime Governance",
        "claim_ledger": [{"claim_text": "X", "source_fact_ids": ["fact_not_in_any_bundle_zzz"]}],
        "change_log": [],
    }
    gates = _gate_map(
        run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata=_headline_proof_meta(),
        )
    )
    assert not gates["x2_headline_positioning_bundle_id_required"].passed


def test_headline_rejects_generic_it_strategy_demotion_and_seniority_loss():
    from apps_rg.runtime.validators.headline_positioning_x2 import (
        run_headline_positioning_x2_gates,
    )

    out = _good_headline_output()
    out["headline_line"] = "SVP IT Strategy | Data Modernization | AI Governance"
    gates = _gate_map(
        run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata=_headline_proof_meta(),
        )
    )
    assert not gates["x2_headline_generic_it_strategy_demote_forbidden"].passed
    assert not gates["x2_headline_svp_engineering_seniority_required"].passed


def test_headline_rejects_e0_leakage():
    from apps_rg.runtime.validators.headline_positioning_x2 import (
        run_headline_positioning_x2_gates,
    )

    out = _good_headline_output()
    out["headline_line"] = (
        "SVP Engineering | Lakehouse Microservices Architecture | AI Lifecycle Standardization | Retrieval Telemetry Catalogs"
    )
    gates = _gate_map(
        run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata=_headline_proof_meta(),
        )
    )
    assert not gates["x2_headline_e0_ngram_overlap_forbidden"].passed


def test_headline_rejects_jd_only_phrase_stuffing():
    from apps_rg.runtime.validators.headline_positioning_x2 import (
        run_headline_positioning_x2_gates,
    )

    out = _good_headline_output()
    out["headline_line"] = "SVP Engineering | Agentic AI Platform Governance Controls | Regulated Enterprise AI | Runtime Governance"
    jd = "seeking agentic ai platform governance controls for the enterprise"
    gates = _gate_map(
        run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata=_headline_proof_meta(),
            jd_text=jd,
        )
    )
    assert not gates["x2_headline_jd_only_phrase_forbidden"].passed


# ---------------------------------------------------------------------------
# PART B/C — Unify graph gap fill + role episode bundles
# ---------------------------------------------------------------------------


def test_unify_graph_gap_fill_classifies_all_signals():
    data = json.loads(
        (REPO_ROOT / "apps_rg" / "fact_inventory" / "unify_graph_gap_fill.json").read_text("utf-8")
    )
    valid = set(data["classification_legend"].keys())
    signals = data["signals"]
    assert len(signals) >= 20
    for s in signals:
        assert s["classification"] in valid, s
    # Internal-only and draft signals must not claim external authority.
    for s in signals:
        if s["classification"] in ("ACTIVE_INTERNAL_ONLY", "DRAFT", "SUPPORTING_CONTEXT_ONLY"):
            assert s["external_claim_policy"] != "approved_metric_linked"


def test_unify_role_episode_bundles_validate_with_bindings():
    from apps_rg.runtime.sections.unify_graph_role_episode_registry import (
        UNIFY_EMPLOYER_NODE_ID,
        UNIFY_TIME_WINDOW,
        get_all_bundles,
        validate_bundle,
    )

    bundles = get_all_bundles()
    ids = {b["role_episode_bundle_id"] for b in bundles}
    required = {
        "reb_unify_agentic_platform_architecture",
        "reb_unify_dependency_graph_accelerator",
        "reb_unify_runtime_reliability_governance",
        "reb_unify_production_adoption_lifecycle",
        "reb_unify_distributed_ecosystem_engineering",
        "reb_unify_platform_commercialization_leadership",
    }
    assert required <= ids
    for b in bundles:
        ok, violations = validate_bundle(b)
        assert ok, f"{b['role_episode_bundle_id']}: {violations}"
        assert b["employer_node_id"] == UNIFY_EMPLOYER_NODE_ID
        assert "time_window" not in b
        assert UNIFY_TIME_WINDOW == "2023-02 to present"
        assert b["graph_skill_node_ids"]


def test_unify_metric_outcome_nodes_are_graph_ssot():
    data = json.loads(
        (REPO_ROOT / "apps_rg" / "fact_inventory" / "unify_role_episode_bundles.json").read_text("utf-8")
    )
    nodes = data.get("metric_outcome_nodes") or {}
    approved = data.get("approved_metric_outcome_ids") or {}
    policy = data.get("metric_surface_policy") or {}

    assert nodes
    assert set(nodes) == set(approved)
    assert policy.get("approval_model") == "presence_in_metric_outcome_nodes_is_approval"
    assert policy.get("approved_metric_outcome_ids_role") == "derived_review_index_not_claim_authority"
    assert policy.get("bundle_metric_surface") == (
        "linked_metric_outcome_ids only; metric_outcome_nodes is claim authority"
    )
    for mid, node in nodes.items():
        assert node["metric_outcome_id"] == mid
        assert node["approved"] is True
        assert node["approval_status"] == "APPROVED_GRAPH_SSOT"
        assert node["support_level"] == "approved_by_graph_presence"
        assert node["bundle_bindings"]
        assert "time_window" not in node

    linked_seen: set[str] = set()
    for b in data["bundles"]:
        linked = list(b.get("linked_metric_outcome_ids") or [])
        if not linked:
            continue
        assert "promotable_metrics" not in b
        for mid in linked:
            assert mid in nodes
            assert b["role_episode_bundle_id"] in nodes[mid]["bundle_bindings"]
            linked_seen.add(mid)
    assert linked_seen == set(nodes)


def test_unify_agentic_root_has_svp_engineering_agentic_grain():
    data = json.loads(
        (REPO_ROOT / "apps_rg" / "fact_inventory" / "unify_role_episode_bundles.json").read_text("utf-8")
    )
    ledger = json.loads(
        (REPO_ROOT / "apps_rg" / "fact_inventory" / "master_skills_arsenal_ledger.json").read_text("utf-8")
    )
    bundle = next(
        b
        for b in data["bundles"]
        if b["role_episode_bundle_id"] == "reb_unify_agentic_platform_architecture"
    )

    expected_skill_ids = {
        "skill_unify_agentic_l0_route_policy_dispatch",
        "skill_unify_agentic_multi_agent_orchestration_contracts",
        "skill_unify_agentic_graphrag_context_pack_grounding",
        "skill_unify_agentic_tool_sandbox_egress_controls",
        "skill_unify_agentic_runtime_gate_verdict_contracts",
        "skill_unify_agentic_human_override_escalation_paths",
        "skill_unify_agentic_replay_key_audit_manifest_design",
        "skill_unify_agentic_runtime_proof_bundle_lineage",
    }
    expected_metric_ids = {
        "metric_unify_agentic_l0_route_policy_dispatch_surface",
        "metric_unify_agentic_multi_agent_orchestration_contract_surface",
        "metric_unify_agentic_graphrag_context_pack_grounding_surface",
        "metric_unify_agentic_tool_sandbox_egress_policy_surface",
        "metric_unify_agentic_runtime_gate_verdict_contract_surface",
        "metric_unify_agentic_human_override_escalation_surface",
        "metric_unify_agentic_replay_key_audit_manifest_surface",
        "metric_unify_agentic_runtime_proof_bundle_lineage_surface",
    }

    assert expected_skill_ids <= set(bundle["graph_skill_node_ids"])
    assert expected_metric_ids <= set(bundle["linked_metric_outcome_ids"])
    assert len(bundle["graph_skill_node_ids"]) >= 14
    assert len(bundle["linked_metric_outcome_ids"]) >= 10

    real_skill_ids = {
        str(r.get("skill_id"))
        for r in ledger.get("skill_rows", [])
        if isinstance(r, dict) and r.get("skill_id")
    }
    real_node_ids = {
        str(n.get("node_id"))
        for n in ledger.get("graph_nodes", [])
        if isinstance(n, dict) and n.get("node_id")
    }
    assert expected_skill_ids <= real_skill_ids
    assert expected_skill_ids <= real_node_ids

    for mid in expected_metric_ids:
        node = data["metric_outcome_nodes"][mid]
        assert node["approval_status"] == "APPROVED_GRAPH_SSOT"
        assert "reb_unify_agentic_platform_architecture" in node["bundle_bindings"]
        assert node["surface_tokens"], f"{mid} lacks ATS surface tokens"


def test_unify_internal_only_bundle_not_external_claim():
    from apps_rg.runtime.sections.unify_graph_role_episode_registry import get_bundle_by_id

    b = get_bundle_by_id("reb_unify_dependency_graph_accelerator")
    assert b is not None
    assert b["external_claim_policy"] == "internal_only_not_external_claim"
    assert b["activation_status"] == "ACTIVE_INTERNAL_ONLY"


# ---------------------------------------------------------------------------
# PART D — Unify bullets consumption
# ---------------------------------------------------------------------------


def _unify_bullets_proof_meta():
    from apps_rg.runtime.sections.unify_role_episode_evidence import (
        attach_role_episode_bundles_to_proof_pool_metadata,
    )

    return attach_role_episode_bundles_to_proof_pool_metadata(
        {"proof_pool_type": "augmented_skills_graph", "graph_skills_proof_pool": True},
        section_id="unify_bullets",
    )


def _good_unify_bullets():
    bullets = [
        {"bullet_id": "bul_unify_001", "bullet_text": "Architected a governed agentic AI platform with deterministic routing and GraphRAG retrieval across regulated execution.", "has_metric": False},
        {"bullet_id": "bul_unify_002", "bullet_text": "Drove dependency-graph-driven modernization, reducing refactor risk across enterprise architecture.", "has_metric": False},
        {"bullet_id": "bul_unify_003", "bullet_text": "Owned runtime reliability with evaluation gates, telemetry instrumentation, and rollback controls.", "has_metric": False},
        {"bullet_id": "bul_unify_004", "bullet_text": "Standardized the AI systems lifecycle, compressing lab-to-production cycle from six months to three weeks.", "has_metric": True},
        {"bullet_id": "bul_unify_005", "bullet_text": "Engineered distributed cloud and data infrastructure on Databricks Lakehouse with vector services.", "has_metric": False},
        {"bullet_id": "bul_unify_006", "bullet_text": "Scaled the platform operating model and commercialization, generating $22M IP-led revenue and 20% margin expansion.", "has_metric": True},
    ]
    change_log = [
        {"bullet_id": "bul_unify_001", "role_episode_bundle_id": "reb_unify_agentic_platform_architecture", "graph_skill_node_ids": ["skill_governed_agentic_systems_architecture"], "source_fact_ids": ["fact_engineering_platform_001"]},
        {"bullet_id": "bul_unify_002", "role_episode_bundle_id": "reb_unify_dependency_graph_accelerator", "graph_skill_node_ids": ["skill_dependency_and_join_control"], "source_fact_ids": ["fact_engineering_platform_005"]},
        {"bullet_id": "bul_unify_003", "role_episode_bundle_id": "reb_unify_runtime_reliability_governance", "graph_skill_node_ids": ["skill_audit_grade_observability"], "source_fact_ids": ["fact_engineering_platform_003"]},
        {"bullet_id": "bul_unify_004", "role_episode_bundle_id": "reb_unify_production_adoption_lifecycle", "graph_skill_node_ids": ["skill_managed_workflow_orchestration"], "source_fact_ids": ["fact_engineering_platform_004"], "metric_outcome_ids": ["metric_unify_cycle_six_months_to_three_weeks"]},
        {"bullet_id": "bul_unify_005", "role_episode_bundle_id": "reb_unify_distributed_ecosystem_engineering", "graph_skill_node_ids": ["skill_sr_cloud_data_platform_engineering"], "source_fact_ids": ["fact_engineering_platform_002"]},
        {"bullet_id": "bul_unify_006", "role_episode_bundle_id": "reb_unify_platform_commercialization_leadership", "graph_skill_node_ids": ["skill_ai_platform_commercialization"], "source_fact_ids": ["fact_engineering_platform_006"], "metric_outcome_ids": ["metric_unify_22m_ip_led_revenue", "metric_unify_20pct_gross_margin_expansion"]},
    ]
    return bullets, {"bullets": bullets, "change_log": change_log}


def test_unify_bullets_gates_pass_on_bundle_backed_packet():
    from apps_rg.runtime.validators.unify_role_episode_x2 import (
        run_unify_bullets_role_episode_x2_gates,
    )

    bullets, parsed = _good_unify_bullets()
    gates = _gate_map(
        run_unify_bullets_role_episode_x2_gates(
            bullets=bullets,
            parsed_output=parsed,
            proof_pool_metadata=_unify_bullets_proof_meta(),
        )
    )
    for gid in (
        "x2_unify_role_episode_bundles_in_proof_pool",
        "x2_unify_bullet_role_episode_bundle_id_required",
        "x2_unify_graph_skill_node_ids_required",
        "x2_unify_source_fact_or_graph_lineage_required",
        "x2_unify_metric_outcome_id_required_when_has_metric",
        "x2_unify_flat_skill_only_graph_packet_forbidden",
        "x2_unify_generic_consulting_language_forbidden",
        "x2_unify_seniority_floor_met",
        "x2_unify_technical_specificity_floor_met",
        "x2_unify_architecture_mechanism_required",
        "x2_unify_commercial_or_operating_scope_required",
        "x2_unify_base_archive_ngram_overlap_forbidden_or_warn",
    ):
        assert gid in gates, f"missing {gid}"
        assert gates[gid].passed, f"{gid} should pass: {gates[gid].failure_reason}"


def test_unify_bullets_rejects_flat_skill_only_packet():
    from apps_rg.runtime.validators.unify_role_episode_x2 import (
        run_unify_bullets_role_episode_x2_gates,
    )

    bullets, parsed = _good_unify_bullets()
    flat_meta = {"role_episode_bundle_consumption": True, "graph_skill_node_ids": ["skill_x"]}
    gates = _gate_map(
        run_unify_bullets_role_episode_x2_gates(
            bullets=bullets, parsed_output=parsed, proof_pool_metadata=flat_meta
        )
    )
    assert not gates["x2_unify_flat_skill_only_graph_packet_forbidden"].passed
    assert not gates["x2_unify_role_episode_bundles_in_proof_pool"].passed


def test_unify_bullets_rejects_generic_consulting_and_missing_bundle_id():
    from apps_rg.runtime.validators.unify_role_episode_x2 import (
        run_unify_bullets_role_episode_x2_gates,
    )

    bullets, parsed = _good_unify_bullets()
    bullets[0]["bullet_text"] = "Partnered with stakeholders and delivered consulting engagements to drive strategic value."
    parsed["change_log"] = [{"bullet_id": "bul_unify_001"}]  # no bundle id / skills
    gates = _gate_map(
        run_unify_bullets_role_episode_x2_gates(
            bullets=bullets, parsed_output=parsed, proof_pool_metadata=_unify_bullets_proof_meta()
        )
    )
    assert not gates["x2_unify_generic_consulting_language_forbidden"].passed
    assert not gates["x2_unify_bullet_role_episode_bundle_id_required"].passed


def test_unify_bullets_rejects_metric_without_outcome_id():
    """Under derive_from_cited_facts (dec_19e9c91073ae4b5ab) a has_metric bullet must bind a bundle
    with an approved metric_outcome_id. A metric bullet that echoes no outcome id AND cites no
    bundle-linked fact (so no bundle/metric can be derived) must fail."""
    from apps_rg.runtime.validators.unify_role_episode_x2 import (
        run_unify_bullets_role_episode_x2_gates,
    )

    bullets, parsed = _good_unify_bullets()
    for entry in parsed["change_log"]:
        entry.pop("metric_outcome_ids", None)
        # Sever fact citations so no bundle (and thus no approved metric) can be derived.
        entry["source_fact_ids"] = ["fact_not_in_any_bundle_zzz"]
    gates = _gate_map(
        run_unify_bullets_role_episode_x2_gates(
            bullets=bullets, parsed_output=parsed, proof_pool_metadata=_unify_bullets_proof_meta()
        )
    )
    assert not gates["x2_unify_metric_outcome_id_required_when_has_metric"].passed


def test_unify_bullets_rejects_base_archive_hydration():
    from apps_rg.runtime.validators.unify_role_episode_x2 import (
        run_unify_bullets_role_episode_x2_gates,
    )

    bullets, parsed = _good_unify_bullets()
    combined = "\n".join(b["bullet_text"] for b in bullets)
    gates = _gate_map(
        run_unify_bullets_role_episode_x2_gates(
            bullets=bullets,
            parsed_output=parsed,
            proof_pool_metadata=_unify_bullets_proof_meta(),
            base_texts=[combined],
        )
    )
    assert not gates["x2_unify_base_archive_ngram_overlap_forbidden_or_warn"].passed


# ---------------------------------------------------------------------------
# PART E — Unify narrative consumption
# ---------------------------------------------------------------------------


def _unify_narrative_proof_meta():
    from apps_rg.runtime.sections.unify_role_episode_evidence import (
        attach_role_episode_bundles_to_proof_pool_metadata,
    )

    return attach_role_episode_bundles_to_proof_pool_metadata(
        {"proof_pool_type": "augmented_skills_graph", "graph_skills_proof_pool": True},
        section_id="unify_narrative",
    )


def _good_unify_narrative():
    sentence = (
        "Owned the platform roadmap and commercialization of a governed agentic AI platform at Unify "
        "Consulting, architecting deterministic runtime and scaling reusable platform services for regulated adoption."
    )
    parsed = {
        "narrative_sentence": sentence,
        "role_episode_bundle_ids": ["reb_unify_platform_commercialization_leadership"],
        "change_log": [
            {
                "role_episode_bundle_id": "reb_unify_agentic_platform_architecture",
                "graph_skill_node_ids": ["skill_governed_agentic_systems_architecture"],
                "source_fact_ids": ["fact_engineering_platform_001"],
            }
        ],
    }
    return sentence, parsed


def test_unify_narrative_gates_pass_on_bundle_backed_packet():
    from apps_rg.runtime.validators.unify_role_episode_x2 import (
        run_unify_narrative_role_episode_x2_gates,
    )

    sentence, parsed = _good_unify_narrative()
    gates = _gate_map(
        run_unify_narrative_role_episode_x2_gates(
            narrative_sentence=sentence,
            parsed_output=parsed,
            proof_pool_metadata=_unify_narrative_proof_meta(),
        )
    )
    for gid in (
        "x2_unify_narrative_role_episode_bundles_in_proof_pool",
        "x2_unify_narrative_role_episode_bundle_id_required",
        "x2_unify_narrative_graph_skill_node_ids_required",
        "x2_unify_narrative_source_fact_or_graph_lineage_required",
        "x2_unify_narrative_flat_skill_only_forbidden",
        "x2_unify_narrative_generic_consulting_language_forbidden",
        "x2_unify_narrative_unsupported_new_claim_forbidden",
        "x2_unify_narrative_base_archive_ngram_overlap_forbidden_or_warn",
        "x2_unify_narrative_seniority_floor_met",
        "x2_unify_narrative_technical_specificity_floor_met",
    ):
        assert gid in gates, f"missing {gid}"
        assert gates[gid].passed, f"{gid} should pass: {gates[gid].failure_reason}"


def test_unify_narrative_rejects_flat_and_missing_bundle():
    from apps_rg.runtime.validators.unify_role_episode_x2 import (
        run_unify_narrative_role_episode_x2_gates,
    )

    sentence, parsed = _good_unify_narrative()
    parsed["role_episode_bundle_ids"] = []
    parsed["change_log"] = []
    flat_meta = {"role_episode_bundle_consumption": True, "graph_skill_node_ids": ["skill_x"]}
    gates = _gate_map(
        run_unify_narrative_role_episode_x2_gates(
            narrative_sentence=sentence, parsed_output=parsed, proof_pool_metadata=flat_meta
        )
    )
    assert not gates["x2_unify_narrative_flat_skill_only_forbidden"].passed
    assert not gates["x2_unify_narrative_role_episode_bundle_id_required"].passed


def test_unify_narrative_rejects_unsupported_new_claim():
    from apps_rg.runtime.validators.unify_role_episode_x2 import (
        run_unify_narrative_role_episode_x2_gates,
    )

    sentence, parsed = _good_unify_narrative()
    bad = sentence + " delivering $99M in net-new bookings and 73% adoption."
    gates = _gate_map(
        run_unify_narrative_role_episode_x2_gates(
            narrative_sentence=bad,
            parsed_output=parsed,
            proof_pool_metadata=_unify_narrative_proof_meta(),
        )
    )
    assert not gates["x2_unify_narrative_unsupported_new_claim_forbidden"].passed


def test_unify_narrative_rejects_generic_consulting_language():
    from apps_rg.runtime.validators.unify_role_episode_x2 import (
        run_unify_narrative_role_episode_x2_gates,
    )

    sentence, parsed = _good_unify_narrative()
    bad = "Partnered with stakeholders to drive strategic value and ensure alignment across delivery."
    gates = _gate_map(
        run_unify_narrative_role_episode_x2_gates(
            narrative_sentence=bad,
            parsed_output=parsed,
            proof_pool_metadata=_unify_narrative_proof_meta(),
        )
    )
    assert not gates["x2_unify_narrative_generic_consulting_language_forbidden"].passed


# ---------------------------------------------------------------------------
# Config enablement
# ---------------------------------------------------------------------------


def _config_section(section_id: str):
    profile = yaml.safe_load(
        (REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "section_retrieval_profile.yaml").read_text("utf-8")
    )
    for sec in profile.get("sections", []):
        if sec.get("section_id") == section_id:
            return sec
    raise AssertionError(f"{section_id} not found in section_retrieval_profile.yaml")


def test_headline_config_enables_graph_only_in_bundle_mode():
    sec = _config_section("headline")
    assert sec["graph_expansion_allowed"] is True
    assert sec["headline_positioning_bundle_consumption"] == "required"
    assert sec["graph_expansion_mode"] == "headline_positioning_bundle_only"


@pytest.mark.parametrize("section_id", ["unify_bullets", "unify_narrative"])
def test_unify_config_enables_graph_only_in_role_episode_mode(section_id):
    sec = _config_section(section_id)
    assert sec["graph_expansion_allowed"] is True
    assert sec["role_episode_bundle_consumption"] == "required"
    assert sec["graph_expansion_mode"] == "role_episode_bundle_only"


# ---------------------------------------------------------------------------
# Cross-section shared guards
# ---------------------------------------------------------------------------


def test_cross_section_guards_detect_signals():
    from apps_rg.runtime.sections.cross_section_signal_guards import (
        detect_generic_consulting_phrases,
        detect_jd_only_phrases,
        is_flat_skill_only_graph_packet,
        seniority_floor_score,
        technical_specificity_score,
    )

    assert seniority_floor_score("Owned and scaled the platform") >= 1
    assert technical_specificity_score("deterministic routing and GraphRAG retrieval") >= 1
    assert detect_generic_consulting_phrases("partnered with stakeholders")
    assert detect_jd_only_phrases("alpha beta gamma delta epsilon zeta", "x alpha beta gamma delta epsilon zeta y", min_run=6)
    assert is_flat_skill_only_graph_packet({"graph_skill_node_ids": ["s"]})
    assert not is_flat_skill_only_graph_packet({"role_episode_bundles": [{"x": 1}]})


# ---------------------------------------------------------------------------
# Competencies capability-family anchor injection (Author-Gate dec_19e9daa115a62cf3a)
# ---------------------------------------------------------------------------


def _llmops_packet():
    return {
        "competency_bundles": [
            {
                "competency_bundle_id": "ccb_llmops_reliability",
                "capability_family": "llmops_reliability",
                "graph_skill_node_ids": ["skill_audit_grade_observability"],
                "linked_source_fact_ids": ["fact_engineering_platform_004"],
                "vocabulary_anchors": [
                    "audit-grade observability",
                    "evaluation gauntlet design",
                ],
            }
        ]
    }


def test_competencies_anchor_injection_covers_uncovered_family():
    from apps_rg.runtime.sections.competency_capability_evidence import (
        augment_bound_category_family_terms,
    )

    # A leadership-framed category bound to the LLMOps bundle with NO observability vocabulary.
    cats = [
        {
            "category_label": "Engineering & Delivery Leadership",
            "competency_bundle_id": "ccb_llmops_reliability",
            "terms": [
                {"text": "Engineering organization scale-out", "source_fact_ids": ["fact_exec_002"]},
            ],
        }
    ]
    augment_bound_category_family_terms(
        cats,
        packet=_llmops_packet(),
        allowed_fact_ids={"fact_engineering_platform_004", "fact_exec_002"},
    )
    texts = " ".join(str(t.get("text") or "") for t in cats[0]["terms"]).lower()
    assert "observability" in texts  # LLMOps family now lexically covered
    injected = [t for t in cats[0]["terms"] if "observability" in str(t.get("text") or "").lower()]
    assert injected and injected[0]["source_fact_id"] == "fact_engineering_platform_004"
    assert injected[0].get("source_skill_ids")  # graph-backed, not default_fid


def test_competencies_anchor_injection_no_fabrication_without_allowed_fact():
    from apps_rg.runtime.sections.competency_capability_evidence import (
        augment_bound_category_family_terms,
    )

    cats = [
        {
            "category_label": "Engineering & Delivery Leadership",
            "competency_bundle_id": "ccb_llmops_reliability",
            "terms": [{"text": "Engineering organization scale-out", "source_fact_ids": ["fact_exec_002"]}],
        }
    ]
    before = len(cats[0]["terms"])
    # No allowed linked fact -> no injection (no fabricated provenance).
    augment_bound_category_family_terms(
        cats, packet=_llmops_packet(), allowed_fact_ids={"fact_exec_002"}
    )
    assert len(cats[0]["terms"]) == before
