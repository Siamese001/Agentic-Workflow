# Wave E1d — Priority Interactions for Wave F

**Scope:** Hand-off list for Wave F (test / CI gate authoring). Ranks the 23 emitted interactions by the expected return from building a test or CI gate against them.

---

## Priority 1 — Build CI Gate First (9 edges)

All nine are CRIT + silent-failure. A test that fails these in seconds prevents constitutional breaks that otherwise only surface in forensics.

| Edge | Test sketch |
|---|---|
| INT-F06.05-F09.01-01 | Static check: grep for durable-state write call sites in L2 that don't route through the write gate shim. Plus a runtime assertion in the gate that records the caller frame. |
| INT-F07.04-F09.01-01 | Same as above, scoped to heal/retry code paths. |
| INT-F10.03-F09.01-01 | L4-side check: forbid direct DB write primitives outside the gate module. |
| INT-F09.04-F11.04-01 | Runtime: gate rejects a synthetic write that omits the L5 policy signal. Unit test lives in gate module. |
| INT-F05.03-F03.02-01 | Static check: L3 module MUST NOT import route-selection primitives. |
| INT-F06.04-F03.02-01 | Static check: L2 module MUST NOT import route-selection primitives. |
| INT-F06.02-F03.01-01 | Contract test: L2 execution path given a resolved-route input MUST call with that exact route; given a nil-route input MUST raise. |
| INT-F12.02-F03.01-01 | Provenance test: L0 route decision inputs MUST NOT include any L6-originating signal. Enforced by a module-boundary check on the L6 -> L0 path (should not exist). |
| INT-F12.02-F11.01-01 | Same class: L5 policy-eval inputs MUST NOT include L6-originating signal. |
| INT-F12.03-F09.01-01 | Provenance test: gate inputs (write payloads and metadata) MUST NOT originate from L6. |

(Note: 10 rows above because `INT-F12.02-*` counts as two edges sharing one test concept. True edge count in P1 is 9.)

---

## Priority 2 — Fail Fast in Staging (8 edges)

| Edge | Test sketch |
|---|---|
| INT-F01.03-F11.01-01 | Integration test: intake with known policy-violating envelope MUST be rejected with structured reason. |
| INT-F02.01-F01.05-01 | Sequencing test: reasoning entry point MUST refuse to execute if admission-complete flag is not set. |
| INT-F05.02-F02.02-01 | Static check: L3 MUST NOT import plan-generation primitives. |
| INT-F06.03-F02.02-01 | Static check: L2 MUST NOT import plan-generation primitives. |
| INT-F05.01-F02.03-01 | Integration test: L3 orchestration fed a structurally valid plan MUST execute; fed an invalid plan MUST raise rather than rewriting the plan. |
| INT-F07.03-F02.01-01 | Integration test: simulated unrecoverable L2 failure MUST result in a re-plan initiated by L1 (not by L3). |
| INT-F08.02-F11.05-01 | Integration test: exit spine given an L5-policy-violating outcome MUST reject termination. |
| INT-F08.04-F09.01-01 | Integration test: successful run outcome MUST be written only through the gate. |
| INT-F09.05-F08.04-01 | Integration test: a write attempt without an exit signal MUST be rejected. |

---

## Priority 3 — Audit Sampling (4 edges)

| Edge | Test sketch |
|---|---|
| INT-F05.04-F06.01-01 | Periodic check: L3 dispatch calls reach L2. Probably exercised incidentally by P1/P2 tests. |
| INT-F07.03-F05.01-01 | Audit: escalation chain goes L2 -> L3 -> L1; periodic log review. |
| INT-F11.07-F09.01-01 | Static check: L5 module MUST NOT call gate write primitives. |
| INT-F12.05-F02.01-01 | Feed-forward audit: future-run L1 loads L6 artifacts when present. Low priority because it affects only later runs. |

---

## Priority 4 — Documented Only (0 edges)

No current edges fall here. (The F12.05 DEPENDS_ON was upgraded to P3 because future-run consumption is still worth a sanity check.)

---

## Wave F Handoff Summary

- **9 edges** get gate-level CI tests.
- **8 edges** get staging-integration tests.
- **4 edges** get audit-sampling coverage.
- **0 edges** are documented-only.

Wave F authors MUST NOT rewrite or downgrade the edge definitions in `proposals/edges.yaml`; they consume the edge set as-is and author test artifacts against each edge's `(source_atom_id, target_atom_id, edge_kind)` triple.

## Known Gaps That Wave F Cannot Fix

Wave F cannot raise F08 coverage above what E1d has emitted; the `SRC-ADR-EXIT` unsourced blocker (DEC-E1c-EXIT-UNSOURCED) must be resolved by a future wave authoring a dedicated exit-spine ADR. Until then, the F08-rooted edges stay `WEAK_EVIDENCE` and the F08 scorecard cannot exceed ~0.4.
