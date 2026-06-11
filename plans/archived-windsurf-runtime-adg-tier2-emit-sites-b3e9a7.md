---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-adg-tier2-emit-sites-b3e9a7.md'
original_relative_path: 'runtime-adg-tier2-emit-sites-b3e9a7.md'
source_sha256: 823132be4014032972c2a3e305241f8f0ab2065cc4c9a78bf93f61f2809c6cb2
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Runtime ADG Tier 2 — Close the 3 Emit-Site Gaps

**Slug**: `runtime-adg-tier2-emit-sites-b3e9a7`
**Status**: Active
**Tier**: T2
**Created**: 2026-04-23
**Parent**: `runtime-adg-tier1-5-span-naming-a31bcf`

## Empirical Finding (from Tier 1.5)

After Tier 1.5 calibration, the audit reports **0 name_mismatches** and **3 emit_site_gaps**. These are real architectural holes — the spans simply are not being emitted anywhere in the runtime.

| Category | Status | Fix |
|---|---|---|
| `runtime.trace_root` | 🔴 GAP | Emit at orchestrator entry with `trace_id`/`run_id`/`input_envelope_hash` |
| `L2.step.seal` | 🔴 GAP | Helper for per-step seal with `output_hash`/`evidence_ids`/`replay_key` |
| `Exit.disposition` | 🔴 GAP | Emit at orchestrator exit with `exit_disposition`/`policy_hash`/`reason_codes` |

## Scope

Add a thin emitter module that writes spans directly into the adapter's `_completed_spans` list (no OTel dependency — deterministic regardless of env). Wire `trace_root` + `exit.disposition` into `AutoPersistenceTracingAdapter.trace_orchestrator()` so every run gets them automatically. Provide `seal_step()` as an opt-in helper for per-step callers.

## Success Criteria

1. After Tier 2, audit reports **Tier 1 satisfied ≥ 4/5** (80%) — trace_root and exit.disposition auto-emitted, seal_step exercised via integration test
2. A single run of `trace_orchestrator()` appends 3 new runtime-ADG-compliant spans to the completed list
3. Unit tests cover all 3 emit helpers
4. Integration test demonstrates the full flow: orchestrator context → drain → materialize → validate_tier1_coverage ≥ 3/5
5. No regression on existing 82 tests

## Out of Scope

- Rewiring every `*Agent` to call `seal_step` (Tier 3)
- Real OTel attribute emission (current system uses internal span records, fine as-is)
- Full attribute depth (Tier 2.5)

## Files Touched

| File | Action |
|---|---|
| `system_learning/runtime_adg/runtime_span_emitter.py` | New: 3 emission helpers |
| `system_learning/runtime_adg/auto_persistence.py` | Patch: wire trace_root/exit.disposition into trace_orchestrator |
| `tests/unit/system_learning/runtime_adg/test_runtime_span_emitter.py` | New tests |
| `tests/integration/system_learning/runtime_adg/test_tier1_coverage_e2e.py` | New e2e |
