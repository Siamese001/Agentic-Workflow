---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\runtime-otel-spec-coverage-7c4d2a.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\runtime-otel-spec-coverage-7c4d2a.md'
source_sha256: fc814599232f7b27ee8fc0538222d7db3e1a20407a3dcfeaaabc7c1ad2fe089f
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime OTEL Spec Full Coverage — 7c4d2a

**Goal**: Implement every row from `docs/reference/Runtime ADG and OTEL Spans.md`
as formal SSOT semconv constants + Tier 2 contracts + emit helpers + tests.

## Source-of-Truth

`docs/reference/Runtime ADG and OTEL Spans.md` — 13 stages, ~80 spans, ~150 attrs.

## Existing Implementation (gap analysis)

| Stage | semconv | Tier 1 contract | Emitter |
|---|:---:|:---:|:---:|
| trace_root | ❌ | ✅ | ✅ |
| U0 intake | ❌ | partial | ❌ |
| L1 reasoning | ❌ | ❌ | ❌ |
| L0 route | ❌ | ✅ (select only) | ❌ |
| Direct path | ❌ | ❌ | ❌ |
| L3 orchestration | ❌ | ❌ | ❌ |
| C0 retrieval | ✅ (rag.py) | partial | external |
| Prompt assembly | ❌ | ❌ | ❌ |
| L2 execution | ❌ | ✅ (seal+invoke) | ✅ (seal) |
| Exit eval | ❌ | ✅ (disposition only) | ✅ (disposition) |
| Response | ❌ | ❌ | ❌ |
| UWG/L4 commit | ❌ | ❌ | ❌ |
| L6 eval | ❌ | ❌ | ❌ |
| Meta-learning | ❌ | ❌ | ❌ |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | 1.1 | semconv/runtime.py SSOT for all 13 stages | 8000 | rag.py pattern reused | Todo | All span/attr/node/edge constants exist; importable |
| W2 | 2.1 | span_contracts.py Tier 2 (additive) | 4000 | preserve Tier 1 backward compat | Todo | validate_tier2_coverage works on existing snapshots |
| W3 | 3.1 | runtime_span_emitter.py — 8 new emit helpers | 5000 | follow existing fail-open pattern | Todo | emit_intake/L1/PA/L3/Response/Commit/Eval/MetaLearning all produce correct spans |
| W4 | 4.1 | Unit tests for semconv + contracts + emitters | 5000 | pytest_mcp baseline | Todo | All new tests green |
| W5 | 5.1 | Doc cross-check test (parse spec, assert each row implemented) | 2500 | regex over ASCII boxes | Todo | Test asserts 100% spec coverage |
| W6 | 6.1 | Coverage gate Tier 2 report extension | 2000 | audit-only, no enforce | Todo | `--tier2` flag prints stage matrix |
| W7 | 7.1 | pytest scoped run, commit, push | 2000 | no regressions | Todo | All new tests pass; pushed to origin/main |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | semconv/runtime.py | 1 new file ~600 lines | Avoid name collision with rag.py | 8000 | Todo |
| 2.1 | Tier 2 contracts | span_contracts.py (additive) | Backward compat | 4000 | Todo |
| 3.1 | Emit helpers | runtime_span_emitter.py (additive) | Fail-open discipline | 5000 | Todo |
| 4.1 | Unit tests | tests/unit/agentic_core/L6_observability/semconv/, tests/unit/system_learning/runtime_adg/ | None | 5000 | Todo |
| 5.1 | Doc cross-check | tests/unit/.../test_spec_coverage.py | Spec ASCII parsing | 2500 | Todo |
| 6.1 | CI gate Tier 2 | check_runtime_adg_coverage.py | None | 2000 | Todo |
| 7.1 | Verify + commit + push | git | None | 2000 | Todo |

## ADG_GRAPH_LAYER_EVIDENCE

This plan is purely additive (semconv constants, contract registrations, emit helpers,
tests). It does not change any L0..L6 import topology or P-classification. ADG snapshot
`adg_indexed_04252026_0843.sqlite` (Redis hot) confirms `agentic_core/L6_observability/semconv/`
has fan_in=12 from RAG emitters; this plan extends that surface but does not alter callers.
No mv_* shifts expected; no semantic edges affected; no v_p* matches.

## ADG_HOTSPOT_REPORT

| Target | Layer | Fan-in | Archetype | Surface | Impact | Notes |
|---|---|---|---|---|---|---|
| semconv/runtime.py | L6 | 0 (new) | OBSERVABILITY | Observability | low | New SSOT, additive |
| span_contracts.py | L7 (system_learning) | 4 | SAFETY_GATEKEEPER | Observability | low | Tier 2 additive |
| runtime_span_emitter.py | L7 | 6 | ORCHESTRATOR | Observability | low | New helpers additive |
