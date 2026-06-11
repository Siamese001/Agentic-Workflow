---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-adg-coverage-audit-4f7a21.md'
original_relative_path: 'runtime-adg-coverage-audit-4f7a21.md'
source_sha256: e76c3e795799a6cdb7e0389fe0c94bb1cbf345d6bb83410d69189ec30dda55bf
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Runtime ADG Coverage Audit

**Slug**: `runtime-adg-coverage-audit-4f7a21`
**Status**: Active
**Tier**: T2 (diagnostic; read-only across 3 file trees)
**Owner**: Cascade
**Created**: 2026-04-23

## Context

Post-cleanup gap analysis (2026-04-23) flagged the Runtime ADG subsystem as
"unclear if coverage is complete": `artifacts/otel/` didn't exist and the
visible backend at `agentic_core/L4_state/memory/runtime_adg/` appeared thin.

Deeper probe reveals:

- **Snapshots on disk**: 89 content-addressed `.json` files under
  `agentic_core/L4_state/memory/runtime_adg/<hash[:2]>/<hash>.json`
  (total 100 KB, oldest 2026-04-13, newest 2026-04-23 11:37)
- **`_index.json`**: 89 version-id → content-hash entries ✅
- **`_trace_index.json`**: only **2 entries** — one is an empty-string key
  (schema violation) and one real trace ID

**The real gap**: 88 of 89 persisted snapshots have **no `trace_id` binding**.
They were committed via a path that did not call `_trace_index[trace_id] = version_id`.

## Goal

Produce a read-only coverage report that answers:

1. Which code paths commit snapshots to `FileBackedRuntimeADGStore.persist()`?
2. Of those, which pass a valid `trace_id` and which leave it blank?
3. Which agents in the repo emit OTEL spans at all?
4. Which trace IDs exist in the trace-index and match snapshots on disk?
5. What is the expected emitter set vs the actual emitter set?

**Out of scope**: wiring missing emitters. That becomes a separate remediation
wave if coverage gaps are material.

## Method

Pure static analysis + on-disk inspection. No MCP writes, no code changes
in `agentic_core/` or `apps_*/`.

### Phase 1 — Emitter inventory

Enumerate in `agentic_core/**/*.py` and `apps_*/**/*.py`:
- Agent classes (class names ending in `Agent`)
- `get_tracer(` call-sites
- `start_span(` / `as_current_span(` call-sites
- `record_execution_trace(` / `emit_*` call-sites from
  `agentic_core.runtime.contracts.lifecycle_trace_contract`
- Direct calls to `FileBackedRuntimeADGStore.persist(`

### Phase 2 — Trace-index integrity

Read `_index.json` and `_trace_index.json` in
`agentic_core/L4_state/memory/runtime_adg/`. Validate:
- Every `_trace_index.json` value exists as a key in `_index.json`
- Every `_index.json` value has a corresponding content-addressed file on disk
- Count unbound snapshots (in `_index.json`, not in `_trace_index.json`)

### Phase 3 — Snapshot schema sampling

Sample N=5 random snapshot files. Report:
- Whether each has `trace_id`, `snapshot_id`, `nodes`, `edges`
- Which agent/tool produced it (inferable from node content)

### Phase 4 — Report

Write `docs/reports/runtime_adg_coverage_<timestamp>.md` with:
- Expected vs actual emitter set
- Trace-index integrity findings
- Snapshot schema compliance rate
- Gap classification (P1/P2/P3) per the Deferred Scope scorer

## Deliverables

1. `tools/debug/_runtime_adg_coverage_audit.py` — diagnostic tool (new, read-only)
2. `docs/reports/runtime_adg_coverage_<ts>.md` — findings (new)
3. Notion Wave/Phase Convergence row per `DEFERRED_SCOPE:` markers emitted by the audit
4. (If findings warrant) a follow-up remediation plan slug — NOT in this plan's scope

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | W1.P1 | Emitter inventory + trace-index integrity + report | 6000 | Active |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Coverage audit | `tools/debug/`, `docs/reports/`, read-only scan of `agentic_core/`, `apps_*/`, `system_learning/` | Finding emit sites among many candidates; distinguishing live from dead code | 6000 | Active |

## Success Criteria

- Audit tool runs cleanly with exit 0
- Report is written to `docs/reports/runtime_adg_coverage_<ts>.md`
- Coverage numbers (expected emitters, actual emitters, bound/unbound snapshots) are cited
- Notion row posted with P-band computed from Deferred Scope scorer

## Status Notes

Runtime ADG is a diagnostic subsystem. A coverage gap here means meta-learning
and healing-chain analysis are running on incomplete data. Material if any P0
loss-of-trace scenario is possible.
