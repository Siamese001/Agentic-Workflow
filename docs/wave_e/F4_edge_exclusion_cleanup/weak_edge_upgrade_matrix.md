# Wave F4 — Weak Edge Upgrade Matrix

Per-edge direct-support analysis against v1.3 canonical sources. Bar:

> *Upgrade edge evidence only where existing canonical sources already support the relationship directly.*
> *Do not upgrade an edge just because both endpoint atoms are normative.*

Each row records the edge claim, endpoint evidence in v1.3, candidate sources, whether the candidate directly states the edge claim, and the final disposition.

## Result summary

| Edge ID | v1.3 endpoints | Upgrade? | New evidence_class |
|---|---|---|---|
| INT-F02.01-F01.05-01 | N / N | ✅ | NORMATIVE |
| INT-F05.04-F06.01-01 | N / N | ✅ | NORMATIVE |
| INT-F07.03-F02.01-01 | N / N | ✅ | NORMATIVE |
| INT-F07.03-F05.01-01 | N / N | ✅ | NORMATIVE |
| INT-F08.04-F09.01-01 | N / N | ✅ | NORMATIVE |
| INT-F09.05-F08.04-01 | N / N | ✅ | NORMATIVE |
| INT-F12.05-F02.01-01 | N / N | ✅ | NORMATIVE |
| INT-F12.08-F08.03-01 | N / N | ✅ | NORMATIVE |

**8 of 8 weak edges upgrade.** 0 remain WEAK. Each upgrade is grounded in a direct-statement source, not merely endpoint strength.

---

## Per-edge analysis

### 1. INT-F02.01-F01.05-01 (DEPENDS_ON)

- **Claim:** F02.01 (L1 plan authority) DEPENDS_ON F01.05 (no downstream invocation before admission).
- **v1.3 binding:** `[SRC-INT-002]` WEAK_EVIDENCE.
- **Direct-support test:**
  - F01.05's own claim ("Downstream reasoning, routing, and execution MUST NOT be invoked before admission completes") *is* the DEPENDS_ON statement — it normatively orders admission before plan production.
  - SRC-INT-001 (AGENTS.md layer separation) normatively asserts L1 runs only on admitted requests.
  - SRC-INT-003 governing semantics frames the same ordering.
  - SRC-RULE-001 admission-gate discipline is constitutional.
- **Disposition:** **UPGRADE** → `[SRC-RULE-001, SRC-INT-001, SRC-INT-003]`.

### 2. INT-F05.04-F06.01-01 (REQUIRES)

- **Claim:** F05.04 (L3 dispatch to L2) REQUIRES F06.01 (L2 executes dispatched tasks).
- **v1.3 binding:** `[SRC-INT-003]` WEAK_EVIDENCE. Endpoint F05.04 is newly NORMATIVE in v1.3 via SRC-ADR-008.
- **Direct-support test:**
  - SRC-ADR-008 (ADR-L3-001) L3-I1 step 2 explicitly declares L3 MUST dispatch each plan step to L2.
  - L3-I1 also specifies L3 treats L2's `ExecutionResult` as authoritative — L3 dispatch cannot function without L2 execution.
  - This is a direct REQUIRES statement, not merely adjacent.
- **Disposition:** **UPGRADE** → `[SRC-INT-003, SRC-ADR-008]`.

### 3. INT-F07.03-F02.01-01 (CONDITIONAL_ON "Unrecoverable L2 task failure detected")

- **Claim:** F07.03 (unrecoverable failures surface to L3) CONDITIONAL_ON F02.01 (L1 plan authority), guarded by the unrecoverable-failure condition.
- **v1.3 binding:** `[SRC-INT-003]` WEAK_EVIDENCE. Endpoint F07.03 is newly NORMATIVE in v1.3.
- **Direct-support test:**
  - SRC-ADR-009 (ADR-ESC-001) ESC-I1 names L3 as the escalation target and bounds the unrecoverable condition (max_attempts=3, scope-lock violation, HITL DECLINE, governance hard-fail).
  - SRC-ADR-008 L3-I3 declares L3 emits a re-plan request back to L1 (F02.01's owning family) on accepting the escalation signal. This is the conditional dependency on F02.01.
  - Together the two ADRs form the full L2 → L3 → L1 re-plan contract the edge encodes.
- **Disposition:** **UPGRADE** → `[SRC-INT-003, SRC-ADR-008, SRC-ADR-009]`.

### 4. INT-F07.03-F05.01-01 (REQUIRES)

- **Claim:** F07.03 REQUIRES F05.01 (L3 orchestration family).
- **v1.3 binding:** `[SRC-INT-003]` WEAK_EVIDENCE.
- **Direct-support test:**
  - SRC-ADR-009 ESC-I1 binds the escalation to L3 orchestration; F05.01 is the L3 orchestration atom.
  - SRC-ADR-008 L3-I3 receiving contract explicitly names the orchestration path as the escalation acceptor.
- **Disposition:** **UPGRADE** → `[SRC-INT-003, SRC-ADR-008, SRC-ADR-009]`.

### 5. INT-F08.04-F09.01-01 (REQUIRES)

- **Claim:** F08.04 (spine signals UWG for outcome writes) REQUIRES F09.01 (UWG sole durable write path).
- **v1.3 binding:** `[SRC-INT-003]` WEAK_EVIDENCE.
- **Direct-support test:**
  - F08.04's own claim is the REQUIRES: the spine's obligation is expressed relative to UWG.
  - SRC-ADR-003 (eval_pipeline_acceptance) names `GovernedHandoffAgent` as the sole durable-write seam, binding the spine's outcome emission directly to UWG signaling. This is a direct statement.
- **Disposition:** **UPGRADE** → `[SRC-INT-003, SRC-ADR-003]`.

### 6. INT-F09.05-F08.04-01 (REQUIRES)

- **Claim:** F09.05 (UWG rejects writes lacking exit signal) REQUIRES F08.04 (spine signals UWG).
- **v1.3 binding:** `[SRC-INT-003]` WEAK_EVIDENCE.
- **Direct-support test:**
  - F09.05's own claim is the REQUIRES: UWG depends on the exit signal as precondition.
  - SRC-ADR-003 names `ExitControlGate.evaluate_sealed()` as the sole live gate call — directly supporting UWG's dependency on the spine.
- **Disposition:** **UPGRADE** → `[SRC-INT-003, SRC-ADR-003]`.

### 7. INT-F12.05-F02.01-01 (DEPENDS_ON)

- **Claim:** F12.05 (future-run artifacts consumed only by L1) DEPENDS_ON F02.01 (L1 plan authority).
- **v1.3 binding:** `[SRC-INT-002]` WEAK_EVIDENCE.
- **Direct-support test:**
  - F12.05's own claim literally names L1 as the consumer — the DEPENDS_ON is self-supporting.
  - SRC-INT-004 (AGENTS.md Memory Lifecycle) declares the session-start recall protocol binding L1 reasoning to prior-run artifacts.
  - SRC-RULE-001 §17 (memory lifecycle mandatory) gives constitutional force.
  - SRC-INT-001 layer separation confirms L1 reasoning as the only current-run consumer of future-run artifacts.
- **Disposition:** **UPGRADE** → `[SRC-RULE-001, SRC-INT-001, SRC-INT-004]`.

### 8. INT-F12.08-F08.03-01 (DEPENDS_ON)

- **Claim:** F12.08 (L6 records F08 spine outcomes) DEPENDS_ON F08.03 (spine records run outcome).
- **v1.3 binding:** `[SRC-INT-004]` WEAK_EVIDENCE.
- **Direct-support test:**
  - F12.08's own claim literally names the F08 spine as the source of recorded outcomes.
  - SRC-ADR-003 names the spine's outcome-recording responsibility (`evaluate_and_emit()` as sole canonical choke point).
  - SRC-INT-004 memory lifecycle defines the write-back path from spine outcomes into persistent memory.
- **Disposition:** **UPGRADE** → `[SRC-INT-004, SRC-ADR-003]`.

---

## Edges that remain WEAK after F4

**None.** All 8 v1.3 weak edges have direct-statement support from existing canonical sources. None required a new source to close.

## Note on not over-reaching

The F4 bar was deliberately stricter than "both endpoints NORMATIVE". For each edge, the direct-support test above identified an existing canonical source (or combination of sources) whose text states the edge claim — not merely the endpoint atom claims. If a candidate edge had failed that test, it would have remained WEAK_EVIDENCE. None did.
