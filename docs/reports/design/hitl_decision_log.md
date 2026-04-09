# HITL Decision Log
**Phase**: Design Only — No code changes permitted  
**Date**: 2026-04-09  
**Status**: ALL DECISIONS RESOLVED ✅

---

## HITL-001 — Exit Gate Implementation Path

| Field | Value |
|---|---|
| **hitl_id** | HITL-001 |
| **trigger_rule** | §HITL-1.1 (multiple plausible implementation paths); confidence 0.70 |
| **gap_ids** | GAP-004 |
| **req_ids** | REQ-012 |
| **blocking_batches** | B02 |
| **status** | RESOLVED ✅ |

**Decision**: **Option A — New standalone `exit_control_gate.py`**

Create `agentic_core/L5_safety/enforcement/exit_control_gate.py` as an independent module implementing X1A–X1D evaluation and `ExitDisposition` enum. Wire to `outcome_logger`, BUS_D/E signals, UWG trigger, and HITL trigger.

**Rationale**: Cleanest match to architecture spec. No regression risk on existing `policy_enforcement_point.py`. Testable in isolation.

---

## HITL-002 — Ingress Envelope Layer Placement

| Field | Value |
|---|---|
| **hitl_id** | HITL-002 |
| **trigger_rule** | §HITL-1.1 (layer placement decision); §HITL-1.2 (refactoring scope) |
| **gap_ids** | GAP-001 |
| **req_ids** | REQ-001, REQ-002 |
| **blocking_batches** | B01 |
| **status** | RESOLVED ✅ |

**Decision**: **Option A — `L5_safety/enforcement/ingress_envelope_check.py`**

Place the new E1–E6 ingress gate in `L5_safety/enforcement/` consistent with L5's cross-cutting policy authority. Rate limiter invocation, auth, tenant bind, trace_root stamping, and rejection slip emission all belong here.

**Rationale**: L5 is the canonical policy plane; placing ingress enforcement here is architecturally consistent with all other enforcement gates (`hitl_gate.py`, `policy_enforcement_point.py`, `circuit_breaker_gate.py`).

---

## HITL-003 — ExitDisposition Enum Layer Ownership

| Field | Value |
|---|---|
| **hitl_id** | HITL-003 |
| **trigger_rule** | §HITL-1.1 (cross-layer authority placement); confidence below 0.80 for alternative paths |
| **gap_ids** | GAP-004 |
| **req_ids** | REQ-012 |
| **blocking_batches** | B02 |
| **status** | RESOLVED ✅ |

**Decision**: **Option A — `L5_safety/types/exit_disposition_types.py`**

Define `ExitDisposition` enum (`ALLOW_RESPONSE`, `DENY_RETURN`, `ESCALATE_TO_HITL`, `COMMIT_TO_UWG`) in `L5_safety/types/`. L5 is the cross-cutting policy plane with authority over exit decisions.

**Rationale**: Exit disposition is a policy/safety concern, not an execution type. Placing it in `L2_execution/types/` would require L5 to import from L2, violating layer gravity. `L5_safety/types/core_contracts_types.py` already establishes the pattern for policy-typed contracts.

**Constraint recorded**: L2 may import `ExitDisposition` from L5 (acceptable since L5 is cross-cutting). L5 must never import from L2 for this type.

---

## HITL-004 — Exit-Control HITL vs Healing HITL Module Structure

| Field | Value |
|---|---|
| **hitl_id** | HITL-004 |
| **trigger_rule** | §HITL-1.1 (multiple plausible paths); §HITL-1.5 (change touching HITL, policy, write-path authority) |
| **gap_ids** | GAP-005 |
| **req_ids** | REQ-013 |
| **blocking_batches** | B03 |
| **status** | RESOLVED ✅ |

**Decision**: **Option A — Separate `exit_control_hitl.py` alongside existing `hitl_gate.py`**

Create `agentic_core/L5_safety/enforcement/exit_control_hitl.py` implementing H1–H5 exit-control HITL sequence:
- H1: freeze `authority_state=FROZEN`, `write_auth=NONE`
- H2: materialize bounded packet (no live state reference)
- H3: human reviews bounded packet only
- H4: human input treated as untrusted DATA by L5 validator
- H5: L5 re-clearance gate before any ALLOW or COMMIT

Keep `hitl_gate.py` unchanged for healing destructive operations (Y/N/S/A interactive TTY prompts).

**Rationale**: The two HITL contexts have fundamentally different semantics. Exit-control HITL involves a state freeze, authority lock, and re-clearance loop. Healing HITL involves interactive TTY prompts for destructive file operations. Conflating them in one module creates a security surface where exit-control freeze semantics could be bypassed by the healing code path.

**Constraints recorded**: No `SOVEREIGN_AUTO_APPROVE` or `ARCHIVE_BATCH_ACCEPT` bypass permitted in `exit_control_hitl.py`. No TTY check — exit-control HITL always materializes a packet; no interactive prompt.

---

## HITL-005 — Commandant's Gauntlet SME Sign-Off Mode

| Field | Value |
|---|---|
| **hitl_id** | HITL-005 |
| **trigger_rule** | §HITL-1.1 (multiple plausible paths); §HITL-1.5 (change touching HITL, write path, UWG) |
| **gap_ids** | GAP-009 |
| **req_ids** | REQ-020 |
| **blocking_batches** | B11 |
| **status** | RESOLVED ✅ |

**Decision**: **Option A — Async approval queue with `promotion_token` expiry**

SME sign-off is an asynchronous queue:
1. Proposed promotion enters `pending_sme_approval` queue (frozen state)
2. SME reviews asynchronously; issues a signed approval token with expiry timestamp
3. `CommandantGauntlet` checks token validity (signature + non-expired) before issuing `promotion_token` to UWG
4. Expired approval tokens are rejected; promotion must re-enter queue
5. No timeout auto-approval path exists

**Rationale**: Matches the `night shift / future visits only` language in C6 spec. Human review cadence is hours-to-days; a synchronous block would deadlock the promotion pipeline. The async queue with signed token is the only path that preserves SME authority without introducing a silent auto-approval bypass.

**Constraints recorded**:
- `promotion_token` issued only after: shadow replay passes, regression tests pass, signed SME approval token present and non-expired, sovereign approve issued
- UWG MUST verify the gauntlet signature on every `promotion_token` before ledger commit
- No `COMMANDANT_AUTO_APPROVE` environment variable bypass permitted
- Queue persistence must survive process restart (no in-memory-only queue)

---

## Decision Summary Table

| hitl_id | Description | Decision | Blocking batch | Status |
|---|---|---|---|---|
| HITL-001 | Exit gate implementation | Option A: New standalone `exit_control_gate.py` | B02 | ✅ RESOLVED |
| HITL-002 | Ingress envelope placement | Option A: `L5_safety/enforcement/ingress_envelope_check.py` | B01 | ✅ RESOLVED |
| HITL-003 | ExitDisposition enum ownership | Option A: `L5_safety/types/exit_disposition_types.py` | B02 | ✅ RESOLVED |
| HITL-004 | Exit-control HITL vs healing HITL | Option A: Separate `exit_control_hitl.py` | B03 | ✅ RESOLVED |
| HITL-005 | Commandant's Gauntlet SME mode | Option A: Async approval queue with token expiry | B11 | ✅ RESOLVED |

All HITL decisions resolved. Wave 1 (B01, B02, B03) and Wave 4 (B11) coding may proceed subject to normal constitutional gates.
