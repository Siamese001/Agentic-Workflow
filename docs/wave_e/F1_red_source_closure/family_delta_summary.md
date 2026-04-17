# Wave F1 — Family Delta Summary

Per-family projected effect of F1 proposals once integrated into canonical v2.

---

## F12 L6 Observability and Future-Run Learning — MATERIAL CLOSURE

| Metric | Canonical v1 | Projected post-F1 |
|---|---:|---:|
| Atom count | 6 | 8 |
| NORMATIVE | 4 | 7 |
| WEAK_EVIDENCE | 1 | 0 |
| EXCLUDED | 1 | 1 |
| Edges in / out | 4 | 7 |
| coverage_score | 0.80 YELLOW | **1.00 GREEN** |

**Changes:**
- F12.05 patched WEAK_EVIDENCE → NORMATIVE (richer binding including SRC-INT-004).
- F12.07 added (NORMATIVE) — memory-lifecycle session-start consumption mechanism.
- F12.08 added (NORMATIVE) — L6 records F08 exit outcomes to memory.
- 3 new edges: REFINES, REQUIRES, DEPENDS_ON.

---

## F04 Context Assembly — NO CHANGE

| Metric | Canonical v1 | Projected post-F1 |
|---|---:|---:|
| coverage_score | 0.25 RED | 0.25 RED |

F1 attempted honest closure on F04.02, F04.03, F04.04. All three remain WEAK_EVIDENCE because no rule, ADR, or governing-semantics statement covers context attribution, private-context prohibition, or context idempotence. Recorded as DEFERRED in `source_gap_closure_log.md`.

---

## F07 Heal/Retry — NO CHANGE

| Metric | Canonical v1 | Projected post-F1 |
|---|---:|---:|
| coverage_score | 0.25 RED | 0.25 RED |

F1 considered authoring F11.08 "L5 MUST bound retry budgets" but rejected because it would degrade F11 from GREEN 1.00 to YELLOW 0.875 without genuinely strengthening F07. Retry policy lacks a canonical source.

---

## F08 Exit Spine — NO CHANGE

| Metric | Canonical v1 | Projected post-F1 |
|---|---:|---:|
| coverage_score | 0.20 RED | 0.20 RED |

F1 could not materialize a real exit-spine source without fabricating an ADR locator. F08 carries forward as the single most important outstanding blocker.

Note: F1 adds `INT-F12.08-F08.03-01 DEPENDS_ON`, which does not strengthen F08 itself (F08.03 remains WEAK_EVIDENCE) but does record that F12.08 depends on the outcome F08 produces. Integration pass will recognize the new edge.

---

## F01, F03, F05 — NO CHANGE

F01.06, F03.04, F05.04 remain WEAK_EVIDENCE. No additional sources exist. Yellow-family scorecards (F01 0.83, F03 0.75, F05 0.75) unchanged.

---

## F02 — EDGE DELTA (no atom change)

F02 gains one incoming edge: `INT-F12.07-F02.01-01 REQUIRES`.
- Atom state unchanged.
- Edge count: 6 → 7.
- coverage_score: 1.00 GREEN (unchanged).

---

## Families Receiving New Edges

| Family | New edge | Endpoint role |
|---|---|---|
| F02 | INT-F12.07-F02.01-01 | target |
| F08 | INT-F12.08-F08.03-01 | target |
| F12 | INT-F12.05-F12.07-01, INT-F12.07-F02.01-01, INT-F12.08-F08.03-01 | source × 3 |

---

## Global Coverage Projection

| Metric | Canonical v1 | Projected post-F1 |
|---|---:|---:|
| Total counted atoms | 58 | 60 |
| NORMATIVE | 43 | 45 |
| WEAK_EVIDENCE | 15 | 13 |
| UNRESOLVED | 0 | 0 |
| Global coverage_score | **0.741 RED** | **0.776 YELLOW** |

**Bucket flip:** RED → YELLOW.

**What remains for later waves to close:**
- F04 RED (3 atoms weak)
- F07 RED (3 atoms weak)
- F08 RED (4 atoms weak)
- Plus yellow-family low-effort tightenings (F01.06, F03.04, F05.04).
