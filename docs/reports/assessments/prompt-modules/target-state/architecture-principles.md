<!-- VERSION: 0.1.0 -->
# ARCHITECTURE DESIGN PRINCIPLES — AUDITABLE INVARIANTS (L0–L6)

> These are binding system invariants distilled into audit checks; you must evaluate them where relevant to the V15 capability set.

## P1. Fail-Closed Defaults (GLOBAL)

* Default action is **BLOCK** at boundaries.
* Missing required header/token/schema field/signature/health check halts progression.
* Timeout == reject (never partial approval).
* Degraded mode is a freeze: if validation services are unavailable, state mutation is forbidden.

## P2. Determinism & Replayability (GLOBAL)

* Every request is replayable: same `(payload + policy_hash + retrieved_context_set)` ⇒ same plan + same allowed side-effects.
* Any stochastic component is bounded, logged, and excluded from commit paths unless proven deterministic in sandbox/double-run.

## P3. No Silent State Mutation (GLOBAL)

* Only execution path may mutate external state; planning/knowledge/observability must be physically incapable of writes.
* No implicit writes: any side-effect not registered in the Side-Effect Registry is an abort.
* `apps_*` code MUST NOT mutate external state or governed repos/config; it is treated as an untrusted caller and must traverse the same L2 chokepoint + capability tokens.

## P4. Immutable Traceability (GLOBAL)

* TraceID is mandatory and immutable.
* Loss of TraceID is fatal.
* All artifacts are TraceID-addressable (logs/metrics/diffs/snapshots/tokens/decisions).

## P5. Authority Is Tokenized (GLOBAL)

* Write authority requires signed artifacts; conversational approval is non-authoritative.
* Tokens are scoped and expiring; bind (TraceID, action-set, target-set, policy-hash, timestamp, nonce).

### P5.1 Capability-Gated Execution Boundary (P0, GLOBAL)

* L2 tool/action invocation MUST be capability-gated at a **single chokepoint** (no scattered checks).
* Capability tokens MUST be typed, deterministic artifacts, semantic-clock bound, and trace-addressable.
* Every attempted invocation MUST emit a typed decision artifact (ALLOW or DENY).
* Absence of a valid capability token at the L2 boundary MUST FAIL-CLOSED (abort).
* Capability scope MUST include (minimum): permitted operations + permitted targets + max invocations.

This requirement is a prerequisite for any governed improvement activation in §16.

## P6. Explicit Boundaries / Zero Trust Between Layers (GLOBAL)

* Layer APIs are typed and versioned; cross-layer calls must conform to schemas.
* Health is binary; unknown health treated as unhealthy.
* `apps_*` folders are outside the control spine: they may consume `agentic_core` only through typed public entrypoints (routing + prompt composition). Direct reach into internal enforcement/policy/prompt-governance internals is forbidden (P6).

---
