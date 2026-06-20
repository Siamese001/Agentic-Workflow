---
plan_id: apps-rg-l7-deferred-scope-d117ea
plan_type: tracker
status: Completed
---

# Plan: apps_rg L7 Route Family — Deferred Scope Items

Tracks two deferred items from completed plan `apps-rg-l7-route-family-cert-fix-b8f3a1`.

---

## Context (SCQA)

- **Situation** — The L7 route-family coverage matrix now certifies R4_SINGLE_ACTION after the contract payload patch (parent plan completed 2026-05-08). The `route_contract.json` payload includes `request_id` + `trace_root` in all 3 emission sites.
- **Complication** — Two improvements were explicitly deferred during the parent plan: (1) R1A cache hits serve stale L7 evidence that will never certify, and (2) the L7 verifier script is advisory-only (does not fail-closed on NOT_CERTIFIED families).
- **Question** — How do we ensure L7 evidence stays fresh on cache hits and that CI gates enforce certification?
- **Answer** — W1 refreshes L7 evidence on R1A cache replay; W2 promotes the L7 verifier to fail-closed mode.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `agentic_core/runtime/entrypoints/integrated_exact_cache_run.py` | R1A cache replay entrypoint — needs L7 re-emission | 🔲 |
| `agentic_core/L7_auditability/coverage/route_family_l7_coverage.py` | L7 classifier logic | 🔲 |
| `scripts/verify_agentic_core_l7_route_family_coverage.py` | Current advisory verifier | 🔲 |
| Parent plan `.cursor/plans/apps-rg-l7-route-family-cert-fix-b8f3a1.md` | DEFERRED_SCOPE markers | ✅ |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 | P1.1 | Refresh L7 evidence on R1A cache hit | ~8k | R1A replay path is deterministic and observable | ✅ DONE | Cache-hit runs re-emit `agentic_core_l7_route_family_coverage.json` with fresh timestamps |
| W2 | P2.1 | Promote L7 verifier to fail-closed | ~4k | CI environment supports env-var gating | ✅ DONE | `verify_agentic_core_l7_route_family_coverage.py` exits non-zero when exercised family is NOT_CERTIFIED |

**Total: ~12k tokens across 2 waves**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| P1.1 | L7 evidence refresh on R1A cache hit | `apps_rg/__main__.py` (cache-hit path) | Stale evidence from pre-patch runs permanently shows NOT_CERTIFIED | ~8k | ✅ DONE |
| P2.1 | L7 verifier fail-closed promotion | `ops_scripts/ci/verify_agentic_core_l7_route_family_coverage.py` | Advisory mode masks regressions | ~4k | ✅ DONE |

---

## Out Of Scope

- Certifying other route families (R1B, R3, R5, MANAGED_WORKFLOW, UWG) — each requires running its own entrypoint
- Modifying `route_family_l7_coverage.py` classifier logic
- R1A cache invalidation or TTL changes

---

## Gap Register

**GAP-1: R1A cache replay does not re-emit L7 evidence**
- When R1A exact-cache returns a frozen artifact bundle, L7 coverage matrix is not regenerated
- Impact: runs that hit cache permanently show 0/9 CERTIFIED even though the payload contract is now correct

**GAP-2: L7 verifier is advisory-only**
- `verify_agentic_core_l7_route_family_coverage.py` logs warnings but exits 0 regardless of certification status
- Impact: regressions in L7 evidence emission are not caught by CI

---

## Success Criteria

- [ ] R1A cache-hit runs produce fresh `agentic_core_l7_route_family_coverage.json` with `summary.certified >= 1`
- [ ] L7 verifier exits non-zero when exercised family is NOT_CERTIFIED (fail-closed, env-var gated)
- [ ] No regressions in existing test suite

---

## Rollback Strategy

1. W1: revert cache-replay L7 emission patch — cache hits return to prior behavior (stale but harmless)
2. W2: set env var to advisory mode — verifier reverts to exit-0

---

## References

- Parent plan: `apps-rg-l7-route-family-cert-fix-b8f3a1` (Completed 2026-05-08)
- DEFERRED_SCOPE markers in parent plan §"Out of Scope (Deferred)"

PLAN_CREATED: slug=apps-rg-l7-deferred-scope-d117ea path=.cursor/plans/apps-rg-l7-deferred-scope-d117ea.md
