# Wave F3 — Escalation Authority Decision

Detailed rationale for how F07.03 is closed.

## Problem statement

F07.03 asserts: *"Unrecoverable failures MUST surface to L3 for re-planning."*

Prior sources considered in F2:

- SRC-ADR-001 (`docs/architecture/healing_dispatch_routing_adr.md`, ADR-F25-int) — carries `invalid_for_normative_use=True`. Its ESCALATED tier routes to HITL or deterministic abort, not to L3.
- SRC-ADR-002 (`HEALER_RETRY_HARDENING_SPEC.md`) — retry bounds but no escalation target.
- Constitutional rules — no escalation-target clause.

F2 held F07.03 at WEAK_EVIDENCE.

## Option evaluation

### Option A — revise `healing_dispatch_routing_adr.md`

Drop `invalid_for_normative_use=True` and extend the ESCALATED tier to include "surface to L3 for re-planning".

**Pros:** single source covers the full failure-handling stack.

**Cons:**
- Contradicts the ADR's original framing as a repo-internal current-state description.
- Retroactively changes the meaning of a released and accepted ADR.
- The ESCALATED tier's "HITL or deterministic abort" decision is still correct for the tier-decision layer; mixing it with re-planning escalation conflates two layers.
- Violates "do not fake this by stretching advisory text".

### Option B — author a new narrow ADR explicitly naming L3

**Pros:**
- Leaves ADR-F25-int unchanged and honest.
- Cleanly separates the tier-decision layer (which tier heals?) from the escalation layer (what happens after all tiers fail?).
- Normative scope is declared up front.
- Supports F07.03 directly via explicit wording.

**Cons:**
- Introduces a second ADR in the same general area. Mitigation: cross-reference ADR-F25-int in §1.

## Chosen option: B

Authored `docs/architecture/unrecoverable_failure_escalation_adr.md` (ADR-ESC-001). Registered as SRC-ADR-009.

### Companion decision: L3 charter

F07.03 needs BOTH:
1. An emitting declaration — "L2 MUST send the failure signal to L3" — provided by ADR-ESC-001 ESC-I1.
2. A receiving declaration — "L3 MUST accept the signal and emit a re-plan request" — provided by ADR-L3-001 L3-I3.

Without the receiving half, the emitting half is half-normative. With both, F07.03 has a full L2 → L3 → L1 re-plan contract.

**F07.03 final authority_binding:** `[SRC-INT-003, SRC-ADR-008, SRC-ADR-009]`.

## SRC-ADR-001 disposition (unchanged)

- Remains classified as ADVISORY.
- Remains `invalid_for_normative_use=True` in its source document.
- Is NOT added to F07.03's `authority_binding`.
- Continues to describe healing-tier semantics; ADR-ESC-001 is the escalation-layer authority sitting above it.

This preserves the constitutional discipline of never promoting an advisory source to normative use.

## Definition of "unrecoverable failure" (ADR-ESC-001 §3.1)

Declared explicitly to avoid ambiguity:

1. `max_attempts=3` exhausted across all healing tiers.
2. Scope-lock violation at a tier boundary.
3. HITL DECLINE at ESCALATED tier, or HITL unavailable when required.
4. Governance hard-fail with no guardian exemption.

Any other failure class is recoverable and does not trigger L3 escalation. This bounds F07.03 to a concrete event class.

## No conflict with other families

- F02 (L1 planning): untouched. L1 receives the re-plan request; it does not escalate anything here.
- F03 (L0 routing): untouched. Route authority stays with L0.
- F05 (L3 orchestration): strengthened via ADR-L3-001 (companion charter).
- F06 (L2 execution): the emitter side of ESC-I1 is L2; no F06 atoms are weakened.
- F07 (heal/retry/recovery): F07.03 closes; F07.01, F07.02, F07.04 unaffected.
- F08 (evaluation spine): untouched. Evaluation-spine exit policy is a separate concern.
- F09 (UWG): untouched. Escalation signals are not durable writes.

## Outcome

F07.03 closes. F07 family moves YELLOW → GREEN.
