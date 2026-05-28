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
        assert b["time_window"] == UNIFY_TIME_WINDOW
        assert b["graph_skill_node_ids"]


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
    from apps_rg.runtime.validators.unify_role_episode_x2 import (
        run_unify_bullets_role_episode_x2_gates,
    )

    bullets, parsed = _good_unify_bullets()
    for entry in parsed["change_log"]:
        entry.pop("metric_outcome_ids", None)
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
