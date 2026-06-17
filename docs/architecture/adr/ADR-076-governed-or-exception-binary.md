# ADR-076 — GOVERNED-or-EXCEPTION Binary for `apps_*` Packages

**Status:** Accepted
**Date:** 2026-04-30
**Deciders:** apps_* owners, apps_shared substrate owner, governance review board
**Source plan:** `.claude/plans/apps-runtime-first-principles-e6ba58.md` (W7)
**Related:** ADR-023 (runtime HITL exit control), ADR-050 (intelligence ledger family)

---

## Context

The platform now has 7 `apps_*` packages: `apps_eval`, `apps_exec`, `apps_lic`,
`apps_research`, `apps_rfp`, `apps_rg`, `apps_shared`, `apps_underwriting_ai`.
Five are fully governed by `apps_shared.integrations.governed_app_runner.GovernedAppRunner`
(the substrate that codifies the L1→L0→C0→L2→L5+L6 pipeline). Two are
documented permanent exceptions:

- `apps_eval` — circular dependency (the substrate calls `evaluate_and_emit`,
  which would route through `apps_eval` itself).
- `apps_underwriting_ai` — regulatory domain constraint (legally-binding
  credit decisions cannot be funneled through a generic evidence-retrieval
  substrate).

Both exceptions implement compensating controls (see `apps_*_exception.py`)
and emit `BUS_T_telemetry` so the L6 observability surface is preserved.

The architectural shape is **first-principles correct**: every governed app
adopts the substrate; every exception is formally documented with a reason
code and compensating controls; `APP_REGISTRY` in
`apps_shared/integrations/app_registry.py` is the SSOT for this status.

### The gap that ADR-076 closes

Today, **the architecture is correct by convention**. There is no enforced
binary at CI time:

1. A new `apps_<name>/` package can be added to the repo without any
   `APP_REGISTRY` entry. The substrate will simply not run for it; runtime
   spine views will silently exclude it.
2. An app could partially adopt the substrate (e.g., call
   `run_governed_core` directly without registering as a `GovernedAppEntry`)
   and pass code review.
3. An app could be removed from the registry without anyone noticing, since
   no test enforces that every `apps_*` package on disk has a registry row.

These three failure modes cause silent regressions in governance coverage
that the rest of the system (ADG, the apps_underwriting_ai L_UNKNOWN
classification regression that W4 just fixed, the substrate hardening in
W1+W2) only surfaces accidentally.

## Decision

Adopt and enforce the **GOVERNED-or-EXCEPTION binary**:

> Every `apps_*` package on disk MUST appear in `APP_REGISTRY` as either:
>
> 1. A `GovernedAppEntry` — fully adopted; subclasses `GovernedAppRunner` and
>    runs the canonical L1→L0→C0→L2→L5+L6 pipeline.
> 2. A `FormalExceptionEntry` — permanent exception with a reason code,
>    compensating controls, owner, and review cadence.

Partial adoption, undocumented exceptions, and silent omission are all
forbidden.

### Enforcement layers

| Layer | Mechanism | Failure mode |
|-------|-----------|--------------|
| Advisory (today) | `apps_shared/integrations/app_registry.py` docstrings + this ADR | Silent omission |
| **Deterministic (W7)** | `ops_scripts/ci/check_app_registry_conformance.py` | Fail-closed in CI |
| Per-app conformance | Existing `tests/unit/apps_*/test_governance_conformance.py` | Per-app shape validation |

The W7 CI gate scans the repo root for `apps_*/` directories that contain
real Python source, then asserts every one is keyed in `APP_REGISTRY`. It
runs in pre-commit and as a standalone CI check.

## Consequences

### Positive

- **No silent governance regressions.** Adding a new `apps_<name>` package
  now requires either (a) substrate adoption + `GovernedAppEntry` row, or
  (b) `FormalExceptionEntry` row with a reason code and compensating
  controls. There is no third path.
- **Removal regressions surface immediately.** Deleting an `APP_REGISTRY`
  entry without removing the package fails CI.
- **Audit trail is durable.** Every governance decision (governed or
  exception) is on disk in `app_registry.py` rather than in tribal
  knowledge or code review history.
- **Aligns with constitutional §22 + ADR-050 pattern.** Same shape as the
  intelligence ledger family enforcement: SSOT registry + deterministic
  CI gate + advisory-tier rule.

### Negative / Trade-offs

- Adding a new app requires one extra step (registry entry). This is the
  intended friction.
- The CI gate must be kept in sync with the registry data shape. We mitigate
  by importing the registry rather than re-parsing the file.

### Migration

No migration needed: all 7 existing `apps_*` packages already have registry
entries (5 governed, 2 formal exceptions).

## Verification

- Plan: `.claude/plans/apps-runtime-first-principles-e6ba58.md` W7
- Implementation: `ops_scripts/ci/check_app_registry_conformance.py`
- Tests: `tests/unit/ops_scripts/ci/test_check_app_registry_conformance.py`

## Out-of-scope future work

- Promoting one of the formal exceptions to governed (would require
  resolving the underlying constraint; not driven by this ADR).
- Encoding the conformance gate's package-discovery rules in YAML so the
  set of allowed prefixes is configurable.
- Extending the binary to other subtrees (e.g., `tools_*`, `infra_*`) — out
  of scope for ADR-076; if needed, a separate ADR with per-subtree
  governance shape.
