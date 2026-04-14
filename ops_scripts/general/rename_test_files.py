"""One-shot rename script: strip low-signal tokens (phase/wave/vX/reqNNN) from test filenames."""

from __future__ import annotations

import os
from pathlib import Path
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]

RENAMES: list[tuple[str, str]] = [
    # ── tests/guardian ────────────────────────────────────────────────────────
    (
        "tests/guardian/test_v15_p2_compliance.py",
        "tests/guardian/test_determinism_replayability_contracts.py",
    ),
    (
        "tests/guardian/test_v15_p2_wave2_1_inventory.py",
        "tests/guardian/test_runtime_entrypoint_inventory.py",
    ),
    ("tests/guardian/test_v15_p3_compliance.py", "tests/guardian/test_governance_escalation_contracts.py"),
    ("tests/guardian/test_v15_p4_compliance.py", "tests/guardian/test_traceability_provenance_contracts.py"),
    ("tests/guardian/test_v15_p5_compliance.py", "tests/guardian/test_crypto_trust_signing_contracts.py"),
    ("tests/guardian/test_v15_p6_compliance.py", "tests/guardian/test_meta_invariant_governance.py"),
    ("tests/guardian/test_v15_p7_bugfixes.py", "tests/guardian/test_execution_gateway_bugfixes.py"),
    (
        "tests/guardian/test_v15_p8_2c_mode_matrix.py",
        "tests/guardian/test_enforcement_mode_transition_matrix.py",
    ),
    ("tests/guardian/test_v15_p8_cat_c.py", "tests/guardian/test_mission_runner_wiring.py"),
    ("tests/guardian/test_v15_p8_cat_d.py", "tests/guardian/test_retry_mixin_wiring.py"),
    ("tests/guardian/test_v15_p8_cat_e.py", "tests/guardian/test_ssot_bootstrap_wiring.py"),
    ("tests/guardian/test_v15_p10_1_review_summary.py", "tests/guardian/test_review_summary_generator.py"),
    ("tests/guardian/test_v15_p10_2_policy_pack.py", "tests/guardian/test_policy_pack_validator.py"),
    ("tests/guardian/test_v15_p10_4_incident_bundle.py", "tests/guardian/test_incident_bundle_generator.py"),
    ("tests/guardian/test_execute_ssot_v15_contract.py", "tests/guardian/test_execute_ssot_contract.py"),
    ("tests/guardian/test_healers_wave6.py", "tests/guardian/test_structure_healers.py"),
    # ── tests/governance ──────────────────────────────────────────────────────
    ("tests/governance/test_req016_020_fail_closed.py", "tests/governance/test_fail_closed.py"),
    (
        "tests/governance/test_req018_hmac_artifact_coverage.py",
        "tests/governance/test_hmac_artifact_coverage.py",
    ),
    (
        "tests/governance/test_req060_063_meta_learning_replay.py",
        "tests/governance/test_meta_learning_replay.py",
    ),
    ("tests/governance/test_req071_stage8_uwg_routing.py", "tests/governance/test_uwg_routing.py"),
    ("tests/governance/test_req085_086_hil.py", "tests/governance/test_hil_approval.py"),
    (
        "tests/governance/test_req087_modify_diff_signature_invalidation.py",
        "tests/governance/test_diff_signature_invalidation.py",
    ),
    ("tests/governance/test_req091_tier3_freeze.py", "tests/governance/test_tier3_freeze.py"),
    ("tests/governance/test_req095_prompt_determinism.py", "tests/governance/test_prompt_determinism.py"),
    ("tests/governance/test_req106_replay_sandbox.py", "tests/governance/test_replay_sandbox.py"),
    ("tests/governance/test_req111_no_uuid4_determinism.py", "tests/governance/test_no_uuid4_determinism.py"),
    (
        "tests/governance/test_req114_no_wallclock_determinism.py",
        "tests/governance/test_no_wallclock_determinism.py",
    ),
    ("tests/governance/test_req118_no_reflection_bypass.py", "tests/governance/test_no_reflection_bypass.py"),
    (
        "tests/governance/test_req121_126_subprocess_env.py",
        "tests/governance/test_subprocess_env_isolation.py",
    ),
    ("tests/governance/test_req129_no_mutable_globals.py", "tests/governance/test_no_mutable_globals.py"),
    ("tests/governance/test_req136_256_cross_layer_schema.py", "tests/governance/test_cross_layer_schema.py"),
    ("tests/governance/test_req157_302_trace_replay.py", "tests/governance/test_trace_replay.py"),
    ("tests/governance/test_req158_303_hash_chain_tamper.py", "tests/governance/test_hash_chain_tamper.py"),
    ("tests/governance/test_req177_354_sig_before_effect.py", "tests/governance/test_sig_before_effect.py"),
    (
        "tests/governance/test_req184_381_384_canonical_hash_replay.py",
        "tests/governance/test_canonical_hash_replay.py",
    ),
    (
        "tests/governance/test_req186_390_392_393_395_396_hmac_lifecycle.py",
        "tests/governance/test_hmac_lifecycle.py",
    ),
    (
        "tests/governance/test_req188_189_398_399_403_404_407_enclave_replay.py",
        "tests/governance/test_enclave_replay.py",
    ),
    (
        "tests/governance/test_req192_409_semantic_clock_replay.py",
        "tests/governance/test_semantic_clock_replay.py",
    ),
    ("tests/governance/test_req199_211_236_emission.py", "tests/governance/test_guardian_emission.py"),
    (
        "tests/governance/test_req201_212_222_242_262_289_rag_law_rollback.py",
        "tests/governance/test_rag_law_rollback.py",
    ),
    ("tests/governance/test_req239_240_quorum.py", "tests/governance/test_quorum.py"),
    (
        "tests/governance/test_req243_244_247_audit_completeness.py",
        "tests/governance/test_audit_completeness.py",
    ),
    ("tests/governance/test_req245_248_hil_ttl.py", "tests/governance/test_hil_ttl.py"),
    (
        "tests/governance/test_req253_254_cross_wave_linkage.py",
        "tests/governance/test_cross_context_linkage.py",
    ),
    ("tests/governance/test_req270_273_seam_mutable_ref.py", "tests/governance/test_seam_mutable_ref.py"),
    (
        "tests/governance/test_req298_337_discovery_promotion.py",
        "tests/governance/test_discovery_promotion.py",
    ),
    ("tests/governance/test_req307_308_evidence_replay.py", "tests/governance/test_evidence_replay.py"),
    (
        "tests/governance/test_req313_320_surgical_ssot_replay.py",
        "tests/governance/test_surgical_ssot_replay.py",
    ),
    (
        "tests/governance/test_req327_331_360_365_side_effect_legality.py",
        "tests/governance/test_side_effect_legality.py",
    ),
    ("tests/governance/test_req345_349_freeze_subsystems.py", "tests/governance/test_freeze_subsystems.py"),
    ("tests/governance/test_req346_347_tier3_authority.py", "tests/governance/test_tier3_authority.py"),
    (
        "tests/governance/test_req378_384_forensic_determinism.py",
        "tests/governance/test_forensic_determinism.py",
    ),
    (
        "tests/governance/test_req411_413_provider_binding.py",
        "tests/governance/test_provider_binding_contracts.py",
    ),
    (
        "tests/governance/test_req413_provider_binding_determinism.py",
        "tests/governance/test_provider_binding_determinism.py",
    ),
    ("tests/governance/test_req414_egress_guard.py", "tests/governance/test_egress_guard.py"),
    ("tests/governance/test_req414_network_egress_guard.py", "tests/governance/test_network_egress_guard.py"),
    (
        "tests/governance/test_req415_provider_substitution_prohibition.py",
        "tests/governance/test_provider_substitution_prohibition.py",
    ),
    (
        "tests/governance/test_req416_critical_dual_enforcement.py",
        "tests/governance/test_critical_dual_enforcement.py",
    ),
    (
        "tests/governance/test_req417_runtime_mutation_guard.py",
        "tests/governance/test_runtime_mutation_guard.py",
    ),
    (
        "tests/governance/test_req_p0_canonical_digest_stability.py",
        "tests/governance/test_canonical_digest_stability.py",
    ),
    (
        "tests/governance/test_req_p0_capability_replay_binding.py",
        "tests/governance/test_capability_replay_binding.py",
    ),
    ("tests/governance/test_req_p0_gateway_monopoly.py", "tests/governance/test_gateway_monopoly.py"),
    (
        "tests/governance/test_req_p0_runtime_write_interceptor.py",
        "tests/governance/test_runtime_write_interceptor.py",
    ),
    (
        "tests/governance/test_req_p1_freeze_complete_revocation.py",
        "tests/governance/test_freeze_complete_revocation.py",
    ),
    ("tests/governance/test_req_p1_freeze_timing.py", "tests/governance/test_freeze_timing.py"),
    (
        "tests/governance/test_req_p2_cognitive_diff_trusted.py",
        "tests/governance/test_cognitive_diff_trusted.py",
    ),
    (
        "tests/governance/test_req_p2_deterministic_velocity.py",
        "tests/governance/test_deterministic_velocity.py",
    ),
    (
        "tests/governance/test_req_p2_evacuation_discipline.py",
        "tests/governance/test_evacuation_discipline.py",
    ),
    (
        "tests/governance/test_req_p2_metrics_chokepoint_ast.py",
        "tests/governance/test_metrics_chokepoint_ast.py",
    ),
    (
        "tests/governance/test_req_p2_metrics_single_emission.py",
        "tests/governance/test_metrics_single_emission.py",
    ),
    # ── tests/evaluation ──────────────────────────────────────────────────────
    ("tests/evaluation/test_phase1_metrics.py", "tests/evaluation/test_eval_metrics.py"),
    ("tests/evaluation/test_phase1_runners.py", "tests/evaluation/test_eval_runners.py"),
    ("tests/evaluation/test_phase1_schemas.py", "tests/evaluation/test_eval_schemas.py"),
    ("tests/evaluation/test_phase2_retrieval.py", "tests/evaluation/test_eval_retrieval.py"),
    ("tests/evaluation/test_phase3_chunking.py", "tests/evaluation/test_eval_chunking.py"),
    ("tests/evaluation/test_phase4_monitoring.py", "tests/evaluation/test_eval_monitoring.py"),
    ("tests/evaluation/test_phase5_feedback.py", "tests/evaluation/test_eval_feedback.py"),
    (
        "tests/evaluation/test_phase6_completeness_retrieval.py",
        "tests/evaluation/test_eval_completeness_retrieval.py",
    ),
    # ── tests/integration ─────────────────────────────────────────────────────
    ("tests/integration/test_phase1_enforcer_seam.py", "tests/integration/test_enforcer_seam.py"),
    (
        "tests/integration/test_phase2_orchestrator_hardening.py",
        "tests/integration/test_orchestrator_hardening.py",
    ),
    (
        "tests/integration/test_phase3_router_discrimination.py",
        "tests/integration/test_router_discrimination.py",
    ),
    (
        "tests/integration/test_phase4_stability_guardrails.py",
        "tests/integration/test_stability_guardrails.py",
    ),
    ("tests/integration/test_phase5_authority_boundary.py", "tests/integration/test_authority_boundary.py"),
    ("tests/integration/test_phase_b_memory_routing.py", "tests/integration/test_memory_routing.py"),
    (
        "tests/integration/test_wave_creative_cross_wave.py",
        "tests/integration/test_creative_cross_context.py",
    ),
    # ── tests/system_learning ─────────────────────────────────────────────────
    ("tests/system_learning/test_phase_a_learning_loop.py", "tests/system_learning/test_learning_loop.py"),
    (
        "tests/system_learning/test_w2_negative_control.py",
        "tests/system_learning/test_healing_optimizer_negative_control.py",
    ),
    (
        "tests/system_learning/test_w3_negative_control.py",
        "tests/system_learning/test_pattern_analysis_negative_control.py",
    ),
    ("tests/system_learning/test_w5_replay_engine.py", "tests/system_learning/test_replay_engine.py"),
    # ── tests/unit (top-level) ────────────────────────────────────────────────
    ("tests/unit/test_phase2_retrieval_anchors.py", "tests/unit/test_retrieval_anchors.py"),
    ("tests/unit/test_phase2_versioned_config.py", "tests/unit/test_versioned_config.py"),
    ("tests/unit/test_phase3_detection_signal.py", "tests/unit/test_detection_signal.py"),
    ("tests/unit/test_phase3_l4_persistence.py", "tests/unit/test_l4_persistence.py"),
    ("tests/unit/test_phase4_ml_compatibility.py", "tests/unit/test_ml_compatibility.py"),
    ("tests/unit/test_phase4_ml_end_to_end_envelope.py", "tests/unit/test_ml_end_to_end_envelope.py"),
    ("tests/unit/test_phase4_ml_write_envelope.py", "tests/unit/test_ml_write_envelope.py"),
    ("tests/unit/test_phase5_l4_violation_persistence.py", "tests/unit/test_l4_violation_persistence.py"),
    ("tests/unit/test_phase5_violation_event.py", "tests/unit/test_violation_event.py"),
    ("tests/unit/test_phase6_readonly_scope.py", "tests/unit/test_readonly_scope.py"),
    ("tests/unit/test_phase6_retrieval_snapshot.py", "tests/unit/test_retrieval_snapshot.py"),
    ("tests/unit/test_phase7_tool_executor.py", "tests/unit/test_tool_executor.py"),
    ("tests/unit/test_phase7_tool_intent_model.py", "tests/unit/test_tool_intent_model.py"),
    ("tests/unit/test_phase8_citation_bundle_model.py", "tests/unit/test_citation_bundle_model.py"),
    ("tests/unit/test_phase8_citation_enforcement.py", "tests/unit/test_citation_enforcement.py"),
    ("tests/unit/test_phase9_replay_bundle_model.py", "tests/unit/test_replay_bundle_model.py"),
    ("tests/unit/test_phase9_replay_verifier.py", "tests/unit/test_replay_verifier.py"),
    ("tests/unit/test_runtime_state_digest_phase2.py", "tests/unit/test_runtime_state_digest.py"),
    ("tests/unit/test_ssot_mixins_phase2_7.py", "tests/unit/test_ssot_mixin_integration.py"),
    ("tests/unit/test_wave1_cda_sync_wrapper.py", "tests/unit/test_cda_sync_wrapper.py"),
    ("tests/unit/test_wave2_gravity_exclusion.py", "tests/unit/test_gravity_exclusion.py"),
    ("tests/unit/test_wave4_v15_agent_id.py", "tests/unit/test_agent_id_contracts.py"),
    ("tests/unit/test_wave5_longpaths_guard.py", "tests/unit/test_longpaths_guard.py"),
    ("tests/unit/test_wave6_hitl_gates.py", "tests/unit/test_hitl_gates.py"),
    # ── tests/unit_min_deps ───────────────────────────────────────────────────
    (
        "tests/unit_min_deps/test_phase2_unsafe_io_enforcement.py",
        "tests/unit_min_deps/test_unsafe_io_enforcement.py",
    ),
    ("tests/unit_min_deps/test_phase7_hardening.py", "tests/unit_min_deps/test_l4_state_writer_isolation.py"),
    (
        "tests/unit_min_deps/test_phase8_hardening.py",
        "tests/unit_min_deps/test_pattern_analysis_hardening.py",
    ),
    (
        "tests/unit_min_deps/test_phase9_hardening.py",
        "tests/unit_min_deps/test_resource_predictor_hardening.py",
    ),
    ("tests/unit_min_deps/test_w5_determinism_digest.py", "tests/unit_min_deps/test_determinism_digest.py"),
    (
        "tests/unit_min_deps/test_w5_executiontrace_plan_hash.py",
        "tests/unit_min_deps/test_executiontrace_plan_hash.py",
    ),
    (
        "tests/unit_min_deps/test_w5_handshake_state_machine.py",
        "tests/unit_min_deps/test_handshake_state_machine.py",
    ),
    (
        "tests/unit_min_deps/test_w5_l3_orchestrator_paths.py",
        "tests/unit_min_deps/test_l3_orchestrator_paths.py",
    ),
    (
        "tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py",
        "tests/unit_min_deps/test_meta_learning_intake_wiring.py",
    ),
    # ── tests/unit/agentic_core subdirectories ────────────────────────────────
    ("tests/unit/agentic_core/cache/test_redis_mcp_p3.py", "tests/unit/agentic_core/cache/test_redis_mcp.py"),
    (
        "tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_phase2.py",
        "tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_routing.py",
    ),
    (
        "tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_phase2_hang_fix.py",
        "tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_hang_fix.py",
    ),
    (
        "tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_phases345.py",
        "tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_legacy_stages.py",
    ),
    (
        "tests/unit/agentic_core/L0_routing/scripts/test_find_real_duplicates_v2_util.py",
        "tests/unit/agentic_core/L0_routing/scripts/test_find_real_duplicates_util.py",
    ),
    (
        "tests/unit/agentic_core/L0_routing/scripts/test_v25_structural_strictness.py",
        "tests/unit/agentic_core/L0_routing/scripts/test_structural_strictness.py",
    ),
    (
        "tests/unit/agentic_core/L0_routing/types/test_v15_contracts_types_adg.py",
        "tests/unit/agentic_core/L0_routing/types/test_guardian_contracts_types_adg.py",
    ),
    (
        "tests/unit/agentic_core/L0_routing/types/test_v15_p2_contracts_types_adg.py",
        "tests/unit/agentic_core/L0_routing/types/test_determinism_contracts_types_adg.py",
    ),
    (
        "tests/unit/agentic_core/L0_routing/utils/test_sovereign_alignment_v2_util_adg.py",
        "tests/unit/agentic_core/L0_routing/utils/test_sovereign_alignment_util_adg.py",
    ),
    (
        "tests/unit/agentic_core/L2_execution/healers/test_healing_tier_dispatcher_phase2_integration.py",
        "tests/unit/agentic_core/L2_execution/healers/test_healing_tier_dispatcher_integration.py",
    ),
    (
        "tests/unit/agentic_core/L2_execution/tools/test_git_ops_mcp_p1.py",
        "tests/unit/agentic_core/L2_execution/tools/test_git_ops_mcp.py",
    ),
    (
        "tests/unit/agentic_core/L2_execution/tools/test_read_gateway_p4.py",
        "tests/unit/agentic_core/L2_execution/tools/test_read_gateway.py",
    ),
    (
        "tests/unit/agentic_core/L2_execution/utils/test_egress_mcp_p2.py",
        "tests/unit/agentic_core/L2_execution/utils/test_egress_mcp.py",
    ),
    (
        "tests/unit/agentic_core/L3_orchestration/reasoning/test_state_management_mcp_p5.py",
        "tests/unit/agentic_core/L3_orchestration/reasoning/test_state_management_mcp.py",
    ),
    ("tests/unit/apps_shared/test_apps_refactor_phases.py", "tests/unit/apps_shared/test_apps_refactor.py"),
]


def main() -> None:
    renamed = 0
    skipped_missing = 0
    collisions: list[str] = []

    for src_rel, dst_rel in tqdm(RENAMES, desc="Processing", unit="item"):
        src = ROOT / src_rel
        dst = ROOT / dst_rel

        if not src.exists():
            print(f"  SKIP (missing)  {src_rel}")
            skipped_missing += 1
            continue

        if dst.exists():
            collisions.append(f"  COLLISION: {dst_rel} already exists (src={src_rel})")
            continue

        os.rename(src, dst)
        print(f"  OK  {src.name}  →  {dst.name}")
        renamed += 1

    print()
    print(f"Renamed:        {renamed}")
    print(f"Skipped:        {skipped_missing}")
    print(f"Collisions:     {len(collisions)}")
    for c in collisions:
        print(c)


if __name__ == "__main__":
    main()
