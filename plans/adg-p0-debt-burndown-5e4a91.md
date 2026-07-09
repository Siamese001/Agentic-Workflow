# ADG P0 Debt Burndown

> **plan_id**: `adg-p0-debt-burndown-5e4a91` — wave markers use `plan=adg-p0-debt-burndown-5e4a91`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W282
LAST_COMPLETED_WAVE: W281
LAST_UPDATED: 2026-07-09

PLAN_CREATED: plan=adg-p0-debt-burndown-5e4a91 slug=adg-p0-debt-burndown-5e4a91 status="In Progress"

---

## Scope

Reduce the current P0 tracked debt inventory instead of hiding it as report-only
telemetry. The starting point is snapshot `adg_indexed_07082026_2319.sqlite`
and gate results `adg_gate_results_20260709_033256.json`.

Starting P0 tracked rows:

| Gate | Rows | Why P0 |
| --- | ---: | --- |
| `G_REACH_l0_reachability` | 1450 | Core production modules not reachable from L0 entrypoints can indicate detached runtime authority. |
| `S2_uwg_bypass_ratchet` | 755 | Write paths bypassing UWG weaken durable-write auditability and replay guarantees. |
| `3_write_sovereignty` | 765 | Non-UWG durable write inventory is the source surface underneath S2. |
| `J1_canonical_pipeline_wiring` | 1 | Canonical pipeline declarations must match live wiring. |

Total visible P0 tracked debt: 2971 rows.

## Burndown Policy

`P0_FIX` and released `P0_WAVE` rows still stop the line. P0 tracked rows are
also real P0 debt, but they are burned down through owned waves with explicit
targets, not by pretending every row can be repaired safely in one patch.

Target sequence:

1. Reduce `2971 -> <= 2037` by removing confirmed scanner false positives
   and non-durable generated-artifact writer rows from the write-sovereignty
   MV producer.
2. Reduce `<= 2037 -> <= 2000` by promoting high-confidence write-sovereignty
   clusters into owned source-routing waves.
3. Reduce `<= 2000 -> <= 1500` by addressing G_REACH clusters with real runtime
   ownership or approved deletion/deprecation.
4. Continue lowering floors only after source or MV proof reduces actual rows.

Waves 2-6 remove 224 rows on the released `07082026_2319` snapshot. Combined
with Wave 1's 53 rows, the projected post-regeneration tracked P0 inventory is
`2971 - 277 = 2694`.

Waves 7-16 remove 80 additional site-scoped rows on the released
`07082026_2319` snapshot. Combined with Waves 1-6, the projected
post-regeneration tracked P0 inventory is `2971 - 357 = 2614`.

Waves 17-116 remove 267 additional site-scoped rows on the released
`07082026_2319` snapshot. Combined with Waves 1-16, the projected
post-regeneration tracked P0 inventory is `2971 - 624 = 2347`.

Waves 117-281 remove 310 additional site-scoped rows on the released
`07082026_2319` snapshot. Combined with Waves 1-116, the projected
post-regeneration tracked P0 inventory is `2971 - 934 = 2037`.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0 | P0 tracked semantics | N/A | Handoff keeps `P0_TRACKED_BACKLOG=4` visible | DONE | P0 tracked rows remain burn-down backlog, not report-only KPI rows |
| W1 | W1 | Non-mutating write-symbol false positives | N/A | Helper symbols are scanner false positives | DONE | Synthetic MV test excludes helpers and keeps real writes visible |
| W2-W6 | W2-W6 | Initial site-scoped artifact writers | N/A | Exact sites are generated artifacts | DONE | Projected reduction reaches `2971 - 277 = 2694` |
| W7-W16 | W7-W16 | Additional site-scoped artifact writers | N/A | Exact sites are generated artifacts | DONE | Projected reduction reaches `2971 - 357 = 2614` |
| W17-W116 | W17-W116 | Exact artifact/output sites | N/A | Exact sites are generated artifacts or proof output | DONE | Projected reduction reaches `2971 - 624 = 2347` |
| W117-W281 | W117-W281 | Exact artifact/report/proof and false-positive sites | N/A | Safe pool is exact-site only; real stores are deferred | DONE | Projected reduction reaches `2971 - 934 = 2037`; 84 pairs remain deferred |
| W282 | W282 | Source routing for real write clusters | TBD | Requires ownership decisions for durable stores and logs | TODO | Real write clusters route through UWG or sanctioned layer authorities |
| W283 | W283 | G_REACH owned runtime wiring | TBD | Reachability repairs must map to real runtime paths | TODO | L0 reachability debt reduced without artificial imports |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0 | Restore P0 tracked semantics | DONE |
| W1 | Non-mutating write-symbol false positives | DONE |
| W2-W6 | Site-scoped artifact writers | DONE |
| W7-W16 | Follow-on exact site scopes | DONE |
| W17-W116 | Site-scoped artifact, proof, and output sites | DONE |
| W117-W281 | Site-scoped artifact, report, proof, and false-positive sites | DONE |
| W282 | Source routing for real write clusters | TODO |
| W283 | G_REACH owned runtime wiring | TODO |

## Waves

### Wave 0: Restore P0 Tracked Semantics

Goal: Keep P0 TRACK rows visible as burn-down backlog, not report-only KPI rows.

Files:

- `tools/reports/adg_bcg_adapter.py`
- `tools/adg/run_full_adg_audit.py`
- report and handoff count tests

Exit:

- Existing handoff counts remain compatible with `P0_TRACKED_BACKLOG=4`.
- Burndown reports put P0 TRACK rows in the BURN section.

### Wave 1: Non-Mutating Write-Symbol False Positives

Goal: Remove scanner false positives from `mv_write_sovereignty_paths`.

Symbols:

- `assert_no_persistent_write`
- `compute_content_hash`
- `get_bm25_store`
- `get_default_store`
- `get_validated_project_root`
- `is_commit_sandbox_active`

Expected reduction on `07082026_2319`: about 53 write-sovereignty rows.

Files:

- `tools/generate/materialized_views/phase_a_path_authority.py`
- `tests/unit/tools/generate/test_materialized_views_phase_a.py`

Exit:

- Synthetic MV test proves these helpers are excluded.
- Synthetic MV test proves `path.write_text` remains flagged.

### Wave 2: Non-Durable Artifact Writer Refinement

Goal: Reduce rows where the write target is an artifact/report/proof surface,
not durable agent state.

Symbols:

- `OUT_JSON.write_text`
- `OUT_MD.write_text`
- `CLOSEOUT_JSON.write_text`
- `CLOSEOUT_MD.write_text`
- `OUT_RECEIPT_JSON.write_text`
- `OUT_RECEIPT_MD.write_text`
- `P1_W5_RECEIPT_JSON.write_text`
- `P1_W5_RECEIPT_MD.write_text`
- `OUT_PATH.write_text`
- `DESIGN_PATH.write_text`

Expected reduction on `07082026_2319`: about 46 write-sovereignty rows.

Exit:

- Synthetic MV test proves these exact symbols are excluded.
- Synthetic MV test proves `path.write_text` remains flagged.

Stop condition: do not exclude source paths that write durable execution state,
ledgers, replay snapshots, or production memory.

### Wave 3: Receipt and Manifest Writer Refinement

Goal: Remove generated receipt/manifest/report metadata writes from the
write-sovereignty P0 inventory.

Symbols:

- `receipt_path.write_text`
- `receipt_json_path.write_text`
- `receipt_md_path.write_text`
- `p_receipt.write_text`
- `manifest_path.write_text`
- `man_path.write_text`
- `report_path.write_text`
- `meta_path.write_text`
- `mf_path.write_text`

Expected reduction on `07082026_2319`: about 50 write-sovereignty rows.

Exit:

- Synthetic MV test proves these exact symbols are excluded.
- Synthetic MV test proves `path.write_text` remains flagged.

Stop condition: do not exclude ledger/state writes or broad `*.write_text`
patterns.

### Wave 4: Output and Brief Writer Refinement

Goal: Remove generated output, summary, brief, and company-brief artifact
writers from the write-sovereignty P0 inventory.

Symbols:

- `json_path.write_text`
- `md_path.write_text`
- `out.write_text`
- `out_path.write_text`
- `out_md.write_text`
- `out_json.write_text`
- `output_path.write_text`
- `output_file.write_text`
- `brief_path.write_text`
- `briefing_path.write_text`
- `company_brief_path.write_text`
- `wizard_brief_path.write_text`
- `summary_path.write_text`

Expected reduction on `07082026_2319`: about 94 write-sovereignty rows.

Exit:

- Synthetic MV test proves these exact symbols are excluded.
- Synthetic MV test proves `path.write_text` remains flagged.

Stop condition: do not exclude broad output directories, app-owned runtime
state, or production memory writes.

### Wave 5: Factory and Process Scanner False Positives

Goal: Remove factory/process scanner hits that are not durable state writes.

Symbols:

- `create_artifact`
- `create_legacy_import_healer`
- `TraceFeatureRecord.from_bundle`
- `subprocess.Popen`

Expected reduction on `07082026_2319`: about 14 write-sovereignty rows.

Exit:

- Synthetic MV test proves these exact symbols are excluded.
- Synthetic MV test proves `path.write_text` remains flagged.

Stop condition: do not exclude real write APIs, subprocess call families, or
process output persistence.

### Wave 6: Proof Artifact Writer Refinement

Goal: Remove generated proof artifact writers that produce assertions,
coverage snapshots, requirements reports, RCA reports, contracts, baselines,
and local artifact evidence.

Symbols:

- `assertion_path.write_text`
- `coverage_path.write_text`
- `requirements_path.write_text`
- `rca_path.write_text`
- `rc_path.write_text`
- `contract_path.write_text`
- `baseline_file.write_text`
- `artifact_path.write_text`
- `artifact.write_text`

Expected reduction on `07082026_2319`: about 20 write-sovereignty rows.

Exit:

- Synthetic MV test proves these exact symbols are excluded.
- Synthetic MV test proves `path.write_text` remains flagged.

Stop condition: do not exclude durable baseline/state stores or non-evidence
contract writers.

### Wave 7: Runtime Envelope Artifact Sites

Goal: Remove integrated runtime NHSR/spine envelope artifact writes from the
write-sovereignty inventory without excluding those symbols globally.

Sites:

- `nhsr_path.write_text` in integrated runtime entrypoints
- `spine_path.write_text` in integrated runtime entrypoints

Expected reduction on `07082026_2319`: about 16 write-sovereignty rows.

Exit:

- Site-scoped MV test proves configured sites are excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Wave 8: C0 FEC Bridge Artifact Sites

Goal: Remove final-evidence-contract bridge and compatibility artifact writes
from the write-sovereignty inventory.

Sites:

- `p_bridge.write_text` in `apps_rg/runtime/spine/c0_fec_compose.py`
- `p_legacy.write_text` in `apps_rg/runtime/spine/c0_fec_compose.py`

Expected reduction on `07082026_2319`: about 6 write-sovereignty rows.

Exit:

- Site-scoped MV test proves configured sites are excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Wave 9: Runtime Exhaust Handoff Artifact Sites

Goal: Remove runtime-exhaust bundle and L6 handoff receipt artifacts from the
write-sovereignty inventory.

Sites:

- `p_bundle.write_text` in `apps_rg/runtime/section_runtime_exhaust_spine_receipt.py`
- `p_handoff.write_text` in `apps_rg/runtime/section_runtime_exhaust_spine_receipt.py`

Expected reduction on `07082026_2319`: about 4 write-sovereignty rows.

Exit:

- Site-scoped MV test proves configured sites are excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Wave 10: Section-One Certification Artifact Sites

Goal: Remove one-spine, proof-eligibility, and product-certification receipt
artifacts from the write-sovereignty inventory.

Sites:

- `p_cert.write_text` in `apps_rg/runtime/section_one_spine_certification.py`
- `p_pe.write_text` in `apps_rg/runtime/section_one_spine_certification.py`
- `p_pc.write_text` in `apps_rg/runtime/section_one_spine_certification.py`

Expected reduction on `07082026_2319`: about 6 write-sovereignty rows.

Exit:

- Site-scoped MV test proves configured sites are excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Wave 11: Front-Spine Contract Artifact Sites

Goal: Remove section-front, validated-request, L1 plan, and route contract
artifact writes from the write-sovereignty inventory.

Sites:

- `p_master.write_text` in `apps_rg/runtime/spine/front_contracts.py`
- `p_vr.write_text` in `apps_rg/runtime/spine/front_contracts.py`
- `p_l1.write_text` in `apps_rg/runtime/spine/front_contracts.py`
- `p_route.write_text` in `apps_rg/runtime/spine/front_contracts.py`

Expected reduction on `07082026_2319`: about 8 write-sovereignty rows.

Exit:

- Site-scoped MV test proves configured sites are excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Wave 12: L2 Evidence and Disposition Artifact Sites

Goal: Remove sealed L2, evidence digest, X1D, and X3 disposition artifact writes
from the write-sovereignty inventory.

Sites:

- `p_sealed.write_text` in `apps_rg/runtime/section_l2_spine_receipt.py`
- `sm_path.write_text` in `apps_rg/runtime/evidence/canonical_evidence_digest_chain.py`
- `x1d_path.write_text` in `apps_rg/runtime/assembly/full_resume_llm_coherence.py`
- `x3_path.write_text` in `apps_rg/runtime/internal/resume_package_disposition.py`

Expected reduction on `07082026_2319`: about 8 write-sovereignty rows.

Exit:

- Site-scoped MV test proves configured sites are excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Wave 13: Resume Diagnostic Artifact Sites

Goal: Remove generated-resume, provider snippet, and prior-resume variant
artifact writes from the write-sovereignty inventory.

Sites:

- `prod_out.write_text` in `apps_rg/l2_recipe/modular_resume_generation.py`
- `prod_out.write_text` in `apps_rg/runtime/orchestration/patch_run.py`
- `snip.write_text` in `apps_rg/l2_recipe/provider_run_diagnostics.py`
- `dest.write_text` in `apps_rg/runtime/c0/prior_resume_variant_extractor.py`

Expected reduction on `07082026_2319`: about 8 write-sovereignty rows.

Exit:

- Site-scoped MV test proves configured sites are excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Wave 14: Shadow and Spine Emission Artifact Sites

Goal: Remove runtime-exhaust reseal, synthesized spine context, L6 learning,
and non-authoritative proposal artifact writes from the write-sovereignty
inventory.

Sites:

- `bundle_path.write_text` in `apps_shared/spine_emission/reseal.py`
- `dst_path.write_text` in `apps_shared/spine_emission/context.py`
- `learning_path.write_text` in `apps_rg/runtime/shadow/competencies_l6.py`
- `proposals_path.write_text` in `apps_rg/runtime/shadow/competencies_l6.py`

Expected reduction on `07082026_2319`: about 8 write-sovereignty rows.

Exit:

- Site-scoped MV test proves configured sites are excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Wave 15: Research, Template, and Closeout Artifact Sites

Goal: Remove research run summaries, source registers, interactive templates,
offline traversal receipts, and graph-expansion closeout artifacts from the
write-sovereignty inventory.

Sites:

- `p.write_text` in `apps_research/reasoning/ResearchOrchestrator.py`
- `src_reg_path.write_text` in `apps_research/reasoning/ResearchOrchestrator.py`
- `input_path.write_text` in `apps_shared/cli/interactive_wizard.py`
- `receipt_json.write_text` in `apps_rg/fact_inventory/run_w14_senior_role_offline_traversal.py`
- `closeout_path.write_text` in `apps_rg/fact_inventory/track_weighted_graph_expansion.py`

Expected reduction on `07082026_2319`: about 10 write-sovereignty rows.

Exit:

- Site-scoped MV test proves configured sites are excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Wave 16: Site-Scoped Non-Write Helper False Positives

Goal: Remove call sites that read, route, or log in memory but were emitted by
the broad write-edge scanner.

Sites:

- `compute_replay_hash` in `agentic_core/L2_execution/types/vllm_replay_validator_types.py`
- `get_write_gateway` in `agentic_core/L2_execution/enforcement/write_governor_mixin.py`
- `self.log_event` in `apps_shared/utils/security_config_util.py`

Expected reduction on `07082026_2319`: about 6 write-sovereignty rows.

Exit:

- Site-scoped MV test proves configured sites are excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Waves 17-116: Site-Scoped Artifact, Proof, and Output Sites

Goal: Remove the next 100 released write-sovereignty rows that are exact
artifact/proof/output sites, without excluding generic symbols globally.

Selection guard:

- Exclude only exact `(write_symbol, writer_file)` pairs listed below.
- Keep same-symbol writes in other files visible.
- Do not include cache stores, secrets, audit trails, HITL replay stores,
  training stores, or generic file APIs without artifact-site evidence.

Expected reduction on `07082026_2319`: about 267 write-sovereignty rows.

| Wave | Rows | Symbol | Writer file |
| --- | ---: | --- | --- |
| W17 | 10 | `write_text` | `apps_rg/runtime/reasoning/bullet_lane_self_consistency.py` |
| W18 | 10 | `write_text` | `apps_rg/runtime/sections/competencies_lane_execution.py` |
| W19 | 10 | `write_text` | `apps_rg/runtime/sections/ibm_narrative_lane_execution.py` |
| W20 | 10 | `write_text` | `apps_rg/runtime/sections/role_episode_lane.py` |
| W21 | 6 | `path.write_text` | `apps_rg/cache/cache_preflight_evidence.py` |
| W22 | 6 | `write_text` | `apps_rg/fact_inventory/materialize_career_tracks_p1.py` |
| W23 | 6 | `write_text` | `apps_rg/runtime/judges/bullet_pool_claude_selector.py` |
| W24 | 6 | `path.write_text` | `apps_rg/runtime/post_x3_completion.py` |
| W25 | 6 | `write_text` | `apps_rg/runtime/sections/executive_summary_proof_bundle.py` |
| W26 | 4 | `path.write_text` | `agentic_core/runtime/entrypoints/integrated_fallback_run.py` |
| W27 | 4 | `path.write_text` | `agentic_core/runtime/entrypoints/integrated_grounded_read_run.py` |
| W28 | 4 | `path.write_text` | `agentic_core/runtime/entrypoints/integrated_managed_workflow_real_run.py` |
| W29 | 4 | `path.write_text` | `agentic_core/runtime/entrypoints/integrated_single_action_run.py` |
| W30 | 4 | `write_text` | `apps_research/__main__.py` |
| W31 | 4 | `path.write_text` | `apps_rg/runtime/bindings/section_lane_c0_metrics.py` |
| W32 | 4 | `write_text` | `apps_rg/runtime/integrated_lane_evidence_packaging.py` |
| W33 | 4 | `path.write_text` | `apps_rg/runtime/observability/trace_reconciliation.py` |
| W34 | 4 | `write_text` | `apps_rg/runtime/pre_dispatch_preflight.py` |
| W35 | 4 | `path.write_text` | `apps_rg/runtime/section_failure_forensics.py` |
| W36 | 4 | `write_text` | `apps_rg/runtime/sections/executive_summary_candidate_pool.py` |
| W37 | 4 | `path.write_text` | `apps_rg/runtime/shadow/l6_microstep_observability.py` |
| W38 | 4 | `write_text` | `apps_underwriting_ai/tools/run_underwriting.py` |
| W39 | 2 | `path.write_text` | `agentic_core/L2_execution/utils/determinism.py` |
| W40 | 2 | `target.write_text` | `agentic_core/L3_orchestration/managed_workflow_runner.py` |
| W41 | 2 | `target.write_text` | `agentic_core/runtime/entry/apps_rg_w9_managed_workflow_e2e.py` |
| W42 | 2 | `path.write_text` | `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py` |
| W43 | 2 | `path.write_text` | `apps_eval/adapters/apps_rg.py` |
| W44 | 2 | `target.write_text` | `apps_eval/adapters/apps_rg.py` |
| W45 | 2 | `path.write_text` | `apps_eval/scenarios.py` |
| W46 | 2 | `path.write_text` | `apps_lic/runtime/dispatch/runtime_proof_bundle.py` |
| W47 | 2 | `path.write_text` | `apps_lic/runtime/dispatch/stage_receipts.py` |
| W48 | 2 | `path.write_text` | `apps_research/engines/company_brief_engine.py` |
| W49 | 2 | `path.write_text` | `apps_research/utils/research_artifact_util.py` |
| W50 | 2 | `path.write_text` | `apps_rg/cache/r1b_whole_run_preflight.py` |
| W51 | 2 | `path.write_text` | `apps_rg/fact_inventory/apply_c03_graph_full_zero_loss_overwrite.py` |
| W52 | 2 | `path.write_text` | `apps_rg/fact_inventory/apply_c03_graph_skill_granularity_hardening.py` |
| W53 | 2 | `OUT_LEDGER.write_text` | `apps_rg/fact_inventory/apply_commercial_skills_expansion.py` |
| W54 | 2 | `OUT_LEDGER.write_text` | `apps_rg/fact_inventory/apply_cro_projection_hardening.py` |
| W55 | 2 | `tmp.write_text` | `apps_rg/fact_inventory/apply_phase1_new_skill_nodes.py` |
| W56 | 2 | `tmp.write_text` | `apps_rg/fact_inventory/apply_phase1_resume_linkage_remediation.py` |
| W57 | 2 | `path.write_text` | `apps_rg/fact_inventory/run_w14_senior_role_offline_traversal.py` |
| W58 | 2 | `write_text` | `apps_rg/fact_inventory/run_w14_senior_role_offline_traversal.py` |
| W59 | 2 | `path.write_text` | `apps_rg/l2_recipe/modular_resume_generation.py` |
| W60 | 2 | `path.write_text` | `apps_rg/l2_recipe/modular_rg_output_builder.py` |
| W61 | 2 | `write_text` | `apps_rg/l2_recipe/steps.py` |
| W62 | 2 | `path.write_text` | `apps_rg/runtime/c0/evidence_room.py` |
| W63 | 2 | `write_text` | `apps_rg/runtime/c0/fact_vector_index_preflight.py` |
| W64 | 2 | `path.write_text` | `apps_rg/runtime/dispatch/spine_stage_receipts.py` |
| W65 | 2 | `path.write_text` | `apps_rg/runtime/final_resume_outputs.py` |
| W66 | 2 | `write_text` | `apps_rg/runtime/final_resume_outputs.py` |
| W67 | 2 | `path.write_text` | `apps_rg/runtime/graph_selection_rationale.py` |
| W68 | 2 | `path.write_text` | `apps_rg/runtime/graph_skills_run_artifacts.py` |
| W69 | 2 | `path.write_text` | `apps_rg/runtime/internal/locked_copy_builder.py` |
| W70 | 2 | `path.write_text` | `apps_rg/runtime/judges/bullet_pool_claude_selector.py` |
| W71 | 2 | `open` | `apps_rg/runtime/judges/executive_summary_judge_packet.py` |
| W72 | 2 | `path.write_text` | `apps_rg/runtime/judges/grade_only_judge_packet.py` |
| W73 | 2 | `path.write_text` | `apps_rg/runtime/locked_copy/locked_copy_x2.py` |
| W74 | 2 | `path.write_text` | `apps_rg/runtime/mandatory_run_outputs.py` |
| W75 | 2 | `path.write_text` | `apps_rg/runtime/orchestration/canonical_dispatch.py` |
| W76 | 2 | `path.write_text` | `apps_rg/runtime/orchestration/patch_run.py` |
| W77 | 2 | `path.write_text` | `apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py` |
| W78 | 2 | `write_text` | `apps_rg/runtime/orchestration/section_lane_executor.py` |
| W79 | 2 | `path.write_text` | `apps_rg/runtime/pre_dispatch_preflight.py` |
| W80 | 2 | `write_text` | `apps_rg/runtime/providers/section_provider_call.py` |
| W81 | 2 | `path.write_text` | `apps_rg/runtime/reasoning/bullet_pool_reselection.py` |
| W82 | 2 | `path.write_text` | `apps_rg/runtime/reasoning/competencies_graph_pool.py` |
| W83 | 2 | `path.write_text` | `apps_rg/runtime/run_bundle_index.py` |
| W84 | 2 | `path.write_text` | `apps_rg/runtime/run_correlation_links.py` |
| W85 | 2 | `path.write_text` | `apps_rg/runtime/runtime_proof_layout.py` |
| W86 | 2 | `path.write_text` | `apps_rg/runtime/section_l2_spine_receipt.py` |
| W87 | 2 | `path.write_text` | `apps_rg/runtime/section_l7_binding_lane_integration.py` |
| W88 | 2 | `path.write_text` | `apps_rg/runtime/section_repair_ledger.py` |
| W89 | 2 | `path.write_text` | `apps_rg/runtime/sections/executive_summary_evidence_capsule.py` |
| W90 | 2 | `path.write_text` | `apps_rg/runtime/sections/executive_summary_operator_reporting.py` |
| W91 | 2 | `path.write_text` | `apps_rg/runtime/sections/executive_summary_regen_dispatch.py` |
| W92 | 2 | `path.write_text` | `apps_rg/runtime/sections/executive_summary_token_budget.py` |
| W93 | 2 | `write_text` | `apps_rg/runtime/sections/ibm_narrative_lane_runtime.py` |
| W94 | 2 | `path.write_text` | `apps_rg/runtime/sections/lane_artifact_io.py` |
| W95 | 2 | `path.write_text` | `apps_rg/runtime/sections/section_x2_gate_outputs.py` |
| W96 | 2 | `path.write_text` | `apps_rg/runtime/sections_root_manifest.py` |
| W97 | 2 | `path.write_text` | `apps_rg/runtime/spine/c0_graph_lane_receipt.py` |
| W98 | 2 | `path.write_text` | `apps_rg/runtime/spine/l2_handoff_receipt.py` |
| W99 | 2 | `path.write_text` | `apps_rg/runtime/spine/l6_eval_before_learn_receipt.py` |
| W100 | 2 | `path.write_text` | `apps_rg/runtime/spine/l6_shadow_eval_runner.py` |
| W101 | 2 | `path.write_text` | `apps_rg/runtime/spine/section_c0_retrieve.py` |
| W102 | 2 | `path.write_text` | `apps_rg/runtime/spine/section_x3_finalize.py` |
| W103 | 2 | `path.write_text` | `apps_rg/runtime/spine/spine_span_emit.py` |
| W104 | 2 | `path.write_text` | `apps_shared/contracts/cross_app/base.py` |
| W105 | 2 | `path.write_text` | `apps_shared/spine_emission/context.py` |
| W106 | 1 | `out_path.open` | `agentic_core/L0_routing/types/routing_contracts_types.py` |
| W107 | 1 | `brief_path.open` | `agentic_core/runtime/exit/apps_research_exit_binding.py` |
| W108 | 1 | `metadata_path.open` | `agentic_core/runtime/exit/apps_research_exit_binding.py` |
| W109 | 1 | `open` | `apps_rg/runtime/judges/executive_summary_x1d.py` |
| W110 | 1 | `open` | `apps_rg/runtime/judges/executive_summary_x1d_dimension_verdicts.py` |
| W111 | 1 | `path.write_bytes` | `apps_rg/runtime/reasoning/bullet_pool_reselection.py` |
| W112 | 1 | `open` | `apps_rg/runtime/sections/executive_summary_generation_grade_contract.py` |
| W113 | 1 | `open` | `apps_rg/runtime/sections/executive_summary_judge_variance.py` |
| W114 | 1 | `open` | `apps_rg/runtime/sections/executive_summary_upstream_triangulation.py` |
| W115 | 1 | `path.open` | `apps_rg/runtime/spine/spine_span_emit.py` |
| W116 | 1 | `out_path.open` | `apps_rg/tools/fact_vector_ingest.py` |

Exit:

- Site-scoped MV test proves every configured site is excluded.
- Same-symbol different-file test proves future generic writes remain flagged.

### Waves 117-281: Site-Scoped Artifact, Report, Proof, and False-Positive Sites

Goal: Remove the next safe released write-sovereignty rows that are exact
artifact/report/proof sites or scanner false positives, without excluding
generic symbols globally.

Selection guard:

- Exclude only exact `(write_symbol, writer_file)` pairs listed below.
- Keep same-symbol writes in other files visible.
- Defer real durable stores, secrets, HITL replay logs, checkpoints, training
  stores, vector/embedding stores, and generic file APIs.

Expected reduction on `07082026_2319`: about 310 write-sovereignty rows.
The requested 200-wave pass found only 165 pairs that stayed within the
standing mechanical-ADG approval scope. The remaining 84 pairs / 114 rows are
deferred to source-routing or ownership review instead of being hidden by MV
exclusion.

| Wave | Rows | Symbol | Writer file |
| --- | ---: | --- | --- |
| W117 | 8 | `out.write_text` | `agentic_core/L7_auditability/fortknox/emit_l7_fortknox_evidence.py` |
| W118 | 8 | `write_text` | `apps_rg/cache/r1b_derived_index.py` |
| W119 | 6 | `json_path.write_text` | `apps_eval/trends.py` |
| W120 | 4 | `md_path.write_text` | `apps_eval/trends.py` |
| W121 | 4 | `write_text` | `apps_rg/cache/r1b_chroma_read_surface_projection.py` |
| W122 | 4 | `receipt_json_path.write_text` | `apps_rg/fact_inventory/competencies_graph_skills_proof_pool.py` |
| W123 | 4 | `receipt_md_path.write_text` | `apps_rg/fact_inventory/competencies_graph_skills_proof_pool.py` |
| W124 | 4 | `man_path.write_text` | `apps_rg/l2_recipe/resume_artifact_gate.py` |
| W125 | 3 | `get_validated_project_root` | `agentic_core/L0_routing/config/path_constants.py` |
| W126 | 3 | `compute_content_hash` | `agentic_core/L6_system_learning/engines/embedding_corpus_extraction.py` |
| W127 | 3 | `create_artifact` | `agentic_core/utils/workflow_engines/drift_monitor.py` |
| W128 | 2 | `out_path.write_text` | `agentic_core/L0_routing/types/guardian_contract_types.py` |
| W129 | 2 | `path.write_text` | `agentic_core/L0_routing/utils/filesystem_mcp_client.py` |
| W130 | 2 | `is_commit_sandbox_active` | `agentic_core/L2_execution/reasoning/tool_intent_executor.py` |
| W131 | 2 | `compute_replay_hash` | `agentic_core/L2_execution/types/vllm_replay_validator_types.py` |
| W132 | 2 | `lock_file_path.write_text` | `agentic_core/L2_execution/utils/dependency_locker.py` |
| W133 | 2 | `get_validated_project_root` | `agentic_core/L3_orchestration/reasoning/engines/orchestrator_engine.py` |
| W134 | 2 | `get_validated_project_root` | `agentic_core/L5_safety/config/structure_blueprint/ssot.py` |
| W135 | 2 | `output_path.write_text` | `agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py` |
| W136 | 2 | `file_path.write_text` | `agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py` |
| W137 | 2 | `path.write_text` | `agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py` |
| W138 | 2 | `requirements_path.write_text` | `agentic_core/L5_safety/utils/dependency_pruning_util.py` |
| W139 | 2 | `get_validated_project_root` | `agentic_core/L5_safety/utils/location_utils_util.py` |
| W140 | 2 | `output_path.write_text` | `agentic_core/L5_safety/utils/structure_drift_writer.py` |
| W141 | 2 | `output_file.write_text` | `agentic_core/L5_safety/validators/structure_drift_validator.py` |
| W142 | 2 | `json_path.write_text` | `agentic_core/L6_observability/shadow_eval/span_export.py` |
| W143 | 2 | `report_path.write_text` | `agentic_core/L6_system_learning/engines/cross_repo_system_learning_import.py` |
| W144 | 2 | `output_path.write_bytes` | `agentic_core/L6_system_learning/engines/seed_embedding_pack_builder.py` |
| W145 | 2 | `out_path.write_text` | `agentic_core/L7_auditability/coverage/route_family_l7_coverage.py` |
| W146 | 2 | `tmp_path.write_text` | `agentic_core/mixins/atomic_execution_mixin.py` |
| W147 | 2 | `context.file_path.write_text` | `agentic_core/mixins/cst_healer_mixin.py` |
| W148 | 2 | `manifest_path.write_text` | `agentic_core/runtime/entrypoints/integrated_fallback_run.py` |
| W149 | 2 | `manifest_path.write_text` | `agentic_core/runtime/entrypoints/integrated_grounded_read_run.py` |
| W150 | 2 | `manifest_path.write_text` | `agentic_core/runtime/entrypoints/integrated_managed_workflow_real_run.py` |
| W151 | 2 | `manifest_path.write_text` | `agentic_core/runtime/entrypoints/integrated_single_action_run.py` |
| W152 | 2 | `shutil.move` | `agentic_core/utils/structural_healing_engine_util.py` |
| W153 | 2 | `report_path.write_text` | `apps_eval/matrix.py` |
| W154 | 2 | `summary_path.write_text` | `apps_eval/matrix.py` |
| W155 | 2 | `artifact.write_text` | `apps_eval/scenarios.py` |
| W156 | 2 | `wizard_brief_path.write_text` | `apps_lic/__main__.py` |
| W157 | 2 | `briefing_path.write_text` | `apps_research/__main__.py` |
| W158 | 2 | `company_brief_path.write_text` | `apps_research/__main__.py` |
| W159 | 2 | `brief_path.write_text` | `apps_research/reasoning/ResearchOrchestrator.py` |
| W160 | 2 | `path.write_text` | `apps_rg/cache/r1b_chroma_read_surface_projection.py` |
| W161 | 2 | `out_path.write_text` | `apps_rg/fact_inventory/apply_c03_graph_full_zero_loss_overwrite.py` |
| W162 | 2 | `LEDGER.write_text` | `apps_rg/fact_inventory/apply_career_phase_wiring.py` |
| W163 | 2 | `CLOSEOUT_JSON.write_text` | `apps_rg/fact_inventory/apply_commercial_skills_expansion.py` |
| W164 | 2 | `CLOSEOUT_MD.write_text` | `apps_rg/fact_inventory/apply_commercial_skills_expansion.py` |
| W165 | 2 | `DESIGN_PATH.write_text` | `apps_rg/fact_inventory/apply_commercial_skills_expansion.py` |
| W166 | 2 | `DESIGN_PATH.write_text` | `apps_rg/fact_inventory/apply_cro_projection_hardening.py` |
| W167 | 2 | `OUT_JSON.write_text` | `apps_rg/fact_inventory/apply_cro_projection_hardening.py` |
| W168 | 2 | `OUT_MD.write_text` | `apps_rg/fact_inventory/apply_cro_projection_hardening.py` |
| W169 | 2 | `CLOSEOUT_JSON.write_text` | `apps_rg/fact_inventory/apply_draft_skill_promotions_20260527.py` |
| W170 | 2 | `CLOSEOUT_MD.write_text` | `apps_rg/fact_inventory/apply_draft_skill_promotions_20260527.py` |
| W171 | 2 | `ledger_path.write_text` | `apps_rg/fact_inventory/apply_draft_skill_promotions_20260527.py` |
| W172 | 2 | `CLOSEOUT_JSON.write_text` | `apps_rg/fact_inventory/apply_svp_it_strategy_skill_20260527.py` |
| W173 | 2 | `CLOSEOUT_MD.write_text` | `apps_rg/fact_inventory/apply_svp_it_strategy_skill_20260527.py` |
| W174 | 2 | `ledger_path.write_text` | `apps_rg/fact_inventory/apply_svp_it_strategy_skill_20260527.py` |
| W175 | 2 | `OUT_JSON.write_text` | `apps_rg/fact_inventory/audit_phase2_airline_anchor_evidence.py` |
| W176 | 2 | `OUT_MD.write_text` | `apps_rg/fact_inventory/audit_phase2_airline_anchor_evidence.py` |
| W177 | 2 | `OUT_JSON.write_text` | `apps_rg/fact_inventory/audit_phase2_estimation_sizing_evidence.py` |
| W178 | 2 | `OUT_MD.write_text` | `apps_rg/fact_inventory/audit_phase2_estimation_sizing_evidence.py` |
| W179 | 2 | `OUT_JSON.write_text` | `apps_rg/fact_inventory/build_cro_projection_gap_analysis.py` |
| W180 | 2 | `OUT_MD.write_text` | `apps_rg/fact_inventory/build_cro_projection_gap_analysis.py` |
| W181 | 2 | `output_path.write_text` | `apps_rg/fact_inventory/detect_graph_skill_gaps.py` |
| W182 | 2 | `ledger_path.write_text` | `apps_rg/fact_inventory/graph_v2_quality_migration.py` |
| W183 | 2 | `OUT_RECEIPT_JSON.write_text` | `apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py` |
| W184 | 2 | `OUT_RECEIPT_MD.write_text` | `apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py` |
| W185 | 2 | `ledger_path.write_text` | `apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py` |
| W186 | 2 | `OUT_PATH.write_text` | `apps_rg/fact_inventory/materialize_arsenal_from_design.py` |
| W187 | 2 | `LEDGER_PATH.write_text` | `apps_rg/fact_inventory/materialize_career_tracks_p1.py` |
| W188 | 2 | `out_json.write_text` | `apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py` |
| W189 | 2 | `out_md.write_text` | `apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py` |
| W190 | 2 | `OUT_JSON.write_text` | `apps_rg/fact_inventory/run_w14b_taxonomy_track_weight_wiring.py` |
| W191 | 2 | `OUT_MD.write_text` | `apps_rg/fact_inventory/run_w14b_taxonomy_track_weight_wiring.py` |
| W192 | 2 | `P1_W5_RECEIPT_JSON.write_text` | `apps_rg/fact_inventory/track_balanced_section_projection.py` |
| W193 | 2 | `P1_W5_RECEIPT_MD.write_text` | `apps_rg/fact_inventory/track_balanced_section_projection.py` |
| W194 | 2 | `md_path.write_text` | `apps_rg/fact_inventory/track_weighted_graph_expansion.py` |
| W195 | 2 | `receipt_path.write_text` | `apps_rg/fact_inventory/track_weighted_graph_expansion.py` |
| W196 | 2 | `out.write_text` | `apps_rg/fact_inventory/validate_c03_graph_hardening.py` |
| W197 | 2 | `out.write_text` | `apps_rg/l2_recipe/provider_run_diagnostics.py` |
| W198 | 2 | `json_path.write_text` | `apps_rg/l2_recipe/resume_artifact_gate.py` |
| W199 | 2 | `out.write_text` | `apps_rg/l2_recipe/steps.py` |
| W200 | 2 | `out_path.write_text` | `apps_rg/runtime/assembly/full_resume_llm_coherence.py` |
| W201 | 2 | `artifact_path.write_text` | `apps_rg/runtime/bindings/c0_metrics_writer.py` |
| W202 | 2 | `write_text` | `apps_rg/runtime/c0/c02_fact_vector_ingest.py` |
| W203 | 2 | `out.write_text` | `apps_rg/runtime/cli_section_execution_report.py` |
| W204 | 2 | `out.write_text` | `apps_rg/runtime/embedding_settings.py` |
| W205 | 2 | `out_path.write_text` | `apps_rg/runtime/evidence/canonical_evidence_digest_chain.py` |
| W206 | 2 | `contract_path.write_text` | `apps_rg/runtime/final_resume_outputs.py` |
| W207 | 2 | `manifest_path.write_text` | `apps_rg/runtime/final_resume_outputs.py` |
| W208 | 2 | `out.write_text` | `apps_rg/runtime/full_resume_review_bundle.py` |
| W209 | 2 | `json_path.write_text` | `apps_rg/runtime/full_run_section_status.py` |
| W210 | 2 | `md_path.write_text` | `apps_rg/runtime/full_run_section_status.py` |
| W211 | 2 | `out_path.write_text` | `apps_rg/runtime/integrated_lane_evidence_packaging.py` |
| W212 | 2 | `mf_path.write_text` | `apps_rg/runtime/internal/resume_package_disposition.py` |
| W213 | 2 | `rc_path.write_text` | `apps_rg/runtime/internal/resume_package_disposition.py` |
| W214 | 2 | `baseline_file.write_text` | `apps_rg/runtime/judges/graph_skills_x1d_rubric_contract.py` |
| W215 | 2 | `json_path.write_text` | `apps_rg/runtime/mandatory_run_outputs.py` |
| W216 | 2 | `manifest_path.write_text` | `apps_rg/runtime/orchestration/canonical_dispatch.py` |
| W217 | 2 | `brief_path.write_text` | `apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py` |
| W218 | 2 | `coverage_path.write_text` | `apps_rg/runtime/post_x3_completion.py` |
| W219 | 2 | `json_path.write_text` | `apps_rg/runtime/runtime_executive_summary.py` |
| W220 | 2 | `md_path.write_text` | `apps_rg/runtime/runtime_executive_summary.py` |
| W221 | 2 | `p_receipt.write_text` | `apps_rg/runtime/section_l2_spine_receipt.py` |
| W222 | 2 | `out.write_text` | `apps_rg/runtime/section_l7_binding_manifest.py` |
| W223 | 2 | `p_receipt.write_text` | `apps_rg/runtime/section_runtime_exhaust_spine_receipt.py` |
| W224 | 2 | `receipt_path.write_text` | `apps_rg/runtime/sections/executive_summary_regen_observability.py` |
| W225 | 2 | `rca_path.write_text` | `apps_rg/runtime/shadow/competencies_l6.py` |
| W226 | 2 | `json_path.write_text` | `apps_rg/runtime/shadow/headline_l6.py` |
| W227 | 2 | `md_path.write_text` | `apps_rg/runtime/shadow/headline_l6.py` |
| W228 | 2 | `p_receipt.write_text` | `apps_rg/runtime/spine/c0_fec_compose.py` |
| W229 | 2 | `receipt_path.write_text` | `apps_rg/runtime/spine/governed_pa_compose.py` |
| W230 | 2 | `json_path.write_text` | `apps_rg/runtime/validators/validate_exec_summary_graph_only_generation.py` |
| W231 | 2 | `md_path.write_text` | `apps_rg/runtime/validators/validate_exec_summary_graph_only_generation.py` |
| W232 | 2 | `out.write_text` | `apps_rg/runtime/whole_run_exit.py` |
| W233 | 1 | `get_validated_project_root` | `agentic_core/L0_routing/reasoning/RootCustomsAgent.py` |
| W234 | 1 | `assert_no_persistent_write` | `agentic_core/L0_routing/types/guardian_contract_types.py` |
| W235 | 1 | `get_validated_project_root` | `agentic_core/L0_routing/utils/path_util.py` |
| W236 | 1 | `assert_no_persistent_write` | `agentic_core/L0_routing/utils/root_customs_util.py` |
| W237 | 1 | `get_validated_project_root` | `agentic_core/L0_routing/utils/root_customs_util.py` |
| W238 | 1 | `shutil.move` | `agentic_core/L0_routing/utils/root_customs_util.py` |
| W239 | 1 | `get_write_gateway` | `agentic_core/L2_execution/enforcement/write_governor_mixin.py` |
| W240 | 1 | `subprocess.Popen` | `agentic_core/L2_execution/utils/safe_subprocess.py` |
| W241 | 1 | `path.write_bytes` | `agentic_core/L2_execution/writers/patch_envelope.py` |
| W242 | 1 | `get_validated_project_root` | `agentic_core/L5_safety/enforcement/airlock_trimmer_enforcer.py` |
| W243 | 1 | `open` | `agentic_core/L5_safety/enforcement/audit/ai_check_audit.py` |
| W244 | 1 | `open` | `agentic_core/L5_safety/enforcement/audit/safety_audit_trail.py` |
| W245 | 1 | `get_validated_project_root` | `agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py` |
| W246 | 1 | `get_validated_project_root` | `agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py` |
| W247 | 1 | `baseline_path.write_bytes` | `agentic_core/L5_safety/enforcement/module_collision_guardrail.py` |
| W248 | 1 | `subprocess.Popen` | `agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py` |
| W249 | 1 | `get_validated_project_root` | `agentic_core/L5_safety/types/agent_audit_result_types.py` |
| W250 | 1 | `get_validated_project_root` | `agentic_core/L5_safety/utils/force_app_depth_util.py` |
| W251 | 1 | `get_validated_project_root` | `agentic_core/L5_safety/utils/forge_fortress_util.py` |
| W252 | 1 | `create_legacy_import_healer` | `agentic_core/L5_safety/utils/location_healer_util.py` |
| W253 | 1 | `get_validated_project_root` | `agentic_core/L5_safety/utils/location_healer_util.py` |
| W254 | 1 | `get_validated_project_root` | `agentic_core/L5_safety/utils/location_path_util.py` |
| W255 | 1 | `subprocess.Popen` | `agentic_core/L5_safety/utils/subprocess_security_util.py` |
| W256 | 1 | `get_validated_project_root` | `agentic_core/L5_safety/utils/verify_no_mock_data_util.py` |
| W257 | 1 | `create_legacy_import_healer` | `agentic_core/L5_safety/validators/mission_preflight_validator.py` |
| W258 | 1 | `get_validated_project_root` | `agentic_core/L5_safety/validators/report_location_validator.py` |
| W259 | 1 | `path.open` | `agentic_core/L6_observability/flywheel_promoter.py` |
| W260 | 1 | `assert_no_persistent_write` | `agentic_core/L6_observability/utils/fix_testing_observability_util.py` |
| W261 | 1 | `path.write_bytes` | `agentic_core/L6_system_learning/engines/cross_repo_system_learning_import.py` |
| W262 | 1 | `compute_content_hash` | `agentic_core/L6_system_learning/engines/graph_neighborhood_embedder.py` |
| W263 | 1 | `compute_content_hash` | `agentic_core/L6_system_learning/engines/healer_outcome_embedder.py` |
| W264 | 1 | `compute_content_hash` | `agentic_core/L6_system_learning/engines/incident_bundle_embedder.py` |
| W265 | 1 | `compute_content_hash` | `agentic_core/L6_system_learning/engines/mutation_diff_embedder.py` |
| W266 | 1 | `compute_content_hash` | `agentic_core/L6_system_learning/engines/path_d_preference_embedder.py` |
| W267 | 1 | `compute_content_hash` | `agentic_core/L6_system_learning/engines/policy_guardrail_embedder.py` |
| W268 | 1 | `compute_content_hash` | `agentic_core/L6_system_learning/engines/prompt_outcome_embedder.py` |
| W269 | 1 | `compute_content_hash` | `agentic_core/L6_system_learning/engines/replay_failure_embedder.py` |
| W270 | 1 | `compute_content_hash` | `agentic_core/L6_system_learning/engines/retrieval_case_embedder.py` |
| W271 | 1 | `manifest_path.write_bytes` | `agentic_core/L6_system_learning/engines/seed_embedding_pack_builder.py` |
| W272 | 1 | `TraceFeatureRecord.from_bundle` | `agentic_core/L6_system_learning/engines/trace_feature_extractor.py` |
| W273 | 1 | `shutil.rmtree` | `agentic_core/mixins/atomic_execution_mixin.py` |
| W274 | 1 | `tmp_path.open` | `agentic_core/utils/schemas/evaluation_dataset_schema.py` |
| W275 | 1 | `create_artifact` | `agentic_core/utils/workflow_engines/dpo_batch_builder.py` |
| W276 | 1 | `create_artifact` | `agentic_core/utils/workflow_engines/offline_eval_runner.py` |
| W277 | 1 | `create_artifact` | `agentic_core/utils/workflow_engines/proposer_bridge.py` |
| W278 | 1 | `create_artifact` | `agentic_core/utils/workflow_engines/replay_eval_runner.py` |
| W279 | 1 | `open` | `apps_lic/migrations/w5_migration.py` |
| W280 | 1 | `shutil.move` | `apps_shared/utils/subatomic_hop_util.py` |
| W281 | 1 | `get_validated_project_root` | `apps_shared/utils/waterfall_reconciliation_util.py` |

Exit:

- Site-scoped MV test proves every configured site is excluded.
- Same-symbol different-file test proves future generic writes remain flagged.
- Deferred candidate list stays visible for routing work instead of being
  treated as no-op backlog.

### Wave 282: Source Routing for Real Write Clusters

Goal: Route high-confidence real writes through UWG or sanctioned layer
authorities.

Candidate clusters:

- app runtime manifest/lock writes
- L2 deterministic output writers
- L6 telemetry/report persistence
- cache stores, vector stores, secrets, HITL replay, checkpoints, and training
  surfaces deferred from W117-W281

Stop condition: stop for design review if routing changes public contracts,
runtime persistence semantics, or migration receipts.

### Wave 283: G_REACH Owned Runtime Wiring

Goal: Reduce L0 reachability debt by wiring or retiring real orphan clusters.

Candidate clusters:

- C0 context engine modules
- L1 planning/enforcement modules
- unused/deleted legacy modules

Stop condition: do not add artificial L0 imports just to make ADG green; each
reachability repair must correspond to a real runtime path, test, or deletion.

## Validation

Focused checks for this wave:

- `python -m pytest tests/unit/tools/generate/test_materialized_views_phase_a.py tests/unit/tools/reports/test_adg_bcg_adapter.py tests/unit/tools/reports/test_adg_burndown_report_mandatory.py tests/unit/tools_adg/test_run_full_adg_audit.py::test_repair_counts_split_p0_fix_wave_and_backlog -q`
- `python tools/adg/consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json`

Full proof after merge requires the upstream full ADG producer to regenerate
digest-bound artifacts. This branch does not rewrite the existing handoff.
