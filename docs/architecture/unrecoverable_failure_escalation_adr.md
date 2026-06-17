# Architecture Decision Record — Unrecoverable Failure Escalation to L3 for Re-planning

**ADR ID:** ADR-ESC-001
**Status:** Accepted
**Date:** 2026-04-17
**Authority tier:** T4_repo_canonical
**Normative use:** `invalid_for_normative_use = False` — this ADR IS a normative source for the L2→L3 escalation contract on unrecoverable failures.
**Scope marker:** Escalation target for unrecoverable L2 task-execution failures.

---

## 1. Status

**Accepted.** This ADR names L3 as the sole escalation target for unrecoverable L2 task-execution failures, complementing `ADR-L3-001` (L3 charter) and `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` (SRC-ADR-002, retry bounds). It does not supersede `docs/architecture/healing_dispatch_routing_adr.md` (ADR-F25-int) — that ADR remains the authoritative description of the confidence-scored healing dispatch tiers. This ADR sits above the healing-tier decision and fixes what happens AFTER a healing attempt at tier ESCALATED fails terminally.

---

## 2. Context

Requirement-graph atom **F07.03** asserts: *"Unrecoverable failures MUST surface to L3 for re-planning."* Prior to this ADR the atom was held at WEAK_EVIDENCE because the only candidate source — `healing_dispatch_routing_adr.md` — carries `invalid_for_normative_use = True` and names HITL or deterministic abort at the ESCALATED tier, not L3 re-planning.

F07.03 is a higher-level escalation contract than the healing tier decision. The healing-tier ADR answers *"which tier attempts the heal?"*. This ADR answers *"what happens when every tier of healing has failed and the failure is unrecoverable?"*.

---

## 3. Decision — ESC-I1 Escalation Target

**When an L2 task execution produces an unrecoverable failure, the failure MUST surface to L3 as an escalation event. L3, per its charter (`ADR-L3-001` §3.4), MUST halt further step dispatch for the current plan and emit a re-plan request to L1.**

### 3.1 Definition of "unrecoverable failure"

A failure is unrecoverable when any of the following is true:

1. `HealerRetryManager.execute_with_retry()` has exhausted `max_attempts = 3` across all healing tiers (LOCAL_AGENT → COORDINATED → ESCALATED) per `HEALER_RETRY_HARDENING_SPEC.md`.
2. Scope-lock has been violated at a tier boundary (`RetryConfig.scope_lock = True`). Scope-lock violations are non-retryable.
3. The HITL gate at the ESCALATED tier returns DECLINE, or is not operationally available in environments where it is required.
4. The violation has been classified as a governance hard-fail (constitutional rule breach with no guardian exemption).

### 3.2 Escalation path

The escalation path from L2 to L3 is:

1. L2 (or the healer subsystem) determines the failure is unrecoverable per §3.1.
2. L2 MUST emit an `UnrecoverableFailure` signal carrying: the failing step's `plan_step_id`, the failure classification from §3.1, the last healing tier reached, and the failure's `ExecutionTrace` excerpt.
3. L3 MUST receive the signal via its orchestration path and MUST NOT silently drop it.
4. L3 applies `ADR-L3-001` §3.4: halt dispatch, record outcome, emit re-plan request to L1 (or abort the plan if re-planning is not available).
5. L3 MUST NOT attempt to resume the failing step without an updated plan from L1.

### 3.3 What this ADR does NOT permit

- L2 MUST NOT skip L3 and call L1 directly for re-planning. L3 is the escalation choke point.
- L2 MUST NOT attempt a fourth healing attempt after `max_attempts = 3` is exhausted, even through a different call path.
- HITL DECLINE at ESCALATED tier MUST propagate upward to L3 as an unrecoverable failure. Silent abort with no L3 notification is forbidden.
- L3 MUST NOT re-plan autonomously. The re-plan request is directed at L1; L1 remains the plan authority.

### 3.4 Relation to HITL

When the ESCALATED healing tier routes to a HITL gate (per ADR-F25-int §3.1), two outcomes are possible:

- **HITL APPROVE:** the healing attempt may proceed with human-endorsed correction. No escalation to L3 occurs.
- **HITL DECLINE or unavailable:** the failure becomes unrecoverable under §3.1 item 3. L3 escalation applies.

This ADR does not redefine the HITL gate's input or decision semantics — those remain in `.claude/rules/hitl-enforcement.md`.

---

## 4. Consequences

### 4.1 Positive

- F07.03 has a normative source citation.
- The boundary between "healing tier decision" (`ADR-F25-int`) and "post-healing escalation contract" (this ADR) is explicit and non-overlapping.
- L3's escalation responsibility is a single-sentence contract instead of an implicit expectation.
- Together with `ADR-L3-001`, this ADR makes the full unrecoverable-failure flow (L2 → L3 → L1 re-plan) a canonical architectural decision.

### 4.2 Negative / tradeoffs

- **Implementation debt:** the `UnrecoverableFailure` signal type is not yet uniformly implemented across L2's healer subsystem and L3's orchestration path. The type contract is tracked as an implementation-debt item.
- **Backward interaction with ADR-F25-int:** ADR-F25-int remains `invalid_for_normative_use = True` by design (it describes internal tier semantics). This ADR is the normative counterpart; the two must be read together.

### 4.3 Non-consequences

- This ADR does NOT revise ADR-F25-int's tier names, thresholds, or scope-lock semantics.
- This ADR does NOT add a new family or atom.
- This ADR does NOT change UWG's sole-durable-write-path invariant (escalation signals are not durable writes in the UWG sense).
- This ADR does NOT specify the wire format of the `UnrecoverableFailure` signal; that is implementation detail.

---

## 5. Validation Criteria

- **ESC-I1 escalation:** a test verifying that every code path producing an unrecoverable failure emits the `UnrecoverableFailure` signal and that L3 receives it. Test hook: `tests/architecture/test_unrecoverable_escalation.py` (to be authored).
- **No-skip invariant:** a static gate forbidding L2 from calling L1 directly for re-planning. Test hook: `tests/architecture/test_l2_no_direct_l1_replan.py` (to be authored).

Validation tests are implementation-debt items, not blockers for publishing this ADR.

---

## 6. References

- `docs/architecture/healing_dispatch_routing_adr.md` — tier decision (invalid_for_normative_use=True by design)
- `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` — retry bounds
- `docs/architecture/l3_orchestration_charter_adr.md` — L3 charter; §3.4 is the receiving contract
- `.claude/rules/hitl-enforcement.md` — HITL gate semantics
- Requirement graph family F07; atom F07.03

---

## 7. Change History

| Version | Date | Note |
|---|---|---|
| 1.0 | 2026-04-17 | Initial ADR — names L3 as the sole escalation target for unrecoverable L2 failures. Authored in Wave F3 to close F07.03 blocker. Sits above ADR-F25-int at the post-healing escalation layer. |
