# Exhaustive ADG CI Report

- **Generated:** 2026-04-28T19:29:02+00:00
- **Snapshot SQLite:** `adg_indexed_04282026_1505.sqlite` (412,590,080 bytes)
- **Snapshot source:** extracted
- **Gate results:** `artifacts\adg\adg_gate_results_20260428_191222.json`
- **Burndown table:** `C:\Git\Agentic-Workflow\_tmp_extract\run\adg\adg_burndown_table.json`
- **Dispatcher overall verdict:** **BLOCKED**

## 1. Executive Summary

**Severity bands** (from `adg_burndown_table.json`):

| Band | Label | Gross | Guardian | Net | Diff |
|------|-------|------:|---------:|----:|-----:|
| P0 | layer_violations | 0 | 0 | 0 | +0 |
| P1 | anti_patterns_high | 0 | 0 | 0 | +0 |
| P2 | anti_patterns_medium | 0 | 0 | 0 | +0 |
| P3 | style_warnings | 1 | 0 | 1 | +0 |

**Dispatcher gates** (from `adg_gate_results_*.json`):

- block_pass: **7** | block_fail: **8** | ratchet_pass: **26** | ratchet_regressed: **1** | warn: **6**
- Total dispatcher gates: **48**

**Snapshot surface inventory:**

- Materialized views (`mv_*`): **52**
- P-views (`v_p0..v_p3`): **15**
- Other analytical views: **17**
- Core tables: **20**

## 2. Dispatcher Gates (48)

Every gate registered in `ops_scripts/ci/adg_gates/run.py`. Enforcement contract: **block** = any violation fails the run; **ratchet** = only NEW violations beyond baseline fail; **warn** = advisory.

| Gate ID | Band | Enf | Status | Violations | Owner |
|---------|:----:|:---:|:------:|-----------:|:-----:|
| `10_infra_wiring` | P0 | block | FAIL | 9 | adg_gates |
| `2_authority_boundary` | P0 | block | FAIL | 17 | adg_gates |
| `3_write_sovereignty` | P0 | block | FAIL | 1,454 | adg_gates |
| `4_capability_egress` | P0 | block | FAIL | 2 | adg_gates |
| `C1_uwg_bypass_pview` | P0 | block | FAIL | 1 | wiring_ci |
| `C2_l5_bypass_pview` | P0 | block | FAIL | 1 | wiring_ci |
| `J1_canonical_pipeline_wiring` | P0 | block | FAIL | 6 | wiring_ci |
| `1_critical_path_integrity` | P0 | block | PASS | 0 | adg_gates |
| `5_text_to_action` | P0 | block | PASS | 0 | adg_gates |
| `6_determinism_provenance` | P0 | block | PASS | 0 | adg_gates |
| `9_executor_theater` | P0 | block | PASS | 0 | adg_gates |
| `G_REACH_l0_reachability` | P0 | ratchet | PASS | 2,181 | wiring_ci |
| `L2_lpg_drift_ratchet` | P0 | ratchet | PASS | 20 | wiring_ci |
| `S2_uwg_bypass_ratchet` | P0 | ratchet | PASS | 2,728 | wiring_ci |
| `W5_waiver_expiry` | P0 | block | PASS | 0 | wiring_ci |
| `G2_seam_test_export_coherence` | P1 | block | FAIL | 6 | wiring_ci |
| `8_trace_replay_eval` | P1 | ratchet | REGR | 593 | adg_gates |
| `11_architecture_witness` | P1 | block | PASS | 0 | adg_gates |
| `12_prompt_assembly_wiring` | P1 | block | PASS | 0 | adg_gates |
| `7_lifecycle_coverage` | P1 | ratchet | PASS | 0 | adg_gates |
| `B2_layer_skip_ratchet` | P1 | ratchet | PASS | 871 | wiring_ci |
| `C3_silent_writes_ratchet` | P1 | ratchet | PASS | 1,630 | wiring_ci |
| `C4_policy_without_audit_ratchet` | P1 | ratchet | PASS | 1 | wiring_ci |
| `E1_trace_stub_module` | P1 | ratchet | PASS | 1,143 | wiring_ci |
| `G_ISLAND_connected_components` | P1 | ratchet | PASS | 0 | wiring_ci |
| `G_WATCHLIST_DELTA_hotspot_regressions` | P1 | ratchet | PASS | 0 | wiring_ci |
| `H1_new_orphans_delta_ratchet` | P1 | ratchet | PASS | -1 | wiring_ci |
| `H2_fanin_collapse_ratchet` | P1 | ratchet | PASS | -1 | wiring_ci |
| `I1_exit_disposition_ratchet` | P1 | ratchet | PASS | 692 | wiring_ci |
| `M_taint_actionable_ratchet` | P1 | ratchet | PASS | 373 | wiring_ci |
| `N_guardrail_separation_ratchet` | P1 | ratchet | PASS | 464 | wiring_ci |
| `O_tool_call_parity_ratchet` | P1 | ratchet | PASS | 182 | wiring_ci |
| `P_structured_output_ratchet` | P1 | ratchet | PASS | 1 | wiring_ci |
| `A3_dead_public_symbol_ratchet` | P2 | ratchet | PASS | 1 | wiring_ci |
| `C5_unresolved_callsites_ratchet` | P2 | ratchet | PASS | 0 | wiring_ci |
| `D2_role_duplication_warn` | P2 | warn | PASS | 76 | wiring_ci |
| `F1_untyped_seam_ratchet` | P2 | ratchet | PASS | 981 | wiring_ci |
| `F2_broken_contract_ratchet` | P2 | ratchet | PASS | 0 | wiring_ci |
| `H4_mv_staleness_ratchet` | P2 | ratchet | PASS | 0 | wiring_ci |
| `I2_replay_surface_gaps_ratchet` | P2 | ratchet | PASS | 1,109 | wiring_ci |
| `D1_layer_doc_binding` | P3 | warn | PASS | 3 | wiring_ci |
| `E3_trace_theater_kpi` | P3 | warn | PASS | 0 | wiring_ci |
| `F3_missing_adapter_warn` | P3 | warn | PASS | 0 | wiring_ci |
| `H3_ap_velocity_kpi` | P3 | warn | PASS | 0 | wiring_ci |
| `K1_churn_complexity_kpi` | P3 | warn | PASS | 0 | wiring_ci |
| `M1_module_loc_ratchet` | P3 | ratchet | PASS | 356 | wiring_ci |
| `Q2_cyclomatic_complexity_ratchet` | P3 | ratchet | PASS | 481 | wiring_ci |
| `S4_unused_imports_ratchet` | P3 | ratchet | PASS | 7,937 | wiring_ci |

## 3. Materialized Views (mv_*)

Pre-computed analytical tables built by `tools/generate/materialized_views/` during every ADG run. The graph layer (constitutional §22) requires plans to cite these views as primary evidence.

| View | Rows | Description | Finding |
|------|-----:|-------------|---------|
| `mv_actionable_surface_without_schema` | 457 | Action-class tools published without a JSON Schema contract. | 457 action-class tools lack a schema — schema-less tool calls cannot be validated at the spine. |
| `mv_agent_specialization_overlap` | 2,497 | Agent classes whose specializations overlap (potential dedup target). | 2,497 overlapping agent specializations. |
| `mv_agent_tool_ratio` | 16 | Tools-per-agent ratio per agent class. | 16 agent classes scored for tool ratio. |
| `mv_authority_boundary_breaches` | 17 | L0/L_PG calls that cross authority boundaries other than UWG/spine. | 17 authority-boundary breaches — block-class P0 fail at this count. |
| `mv_capability_and_egress_gaps` | 1 | Outbound provider/SDK calls that bypass the sanctioned capability adapter. | 1 egress paths bypass capability adapters — silent provider sprawl risk. |
| `mv_critical_path_segments` | 183 | Edges that participate in any critical execution path (run → seal → disposition). | 183 edges on the critical path — these are the high-blast-radius edges. |
| `mv_cross_cutting_witness_tiers` | 56 | Tier-1 emit-site witness sites broken down by cross-cutting concern. | 56 witness-tier sites — cross-cutting coverage of trace_root / step.seal / disposition. |
| `mv_debt_concentration_hotspots` | 2,647 | Modules with concentrated technical debt (multiple SC/AP defects in one file). | 2,647 debt-concentrated modules — top targets for refactoring waves. |
| `mv_dependency_cone_risk` | 8,085 | Forward dependency cone (transitive imports) per node, weighted by criticality. | 8,085 nodes scored for dependency-cone risk — used to rank refactor blast-radius. |
| `mv_determinism_provenance_drift` | 4,821 | Trace_root emit sites missing determinism digest or replay key. | 4,821 emit sites with provenance drift — replay/reproduction may be incomplete. |
| `mv_digest_reconciliation` | 6 | Snapshot-to-snapshot digest reconciliation per pipeline phase. | 6 digest reconciliation rows — phase-level integrity check. |
| `mv_eval_coverage_by_path` | 13 | Eval coverage rolled up per repo path. | 13 paths reported — eval coverage by file area. |
| `mv_exemptions_near_critical_paths` | 2,148 | Guardian exemptions located on or adjacent to critical paths. | 2,148 exemptions touch critical paths — high-priority audit candidates. |
| `mv_exit_disposition_coverage` | 768 | Tier-1 Exit.disposition emit-site coverage per layer. | 768 layers tracked for Exit.disposition coverage. |
| `mv_gateway_bypass_paths` | 1 | Code paths that mutate state without crossing the L4 UWG. | 1 gateway-bypass paths — direct write sovereignty violation. |
| `mv_graph_chokepoint_bridges` | 1,857 | Edges whose removal would disconnect a layer subgraph. | 1,857 chokepoint bridges — single points of layer-connectivity failure. |
| `mv_graph_critical_path_blast_radius` | 47 | Per-symbol blast radius if removed from the critical path. | 47 symbols ranked by critical-path blast radius — refactor priority signal. |
| `mv_graph_reverse_dependency_hotspots` | 38 | Top reverse-dependency centrality (most-imported-from symbols). | 38 reverse-dep hotspots — bottom-up dependency hubs. |
| `mv_graph_scc_clusters` | 0 | Strongly-connected components in the import graph (cycles). | 0 SCCs — non-zero values mean import cycles exist. |
| `mv_graph_vs_report_mismatches` | 1 | Disagreements between graph-derived facts and downstream reports. | 1 graph/report mismatches — non-zero values undermine the canonical-truth invariant. |
| `mv_handoff_witness_tiers` | 17 | Layer-handoff witness coverage (L1→L2, L2→L3, etc.). | 17 handoff witnesses — each is a layer-boundary observability checkpoint. |
| `mv_heal_retry_exit_gaps` | 64 | Healing-loop exit paths missing an Exit.disposition emit site. | 64 healing exits without disposition — silent recovery paths. |
| `mv_high_fan_in_out_with_defects` | 7,163 | Symbols with high fan-in OR fan-out AND at least one SC/AP defect. | 7,163 high-fanout/-fanin defective symbols — refactor priority by impact. |
| `mv_hitl_reclearance_gaps` | 1,597 | Author-Gate / runtime HITL flows missing the modify-then-reclear edge. | 1,597 HITL re-clearance gaps — incomplete approval chains. |
| `mv_hotspot_centrality` | 8,085 | Hotspot ranking by graph centrality (PageRank / betweenness blend). | 8,085 centrality-ranked hotspots — primary input to refactor wave order. |
| `mv_hotspot_coverage_risk` | 3,433 | Hotspots × test-coverage cross-join with priority bands (P1..P5). | 3,433 hotspots scored on coverage risk — used by hotspot_coverage_report.py. |
| `mv_l2_phase_coverage` | 5 | L2 execution phase coverage (capability / call / seal / dispatch). | 5 phases tracked for L2 coverage — execution layer observability. |
| `mv_live_future_mutation_conflicts` | 0 | State writes that may race with future mutations on the same key. | 0 mutation conflicts — non-zero values indicate write-write race risk. |
| `mv_local_heal_first_breaches` | 0 | Healing actions that escaped local heal-first containment. | 0 local-first breaches — healing escalated past intended scope. |
| `mv_manager_sprawl` | 101 | Manager / Orchestrator class proliferation per layer. | 101 manager classes — high values often signal orchestration sprawl. |
| `mv_modified_area_regressions` | 2,699 | SC/AP defects whose source location intersects this run's modified files. | 2,699 modified-area regressions — defects in code touched this run. |
| `mv_new_cross_layer_dependencies` | 168 | Cross-layer imports introduced since the previous snapshot baseline. | 168 new cross-layer deps — delta vs prev snapshot. |
| `mv_new_provider_surfaces` | 32 | Provider/SDK surfaces that appeared since the previous snapshot. | 32 new provider surfaces — drift watch. |
| `mv_new_write_bypass_paths` | 1,454 | Write-bypass paths flagged as 'new' (severity ∈ {critical, warning}). | 1,454 write-bypass paths flagged new — block-class trigger for P0 write_sovereignty gate. |
| `mv_newly_introduced_critical_paths` | 5,407 | Critical-path edges introduced since previous snapshot baseline. | 5,407 newly-introduced critical paths — delta drives P0 regressions. |
| `mv_observability_interference_breaches` | 0 | Observability code that interferes with the production code path. | 0 observability interference breaches — non-zero is a §6 invariant violation. |
| `mv_path_criticality_rollup` | 8,085 | Rolled-up criticality score per node across all critical-path memberships. | 8,085 nodes with criticality scores — the impact-ordering primitive. |
| `mv_prompt_assembly_wiring_gaps` | 17 | Wiring gaps in the prompt assembly path (S0/D0/I0/C0/U0 slots). | 17 prompt-assembly wiring gaps — block-class P1 trigger when >0. |
| `mv_provider_surface_sprawl` | 26 | Provider SDK surface area (distinct callable symbols per provider). | 26 provider surface entries — sprawl monitor. |
| `mv_repeated_p3_near_critical_paths` | 967 | P3 style warnings that repeatedly land on or near critical paths. | 967 P3 sites near critical paths — promotion candidates to P2. |
| `mv_replay_surface_gaps` | 1,109 | Replay-surface coverage gaps (state reads/writes not observable). | 1,109 replay-surface gaps — unobservable mutations. |
| `mv_runtime_spine_gaps` | 7 | Runtime-spine emit sites missing from the live OTEL pipeline. | 7 runtime-spine gaps — Tier-1 telemetry blind spots. |
| `mv_snapshot_baseline` | 1 | Anchor row for the current snapshot (one row per run). | 1 baseline anchor row — used by all delta-class gates. |
| `mv_snapshot_integrity_anomalies` | 261,552 | Anomalies in the snapshot itself (orphan ids, dup rows, schema drift). | 261,552 snapshot integrity anomalies — high values indicate ingest-side bugs. |
| `mv_snapshot_regression_summary` | 1 | Aggregate delta vs previous baseline (one row). | 1 regression-summary row — see fields for per-metric deltas. |
| `mv_structured_output_gaps` | 3 | Tool calls missing structured-output schema validation. | 3 structured-output gaps — silent shape drift risk. |
| `mv_task_contract_gaps` | 1,109 | Task contracts (entry → exit shape) that are incomplete. | 1,109 task-contract gaps — incomplete shape declarations at task boundaries. |
| `mv_tool_surface_overlap` | 0 | Tool capabilities exposed by multiple adapters (overlap risk). | 0 overlapping tool surfaces — consolidation candidates. |
| `mv_trace_replay_eval_gaps` | 580 | Trace-replay eval coverage gaps (paths where replay would skip). | 580 replay/eval gaps — feeds 8_trace_replay_eval ratchet. |
| `mv_unknown_taxonomy_and_orphans` | 4,821 | Symbols that did not classify into any taxonomy bucket. | 4,821 unclassified symbols — gardening backlog. |
| `mv_untrusted_text_to_action_risk` | 0 | User text reaching action-class tools without prompt-governance gating. | 0 text-to-action risk paths — non-zero is a P0 fail in 5_text_to_action. |
| `mv_write_sovereignty_paths` | 1,521 | Every state-write path with severity classification. | 1,521 total write paths — feeds 3_write_sovereignty gate. |

## 4. P-Views (v_p0_* … v_p3_*)

Pre-classified architectural concerns by priority band. P0 rows are block-class — any non-zero count fails the run unless guardian-exempted.

| View | Rows | Description | Finding |
|------|-----:|-------------|---------|
| `v_p0_apps_direct_infra` | 0 | P0: apps_* directly imports infrastructure/* (forbidden). | 0 apps_*→infra direct imports — must be 0 (block-class). |
| `v_p0_l0_raw_execution` | 3 | P0: L0 invokes raw execution without going through the orchestrator. | 3 L0-raw-execution sites — must be 0 (block-class). |
| `v_p0_l1_direct_infra` | 0 | P0: L1 cognition imports infrastructure directly. | 0 L1→infra direct imports — must be 0. |
| `v_p0_l6_mutation` | 0 | P0: L6 observability code mutates production state. | 0 L6 mutations — must be 0 (observability must not interfere). |
| `v_p0_provider_bypass` | 0 | P0: provider call that bypasses the capability adapter. | 0 provider bypasses — must be 0 (block-class). |
| `v_p0_write_bypass_uwg` | 1 | P0: state write that does not flow through the L4 UWG. | 1 UWG bypasses — must be 0 (block-class). |
| `v_p1_ad_hoc_imports` | 0 | P1: ad-hoc imports of internal modules (not through SSOT seam). | 0 ad-hoc imports — promotion candidates if persistent. |
| `v_p1_mis_layered_infra` | 0 | P1: infrastructure module placed in the wrong layer. | 0 mis-layered infra modules. |
| `v_p1_not_on_spine` | 1 | P1: emit site or seam declared but not reachable from the spine. | 1 non-spine sites — orphan declarations. |
| `v_p1_raw_http_outside_seam` | 0 | P1: raw HTTP call outside the sanctioned HTTP seam. | 0 raw-HTTP outside seam — provider-egress drift. |
| `v_p1_zero_caller_infra` | 1 | P1: infrastructure module with zero callers (dead infra). | 1 zero-caller infra modules — archive candidates. |
| `v_p2_dormant_ambiguous` | 0 | P2: declarations that are dormant AND ambiguous (cannot tell if dead or planned). | 0 dormant-ambiguous sites. |
| `v_p2_duplicated_adapters` | 3 | P2: adapters that duplicate each other's capability. | 3 duplicated adapter pairs. |
| `v_p2_mixed_usage` | 3 | P2: symbols used both inside and outside their declared layer. | 3 mixed-usage symbols. |
| `v_p3_isolated_experimental` | 4 | P3: experimental code with no production reach. | 4 isolated experimental modules — informational only. |

## 5. Other Analytical Views

| View | Rows | Description |
|------|-----:|-------------|
| `edge_view` | 721,284 | Pre-joined edges×nodes×layers projection (read path for analytics). |
| `mv_async_fire_and_forget_hotspots` | 5 | Async tasks launched without retention (potential lost futures). |
| `mv_boundary_string_unresolved` | 1,142 | String-typed boundary references that the resolver could not bind. |
| `mv_dead_import_hotspots_overlay` | 318 | Imports that resolve but whose target is never used. |
| `mv_entrypoint_kind_summary` | 6 | (no description registered yet) |
| `mv_external_calls_no_timeout` | 0 | External calls without a `timeout=` argument (constitutional §14). |
| `mv_hidden_writes_overlay` | 455 | Writes through indirection layers (proxies, getattr, exec). |
| `mv_mcp_contract_drift` | 0 | MCP tool declarations that no longer match the canonical contract. |
| `mv_module_duplicate_clusters_overlay` | 12 | Modules whose AST signatures match — duplication candidates. |
| `mv_module_load_action_calls_overlay` | 1,710 | Action-class calls invoked at module-load time (side-effect at import). |
| `mv_overlay_debt_summary` | 15 | Per-overlay summary of detected debt items. |
| `mv_r6_summary` | 1 | R6 review cycle aggregate row (one row, snapshot-scoped). |
| `mv_rename_shim_consumers` | 5 | Consumers still importing through deprecation re-export shims. |
| `mv_truth_expansion_summary` | 1 | Truth-table expansion / canonical inference one-row summary. |
| `mv_unresolved_config_refs` | 95 | Env/config references the resolver could not bind to a declaration. |
| `precision_metrics_view` | 1 | Precision-pass metrics (variable attributes, side effects, callsite resolution). |
| `v_infra_violations_summary` | 4 | Infra-imports violations rolled up by class. |

## 6. Core Tables

| Table | Rows | Description |
|-------|-----:|-------------|
| `async_fire_and_forget` | 6 | Async-task launches with no retention/await (fire-and-forget instances). |
| `boundary_strings` | 2,848 | All string literals participating in module/symbol boundary references. |
| `config_references` | 1,184 | Every env/config flag read in the codebase (input to check_config_references). |
| `coverage_by_path` | 19 | coverage.py data ingested per repo path. |
| `edges` | 721,284 | Canonical edge table (imports / calls / writes / flows_to / etc.). |
| `external_calls` | 0 | External (provider/SDK/HTTP) call sites (input for capability_egress checks). |
| `gate_self_consistency` | 107 | Per-gate self-consistency probe rows (gate-of-gates). |
| `mcp_config_servers` | 14 | .windsurf/mcp_config.json declared servers. |
| `mcp_tool_declarations` | 85 | All @mcp.tool decorated functions ingested per MCP server. |
| `meta` | 8 | Snapshot meta (commit_sha, timestamp, generator version). |
| `module_entrypoints` | 8,646 | Every module-level entrypoint with classification (test / cli / api / service). |
| `module_origins` | 8,646 | Per-module origin classification (production / test / tool / archive). |
| `nodes` | 115,504 | Canonical node table (modules + symbols + classes + functions). |
| `overlay_violations` | 118,399 | Violations recorded by overlay analyses (vs canonical violations). |
| `side_effect_calls` | 134,376 | Call sites flagged as side-effecting (writes / IO / network / import-time). |
| `snapshot_metadata` | 6 | Per-snapshot bookkeeping (one row per run). |
| `sqlite_sequence` | 10 | SQLite internal AUTOINCREMENT bookkeeping. |
| `t_infra_importers` | 533 | Modules that import infrastructure namespaces (input to v_p0_apps_direct_infra). |
| `test_stubs` | 844 | Discovered pytest test_* functions (input to test_harness_coverage). |
| `violations` | 8,788 | Canonical violations table — the SC/AP burndown source. |

## 7. Wiring CI Ratchet Baselines

Per-gate ceiling files in `ops_scripts/ci/baselines/wiring_*_ratchet.json`. `count` is the absorbed floor; `tighten_history` records pay-down events; `loosen_history` (added 2026-04-28) records floor-absorb events.

| Baseline | Gate ID | Count | Last Tightened | Last Loosened |
|----------|---------|------:|----------------|---------------|
| `wiring_broken_contract_ratchet.json` | `F2_broken_contract_ratchet` | 0 | — | — |
| `wiring_cyclomatic_complexity_ratchet.json` | `Q2_cyclomatic_complexity_ratchet` | 481 | 2026-04-28T19:12:10.886420+00:00 | 2026-04-28T19:05:38+00:00 |
| `wiring_dead_folder_detector_ratchet.json` | `D_dead_folder_detector` | 0 | 2026-04-24T02:32:21.534650+00:00 | — |
| `wiring_dead_methods_ratchet.json` | `A3B_dead_methods_in_live_classes_ratchet` | 606 | 2026-04-24T02:32:20.533778+00:00 | — |
| `wiring_dead_symbol_ratchet.json` | `A3_dead_public_symbol_ratchet` | 1 | — | 2026-04-28T18:49:35+00:00 |
| `wiring_exit_disposition_ratchet.json` | `I1_exit_disposition_ratchet` | 692 | 2026-04-23T22:30:14.645374+00:00 | 2026-04-28T18:49:35+00:00 |
| `wiring_fanin_collapse_ratchet.json` | `H2_fanin_collapse_ratchet` | 0 | — | — |
| `wiring_graph_island_ratchet.json` | `G_ISLAND_connected_components` | 0 | — | — |
| `wiring_graph_reach_archival_ratchet.json` | `G_REACH_ARCHIVAL_orphans` | 1,480 | 2026-04-24T02:31:03.915541+00:00 | — |
| `wiring_graph_reach_ratchet.json` | `G_REACH_l0_reachability` | 2,181 | 2026-04-23T22:30:21.998576+00:00 | 2026-04-28T18:49:35+00:00 |
| `wiring_graph_watchlist_delta_ratchet.json` | `G_WATCHLIST_DELTA_hotspot_regressions` | 0 | — | — |
| `wiring_guardrail_separation_ratchet.json` | `N_guardrail_separation_ratchet` | 464 | 2026-04-24T14:30:40.493181+00:00 | 2026-04-28T18:49:35+00:00 |
| `wiring_layer_skip_ratchet.json` | `B2_layer_skip_ratchet` | 871 | 2026-04-23T22:30:08.713325+00:00 | 2026-04-28T18:49:35+00:00 |
| `wiring_lpg_drift_ratchet.json` | `L2_lpg_drift_ratchet` | 20 | — | 2026-04-28T18:49:35+00:00 |
| `wiring_module_loc_ratchet.json` | `M1_module_loc_ratchet` | 356 | 2026-04-23T22:21:52.107076+00:00 | 2026-04-28T18:49:35+00:00 |
| `wiring_mv_staleness_ratchet.json` | `H4_mv_staleness_ratchet` | 0 | — | — |
| `wiring_new_orphans_delta_ratchet.json` | `H1_new_orphans_delta_ratchet` | 0 | — | — |
| `wiring_policy_without_audit_ratchet.json` | `C4_policy_without_audit_ratchet` | 1 | — | — |
| `wiring_replay_surface_gaps_ratchet.json` | `I2_replay_surface_gaps_ratchet` | 1,109 | 2026-04-28T19:12:11.029859+00:00 | 2026-04-28T19:05:38+00:00 |
| `wiring_silent_writes_ratchet.json` | `C3_silent_writes_ratchet` | 1,630 | 2026-04-28T19:12:10.922189+00:00 | 2026-04-28T19:05:38+00:00 |
| `wiring_structured_output_ratchet.json` | `P_structured_output_ratchet` | 1 | — | — |
| `wiring_taint_actionable_ratchet.json` | `M_taint_actionable_ratchet` | 373 | 2026-04-28T19:12:11.180065+00:00 | 2026-04-28T19:05:38+00:00 |
| `wiring_tool_call_parity_ratchet.json` | `O_tool_call_parity_ratchet` | 182 | 2026-04-23T18:44:02.430696+00:00 | 2026-04-28T18:49:35+00:00 |
| `wiring_trace_stub_ratchet.json` | `E1_trace_stub_module` | 1,143 | 2026-04-28T10:59:54.822861+00:00 | — |
| `wiring_unresolved_callsites_ratchet.json` | `C5_unresolved_callsites_ratchet` | 0 | — | — |
| `wiring_untyped_seam_ratchet.json` | `F1_untyped_seam_ratchet` | 981 | 2026-04-23T22:30:14.799626+00:00 | 2026-04-28T18:49:35+00:00 |
| `wiring_unused_imports_ratchet.json` | `S4_unused_imports_ratchet` | 7,937 | 2026-04-28T19:12:03.380676+00:00 | 2026-04-28T19:05:38+00:00 |
| `wiring_uwg_bypass_ratchet.json` | `S2_uwg_bypass_ratchet` | 2,728 | 2026-04-28T19:12:03.338352+00:00 | 2026-04-28T19:05:38+00:00 |

## 8. File-Counter Gate Baselines

Baselines for the three legacy-debt ratchet gates (`config_references`, `lifecycle_pairs`, `hardcoded_exclusions`). These gates use a flat list of locked-in known issues; new issues fail the run.

| Baseline | Tracked Items | Description |
|----------|--------------:|-------------|
| `config_references_baseline.json` | 222 | env-flag reads not declared in `.env.example` (legacy debt). |
| `lifecycle_pairs_baseline.json` | 270 | open-without-close lifecycle leaks (legacy debt). |
| `hardcoded_exclusions_baseline.json` | 13 | hardcoded path/pattern exclusions outside `config/excluded_paths.yaml`. |

## 9. Supplementary Snapshot Reports

Each ADG run emits a fixed family of analytical JSONs alongside the SQLite. These are interpretive summaries that the materialized views feed.

| Report | Findings |
|--------|----------|
| `closure_validation_report_04282026_1505.json` | summary keys=3, closure_rows=13, determinism keys=11, semantic_precision keys=23 |
| `edge_density_report_04282026_1505.json` | total_edges=721,284, density_metrics keys=3, critical-edge keys=7, edge_distribution buckets=82 |
| `layer_coverage_report_04282026_1505.json` | total_modules=115,475, unknown_modules=50, layers=17, coverage_metrics keys=3 |
| `adg_runtime_spine_04282026_1505.json` | emit_sites=0, gaps=0 |
| `adg_refactor_accelerator_04282026_1505.json` | recommendations=0 |
| `provenance_report_04282026_1505.json` | top-level keys: ['artifact_digest', 'commit_sha', 'generation_metrics', 'reconciliation', 'repo_state_hash', 'scanner_digest', 'schema_version', 'timestamp', 'validation'] |
| `adg_graph_watchlist_20260428_151243.json` | items=30 |
| `adg_anomaly_watchlist_20260428_151243.json` | items=50 |
| `p0_remediation_wave_plan_04282026_1505.json` | waves=3, clean_snapshot=False |

## 10. Antipattern Ratchet State (P1 / P2)

- **P1 antipattern ratchet** (`p1_ratchet.json`): high_severity_ceiling=155, _recalibration_note=Bumped from 80 to 155 in commit addressing NEXT_STEP `adg-p1-ratchet-drift-investigation`. The +75 delta is not new bad code: the prior 80 ceiling was set before (a) the Surface-Override classifier promoted ~48 P2/P3 rows to P1 (per ADR-024 Part B) and (b) new graph-layer materialized views (mv_hotspot_centrality, mv_dependency_cone_risk, mv_path_criticality_rollup) classify additional structural risks as HIGH. Confirmed via the ADG run on 04282026_0933 against artifacts/adg/_archive/2026-04/adg_run_04282026_0933.zip.gz: severity histogram CRITICAL=16, HIGH=155, MEDIUM=8 (=ceiling, stable), LOW=8478. Future regressions surface immediately because the ratchet now anchors at 155., _recalibration_date=2026-04-28, _prior_ceiling=80
- **P2 antipattern ratchet** (`p2_ratchet.json`): exception_swallow_ceiling=8

## 11. Top Blockers (Failing or Regressed)

| Gate | Band | Enf | Violations | Owner |
|------|:----:|:---:|-----------:|:-----:|
| `3_write_sovereignty` | P0 | block | 1,454 | adg_gates |
| `8_trace_replay_eval` | P1 | ratchet | 593 | adg_gates |
| `2_authority_boundary` | P0 | block | 17 | adg_gates |
| `10_infra_wiring` | P0 | block | 9 | adg_gates |
| `J1_canonical_pipeline_wiring` | P0 | block | 6 | wiring_ci |
| `G2_seam_test_export_coherence` | P1 | block | 6 | wiring_ci |
| `4_capability_egress` | P0 | block | 2 | adg_gates |
| `C1_uwg_bypass_pview` | P0 | block | 1 | wiring_ci |
| `C2_l5_bypass_pview` | P0 | block | 1 | wiring_ci |

## 12. Provenance & Counting Mode

| Field | Value |
|-------|-------|
| `counting_mode` | violations_plus_exempted_edge_inference |
| `generator_module` | tools.generate.reporting.reports._print_defect_table |
| `historical_interpretation_note` | defensible broad trend is ~1254 to 631; single-tranche ~623 attribution is not proven |
| `p0_includes_antipattern_critical` | True |
| `severity_band_ssot` | agentic_core.adg.severity_bands |
| `source_mismatch_with_latest` | False |
| `sqlite_source_name` |  |
| `sqlite_source_path` |  |
| `sqlite_source_timestamp` |  |

---
Renderer: `tools/reports/exhaustive_adg_ci_report.py`. Re-run: `python tools/reports/exhaustive_adg_ci_report.py`.
