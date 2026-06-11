---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-adg-tier1-trace-binding-c9b84d.md'
original_relative_path: 'runtime-adg-tier1-trace-binding-c9b84d.md'
source_sha256: 01b0cd9eb6a4ade8dbd9679a668aedeeca33559f1333298c8d04e01398f33e45
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Runtime ADG Tier 1 — Trace-Binding Remediation

**Slug**: `runtime-adg-tier1-trace-binding-c9b84d`
**Status**: Active
**Tier**: T2 (focused; 4 files in the critical path, plus back-fill script + tests)
**Created**: 2026-04-23
**Parent audit**: `.windsurf/plans/runtime-adg-coverage-audit-4f7a21.md`

## Root Cause (confirmed from audit)

`@c:/Git/Agentic-Workflow/system_learning/runtime_adg/store.py:145-152`:

```python
def persist(self, snapshot: RuntimeADGSnapshot) -> str:
    version_id = self._version_store.commit_change_package(snapshot)
    if snapshot.trace_id not in self._trace_index:    # ← THE BUG
        self._trace_index[snapshot.trace_id] = version_id
        ...
```

The *very first* snapshot persisted had `trace_id=""`. That put `""` into
`_trace_index.json`. Every subsequent empty-trace snapshot — 88 of them —
found `"" in self._trace_index == True` and was silently skipped by the
index update. The snapshot file was still written to L4, but never bound.

This is not a "missing feature." It is a correctness bug that has been
silently accumulating orphaned snapshots for 10 days.

## Tier 1 Span Categories (what "done" means)

Per `@c:/Git/Agentic-Workflow/docs/reference/Runtime ADG and OTEL Spans.md`,
Tier 1 is the **correlation spine**: 5 span categories that every run MUST
emit for the runtime ADG to be reconstructible.

| # | Category | Required attrs (minimum) |
|---|---|---|
| 1 | `runtime.trace_root` | `trace_id`, `run_id`, `parent_span_id=null`, `input_envelope_hash` |
| 2 | `L0.route.select` | `selected_route`, `reason_codes`, `confidence`, `cache_decision` |
| 3 | `L2.step.seal` | `output_hash`, `evidence_ids`, `lineage_hash`, `replay_key` |
| 4 | `L2.model.invoke` OR `L2.tool.invoke` | `model_id`/`tool_name`, `prompt_hash`/`args_hash`, `output_hash`/`return_code` |
| 5 | `Exit.disposition` | `exit_disposition`, `policy_hash`, `reason_codes` |

Tier 1 scope does NOT require wiring new emit sites across the codebase.
It requires (a) fixing the storage bug so existing emits are correctly
bound, and (b) a **validation contract** that flags snapshots missing
any of the 5 categories.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | W1.P1, W1.P2, W1.P3, W1.P4 | Guardrail + bug fix + span contract + back-fill | 10000 | Active |
| W2 | W2.P1 | Tests + coverage re-audit + Notion update | 3000 | Active |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Persist guardrail | `system_learning/runtime_adg/store.py` — reject empty trace_id + empty payload; fix first-write-wins bug; drop stale "" key | Back-compat: existing callers may rely on broken behavior; solution is `force=True` escape hatch for migration only | 3000 | Active |
| W1.P2 | Tier 1 span contract | New `system_learning/runtime_adg/span_contracts.py` with `validate_tier1_coverage(snapshot)` | Tier 1 category detection from span names — needs fuzzy matching against existing lifecycle contract emissions | 2500 | Active |
| W1.P3 | Back-fill script | New `tools/runtime_adg/backfill_trace_index.py` — scan 89 snapshots, extract real trace_id from payload, rebuild `_trace_index.json`, archive empties | Canonical bytes parser already exists; leverage `_deserialise_snapshot` | 2500 | Active |
| W1.P4 | Wire validator into persist | `store.py` accepts optional `strict_tier1: bool` param; logs violations but doesn't block | Avoid noisy logs in production during rollout | 2000 | Active |
| W2.P1 | Verification | Re-run `_runtime_adg_coverage_audit.py`; success = `trace_unbound_pct < 5%`, `0% empty payloads`, `Tier 1 coverage > 80%` | — | 3000 | Active |

## Success Criteria

1. `persist()` raises on `trace_id == ""` unless `allow_unbound=True` (migration only)
2. `persist()` raises on `nodes == 0 AND edges == 0` unconditionally
3. `_trace_index.json` has 0 empty-string keys and 0 empty-string values
4. Back-fill recovers trace_id from any snapshot whose payload header contains a non-empty `trace_id`
5. `validate_tier1_coverage()` returns `dict[category -> bool]` for any snapshot
6. Audit re-run: `trace_unbound_pct < 5%`, `empty_payload_sample_rate == 0%`
7. All existing `persist()` callers pass (3 sites) — no regression
8. 100% new code has tests

## Out of Scope

- Wiring new `runtime.trace_root` emit sites in intake paths (deferred to Tier 1.5)
- Back-filling attribute contracts (`run_id`, `input_envelope_hash`, etc.) in existing snapshots — they were never captured, cannot be synthesized
- Tier 2/3 spans (model.invoke, tool.invoke, Exit.disposition detail spans) — deferred
- L6 eval, meta-learning, cost telemetry (Tier 4 — not in scope)

## Files Touched

| File | Action |
|---|---|
| `system_learning/runtime_adg/store.py` | Patch (guardrail + bug fix) |
| `system_learning/runtime_adg/span_contracts.py` | New |
| `tools/runtime_adg/backfill_trace_index.py` | New |
| `tests/unit/system_learning/runtime_adg/test_store_guardrail.py` | New |
| `tests/unit/system_learning/runtime_adg/test_span_contracts.py` | New |
| `tests/unit/tools/runtime_adg/test_backfill_trace_index.py` | New |
