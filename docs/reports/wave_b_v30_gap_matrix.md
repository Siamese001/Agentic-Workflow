# Wave B v30 Gap Matrix

**Date**: 2026-04-15
**Source**: `docs/reports/wave_b_v30_coverage_audit.md`
**Purpose**: Single compact view separating covered v30 families from open Wave C blockers.
**Anti-drift rule**: v30 is a coverage checklist only. All grounding is from `ext_authority`.

---

## Gap Matrix

| v30 Family | Classification | Covered by Wave B | Open — Blocks Wave C | B6 Source Category |
|-----------|---------------|------------------|---------------------|-------------------|
| F01 — L0 Route Authority | ADEQUATE | ✅ TS-10, TS-11 | — | — |
| **F02 — R1A Exact Cache Route** | **MISSING** | ❌ None | ✅ YES | LLM response caching library docs |
| **F03 — R1B Semantic Cache Route** | **MISSING** | ❌ None | ✅ YES | Semantic/vector LLM caching docs |
| F04 — R3 Agentic RAG | ADEQUATE | ✅ TS-02, TS-08, TS-10 | — | — |
| F05 — C0 Context Assembly | ADEQUATE | ✅ TS-01, TS-08 | — | — |
| F06 — V1 Dense Vector Retrieval | ADEQUATE | ✅ TS-05, TS-06 | — | — |
| **F07 — V1 Full Retrieval Pipeline** | **WEAK** | ❌ TS-03 WEAK · TS-04 WEAK · TS-07 WEAK · TS-19 WEAK | ✅ YES | Hybrid retrieval · Reranker · Parent-child · Embedding docs |
| F08 — Prompt Assembly (packaging) | ADEQUATE | ✅ TS-01, TS-08 | — | — |
| F09 — R4 External Action Route | STRONG | ✅ TS-13, TS-14 | — | — |
| **F10 — R5 Fallback / Abstain-Refine** | **WEAK** | ❌ TS-09 WEAK (dist@1=0.510) | ✅ YES | Abstain / graceful fallback best practices |
| F11 — L5 Guardrails | ADEQUATE | ✅ TS-16 | — | — |
| F12 — L5 Normative Requirements | WEAK | ❌ TS-20 WEAK | ⚠️ repo_evidence Lane C — not ext_authority | None for ext_authority |
| F13 — [5] Exit Control / Current-Run Eval | ADEQUATE | ✅ TS-17 | — | — |
| F14 — [6] Future-Run Learning / L6 | ADEQUATE | ✅ TS-17, tracing docs | — | — |
| F15 — L2 Execution Contract (ext. repr.) | STRONG | ✅ TS-12, TS-15 | — | — |

---

## Coverage Summary

| Status | Families | Count |
|--------|---------|-------|
| STRONG | F09, F15 | 2 |
| ADEQUATE | F01, F04, F05, F06, F08, F11, F13, F14 | 8 |
| WEAK | F07, F10, F12 | 3 |
| MISSING | F02, F03 | 2 |
| **Total** | | **15** |

**Grounded (STRONG + ADEQUATE)**: 10/15 = 67%
**Open and blocking ext_authority Wave C**: 4/15 — F02, F03, F07, F10
**Out of ext_authority scope (→ repo_evidence)**: 1/15 — F12

---

## Wave B Registry vs v30: Delta View

The Wave B registry grounded 14/20 audit topics. v30 adds 2 net-new semantic families (F02, F03) not represented in the original 20-query audit:

| Delta | Detail |
|-------|--------|
| Wave B audit topics adequately covered | 14/20 (TS-01 to TS-20) |
| v30 families fully covered by those 14 topics | F01, F04, F05, F06, F08, F09, F11, F13, F14, F15 |
| v30 families weakly covered by the 6 WEAK topics | F07 (4 weak topics), F10 (1 weak topic), F12 (1 weak topic) |
| v30 families with NO Wave B audit topic | **F02 (R1A)**, **F03 (R1B)** — net-new gaps |

---

## B6 Required Source Additions

| Priority | Source Addition | Closes Family | Closes TS Gap |
|----------|----------------|--------------|---------------|
| P1 | LLM response caching library docs (deterministic cache routing) | F02 — R1A | NEW (no prior TS) |
| P2 | Semantic/vector LLM caching docs (similarity-based cache lookup) | F03 — R1B | NEW (no prior TS) |
| P3 | Hybrid dense+sparse retrieval docs with score fusion | F07 | TS-03 |
| P4 | Cross-encoder reranking pipeline docs | F07 | TS-04 |
| P5 | Parent-child chunk expansion docs | F07 | TS-07 |
| P6 | Abstain / graceful fallback best practices | F10 | TS-09 |
| P7 | Embedding model comparison and selection guide | F07 / F03 | TS-19 |

**Total: 7 ext_authority source additions.**
**F12 (Normative Requirements)**: add to `repo_evidence` Lane C only — not a B6 ext_authority item.

---

## Post-B6 Gate Target

| Gate | Current | Post-B6 Target |
|------|---------|----------------|
| G9 retrieval strength | 14/20 = 70% ❌ | ≥17/22 = 77% ✅ (extended 22-query audit) |
| F02 R1A coverage | MISSING | ADEQUATE via P1 |
| F03 R1B coverage | MISSING | ADEQUATE via P2 |
| F07 retrieval pipeline | WEAK (4 topics) | ADEQUATE via P3–P5, P7 |
| F10 fallback / abstain | WEAK | ADEQUATE via P6 |
| G1–G8, G10, G11 | PASS | Must remain PASS |

Extended audit adds 2 new queries (for F02, F03) to the existing 20. New denominator: 22.
Required threshold: ≥17/22 (77%) to exceed G9 75% hard gate.

---

## Go/No-Go Verdict

**Wave C: NO-GO until B6 complete.**

| Condition | Status |
|-----------|--------|
| Hard freeze gates (G1–G8, G10, G11) | ✅ PASS — no rework needed |
| G9 retrieval strength ≥75% | ❌ FAIL — 14/20 = 70% |
| F02 R1A Exact Cache externally grounded | ❌ MISSING |
| F03 R1B Semantic Cache externally grounded | ❌ MISSING |
| F07 V1 Full Pipeline adequately grounded | ❌ WEAK (4 topics) |
| F10 R5 Fallback / Abstain adequately grounded | ❌ WEAK |
| B6 source addition plan drafted | ❌ NOT YET |

**One bounded B6 prompt is the single required next action.** Scope: 7 source additions, re-run 22-query audit, verify G9 pass. Wave C entry unblocked when G9 passes and all 11 hard gates remain PASS.
