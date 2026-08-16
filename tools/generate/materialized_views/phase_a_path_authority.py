"""Phase A materialized views — Critical path, authority/sovereignty, lifecycle, topology seeds.

Covers view families:
    1. Critical path and spine (mv_critical_path_segments, mv_runtime_spine_gaps,
       mv_path_criticality_rollup)
    2. Authority and sovereignty (mv_authority_boundary_breaches, mv_write_sovereignty_paths,
       mv_live_future_mutation_conflicts, mv_hitl_reclearance_gaps)
    3. Lifecycle and phase coverage (mv_l2_phase_coverage, mv_exit_disposition_coverage,
       mv_heal_retry_exit_gaps)
    Partial 8. Determinism seeds (mv_digest_reconciliation, mv_snapshot_integrity_anomalies)
    Partial 10. Topology seeds (mv_hotspot_centrality, mv_unknown_taxonomy_and_orphans)
    11. Prompt-assembly wiring gaps (mv_prompt_assembly_wiring_gaps)

All tables are physical (DROP + CREATE AS SELECT), idempotent, and snapshot-stamped via
    (SELECT value FROM meta WHERE key='commit_sha') AS snapshot_id
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from tools.generate.infra_wiring_views import materialize_receipt_ast_sites
from tools.generate.materialized_views.sqlite_helpers import (
    connect_sqlite_for_mv as _connect_sqlite,
)

_PHASE_A_TABLES: tuple[str, ...] = (
    "mv_critical_path_segments",
    "mv_runtime_spine_gaps",
    "mv_path_criticality_rollup",
    "mv_authority_boundary_breaches",
    "mv_write_sovereignty_paths",
    "mv_live_future_mutation_conflicts",
    "mv_hitl_reclearance_gaps",
    "mv_l2_phase_coverage",
    "mv_exit_disposition_coverage",
    "mv_heal_retry_exit_gaps",
    "mv_digest_reconciliation",
    "mv_snapshot_integrity_anomalies",
    "mv_hotspot_centrality",
    "mv_unknown_taxonomy_and_orphans",
    "mv_prompt_assembly_wiring_gaps",
    "mv_handoff_witness_tiers",
    "mv_cross_cutting_witness_tiers",
    "mv_local_heal_first_breaches",
    "mv_observability_interference_breaches",
)

_SPINE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")

# Layers whose imports count as evidence of spine-connectivity when auditing
# spine-layer modules. L_APP/L_SHARED sit above the runtime spine but actively
# consume its exports — their imports prove a module is reachable.
_SPINE_CONNECTION_SOURCE_LAYERS = (
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L_APP",
    "L_SHARED",
)


def _spine_connection_sources_in() -> str:
    return "(" + ", ".join(f"'{l}'" for l in _SPINE_CONNECTION_SOURCE_LAYERS) + ")"


_FORBIDDEN_LAYER_PAIRS = (
    ("L6", "L2"),
    ("L6", "L0"),
    ("L6", "L1"),
    ("L_APP", "L0"),
    ("L_APP", "L1"),
    ("L_APP", "L2"),
)

_UWG_PATH_FRAGMENTS = (
    "UniversalWrite",
    "write_gateway",
    "uwg",
    "mutation_prohibition",
    "durable_write",
)

# Symbol-pattern fragments matching canonical UWG call sites (e.g. ``_wg.write_text(...)``,
# ``self._wg.commit(...)``, ``write_gateway.commit(...)``). A write whose ``e.symbol``
# matches any of these is UWG-routed regardless of which file makes the call.
# Without this, ~117/1483 violations on the 04282026_1853 snapshot were false positives
# because callers using the ``_wg`` abbreviation were misclassified by path-only detection.
_UWG_SYMBOL_FRAGMENTS = (
    "_wg.",
    "self._wg.",
    "self.uwg.",
    "self.write_gateway.",
    "write_gateway.",
    "uwg.",
    "UniversalWrite",
)

# Symbol fragments identifying writes that go through the canonical L5
# ArchivalGatekeeper file-operation authority. Per
# agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py docstring:
# "Singleton/Static Service - Single point of control for all file operations
# (move, delete, archive) across the entire codebase". Routing through
# ArchivalGatekeeper IS the design-correct path for file-system operations,
# analogous to routing through UWG for L4 state mutations. These symbols are
# NOT bypasses and MUST be excluded from mv_write_sovereignty_paths.
# 2026-04-28 W2.1 finding.
_ARCHIVAL_GATEKEEPER_SYMBOL_FRAGMENTS = (
    ".safe_move",
    ".safe_archive",
    ".safe_delete",
    "ArchivalGatekeeper",
)

# Symbol names that can be emitted by the broad governance write-edge scanner
# but are read/check/helper operations, not durable state writes. Keep this list
# tight: real write methods such as write_text/open remain in the MV until
# routed through UWG or explicitly handled by another authority.
_NON_MUTATING_WRITE_SYMBOLS = (
    "assert_no_persistent_write",
    "compute_content_hash",
    "get_bm25_store",
    "get_default_store",
    "get_validated_project_root",
    "is_commit_sandbox_active",
)

# Exact symbols for generated artifact writes. These produce operator reports,
# receipts, closeouts, briefs, and local proof artifacts rather than durable
# agent state. Exact matching keeps real generic writes such as path.write_text
# visible until routed or otherwise justified.
_NON_DURABLE_ARTIFACT_WRITE_SYMBOLS = (
    "CLOSEOUT_JSON.write_text",
    "CLOSEOUT_MD.write_text",
    "DESIGN_PATH.write_text",
    "OUT_JSON.write_text",
    "OUT_MD.write_text",
    "OUT_PATH.write_text",
    "OUT_RECEIPT_JSON.write_text",
    "OUT_RECEIPT_MD.write_text",
    "P1_W5_RECEIPT_JSON.write_text",
    "P1_W5_RECEIPT_MD.write_text",
    "artifact.write_text",
    "artifact_path.write_text",
    "assertion_path.write_text",
    "baseline_file.write_text",
    "brief_path.write_text",
    "briefing_path.write_text",
    "company_brief_path.write_text",
    "contract_path.write_text",
    "coverage_path.write_text",
    "json_path.write_text",
    "man_path.write_text",
    "manifest_path.write_text",
    "md_path.write_text",
    "meta_path.write_text",
    "mf_path.write_text",
    "out.write_text",
    "out_json.write_text",
    "out_md.write_text",
    "out_path.write_text",
    "output_file.write_text",
    "output_path.write_text",
    "p_receipt.write_text",
    "rc_path.write_text",
    "rca_path.write_text",
    "receipt_json_path.write_text",
    "receipt_md_path.write_text",
    "receipt_path.write_text",
    "report_path.write_text",
    "requirements_path.write_text",
    "summary_path.write_text",
    "wizard_brief_path.write_text",
)

# Additional scanner false positives: factory/process calls that may have side
# effects but are not durable state writes and should not be counted as UWG
# bypass rows in write-sovereignty.
_NON_DURABLE_ARTIFACT_HELPER_SYMBOLS = (
    "TraceFeatureRecord.from_bundle",
    "create_artifact",
    "create_legacy_import_healer",
    "subprocess.Popen",
)

# Site-scoped generated artifact writes from the 07082026_2319 P0 backlog.
# These symbols are generic enough that a symbol-only exemption would hide
# future real writes; bind them to the exact artifact-producing source files.
_NON_DURABLE_ARTIFACT_WRITE_SITES = (
    ("bundle_path.write_text", "apps_shared/spine_emission/reseal.py"),
    ("closeout_path.write_text", "apps_rg/fact_inventory/track_weighted_graph_expansion.py"),
    ("dest.write_text", "apps_rg/runtime/c0/prior_resume_variant_extractor.py"),
    ("dst_path.write_text", "apps_shared/spine_emission/context.py"),
    ("input_path.write_text", "apps_shared/cli/interactive_wizard.py"),
    ("learning_path.write_text", "apps_rg/runtime/shadow/competencies_l6.py"),
    ("nhsr_path.write_text", "agentic_core/runtime/entrypoints/integrated_fallback_run.py"),
    ("nhsr_path.write_text", "agentic_core/runtime/entrypoints/integrated_grounded_read_run.py"),
    ("nhsr_path.write_text", "agentic_core/runtime/entrypoints/integrated_managed_workflow_real_run.py"),
    ("nhsr_path.write_text", "agentic_core/runtime/entrypoints/integrated_single_action_run.py"),
    ("p.write_text", "apps_research/reasoning/ResearchOrchestrator.py"),
    ("p_bridge.write_text", "apps_rg/runtime/spine/c0_fec_compose.py"),
    ("p_bundle.write_text", "apps_rg/runtime/section_runtime_exhaust_spine_receipt.py"),
    ("p_cert.write_text", "apps_rg/runtime/section_one_spine_certification.py"),
    ("p_handoff.write_text", "apps_rg/runtime/section_runtime_exhaust_spine_receipt.py"),
    ("p_l1.write_text", "apps_rg/runtime/spine/front_contracts.py"),
    ("p_legacy.write_text", "apps_rg/runtime/spine/c0_fec_compose.py"),
    ("p_master.write_text", "apps_rg/runtime/spine/front_contracts.py"),
    ("p_pc.write_text", "apps_rg/runtime/section_one_spine_certification.py"),
    ("p_pe.write_text", "apps_rg/runtime/section_one_spine_certification.py"),
    ("p_route.write_text", "apps_rg/runtime/spine/front_contracts.py"),
    ("p_sealed.write_text", "apps_rg/runtime/section_l2_spine_receipt.py"),
    ("p_vr.write_text", "apps_rg/runtime/spine/front_contracts.py"),
    ("prod_out.write_text", "apps_rg/l2_recipe/modular_resume_generation.py"),
    ("prod_out.write_text", "apps_rg/runtime/orchestration/patch_run.py"),
    ("proposals_path.write_text", "apps_rg/runtime/shadow/competencies_l6.py"),
    ("receipt_json.write_text", "apps_rg/fact_inventory/run_w14_senior_role_offline_traversal.py"),
    ("sm_path.write_text", "apps_rg/runtime/evidence/canonical_evidence_digest_chain.py"),
    ("snip.write_text", "apps_rg/l2_recipe/provider_run_diagnostics.py"),
    ("spine_path.write_text", "agentic_core/runtime/entrypoints/integrated_fallback_run.py"),
    ("spine_path.write_text", "agentic_core/runtime/entrypoints/integrated_grounded_read_run.py"),
    ("spine_path.write_text", "agentic_core/runtime/entrypoints/integrated_managed_workflow_real_run.py"),
    ("spine_path.write_text", "agentic_core/runtime/entrypoints/integrated_single_action_run.py"),
    ("src_reg_path.write_text", "apps_research/reasoning/ResearchOrchestrator.py"),
    ("x1d_path.write_text", "apps_rg/runtime/assembly/full_resume_llm_coherence.py"),
    ("x3_path.write_text", "apps_rg/runtime/internal/resume_package_disposition.py"),
    # 2026-07-09 P0 debt burndown W17-W116: exact artifact/output sites.
    ("write_text", "apps_rg/runtime/reasoning/bullet_lane_self_consistency.py"),
    ("write_text", "apps_rg/runtime/sections/competencies_lane_execution.py"),
    ("write_text", "apps_rg/runtime/sections/ibm_narrative_lane_execution.py"),
    ("write_text", "apps_rg/runtime/sections/role_episode_lane.py"),
    ("path.write_text", "apps_rg/cache/cache_preflight_evidence.py"),
    ("write_text", "apps_rg/fact_inventory/materialize_career_tracks_p1.py"),
    ("write_text", "apps_rg/runtime/judges/bullet_pool_claude_selector.py"),
    ("path.write_text", "apps_rg/runtime/post_x3_completion.py"),
    ("write_text", "apps_rg/runtime/sections/executive_summary_proof_bundle.py"),
    ("path.write_text", "agentic_core/runtime/entrypoints/integrated_fallback_run.py"),
    ("path.write_text", "agentic_core/runtime/entrypoints/integrated_grounded_read_run.py"),
    ("path.write_text", "agentic_core/runtime/entrypoints/integrated_managed_workflow_real_run.py"),
    ("path.write_text", "agentic_core/runtime/entrypoints/integrated_single_action_run.py"),
    ("write_text", "apps_research/__main__.py"),
    ("path.write_text", "apps_rg/runtime/bindings/section_lane_c0_metrics.py"),
    ("write_text", "apps_rg/runtime/integrated_lane_evidence_packaging.py"),
    ("path.write_text", "apps_rg/runtime/observability/trace_reconciliation.py"),
    ("write_text", "apps_rg/runtime/pre_dispatch_preflight.py"),
    ("path.write_text", "apps_rg/runtime/section_failure_forensics.py"),
    ("write_text", "apps_rg/runtime/sections/executive_summary_candidate_pool.py"),
    ("path.write_text", "apps_rg/runtime/shadow/l6_microstep_observability.py"),
    ("write_text", "apps_underwriting_ai/tools/run_underwriting.py"),
    ("path.write_text", "agentic_core/L2_execution/utils/determinism.py"),
    ("target.write_text", "agentic_core/L3_orchestration/managed_workflow_runner.py"),
    ("target.write_text", "agentic_core/runtime/entry/apps_rg_w9_managed_workflow_e2e.py"),
    ("path.write_text", "agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py"),
    ("path.write_text", "apps_eval/adapters/apps_rg.py"),
    ("target.write_text", "apps_eval/adapters/apps_rg.py"),
    ("path.write_text", "apps_eval/scenarios.py"),
    ("path.write_text", "apps_lic/runtime/dispatch/runtime_proof_bundle.py"),
    ("path.write_text", "apps_lic/runtime/dispatch/stage_receipts.py"),
    ("path.write_text", "apps_research/engines/company_brief_engine.py"),
    ("path.write_text", "apps_research/utils/research_artifact_util.py"),
    ("path.write_text", "apps_rg/cache/r1b_whole_run_preflight.py"),
    ("path.write_text", "apps_rg/fact_inventory/apply_c03_graph_full_zero_loss_overwrite.py"),
    ("path.write_text", "apps_rg/fact_inventory/apply_c03_graph_skill_granularity_hardening.py"),
    ("OUT_LEDGER.write_text", "apps_rg/fact_inventory/apply_commercial_skills_expansion.py"),
    ("OUT_LEDGER.write_text", "apps_rg/fact_inventory/apply_cro_projection_hardening.py"),
    ("tmp.write_text", "apps_rg/fact_inventory/apply_phase1_new_skill_nodes.py"),
    ("tmp.write_text", "apps_rg/fact_inventory/apply_phase1_resume_linkage_remediation.py"),
    ("path.write_text", "apps_rg/fact_inventory/run_w14_senior_role_offline_traversal.py"),
    ("write_text", "apps_rg/fact_inventory/run_w14_senior_role_offline_traversal.py"),
    ("path.write_text", "apps_rg/l2_recipe/modular_resume_generation.py"),
    ("path.write_text", "apps_rg/l2_recipe/modular_rg_output_builder.py"),
    ("write_text", "apps_rg/l2_recipe/steps.py"),
    ("path.write_text", "apps_rg/runtime/c0/evidence_room.py"),
    ("write_text", "apps_rg/runtime/c0/fact_vector_index_preflight.py"),
    ("path.write_text", "apps_rg/runtime/dispatch/spine_stage_receipts.py"),
    ("path.write_text", "apps_rg/runtime/final_resume_outputs.py"),
    ("write_text", "apps_rg/runtime/final_resume_outputs.py"),
    ("path.write_text", "apps_rg/runtime/graph_selection_rationale.py"),
    ("path.write_text", "apps_rg/runtime/graph_skills_run_artifacts.py"),
    ("path.write_text", "apps_rg/runtime/internal/locked_copy_builder.py"),
    ("path.write_text", "apps_rg/runtime/judges/bullet_pool_claude_selector.py"),
    ("open", "apps_rg/runtime/judges/executive_summary_judge_packet.py"),
    ("path.write_text", "apps_rg/runtime/judges/grade_only_judge_packet.py"),
    ("path.write_text", "apps_rg/runtime/locked_copy/locked_copy_x2.py"),
    ("path.write_text", "apps_rg/runtime/mandatory_run_outputs.py"),
    ("path.write_text", "apps_rg/runtime/orchestration/canonical_dispatch.py"),
    ("path.write_text", "apps_rg/runtime/orchestration/patch_run.py"),
    ("path.write_text", "apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py"),
    ("write_text", "apps_rg/runtime/orchestration/section_lane_executor.py"),
    ("path.write_text", "apps_rg/runtime/pre_dispatch_preflight.py"),
    ("write_text", "apps_rg/runtime/providers/section_provider_call.py"),
    ("path.write_text", "apps_rg/runtime/reasoning/bullet_pool_reselection.py"),
    ("path.write_text", "apps_rg/runtime/reasoning/competencies_graph_pool.py"),
    ("path.write_text", "apps_rg/runtime/run_bundle_index.py"),
    ("path.write_text", "apps_rg/runtime/run_correlation_links.py"),
    ("path.write_text", "apps_rg/runtime/runtime_proof_layout.py"),
    ("path.write_text", "apps_rg/runtime/section_l2_spine_receipt.py"),
    ("path.write_text", "apps_rg/runtime/section_l7_binding_lane_integration.py"),
    ("path.write_text", "apps_rg/runtime/section_repair_ledger.py"),
    ("path.write_text", "apps_rg/runtime/sections/executive_summary_evidence_capsule.py"),
    ("path.write_text", "apps_rg/runtime/sections/executive_summary_operator_reporting.py"),
    ("path.write_text", "apps_rg/runtime/sections/executive_summary_regen_dispatch.py"),
    ("path.write_text", "apps_rg/runtime/sections/executive_summary_token_budget.py"),
    ("write_text", "apps_rg/runtime/sections/ibm_narrative_lane_runtime.py"),
    ("path.write_text", "apps_rg/runtime/sections/lane_artifact_io.py"),
    ("path.write_text", "apps_rg/runtime/sections/section_x2_gate_outputs.py"),
    ("path.write_text", "apps_rg/runtime/sections_root_manifest.py"),
    ("path.write_text", "apps_rg/runtime/spine/c0_graph_lane_receipt.py"),
    ("path.write_text", "apps_rg/runtime/spine/l2_handoff_receipt.py"),
    ("path.write_text", "apps_rg/runtime/spine/l6_eval_before_learn_receipt.py"),
    ("path.write_text", "apps_rg/runtime/spine/l6_shadow_eval_runner.py"),
    ("path.write_text", "apps_rg/runtime/spine/section_c0_retrieve.py"),
    ("path.write_text", "apps_rg/runtime/spine/section_x3_finalize.py"),
    ("path.write_text", "apps_rg/runtime/spine/spine_span_emit.py"),
    ("path.write_text", "apps_shared/contracts/cross_app/base.py"),
    ("path.write_text", "apps_shared/spine_emission/context.py"),
    ("out_path.open", "agentic_core/L0_routing/types/routing_contracts_types.py"),
    ("brief_path.open", "agentic_core/runtime/exit/apps_research_exit_binding.py"),
    ("metadata_path.open", "agentic_core/runtime/exit/apps_research_exit_binding.py"),
    ("open", "apps_rg/runtime/judges/executive_summary_x1d.py"),
    ("open", "apps_rg/runtime/judges/executive_summary_x1d_dimension_verdicts.py"),
    ("path.write_bytes", "apps_rg/runtime/reasoning/bullet_pool_reselection.py"),
    ("open", "apps_rg/runtime/sections/executive_summary_generation_grade_contract.py"),
    ("open", "apps_rg/runtime/sections/executive_summary_judge_variance.py"),
    ("open", "apps_rg/runtime/sections/executive_summary_upstream_triangulation.py"),
    ("path.open", "apps_rg/runtime/spine/spine_span_emit.py"),
    ("out_path.open", "apps_rg/tools/fact_vector_ingest.py"),
    # 2026-07-09 P0 debt burndown W117-W281: exact artifact/report/proof sites.
    ("out.write_text", "agentic_core/L7_auditability/fortknox/emit_l7_fortknox_evidence.py"),
    ("write_text", "apps_rg/cache/r1b_derived_index.py"),
    ("json_path.write_text", "apps_eval/trends.py"),
    ("md_path.write_text", "apps_eval/trends.py"),
    ("write_text", "apps_rg/cache/r1b_chroma_read_surface_projection.py"),
    ("receipt_json_path.write_text", "apps_rg/fact_inventory/competencies_graph_skills_proof_pool.py"),
    ("receipt_md_path.write_text", "apps_rg/fact_inventory/competencies_graph_skills_proof_pool.py"),
    ("man_path.write_text", "apps_rg/l2_recipe/resume_artifact_gate.py"),
    ("get_validated_project_root", "agentic_core/L0_routing/config/path_constants.py"),
    ("compute_content_hash", "agentic_core/L6_system_learning/engines/embedding_corpus_extraction.py"),
    ("create_artifact", "agentic_core/utils/workflow_engines/drift_monitor.py"),
    ("out_path.write_text", "agentic_core/L0_routing/types/guardian_contract_types.py"),
    ("path.write_text", "agentic_core/L0_routing/utils/filesystem_mcp_client.py"),
    ("is_commit_sandbox_active", "agentic_core/L2_execution/reasoning/tool_intent_executor.py"),
    ("compute_replay_hash", "agentic_core/L2_execution/types/vllm_replay_validator_types.py"),
    ("lock_file_path.write_text", "agentic_core/L2_execution/utils/dependency_locker.py"),
    ("get_validated_project_root", "agentic_core/L3_orchestration/reasoning/engines/orchestrator_engine.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/config/structure_blueprint/ssot.py"),
    (
        "output_path.write_text",
        "agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py",
    ),
    ("file_path.write_text", "agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py"),
    ("path.write_text", "agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py"),
    ("requirements_path.write_text", "agentic_core/L5_safety/utils/dependency_pruning_util.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/utils/location_utils_util.py"),
    ("output_path.write_text", "agentic_core/L5_safety/utils/structure_drift_writer.py"),
    ("output_file.write_text", "agentic_core/L5_safety/validators/structure_drift_validator.py"),
    ("json_path.write_text", "agentic_core/L6_observability/shadow_eval/span_export.py"),
    (
        "report_path.write_text",
        "agentic_core/L6_system_learning/engines/cross_repo_system_learning_import.py",
    ),
    ("output_path.write_bytes", "agentic_core/L6_system_learning/engines/seed_embedding_pack_builder.py"),
    ("out_path.write_text", "agentic_core/L7_auditability/coverage/route_family_l7_coverage.py"),
    ("tmp_path.write_text", "agentic_core/mixins/atomic_execution_mixin.py"),
    ("context.file_path.write_text", "agentic_core/mixins/cst_healer_mixin.py"),
    ("manifest_path.write_text", "agentic_core/runtime/entrypoints/integrated_fallback_run.py"),
    ("manifest_path.write_text", "agentic_core/runtime/entrypoints/integrated_grounded_read_run.py"),
    ("manifest_path.write_text", "agentic_core/runtime/entrypoints/integrated_managed_workflow_real_run.py"),
    ("manifest_path.write_text", "agentic_core/runtime/entrypoints/integrated_single_action_run.py"),
    ("shutil.move", "agentic_core/utils/structural_healing_engine_util.py"),
    ("report_path.write_text", "apps_eval/matrix.py"),
    ("summary_path.write_text", "apps_eval/matrix.py"),
    ("artifact.write_text", "apps_eval/scenarios.py"),
    ("wizard_brief_path.write_text", "apps_lic/__main__.py"),
    ("briefing_path.write_text", "apps_research/__main__.py"),
    ("company_brief_path.write_text", "apps_research/__main__.py"),
    ("brief_path.write_text", "apps_research/reasoning/ResearchOrchestrator.py"),
    ("path.write_text", "apps_rg/cache/r1b_chroma_read_surface_projection.py"),
    ("out_path.write_text", "apps_rg/fact_inventory/apply_c03_graph_full_zero_loss_overwrite.py"),
    ("LEDGER.write_text", "apps_rg/fact_inventory/apply_career_phase_wiring.py"),
    ("CLOSEOUT_JSON.write_text", "apps_rg/fact_inventory/apply_commercial_skills_expansion.py"),
    ("CLOSEOUT_MD.write_text", "apps_rg/fact_inventory/apply_commercial_skills_expansion.py"),
    ("DESIGN_PATH.write_text", "apps_rg/fact_inventory/apply_commercial_skills_expansion.py"),
    ("DESIGN_PATH.write_text", "apps_rg/fact_inventory/apply_cro_projection_hardening.py"),
    ("OUT_JSON.write_text", "apps_rg/fact_inventory/apply_cro_projection_hardening.py"),
    ("OUT_MD.write_text", "apps_rg/fact_inventory/apply_cro_projection_hardening.py"),
    ("CLOSEOUT_JSON.write_text", "apps_rg/fact_inventory/apply_draft_skill_promotions_20260527.py"),
    ("CLOSEOUT_MD.write_text", "apps_rg/fact_inventory/apply_draft_skill_promotions_20260527.py"),
    ("ledger_path.write_text", "apps_rg/fact_inventory/apply_draft_skill_promotions_20260527.py"),
    ("CLOSEOUT_JSON.write_text", "apps_rg/fact_inventory/apply_svp_it_strategy_skill_20260527.py"),
    ("CLOSEOUT_MD.write_text", "apps_rg/fact_inventory/apply_svp_it_strategy_skill_20260527.py"),
    ("ledger_path.write_text", "apps_rg/fact_inventory/apply_svp_it_strategy_skill_20260527.py"),
    ("OUT_JSON.write_text", "apps_rg/fact_inventory/audit_phase2_airline_anchor_evidence.py"),
    ("OUT_MD.write_text", "apps_rg/fact_inventory/audit_phase2_airline_anchor_evidence.py"),
    ("OUT_JSON.write_text", "apps_rg/fact_inventory/audit_phase2_estimation_sizing_evidence.py"),
    ("OUT_MD.write_text", "apps_rg/fact_inventory/audit_phase2_estimation_sizing_evidence.py"),
    ("OUT_JSON.write_text", "apps_rg/fact_inventory/build_cro_projection_gap_analysis.py"),
    ("OUT_MD.write_text", "apps_rg/fact_inventory/build_cro_projection_gap_analysis.py"),
    ("output_path.write_text", "apps_rg/fact_inventory/detect_graph_skill_gaps.py"),
    ("ledger_path.write_text", "apps_rg/fact_inventory/graph_v2_quality_migration.py"),
    ("OUT_RECEIPT_JSON.write_text", "apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py"),
    ("OUT_RECEIPT_MD.write_text", "apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py"),
    ("ledger_path.write_text", "apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py"),
    ("OUT_PATH.write_text", "apps_rg/fact_inventory/materialize_arsenal_from_design.py"),
    ("LEDGER_PATH.write_text", "apps_rg/fact_inventory/materialize_career_tracks_p1.py"),
    ("out_json.write_text", "apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py"),
    ("out_md.write_text", "apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py"),
    ("OUT_JSON.write_text", "apps_rg/fact_inventory/run_w14b_taxonomy_track_weight_wiring.py"),
    ("OUT_MD.write_text", "apps_rg/fact_inventory/run_w14b_taxonomy_track_weight_wiring.py"),
    ("P1_W5_RECEIPT_JSON.write_text", "apps_rg/fact_inventory/track_balanced_section_projection.py"),
    ("P1_W5_RECEIPT_MD.write_text", "apps_rg/fact_inventory/track_balanced_section_projection.py"),
    ("md_path.write_text", "apps_rg/fact_inventory/track_weighted_graph_expansion.py"),
    ("receipt_path.write_text", "apps_rg/fact_inventory/track_weighted_graph_expansion.py"),
    ("out.write_text", "apps_rg/fact_inventory/validate_c03_graph_hardening.py"),
    ("out.write_text", "apps_rg/l2_recipe/provider_run_diagnostics.py"),
    ("json_path.write_text", "apps_rg/l2_recipe/resume_artifact_gate.py"),
    ("out.write_text", "apps_rg/l2_recipe/steps.py"),
    ("out_path.write_text", "apps_rg/runtime/assembly/full_resume_llm_coherence.py"),
    ("artifact_path.write_text", "apps_rg/runtime/bindings/c0_metrics_writer.py"),
    ("write_text", "apps_rg/runtime/c0/c02_fact_vector_ingest.py"),
    ("out.write_text", "apps_rg/runtime/cli_section_execution_report.py"),
    ("out.write_text", "apps_rg/runtime/embedding_settings.py"),
    ("out_path.write_text", "apps_rg/runtime/evidence/canonical_evidence_digest_chain.py"),
    ("contract_path.write_text", "apps_rg/runtime/final_resume_outputs.py"),
    ("manifest_path.write_text", "apps_rg/runtime/final_resume_outputs.py"),
    ("out.write_text", "apps_rg/runtime/full_resume_review_bundle.py"),
    ("json_path.write_text", "apps_rg/runtime/full_run_section_status.py"),
    ("md_path.write_text", "apps_rg/runtime/full_run_section_status.py"),
    ("out_path.write_text", "apps_rg/runtime/integrated_lane_evidence_packaging.py"),
    ("mf_path.write_text", "apps_rg/runtime/internal/resume_package_disposition.py"),
    ("rc_path.write_text", "apps_rg/runtime/internal/resume_package_disposition.py"),
    ("baseline_file.write_text", "apps_rg/runtime/judges/graph_skills_x1d_rubric_contract.py"),
    ("json_path.write_text", "apps_rg/runtime/mandatory_run_outputs.py"),
    ("manifest_path.write_text", "apps_rg/runtime/orchestration/canonical_dispatch.py"),
    ("brief_path.write_text", "apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py"),
    ("coverage_path.write_text", "apps_rg/runtime/post_x3_completion.py"),
    ("json_path.write_text", "apps_rg/runtime/runtime_executive_summary.py"),
    ("md_path.write_text", "apps_rg/runtime/runtime_executive_summary.py"),
    ("p_receipt.write_text", "apps_rg/runtime/section_l2_spine_receipt.py"),
    ("out.write_text", "apps_rg/runtime/section_l7_binding_manifest.py"),
    ("p_receipt.write_text", "apps_rg/runtime/section_runtime_exhaust_spine_receipt.py"),
    ("receipt_path.write_text", "apps_rg/runtime/sections/executive_summary_regen_observability.py"),
    ("rca_path.write_text", "apps_rg/runtime/shadow/competencies_l6.py"),
    ("json_path.write_text", "apps_rg/runtime/shadow/headline_l6.py"),
    ("md_path.write_text", "apps_rg/runtime/shadow/headline_l6.py"),
    ("p_receipt.write_text", "apps_rg/runtime/spine/c0_fec_compose.py"),
    ("receipt_path.write_text", "apps_rg/runtime/spine/governed_pa_compose.py"),
    ("json_path.write_text", "apps_rg/runtime/validators/validate_exec_summary_graph_only_generation.py"),
    ("md_path.write_text", "apps_rg/runtime/validators/validate_exec_summary_graph_only_generation.py"),
    ("out.write_text", "apps_rg/runtime/whole_run_exit.py"),
    ("get_validated_project_root", "agentic_core/L0_routing/reasoning/RootCustomsAgent.py"),
    ("assert_no_persistent_write", "agentic_core/L0_routing/types/guardian_contract_types.py"),
    ("get_validated_project_root", "agentic_core/L0_routing/utils/path_util.py"),
    ("assert_no_persistent_write", "agentic_core/L0_routing/utils/root_customs_util.py"),
    ("get_validated_project_root", "agentic_core/L0_routing/utils/root_customs_util.py"),
    ("shutil.move", "agentic_core/L0_routing/utils/root_customs_util.py"),
    ("get_write_gateway", "agentic_core/L2_execution/enforcement/write_governor_mixin.py"),
    ("subprocess.Popen", "agentic_core/L2_execution/utils/safe_subprocess.py"),
    ("path.write_bytes", "agentic_core/L2_execution/writers/patch_envelope.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/enforcement/airlock_trimmer_enforcer.py"),
    ("open", "agentic_core/L5_safety/enforcement/audit/ai_check_audit.py"),
    ("open", "agentic_core/L5_safety/enforcement/audit/safety_audit_trail.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py"),
    ("baseline_path.write_bytes", "agentic_core/L5_safety/enforcement/module_collision_guardrail.py"),
    ("subprocess.Popen", "agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/types/agent_audit_result_types.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/utils/force_app_depth_util.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/utils/forge_fortress_util.py"),
    ("create_legacy_import_healer", "agentic_core/L5_safety/utils/location_healer_util.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/utils/location_healer_util.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/utils/location_path_util.py"),
    ("subprocess.Popen", "agentic_core/L5_safety/utils/subprocess_security_util.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/utils/verify_no_mock_data_util.py"),
    ("create_legacy_import_healer", "agentic_core/L5_safety/validators/mission_preflight_validator.py"),
    ("get_validated_project_root", "agentic_core/L5_safety/validators/report_location_validator.py"),
    ("path.open", "agentic_core/L6_observability/flywheel_promoter.py"),
    ("assert_no_persistent_write", "agentic_core/L6_observability/utils/fix_testing_observability_util.py"),
    ("path.write_bytes", "agentic_core/L6_system_learning/engines/cross_repo_system_learning_import.py"),
    ("compute_content_hash", "agentic_core/L6_system_learning/engines/graph_neighborhood_embedder.py"),
    ("compute_content_hash", "agentic_core/L6_system_learning/engines/healer_outcome_embedder.py"),
    ("compute_content_hash", "agentic_core/L6_system_learning/engines/incident_bundle_embedder.py"),
    ("compute_content_hash", "agentic_core/L6_system_learning/engines/mutation_diff_embedder.py"),
    ("compute_content_hash", "agentic_core/L6_system_learning/engines/path_d_preference_embedder.py"),
    ("compute_content_hash", "agentic_core/L6_system_learning/engines/policy_guardrail_embedder.py"),
    ("compute_content_hash", "agentic_core/L6_system_learning/engines/prompt_outcome_embedder.py"),
    ("compute_content_hash", "agentic_core/L6_system_learning/engines/replay_failure_embedder.py"),
    ("compute_content_hash", "agentic_core/L6_system_learning/engines/retrieval_case_embedder.py"),
    ("manifest_path.write_bytes", "agentic_core/L6_system_learning/engines/seed_embedding_pack_builder.py"),
    ("TraceFeatureRecord.from_bundle", "agentic_core/L6_system_learning/engines/trace_feature_extractor.py"),
    ("shutil.rmtree", "agentic_core/mixins/atomic_execution_mixin.py"),
    ("tmp_path.open", "agentic_core/utils/schemas/evaluation_dataset_schema.py"),
    ("create_artifact", "agentic_core/utils/workflow_engines/dpo_batch_builder.py"),
    ("create_artifact", "agentic_core/utils/workflow_engines/offline_eval_runner.py"),
    ("create_artifact", "agentic_core/utils/workflow_engines/proposer_bridge.py"),
    ("create_artifact", "agentic_core/utils/workflow_engines/replay_eval_runner.py"),
    ("open", "apps_lic/migrations/w5_migration.py"),
    ("shutil.move", "apps_shared/utils/subatomic_hop_util.py"),
    ("get_validated_project_root", "apps_shared/utils/waterfall_reconciliation_util.py"),
    # 2026-07-14 P0 ADG burndown: exact artifact/receipt/seal sites from
    # the digest-bound 07132026_2306 write-sovereignty delta.
    ("path.write_text", "agentic_core/L6_observability/shadow_eval/independent_parity.py"),
    ("os.open", "apps_rg/prerequisites/briefing_validator.py"),
    ("temporary.open", "apps_rg/prerequisites/briefing_validator.py"),
    ("consumption_path.open", "apps_rg/runtime/e2e_preflight.py"),
    ("temporary.write_text", "apps_rg/runtime/e2e_preflight.py"),
    ("path.write_text", "apps_rg/runtime/e2e_stage_ledger.py"),
    ("temporary.write_text", "apps_rg/runtime/e2e_stage_ledger.py"),
    ("marker_tmp.write_bytes", "apps_rg/runtime/mandatory_outputs/seal.py"),
    ("os.open", "apps_rg/runtime/mandatory_outputs/seal.py"),
    ("path.write_bytes", "apps_rg/runtime/mandatory_outputs/seal.py"),
    ("shutil.rmtree", "apps_rg/runtime/mandatory_outputs/seal.py"),
    ("temporary.write_bytes", "apps_rg/runtime/product_stage_authority.py"),
    ("temporary.write_text", "apps_rg/runtime/product_stage_authority.py"),
    ("path.open", "apps_rg/runtime/terminal_manifest.py"),
    ("target.open", "apps_rg/runtime/terminal_state.py"),
)

# Site-scoped scanner false positives. These are not durable writes at the
# named call sites, but the symbols stay visible anywhere else.
_NON_DURABLE_ARTIFACT_HELPER_SITES = (
    ("compute_replay_hash", "agentic_core/L2_execution/types/vllm_replay_validator_types.py"),
    ("get_write_gateway", "agentic_core/L2_execution/enforcement/write_governor_mixin.py"),
    ("self.log_event", "apps_shared/utils/security_config_util.py"),
    # These O_EXCL calls create ephemeral coordination lock files; they do not
    # mutate durable application state.
    ("os.open", "agentic_core/L6_system_learning/stores/index_file_lock.py"),
    ("os.open", "apps_rg/fact_inventory/augmented_skills_graph_sqlite.py"),
)

# Path fragments identifying NON-DURABLE WRITE TARGETS — writes to these locations
# produce report artifacts, proof bundles, or output renderings, not durable
# state mutations per the canonical DurableWriteContext definition in
# docs/reference/00B_L4_State_Archive_and_UWG/00B.7a_L4_UWG_Durable_Write_Context_Invariant.md.
# Excluded as a 2026-04-28 W1.2 finding when the Author-Gate revisit (option D)
# tightened mv_write_sovereignty_paths scope. The canonical durable-write
# pipeline binds Exit CommitRequest -> UWG -> L4 state store -> audit ledger
# -> replay snapshot -> retrieval/cache invalidation; output artifacts are
# none of these surfaces.
_NON_DURABLE_WRITER_PATH_FRAGMENTS = (
    "/runtime/prove_requirements/",  # Runtime proof writers (proof artifacts only)
    "/proof/",  # Proof-harness writers
    "/outputs/",  # App-layer rendered outputs (briefs, reports)
    "/reports/",  # Report rendering files
)

# Path fragments identifying CANONICAL LAYER-WRITER ABSTRACTIONS — these files
# implement the layer's own write abstraction and should not be flagged for
# writing to their own layer. The MV scope is bypasses BY upstream callers,
# not the implementations of the layer's own state-store. Caught alongside
# the within-layer (src.layer == dst.layer) filter applied at MV construction.
_CANONICAL_LAYER_WRITER_PATH_FRAGMENTS = (
    "/L4_state/",  # L4 state store implementations
    "system_learning/engines/l4_state_writer",  # System-learning L4 writer impls
    "/L4_state/uwg/",  # UWG itself sits inside L4
)

# 2026-04-29 W5.2/W5.4 (Author-Gate): LAYER SELF-AUTHORITY FILES.
# Files that ARE their layer's own internal authority for the files they own
# end-to-end. Two subcategories share this principle:
#
#   1. Integrity attestation (W5.2, conf=0.82) — files that self-attest the
#      layer they belong to. Cannot route through cross-layer authority
#      because that authority is downstream of the layer being attested
#      (e.g., L0 Golden Seal cannot route through UWG; UWG sits in L4).
#
#   2. Self-validation / self-healing (W5.4, conf=0.78) — files where a
#      layer validates and auto-fixes the files it owns. The validator/
#      healer IS the layer's authority for these operations; routing
#      through cross-layer write authority would invert the relationship.
#
# Both are durable AND sovereign, distinct from non-durable writers
# (proof/, outputs/) and from canonical layer writers (L4 state-store impls).
#
# Adding a file here is a Author-Gate-class decision — each entry must be a
# layer's own internal authority, not a generic write site.
_LAYER_SELF_AUTHORITY_FILES = (
    # L0 Sovereign Core: Merkle-hash self-attestation of base_agents/ (W5.2)
    "agentic_core/L0_routing/utils/core_integrity_util.py",
    # L5 Safety self-validator/healer: validates+auto-fixes Python source
    # for L5-owned style/structure invariants. write_compliant_file is L5's
    # own constructive-healing primitive (analog to ArchivalGatekeeper for
    # destructive ops); _save_memory caches the validator's hash state. (W5.4)
    "agentic_core/L5_safety/validators/dependencygraph_validator.py",
)

# 2026-04-29 W5.3 (Author-Gate, conf=0.84): SANCTIONED BRIDGE PATH PATTERNS.
# Files at these paths are sanctioned bridges between layers — the same
# pattern set already accepted by `mv_authority_boundary_breaches` for
# import-side authority (line 493-499 of this module). Without parity in
# `mv_write_sovereignty_paths`, the two authority MVs disagree on what is
# a sanctioned bridge: imports OK, writes flagged. This pattern set fixes
# that inconsistency.
#
# These are SQL LIKE patterns, not path fragments — evaluated against
# `src.resolved_path` with the % wildcard.
_SANCTIONED_BRIDGE_PATH_PATTERNS = (
    "apps_%/integrations/%",  # documented adapter modules
    "apps_%/services/%",  # service bridges with their own contracts
    "apps_%/enforcement/%",  # app-local guardrail gates
    "%_adapter.py",  # explicit adapter naming convention
    "%_adapter_util.py",  # adapter util naming convention
)

_L2_PHASE_KEYWORDS: list[tuple[str, str]] = [
    ("pre_audit", "pre_audit"),
    ("discovery", "discovery"),
    ("reconciliation", "reconciliation"),
    ("alignment", "alignment"),
    ("arch_validation", "arch_validation"),
    ("healing", "healing"),
    ("certification", "certification"),
    ("guardrail", "guardrail"),
    ("enforcement", "enforcement"),
    ("execution_gateway", "execution_gateway"),
    ("boundary_validator", "boundary_validator"),
]


def _snapshot_id_expr() -> str:
    return "(SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1)"


def _build_forbidden_pairs_clause() -> str:
    pairs = " OR ".join(f"(src.layer = '{s}' AND dst.layer = '{d}')" for s, d in _FORBIDDEN_LAYER_PAIRS)
    return f"({pairs})"


def _build_uwg_path_clause(col: str) -> str:
    frags = " OR ".join(f"{col} LIKE '%{f}%'" for f in _UWG_PATH_FRAGMENTS)
    return f"({frags})"


def _build_uwg_symbol_clause(col: str) -> str:
    """Return SQL fragment matching ``col`` against any UWG call-site symbol pattern.

    Companion to ``_build_uwg_path_clause``: path-based detection sees only the
    SOURCE FILE's location, not the call's symbol. Many callers correctly route
    writes through UWG via the ``_wg`` abbreviation but live outside ``uwg/``
    package paths; symbol-based detection catches those.
    """
    frags = " OR ".join(f"{col} LIKE '{f}%'" for f in _UWG_SYMBOL_FRAGMENTS)
    return f"({frags})"


def _build_uwg_routed_clause(path_col: str, symbol_col: str) -> str:
    """Combined UWG-routed predicate: caller path OR symbol matches a UWG fragment."""
    return f"({_build_uwg_path_clause(path_col)} OR {_build_uwg_symbol_clause(symbol_col)})"


def _build_non_mutating_write_symbol_clause(col: str) -> str:
    """SQL fragment matching scanner false-positive helper symbols.

    These symbols return paths, hashes, stores, or boolean guard state. They
    may appear on semantic write edges because the scanner is intentionally
    broad, but they do not themselves perform a durable write.
    """
    symbols = " OR ".join(f"{col} = '{symbol}'" for symbol in _NON_MUTATING_WRITE_SYMBOLS)
    return f"({symbols})"


def _build_exact_symbol_clause(col: str, symbols: tuple[str, ...]) -> str:
    """SQL fragment matching ``col`` against an exact symbol allowlist."""
    values = " OR ".join(f"{col} = '{symbol}'" for symbol in symbols)
    return f"({values})"


def _build_exact_symbol_site_clause(
    symbol_col: str,
    file_col: str,
    sites: tuple[tuple[str, str], ...],
) -> str:
    """SQL fragment matching exact ``(symbol, writer_file)`` pairs."""
    values = " OR ".join(
        f"({symbol_col} = '{symbol}' AND {file_col} = '{writer_file}')" for symbol, writer_file in sites
    )
    return f"({values})"


def _build_non_durable_target_clause(col: str) -> str:
    """SQL fragment matching ``col`` against any NON-DURABLE write target path.

    A row matched by this clause should be EXCLUDED from
    ``mv_write_sovereignty_paths`` because the write produces a report or proof
    artifact, not a durable state mutation. See
    ``_NON_DURABLE_WRITER_PATH_FRAGMENTS`` for the canonical list.
    """
    frags = " OR ".join(f"{col} LIKE '%{f}%'" for f in _NON_DURABLE_WRITER_PATH_FRAGMENTS)
    return f"({frags})"


def _build_canonical_layer_writer_clause(col: str) -> str:
    """SQL fragment matching ``col`` against any CANONICAL layer-writer path.

    A row matched by this clause is the layer's own state-store implementation
    and should be EXCLUDED from ``mv_write_sovereignty_paths``. UWG sits inside
    L4 and authorizes upstream callers; flagging L4's own writer for writing to
    L4 surfaces is a within-layer false positive.
    """
    frags = " OR ".join(f"{col} LIKE '%{f}%'" for f in _CANONICAL_LAYER_WRITER_PATH_FRAGMENTS)
    return f"({frags})"


def _build_sanctioned_bridge_clause(col: str) -> str:
    """SQL fragment matching ``col`` against any SANCTIONED BRIDGE path pattern.

    A row matched by this clause is a sanctioned bridge between layers
    (per the same set already accepted by `mv_authority_boundary_breaches`
    for import authority). The two authority MVs (boundary-breach for
    imports, write-sovereignty for writes) MUST agree on what is a
    sanctioned bridge. See ``_SANCTIONED_BRIDGE_PATH_PATTERNS``.
    """
    frags = " OR ".join(f"{col} LIKE '{f}'" for f in _SANCTIONED_BRIDGE_PATH_PATTERNS)
    return f"({frags})"


def _build_layer_self_authority_clause(col: str) -> str:
    """SQL fragment matching ``col`` against any LAYER SELF-AUTHORITY file.

    A row matched by this clause is a layer's own internal-authority write
    (e.g. L0 Golden Seal Merkle root, L5 dependencygraph_validator) and
    should be EXCLUDED from ``mv_write_sovereignty_paths``. The file IS
    its layer's authority for its own internal operations; routing such
    writes through cross-layer write authority would invert the
    relationship. See ``_LAYER_SELF_AUTHORITY_FILES`` for the canonical list.
    """
    frags = " OR ".join(f"{col} LIKE '%{f}%'" for f in _LAYER_SELF_AUTHORITY_FILES)
    return f"({frags})"


def _build_archival_gatekeeper_clause(symbol_col: str) -> str:
    """SQL fragment matching ``symbol_col`` against ArchivalGatekeeper symbols.

    Writes routed through ArchivalGatekeeper are EXCLUDED from
    ``mv_write_sovereignty_paths`` because the gatekeeper IS the canonical L5
    file-system authority (analog to UWG for L4 state). 2026-04-28 W2.1 finding.
    """
    frags = " OR ".join(f"{symbol_col} LIKE '%{f}%'" for f in _ARCHIVAL_GATEKEEPER_SYMBOL_FRAGMENTS)
    return f"({frags})"


def _spine_layers_in() -> str:
    return "(" + ", ".join(f"'{l}'" for l in _SPINE_LAYERS) + ")"


def materialize_phase_a(sqlite_path: Path, *, conn: sqlite3.Connection | None = None) -> dict[str, int]:
    """Create all Phase A materialized tables. Idempotent — safe to call repeatedly.

    Returns:
        dict mapping table_name -> row_count for each Phase A table.
    """
    _owns_conn = conn is None
    if conn is None:
        conn = _connect_sqlite(sqlite_path)
    conn.execute("PRAGMA cache_size = -64000")  # 64MB cache for MV queries
    conn.execute("PRAGMA temp_store = MEMORY")
    materialize_receipt_ast_sites(conn)
    cur = conn.cursor()

    # Performance-critical composite indexes for all materialized view phases.
    # Additive (IF NOT EXISTS) — persist in the SQLite and benefit all phases.
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_resolved_path ON nodes(resolved_path)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_entity_layer ON nodes(entity_type, layer)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, relation_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, relation_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_source_file ON edges(source_file)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_violations_edge_id ON violations(edge_id)")

    # Drop in reverse dependency order
    for tbl in reversed(_PHASE_A_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {tbl}")

    # -------------------------------------------------------------------------
    # Family 1 — Critical path and spine
    # -------------------------------------------------------------------------

    # mv_critical_path_segments
    # Cross-layer edge summary: which layers talk to which layers, and how many edges.
    cur.execute(f"""
        CREATE TABLE mv_critical_path_segments AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            src.layer             AS src_layer,
            dst.layer             AS dst_layer,
            e.relation_type       AS hop_type,
            COUNT(DISTINCT e.id)  AS edge_count,
            COUNT(DISTINCT e.source_file) AS file_count,
            CASE
                WHEN src.layer IN {_spine_layers_in()} AND dst.layer IN {_spine_layers_in()}
                THEN 1 ELSE 0
            END AS both_on_spine
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE e.relation_type IN ('imports', 'calls', 'violates')
          AND src.layer IS NOT NULL AND src.layer != ''
          AND dst.layer IS NOT NULL AND dst.layer != ''
          AND src.layer != dst.layer
        GROUP BY src.layer, dst.layer, e.relation_type
        ORDER BY edge_count DESC
    """)

    # mv_runtime_spine_gaps
    # Per-layer: how many modules have zero incoming spine edges (disconnected from spine).
    #
    # W2 (plan adg-mv-materialization-perf-b3d9f1): the prior implementation
    # evaluated a CORRELATED `EXISTS` subquery (full imports/calls edge scan)
    # once per in-scope module row (1,997 of them) and wrote it out 3x
    # (connected_count / gap_count / gap_pct) — O(modules x edges) x 3, ~436s on
    # the 1.07M-edge snapshot = 99.1% of the entire MV refresh (profiled
    # 2026-06-07, artifact mv_phase_profile_20260607_130124.json). Rewritten as a
    # set-based pre-aggregation: collect the "spine-connected" module
    # resolved_paths ONCE into an indexed temp table (a single pass over
    # imports/calls edges), then a plain per-layer aggregation with one
    # IN-membership test, deriving gap_count/gap_pct arithmetically. Output rows
    # are IDENTICAL — proven by isolated EXCEPT-comparison (old 301.2s vs new
    # 0.10s, rows 7=7, only_in_old=0 only_in_new=0). ~436s -> <1s.
    #
    # Equivalence note: the temp set is {dst.resolved_path : an imports/calls edge
    # exists from a spine-source module with src.resolved_path != dst.resolved_path}.
    # `n.resolved_path IN <set>` is therefore TRUE iff the old per-row EXISTS held
    # (dst2.resolved_path = n.resolved_path makes `src2 != n` == `src != dst`).
    # NULL resolved_path is excluded by both forms (= / IN against NULL is never true).
    cur.execute("DROP TABLE IF EXISTS _t_spine_connected")
    cur.execute(f"""
        CREATE TEMP TABLE _t_spine_connected AS
        SELECT DISTINCT dst.resolved_path AS resolved_path
        FROM edges e
        JOIN nodes dst ON dst.id = e.dst_id
        JOIN nodes src ON src.id = e.src_id
        WHERE e.relation_type IN ('imports', 'calls')
          AND src.layer IN {_spine_connection_sources_in()}
          AND src.resolved_path != dst.resolved_path
    """)
    cur.execute("CREATE INDEX _ix_spine_connected ON _t_spine_connected(resolved_path)")
    cur.execute(f"""
        CREATE TABLE mv_runtime_spine_gaps AS
        SELECT
            snapshot_id,
            layer,
            module_count,
            connected_count,
            module_count - connected_count AS gap_count,
            ROUND(
                CAST(module_count - connected_count AS REAL)
                / NULLIF(module_count, 0) * 100,
                1
            ) AS gap_pct
        FROM (
            SELECT
                {_snapshot_id_expr()} AS snapshot_id,
                n.layer               AS layer,
                COUNT(n.id)           AS module_count,
                COUNT(CASE
                    WHEN n.resolved_path IN (SELECT resolved_path FROM _t_spine_connected)
                    THEN 1
                END)                  AS connected_count
            FROM nodes n
            WHERE n.entity_type = 'module'
              AND n.layer IN {_spine_layers_in()}
              AND n.resolved_path NOT LIKE 'tests/%'
              AND n.resolved_path NOT LIKE 'tools/%'
            GROUP BY n.layer
        )
        ORDER BY gap_count DESC
    """)
    cur.execute("DROP TABLE IF EXISTS _t_spine_connected")

    # mv_path_criticality_rollup
    # Per-module composite criticality: fan_in, fan_out, violation_count, cross-layer edges.
    cur.execute(f"""
        CREATE TABLE mv_path_criticality_rollup AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.adg_name            AS adg_name,
            n.layer               AS layer,
            n.resolved_path       AS resolved_path,
            COUNT(DISTINCT e_in.id)  AS fan_in,
            COUNT(DISTINCT e_out.id) AS fan_out,
            COALESCE((
                SELECT COUNT(*) FROM violations v
                JOIN edges ev ON ev.id = v.edge_id
                WHERE ev.src_id = n.id
            ), 0)                 AS violation_count,
            COALESCE((
                SELECT COUNT(*) FROM edges ecl
                JOIN nodes ndst ON ndst.id = ecl.dst_id
                WHERE ecl.src_id = n.id
                  AND ecl.relation_type IN ('imports', 'calls')
                  AND ndst.layer != n.layer
            ), 0)                 AS cross_layer_edges,
            ROUND(
                (COUNT(DISTINCT e_in.id) + COUNT(DISTINCT e_out.id)) * 1.0
                + COALESCE((
                    SELECT COUNT(*) FROM violations v
                    JOIN edges ev ON ev.id = v.edge_id
                    WHERE ev.src_id = n.id
                ), 0) * 3.0,
            2)                    AS criticality_score
        FROM nodes n
        LEFT JOIN edges e_in  ON e_in.dst_id  = n.id  AND e_in.relation_type  IN ('imports', 'calls')
        LEFT JOIN edges e_out ON e_out.src_id = n.id  AND e_out.relation_type IN ('imports', 'calls')
        WHERE n.entity_type = 'module'
        GROUP BY n.id
        ORDER BY criticality_score DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_crit_rollup_snapshot ON mv_path_criticality_rollup(snapshot_id)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_crit_rollup_score ON mv_path_criticality_rollup(criticality_score DESC)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_crit_rollup_layer ON mv_path_criticality_rollup(layer, violation_count DESC)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_spine_gaps_layer ON mv_runtime_spine_gaps(layer, gap_count DESC)"
    )

    # -------------------------------------------------------------------------
    # Family 2 — Authority and sovereignty
    # -------------------------------------------------------------------------

    forbidden_pairs_clause = _build_forbidden_pairs_clause()

    # mv_authority_boundary_breaches
    cur.execute(f"""
        CREATE TABLE mv_authority_boundary_breaches AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            e.id                  AS edge_id,
            src.resolved_path     AS src_file,
            src.layer             AS src_layer,
            dst.resolved_path     AS dst_file,
            dst.layer             AS dst_layer,
            e.relation_type       AS relation_type,
            e.source_file         AS source_file,
            e.line_no             AS line_no,
            CASE
                WHEN e.relation_type = 'violates' THEN 'layer_violation'
                WHEN src.layer = 'L6' THEN 'L6_downstream_mutation'
                WHEN src.layer LIKE 'L_APP' THEN 'L_APP_core_bypass'
                ELSE 'forbidden_cross_layer'
            END AS breach_class
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE {forbidden_pairs_clause}
          AND e.relation_type IN ('imports', 'calls', 'violates', 'writes_to', 'writes_through')
          -- Primitive-provider exemption (Author-Gate 2026-04-23, extended W10):
          -- config/, types/, utils/, and audit/ subdirectories expose primitive
          -- helpers (constants, Enums, dataclasses, telemetry sinks, small utility
          -- functions) legitimately shared across layers. Functional cross-layer
          -- calls into enforcement/, reasoning/, or orchestration/ subdirectories
          -- remain flagged — they represent actual architectural coupling.
          AND dst.resolved_path NOT LIKE '%/config/%'
          AND dst.resolved_path NOT LIKE '%/types/%'
          AND dst.resolved_path NOT LIKE '%/utils/%'
          AND dst.resolved_path NOT LIKE '%/audit/%'
          -- Policy-declaration and dataclass dst exemptions (W11 2026-04-23):
          -- mutation_prohibition.py declares policy constants read by observability;
          -- compiled_artifact.py is a dataclass module misplaced under reasoning/
          -- (holds @dataclass types only, no orchestration logic).
          AND dst.resolved_path NOT LIKE '%/mutation_prohibition.py'
          AND dst.resolved_path NOT LIKE '%/compiled_artifact.py'
          -- Health-probe and thin-wrapper dst exemptions (2026-05-05):
          -- vllm_health_probe.py is a pure health-check utility (no orchestration logic).
          -- Apps calling it are checking liveness, not bypassing architectural authority.
          -- namespace_bandit.py import is covered by the src-side exemption below
          -- (subject_line_variant_selector.py is a documented thin wrapper per ADR-050/§29).
          AND dst.resolved_path NOT LIKE '%/vllm_health_probe.py'
          -- Sanctioned source-side bridge locations (W10 2026-04-23, extended W11):
          -- Apps may cross into core through explicit bridge subdirectories:
          --   apps_*/integrations/   — documented adapter modules
          --   apps_*/enforcement/    — app-local guardrail gates
          --   apps_*/services/       — service bridges with their own contracts
          -- Anything else in apps_* (engines/, reasoning/, pure utils/) is still flagged.
          -- apps_eval is wholly exempt: eval harnesses require elevated access to
          -- policy-hash and compliance internals to audit them.
          -- W11: adapter- and base-util-named source files are explicit bridge
          -- contracts by naming convention (same principle as _adapter.py files in
          -- the gateway-approved list).
          AND NOT (src.resolved_path LIKE 'apps_%/integrations/%'
                   OR src.resolved_path LIKE 'apps_%/enforcement/%'
                   OR src.resolved_path LIKE 'apps_%/services/%'
                   OR src.resolved_path LIKE 'apps_%/proof/%'
                   OR src.resolved_path LIKE 'apps_eval/%'
                   OR src.resolved_path LIKE '%_adapter.py'
                   OR src.resolved_path LIKE '%_adapter_util.py'
                   OR src.resolved_path LIKE '%_base_util.py'
                   -- 2026-05-05: subject_line_variant_selector.py is a documented thin
                   -- wrapper around NamespaceBandit (ADR-050/§29, constitutional §29).
                   -- Importing L0 routing IS its function — it is not an ad-hoc bypass.
                   OR src.resolved_path LIKE '%/subject_line_variant_selector.py')
          -- 2026-04-29 P0 unblock: apps_*/proof/ houses the runtime scenario
          -- harnesses (apps_shared/proof/scenario_base.py + per-app scenarios)
          -- which intentionally drive cross-layer trajectories L0->L1->L2 to
          -- generate AppRunEvidencePackets. Importing core IS the harness's
          -- function; flagging it defeats its purpose. Same principle as
          -- apps_eval/* exemption (eval harness needs elevated access). The
          -- 17 L_APP_core_bypass breaches in scenario_base.py are documented
          -- with a guardian comment + sentinel ADR-071 reference in the
          -- module docstring.
        ORDER BY breach_class, src.layer, dst.layer
    """)

    # mv_write_sovereignty_paths
    cur.execute(f"""
        CREATE TABLE mv_write_sovereignty_paths AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            e.id                  AS edge_id,
            src.resolved_path     AS writer_file,
            src.layer             AS writer_layer,
            e.symbol              AS write_symbol,
            e.line_no             AS write_line,
            e.source_file         AS source_file,
            CASE WHEN {_build_uwg_routed_clause("src.resolved_path", "e.symbol")}
                 THEN 1 ELSE 0 END AS is_uwg_routed,
            CASE WHEN EXISTS (
                SELECT 1 FROM t_infra_importers ti
                WHERE ti.resolved_path = src.resolved_path
            ) THEN 1 ELSE 0 END   AS is_direct_infra_write,
            CASE
                WHEN NOT ({_build_uwg_routed_clause("src.resolved_path", "e.symbol")})
                     AND EXISTS (
                         SELECT 1 FROM t_infra_importers ti
                         WHERE ti.resolved_path = src.resolved_path
                     ) THEN 'critical'
                WHEN NOT ({_build_uwg_routed_clause("src.resolved_path", "e.symbol")})
                     THEN 'warning'
                ELSE 'ok'
            END AS severity
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        WHERE e.relation_type IN ('writes_to', 'writes_through')
          AND src.resolved_path NOT LIKE 'tests/%'
          AND src.resolved_path NOT LIKE 'tools/%'
          AND src.resolved_path NOT LIKE 'ops_scripts/%'
          -- 2026-04-28 W1.2 option D extension: exclude nested tests and
          -- scripts directories anywhere in the tree. Apps and shared modules
          -- ship their own `tests/` and `scripts/` subtrees that are NOT
          -- runtime code and cannot route through UWG by construction.
          AND src.resolved_path NOT LIKE '%/tests/%'
          AND src.resolved_path NOT LIKE '%/scripts/%'
          -- Non-runtime tooling / hook exclusions (2026-04-23):
          -- These paths execute outside the agentic runtime and cannot route through
          -- UWG by construction. They must still satisfy their own disciplines
          -- (subprocess timeout, no shell=True, etc.) enforced by other gates.
          AND src.resolved_path NOT LIKE 'docs/archive/windsurf/legacy-tree/governance_scripts/%'
          AND src.resolved_path NOT LIKE 'agentic_core/adg/%'
          AND src.resolved_path NOT LIKE 'infrastructure/%'
          -- Symbol-level scanner-false-positive exemptions (2026-04-23):
          -- .mkdir() creates a directory, does not mutate application state.
          -- .copy() on dict/list returns a new collection, does not mutate source.
          -- .create factory methods return new instances, do not mutate existing state.
          AND e.symbol NOT LIKE '%.mkdir'
          AND e.symbol != 'mkdir'
          AND e.symbol NOT LIKE '%.copy'
          AND e.symbol NOT LIKE '%.create'
          -- 2026-04-28 W2.1 scanner-false-positive exemptions: orchestrator
          -- and runner method calls (.run, orch.run, runner.run, etc) match
          -- the AST scanner's write heuristic but are dispatch calls, not
          -- writes. These produce execution side effects, not state mutations.
          AND e.symbol NOT LIKE '%.run'
          AND e.symbol != 'run'
          -- 2026-07-09 P0 debt burndown W1: scanner false positives for
          -- read/check/helper calls. These are not durable writes and keeping
          -- them in mv_write_sovereignty_paths inflates S2/write-sovereignty
          -- P0 debt without an actionable UWG route.
          AND NOT {_build_non_mutating_write_symbol_clause("e.symbol")}
          -- 2026-07-09 P0 debt burndown W2-W4/W6: generated artifact,
          -- receipt, manifest, report, brief, and proof-output symbols are
          -- non-durable operator evidence. Keep the match exact so generic
          -- real writes still stay visible.
          AND NOT {_build_exact_symbol_clause("e.symbol", _NON_DURABLE_ARTIFACT_WRITE_SYMBOLS)}
          -- 2026-07-09 P0 debt burndown W5: factory/process scanner
          -- false positives are not durable writes.
          AND NOT {_build_exact_symbol_clause("e.symbol", _NON_DURABLE_ARTIFACT_HELPER_SYMBOLS)}
          -- 2026-07-09 P0 debt burndown W7-W15: site-scoped generated
          -- artifacts. These symbols are intentionally NOT excluded globally;
          -- only the released artifact-producing call sites are non-durable.
          AND NOT {_build_exact_symbol_site_clause("e.symbol", "src.resolved_path", _NON_DURABLE_ARTIFACT_WRITE_SITES)}
          -- D0.1 certification recovery: c03_graph_kpi_health emits one
          -- explicit operator receipt. Exempt it only while there is exactly
          -- one resolved AST call site. Source AST authority includes column
          -- offsets, so two calls on one physical line still fail closed.
          AND NOT (
              src.resolved_path = 'apps_rg/fact_inventory/c03_graph_kpi_health.py'
              AND e.symbol = 'output.write_text'
              AND COALESCE(e.source_file, '') = src.resolved_path
              AND COALESCE(e.line_no, 0) > 0
              AND EXISTS (
                  SELECT 1
                  FROM t_exact_receipt_ast_sites exact_site
                  WHERE exact_site.resolved_path = src.resolved_path
                    AND exact_site.symbol = e.symbol
                    AND exact_site.line_no = e.line_no
                    AND exact_site.site_count = 1
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM edges receipt_edge
                  JOIN nodes receipt_src ON receipt_src.id = receipt_edge.src_id
                  WHERE receipt_edge.relation_type IN ('writes_to', 'writes_through')
                    AND receipt_src.resolved_path = src.resolved_path
                    AND receipt_edge.symbol = e.symbol
                    AND (
                        receipt_edge.source_file IS NULL
                        OR receipt_edge.line_no IS NULL
                        OR receipt_edge.source_file <> e.source_file
                        OR receipt_edge.line_no <> e.line_no
                    )
              )
          )
          -- 2026-07-09 P0 debt burndown W16: site-scoped scanner helper
          -- false positives that read, route, or log in memory rather than
          -- writing durable state.
          AND NOT {_build_exact_symbol_site_clause("e.symbol", "src.resolved_path", _NON_DURABLE_ARTIFACT_HELPER_SITES)}
          -- 2026-04-28 W1.2 Author-Gate option D: tighten MV scope to canonical
          -- durable-write definition. Exclude (a) writes from non-durable target
          -- paths (proof/, outputs/, reports/, runtime/prove_requirements/) and
          -- (b) the layer's own canonical writer abstractions (within-L4 writes
          -- where src is L4's own state-store impl). Refer to
          -- _NON_DURABLE_WRITER_PATH_FRAGMENTS and
          -- _CANONICAL_LAYER_WRITER_PATH_FRAGMENTS for the canonical lists.
          AND NOT {_build_non_durable_target_clause("src.resolved_path")}
          AND NOT {_build_canonical_layer_writer_clause("src.resolved_path")}
          -- 2026-04-29 W5.2/W5.4 Author-Gate: layer self-authority files ARE
          -- their layer's own internal authority for files owned end-to-end
          -- (integrity attestation, self-validation/healing). Routing such
          -- writes through cross-layer write authority would invert the
          -- relationship. See _LAYER_SELF_AUTHORITY_FILES.
          AND NOT {_build_layer_self_authority_clause("src.resolved_path")}
          -- 2026-04-29 W5.3 Author-Gate: mirror the authority-boundary MV's
          -- sanctioned-bridge exemption (apps_*/integrations/, apps_*/services/,
          -- apps_*/enforcement/, *_adapter.py, *_adapter_util.py). Without
          -- this clause the two authority MVs disagreed: imports OK, writes
          -- flagged. See _SANCTIONED_BRIDGE_PATH_PATTERNS.
          AND NOT {_build_sanctioned_bridge_clause("src.resolved_path")}
          -- 2026-04-28 W2.1 ArchivalGatekeeper exclusion: writes routed through
          -- ArchivalGatekeeper.safe_move/safe_archive/safe_delete go through
          -- the canonical L5 file-operation authority — same pattern as
          -- routing through UWG for L4 state. NOT bypasses.
          AND NOT {_build_archival_gatekeeper_clause("e.symbol")}
          -- 2026-04-28 W4 PascalCase class-instantiation exclusion:
          -- _GovernancePlaneVisitor emits writes_through for any call to a
          -- symbol in GOVERNANCE_WRITE_SYMBOLS, which includes 22 PascalCase
          -- dataclass types (ViolationConstraint, CorpusRecord, ExecutionContext,
          -- SurgicalContext, ProposalCommitter, TraceFeatureRecord, KeyRecord,
          -- MutationDiffRecord, ReplayFailureRecord, PromptOutcomeRecord,
          -- HealingOutcomeIntakeRecord, PolicyUpdateProposal, HealingInput,
          -- HealingSuccessRateStore, InMemoryHealingOutcomeIntakeStore, etc.).
          -- These are type instantiations returning new objects, not writes.
          -- Heuristic: writes_through with a single PascalCase identifier
          -- (no dot, starts uppercase, has lowercase) is a class instantiation.
          -- writes_through for real write methods like `.write_text` (has dot)
          -- or top-level write functions like `execute_write` (lowercase start)
          -- are unaffected.
          AND NOT (
              e.relation_type = 'writes_through'
              AND e.symbol NOT LIKE '%.%'
              AND substr(e.symbol, 1, 1) BETWEEN 'A' AND 'Z'
              AND lower(e.symbol) != e.symbol
              AND upper(e.symbol) != e.symbol
          )
        ORDER BY severity, writer_layer
    """)

    # mv_live_future_mutation_conflicts
    # Files with both live-run writes AND future/snapshot link edges — potential current/future confusion.
    cur.execute(f"""
        CREATE TABLE mv_live_future_mutation_conflicts AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            src.resolved_path     AS file,
            src.layer             AS layer,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_to', 'writes_through') THEN e.id END) AS live_write_count,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('links_execution_to_snapshot', 'snapshots_state') THEN e.id END) AS snapshot_link_count,
            CASE
                WHEN COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_to', 'writes_through') THEN e.id END) > 0
                 AND COUNT(DISTINCT CASE WHEN e.relation_type IN ('links_execution_to_snapshot', 'snapshots_state') THEN e.id END) > 0
                THEN 'live_and_future_write_conflict'
                ELSE 'no_conflict'
            END AS conflict_type
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        WHERE e.relation_type IN ('writes_to', 'writes_through', 'links_execution_to_snapshot', 'snapshots_state')
          AND src.resolved_path NOT LIKE 'tests/%'
          AND src.resolved_path NOT LIKE 'tools/%'
        GROUP BY src.resolved_path, src.layer
        HAVING live_write_count > 0 AND snapshot_link_count > 0
        ORDER BY live_write_count DESC
    """)

    # mv_hitl_reclearance_gaps
    # Modules with write edges but no applies_guardrail outgoing edge.
    cur.execute(f"""
        CREATE TABLE mv_hitl_reclearance_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            COALESCE((
                SELECT COUNT(*) FROM edges ew
                WHERE ew.src_id = n.id
                  AND ew.relation_type IN ('writes_to', 'writes_through')
            ), 0)                 AS write_edge_count,
            COALESCE((
                SELECT COUNT(*) FROM edges eg
                WHERE eg.src_id = n.id
                  AND eg.relation_type = 'applies_guardrail'
            ), 0)                 AS guardrail_edge_count,
            CASE
                WHEN COALESCE((
                    SELECT COUNT(*) FROM edges ew
                    WHERE ew.src_id = n.id
                      AND ew.relation_type IN ('writes_to', 'writes_through')
                ), 0) > 0
                 AND COALESCE((
                    SELECT COUNT(*) FROM edges eg
                    WHERE eg.src_id = n.id
                      AND eg.relation_type = 'applies_guardrail'
                ), 0) = 0
                THEN 'write_without_guardrail'
                ELSE 'ok'
            END AS gap_type
        FROM nodes n
        WHERE n.entity_type = 'module'
          AND n.layer IN {_spine_layers_in()}
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
        ORDER BY write_edge_count DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_auth_breach_layers ON mv_authority_boundary_breaches(src_layer, dst_layer)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_write_sov_severity ON mv_write_sovereignty_paths(severity, is_uwg_routed)"
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_hitl_gap ON mv_hitl_reclearance_gaps(gap_type, layer)")

    # -------------------------------------------------------------------------
    # Family 3 — Lifecycle and phase coverage
    # -------------------------------------------------------------------------

    phase_cases = "\n            ".join(
        f"WHEN n.resolved_path LIKE '%{kw}%' THEN '{label}'" for kw, label in _L2_PHASE_KEYWORDS
    )

    # mv_l2_phase_coverage
    cur.execute(f"""
        CREATE TABLE mv_l2_phase_coverage AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            phase_label,
            COUNT(node_id)         AS node_count,
            MAX(has_entry_edge)    AS has_entry_edge,
            MAX(has_exit_edge)     AS has_exit_edge,
            MAX(covered_by_test)   AS covered_by_test,
            CASE WHEN COUNT(node_id) = 0 THEN 1 ELSE 0 END AS gap_flag
        FROM (
            SELECT
                n.id AS node_id,
                CASE
                    {phase_cases}
                    ELSE 'phase_unknown'
                END AS phase_label,
                CASE WHEN EXISTS (
                    SELECT 1 FROM edges ei WHERE ei.dst_id = n.id
                      AND ei.relation_type IN ('imports', 'calls')
                ) THEN 1 ELSE 0 END AS has_entry_edge,
                CASE WHEN EXISTS (
                    SELECT 1 FROM edges eo WHERE eo.src_id = n.id
                      AND eo.relation_type IN ('routes_to_capability', 'routes_to_agent',
                                               'invokes_eval', 'writes_through')
                ) THEN 1 ELSE 0 END AS has_exit_edge,
                CASE WHEN EXISTS (
                    SELECT 1 FROM edges ec WHERE ec.dst_id = n.id
                      AND ec.relation_type = 'covers'
                ) THEN 1 ELSE 0 END AS covered_by_test
            FROM nodes n
            WHERE n.layer = 'L2'
              AND n.entity_type = 'module'
              AND n.resolved_path NOT LIKE 'tests/%'
        )
        GROUP BY phase_label
        ORDER BY phase_label
    """)

    # mv_exit_disposition_coverage
    cur.execute(f"""
        CREATE TABLE mv_exit_disposition_coverage AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            COALESCE((
                SELECT COUNT(*) FROM edges eo
                WHERE eo.src_id = n.id
                  AND eo.relation_type IN (
                      'routes_to_capability', 'invokes_eval',
                      'writes_through', 'writes_via_uwg',
                      'execution_terminates_at_uwg'
                  )
            ), 0)                 AS outgoing_terminal_count,
            CASE WHEN COALESCE((
                SELECT COUNT(*) FROM edges eo
                WHERE eo.src_id = n.id
                  AND eo.relation_type IN (
                      'routes_to_capability', 'invokes_eval',
                      'writes_through', 'writes_via_uwg',
                      'execution_terminates_at_uwg'
                  )
            ), 0) > 0 THEN 1 ELSE 0 END AS is_terminal_covered,
            CASE WHEN COALESCE((
                SELECT COUNT(*) FROM edges eo
                WHERE eo.src_id = n.id
                  AND eo.relation_type IN (
                      'routes_to_capability', 'invokes_eval',
                      'writes_through', 'writes_via_uwg',
                      'execution_terminates_at_uwg'
                  )
            ), 0) = 0 THEN 'no_exit_disposition'
            ELSE 'ok' END         AS gap_type
        FROM nodes n
        WHERE n.layer IN ('L2', 'L5')
          AND n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
        ORDER BY is_terminal_covered ASC, layer
    """)

    # mv_heal_retry_exit_gaps
    cur.execute(f"""
        CREATE TABLE mv_heal_retry_exit_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            CASE WHEN n.resolved_path LIKE '%heal%'
                   OR n.adg_name LIKE '%heal%' THEN 1 ELSE 0 END AS has_heal_keyword,
            CASE WHEN n.resolved_path LIKE '%retry%'
                   OR n.adg_name LIKE '%retry%'
                   OR n.resolved_path LIKE '%rollback%' THEN 1 ELSE 0 END AS has_retry_keyword,
            CASE WHEN EXISTS (
                SELECT 1 FROM edges eo WHERE eo.src_id = n.id
                  AND eo.relation_type IN (
                      'routes_to_capability', 'invokes_eval',
                      'writes_through', 'escalates_failure',
                      'execution_terminates_at_uwg'
                  )
            ) THEN 1 ELSE 0 END   AS has_terminal_exit,
            CASE WHEN (
                    n.resolved_path LIKE '%heal%' OR n.adg_name LIKE '%heal%'
                    OR n.resolved_path LIKE '%retry%' OR n.adg_name LIKE '%retry%'
                )
              AND NOT EXISTS (
                SELECT 1 FROM edges eo WHERE eo.src_id = n.id
                  AND eo.relation_type IN (
                      'routes_to_capability', 'invokes_eval',
                      'writes_through', 'escalates_failure',
                      'execution_terminates_at_uwg'
                  )
            ) THEN 1 ELSE 0 END   AS gap_flag
        FROM nodes n
        WHERE n.entity_type = 'module'
          AND n.layer IN {_spine_layers_in()}
          AND (
            n.resolved_path LIKE '%heal%' OR n.adg_name LIKE '%heal%'
            OR n.resolved_path LIKE '%retry%' OR n.adg_name LIKE '%retry%'
            OR n.resolved_path LIKE '%rollback%'
          )
          AND n.resolved_path NOT LIKE 'tests/%'
        ORDER BY gap_flag DESC
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_l2_phase ON mv_l2_phase_coverage(phase_label, gap_flag)")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_exit_disp ON mv_exit_disposition_coverage(gap_type, layer)"
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_heal_gap ON mv_heal_retry_exit_gaps(gap_flag, layer)")

    # -------------------------------------------------------------------------
    # Partial Family 8 — Determinism seeds
    # -------------------------------------------------------------------------

    # mv_digest_reconciliation
    # Compare meta-stored counts against actual table counts.
    cur.execute(f"""
        CREATE TABLE mv_digest_reconciliation AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            m.key                 AS meta_key,
            m.value               AS meta_value,
            CASE m.key
                WHEN 'total_nodes' THEN CAST((SELECT COUNT(*) FROM nodes) AS TEXT)
                WHEN 'total_edges' THEN CAST((SELECT COUNT(*) FROM edges) AS TEXT)
                ELSE NULL
            END                   AS cross_check_value,
            CASE
                WHEN m.key NOT IN ('total_nodes', 'total_edges') THEN NULL
                WHEN m.key = 'total_nodes'
                     AND m.value = CAST((SELECT COUNT(*) FROM nodes) AS TEXT) THEN 1
                WHEN m.key = 'total_edges'
                     AND m.value = CAST((SELECT COUNT(*) FROM edges) AS TEXT) THEN 1
                ELSE 0
            END                   AS match_flag
        FROM meta m
        WHERE m.key IN ('total_nodes', 'total_edges', 'commit_sha',
                        'schema_version', 'artifact_digest', 'scanner_digest')
        ORDER BY m.key
    """)

    # mv_snapshot_integrity_anomalies
    cur.execute(f"""
        CREATE TABLE mv_snapshot_integrity_anomalies AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            'null_resolved_path'  AS anomaly_type,
            CAST(n.id AS TEXT)    AS affected_id,
            n.adg_name            AS detail
        FROM nodes n
        WHERE n.resolved_path IS NULL OR n.resolved_path = ''
        UNION ALL
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            'null_layer'          AS anomaly_type,
            CAST(n.id AS TEXT)    AS affected_id,
            n.adg_name            AS detail
        FROM nodes n
        WHERE (n.layer IS NULL OR n.layer = '')
          AND n.identity_kind != 'external_module'
          AND n.entity_type = 'module'
        UNION ALL
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            'dynamic_override'    AS anomaly_type,
            CAST(e.id AS TEXT)    AS affected_id,
            e.source_file || ':' || CAST(e.line_no AS TEXT) AS detail
        FROM edges e
        WHERE e.dynamic_resolution IS NOT NULL
          AND e.dynamic_resolution != ''
          AND e.source_file NOT LIKE 'tests/%'
          AND e.source_file NOT LIKE 'tools/%'
        ORDER BY anomaly_type
    """)

    # -------------------------------------------------------------------------
    # Partial Family 10 — Topology seeds
    # -------------------------------------------------------------------------

    # mv_hotspot_centrality
    # Fix: Aggregate at symbol level first (edges reference symbols, not modules),
    # then roll up to module level via resolved_path.
    cur.execute("DROP TABLE IF EXISTS _t_symbol_inbound")
    cur.execute("DROP TABLE IF EXISTS _t_symbol_outbound")

    # Pre-aggregate inbound edges at symbol level by resolved_path
    cur.execute("""
        CREATE TEMP TABLE _t_symbol_inbound AS
        SELECT
            sym.resolved_path AS file_path,
            COUNT(DISTINCT e.id) AS fan_in
        FROM edges e
        JOIN nodes sym ON e.dst_id = sym.id
        WHERE e.relation_type IN ('imports', 'calls')
        AND sym.resolved_path IS NOT NULL
        GROUP BY sym.resolved_path
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_sym_in ON _t_symbol_inbound(file_path)")

    # Pre-aggregate outbound edges at symbol level by resolved_path
    cur.execute("""
        CREATE TEMP TABLE _t_symbol_outbound AS
        SELECT
            sym.resolved_path AS file_path,
            COUNT(DISTINCT e.id) AS fan_out
        FROM edges e
        JOIN nodes sym ON e.src_id = sym.id
        WHERE e.relation_type IN ('imports', 'calls')
        AND sym.resolved_path IS NOT NULL
        GROUP BY sym.resolved_path
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_sym_out ON _t_symbol_outbound(file_path)")

    cur.execute(f"""
        CREATE TABLE mv_hotspot_centrality AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.adg_name            AS adg_name,
            n.layer               AS layer,
            n.resolved_path       AS resolved_path,
            COALESCE(fi.fan_in, 0)   AS fan_in,
            COALESCE(fo.fan_out, 0)  AS fan_out,
            COALESCE(fi.fan_in, 0) + COALESCE(fo.fan_out, 0) AS degree,
            ROUND(
                CAST(COALESCE(fi.fan_in, 0) AS REAL)
                * CAST(COALESCE(fo.fan_out, 0) AS REAL)
                / NULLIF((SELECT COUNT(*) FROM nodes WHERE entity_type='module'), 0),
            4)                    AS betweenness_approx,
            ROUND(
                CAST(COALESCE(fi.fan_in, 0) AS REAL)
                / NULLIF((SELECT COUNT(*) FROM nodes WHERE entity_type='module'), 0),
            4)                    AS degree_centrality
        FROM nodes n
        LEFT JOIN _t_symbol_inbound fi ON fi.file_path = n.resolved_path
        LEFT JOIN _t_symbol_outbound fo ON fo.file_path = n.resolved_path
        WHERE n.entity_type = 'module'
        GROUP BY n.id
        ORDER BY fan_in DESC
    """)

    cur.execute("DROP TABLE IF EXISTS _t_symbol_inbound")
    cur.execute("DROP TABLE IF EXISTS _t_symbol_outbound")

    # mv_unknown_taxonomy_and_orphans
    cur.execute(f"""
        CREATE TABLE mv_unknown_taxonomy_and_orphans AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            n.identity_kind       AS identity_kind,
            n.entity_type         AS entity_type,
            CASE WHEN n.layer IS NULL OR n.layer = '' THEN 1 ELSE 0 END AS unknown_taxonomy_flag,
            CASE
                WHEN NOT EXISTS (
                    SELECT 1 FROM edges ei WHERE ei.dst_id = n.id
                )
                 AND NOT EXISTS (
                    SELECT 1 FROM edges eo WHERE eo.src_id = n.id
                ) THEN 1
                ELSE 0
            END                   AS orphan_flag
        FROM nodes n
        WHERE n.entity_type = 'module'
          AND n.identity_kind != 'external_module'
          AND n.resolved_path NOT LIKE 'tests/%'
        ORDER BY unknown_taxonomy_flag DESC, orphan_flag DESC
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_hotspot_fi ON mv_hotspot_centrality(fan_in DESC, layer)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_hotspot_snapshot ON mv_hotspot_centrality(snapshot_id)")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_orphan_flags ON mv_unknown_taxonomy_and_orphans(orphan_flag, unknown_taxonomy_flag)"
    )

    # -------------------------------------------------------------------------
    # Family 11 — Prompt-assembly runtime wiring gaps
    # -------------------------------------------------------------------------

    # mv_prompt_assembly_wiring_gaps
    # For each module in the prompt-assembly subsystem (dispatcher, bridge, contracts,
    # evidence-contract surface), count live (non-test) callers separately from
    # test-only callers.
    #
    # gap_type = 'disconnected'  =>  module is built and test-covered but has
    #                                zero live runtime callers — the exact
    #                                negative-space pattern that was previously
    #                                undetectable by SC-5 / AP-14 / mv_unknown_taxonomy_and_orphans.
    cur.execute("DROP TABLE IF EXISTS mv_prompt_assembly_wiring_gaps")
    cur.execute(f"""
        CREATE TABLE mv_prompt_assembly_wiring_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.adg_name            AS target_symbol,
            n.resolved_path       AS target_file,
            n.layer               AS layer,
            COUNT(DISTINCT e.id)  AS total_callers,
            COUNT(DISTINCT CASE
                WHEN c.resolved_path NOT LIKE 'tests/%'
                 AND c.resolved_path NOT LIKE 'test_%'
                THEN e.id END)    AS live_callers,
            COUNT(DISTINCT CASE
                WHEN c.resolved_path LIKE 'tests/%'
                  OR c.resolved_path LIKE 'test_%'
                THEN e.id END)    AS test_callers,
            CASE
                WHEN COUNT(DISTINCT CASE
                    WHEN c.resolved_path NOT LIKE 'tests/%'
                     AND c.resolved_path NOT LIKE 'test_%'
                    THEN e.id END) = 0
                THEN 'disconnected'
                ELSE 'ok'
            END                   AS gap_type
        FROM nodes n
        LEFT JOIN edges e  ON e.dst_id = n.id AND e.relation_type = 'imports'
        LEFT JOIN nodes c  ON c.id = e.src_id
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
          AND (
              n.resolved_path LIKE 'tools/adg/prompt_assembly/%'
           OR n.resolved_path LIKE '%c0_evidence_contract_types%'
           OR n.resolved_path LIKE '%c0_dispatcher%'
           OR n.resolved_path LIKE '%c0_bridge_adapter%'
          )
        GROUP BY n.id
        ORDER BY live_callers ASC, total_callers DESC
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_pa_wiring_gap "
        "ON mv_prompt_assembly_wiring_gaps(gap_type, live_callers, test_callers)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_pa_wiring_snapshot ON mv_prompt_assembly_wiring_gaps(snapshot_id)"
    )

    # -------------------------------------------------------------------------
    # Family 12 — Handoff witness tiers (runtime-spine Phase 2)
    # -------------------------------------------------------------------------

    # mv_handoff_witness_tiers
    # For each of the 17 architecture-handoff relation types, classify ADG edges
    # into three witness tiers:
    #   plumbing  — graph_persister.py / lifecycle_trace_contract.py (bootstrap proof)
    #   test      — tests/ prefix (coverage proof)
    #   live_rt   — all other production-code edges (runtime-spine obligation)
    # runtime_orphaned = 1 when extraction is wired and (plumbing OR test) exists
    #                     but live_runtime_witness_count = 0
    cur.execute("DROP TABLE IF EXISTS mv_handoff_witness_tiers")
    cur.execute(f"""
        CREATE TABLE mv_handoff_witness_tiers AS
        WITH handoff_rels AS (
            SELECT 'validates_request'           AS relation_type,
                   'mv_ingress_before_anything'  AS view_name
            UNION ALL SELECT 'produces_plan',            'mv_l1_plan_before_route'
            UNION ALL SELECT 'proposes_route',            'mv_l1_plan_before_route'
            UNION ALL SELECT 'prefilters_scope',          'mv_retrieval_evidence_handoff'
            UNION ALL SELECT 'produces_evidence_contract','mv_retrieval_evidence_handoff'
            UNION ALL SELECT 'packages_prompt_envelope',  'mv_evidence_to_prompt_handoff'
            UNION ALL SELECT 'stamps_execution_packet',   'mv_governed_execution_envelope_continuity'
            UNION ALL SELECT 'propagates_policy_hash',    'mv_governed_execution_envelope_continuity'
            UNION ALL SELECT 'propagates_replay_key',     'mv_governed_execution_envelope_continuity'
            UNION ALL SELECT 'publishes_retrieval_surface','mv_governed_execution_envelope_continuity'
            UNION ALL SELECT 'promotes_future_run_change','mv_governed_execution_envelope_continuity'
            UNION ALL SELECT 'seals_result',              'mv_runtime_exit_continuity'
            UNION ALL SELECT 'chooses_exit_disposition',  'mv_runtime_exit_continuity'
            UNION ALL SELECT 'materializes_hitl_packet',  'mv_runtime_exit_continuity'
            UNION ALL SELECT 'reclears_human_decision',   'mv_runtime_exit_continuity'
            UNION ALL SELECT 'verifies_blast_radius',     'mv_runtime_exit_continuity'
            UNION ALL SELECT 'appends_commit_receipt',    'mv_runtime_exit_continuity'
        ),
        tier_counts AS (
            SELECT
                hr.relation_type,
                hr.view_name,
                COALESCE(SUM(CASE
                    WHEN e.source_file IN (
                        'agentic_core/adg/extraction/graph_persister.py',
                        'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
                    ) THEN 1 ELSE 0 END), 0) AS plumbing_witness_count,
                COALESCE(SUM(CASE
                    WHEN e.source_file LIKE 'tests/%'
                    THEN 1 ELSE 0 END), 0)   AS test_witness_count,
                COALESCE(SUM(CASE
                    WHEN e.source_file NOT IN (
                        'agentic_core/adg/extraction/graph_persister.py',
                        'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
                    ) AND e.source_file NOT LIKE 'tests/%'
                    THEN 1 ELSE 0 END), 0)   AS live_runtime_witness_count
            FROM handoff_rels hr
            LEFT JOIN edges e ON e.relation_type = hr.relation_type
            GROUP BY hr.relation_type, hr.view_name
        )
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            relation_type,
            view_name,
            plumbing_witness_count,
            test_witness_count,
            live_runtime_witness_count,
            CASE WHEN (plumbing_witness_count + test_witness_count + live_runtime_witness_count) = 0
                 THEN 1 ELSE 0 END AS zero_witness_count,
            CASE WHEN (plumbing_witness_count > 0 OR test_witness_count > 0)
                  AND live_runtime_witness_count = 0
                 THEN 1 ELSE 0 END AS built_plus_test_or_plumbing_covered_plus_runtime_orphaned,
            CASE WHEN (plumbing_witness_count + test_witness_count + live_runtime_witness_count) > 0
                  AND (plumbing_witness_count > 0 OR test_witness_count > 0)
                  AND live_runtime_witness_count = 0
                 THEN 1 ELSE 0 END AS runtime_orphaned
        FROM tier_counts
        ORDER BY view_name, relation_type
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_handoff_witness_rt_orphaned"
        " ON mv_handoff_witness_tiers(runtime_orphaned, view_name)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_handoff_witness_snapshot ON mv_handoff_witness_tiers(snapshot_id)"
    )

    # -------------------------------------------------------------------------
    # Family 13 — Cross-cutting witness tiers (all architectural obligation families)
    # -------------------------------------------------------------------------

    # mv_cross_cutting_witness_tiers
    # Same witness-tier model as mv_handoff_witness_tiers but covering all 13
    # cross-cutting architectural obligation families:
    #
    #   1.  capability_egress_chokepoint       — capability token + egress route proof
    #   2.  local_heal_first                   — local healer dispatches before escalation
    #   3.  heal_retry_under_blueprint         — orchestrator retries under same blueprint
    #   4.  exit_hitl_envelope_continuity      — exit packet sealed + HITL cleared
    #   5.  hitl_freeze_materialize_reclear    — context frozen before HITL, recleared after
    #   6.  commit_uwg_envelope_continuity     — blast-radius checked + receipt appended
    #   7.  uwg_full_commit_chain              — full UWG validation + durable commit
    #   8.  no_direct_write_live_planes        — writes route through UWG, no bypass
    #   9.  replay_envelope_continuity         — RNG/time sealed + replay key emitted
    #   10. observability_non_interference     — observability reads only, no side-effects
    #   11. future_run_only_promotion          — promotion gated + committed via DPO
    #   12. offline_publication_before_runtime — surface published offline before runtime reads
    #   13. retrieval_surface_integrity        — retrieval indexed, guardrailed, routed
    #
    # Tier semantics identical to mv_handoff_witness_tiers:
    #   plumbing  — graph_persister.py + lifecycle_trace_contract.py (bootstrap proof)
    #   test      — tests/* prefix (coverage proof)
    #   live_rt   — all other production-code edges (runtime-spine obligation)
    cur.execute("DROP TABLE IF EXISTS mv_cross_cutting_witness_tiers")
    cur.execute(f"""
        CREATE TABLE mv_cross_cutting_witness_tiers AS
        WITH cross_cutting_rels AS (
            -- 1. capability_egress_chokepoint
            SELECT 'capability_egress_chokepoint'  AS family_name,
                   'routes_to_capability'           AS relation_type
            UNION ALL SELECT 'capability_egress_chokepoint', 'issues_capability_token'
            UNION ALL SELECT 'capability_egress_chokepoint', 'has_capability'
            UNION ALL SELECT 'capability_egress_chokepoint', 'validates_agent_capability'
            -- 2. local_heal_first
            UNION ALL SELECT 'local_heal_first',             'dispatches_healing_run'
            UNION ALL SELECT 'local_heal_first',             'confirms_heal'
            UNION ALL SELECT 'local_heal_first',             'aborts_heal'
            -- 3. heal_retry_under_blueprint
            UNION ALL SELECT 'heal_retry_under_blueprint',   'orchestrates_healing'
            UNION ALL SELECT 'heal_retry_under_blueprint',   'heals'
            -- 4. exit_hitl_envelope_continuity
            UNION ALL SELECT 'exit_hitl_envelope_continuity', 'seals_result'
            UNION ALL SELECT 'exit_hitl_envelope_continuity', 'chooses_exit_disposition'
            UNION ALL SELECT 'exit_hitl_envelope_continuity', 'materializes_hitl_packet'
            UNION ALL SELECT 'exit_hitl_envelope_continuity', 'reclears_human_decision'
            -- 5. hitl_freeze_materialize_reclear
            UNION ALL SELECT 'hitl_freeze_materialize_reclear', 'freezes_context'
            UNION ALL SELECT 'hitl_freeze_materialize_reclear', 'escalates_to_human'
            UNION ALL SELECT 'hitl_freeze_materialize_reclear', 'awaits_approval'
            UNION ALL SELECT 'hitl_freeze_materialize_reclear', 'requires_human_review'
            UNION ALL SELECT 'hitl_freeze_materialize_reclear', 'learns_from_decision'
            -- 6. commit_uwg_envelope_continuity
            UNION ALL SELECT 'commit_uwg_envelope_continuity', 'verifies_blast_radius'
            UNION ALL SELECT 'commit_uwg_envelope_continuity', 'appends_commit_receipt'
            UNION ALL SELECT 'commit_uwg_envelope_continuity', 'commits_mutation'
            UNION ALL SELECT 'commit_uwg_envelope_continuity', 'distributes_mutation'
            -- 7. uwg_full_commit_chain
            UNION ALL SELECT 'uwg_full_commit_chain',         'validates_uwg_intent'
            UNION ALL SELECT 'uwg_full_commit_chain',         'checks_policy_hash_at_uwg'
            UNION ALL SELECT 'uwg_full_commit_chain',         'validates_blast_radius_at_uwg'
            UNION ALL SELECT 'uwg_full_commit_chain',         'performs_durable_commit'
            UNION ALL SELECT 'uwg_full_commit_chain',         'applies_hmac_seal'
            UNION ALL SELECT 'uwg_full_commit_chain',         'packages_execution_trace'
            UNION ALL SELECT 'uwg_full_commit_chain',         'appends_hash_chain'
            -- 8. no_direct_write_live_planes
            UNION ALL SELECT 'no_direct_write_live_planes',   'routes_through_uwg'
            UNION ALL SELECT 'no_direct_write_live_planes',   'bypasses_uwg'
            UNION ALL SELECT 'no_direct_write_live_planes',   'execution_terminates_at_uwg'
            -- 9. replay_envelope_continuity
            UNION ALL SELECT 'replay_envelope_continuity',    'guards_replay'
            UNION ALL SELECT 'replay_envelope_continuity',    'seeds_rng'
            UNION ALL SELECT 'replay_envelope_continuity',    'patches_time'
            UNION ALL SELECT 'replay_envelope_continuity',    'emits_replay_key'
            UNION ALL SELECT 'replay_envelope_continuity',    'compares_proof'
            UNION ALL SELECT 'replay_envelope_continuity',    'emits_determinism_digest'
            -- 10. observability_non_interference
            UNION ALL SELECT 'observability_non_interference', 'observes_policy_state'
            UNION ALL SELECT 'observability_non_interference', 'observes_runtime_state'
            UNION ALL SELECT 'observability_non_interference', 'snapshots_state'
            UNION ALL SELECT 'observability_non_interference', 'intercepts_io'
            UNION ALL SELECT 'observability_non_interference', 'transcripts_response'
            UNION ALL SELECT 'observability_non_interference', 'hard_fails_untranscripted'
            -- 11. future_run_only_promotion
            UNION ALL SELECT 'future_run_only_promotion',     'promotes_future_run_change'
            UNION ALL SELECT 'future_run_only_promotion',     'gates_promotion'
            UNION ALL SELECT 'future_run_only_promotion',     'commits_optimization'
            UNION ALL SELECT 'future_run_only_promotion',     'builds_dpo_batch'
            -- 12. offline_publication_before_runtime
            UNION ALL SELECT 'offline_publication_before_runtime', 'publishes_retrieval_surface'
            UNION ALL SELECT 'offline_publication_before_runtime', 'reads_materialized_surface'
            UNION ALL SELECT 'offline_publication_before_runtime', 'materializes_read_view'
            -- 13. retrieval_surface_integrity
            UNION ALL SELECT 'retrieval_surface_integrity',   'indexes_for_retrieval'
            UNION ALL SELECT 'retrieval_surface_integrity',   'retrieves_via'
            UNION ALL SELECT 'retrieval_surface_integrity',   'retrieves_from_store'
            UNION ALL SELECT 'retrieval_surface_integrity',   'applies_retrieval_guardrail'
            UNION ALL SELECT 'retrieval_surface_integrity',   'routes_retrieval'
        ),
        tier_counts AS (
            SELECT
                cr.family_name,
                cr.relation_type,
                COALESCE(SUM(CASE
                    WHEN e.source_file IN (
                        'agentic_core/adg/extraction/graph_persister.py',
                        'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
                    ) THEN 1 ELSE 0 END), 0) AS plumbing_witness_count,
                COALESCE(SUM(CASE
                    WHEN e.source_file LIKE 'tests/%'
                    THEN 1 ELSE 0 END), 0)   AS test_witness_count,
                COALESCE(SUM(CASE
                    WHEN e.source_file NOT IN (
                        'agentic_core/adg/extraction/graph_persister.py',
                        'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
                    ) AND e.source_file NOT LIKE 'tests/%'
                    THEN 1 ELSE 0 END), 0)   AS live_runtime_witness_count
            FROM cross_cutting_rels cr
            LEFT JOIN edges e ON e.relation_type = cr.relation_type
            GROUP BY cr.family_name, cr.relation_type
        )
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            family_name,
            relation_type,
            plumbing_witness_count,
            test_witness_count,
            live_runtime_witness_count,
            CASE WHEN (plumbing_witness_count + test_witness_count + live_runtime_witness_count) = 0
                 THEN 1 ELSE 0 END AS zero_witness_count,
            CASE WHEN (plumbing_witness_count > 0 OR test_witness_count > 0)
                  AND live_runtime_witness_count = 0
                 THEN 1 ELSE 0 END AS built_plus_test_or_plumbing_covered_plus_runtime_orphaned,
            CASE WHEN (plumbing_witness_count + test_witness_count + live_runtime_witness_count) > 0
                  AND (plumbing_witness_count > 0 OR test_witness_count > 0)
                  AND live_runtime_witness_count = 0
                 THEN 1 ELSE 0 END AS runtime_orphaned
        FROM tier_counts
        ORDER BY family_name, relation_type
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_cc_witness_rt_orphaned"
        " ON mv_cross_cutting_witness_tiers(runtime_orphaned, family_name)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_cc_witness_snapshot ON mv_cross_cutting_witness_tiers(snapshot_id)"
    )

    # -------------------------------------------------------------------------
    # Family 14 — Class B breach surfaces (absence/forbidden-path semantics)
    # -------------------------------------------------------------------------

    # mv_local_heal_first_breaches
    # Identifies heal-domain production modules that have escalation edges
    # (escalates_failure, escalates_to_human) but NO local-heal-first relations
    # (dispatches_healing_run, confirms_heal, aborts_heal) in the same source file.
    # Zero rows = no breach (PASSED). Any rows = forbidden path detected.
    cur.execute("DROP TABLE IF EXISTS mv_local_heal_first_breaches")
    cur.execute(f"""
        CREATE TABLE mv_local_heal_first_breaches AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            e.source_file,
            e.relation_type         AS escalation_relation,
            COUNT(DISTINCT e.id)    AS breach_edge_count,
            CASE WHEN EXISTS (
                SELECT 1 FROM edges e2
                WHERE e2.source_file = e.source_file
                  AND e2.relation_type IN (
                      'dispatches_healing_run', 'confirms_heal', 'aborts_heal'
                  )
            ) THEN 0 ELSE 1 END    AS missing_heal_first_in_file
        FROM edges e
        WHERE e.relation_type IN ('escalates_failure', 'escalates_to_human')
          AND e.source_file NOT LIKE 'tests/%'
          AND e.source_file NOT IN (
              'agentic_core/adg/extraction/graph_persister.py',
              'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
          )
          AND (
              e.source_file LIKE '%heal%'
              OR e.source_file LIKE '%retry%'
              OR e.source_file LIKE '%recovery%'
          )
        GROUP BY e.source_file, e.relation_type
        HAVING missing_heal_first_in_file = 1
        ORDER BY breach_edge_count DESC
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_local_heal_breach"
        " ON mv_local_heal_first_breaches(source_file, escalation_relation)"
    )

    # mv_observability_interference_breaches
    # Identifies production source files that have BOTH observability relations
    # (observes_*, snapshots_state, intercepts_io, transcripts_response,
    #  hard_fails_untranscripted) AND mutation/write relations
    # (commits_mutation, performs_durable_commit, applies_hmac_seal, bypasses_uwg,
    #  routes_through_uwg).
    # Any such file is a forbidden-path breach: observability code with side-effects.
    # Zero rows = no breach (PASSED).
    cur.execute("DROP TABLE IF EXISTS mv_observability_interference_breaches")
    cur.execute(f"""
        CREATE TABLE mv_observability_interference_breaches AS
        SELECT
            {_snapshot_id_expr()}        AS snapshot_id,
            obs_e.source_file,
            COUNT(DISTINCT obs_e.id)     AS observability_edge_count,
            COUNT(DISTINCT mut_e.id)     AS mutation_edge_count
        FROM edges obs_e
        JOIN edges mut_e ON mut_e.source_file = obs_e.source_file
        WHERE obs_e.relation_type IN (
            'observes_policy_state', 'observes_runtime_state', 'snapshots_state',
            'intercepts_io', 'transcripts_response', 'hard_fails_untranscripted'
        )
          AND mut_e.relation_type IN (
            'commits_mutation', 'performs_durable_commit', 'applies_hmac_seal',
            'bypasses_uwg', 'routes_through_uwg'
          )
          AND obs_e.source_file NOT LIKE 'tests/%'
          AND obs_e.source_file NOT IN (
              'agentic_core/adg/extraction/graph_persister.py',
              'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
          )
        GROUP BY obs_e.source_file
        HAVING observability_edge_count > 0 AND mutation_edge_count > 0
        ORDER BY mutation_edge_count DESC
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_obs_interference"
        " ON mv_observability_interference_breaches(source_file)"
    )

    conn.commit()

    counts: dict[str, int] = {}
    try:
        for tbl in _PHASE_A_TABLES:
            row = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()
            counts[tbl] = row[0] if row else 0
    finally:
        if _owns_conn:
            conn.close()
    return counts
