# Wave E1b — Compound-to-Atomic Splits

**Scope:** Record every case where an E1a Family intent bundled more than one normative claim and how E1b decomposed it into single-claim atoms.

For each family, the source is the `intent` paragraph in `docs/wave_e/E1a_family_spine/proposals/families.yaml`.

---

## F01 — Request Intake and Envelope Check (6 atoms)

Bundled concerns in the intent:
- shape validation
- authentication verification
- policy precondition satisfaction
- deterministic rejection
- no-downstream-before-admission
- (implicit) structured rejection surfacing

Splits:

| Atom | Claim | Driver |
|---|---|---|
| F01.01 | Reject if shape fails | shape validation |
| F01.02 | Reject if auth fails | authentication |
| F01.03 | Reject if L5 precondition fails | policy precondition |
| F01.04 | Rejection MUST be deterministic | explicit audit requirement |
| F01.05 | Downstream MUST NOT run before admission | sequencing rule |
| F01.06 | Rejection responses MUST carry structured reason code | debuggability (WEAK_EVIDENCE) |

## F02 — L1 Reasoning and Plan Generation (5 atoms)

Bundled concerns: sole-planner, no-other-planners, consume-as-is, no-execute, no-route.

Splits: F02.01 (sole authority), F02.02 (non-L1 MUST NOT plan), F02.03 (consumers consume as-is), F02.04 (L1 MUST NOT execute), F02.05 (L1 MUST NOT route).

## F03 — L0 Route Decision and Switching (4 atoms)

Bundled concerns: sole router, no-other-routers, reject-unbound, one-route-per-step.

Splits: F03.01..F03.04. F03.04 is WEAK_EVIDENCE (determinism inference).

## F04 — Context Assembly and Grounding (4 atoms)

Bundled concerns: single grounding path, attribution, no-private-substitute, idempotence.

Splits: F04.01..F04.04. F04.01 and F04.04 are UNRESOLVED pending the `C0`/`L1` layer decision.

## F05 — L3 Orchestration (4 atoms)

Bundled concerns: orchestrate, no-plan, no-route, dispatch-to-L2.

Splits: F05.01..F05.04.

## F06 — L2 Task Execution (5 atoms)

Bundled concerns: execute, use-L0-route, no-plan, no-route, no-bypass-gate.

Splits: F06.01..F06.05. F06.05 is critical: it restates the Universal Write Gate monopoly from L2's lens.

## F07 — L2 Heal, Retry, and Recovery (4 atoms)

Bundled concerns: bounded heal/retry/recovery, bounded retry termination, surface to L3, no-silent-mutation.

Splits: F07.01..F07.04. F07.04 is NORMATIVE (follows from gate monopoly); others WEAK_EVIDENCE.

## F08 — Runtime Exit Control and Evaluation Spine (5 atoms)

Bundled concerns: single spine, apply L5 policy, record outcome, signal WG, no ad-hoc exit.

Splits: F08.01..F08.05.

## F09 — Universal Write Gate (5 atoms)

Bundled concerns: sole path, all-mutations-through, no-bypass, reject-missing-L5-signal, reject-missing-exit-signal.

Splits: F09.01..F09.05.

## F10 — L4 Durable Archive and State Authority (4 atoms)

Bundled concerns: authoritative state, canonical reads, writes-only-via-gate, no-shadow-state.

Splits: F10.01..F10.04.

## F11 — L5 Policy and Safety Authority (7 atoms)

Bundled concerns: authority, binds-L0, binds-L2, binds-WG, binds-exit, no-execute, no-mutate.

Splits: F11.01..F11.07. Seven atoms is the largest count in E1b; the five "binds X" claims are each their own atom to keep cross-family edges cleanly attached to a single source atom.

## F12 — L6 Observability and Future-Run Learning (6 atoms)

Bundled concerns: observe, no-current-run-influence, no-current-run-mutation, feed future runs, future-run consumer is L1, excluded enhancement.

Splits: F12.01..F12.05 plus F12.06 EXCLUDED (referencing OOS-001).

---

## Splits NOT Performed

Some apparent bundling was intentionally kept as a single atom:

- **"MUST be the sole authority that decomposes ... into a plan"** (F02.01): "decomposes" and "plan" are a single claim about L1's role, not two claims.
- **"MUST be the cross-cutting policy and safety authority"** (F11.01): "policy and safety" is a single authority role; splitting would create an artificial boundary.
- **"sole durable write path to authoritative state"** (F09.01): "sole" and "authoritative state" are one claim about the gate's monopoly, not two.

---

## Totals

- Families decomposed: 12
- Atoms produced: 59
- Splits per family: 4 (min) to 7 (max); mean ~4.9.
