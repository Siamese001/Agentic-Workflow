# Wave F2 - Red-Family Closure Matrix

Atom-by-atom accounting of the three RED families entering F2 (F04, F07, F08) and their projected state post-F2.

---

## F08 Exit Spine - full closure

| Atom | v1.1 evidence | F2 source | F2 evidence | Closure status |
|---|---|---|---|---|
| F08.01 | WEAK_EVIDENCE | SRC-ADR-003 | NORMATIVE | ✅ CLOSED |
| F08.02 | NORMATIVE (v1) | reinforcement | NORMATIVE | — (already closed) |
| F08.03 | WEAK_EVIDENCE | SRC-ADR-003 | NORMATIVE | ✅ CLOSED |
| F08.04 | WEAK_EVIDENCE | SRC-ADR-003 | NORMATIVE | ✅ CLOSED |
| F08.05 | WEAK_EVIDENCE | SRC-ADR-003 | NORMATIVE | ✅ CLOSED |

**Coverage:** 0.20 RED -> 1.00 GREEN. Four atoms upgraded from a single source registration.

**Why this worked:** `eval_pipeline_acceptance.md` was already in the repo, release-accepted 2026-04-13, with 135/135 tests passing. Prior waves missed it.

---

## F07 Heal / Retry / Recovery - partial closure

| Atom | v1.1 evidence | F2 source | F2 evidence | Closure status |
|---|---|---|---|---|
| F07.01 | WEAK_EVIDENCE | SRC-ADR-002 | NORMATIVE | ✅ CLOSED |
| F07.02 | WEAK_EVIDENCE | SRC-ADR-002 | NORMATIVE | ✅ CLOSED |
| F07.03 | WEAK_EVIDENCE | SRC-ADR-001 (advisory) | WEAK_EVIDENCE | ⏳ DEFERRED |
| F07.04 | NORMATIVE (v1) | reinforcement | NORMATIVE | — |

**Coverage:** 0.25 RED -> 0.75 YELLOW. Two atoms upgraded; F07.03 blocked by the `invalid_for_normative_use=True` marker on the healing dispatch ADR.

**Remaining blocker:** normative escalation-target ADR. The existing `healing_dispatch_routing_adr.md` already describes ESCALATED-tier routing to HITL and deterministic abort; promoting it to normative would require dropping its `invalid_for_normative_use=True` marker via HITL review.

---

## F04 Context Assembly - no material closure

| Atom | v1.1 evidence | F2 source | F2 evidence | Closure status |
|---|---|---|---|---|
| F04.01 | NORMATIVE (v1) | — | NORMATIVE | — |
| F04.02 | WEAK_EVIDENCE | none found | WEAK_EVIDENCE | ❌ DEFERRED |
| F04.03 | WEAK_EVIDENCE | none found | WEAK_EVIDENCE | ❌ DEFERRED |
| F04.04 | WEAK_EVIDENCE | SRC-ADR-005 (supplementary) | WEAK_EVIDENCE | ⏳ PARTIAL |

**Coverage:** 0.25 RED -> 0.25 RED. No change.

**Why:** no existing repo document canonicalizes:
- source attribution in agentic context assembly (F04.02)
- prohibition on private unattributed substitute context (F04.03)
- explicit idempotence of context assembly (F04.04 — replay determinism is adjacent but covers mutations, not context)

**F2 refused to fabricate** a context-assembly ADR without implementation backing, HITL approval, or concrete project posture. This is the honest outcome.

**Remaining blocker B3:** context-assembly ADR still required. This is the single biggest blocker preventing canonical GREEN across the whole graph.

---

## Material Improvements Summary

| Red family | Coverage delta | Bucket change | Atoms upgraded | Honest verdict |
|---|---:|:---:|---:|---|
| F04 | +0.00 | none | 0 of 3 | **NO material improvement.** |
| F07 | +0.50 | RED -> YELLOW | 2 of 3 | **Material improvement.** |
| F08 | +0.80 | RED -> GREEN | 4 of 4 | **Full closure.** |

## Source Authority Rank Check

Every NORMATIVE upgrade cites at least one rank ≤ ARCHITECTURAL source:

| Atom | Sources | Highest rank |
|---|---|---|
| F01.06 | SRC-INT-003, SRC-ADR-004 | ARCHITECTURAL (4) |
| F03.04 | SRC-INT-003, SRC-ADR-004 | ARCHITECTURAL (4) |
| F07.01 | SRC-INT-003, SRC-ADR-002 | ARCHITECTURAL (4) |
| F07.02 | SRC-INT-003, SRC-ADR-002 | ARCHITECTURAL (4) |
| F08.01 | SRC-INT-003, SRC-ADR-003 | ARCHITECTURAL (4) |
| F08.03 | SRC-INT-003, SRC-ADR-003 | ARCHITECTURAL (4) |
| F08.04 | SRC-INT-003, SRC-ADR-003 | ARCHITECTURAL (4) |
| F08.05 | SRC-INT-003, SRC-ADR-003 | ARCHITECTURAL (4) |
| F09.05 | SRC-INT-003, SRC-ADR-003 | ARCHITECTURAL (4) |

All nine upgrades pass the rank-floor check.

## Invalid-for-Normative Handling

SRC-ADR-001 (`healing_dispatch_routing_adr.md`) is the only new source marked `invalid_for_normative_use=True`. F2 respects this marker: SRC-ADR-001 is bound to F07.03 as **supplementary ADVISORY context only**, and F07.03's `evidence_class` remains WEAK_EVIDENCE despite the binding.

This is the correct discipline: authority_class=ADVISORY cannot promote an atom to NORMATIVE.
