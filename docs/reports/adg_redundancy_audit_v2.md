# ADG Redundancy Audit v2 ΓÇö code-based

Total CI gates analyzed: 103

## Summary

| Classification | Count | Action |
|----------------|-------|--------|
| NON_GRAPH | 47 | KEEP ΓÇö legitimate non-graph concern |
| POLICY_LAYER | 42 | KEEP ΓÇö policy added on top of ADG |
| THIN_CANDIDATE | 1 | REVIEW ΓÇö possibly truly redundant |
| RAW_CONSUMER | 13 | CONSIDER promoting query to MV |

## THIN_CANDIDATE ΓÇö verify each is actually redundant

These gates select from an MV/P-view and have NO detected policy markers.
Manual review: confirm the MV alone enforces what the gate enforces.

| Gate | LOC | MV/P-view |
|------|-----|-----------|
| `ops_scripts/ci/check_w4_l5_bypass.py` | 71 | MV |

## RAW_CONSUMER ΓÇö 13 gates query raw tables

These gates use SELECT against `edges`/`violations`/`nodes` directly. An MV could pre-compute the join/aggregation. This is an ADG improvement opportunity, NOT a gate retirement.

| Gate | LOC | Has Policy? |
|------|-----|-------------|
| `ops_scripts/ci/check_canonical_pipeline_wiring.py` | 230 | ΓÇö |
| `ops_scripts/ci/check_decision_ledger_chain.py` | 224 | ΓÇö |
| `ops_scripts/ci/check_decision_required.py` | 230 | ΓÇö |
| `ops_scripts/ci/check_exception_contract.py` | 275 | ΓÇö |
| `ops_scripts/ci/check_ledger_freshness.py` | 206 | ΓÇö |
| `ops_scripts/ci/check_ledger_writer_contract.py` | 126 | ΓÇö |
| `ops_scripts/ci/check_marker_ledger_parity.py` | 281 | ΓÇö |
| `ops_scripts/ci/check_memory_promotion_parity.py` | 191 | ΓÇö |
| `ops_scripts/ci/check_notion_decision_parity.py` | 185 | ΓÇö |
| `ops_scripts/ci/check_precedent_receipt.py` | 160 | ΓÇö |
| `ops_scripts/ci/check_prediction_binding_sla.py` | 129 | ΓÇö |
| `ops_scripts/ci/check_w5_missing_adapter.py` | 78 | ΓÇö |
| `ops_scripts/ci/check_w6_trace_theater_kpi.py` | 106 | ΓÇö |

## POLICY_LAYER ΓÇö 42 gates correctly layered

These gates consume ADG primitives AND add policy (thresholds, allowlists, ratchets, temporal deltas). Each retirement would be an enforcement loss.

| Gate | Policy markers (sample) |
|------|--------------------------|
| `ops_scripts/ci/check_cross_mainline_dispatcher.py` | baseline, ratchet |
| `ops_scripts/ci/check_cyclomatic_ceiling.py` | EXCLUDE_PREFIXES, PRODUCTION_ROOTS, baseline |
| `ops_scripts/ci/check_dead_folder_detector.py` | MIN_FOLDER_SIZE, baseline, ratchet |
| `ops_scripts/ci/check_dead_methods_ratchet.py` | Baseline, EXCLUDE_PREFIXES, PRODUCTION_ROOTS |
| `ops_scripts/ci/check_dead_symbols_ratchet.py` | Baseline, EXCLUDE_PREFIXES, PRODUCTION_ROOTS |
| `ops_scripts/ci/check_env_var_in_config_layer.py` | baseline, ratchet |
| `ops_scripts/ci/check_external_service_literal_ssot.py` | Baseline, ratchet |
| `ops_scripts/ci/check_graph_island.py` | baseline, ratchet |
| `ops_scripts/ci/check_graph_reach.py` | Baseline, RATCHET |
| `ops_scripts/ci/check_graph_reach_archival.py` | baseline, ratchet |
| `ops_scripts/ci/check_layer_skip.py` | Baseline, ratchet |
| `ops_scripts/ci/check_lpg_drift_ratchet.py` | baseline, ratchet |
| `ops_scripts/ci/check_module_loc_ratchet.py` | EXCLUDE_PREFIXES, MAX_LOC, PRODUCTION_ROOTS |
| `ops_scripts/ci/check_observability_on_high_fanin.py` | Baseline, fan_in >, fan_out= |
| `ops_scripts/ci/author_gate/check_outcome_coverage.py` | baseline |
| `ops_scripts/ci/check_overlay_ratchet.py` | baseline, ratchet |
| `ops_scripts/ci/check_precedent_usage_rate.py` | baseline |
| `ops_scripts/ci/check_role_dedup.py` | fan_in= |
| `ops_scripts/ci/check_snapshot_has_mvs.py` | MIN_MV_TABLES |
| `ops_scripts/ci/check_ssot_magic_constants.py` | Baseline, ratchet |
| `ops_scripts/ci/check_test_harness_coverage.py` | Ratchet, baseline |
| `ops_scripts/ci/check_trace_stub_modules.py` | EXCLUDE_PATHS, MIN_IMPORTS, PRODUCTION_ROOTS |
| `ops_scripts/ci/check_unused_imports_ratchet.py` | EXCLUDE_LAYERS, baseline, ratchet |
| `ops_scripts/ci/check_uwg_bypass_ratchet.py` | EXCLUDE_LAYERS, baseline, ratchet |
| `ops_scripts/ci/check_violation_aging_sla.py` | baseline, ratchet |
| `ops_scripts/ci/check_w4_exit_disposition.py` | baseline, ratchet |
| `ops_scripts/ci/check_w4_guardrail_separation.py` | baseline, ratchet |
| `ops_scripts/ci/check_w4_policy_without_audit.py` | baseline, ratchet |
| `ops_scripts/ci/check_w4_replay_surface_gaps.py` | baseline, ratchet |
| `ops_scripts/ci/check_w4_silent_writes.py` | baseline, ratchet |
| `ops_scripts/ci/check_w4_tool_call_parity.py` | baseline, ratchet |
| `ops_scripts/ci/check_w4_unresolved_callsites.py` | baseline, ratchet |
| `ops_scripts/ci/check_w4_uwg_bypass_pview.py` | RATCHET |
| `ops_scripts/ci/check_w5_broken_contract.py` | baseline, ratchet |
| `ops_scripts/ci/check_w5_structured_output.py` | baseline, ratchet |
| `ops_scripts/ci/check_w5_taint_actionable.py` | baseline, ratchet |
| `ops_scripts/ci/check_w5_untyped_seam.py` | baseline, ratchet |
| `ops_scripts/ci/check_w6_ap_velocity_kpi.py` | PRODUCTION_ROOTS |
| `ops_scripts/ci/check_w6_fanin_collapse.py` | COLLAPSE_FRACTION, TOP_N, baseline |
| `ops_scripts/ci/check_w6_mv_staleness.py` | baseline, connect_prior, ratchet |
| `ops_scripts/ci/check_w6_new_orphans_delta.py` | baseline, connect_prior, fan_in= |
| `ops_scripts/ci/check_writer_allowlist.py` | ALLOWLIST |

## NON_GRAPH ΓÇö 47 gates (no SQL)

These gates do not execute SQL queries. They check config schema, file-format invariants, process lifecycles, or runtime behavior. Outside ADG scope by design.


## A12 Self-Consistency After Fix

Snapshot: adg_indexed_04252026_0843.sqlite ΓÇö gates examined=100, drift=2
**Note**: A12 enricher was patched in this commit. Re-run `python tools/generate_full_adg.py` to refresh the table; the two prior false-positives (`check_exception_contract.py`, `check_unused_imports_ratchet.py`) should drop to zero.
