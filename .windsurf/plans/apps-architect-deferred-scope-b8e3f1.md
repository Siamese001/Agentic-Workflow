---
plan_id: apps-architect-deferred-scope-b8e3f1
plan_type: infra
parent_plan: apps-architect-pattern-hardening-d7e4f9
---

# apps_architect — Deferred Scope & Hardening Follow-Up

Collects all deferred scope, gaps, and aspirational success criteria from the parent plan `apps-architect-pattern-hardening-d7e4f9` (Completed 2026-05-07). **Do not implement** — this is a capture-only plan for future scheduling.

---

## Context (SCQA)

- **Situation** — `apps_architect` shipped as a functional R3_grounded_read app with 5 waves: spine/FEC/C0, 4 pattern engines, delta + rule generation, README sync + CLI, and OTEL/eval harness wiring. 30 files, 21 Python modules, all syntax-valid and smoke-tested.

- **Complication** — 12 deferred items were explicitly descoped from the parent plan: 5 out-of-scope exclusions, 3 gap-register items, and 4 aspirational success-criteria verifications. None block the current app from running, but all represent hardening depth.

- **Question** — What follow-up work is needed to harden apps_architect from functional skeleton to production-grade pattern enforcement engine?

- **Answer** — This deferred-scope plan captures all 12 items with priority bands, estimated token costs, and dependency ordering. Items are NOT implemented here — this is a registration artifact for future wave scheduling.

---

## Deferred Scope Inventory

### P1 — Security & Operational Hardening

| ID | Item | Source | Est. Tokens | Depends On |
|----|------|--------|-------------|------------|
| DS-1 | GitHub token security — secure storage (env var vs L4 secret) | GAP-3 | ~3K | None |
| DS-2 | C0 collection scope definition — exact collections for plans/rules/core | GAP-1 | ~3K | None |
| DS-3 | Pattern schema versioning — backward-compatible schema evolution | GAP-2 | ~2K | None |

### P2 — Feature Depth

| ID | Item | Source | Est. Tokens | Depends On |
|----|------|--------|-------------|------------|
| DS-4 | Real-time webhook triggers — replace poll-based with event-driven | Out of Scope | ~5K | DS-1 |
| DS-5 | Automatic rule enforcement — apply hardening rules (not just emit) | Out of Scope | ~6K | DS-4 |
| DS-6 | Multi-repo pattern federation — cross-repo pattern sharing | Out of Scope | ~8K | DS-2 |
| DS-7 | Historical pattern archaeology — extend beyond 30-day window | Out of Scope | ~4K | DS-2 |
| DS-8 | Pattern migration execution — auto-apply recommended changes | Out of Scope | ~6K | DS-5 |

### P3 — Verification & Benchmarking

| ID | Item | Source | Est. Tokens | Depends On |
|----|------|--------|-------------|------------|
| DS-9 | Pattern extraction coverage ≥90% — unit test over sample plans | Success Criteria | ~3K | DS-2 |
| DS-10 | Delta false positive rate <5% — manual audit of 20 samples | Success Criteria | ~3K | DS-9 |
| DS-11 | E2E scan latency <30s benchmark — integration test | Success Criteria | ~2K | DS-9 |
| DS-12 | README sync success rate >95% — OTEL span metrics | Success Criteria | ~2K | DS-1 |

---

## Wave Structure (proposed, not committed)

| Wave | Items | Focus | Est. Tokens | Priority |
|------|-------|-------|-------------|----------|
| DW1 | DS-1, DS-2, DS-3 | Security + schema hardening | ~8K | P1 |
| DW2 | DS-9, DS-10, DS-11, DS-12 | Verification & benchmarking | ~10K | P3 |
| DW3 | DS-4, DS-7 | Event-driven + deep history | ~9K | P2 |
| DW4 | DS-5, DS-8 | Auto-enforcement + migration | ~12K | P2 |
| DW5 | DS-6 | Multi-repo federation | ~8K | P2 |

**Total: ~47K tokens across 5 deferred waves**

---

## Out Of Scope (even from deferred)

- ❌ Real-time enforcement with <100ms latency SLA
- ❌ Cross-organization pattern sharing
- ❌ ML-based pattern discovery (rule-based only)
- ❌ Pattern rollback/undo mechanism

---

## Rules

1. **Do not implement** — this is a capture-only plan
2. **Parent plan must be Completed** before any DW wave starts
3. **DS-1 (token security) gates DS-4 and DS-12**
4. **DS-2 (C0 scope) gates DS-6, DS-7, DS-9**

---

## References

- Parent: `.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md` (Completed)
- `apps_research/` — Canonical R3_grounded_read reference
- `.windsurf/rules/adg-canonical-invariants.md` — ADG doctrine
- `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md` — Route taxonomy

---

DEFERRED_SCOPE: plan=apps-architect-deferred-scope-b8e3f1 parent=apps-architect-pattern-hardening-d7e4f9 items=12 waves=5 est_tokens=47K
