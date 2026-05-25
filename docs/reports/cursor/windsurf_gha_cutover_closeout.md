# Windsurf GitHub Actions cutover — closeout

**Plan:** [windsurf-gha-cutover-d9f2a7.md](../../.cursor/plans/windsurf-gha-cutover-d9f2a7.md)  
**Completed:** 2026-05-23  
**Metadata reconcile:** [windsurf_gha_metadata_reconcile_20260525_receipt.md](windsurf_gha_metadata_reconcile_20260525_receipt.md) (2026-05-25)  
**Notion page:** `36927693-f55c-81eb-a9a1-d9955c280b83`

## Summary

Retired tombstone GitHub Actions under `.github/workflows/_deleted/`, migrated live CI and workflows to `.cursor/` SSOT for plans and Author-Gate harness paths, and documented remaining `.windsurf/` dependencies (MCP/hooks schema gates, artifact namespace).

## Wave evidence

| Wave | Result | Proof |
|------|--------|-------|
| W0 | PASS | [windsurf_gha_inventory.json](windsurf_gha_inventory.json) |
| W1 | PASS | `_deleted/` removed; `check_windsurf_governance.py` absent |
| W2 | PASS | `author-gate-gates.yml`, `notion-plan-file-drift-nightly.yml`, `apps-e2e-harness-nightly.yml` updated |
| W3 | PASS | Plan gates use `.cursor/plans/`; [_governance_paths.py](../../ops_scripts/ci/_governance_paths.py) |
| W4 | PASS | Author-Gate workflow runs `.cursor/scripts` + `.cursor/state` only |
| W5 | PASS | This receipt |

## Files changed (high signal)

- Removed: `.github/workflows/_deleted/**` (8 YAML files)
- Added: `ops_scripts/ci/_governance_paths.py`, `docs/reports/cursor/windsurf_gha_inventory.json`
- Workflows: `author-gate-gates.yml`, `notion-plan-file-drift-nightly.yml`, `apps-e2e-harness-nightly.yml`
- CI: `check_notion_plan_file_drift.py`, `check_plan_*`, `check_wave_marker_emission.py`, `check_waiver_provenance.py`, `run_contract_gates.py` (skills dir)
- Docs: precommit analysis, p1_p4 breakdown, pre-commit migration notes

## Commands run

```text
Remove-Item -Recurse .github/workflows/_deleted  -> OK
pytest tests/unit/ops_scripts/ci/test_check_windsurf_config_schema.py ... -o addopts=  -> 77 passed
python ops_scripts/ci/check_notion_plan_file_drift.py  -> exit 0 (advisory drift rows; NOTION_TOKEN set)
```

## Still requires `.windsurf/` (intentional)

| Item | Reason |
|------|--------|
| `check_windsurf_config_schema.py` | Constitutional §27 — `.windsurf/hooks.json` + `mcp_config.json` |
| `check_mcp_editor_parity.py` | Cursor ↔ Windsurf MCP mirror |
| `artifacts/windsurf/*` | Hook violation logs; rename deferred |
| `.windsurf/plans/` archive | Historical plans; active SSOT is `.cursor/plans/` |
| `check_graph_layer_evidence` baseline | Dual-prefix normalization for archived paths |

## Deferred scope

Captured to [windsurf_gha_cutover_deferred_scope.md](windsurf_gha_cutover_deferred_scope.md) with five `DEFERRED_SCOPE:` markers (Notion Wave/Phase rows auto-posted when token present).

| Phase | Band | Item |
|-------|------|------|
| W5.D1 | P3 | Notion plan path batch migration |
| W1.D1 | P3 | Full `.windsurf/` tree deletion (new plan) |
| W5.D2 | P4 | T7.7 governance health re-home |
| W5.D3 | P4 | Full `run_contract_gates.py` (DoD-4) |
| W5.D4 | P4 | `artifacts/windsurf` → `artifacts/cursor` rename |

## Definition of Done

| DoD | Status |
|-----|--------|
| DoD-1 Tombstone workflows removed | PASS |
| DoD-2 Plan drift uses `.cursor/plans/` | PASS |
| DoD-3 Targeted pytest | PASS (77) |
| DoD-4 Full contract-gates | PARTIAL — not re-run full suite in this session |
| DoD-5 Closeout + Notion Completed | PASS |
