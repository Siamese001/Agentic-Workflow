# Windsurf GHA cutover — deferred scope

**Parent plan:** [windsurf-gha-cutover-d9f2a7.md](../../.cursor/plans/windsurf-gha-cutover-d9f2a7.md)  
**Closeout:** [windsurf_gha_cutover_closeout.md](windsurf_gha_cutover_closeout.md)  
**Captured:** 2026-05-23  
**Implemented:** 2026-05-23 — [windsurf_gha_deferred_scope_closeout.md](windsurf_gha_deferred_scope_closeout.md)

Items below were explicitly out of scope for the completed cutover. Priority bands are computed by `tools/priority/deferred_scope_scorer.py` (not hand-assigned).

---

## Markers (machine-readable)

```
DEFERRED_SCOPE: plan=windsurf-gha-cutover-d9f2a7 wave=W5 phase=W5.D1 layer=L_TOOLS fan_in=20 surface=State coverage_gap_pct=45.0 est_tokens=8000 reason=Batch-update Notion Plans and Wave/Phase Plan File paths from .windsurf/plans to .cursor/plans to clear drift gate orphans

DEFERRED_SCOPE: plan=NEW:windsurf-tree-deletion-ci-parity wave=W1 phase=W1.D1 layer=L_TOOLS fan_in=60 surface=Security coverage_gap_pct=25.0 est_tokens=25000 reason=Full .windsurf tree deletion after CI parity proof for hooks MCP and artifact namespace

DEFERRED_SCOPE: plan=windsurf-gha-cutover-d9f2a7 wave=W5 phase=W5.D2 layer=L_TOOLS fan_in=8 surface=Observability coverage_gap_pct=15.0 est_tokens=5000 reason=Re-home T7.7 windsurf-governance-health as optional Cursor advisory gate for .windsurf mirror cross-refs

DEFERRED_SCOPE: plan=windsurf-gha-cutover-d9f2a7 wave=W5 phase=W5.D3 layer=L_TOOLS fan_in=12 surface=Execution coverage_gap_pct=12.0 est_tokens=3000 reason=Re-run full run_contract_gates.py after windsurf-gha-cutover file churn for DoD-4 closure

DEFERRED_SCOPE: plan=windsurf-gha-cutover-d9f2a7 wave=W5 phase=W5.D4 layer=L_TOOLS fan_in=15 surface=Observability coverage_gap_pct=20.0 est_tokens=6000 reason=Rename artifacts/windsurf hook log namespace to artifacts/cursor with dual-read shim
```

---

## Summary table

| ID | Phase | Band (scored) | Title | Status |
|----|-------|---------------|-------|--------|
| D1 | W5.D1 | P3 | Notion plan path batch migration | ✅ DONE |
| D2 | W1.D1 | P3 | Full `.windsurf/` tree deletion | ⏸ OUT_OF_BAND — assessed only; `deletion_safe: false`; separate plan |
| D3 | W5.D2 | P4 | T7.7 governance health re-home | ✅ DONE |
| D4 | W5.D3 | P4 | Full contract-gates re-run | ✅ Ran (graph_layer pre-existing FAIL) |
| D5 | W5.D4 | P4 | Artifact namespace dual-write | ✅ DONE |

---

## Notion writeback

Rows posted to Wave/Phase Convergence DB via `post_cursor_agent_deferred_scope_capture.py` when `NOTION_TOKEN` is set. Local log: `artifacts/windsurf/deferred_scope_capture.jsonl` (or `artifacts/cursor/` if namespace migrated).
