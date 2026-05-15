# ADR-078 — `apps_*` Spine Delegation Invariant

**Status**: Accepted
**Date**: 2026-04-30
**Plan**: `.windsurf/plans/adg-three-bucket-unified-c4f8e2.md` (W3 P3.2)
**Tier**: B (advisory) at acceptance; flips to Tier A (fail-closed) in W5 P5.4
**Supersedes**: planning fragment in `adg-ci-spine-delegation-gate-438b16.md` (now superseded by the unified plan)

## Context

The agentic stack supports two valid runtime modes:

- **Mode A (core-only)**: `user → agentic_core spine → output`
- **Mode B (app overlay)**: `user → apps_* enrichment → agentic_core spine → output`

The forbidden mode is:
`user → apps_* standalone mini-runtime → output` — i.e., an `apps_*` package
that reimplements intake/route/execute logic instead of delegating to
`agentic_core/L0_routing`, `L1_cognition`, `L2_execution`.

This invariant is **not** mechanically detectable at author time (a hook on
file write cannot tell legitimate enrichment from forbidden re-implementation).
It **is** detectable at commit/CI time as a structural ADG property: every
`apps_*/` package MUST have at least one import edge into the spine layers.

A live audit on snapshot `adg_indexed_04302026_1319.sqlite` shows the rule is
not vacuous — `apps_underwriting_ai` has 693 import edges total but **zero**
into `agentic_core.L[0-2]_*`, exactly the violation pattern this ADR addresses.

## Decision

Ship `ops_scripts/ci/check_apps_spine_delegation.py` as a fail-closed CI gate
with this invariant:

> For every `apps_*/` top-level package, the ADG snapshot MUST contain ≥1
> import edge whose `source_file` starts with `apps_X/` and whose destination
> node resolves to a module in `agentic_core/L0_routing/`,
> `agentic_core/L1_cognition/`, or `agentic_core/L2_execution/`. Packages
> declared in `config/apps_spine_delegation_allowlist.yaml` are exempt
> with an auditable reason and an expiry date.

The gate runs in two modes:

| Mode | Default | Behavior on violation |
|---|---|---|
| `advisory` (W3 acceptance) | yes | exit 0, write JSON report |
| `strict` (W5 P5.4 flip) | no, until W5 | exit 1 |

Mode is controlled by `APPS_SPINE_DELEGATION_GATE_MODE ∈ {advisory, strict}`.
Bypass: `APPS_SPINE_DELEGATION_GATE_BYPASS=1` (logged to violations report).

## Consequences

### Positive

- Catches a structural drift class with **zero current detection**
- Pure ADG-derived invariant — no AST scanning, no regex hand-waving
- Aligns with constitutional §22 (graph-layer primary driver) and §28
  (SQLite-direct fallback hierarchy)
- Per-package allowlist makes known-violations auditable and time-bounded

### Negative / risks

- Requires a fresh-enough ADG snapshot to be accurate. Mitigation: gate
  reads the latest non-sentinel `adg_indexed_*.sqlite` and surfaces snapshot
  age in the report. `--snapshot <path>` override for tests.
- v1 catches only the "no spine import" pattern; the stricter "no own
  intake-router-executor triple" check is deferred to a future ADR. The
  simpler check already catches the obvious case (`apps_underwriting_ai`).

### Neutral

- `apps_shared/` is treated like every other apps package. Its 82 spine
  imports satisfy the rule; if it ever drops to zero, it is flagged like any
  other app and must be allowlisted with a reason.

## Allowlist Format

```yaml
# config/apps_spine_delegation_allowlist.yaml
allowed_packages:
  - package: apps_underwriting_ai
    reason: "Pending spine delegation remediation per NEXT_STEP."
    expires: "2026-06-30"  # ISO date; gate warns within 30 days, errors after
```

Each entry MUST carry:
- `package` (string, must match a real `apps_*/` directory)
- `reason` (non-empty string — bare `""` rejected)
- `expires` (ISO date — gate fails closed when allowlist entry is past expiry)

## Pairing — advisory rule

This deterministic gate pairs with the (separate) advisory rule
`core-vs-apps-routing.md` which guides Cursor Agent at author time. The rule is the
soft guidance; this gate is the hard fence.

## References

- Plan: `.windsurf/plans/adg-three-bucket-unified-c4f8e2.md` (W3 P3.2 + W5 P5.4)
- Constitutional §22, §28, §31
- ADR-074 (Runtime Bucket as OTel View) — sibling ADG-derived gate pattern
- Live evidence: `docs/reports/adg/apps_spine_delegation_gate_report.json`
