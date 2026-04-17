# Wave E1d — Interaction Failure Modes

**Scope:** Per-interaction criticality, silent-failure risk, and test priority. Kept here as sidecar markdown because the E0 schema deliberately does not allow these fields on `InteractionEdge` (edges are first-class entities; meta-analysis lives in sidecars).

Criticality levels:
- **CRIT** — violation breaks a governing semantic. Top priority for CI gating.
- **HIGH** — violation produces observable incorrectness but not a constitutional break.
- **MED** — violation degrades audit/operability.
- **LOW** — violation produces cosmetic or advisory issues only.

Silent-failure risk: **YES** means the violation can occur without any externally observable symptom in the short term.

---

## Interaction Criticality Matrix

| Edge ID | Kind | Crit | Silent? | Test priority | Failure mode if broken |
|---|---|---|---|---|---|
| INT-F01.03-F11.01-01 | REQUIRES | HIGH | No | 2 | Admission accepts requests that violate L5 policy; externally observable quickly. |
| INT-F02.01-F01.05-01 | DEPENDS_ON | MED | Yes | 3 | Reasoning begins before admission completes; could complete and return before auth/policy fails. **Silent in dev, caught in audit.** |
| INT-F05.02-F02.02-01 | REFINES | HIGH | Yes | 2 | L3 produces an implicit plan; output looks correct but F02 authorship contract broken. |
| INT-F06.03-F02.02-01 | REFINES | HIGH | Yes | 2 | L2 infers extra plan steps; same silent-drift class as above. |
| INT-F05.03-F03.02-01 | REFINES | CRIT | Yes | 1 | L3 chooses a route; governing semantic (L0 sole router) broken. **Silent until routing audit.** |
| INT-F06.04-F03.02-01 | REFINES | CRIT | Yes | 1 | L2 chooses a route; same class as above. |
| INT-F05.01-F02.03-01 | REQUIRES | HIGH | No | 2 | L3 runs without a plan; loud failure. |
| INT-F05.04-F06.01-01 | REQUIRES | MED | No | 3 | Dispatch fails at runtime. |
| INT-F06.02-F03.01-01 | REQUIRES | CRIT | Yes | 1 | L2 ignores L0's route and uses a default; **silent** if default coincidentally works. |
| INT-F06.05-F09.01-01 | REQUIRES | **CRIT** | **YES** | **1** | L2 mutates state bypassing the gate. **Most dangerous silent failure** — state diverges from authoritative L4 invisibly. |
| INT-F07.04-F09.01-01 | REQUIRES | **CRIT** | **YES** | **1** | Heal/retry writes via private path; state consistency lost during recovery. |
| INT-F10.03-F09.01-01 | REQUIRES | **CRIT** | **YES** | **1** | Any L4 write bypass; same class as F06.05. |
| INT-F07.03-F02.01-01 | CONDITIONAL_ON | HIGH | Yes | 2 | Re-planning happens inside L3 instead of L1; plan authorship boundary broken. |
| INT-F07.03-F05.01-01 | REQUIRES | MED | No | 3 | Escalation skips L3; observable via missing orchestration handoff. |
| INT-F08.02-F11.05-01 | REQUIRES | HIGH | Yes | 2 | Exit spine ignores L5 exit policy; **silent** unless policy is exercised. |
| INT-F08.04-F09.01-01 | REQUIRES | HIGH | Yes | 2 | Spine writes outcome directly, bypassing gate; silent until audit. |
| INT-F09.04-F11.04-01 | REQUIRES | **CRIT** | **YES** | **1** | Gate accepts writes without policy signal; **policy-less mutation** — CRIT silent. |
| INT-F09.05-F08.04-01 | REQUIRES | HIGH | Yes | 2 | Gate accepts writes without exit signal; degrades outcome integrity. |
| INT-F11.07-F09.01-01 | IMPLIES | MED | No | 3 | L5 attempts direct write; caught by gate if gate is honored elsewhere. |
| INT-F12.02-F03.01-01 | FORBIDS | **CRIT** | **YES** | **1** | L0 biases routes on L6 signal; **governing-semantic break, silent** — the worst combination. |
| INT-F12.02-F11.01-01 | FORBIDS | **CRIT** | **YES** | **1** | L5 policy re-evaluates mid-run from L6; same class. |
| INT-F12.03-F09.01-01 | FORBIDS | **CRIT** | **YES** | **1** | L6 triggers a write; constitutional break. |
| INT-F12.05-F02.01-01 | DEPENDS_ON | LOW | No | 4 | Future-run consumption broken; no current-run impact. |

---

## Aggregate

| Level | Edge count | Silent-failure share |
|---|---:|---:|
| CRIT | 9 | 9/9 silent — **100%** |
| HIGH | 8 | 6/8 silent |
| MED | 4 | 1/4 silent |
| LOW | 1 | 0/1 silent |

**Silent-failure share is overwhelmingly concentrated in CRIT.** Wave F test design MUST prioritize CI gating of the nine CRIT edges.

---

## Top Silent-Failure Intersections

Ranked by (criticality × silent-failure risk × breadth of downstream impact):

1. **INT-F06.05-F09.01-01** — L2 bypassing the Write Gate. Touches every durable state path. Without a gate-integrity CI gate, the system can appear healthy while L4 drifts.
2. **INT-F12.02-F03.01-01** — L6 biasing L0 routing silently. Routing outputs remain plausible; the governance break is invisible without explicit provenance tracing.
3. **INT-F09.04-F11.04-01** — Gate accepting policy-less writes. A gate implementation that forgets the policy check is indistinguishable from a correct one on the happy path.
4. **INT-F06.02-F03.01-01** — L2 ignoring the resolved L0 route. Default-route coincidence masks the violation.
5. **INT-F10.03-F09.01-01** — L4 writes that didn't go through the gate. Any ORM or raw SQL path in L4 is a risk vector.
6. **INT-F05.03-F03.02-01 / INT-F06.04-F03.02-01** — non-L0 layers choosing routes. Silent drift; the chosen route might be correct for the wrong reason.
7. **INT-F07.04-F09.01-01** — heal/retry paths with private writes. Recovery is exactly the moment invariants are most at risk.
8. **INT-F12.03-F09.01-01** — L6 triggering a write. Observability-as-mutation anti-pattern; constitutional break.
9. **INT-F12.02-F11.01-01** — L5 policy re-evaluation from L6. Subtler than the L0 case; same class of break.

---

## Test Priority Bucketing

**Priority 1 (block CI on violation):** all CRIT + silent-failure edges. 9 edges.
**Priority 2 (fail fast in staging):** HIGH + silent edges (6) + HIGH non-silent (2) = 8 edges.
**Priority 3 (audit sampling):** MED edges (4).
**Priority 4 (documented but not blocking):** LOW edges (1).

Wave F test scaffolding SHOULD adopt this bucketing as its baseline.
