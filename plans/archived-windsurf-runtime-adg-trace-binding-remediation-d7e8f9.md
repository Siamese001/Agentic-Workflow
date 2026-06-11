---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-adg-trace-binding-remediation-d7e8f9.md'
original_relative_path: 'runtime-adg-trace-binding-remediation-d7e8f9.md'
source_sha256: c75ea0953b3cf3bc50358e4d78ab9f06ccc87c5c29f559d7bb6ef083aedc8732
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: runtime-adg-trace-binding-remediation-d7e8f9
plan_type: audit
---

# Runtime ADG Trace Binding Remediation (Planning Only)

- **Status**: Planning — Author-Gate pending
- **Authored**: 2026-05-02
- **Predecessor audit**: `.windsurf/plans/runtime-adg-coverage-audit-4f7a21.md`
- **Backlog row**: 1 P2 row (impact 297) — "runtime-adg trace binding remediation"

## Context (SCQA)

- **Situation** — the runtime ADG (populated from OTEL spans via `otel_ingest_to_runtime_adg`) accumulates spans but binding between spans and static-ADG nodes drifts. The audit plan surfaced the gap without scoping remediation.
- **Complication** — "trace binding" means ensuring every runtime span can be joined back to a `nodes.id` in the static snapshot. Drift causes `mv_runtime_proof_*` joins to silently drop rows, blurring the runtime proof surface that §32 Fort Knox and §29 closed-loop router depend on.
- **Question** — how to measure binding drift and set a ratchet that prevents further erosion?
- **Answer** — this plan scopes: (1) a measurement script emitting `bound / unbound / total` counts per span source, (2) a baseline threshold captured in `config/adg_trace_binding_baseline.yaml`, (3) a CI gate (`ops_scripts/ci/check_runtime_adg_trace_binding.py`) with ratchet semantics (unbound count may not increase vs baseline).

## Wave Structure

| Wave | Phase IDs | Focus | Tokens | Status |
|---|---|---|---:|---|
| W1 | P0 | Author-Gate approval of this plan | ~500 🟢 | Pending |
| W2 | P1 | Measurement script — `tools/runtime_adg/measure_trace_binding.py` | ~4 000 🟡 | Blocked on W1 |
| W3 | P2 | Baseline capture + `config/adg_trace_binding_baseline.yaml` | ~1 500 🟢 | Blocked on W2 |
| W4 | P3 | CI gate (T8s) + pre-commit + `run_contract_gates.py` dispatch | ~3 000 🟢 | Blocked on W3 |

## Out Of Scope

- Changes to `tools/runtime_adg/` ingest logic — that's the audit plan's surface, not remediation
- OTEL emitter changes — Phase D/E/F governance
- Scanner changes — Phase F

## Author-Gate Trade-offs

- **AG-1**: Baseline source — capture from a single 1-hour trace window, or aggregate over 7 days? ⭐ Recommended: 7-day window (more representative).
- **AG-2**: Ratchet strictness — hard-floor (fail on any regression) or tolerance (fail on >10% regression)? ⭐ Recommended: hard-floor, matches ADG gravity-ratchet pattern.

## Success Criteria

- [ ] Measurement script returns bound/unbound counts reproducibly
- [ ] Baseline captured with 7-day aggregate
- [ ] CI gate wired at T8s; defaults to advisory for first 7 days
- [ ] Notion row `runtime-adg-trace-binding-remediation` flips Completed

## References

- Parent audit: `.windsurf/plans/runtime-adg-coverage-audit-4f7a21.md`
- Runtime ADG MCP: `otel_mcp` (distinct from static `adg_sqlite` per `adg-canonical-invariants` §8)
- Tracker plan: `.windsurf/plans/d-bucket-w3-burndown-b3d5e2.md`
