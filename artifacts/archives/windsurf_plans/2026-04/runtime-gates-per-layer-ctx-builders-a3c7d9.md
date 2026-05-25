# Runtime Gates — Per-Layer GateContext Builders

Plan ID: runtime-gates-per-layer-ctx-builders-a3c7d9

## Goal

Standardize `GateContext` construction so each layer call site reuses one builder
instead of reimplementing context shaping.

## Scope

`agentic_core/L5_safety/runtime_gates/ctx_builders.py`:

- `build_u0_ctx(request, identity)` — request-ingress context
- `build_l0_ctx(intent, route_contract, hitl)` — routing context
- `build_l2_ctx(tool_call, sandbox, capability)` — tool/exec context
- `build_l3_ctx(workflow_state, retry_state)` — orchestration context
- `build_exit_ctx(output, evidence, trace_artifacts)` — exit-eval context
- `merge_ctx(*ctxs)` — combine partial contexts
- All builders return a `GateContext` populated with the fields the relevant
  G-gates read.

Tests verify each builder produces a context that runs the corresponding
`run_layer` to completion (no false halts).
