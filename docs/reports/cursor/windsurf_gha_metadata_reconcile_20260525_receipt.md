# Windsurf GHA cutover — plan metadata reconcile receipt

**Plan:** [windsurf-gha-cutover-d9f2a7.md](../../.cursor/plans/windsurf-gha-cutover-d9f2a7.md)  
**Reconciled:** 2026-05-25  
**Notion Plans row:** `36927693-f55c-81eb-a9a1-d9955c280b83`  
**Notion receipt page (child):** https://www.notion.so/36b27693f55c815abbf8f3e793e0f295  
**Manifest:** [windsurf_gha_metadata_reconcile_20260525_manifest.json](windsurf_gha_metadata_reconcile_20260525_manifest.json)

## STATUS

| Dimension | Status |
|-----------|--------|
| Migration scope (W0–W5 + W5.D1–D4) | **COMPLETE** |
| Plan ledger integrity (phase tables) | **PASS** — reconciled 2026-05-25 |
| Global contract gate (DoD-4) | **PARTIAL** — external graph_layer blocker |
| Full `.windsurf/` tree deletion (W1.D1) | **OUT_OF_BAND** — separate plan |

`PLAN_STATUS: COMPLETED` means windsurf-gha-cutover migration scope only — **not** full repository governance green.

## Changes (zero-loss metadata)

1. Phase Progress + Phase-Level Summary: W0.1–W5.1 → **DONE** (aligned with wave tables).
2. Wave bodies W0–W5: `WAVE_STATUS: DONE`, `PHASE_STATUS: DONE`.
3. Added `STATUS_INTEGRITY_NOTE`, `MIGRATION_SCOPE_STATUS`, `GLOBAL_CONTRACT_GATE_STATUS`, `GOVERNANCE_CERTIFICATION_STATUS`.
4. Deferred scope split: **Completed** (W5.D1–D4) vs **Remaining out of band** (W1.D1 tree deletion).
5. `DEFERRED_SCOPE_COMPLETE` narrowed to W5.D1–D4 (removed W1.D1 from complete claim).
6. Proof artifacts table with receipt-backed paths and command output.

## Proof references

| Artifact | Path |
|----------|------|
| Inventory | [windsurf_gha_inventory.json](windsurf_gha_inventory.json) |
| Cutover closeout | [windsurf_gha_cutover_closeout.md](windsurf_gha_cutover_closeout.md) |
| Deferred closeout | [windsurf_gha_deferred_scope_closeout.md](windsurf_gha_deferred_scope_closeout.md) |
| Deferred SSOT | [windsurf_gha_cutover_deferred_scope.md](windsurf_gha_cutover_deferred_scope.md) |
| Deletion readiness | [windsurf_deletion_readiness.json](../../artifacts/cursor/windsurf_deletion_readiness.json) |

## Commands (verification)

```text
Test-Path .github/workflows/_deleted -> False (_deleted ABSENT: OK)
python ops_scripts/ci/check_windsurf_deletion_readiness.py -> deletion_safe: false (policy)
python ops_scripts/ci/check_cursor_governance_mirror_health.py -> OK
python ops_scripts/ci/run_contract_gates.py -> exit 1
  [check_graph_layer_evidence] FAIL — 6 plan(s) missing graph-layer evidence
  (exec-summary-* plan_type + l5-pa-orchestrator-ref-forward-c7e4a1.md)
python tools/notion/plan_notion_sync_windsurf_gha_cutover.py -> patched Completed
```

## Required followup (not this plan)

- graph_layer / plan-taxonomy remediation for 6 active `.cursor/plans/*.md` violations, **or** waiver with owner reference.
- Full `.windsurf/` deletion: separate `windsurf-tree-deletion-ci-parity` plan when `deletion_safe: true`.
