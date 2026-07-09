# ADG P0 Debt Burndown

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

1. Reduce `2971 -> <= 2694` by removing confirmed scanner false positives
   and non-durable generated-artifact writer rows from the write-sovereignty
   MV producer.
2. Reduce `<= 2694 -> <= 2500` by promoting high-confidence write-sovereignty
   clusters into owned source-routing waves.
3. Reduce `<= 2500 -> <= 2000` by addressing G_REACH clusters with real runtime
   ownership or approved deletion/deprecation.
4. Continue lowering floors only after source or MV proof reduces actual rows.

Waves 2-6 remove 224 rows on the released `07082026_2319` snapshot. Combined
with Wave 1's 53 rows, the projected post-regeneration tracked P0 inventory is
`2971 - 277 = 2694`.

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

### Wave 7: Source Routing for Real Write Clusters

Goal: Route high-confidence real writes through UWG or sanctioned layer
authorities.

Candidate clusters:

- app runtime manifest/lock writes
- L2 deterministic output writers
- L6 telemetry/report persistence

Stop condition: stop for design review if routing changes public contracts,
runtime persistence semantics, or migration receipts.

### Wave 8: G_REACH Owned Runtime Wiring

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
