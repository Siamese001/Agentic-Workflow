---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-gates-per-layer-ctx-builders-a3c7d9.md'
original_relative_path: 'runtime-gates-per-layer-ctx-builders-a3c7d9.md'
source_sha256: aac37057512a0a8f20e7e4e3148628d02cc26b0b457298d3df486686b657e829
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
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
