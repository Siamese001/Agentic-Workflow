# Wave B B5R Gap Matrix

**Date**: 2026-04-15 | **Supersedes**: wave_b_v30_gap_matrix.md
**Anti-drift**: Target-state grounding from ext_authority only. Checklist docs are coverage checklists only.

---

## 31-Family Classification

| # | Family | Scope | Grade | TS Basis | Blocks B6? |
|---|--------|-------|-------|----------|-----------|
| F01 | Request-source modes / bounded ingress | ext_authority | ADEQUATE | TS-11 | No |
| F02 | Identity/quota/schema/normalization/ingress contract | ext_authority | WEAK | TS-16, TS-20 | Advisory |
| F03 | L1 intent framing and work classification | ext_authority | ADEQUATE | TS-01, TS-11 | No |
| F04 | L1 priors/policy/example loading | ext_authority | ADEQUATE | TS-01, TS-11 | No |
| F05 | L1 decomposition/dependency/proposed-route drafting | ext_authority | **STRONG** | TS-12, TS-18 | No |
| F06 | L1 validation/simplify/clarify/abstain planning | ext_authority | WEAK | TS-09 WEAK, TS-17 | **YES** |
| F07 | L0 route authority/prefilters/freshness/ACL | ext_authority | ADEQUATE | TS-10, TS-11 | No |
| F08 | R1A exact cache route | ext_authority | **MISSING** | None | **YES** |
| F09 | R1B semantic cache route | ext_authority | **MISSING** | None | **YES** |
| F10 | R3 grounded-context decision | ext_authority | ADEQUATE | TS-02, TS-10 | No |
| F11 | C0 retrieval planning/scoping | ext_authority | ADEQUATE | TS-01, TS-02 | No |
| F12 | C0 evidence fetch: dense/sparse/cache/metadata/parent-child | ext_authority | WEAK | TS-02 OK; TS-03/07/19 WEAK | **YES** |
| F13 | C0 evidence shaping: dedup/rerank/prune/conflicts | ext_authority | WEAK | TS-08 OK; TS-04 WEAK | **YES** |
| F14 | C0 evidence contract: verified chunks/cited spans/refine-abstain | ext_authority | WEAK | TS-05 OK; TS-09 WEAK | **YES** |
| F15 | Prompt assembly: load/slot/budget/contract | ext_authority | ADEQUATE | TS-01, TS-08 | No |
| F16 | R4 external action route | ext_authority | **STRONG** | TS-13, TS-14 | No |
| F17 | R5 fallback/clarify/abstain route | ext_authority | WEAK | TS-09 (0.510) | **YES** |
| F18 | Governance invocation and authority context | ext_authority | ADEQUATE | TS-16, TS-11 | No |
| F19 | Structure/registry/classification/policy chokepoint | ext_authority | ADEQUATE | TS-13 STRONG, TS-16 | No |
| F20 | Sovereign egress/compliance artifacts/capability token/sandbox | ext_authority | ADEQUATE | TS-13 STRONG, TS-16 | No |
| F21 | Replay envelope and freeze propagation | **INTERNAL** | OUT OF SCOPE | — | No |
| F22 | Replay guard: time/entropy/identity/network/reads/writes | **INTERNAL** | OUT OF SCOPE | — | No |
| F23 | Determinism digest and replay verification | Mixed (mostly internal) | ADEQUATE | TS-05 (provenance) | No |
| F24 | L2 execution lifecycle E1–E5 | ext_authority | ADEQUATE | TS-12 STRONG, TS-15 STRONG | No |
| F25 | Healing/remediation/escalation tiers | ext_authority | WEAK | TS-12 partial | **YES — net-new** |
| F26 | Current-run exit review and explicit dispositions | ext_authority | ADEQUATE | TS-17, TS-16 | No |
| F27 | HITL airlock and L5 re-clearance | ext_authority | ADEQUATE | TS-11, TS-16 | No |
| F28 | UWG/state sovereignty/write governance/read-surface refresh | Mixed (primarily internal) | WEAK | TS-16, TS-11 tangential | Advisory |
| F29 | L6 observability/verify spine/control buses/evidence bundle | ext_authority | ADEQUATE | TS-17, TS-05, tracing docs | No |
| F30 | Shadow evaluation/RCA/promotion pipeline | ext_authority | ADEQUATE | TS-17, TS-11 | No |
| F31 | Capability/tool/model/network/memory/write access-control plane | ext_authority | ADEQUATE | TS-13 STRONG, TS-16 | No |

---

## Coverage Summary

| Grade | Count | Families |
|-------|-------|---------|
| STRONG | 2 | F05, F16 |
| ADEQUATE | 18 | F01,F03,F04,F07,F10,F11,F15,F18,F19,F20,F23,F24,F26,F27,F29,F30,F31 + F12/F13/F14 partial |
| WEAK | 8 | F02, F06, F12, F13, F14, F17, F25, F28 |
| MISSING | 2 | F08, F09 |
| INTERNAL/out of scope | 2 | F21, F22 |
| **Total** | 31 | |

**Blocking B6**: 8 families — F06, F08, F09, F12, F13, F14, F17, F25  
**Advisory (non-blocking)**: 2 families — F02, F28  
**Internal (not B6 ext_authority)**: F21, F22, F28 (primary classification)

---

## B6 Required Source Additions (Minimum Set)

| Priority | Source to Add | Closes Families | Closes TS Gaps |
|----------|--------------|-----------------|----------------|
| P1 | LLM response caching library docs | F08 — R1A | NEW |
| P2 | Semantic/vector LLM caching docs | F09 — R1B | NEW |
| P3 | Hybrid dense+sparse retrieval docs | F12 | TS-03 |
| P4 | Cross-encoder reranking docs | F12, F13 | TS-04 |
| P5 | Parent-child chunk expansion docs | F12 | TS-07 |
| P6 | Abstain/refine + graceful fallback best practices | F06, F14, F17 | TS-09 |
| P7 | Embedding model selection/comparison guide | F12 | TS-19 |
| P8 | Tiered healing/escalation patterns for agentic systems | F25 | NEW |

**Total: 8 ext_authority source additions.**

**Not in B6 ext_authority:**
- F02 (ingress auth/quota): advisory — lower retrieval priority; add to B6 only if scope allows
- F28 (UWG write governance): primarily internal — add to `repo_evidence` Lane C if needed
- F21, F22 (replay): fully internal — no ext_authority source applicable

---

## Delta: B5 (15-family) vs B5R (31-family)

| Status | B5 Count | B5R Count | Net Change |
|--------|---------|---------|-----------|
| Families evaluated | 15 | 31 | +16 new families |
| MISSING (ext_authority) | 2 (F02, F03) | 2 (F08, F09) | Same 2, renumbered |
| WEAK blocking | 4 | 6 | +2 new: F06 (L1 abstain), F25 (healing tiers) |
| B6 source additions required | 7 | **8** | +1 new: healing/escalation tiers (P8) |
| INTERNAL families scoped out | 0 | 2 | +2 (F21, F22 — replay/determinism) |

**Net-new B5R finding**: F25 (healing/escalation tiers) is a confirmed WEAK gap not visible in the B5 15-family framing. It requires one additional source addition (P8).

---

## Post-B6 Gate Target

| Gate | Current | Post-B6 Target |
|------|---------|----------------|
| G9 retrieval strength | 14/20 = 70% ❌ | ≥17/22 = 77% ✅ (22-query extended audit) |
| F08 R1A coverage | MISSING | ADEQUATE via P1 |
| F09 R1B coverage | MISSING | ADEQUATE via P2 |
| F12 evidence fetch | WEAK (3 sub-components) | ADEQUATE via P3, P5, P7 |
| F13 evidence shaping | WEAK (reranking) | ADEQUATE via P4 |
| F14 evidence contract | WEAK (abstain) | ADEQUATE via P6 |
| F17 R5 fallback | WEAK | ADEQUATE via P6 |
| F06 L1 abstain planning | WEAK | ADEQUATE via P6 |
| F25 healing tiers | WEAK | ADEQUATE via P8 |
| G1–G8, G10, G11 (hard gates) | PASS | Must remain PASS |

Extended audit adds 3 new queries: F08 (R1A), F09 (R1B), F25 (healing tiers). New denominator: 23.  
Required: ≥18/23 = 78% to exceed G9 75% hard gate.

---

## Go/No-Go Verdict

**B6: GO — audit is now complete enough to define a bounded source-addition plan.**

The B5R audit has identified all gaps precisely. B6 scope is bounded and unambiguous: 8 source additions, 3 new audit queries, verify ≥18/23 adequately grounded.

**Wave C: NO-GO until B6 complete.** All blocking conditions above must be resolved first.
