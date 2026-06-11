---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-deferred-investigations-b5d9f2.md'
original_relative_path: 'adg-deferred-investigations-b5d9f2.md'
source_sha256: b757a9bcecf6830a6e95395ab1710079023b0a7af41e2b2a543f0f0fc43fa971
recovered_status: SURVIVED_IN_CURRENT
last_commit: 'e37f53042c6'
last_commit_date: '2026-05-06 06:55:44 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: adg-deferred-investigations-b5d9f2
created: 2026-05-03
tier: T3
status: pending
parent: p1p2-burndown-followup-a2e4c7 (Completed 2026-05-03)
---

# ADG Deferred Investigations

Captures the two `DEFERRED_SCOPE:` markers emitted by `p1p2-burndown-followup-a2e4c7` at its W2/W3 closeout (commit `18d306cbaa`). Neither item is executable without further investigation and author-gate input; both are tracked here as independent waves.

## Parent Outcome Recap

- Parent `p1p2-burndown-followup-a2e4c7` closed 2026-05-03 with W1 reconceived + W2/W3 executed via ADR-096 + ADR-097 (docs-only approval).
- P2 ratchet settled 13 → 19 to match post-burndown floor after parallel session additions.
- Two pre-existing / classifier-side issues surfaced during regen and were deferred as separate plans.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|------------:|--------|------------------|
| W1 | W1-01 | P0 Phase-B runner failures investigation | 12000 | Pending | Root-cause and remediate `authority_boundary` (5 violations), `capability_egress` (23 violations), `infra_wiring` (23 violations) reported by `[p0_runner]` Phase B. Either fix violations at source or legitimize via ADR + exemption mechanism. Full ADG regen exits 0 without Phase-B BLOCKED. |
| W2 | W2-01 | P2 view classifier refinement | 10000 | Pending | Teach `v_p2_duplicated_adapters` and `v_p2_mixed_usage` to (a) exempt stdlib modules (`sqlite3`, `json`, `urllib`, etc.) from duplicated-adapter signal per ADR-097; (b) recognize specialized-store patterns (module A wraps sqlite3 for memory, module B wraps for cache) as legitimate rather than duplication. Post-refinement regen: `v_p2_duplicated_adapters` drops from 3 rows → ≤1; `v_p2_mixed_usage` drops from 3 rows → ≤1. |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| W1-01 | P0 Phase-B runner root-cause | `tools/adg/p0_gates/*`, `tools/generate/validation/gates.py`, violation sources across the 51 reported sites | 51 violations across 3 gates; unclear if same root cause or three distinct issues; gates were masked for multiple sessions by upstream P2 ratchet exits; may intersect with parallel-session apps-eval-harness-deferred work | 12000 | Pending |
| W2-01 | P2 classifier stdlib-exemption + specialized-store recognition | `tools/adg/materialized_views/p2_*`, `tools/adg/core/*classifier*`, relevant rule YAML if any | Rule currently matches any Python module imported in 3+ files as a candidate for canonical-adapter review; needs stdlib-allowlist lookup + heuristic for distinct-surface wrappers (memory store vs cache vs signal-registry) | 10000 | Pending |

## ADG_HOTSPOT_REPORT

| Rank | Target | Layer | Surface | Archetype | Impact | Fix class |
|------|--------|-------|---------|-----------|-------:|-----------|
| 1 | W1 P0 Phase-B (51 violations across 3 gates) | L_TOOLS (gates) + all production layers (violation sources) | Execution + Security | SAFETY_GATEKEEPER | 51 (raw count, layer-multiplier TBD per target) | Investigation + (fix OR legitimize-via-ADR) |
| 2 | W2 P2 view classifier | L_TOOLS | Observability | CENTRAL_DEPENDENCY | 6 (3 duplicated-adapter + 3 mixed-usage rows) | Classifier refinement |

## ADG_GRAPH_LAYER_EVIDENCE

- MV `mv_authority_boundary_breaches` (5 rows) — drives W1 authority_boundary gate count; confirms 5 distinct violation sources.
- MV entries tied to `capability_egress` (23 rows) and `infra_wiring` (23 rows) — listed in `[p0_runner] Phase B` BLOCKED output of commit `18d306cbaa`.
- P-views `v_p2_duplicated_adapters` (3 rows: redis/chromadb/sqlite3) and `v_p2_mixed_usage` (3 rows: same keys) — drive W2 refinement scope.
- Semantic edges are not the primary driver here — these are classifier-rule + gate-output concerns.

## Author-Gate Seeds

AG_QUEUE_SEED: plan=adg-deferred-investigations-b5d9f2 id=w1-remediation-vs-adr depends_on= title=W1 remediation strategy — code fix at source vs ADR + guardian-exemption for each of the 51 P0 Phase-B violations
AG_QUEUE_SEED: plan=adg-deferred-investigations-b5d9f2 id=w2-classifier-scope depends_on= title=W2 classifier refinement scope — stdlib-exemption only vs stdlib-exemption + specialized-store heuristic

## DEFERRED_SCOPE Provenance

This plan captures two `DEFERRED_SCOPE:` markers from parent:

DEFERRED_SCOPE: slug=p0-phase-b-runner-failures-investigation parent=p1p2-burndown-followup-a2e4c7 reason=P0-Phase-B-gates-authority-boundary-capability-egress-infra-wiring-blocked-since-18d306cbaa-masked-earlier-by-P2-ratchet
DEFERRED_SCOPE: slug=p2-view-classifier-refinement parent=p1p2-burndown-followup-a2e4c7 reason=P2-views-v_p2_duplicated_adapters-v_p2_mixed_usage-need-stdlib-exemption-and-specialized-store-recognition-per-ADR-097

## References

- Parent plan: `.windsurf/plans/p1p2-burndown-followup-a2e4c7.md` (Completed 2026-05-03)
- Parent commits: `18d306cbaa` (ADR-096+097 + guardian comments), `271a853f38` (plan closeout)
- ADR-096 (L6 universally importable), ADR-097 (canonical adapters)
- Constitutional §6, §8, §22, §24, §35

## Status

**Pending 2026-05-03** — documented-only; no execution this session. Awaiting W1 and W2 author-gate decisions in future sessions.
