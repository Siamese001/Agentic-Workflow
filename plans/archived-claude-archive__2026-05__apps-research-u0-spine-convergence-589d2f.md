---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-research-u0-spine-convergence-589d2f.md'
original_relative_path: '_archive\\2026-05\\apps-research-u0-spine-convergence-589d2f.md'
source_sha256: dbbd12171b9aba9a475bef778b1a2d83988cdce11454dbdacd90e02d4b870260
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-research-u0-spine-convergence-589d2f
plan_type: refactor
status: Completed
authored_at: 2026-05-20
dod_exempt: false
---

# apps_research U0 Profile Spine Convergence

Converge the default `apps_research` product CLI onto the governed **U0 → profile spine** (`AppIngressRunner` + `build_app_runtime_contract()`), delete Phase 0–1 shadow entry files, prove with governance tests and stub runtime, and ship wave-scoped commits.

## Waves (merged session)

| Phase | ID | Outcome |
|-------|-----|---------|
| Convergence | W-AR-U0-1 | Default CLI → profile spine; Phase 0–1 deletes; PA/L2 fixes |
| Scope hygiene | W-AR-U0-2 | Revert `apps_qna` / `apps_lic` / binding drift from staged index |
| Commit-ready | W-AR-U0-3 | 161+ pytest + stub CLI PASS; staged index clean |
| Git sync | W-AR-U0-4 | `59385f10de` pushed `origin/main`; closeout docs `589d2fc30b` |

## Success criteria (met)

- `python -m apps_research --topic ...` uses `AppIngressRunner` and `u0_validate_apps_research`
- Governance tests block legacy `_run_canonical` / capability-registry default path
- `check_no_shadow_spine.py` NC-4 pass (dispatch tombstone retained)
- Wave-scoped commit only (no `apps_qna` / `apps_rg` leakage)

## Non-goals (deferred)

- Phase 3 deletions (`GovernedResearchRun`, `research_capability_registry`, orchestrators)
- Live provider / release-eligibility proof
- Dispatch tombstone removal

## Evidence (disk)

- [apps_research_u0_spine_convergence_closeout_receipt.md](../docs/reports/apps_research/apps_research_u0_spine_convergence_closeout_receipt.md)
- [apps_research_u0_spine_scope_hygiene_closeout_receipt.md](../docs/reports/apps_research/apps_research_u0_spine_scope_hygiene_closeout_receipt.md)
- [apps_research_u0_spine_commit_ready_receipt.md](../docs/reports/apps_research/apps_research_u0_spine_commit_ready_receipt.md)
- [chat_session_waves_closeout_20260520.md](../docs/reports/apps_research/chat_session_waves_closeout_20260520.md)
- [chat_session_waves_manifest_20260520.json](../docs/reports/apps_research/chat_session_waves_manifest_20260520.json)

## Commits

- `59385f10de` — apps_research: converge default CLI onto U0 profile spine
- `589d2fc30b` — docs(apps_research): session wave closeout and manifest
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
