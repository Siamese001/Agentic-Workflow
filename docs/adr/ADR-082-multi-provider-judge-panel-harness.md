# ADR-082: Multi-Provider Judge Panel Harness in agentic_core

**Status:** Accepted (W0)  
**Date:** 2026-05-24  
**Plan:** `core-judge-panel-harness-f3c8d1`

## Context

`apps_rg` runs proof panels (Gemini, OpenAI, Claude) via `run_llm_judges` and hand-rolled `_call_*` adapters. Core provides `LLMJudgeGateway` (single profile) and reasoning transport receipts, but no panel fan-out harness. Provider transport drift produced inconsistent effective rules on identical packets (Brown & Brown RCA).

## Decision

Add `agentic_core/runtime/judges/panel/`:

- `CanonicalJudgeContract` + stable `contract_hash`
- `JudgePanelRunner` — one user prompt / hash, N adapters
- `JudgeProviderAdapter` protocol + `PanelAdapterRegistry`
- `audit_transport_parity` — declared vs observed transport
- `normalize_panel_score` — provider-neutral pass math
- `reconcile_against_gate_closures` — algorithm in core, map in app

Apps supply rubric text, X2 gate summaries, and gate-closure maps. Core does not import `apps_rg`.

## Consequences

- **Positive:** Prevents three-provider rule drift; reusable by future `apps_*` panels.
- **Negative:** Dual stack with `LLMJudgeGateway` until unified profile refs exist.
- **Migration:** `apps_rg` W2 wires adapters; transport-parity remediation must be green first.

## Non-goals

- Replacing Exit-eval L3 judges
- Owning apps_rg rubric or X2 validator implementations
