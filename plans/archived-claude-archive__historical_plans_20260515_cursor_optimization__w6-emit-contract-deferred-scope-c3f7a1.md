---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\w6-emit-contract-deferred-scope-c3f7a1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\w6-emit-contract-deferred-scope-c3f7a1.md'
source_sha256: fac6418ff395afe8f635776430553b66259a129e99c404abf5728bec36d66e07
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
slug: w6-emit-contract-deferred-scope-c3f7a1
status: Completed
parent_plan: w6-emit-contract-enrichment-d8b2a4
created: 2026-05-10
dod_exempt: true
---

# Deferred Scope — W6 Emit-Contract Enrichment

> **Parent plan**: `w6-emit-contract-enrichment-d8b2a4` (Completed 2026-05-10)
> **Purpose**: Capture all items explicitly deferred from the W6 umbrella plan for future implementation.
> **This plan is documentation only — do not implement any wave without explicit user direction.**

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | 1.1–1.N | `apps_*` caller wiring — thread new fields through each app's pipeline | ~30K | Per-app plans required; not batch-able | 🔲 TODO | All `apps_*` callers pass new contract fields; no test regressions per app |
| W2 | 2.1 | Serialized-artifact migration for `artifacts/certification/` + `certification/agentic_core/` | ~8K | Backward-compat is read-side only (W6 §10) | 🔲 TODO | Existing JSON artifacts include new fields without breaking schema validators |
| W3 | 3.1 | Performance regression analysis (cross-cutting, deferred until all waves landed) | ~5K | W6 §10 says deferred until all waves land — now met | 🔲 TODO | Benchmark shows <5% overhead vs pre-W6 baseline on hot path |
| W4 | 4.1 | Cross-process serialization wire format upgrades | ~10K | Separate plan per §10 | 🔲 TODO | Wire format versioning documented + migration path proven |
| W5 | 5.1 | L5 doctrine output `previous_certification_ref` redesign | ~8K | Reused as-is per §10; separate plan when doctrine evolves | 🔲 TODO | `previous_certification_ref` semantics aligned with new `l5_certification_ref` field shape |
| W6 | 6.1 | Additional per-concern CI gates (W0 D12 chose umbrella; individual gates deferred) | ~6K | Up to 8 additional gates (one per concern beyond the W6ECE1 umbrella) | 🔲 TODO | Per-concern gates registered and green in `run_contract_gates.py` |
| W7 | 7.1 | Runtime certification claims on enriched contracts (Constitutional §32) | ~10K | Requires separate Author-Gate per §10 | 🔲 TODO | Author-Gate packet filed; certification claims gated via `compile_requirement_signoff.py` |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS / PARTIAL · ✅ DONE · ❌ BLOCKED

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | apps_rg caller wiring | `apps_rg/` layer bindings + `tests/_apps_contract/` | apps_rg pipeline already wired (d4e8a1); incremental field threading only | ~5K | 🔲 TODO |
| 1.2 | apps_qna caller wiring | `apps_qna/` layer bindings + contract tests | apps_qna has minimal contract coverage | ~4K | 🔲 TODO |
| 1.3 | apps_research caller wiring | `apps_research/` layer bindings + contract tests | Low contract coverage; OTEL spine partial | ~4K | 🔲 TODO |
| 1.4 | apps_lic caller wiring | `apps_lic/` layer bindings + contract tests | Complex multi-step pipeline; replay_key esp. relevant | ~5K | 🔲 TODO |
| 1.5 | apps_eval caller wiring | `apps_eval/` layer bindings + contract tests | Eval engines produce FinalEvidenceContract | ~4K | 🔲 TODO |
| 1.6 | apps_rfp caller wiring | `apps_rfp/` layer bindings + contract tests | HOP assembly uses RouteContract heavily | ~4K | 🔲 TODO |
| 1.7 | apps_underwriting_ai caller wiring | `apps_underwriting_ai/` layer bindings | Decision packet feeds CommitRequest | ~4K | 🔲 TODO |
| 2.1 | Serialized-artifact backward-compat migration | `artifacts/certification/`, `certification/agentic_core/` | Read-side only; no schema breaking changes | ~8K | 🔲 TODO |
| 3.1 | Performance regression baseline + analysis | Hot-path benchmark harness | Needs baseline captured pre-W6 (stale if delayed) | ~5K | 🔲 TODO |
| 4.1 | Cross-process wire format versioning | New serialization spec + migration helpers | Touches all emit contracts across process boundaries | ~10K | 🔲 TODO |
| 5.1 | `previous_certification_ref` redesign | `agentic_core/L5_safety/` doctrine layer | Requires L5 doctrine evolution plan; high risk | ~8K | 🔲 TODO |
| 6.1 | Per-concern CI gates (concern #1 tenant_id) | `ops_scripts/ci/check_w6_concern1_tenant_id.py` | W6ECE1 umbrella already covers; per-concern adds depth | ~2K | 🔲 TODO |
| 6.2–6.8 | Per-concern CI gates (concerns #3–#9) | One gate file per concern | Each gate ~100 lines; low individual risk | ~8K | 🔲 TODO |
| 7.1 | Runtime certification claims Author-Gate + implementation | `certification/` + Constitutional §32 path | AG packet required before any claims; high governance overhead | ~10K | 🔲 TODO |

---

## Deferred Item Register

### D1 — `apps_*` caller wiring (7 apps)
**From**: parent plan §10 Non-Goals: "Implementing `apps_*` callers' use of the new fields (each app's pipeline glue is a separate plan per app)."
**Scope**: All 7 apps (`apps_rg`, `apps_qna`, `apps_research`, `apps_lic`, `apps_eval`, `apps_rfp`, `apps_underwriting_ai`) need pipeline-glue threads for the 9 new concern field sets.
**Action**: Create a per-app sub-plan for each app to wire the fields through their layer bindings and verify via `tests/_apps_contract/`.
**Gate evidence required**: Each app's `tests/_apps_contract/test_<app>_*.py` passes with new fields present.

### D2 — Serialized-artifact migration
**From**: parent plan §10 Non-Goals: "Migrating existing serialized artifacts under `artifacts/certification/` or `certification/agentic_core/` to include the new fields — backward-compat is read-side only."
**Scope**: JSON artifacts that were serialized before W6 fields were added will lack the new fields. Read-side defaults (empty strings, empty tuples) protect against crashes, but audit tooling that expects completeness will flag gaps.
**Action**: After all apps are wired (D1), run a batch migration to backfill the new fields in existing artifacts with their default values. Validate with schema validators.

### D3 — Performance regression analysis
**From**: parent plan §10 Non-Goals: "Performance regression analysis (deferred until all waves land)."
**Scope**: W1–W8 added fields to frozen dataclasses with `slots=True`. The overhead per-instantiation is expected to be negligible, but a benchmark harness should verify on the hot path (L0 route evaluation, L2 execution, L3 orchestration).
**Action**: Benchmark hot-path contract instantiation before and after W6 enrichment. Acceptable threshold: <5% overhead. Instrument via `tests/benchmarks/` or `pytest-benchmark`.
**Note**: Baseline must be captured against a pre-W6 commit (e.g., `b2a23ba0de`) to be meaningful.

### D4 — Cross-process serialization wire format upgrades
**From**: parent plan §10 Non-Goals: "Cross-process serialization wire format upgrades (separate plan)."
**Scope**: When contracts are serialized across process boundaries (e.g., via Redis, gRPC, or JSON-over-HTTP), the new fields need versioned wire format support so old readers don't fail on new writers.
**Action**: Author a separate plan covering: (a) wire format version enum, (b) forward/backward-compat serialization helpers, (c) migration tests.

### D5 — `previous_certification_ref` redesign
**From**: parent plan §10 Non-Goals: "L5 doctrine output `previous_certification_ref` redesign — reused as-is."
**Scope**: `previous_certification_ref` in L5 doctrine output uses a different field shape than the new `l5_certification_ref` standardized across all 11 contracts. They serve different purposes (audit trail vs live cert authority), but the naming divergence creates confusion.
**Action**: When L5 doctrine evolves, align `previous_certification_ref` semantics with the `l5_certification_ref` shape (or document the intentional divergence in ADR-084 §Consequences).

### D6 — Per-concern CI gates (concerns #1, #3–#9)
**From**: parent plan W0 D12 decision: "one umbrella gate (W6ECE1) vs nine per-concern gates" — umbrella chosen.
**Scope**: W6ECE1 (`check_w6_emit_contract_enrichment.py`) covers all 9 concerns in a single structural scan. Per-concern gates would add semantic depth (e.g., verify tenant_id propagation at runtime, verify HMAC signature computation, verify replay_key uniqueness guarantees).
**Action**: Create up to 8 additional per-concern gates in `ops_scripts/ci/` once per-app wiring (D1) is complete and semantic verification is meaningful.

### D7 — Runtime certification claims (Constitutional §32)
**From**: parent plan §10 Non-Goals: "Adding runtime certification claims (Constitutional §32 — requires separate Author-Gate)."
**Scope**: The `l5_certification_ref` field is now present and validated on all 11 contracts. Upgrading from structural presence to active runtime certification claims (where the cert ref is meaningfully populated and verified against the L5 registry at runtime) requires a separate Author-Gate and plan.
**Action**: File Author-Gate `certification_claim` packet. Upon approval, create implementation plan to wire `compile_requirement_signoff.py` for the enriched contract surface.
**Gate**: Constitutional §32 (`FORTKNOX_DISCIPLINE_BYPASS=1` required if bypassed; do not bypass).

---

## Definition of Done

*(dod_exempt: true — this is a documentation-only capture plan)*

---

DEFERRED_SCOPE: plan=w6-emit-contract-deferred-scope-c3f7a1 items=7 parent=w6-emit-contract-enrichment-d8b2a4
PLAN_CREATED: slug=w6-emit-contract-deferred-scope-c3f7a1 path=.windsurf/plans/w6-emit-contract-deferred-scope-c3f7a1.md status=not_started tier=T0 layer=cross-cutting
