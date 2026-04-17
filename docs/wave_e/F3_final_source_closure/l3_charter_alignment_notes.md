# Wave F3 — L3 Charter Alignment Notes

Records how ADR-L3-001 aligns with the existing layer architecture and does not weaken prior family semantics.

## Governing semantics re-check

From `docs/wave_e/00_schema/requirement_graph_schema.yaml`:

- "L1 decomposes and plans"
- "L0 is route authority"
- "L5 is cross-cutting policy authority"
- "L4 is authoritative durable state"
- "Universal Write Gate is the sole durable write path"
- "L6 supports future-run learning only, never current-run mutation"

L3 is not mentioned explicitly. This is intentional: L3 is derivative authority — it walks plans from L1 and dispatches to L2. F05 has always been L3-owned in the canonical families. ADR-L3-001 makes this derivative authority explicit without introducing a new layer.

## Per-layer alignment check

| Layer | L3 relationship per ADR-L3-001 | Conflict with prior canonical claims? |
|---|---|---|
| L0 (route authority, F03) | L3 MUST accept only L0-authorized steps; MUST NOT resolve routes itself. | None. F03.01–F03.04 unchanged. |
| L1 (plan authority, F02) | L3 walks the plan; does NOT decompose. Re-plan requests go back to L1. | None. F02.01–F02.05 unchanged. |
| L2 (task execution, F06) | L3 dispatches each step to L2; treats L2's `ExecutionResult` as authoritative. | None. F06.01–F06.05 unchanged. |
| L4 (durable state, F10) | L3 MUST NOT hold direct L4 references. | None. F10.01–F10.04 unchanged. |
| L5 (cross-cutting policy, F11) | L3 MUST consult L5 policy envelope before dispatch. | None. F11 atoms unchanged. |
| L6 (observability, F12) | L3 MUST NOT consult L6 for current-run decisions; MAY emit telemetry for L6. | None. F12 atoms unchanged. |
| UWG (F09) | L3 MUST NOT bypass UWG; all durable writes flow L2 → UWG. | None. F09.01–F09.05 unchanged. |
| Evaluation spine (F08) | Not mentioned directly in L3-I1/I2/I3. L3 observes UWG's `HandoffRecord` which carries the evaluation spine's approval signal transitively. | None. F08 atoms unchanged. |

No prior atom's claim is weakened. ADR-L3-001 is strictly additive.

## F05 atom-by-atom check

| Atom | Claim | ADR-L3-001 support | Post-F3 evidence |
|---|---|---|---|
| F05.01 | L3 MUST orchestrate multi-step execution of an L1 plan. | L3-I2 sequencing invariant. | Already NORMATIVE in v1.2. No F3 change; remains NORMATIVE. |
| F05.02 | L3 MUST NOT re-decompose the plan. | L3-I1 step 1 bullets "does NOT decompose or re-decompose the plan". | Already NORMATIVE in v1.2. No F3 change. |
| F05.03 | L3 MUST forward writes through UWG. | L3-I1 step 6 + §3.6. | Already NORMATIVE in v1.2. No F3 change. |
| F05.04 | L3 MUST dispatch each plan step to L2. | L3-I1 step 2. | **Upgraded WEAK → NORMATIVE via SRC-ADR-008.** |

Only F05.04 changes. F05.01/.02/.03 are already NORMATIVE with prior bindings; ADR-L3-001 is consistent with them but does not need to be added to their existing bindings (additive-only rule).

## Interaction with ADR-ESC-001

ADR-L3-001 §3.4 (L3-I3) is the receiving half of the escalation contract. ADR-ESC-001 ESC-I1 is the emitting half. The two are complementary:

- ESC-I1: "L2 MUST surface unrecoverable failures to L3."
- L3-I3: "L3 MUST halt dispatch and emit a re-plan request to L1."

No conflict. Both ADRs cite each other at §6 References.

## Interaction with ADR-F25-int

ADR-L3-001 does NOT mention healing tiers. ADR-F25-int continues to describe LOCAL_AGENT / COORDINATED / ESCALATED tier semantics inside L2's healing subsystem. The L3 charter sits one layer above and treats all L2 healing as an L2-internal concern whose unrecoverable output (per ADR-ESC-001) escalates to L3.

No conflict.

## Implementation grounding

- `agentic_core/L3_orchestration/` module root.
- `agentic_core/L3_orchestration/core/orchestrator_state_retry.py` — `OrchestratorStateRetry` with `max_attempts=3`.
- `agentic_core/L3_orchestration/workflow_engines/` — workflow engine implementations (detail, not charter-bearing).

The L3 charter does not require any new module. It codifies invariants over the existing `L3_orchestration/` tree.

## Outcome

ADR-L3-001 is consistent with all 12 existing canonical families and with ADR-ESC-001. F05.04 closes. F05 family moves YELLOW → GREEN. No prior family regresses.
