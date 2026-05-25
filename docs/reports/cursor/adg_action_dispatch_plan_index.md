# ADG action dispatch — plan index

| Field | Value |
|-------|-------|
| **Plan slug** | `adg-action-dispatch-c9e4a2` |
| **Disk SSOT** | [.cursor/plans/adg-action-dispatch-c9e4a2.md](../../.cursor/plans/adg-action-dispatch-c9e4a2.md) |
| **Created** | 2026-05-25 |
| **Status** | Completed (Notion + disk) · **Hardening** APPLIED 2026-05-25 |
| **Problem** | ADG GraphDB/MV/report outputs do not inform next best action |
| **Solution** | Validated `adg_action_queue` + provenance digests + auditable ordering + deterministic hotspot linkage |

## Charter (non-negotiable)

- No `agentic_core` edits · No auto-repair · No TRACK mass cleanup · No gate weakening
- W3 Notion is optional, not ADG certification

## Waves (summary)

| Wave | Deliverable |
|------|-------------|
| W0 | ✅ Playbook + `adg-post-run-burndown.mdc` (2026-05-25) |
| W1 | ✅ Queue + schema + 7 tests + `generate_full_adg` hook |
| W2 | ✅ Hotspot linkage + burndown `## Next action` (2026-05-25) |
| W3 | ✅ `adg_fix_backlog_sync.py` (FIX only; SKIP on missing token) |

## Hardening highlights

1. Provenance: per-input `snapshot_ts`, `digest_sha256`, `status` (present/missing/stale/rejected)
2. Ordering: `sort_bucket`, `sort_band`, `ordering_reason` on every action row
3. TRACK never in `actions[]`; rank-1 FIX preserved under cap
4. Stale `adg_failure_clusters.json` rejected from merge
5. Closeout receipt with `NON_CLAIMS` block

## Related artifacts (baseline)

- [adg_burndown_report.md](../../artifacts/adg/adg_burndown_report.md) — FIX=8, TRACK=17 (2026-05-25)
- [adg-analysis-procedures.mdc](../../.cursor/rules/adg-analysis-procedures.mdc) — P7 routing, repair litmus
- App hotspots: `docs/reports/adg/apps_*_hotspots_*.md`

## Playbook (W0 — DONE)

[adg_action_dispatch_playbook.md](adg_action_dispatch_playbook.md) — 15-min triage ladder, P7 routing, testing hotspots, 2026-05-25 FIX baseline, TRACK deferral.

Post-run rule: [adg-post-run-burndown.mdc](../../.cursor/rules/adg-post-run-burndown.mdc)
