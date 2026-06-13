# Runtime Gates — Dispatch Wiring

Status: In Progress
Owner: Cascade
Plan ID: runtime-gates-dispatch-wiring-c4e9a2

## Goal

Provide a thin per-layer dispatcher API that production code (L0/L1/L2/L3/L5) can call to invoke the relevant subset of runtime gates without each layer re-implementing dispatch.

## Approach

`runtime_gates.dispatch.run_layer(layer: str, ctx: GateContext) -> list[GateDecision]` — invokes all gates whose `PRIMARY_LAYER` matches and short-circuits on stop conditions. Layer constants exposed as module attributes.

## Wave Structure

| Wave | Phase IDs | Focus | Est Tokens | Status |
|---|---|---|---|---|
| W1 | 1.1 | dispatch.py module | 5000 | Done |
| W2 | 2.1 | Tests | 4000 | Done |
| W3 | 3.1 | Final validation + commit + push | 6000 | Done |

## Phase-Level Summary

| Phase | Title | Scope | Pain | Est | Status |
|---|---|---|---|---|---|
| 1.1 | run_layer + LAYER_GATES map | runtime_gates/dispatch.py | layer→gate mapping | 5000 | Done |
| 2.1 | Tests | tests/.../test_dispatch.py | per-layer dispatch | 4000 | Done |
| 3.1 | Validate + commit | git | none | 6000 | Done |

## Out of Scope

- Actual production call sites (Composition Root edits) — that's deeper integration with broader blast radius. This wave provides the API only.
