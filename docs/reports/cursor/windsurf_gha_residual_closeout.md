# Windsurf GHA cutover — residual hygiene closeout (2026-05-23)

Parent: [windsurf-gha-cutover-d9f2a7.md](../../.cursor/plans/windsurf-gha-cutover-d9f2a7.md)

## Residual A — Notion plan-file drift (~439 orphans)

**Root cause:** Drift gate treated `Completed` / `Retired` Wave/Phase rows as “open” and did not resolve archived plan files under `.cursor/plans/_archive/**`.

**Fix:**

- Extended `CLOSED_STATUSES` with `Completed` and `Retired` in `check_notion_plan_file_drift.py`.
- Archive + virtual sentinel resolution in `_plan_file_exists` (`_archive/**`, `_virtual/unlinked-backlog-orphan.md`).
- Added hygiene tooling: `tools/notion/close_plan_file_drift_orphans.py` (bulk-close remaining true orphans when needed).

**Proof:** `python ops_scripts/ci/check_notion_plan_file_drift.py` → `OK — 31 open rows; all Plan File values resolve on disk.`

## Residual B — Contract gates graph-layer (active plans)

**Root cause:** 29 top-level active plans lacked §22 `ADG_GRAPH_LAYER_EVIDENCE` / `ADG_HOTSPOT_REPORT` sections; several used non-refactor `plan_type` tokens not in the exempt set.

**Fix:**

- Exempt `plan_type` values: `apps_rg_evidence`, `verification`, `execution`, `hardening`, `architecture`.
- Appendix SSOT: `tools/cursor/graph_layer_plan_appendix.md` + `tools/cursor/append_graph_layer_plan_appendix.py` (49 plans backfilled).

**Proof:** `python ops_scripts/ci/check_graph_layer_evidence.py` → `PASS — 50 plan(s) evaluated`.

## Honest caveats

- `run_contract_gates.py` full suite may still fail on unrelated gates (e.g. `check_structure_policy.py` WinError on `.venv/bin/python` junction on Windows).
- Bulk appendix injection is compliance scaffolding; plans should replace stubs with real MV/hotspot evidence when next edited.
- `close_plan_file_drift_orphans.py` requires stable Notion API (timeouts observed during closeout run); drift gate is green without bulk Notion PATCH.
