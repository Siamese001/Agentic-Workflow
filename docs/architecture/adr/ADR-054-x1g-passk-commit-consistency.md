# ADR-054 — X1G `pass^k` Commit-Consistency Gate

**Status**: Accepted
**Date**: 2026-04-24
**Deciders**: L3 + L4 (durable-state) owners
**Relates to**: ADR-023 (runtime HITL), ADR-040 (eval flywheel), ADR-044 (request intake envelope hardening)

## Context

Agent behavior is non-deterministic. v3 treats each run as single-shot pass/fail through X1A–D; there is no explicit gate that asks "does this agent succeed *reliably* on this class of task?". The X3C commit path writes to L4 durable storage — an agent with 75% per-trial success and no consistency check will corrupt the ledger ~25% of the time on high-stakes writes.

Anthropic's `pass^k` metric (probability **all** k attempts succeed, falling with k) is the industry-standard consistency metric when consistency is product-critical.

## Decision

Add **X1G (Consistency modifier)** to v4. Implementation: `PassKStore` in `agentic_core.L3_orchestration.exit_eval.consistency` (in-memory baseline) and a **durable SQLite backend** (this ADR mandates the backend contract; implementation lands in the same wave as this ADR).

### Thresholds (H6.1)

| Track | k | θ (pass^k) | Per-trial reliability required |
|---|---|---|---|
| Commit-path, customer-facing | 5 | 0.95 | ~0.9898 |
| Commit-path, internal | 5 | 0.85 | ~0.9680 |
| Non-commit (X3D allow only) | 5 | advisory | — |

Per-trial numbers are derived assuming i.i.d. Bernoulli (H6.1).

### Bucket identity (H6.3)

Consistency buckets key on `(trajectory_class, rubric_version, agent_version, policy_version)`. When any component changes, the bucket **resets** — historical reliability does not transfer across policy/model/rubric changes. This is the correct default under non-i.i.d. behavior.

### Small-sample rule (H6.4)

When fewer than k trials exist, X1G does **not** fall back to a smaller k or to a population mean. Route to X3B (HITL) with reason `INSUFFICIENT_HISTORY`. Counterintuitive but correct: a commit-path write without reliability evidence is equivalent to no reliability evidence.

### Durable backend contract

Production `PassKStore` MUST:
- Persist across process restarts (SQLite file or Redis with AOF).
- Return `INSUFFICIENT_HISTORY` fail-closed on backend read failure (`CONSISTENCY_HISTORY_UNAVAILABLE` reason code — H8).
- Be thread-safe under concurrent `record` / `check`.
- Support bucket reset on key-tuple change (automatic via keying).
- Cap per-bucket memory/rows at `max_retained ≥ k_max_used_anywhere`.

Implementation: `agentic_core/L3_orchestration/exit_eval/consistency_sqlite.py` (this ADR). Interface-compatible with in-memory `PassKStore`; caller-transparent.

### Operational consequence

Many commit-path trajectory_classes will not clear θ=0.95 early in deployment. **By design** — X1G surfaces reliability gaps before L4 corruption. Relaxing θ is a constitutional regression (see `constitutional.md` §10 zero-regression), not a convenience.

## Consequences

**Positive**:
- Commit-path writes to L4 are gated on *demonstrated reliability*, not single-trial luck.
- Non-i.i.d. bucket reset prevents false confidence after policy/model/rubric churn.
- Durable backend makes X1G meaningful across process restarts (the in-memory baseline silently loses history on restart — unacceptable for commit gating).

**Negative / accepted cost**:
- Early-deployment X1G denial rate is high until buckets fill. Requires ops runbook entry (H9 #3).
- Per-bucket storage growth: ~50 bytes/trial × max_retained rows × N buckets. Bounded; not a concern at typical scale.

## Alternatives considered

1. **`pass@k` (any-success)** — rejected: suitable for code-search agents where one success suffices; wrong semantics for commit-path where consistency is product-critical.
2. **Population-mean fallback on insufficient history** — rejected: violates H6.4 invariant; smooths noise and hides new-regime brittleness.
3. **In-memory only, no durable backend** — rejected: process restart = silent history loss = commit-gate circumvention.
4. **Redis-only backend** — rejected: Redis outage = X1G unavailable = X3B storm. SQLite primary + Redis hot cache is the correct tier.

## Open items

- SQLite pragmas: WAL mode and `synchronous=NORMAL` chosen for throughput. Revisit if durability incidents observed.
- Migration path from in-memory `PassKStore` to SQLite: wrapper defaults to SQLite if `$AG_PASSK_STORE_PATH` set, else in-memory (tests use in-memory).
- Retention policy beyond `max_retained`: buckets not written to in >90 days get GC'd. Out of scope for this ADR; tracked in plan.

## References

- v4 spec §X1G
- Hardening: `v4_hardening_addendum.md` H6 (`pass^k` math)
- In-memory baseline: `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/exit_eval/consistency.py`
- Durable impl: `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/exit_eval/consistency_sqlite.py` (this ADR)
- Tests: `@c:/Git/Agentic-Workflow/tests/agentic_core/L3_orchestration/exit_eval/test_consistency_sqlite.py`
