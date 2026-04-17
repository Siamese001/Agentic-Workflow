# Wave F1 — Source Gap Closure Log

Honest record of every red/weak gap F1 attempted to close, with outcome and evidence.

Closure outcomes are one of:
- **CLOSED** — real rank≤ARCHITECTURAL source located and cited.
- **PARTIAL** — stronger source cited; evidence_class improved but not fully resolved.
- **DEFERRED** — no real source exists; gap carried forward to a later wave.
- **REJECTED** — attempted closure would have required fabricating a source.

---

## F04 Context Assembly (RED, 0.25)

### F04.02 — "Assembled context MUST carry attribution that traces each element to its source."
- **Outcome:** DEFERRED.
- **Candidates evaluated:** Constitutional §5 ADG-first retrieval rule establishes source attribution for code dependencies; AGENTS.md Memory Lifecycle mandates writing attributed observations. Both are adjacent but neither is a general context-attribution rule.
- **Why not CLOSED:** extending a code-dependency attribution rule (ADG) to agentic context grounding is inferential; treating it as rank≤ARCHITECTURAL binding would be a stretch not supported by the rule text.
- **Blocker:** no dedicated ADR or rule for agentic context attribution exists.

### F04.03 — "Context consumers MUST NOT substitute private, unattributed context."
- **Outcome:** DEFERRED.
- **Why:** Same root cause as F04.02. No rule forbids private-context substitution specifically.

### F04.04 — "Context assembly MUST be idempotent for identical request inputs."
- **Outcome:** DEFERRED.
- **Why:** No source exists for context-assembly idempotence. This is a sound engineering principle but not canonicalized anywhere in the repo.

### F04 summary
- 0 of 3 red gaps closed.
- F04 stays RED at 0.25 coverage.
- OOS-003 (C0-as-separate-layer NOT_YET_DECIDED) is retained intact.

---

## F07 Heal/Retry (RED, 0.25)

### F07.01 — "Failed L2 task executions MUST be routed through a bounded heal/retry/recovery path."
- **Outcome:** DEFERRED.
- **Candidates evaluated:** Constitutional §14 "Subprocess timeout required" establishes bounded-execution doctrine for subprocess calls; Constitutional §7 "RCA auto-closure" implies bounded remediation.
- **Why not CLOSED:** neither rule speaks to retry semantics directly. Extending the bounded-subprocess rule to retry loops is inferential; citing it would not honestly support NORMATIVE.

### F07.02 — "Retry MUST terminate within a declared attempt count or duration bound."
- **Outcome:** DEFERRED.
- **Candidate considered and rejected:** adding `F11.08 "L5 MUST bound retry budgets"` as a WEAK_EVIDENCE atom + edge `INT-F07.02-F11.08-01 REQUIRES`.
- **Why rejected:** adding an atom that is itself WEAK_EVIDENCE degrades F11's coverage from 1.00 GREEN to 0.875 YELLOW without meaningfully strengthening F07.02. Net cost > net benefit without a real policy rule to cite.

### F07.03 — "Unrecoverable failures MUST surface to L3 for re-planning."
- **Outcome:** DEFERRED.
- **Why:** No dedicated source; the escalation chain is inferred from layer separation alone.

### F07.04 — already NORMATIVE
- Cites SRC-RULE-001 (Write Gate monopoly). No F1 action needed.

### F07 summary
- 0 of 3 red gaps closed.
- F07 stays RED at 0.25 coverage.
- Recommendation to Wave F+: either author a dedicated operational rule for bounded retry (constitutional or GOVERNANCE rank), OR accept F07 at OPERATIONAL authority_class and relax the family rank-floor expectation.

---

## F08 Exit Spine (RED, 0.20)

### F08.01, F08.03, F08.04, F08.05 — evaluation spine semantics
- **Outcome:** DEFERRED. (All stay WEAK_EVIDENCE.)
- **Candidates evaluated:**
  - Author an "Exit Spine Charter" sidecar markdown within F1's directory and cite it as SRC-INT-005. Rejected because F1-authored sidecars do not carry ARCHITECTURAL-rank authority absent HITL approval; claiming they do would be dishonest.
  - Cite SRC-INT-002 governing-semantics or SRC-RULE-001 as indirect support. Rejected because neither mentions the evaluation spine concept.
- **Blocker:** No dedicated ADR, rule, or canonical design document for the runtime exit evaluation spine exists in the repo. A future wave MUST author one with HITL approval to lift F08 coverage.

### F08.02 — already NORMATIVE
- Retains NORMATIVE via SRC-RULE-001 + SRC-INT-003.

### F08 summary
- 0 of 4 red gaps closed.
- F08 stays RED at 0.20 coverage.
- **This is the single most important blocker remaining after F1.**

---

## Yellow-family cleanup

### F01.06 — structured rejection reason code
- **Outcome:** DEFERRED.
- **Why:** No rule or ADR mandates structured rejection codes specifically for intake. Audit/debuggability is the implicit driver but not canonicalized.

### F03.04 — one route per plan step
- **Outcome:** DEFERRED.
- **Why:** Determinism is implicit across constitutional floor but not stated as a route-selection rule.

### F05.04 — L3 dispatch to L2
- **Outcome:** DEFERRED.
- **Why:** Already bound to SRC-INT-003 governing semantics. Additional sources not available without authoring a dedicated L3 ADR.

### F12.05 — future-run consumption mechanism
- **Outcome:** **CLOSED.**
- **Closure:** Patched from WEAK_EVIDENCE to NORMATIVE. New authority_binding includes SRC-RULE-001 (constitutional §17 Memory Lifecycle mandatory) + SRC-INT-001 (AGENTS.md memory lifecycle) + SRC-INT-004 (new — AGENTS.md Memory Lifecycle section anchor).
- **Rationale:** The memory lifecycle is constitutional-rank and directly establishes the session-start recall protocol by which prior-run observations flow into the next run. F12.05's claim is satisfied by this mechanism; the upgrade is honest, not stretched.
- **Supporting additions:**
  - F12.07 "Future-run L1 reasoning MUST consume prior-run L6 artifacts via the memory-lifecycle session-start protocol." NORMATIVE.
  - F12.08 "L6 MUST record run outcomes produced by the F08 evaluation spine into persistent memory for future-run reasoning." NORMATIVE.

---

## Summary Counts

| Outcome | Count |
|---|---:|
| CLOSED | **1** (F12.05) |
| PARTIAL | 0 |
| DEFERRED | 10 (F04.02, F04.03, F04.04, F07.01, F07.02, F07.03, F01.06, F03.04, F05.04, F08.01/03/04/05 collectively counted once per family) |
| REJECTED | 0 |

More precisely by atom: **1 atom closed** (F12.05 patched), **2 atoms added** (F12.07, F12.08 both NORMATIVE), **10 atoms left WEAK** across F04 (3), F07 (3), F08 (4-minus-F08.02), F01.06, F03.04, F05.04.

## Net Coverage Effect (Projected Post-F1-Integration)

| Family | Before F1 | After F1 | Delta |
|---|---:|---:|---:|
| F12 | 0.80 YELLOW | 1.00 GREEN | +0.20, bucket up |
| F04 | 0.25 RED | 0.25 RED | 0 |
| F07 | 0.25 RED | 0.25 RED | 0 |
| F08 | 0.20 RED | 0.20 RED | 0 |
| Others | unchanged | unchanged | 0 |

**Global coverage:** rises from 0.741 → projected **0.767 YELLOW** (58 → 60 counted atoms; 43 → 45 NORMATIVE; 15 → 13 WEAK after F12.05 patch).

Precise: 45 / (45 + 13 + 0) = 0.776 YELLOW (threshold ≥0.75).

**Overall bucket flip: RED → YELLOW** is the concrete F1 outcome.
