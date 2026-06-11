---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-gates-composition-root-wiring-e9b4c2.md'
original_relative_path: 'runtime-gates-composition-root-wiring-e9b4c2.md'
source_sha256: dd938672eb3b4a09ba45622b7361652f4194e04a2fd8a1965dd2c46037f9c7e2
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Gates — Composition Root Wiring

Status: In Progress
Plan ID: runtime-gates-composition-root-wiring-e9b4c2

## Goal

Provide a thin, low-blast-radius enforcement API so production code at any
layer (L0/L1/L2/L3/L5) can invoke the runtime-gate dispatch without each
layer re-implementing it. Bridges `runtime_gates.dispatch.run_layer` to
production call sites via a stable wrapper, decorator, and rollout switch.

## Approach

Single new module `runtime_gates/enforcement.py`:

- `enforce_layer(layer, ctx, *, mode='strict'|'soft'|'audit'|'off')` —
  wraps `run_layer` with explicit halt semantics, OTel-friendly logging,
  and an environment-variable rollout switch.
- `@enforces_layer(layer)` — decorator for layer-entry functions that
  builds a `GateContext` from `kwargs['ctx']` (or a builder callable) and
  raises `RuntimeGateHaltError` on stop conditions.
- `RuntimeGateHaltError` — typed exception carrying the halting `MeshResult`.
- Environment switches:
  - `RUNTIME_GATES_ENFORCEMENT_MODE` (default `audit`)
  - `RUNTIME_GATES_DISABLED_LAYERS` (CSV)

## Wave Structure

| Wave | Phase | Focus | Status |
|---|---|---|---|
| W1 | 1.1 | enforcement.py module | Done |
| W2 | 2.1 | Tests | Done |
| W3 | 3.1 | Commit + push | Done |

## Phase-Level Summary

| Phase | Title | Scope | Pain | Est | Status |
|---|---|---|---|---|---|
| 1.1 | enforcement.py | runtime_gates/enforcement.py | mode semantics | 6000 | Done |
| 2.1 | Tests | tests/.../test_enforcement.py | strict/soft/audit/off + decorator | 4000 | Done |
| 3.1 | Land | git | none | 1000 | Done |

## Out of Scope

- Editing every layer's actual production code — that requires per-layer
  context-builder implementations and is held out for follow-up plans.
  This wave provides the API and the rollout switch only.
