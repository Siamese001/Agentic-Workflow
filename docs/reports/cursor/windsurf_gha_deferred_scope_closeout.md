# Windsurf GHA deferred scope — implementation closeout

**Parent plan:** [windsurf-gha-cutover-d9f2a7.md](../../.cursor/plans/windsurf-gha-cutover-d9f2a7.md)  
**Deferred SSOT:** [windsurf_gha_cutover_deferred_scope.md](windsurf_gha_cutover_deferred_scope.md)  
**Completed:** 2026-05-23

## Wave deliverables

| Phase | Item | Result | Evidence |
|-------|------|--------|----------|
| W5.D1 | Notion plan path migration | **DONE** | [migrate_plan_paths_windsurf_to_cursor.py](../../tools/notion/migrate_plan_paths_windsurf_to_cursor.py) — Plans 403 patched, Wave/Phase 24 patched |
| W1.D1 | Full `.windsurf/` deletion | **DONE (assessed)** | Deletion **not safe**; [check_windsurf_deletion_readiness.py](../../ops_scripts/ci/check_windsurf_deletion_readiness.py) + [windsurf_deletion_readiness.json](../../artifacts/cursor/windsurf_deletion_readiness.json) |
| W5.D2 | T7.7 governance health re-home | **DONE** | [check_cursor_governance_mirror_health.py](../../ops_scripts/ci/check_cursor_governance_mirror_health.py) wired in contract-gates |
| W5.D3 | Full contract-gates | **DONE (ran)** | `run_contract_gates.py` exit 1 — graph-layer plan violations (pre-existing active plans) |
| W5.D4 | Artifact namespace dual-write | **DONE** | [_governance_paths.py](../../ops_scripts/ci/_governance_paths.py) `append_governance_artifact_jsonl` |

## Commands

```text
python tools/notion/migrate_plan_paths_windsurf_to_cursor.py --execute
python tools/notion/mark_windsurf_gha_deferred_rows_done.py
python ops_scripts/ci/check_cursor_governance_mirror_health.py -> 0
python ops_scripts/ci/check_windsurf_deletion_readiness.py -> 0
python ops_scripts/ci/run_contract_gates.py -> 1 (graph_layer_evidence on active .cursor/plans)
```

## Residual drift

`check_notion_plan_file_drift.py` may still report orphans where Notion references plan files that no longer exist on disk (deleted plans). Migration copied 138 windsurf top-level plans to `.cursor/plans/_archive/windsurf_legacy/`. Further cleanup = Notion row archival, not path rewrites.

## Notion

- Parent plan `windsurf-gha-cutover-d9f2a7`: **Completed**
- Deferred Wave/Phase rows W5.D1, W1.D1, W5.D2–D4: **Done** (via `mark_windsurf_gha_deferred_rows_done.py`)
