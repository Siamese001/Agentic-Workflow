# Architecture Decision Record — L3 Orchestration Charter

**ADR ID:** ADR-L3-001
**Status:** Accepted
**Date:** 2026-04-17
**Authority tier:** T4_repo_canonical
**Normative use:** `invalid_for_normative_use = False` — this ADR IS a normative source for L3's orchestration role.
**Scope marker:** L3 orchestration authority for multi-step execution of an L1 plan.

---

## 1. Status

**Accepted.** This ADR codifies the charter and boundary of Layer 3 (Orchestration) in this repository's layered architecture. It does not mandate a module rewrite; it fixes the authority boundaries and the interaction contract with L0, L1, L2, L4, L5, and the Universal Write Gate (UWG).

---

## 2. Context

The governing semantics at the top of `docs/wave_e/00_schema/requirement_graph_schema.yaml` explicitly name L1, L0, L5, L4, and L6. L3 is implicit: it is the execution-time orchestrator that walks an L1 plan step-by-step and dispatches each step to L2 for task execution, subject to L0 route authority and L5 policy validation.

Existing repo artifacts that ground this role:
- `agentic_core/L3_orchestration/` — module root, with `core/`, `enforcement/`, `inference/`, `reasoning/`, `types/`, `utils/`, `workflow_engines/` subdirectories.
- `agentic_core/L3_orchestration/core/orchestrator_state_retry.py` — `OrchestratorStateRetry` with `max_attempts` bounded retry state.
- `docs/specs/hardening/AUTHORITY_HIERARCHY_INVARIANTS.md` (SRC-ADR-006) — names L1/L0/L2/L5/L4/L6/UWG but does not cover L3's charter.

Requirement-graph family **F05 (L3 Orchestration)** depends on L3's charter being canonically declared. Atom **F05.04** ("L3 MUST dispatch each plan step to L2") has had no normative source until this ADR.

---

## 3. Decision — L3 Charter

### 3.1 Role

**L3 is the sole execution-time orchestrator that walks an admitted L1 plan step-by-step and dispatches each step to L2 for task execution.**

L3 does NOT:
- decompose or re-decompose the plan (that is L1's authority)
- select the route or resolve route bindings (that is L0's authority)
- author or mutate cross-cutting policy (that is L5's authority)
- directly mutate durable state (that is UWG's sole path)
- replace or override L2 execution decisions within a step (L2 owns the execution body)

### 3.2 Authority Boundaries (L3-I1)

For every plan step in an admitted L1 plan:

1. **L3 MUST accept the step from L1** only after L0 has authorized the step's route binding (L0 remains the route authority).
2. **L3 MUST dispatch each plan step to L2** for execution, passing the L0-authorized route binding, the L5-validated policy envelope, and the grounded context (per `ADR-CTX-001`).
3. **L3 MUST NOT invoke L2 for a step that lacks a resolved L0 route binding.**
4. **L3 MUST NOT invoke L2 for a step that lacks an L5 policy-validated envelope** in environments where L5 validation is enabled.
5. **L3 MUST treat L2's returned `ExecutionResult` as authoritative for the step's execution outcome.** L3 MAY classify the outcome as success, recoverable failure, or unrecoverable failure, but MUST NOT rewrite the `ExecutionResult` itself.
6. **L3 MUST forward every durable-write signal from L2 through the Universal Write Gate.** L3 has no privileged write path.

### 3.3 Step Sequencing (L3-I2)

L3 walks plan steps in the order declared by L1's plan. L3 MAY:

- skip a step only when a prior step's outcome invalidates the skipped step's precondition and L1's plan declares the precondition link,
- retry a recoverable failure via the canonical retry path (`OrchestratorStateRetry` with bounded `max_attempts`, matching the constraints in `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md`),
- abort the plan walk when an unrecoverable failure surfaces (see §3.4).

L3 MUST NOT:
- reorder plan steps independently of L1,
- materialize steps not declared in the admitted plan,
- extend `max_attempts` beyond the bound declared in the retry hardening spec.

### 3.4 Unrecoverable Failure Handling (L3-I3)

**When L2 reports an unrecoverable failure (retry exhausted, scope-lock violation, or a governance hard-fail), L3 MUST:**

1. record the failure outcome,
2. halt further step dispatch for the current plan,
3. emit a re-plan request targeting L1 for the failed step (or abort the plan if re-planning is not available).

L3 does NOT perform the re-planning itself. L3 is the escalation target from L2 for unrecoverable failures; L1 remains the plan authority. The re-plan request is the signal that moves authority back to L1.

This invariant directly supports atom F07.03 ("Unrecoverable failures MUST surface to L3 for re-planning"). See also `docs/architecture/unrecoverable_failure_escalation_adr.md`.

### 3.5 Interaction with L5 Policy

L3 MUST consult the L5-validated policy envelope before dispatching a step. If the policy envelope is missing, invalid, or stale, L3 MUST treat the step as non-dispatchable and escalate (per §3.4) rather than dispatching with a degraded envelope.

### 3.6 Interaction with L4 and UWG

L3 MUST NOT hold direct references to L4 storage. All durable writes flow from L2 through UWG. L3 observes the committed `HandoffRecord` emitted by UWG for telemetry and for step-sequencing decisions (e.g., confirming a prior step's write committed before dispatching a dependent step).

### 3.7 Interaction with L6

L3 MUST NOT consult L6 observability data for current-run orchestration decisions. L6 is strictly future-run learning per the governing semantics. L3 MAY emit telemetry events that L6 records.

---

## 4. Consequences

### 4.1 Positive

- L3's role is now a first-class architectural contract, resolvable without re-deriving from process maps.
- F05.04 has a normative source citation.
- The L3 → L1 re-plan escalation path is declared, enabling F07.03 and `ADR-ESC-001` to be normatively grounded.
- Authority hierarchy (SRC-ADR-006) gains a consistent L3 layer with explicit boundaries.

### 4.2 Negative / tradeoffs

- **Implementation debt:** several L3 invariants (L3-I1 steps 4 and 5, L3-I2 retry binding) are codified but not fully gate-enforced. CI gates are implementation-debt items.
- **L3 retry semantics** inherit bounds from the healer retry spec. Divergence between L2 healing retries and L3 orchestration retries MUST be resolved at the retry spec revision, not at L3.

### 4.3 Non-consequences

- This ADR does NOT redefine L1's planning authority.
- This ADR does NOT add a new layer or new family.
- This ADR does NOT alter UWG's sole-durable-write-path invariant.
- This ADR does NOT specify workflow engine internals under `L3_orchestration/workflow_engines/`; those remain implementation detail.

---

## 5. Validation Criteria

- **L3-I1 dispatch invariants:** a CI gate that verifies every call site entering L2 execution carries an L0-authorized route binding and (when enabled) an L5 policy envelope. Test hook: `tests/architecture/test_l3_dispatch_authority.py` (to be authored).
- **L3-I2 sequencing invariants:** a test that confirms plan-step ordering is preserved across orchestration. Test hook: `tests/architecture/test_l3_step_sequencing.py` (to be authored).
- **L3-I3 escalation invariants:** a test that verifies unrecoverable failures halt dispatch and emit a re-plan request. Test hook: `tests/architecture/test_l3_unrecoverable_escalation.py` (to be authored).

Validation tests are implementation-debt items, not blockers for publishing this ADR.

---

## 6. References

- `agentic_core/L3_orchestration/` — module root
- `agentic_core/L3_orchestration/core/orchestrator_state_retry.py` — retry state shim
- `docs/specs/hardening/AUTHORITY_HIERARCHY_INVARIANTS.md` — adjacent authority ADR (does not cover L3)
- `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` — retry bounds inherited at §3.3
- `docs/architecture/context_assembly_adr.md` — grounded-context requirement at §3.2 step 2
- `docs/architecture/unrecoverable_failure_escalation_adr.md` — escalation partner ADR
- Requirement graph family F05; atoms F05.01, F05.02, F05.03, F05.04

---

## 7. Change History

| Version | Date | Note |
|---|---|---|
| 1.0 | 2026-04-17 | Initial charter — defines L3's dispatch, sequencing, escalation, and authority-boundary invariants. Authored in Wave F3 to close B6 blocker for F05.04. |
