# ADG Redundancy Audit

Snapshot: `adg_indexed_04252026_0843.sqlite`

## ADG Capability Inventory

- Materialized views: 65 (non-empty: 56)
- P-views (P0/P1/P2/P3 classifiers): 15
- Detector tables:
  - A6: `module_entrypoints` = 6,986 rows
  - A7: `side_effect_calls` = 133,855 rows
  - A9: `config_references` = 1,164 rows
  - A11: `test_stubs` = 590 rows
  - A12: `gate_self_consistency` = 100 rows
  - Overlay: `overlay_violations` = 116,829 rows
  - Core SC/AP: `violations` = 5,348 rows

## CI Gates Analysis (103 gates in ops_scripts/ci/)

### Redundancy candidates: 39 gates flagged

| Gate | Doc (first line) | ADG capability that may cover it |
|------|-------------------|----------------------------------|
| `ops_scripts/ci/check_agents_mcp_coverage.py` | check_agents_mcp_coverage.py ΓÇö CI gate: every MCP server in mcp_config.json | mv_agent_specialization_overlap / mv_agent_tool_ratio; R6 mcp_contract_drift detector + mcp_tool_declarations |
| `ops_scripts/ci/check_agents_md_sync.py` | Fail-closed AGENTS.md autogen-block integrity gate (T6d). | mv_snapshot_baseline / mv_snapshot_integrity_anomalies / mv_snapshot_regression_summary; mv_agent_specialization_overlap / mv_agent_tool_ratio |
| `ops_scripts/ci/check_baseline_staleness.py` | Gate S_STALE ΓÇö baseline-age warning for ratchet JSONs. | mv_snapshot_baseline / mv_snapshot_integrity_anomalies / mv_snapshot_regression_summary |
| `ops_scripts/ci/check_cache_prefix_stability.py` | Cache-prefix stability CI gate ΓÇö EQ-9 (ADR-PROMPT-ASSEMBLY-002 ┬º10). | mv_prompt_assembly_wiring_gaps |
| `ops_scripts/ci/check_config_references.py` | CI gate: env-flag reference integrity between code and .env.example. | mv_snapshot_baseline / mv_snapshot_integrity_anomalies / mv_snapshot_regression_summary |
| `ops_scripts/ci/check_cyclomatic_ceiling.py` | Gate Q2 ΓÇö cyclomatic complexity ratchet (plan W3.6). | (no direct ADG view) ΓÇö file-level metric |
| `ops_scripts/ci/check_dead_folder_detector.py` | Gate D_dead_folder_detector ΓÇö entire production subdirectories that are dead. | mv_unknown_taxonomy_and_orphans / overlay dead_import_resolved |
| `ops_scripts/ci/check_dead_symbols_ratchet.py` | Gate A3 ΓÇö dead public symbol ratchet (plan W2.3). | mv_unknown_taxonomy_and_orphans / overlay dead_import_resolved |
| `ops_scripts/ci/check_decision_ledger_chain.py` | check_decision_ledger_chain.py ΓÇö CI gate: decision-ledger integrity (W1.1). | mv_snapshot_baseline / mv_snapshot_integrity_anomalies / mv_snapshot_regression_summary |
| `ops_scripts/ci/check_exemplar_coverage.py` | CI gate: exemplar coverage \u2014 W5 RH5.2. | mv_agent_specialization_overlap / mv_agent_tool_ratio |
| `ops_scripts/ci/check_external_service_literal_ssot.py` | Gate AUDIT-3 ΓÇö external-service literal SSOT ratchet. | mv_unknown_taxonomy_and_orphans + grep ΓÇö partial coverage |
| `ops_scripts/ci/check_graph_watchlist_delta.py` | Gate G-WATCHLIST-DELTA: graph hotspot regression-count ratchet (H2). | mv_hotspot_centrality / mv_graph_chokepoint_bridges / mv_graph_reverse_dependency_hotspots |
| `ops_scripts/ci/check_hardcoded_exclusions.py` | R3 gate: detect hardcoded exclusion sets outside the allowlist (ratchet). | mv_unknown_taxonomy_and_orphans + grep ΓÇö partial coverage |
| `ops_scripts/ci/check_l1_plan_contract_fields.py` | CI gate ΓÇö L1PlanContract schema drift check (ADR-043). | mv_determinism_provenance_drift / mv_digest_reconciliation |
| `ops_scripts/ci/check_layer_skip.py` | Gate B2 ΓÇö layer-skip ratchet (plan W3.1). | v_p0_apps_direct_infra / v_p1_mis_layered_infra |
| `ops_scripts/ci/check_ledger_coverage.py` | check_ledger_coverage.py ΓÇö CI gate over the Author-Gate decision ledger. | mv_agent_specialization_overlap / mv_agent_tool_ratio |
| `ops_scripts/ci/author_gate/check_ledger_integrity.py` | check_ledger_integrity.py ΓÇö CI gate: Author-Gate ledger hash chain is unbroken. | mv_snapshot_baseline / mv_snapshot_integrity_anomalies / mv_snapshot_regression_summary |
| `ops_scripts/ci/check_lpg_drift_ratchet.py` | Gate L2 ΓÇö L_PG (Prompt Governance / knowledge plane) drift ratchet (plan W3.2). | mv_determinism_provenance_drift / mv_digest_reconciliation |
| `ops_scripts/ci/check_mcp_sync_integrity.py` | Fail-closed MCP sync integrity gate. | mv_snapshot_baseline / mv_snapshot_integrity_anomalies / mv_snapshot_regression_summary; R6 mcp_contract_drift detector + mcp_tool_declarations |
| `ops_scripts/ci/check_module_loc_ratchet.py` | Gate M1 ΓÇö module LOC ratchet (plan W3.3). | (no direct ADG view) ΓÇö file-level metric |
| `ops_scripts/ci/check_notion_plan_file_drift.py` | check_notion_plan_file_drift.py ΓÇö CI drift gate for Notion Γåö disk plan files. | mv_determinism_provenance_drift / mv_digest_reconciliation |
| `ops_scripts/ci/check_observability_on_high_fanin.py` | Gate AUDIT-2 ΓÇö observability on high-fan-in modules ratchet. | mv_hotspot_centrality / mv_graph_chokepoint_bridges / mv_graph_reverse_dependency_hotspots; mv_cross_cutting_witness_tiers / mv_handoff_witness_tiers / mv_runtime_spine_gaps |
| `ops_scripts/ci/author_gate/check_outcome_coverage.py` | check_outcome_coverage.py ΓÇö CI gate: every surfaced decision older than the | mv_agent_specialization_overlap / mv_agent_tool_ratio |
| `ops_scripts/ci/check_runtime_adg_coverage.py` | Runtime ADG Coverage CI Gate ΓÇö W7.1 P4.1 (audit mode). | mv_agent_specialization_overlap / mv_agent_tool_ratio |
| `ops_scripts/ci/check_runtime_hitl_ledger_integrity.py` | CI gate: verify the runtime HITL ledger audit chain (W7 P7.1). | mv_snapshot_baseline / mv_snapshot_integrity_anomalies / mv_snapshot_regression_summary; mv_hitl_reclearance_gaps; mv_exit_disposition_coverage |
| `ops_scripts/ci/check_severity_band_ssot.py` | CI gate: forbid new hardcoded severity/band literals outside SSOT modules. | mv_unknown_taxonomy_and_orphans + grep ΓÇö partial coverage |
| `ops_scripts/ci/check_snapshot_has_mvs.py` | CI gate: check_snapshot_has_mvs.py ΓÇö ADG snapshot graph-layer completeness. | mv_snapshot_baseline / mv_snapshot_integrity_anomalies / mv_snapshot_regression_summary |
| `ops_scripts/ci/check_ssot_magic_constants.py` | Gate AUDIT-1 ΓÇö SSOT magic-constants ratchet. | mv_unknown_taxonomy_and_orphans + grep ΓÇö partial coverage |
| `ops_scripts/ci/check_test_harness_coverage.py` | CI gate: every production module must have at least one test-harness import. | mv_agent_specialization_overlap / mv_agent_tool_ratio |
| `ops_scripts/ci/check_trace_stub_modules.py` | Gate E1 ΓÇö trace-stub module detector (plan W2.4). | mv_cross_cutting_witness_tiers / mv_handoff_witness_tiers / mv_runtime_spine_gaps |
| `ops_scripts/ci/check_violation_aging_sla.py` | Gate AUDIT-6 ΓÇö violation triage SLA ratchet. | violations table + core SC/AP burndown |
| `ops_scripts/ci/check_w4_exit_disposition.py` | Gate I1 ΓÇö L5ΓåöL6 exit-disposition parity (plan W4.6). | mv_exit_disposition_coverage |
| `ops_scripts/ci/check_w4_replay_surface_gaps.py` | Gate I2 ΓÇö replay-surface / evidence-consumption gap (plan W4.7). | mv_replay_surface_gaps / mv_trace_replay_eval_gaps / mv_eval_coverage_by_path |
| `ops_scripts/ci/check_w5_structured_output.py` | Gate P ΓÇö structured-field extraction boundary (plan W5.2). | mv_task_contract_gaps / mv_structured_output_gaps |
| `ops_scripts/ci/check_w5_untyped_seam.py` | Gate F1 ΓÇö untyped cross-layer seam (plan W5.4). | v_p0_apps_direct_infra / v_p1_mis_layered_infra |
| `ops_scripts/ci/check_w6_churn_complexity_kpi.py` | KPI K1 ΓÇö churn ├ù complexity dashboard (plan W6.3, CodeScene formula). | (no direct ADG view) ΓÇö file-level metric |
| `ops_scripts/ci/check_w6_fanin_collapse.py` | Gate H2 ΓÇö fan-in collapse on high-centrality nodes (plan W6.2). | mv_hotspot_centrality / mv_graph_chokepoint_bridges / mv_graph_reverse_dependency_hotspots |
| `ops_scripts/ci/check_w6_trace_theater_kpi.py` | KPI E3 ΓÇö trace-theater growth per layer (plan W6.4). | mv_cross_cutting_witness_tiers / mv_handoff_witness_tiers / mv_runtime_spine_gaps |
| `ops_scripts/ci/check_waiver_provenance.py` | Gate W6_WAIVER_PROVENANCE ΓÇö every wiring-CI waiver must cite a real ADR or plan. | mv_determinism_provenance_drift / mv_digest_reconciliation |

### No-overlap gates: 64

These gates appear unique (no obvious ADG view covers them). They may be **legitimate non-ADG concerns** (config schema, file-format, process-level checks) or **gaps in ADG coverage** worth filing.

| Gate | Doc (first line) |
|------|-------------------|
| `ops_scripts/ci/check_agent_sealed_return.py` | CI gate: opt-in enforcement that @requires_sealed_return classes return SealedL2Artifact. |
| `ops_scripts/ci/check_canonical_pipeline_wiring.py` | Gate J1 ΓÇö canonical pipeline wiring (plan W1.3). |
| `ops_scripts/ci/check_cross_mainline_dispatcher.py` | Gate AUDIT-4 ΓÇö cross-mainline dispatcher ratchet. |
| `ops_scripts/ci/check_dead_methods_ratchet.py` | Gate A3B ΓÇö dead class methods inside live modules (AST-assisted). |
| `ops_scripts/ci/check_decision_required.py` | check_decision_required.py ΓÇö W4.2 pre-commit gate. |
| `ops_scripts/ci/check_deferred_scope_markers.py` | check_deferred_scope_markers.py ΓÇö pre-commit gate for DEFERRED_SCOPE marker contract. |
| `ops_scripts/ci/check_env_var_in_config_layer.py` | Gate AUDIT-5 ΓÇö env-var location ratchet. |
| `ops_scripts/ci/check_exception_contract.py` | CI gate: raise/catch symmetry on declared exception contracts. |
| `ops_scripts/ci/check_exclusion_consistency.py` | R2 gate: YAML runtime-scanner mirrors Γåö path_constants.py frozensets. |
| `ops_scripts/ci/check_exit_decision_schema.py` | CI gate ΓÇö validate emitted ExitDecision artifacts against the SSOT schema. |
| `ops_scripts/ci/check_exit_eval_wiring.py` | CI gate: exit_eval wiring completeness. |
| `ops_scripts/ci/check_expected_wiring.py` | CI gate: verify declared feature wirings still exist in source. |
| `ops_scripts/ci/check_governed_app_conformance.py` | Governed-App Conformance Gate. |
| `ops_scripts/ci/check_graph_island.py` | Gate G-ISLAND: non-giant connected components ratchet (H2). |
| `ops_scripts/ci/check_graph_layer_evidence.py` | CI gate: check_graph_layer_evidence.py |
| `ops_scripts/ci/check_graph_reach.py` | Gate G-REACH: L0-reachability of production modules (H2). |
| `ops_scripts/ci/check_graph_reach_archival.py` | Gate G_REACH_ARCHIVAL ΓÇö subset of G_REACH orphans that are real cleanup candidates. |
| `ops_scripts/ci/check_judge_calibration.py` | CI gate: LLM-judge calibration (LJH4.3). |
| `ops_scripts/ci/check_layer_doc_binding.py` | Gate D1 ΓÇö layer doc-to-code binding (plan W3.4). |
| `ops_scripts/ci/check_ledger_append_only.py` | check_ledger_append_only.py ΓÇö W4.1 CI gate. |
| `ops_scripts/ci/check_ledger_freshness.py` | check_ledger_freshness.py ΓÇö W3.1 per-ledger freshness SLO gate. |
| `ops_scripts/ci/author_gate/check_ledger_schema.py` | check_ledger_schema.py ΓÇö CI gate: decision ledger matches canonical DDL. |
| `ops_scripts/ci/check_ledger_writer_contract.py` | check_ledger_writer_contract.py ΓÇö CI gate for the intelligence-ledger rollout. |
| `ops_scripts/ci/check_lifecycle_pairs.py` | CI gate: enforce resource-lifecycle open/close pairs. |
| `ops_scripts/ci/check_marker_ledger_parity.py` | check_marker_ledger_parity.py ΓÇö CI gate: DECISION_CAPTURED marker Γåö ledger parity (W1.2). |
| `ops_scripts/ci/check_memory_promotion_parity.py` | check_memory_promotion_parity.py ΓÇö W5.2 memory-graph promotion parity. |
| `ops_scripts/ci/check_notion_decision_parity.py` | check_notion_decision_parity.py ΓÇö W5.1 Notion Γåö SQLite decision parity. |
| `ops_scripts/ci/check_notion_schema_mece.py` | check_notion_schema_mece.py ΓÇö CI gate for Notion Wave/Phase Convergence MECE v2. |
| `ops_scripts/ci/check_overlay_ratchet.py` | Parametric overlay ratchet ΓÇö implements C1-C5 from RCA-2026-04-24. |
| `ops_scripts/ci/check_pipeline_skips.py` | CI gate: check_pipeline_skips.py ΓÇö ADG pipeline skip-ledger enforcement. |
| `ops_scripts/ci/check_post_cursor_agent_alive.py` | check_post_cursor_agent_alive.py ΓÇö W5.6 post_cascade hook heartbeat gate. |
| `ops_scripts/ci/check_post_cursor_agent_payload.py` | CI gate: every post_cursor_agent_*.py hook must use the shared payload extractor. |
| `ops_scripts/ci/check_precedent_receipt.py` | check_precedent_receipt.py ΓÇö W2.1 precedent-receipt parity gate. |
| `ops_scripts/ci/check_precedent_usage_rate.py` | check_precedent_usage_rate.py ΓÇö W5.3 precedent usage-rate monitor. |
| `ops_scripts/ci/check_prediction_binding_sla.py` | check_prediction_binding_sla.py ΓÇö W3.2 predictionΓåÆoutcome binding SLA gate. |
| `ops_scripts/ci/check_prompt_packet_contract.py` | C5 PA conformance CI gate (fail-closed). |
| `ops_scripts/ci/check_prompt_reception_v2.py` | CI gate: prompt reception v2 wiring \u2014 W5 RH5.3. |
| `ops_scripts/ci/check_query_progress_bar.py` | Query Progress Bar CI Gate ΓÇö Constitutional Rule ┬º16. |
| `ops_scripts/ci/check_role_dedup.py` | Gate D2 ΓÇö role duplication with orphans (plan W3.4). |
| `ops_scripts/ci/check_rubric_diff_review.py` | CI gate: enforce ADR-053/054 H7 rubric-diff review rules. |
| `ops_scripts/ci/check_seam_test_export_coherence.py` | Gate G2 ΓÇö seam-test export coherence (plan W2.5). |
| `ops_scripts/ci/check_sidecar_freshness.py` | check_sidecar_freshness.py ΓÇö CI gate: author_gate_precedent.json freshness (W2.2). |
| `ops_scripts/ci/check_skill_frontmatter.py` | check_skill_frontmatter.py ΓÇö CI gate: every ``.windsurf/skills/<name>/SKILL.md`` |
| `ops_scripts/ci/check_structure_policy.py` | Structure Policy CI Gate ΓÇö YAML-only enforcement. |
| `ops_scripts/ci/check_terminal_cleanup.py` | Terminal/Subprocess Cleanup CI Gate ΓÇö Constitutional Rule ┬º11. |
| `ops_scripts/ci/check_unused_imports_ratchet.py` | Gate S4 ΓÇö unused-import ratchet (plan W4.4). |
| `ops_scripts/ci/check_uwg_bypass_ratchet.py` | Gate S2 ΓÇö UWG-bypass ratchet (plan W4.2). |
| `ops_scripts/ci/check_w4_guardrail_separation.py` | Gate N ΓÇö guardrail / evaluator co-location (plan W4.9, Anthropic pattern). |
| `ops_scripts/ci/check_w4_l5_bypass.py` | Gate C2 ΓÇö L5 guardrail bypass (plan W4.2). |
| `ops_scripts/ci/check_w4_policy_without_audit.py` | Gate C4 ΓÇö policy decision without audit (plan W4.4). |
| `ops_scripts/ci/check_w4_silent_writes.py` | Gate C3 ΓÇö silent write (no sibling side-effect emit) (plan W4.3). |
| `ops_scripts/ci/check_w4_tool_call_parity.py` | Gate O ΓÇö tool-call ground-truth parity (plan W4.8, Anthropic pattern). |
| `ops_scripts/ci/check_w4_unresolved_callsites.py` | Gate C5 ΓÇö unresolved callsite ratchet (plan W4.5). |
| `ops_scripts/ci/check_w4_uwg_bypass_pview.py` | Gate C1 ΓÇö UWG write-path bypass (plan W4.1). |
| `ops_scripts/ci/check_w5_broken_contract.py` | Gate F2 ΓÇö broken-contract consumer (plan W5.5). |
| `ops_scripts/ci/check_w5_missing_adapter.py` | Gate F3 ΓÇö missing adapter for declared Protocol / abstract class (plan W5.6). |
| `ops_scripts/ci/check_w5_taint_actionable.py` | Gate M ΓÇö untrusted-text-to-action taint (plan W5.1). |
| `ops_scripts/ci/check_w6_ap_velocity_kpi.py` | KPI H3 ΓÇö anti-pattern velocity per 1k LOC (plan W6.5). |
| `ops_scripts/ci/check_w6_mv_staleness.py` | Gate H4 ΓÇö MV staleness via total-edge delta (plan W6.6). |
| `ops_scripts/ci/check_w6_new_orphans_delta.py` | Gate H1 ΓÇö new-orphan delta (plan W6.1). |
| `ops_scripts/ci/check_waiver_expiry.py` | Gate W5.1 ΓÇö waiver expiry gate. |
| `ops_scripts/ci/check_weekly_calibration_freshness.py` | check_weekly_calibration_freshness.py ΓÇö CI gate (W4.3, plan c8f4a2). |
| `ops_scripts/ci/check_windsurf_config_schema.py` | Constitutional ┬º26 ΓÇö Windsurf config schema purity. |
| `ops_scripts/ci/check_writer_allowlist.py` | check_writer_allowlist.py ΓÇö W5.5 ledger writer-process allowlist. |

## Test Files vs ADG Coverage

Total unit tests: 1273

### Tests that may be ADG-redundant

| Test file | Suggested ADG coverage |
|-----------|------------------------|
| `tests/unit/agentic_core/L5_safety/reasoning/test_GravityLeakHealerAgent.py` | Gravity tests covered by v_p0_apps_direct_infra / v_p1_mis_layered_infra |
| `tests/unit/agentic_core/L3_orchestration/reasoning/test_GravityStateAgent.py` | Gravity tests covered by v_p0_apps_direct_infra / v_p1_mis_layered_infra |
| `tests/unit/agentic_core/L5_safety/reasoning/test_PascalSovereigntyAgent.py` | Write-bypass tests covered by v_p0_write_bypass_uwg / mv_write_sovereignty_paths |
| `tests/unit/agentic_core/L5_safety/validators/test_PascalSovereigntyAgent.py` | Write-bypass tests covered by v_p0_write_bypass_uwg / mv_write_sovereignty_paths |
| `tests/unit/apps_rg/utils/test_anthropic_rag_entrypoint.py` | Entrypoint tests covered by A6 / module_entrypoints |
| `tests/unit/agentic_core/L5_safety/reasoning/test_gravity_and_ssot_reconciler_behavior.py` | Gravity tests covered by v_p0_apps_direct_infra / v_p1_mis_layered_infra |
| `tests/unit/agentic_core/L5_safety/validators/test_gravity_leak_validator.py` | Gravity tests covered by v_p0_apps_direct_infra / v_p1_mis_layered_infra |
| `tests/unit/agentic_core/L5_safety/reasoning/test_gravity_validator.py` | Gravity tests covered by v_p0_apps_direct_infra / v_p1_mis_layered_infra |
| `tests/unit/agentic_core/L5_safety/validators/test_gravity_validator.py` | Gravity tests covered by v_p0_apps_direct_infra / v_p1_mis_layered_infra |
| `tests/unit/agentic_core/L5_safety/utils/test_gravity_visitor_util.py` | Gravity tests covered by v_p0_apps_direct_infra / v_p1_mis_layered_infra |
| `tests/unit/agentic_core/L4_state/utils/test_layer_gravity_util.py` | Gravity tests covered by v_p0_apps_direct_infra / v_p1_mis_layered_infra |
| `tests/unit/agentic_core/L5_safety/enforcement/test_layer_sovereignty_enforcer.py` | Write-bypass tests covered by v_p0_write_bypass_uwg / mv_write_sovereignty_paths |
| `tests/unit/agentic_core/L6_observability/enforcement/test_mcp_drift_hardening.py` | MCP-sync tests covered by R6 mcp_contract_drift |
| `tests/unit/agentic_core/L2_execution/reasoning/test_replay_shim_eq6.py` | Shim tests covered by R6 mv_rename_shim_consumers |
| `tests/unit/apps_eval/test_telemetry_shim.py` | Shim tests covered by R6 mv_rename_shim_consumers |
