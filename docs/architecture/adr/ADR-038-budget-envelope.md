# ADR-038 — Per-Request Budget Envelope

- **Status:** Proposed
- **Date:** 2026-04-23
- **Deciders:** Safety Officer (L5), Architecture, Eval Lab
- **Impact Layers:** Ingress (E3), L5, §5 exit, L6, UWG
- **Relates to:** ADR-036 (trace-grader), ADR-037 (trajectory), ADR-027 (OTel alignment)

## 1. Context

Anthropic, Google, and industry guardrail literature all treat a per-request
**budget envelope** (tokens, latency, tool calls, cost) as a first-class contract
stamped at ingress and enforced at exit. v33 ingress (§1 E3) today stamps
`validated_request` / `request_id` / `trace_root` / `caller_scope_baseline` — it does
not stamp a budget envelope. v33 §5 does not have a budget-fit check.

`apps_eval/config/eval_policies.yaml` carries a single `latency_threshold_ms: 30000`
for scenarios; nothing propagates per-request.

## 2. Decision

Add a **`BudgetEnvelope`** to the ingress output contract and a corresponding
**`budget_fit`** check at §5 exit, projected into `ExitDecision.budget.*`.

### 2.1 Envelope shape (stamped at E3)

```
BudgetEnvelope {
  schema_version:     1
  tokens_max:         int  | null    # completion+prompt budget
  latency_ms_max:     int  | null
  tool_calls_max:     int  | null
  cost_usd_max:       float| null
  route_hint:         string|null    # optional preferred routing class
  origin:             "caller" | "tenant_default" | "route_default"
}
```

Null fields are **unbounded** and carry `budget_fit = true` trivially for that axis.

### 2.2 Defaults by source

Resolution order, first match wins:

1. Caller-supplied envelope (U2 API entry only; subject to tenant ceiling).
2. Tenant default (from L5 policy store).
3. Route-class default (L0 R1A/R1B/R2/R3/R4/R5 each has a policy default).
4. Global fallback (token=8 000, latency=30 000 ms, tool_calls=16, cost=$0.50).

All four sources are subject to a **tenant ceiling**; caller values are clamped,
not rejected.

### 2.3 Consumption tracking

- L6 observability tallies `tokens_consumed`, `latency_consumed_ms`,
  `tool_calls_consumed`, `cost_usd_consumed` via OTel spans (ADR-027 alignment).
- The §5 emitter reads the tally from the sealed trace and compares against the
  envelope. Each axis independently marks over-budget; `budget_fit = AND(all axes)`.

### 2.4 Disposition coupling

- `budget_fit == false` → `ExitDecision.reason_code = grader.budget_breach` →
  default disposition is **`escalate_hitl`** with `hitl_class = low_confidence` (the `HitlClass` enum in `agentic_core/L5_safety/exit_control/hitl_classes.py` does not currently carry a `budget_overrun` class; reason_code `grader.budget_breach` carries the specific signal; a follow-up ADR may extend the enum).
- L5 policy MAY downgrade to `deny_reroute` (e.g. unauthenticated anonymous
  caller) or `allow_finish` with warn verdict for low-severity overruns
  (configurable per tenant).

### 2.5 Mid-run enforcement (bounded, not runaway)

- Hard caps at 2× envelope on tokens/latency/tool_calls fire a preemptive
  abort through L5 exit_kill_switch (ADR-042) with `policy_halt=true`.
- Soft caps at 1× envelope do **not** abort mid-run; they surface at §5 only.

## 3. ExitDecision Projection

Populates `ExitDecision.budget` verbatim:
`budget_fit`, `tokens_envelope`, `tokens_consumed`, `latency_envelope_ms`,
`latency_consumed_ms`, `tool_calls_envelope`, `tool_calls_consumed`,
`cost_usd_envelope`, `cost_usd_consumed`.

## 4. Consequences

- **Positive:** parity with Anthropic/Google best-practice; auditable resource
  bounds; grounds cost-per-task metric emission (ADR-041 companion).
- **Negative:** ingress must stamp envelope even for anonymous U0 paths —
  fallback defaults must exist for every route class.
- **Risk:** too-tight defaults will cause false BUDGET_OVERRUN escalations.
  Mitigated by starting with generous global fallback (see §2.2) and tightening
  per-tenant as calibration data accumulates.

## 5. Alternatives Considered

- **Leave budget to each agent.** Rejected — violates L5 cross-cutting authority
  and makes §5 budget-fit prose unenforceable.
- **Enforce only at ingress.** Rejected — can't detect run-time overruns without
  exit check.
- **Enforce only mid-run (hard caps).** Rejected — no aggregate view at §5, no
  `ExitDecision.budget` surface.

## 6. Open Items

- Code execution plan: envelope stamp at E3 + consumption tally wiring
  (blocked on this ADR).
- Policy YAML shape for tenant ceilings and per-route defaults.
- OTel semconv alignment for `budget_*` attributes (follow-up to ADR-027).
