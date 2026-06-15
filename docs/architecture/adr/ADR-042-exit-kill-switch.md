# ADR-042 — L5 Exit Kill-Switch Primitive

- **Status:** Accepted (primitive implemented; runtime integration remains policy-owned)
- **Date:** 2026-04-23
- **Accepted:** 2026-06-15 status reconciliation
- **Deciders:** Safety Officer (L5), Architecture
- **Impact Layers:** L5, §5 exit, UWG, L6 audit
- **Relates to:** ADR-023 (runtime HITL), ADR-038 (budget envelope), ADR-036 (trace-grader)

> **Implementation evidence (2026-06-15):** `agentic_core/L5_safety/eval_spine/kill_switch.py`,
> `agentic_core/L2_execution/enforcement/kill_switch.py`, and
> `config/schemas/kill_switch_audit.schema.json` exist. Operational policy
> rollout is tracked separately from accepting this primitive.

## 1. Context

Industry guardrail literature (Akira, Codebridge, practitioner consensus)
requires a standing primitive that halts classes of outcomes mid-session —
tenant, route, tool, cost-class. v33 §5 currently has dispositions
{allow_finish, deny_reroute, escalate_hitl, commit_request} but no verb to
**preemptively halt** all future dispositions in a declared scope.

The existing L5 layer has static enforcement gates; what is missing is a live
operator/auto primitive that asserts `policy_halt` for the duration of a
declared scope.

## 2. Decision

Declare an **`exit_kill_switch(scope, reason, ttl)`** primitive owned by L5,
addressable by operator action or automated safety trigger (e.g. rapid spike in
`policy_violation` rate, catastrophic cost event, abuse signal).

### 2.1 Scope grammar

```
scope ::=
    "fleet"                              # all requests, all tenants
  | "tenant:<tenant_id>"                 # all requests for a tenant
  | "route:<route_class>"                # L0 route class: R1A, R1B, R2, R3, R4, R5
  | "tool:<tool_name>"                   # any request invoking this tool
  | "agent:<agent_class>"                # specific agent family
  | "cost_class:<class_name>"            # e.g. cost_class:premium
```

Multiple scopes may be active simultaneously; disposition effect is the union.

### 2.2 Behavior at §5

When a run falls into any active kill-switch scope:

1. `ExitDecision.safety.policy_halt = true`.
2. `reason_code = grader.policy_halt`.
3. Disposition **forced to** `deny_reroute` by default, OR `escalate_hitl` if
   the kill-switch was declared with `on_hit: "escalate"`.
4. `ExitDecision.safety.severity_band = "critical"` (or carried from trigger).
5. UWG commit path is **unconditionally blocked** for the affected run — no
   override at this surface. A commit requires the kill-switch to be released.

### 2.3 Mid-run preemption

When a hard budget cap (ADR-038 §2.5) fires at 2× envelope, L5 invokes
`exit_kill_switch(scope="<this_request>", reason="hard_budget_cap", ttl=0)`
for the single request. The request aborts immediately with `policy_halt=true`.

### 2.4 Audit trail (non-negotiable)

Every kill-switch **activation**, **hit**, and **release** writes a row to the
L5 audit ledger (schema TBD in follow-up) with:

```
{
  "event":         "activate" | "hit" | "release",
  "scope":         "<scope expression>",
  "reason":        "<short>",
  "operator":      "<identity>" | "auto:<trigger_name>",
  "ttl_seconds":   int | null,
  "activated_at":  utc,
  "released_at":   utc | null,
  "hit_request_id":string | null
}
```

### 2.5 Release

- **Operator release** — explicit action by Safety Officer.
- **TTL expiry** — `ttl` was set and elapsed.
- **Auto-release guardrail** — if the activating trigger condition clears for a
  configurable cool-down period (default 15 min).

## 3. Consequences

- **Positive:** parity with industry guardrail pattern; single place to halt a
  class of outcomes; audit trail for every halt.
- **Negative:** an active kill-switch is observable to the outside as 4xx/5xx —
  must document behavior for clients.
- **Risk:** over-broad scopes (fleet) can cause outages. Mitigated by requiring
  two-person authorization for `fleet` scope in the resolver (follow-up).

## 4. Alternatives Considered

- **Per-route feature flags only.** Rejected — no unified verb, no unified
  audit trail, lacks scope grammar.
- **UWG-level veto only.** Rejected — UWG only sees commit path; can't halt
  `allow_finish` responses (e.g. data-exfil scenarios).

## 5. Open Items

- Code execution plan: L5 kill-switch store + hit resolver at §5.
- Audit ledger schema.
- Two-person-authorization policy for fleet scope.
- Client error contract when a request is killed (4xx code + reason_code
  surfacing).
