# SLO — apps_shared (Shared Infrastructure Layer)

> **Status:** TARGETS, not yet measured. Wave 4.3 (cost/latency telemetry rollup) closes the loop.
> **Owner:** see `CODEOWNERS`
> **Last reviewed:** 2026-04-29

## Architecture Note

apps_shared is **not a domain app** — it is the L_SHARED infrastructure layer used by every other apps_*. Its SLOs are about **utility reliability and zero-blast-radius**: any apps_shared regression cascades to all 6+ consumers.

This SLO is paired with **W3 (apps_shared purity CI gate)** which mechanically enforces "apps_shared has no `apps_*/` imports."

## Service Level Objectives

| Utility class | p50 | p99 | Hard ceiling | Error budget |
|---|---:|---:|---:|---:|
| **Cache-key generation** (`cache_validator`) | 50µs | 500µs | 5ms | <0.01% / 30d |
| **Generic data validation** (`validation_validator`) | 100µs | 800µs | 5ms | <0.01% / 30d |
| **Type construction** (Pydantic base types) | 50µs | 200µs | 1ms | <0.01% / 30d |
| **Utility module import** (cold) | 10ms | 50ms | 200ms | n/a (one-time) |

## Reliability SLOs

| Dimension | Target |
|---|---|
| **Determinism — same input → same output** | 100% (gate, not target) |
| **Zero domain-app imports from apps_shared** | 100% (CI gate `check_apps_shared_purity.py`) |
| **No circular dependencies** with `apps_*/` | 100% (CI gate) |
| **Test pass rate** | 100% (current: 13/13) |

## Cost Ceiling

apps_shared is **purely deterministic** — no LLM calls, no external I/O at the utility layer. Cost ceiling is **$0/day for utilities themselves**. Cost is consumed by callers.

If a utility module begins making external calls (LLM, network, DB), it MUST be **moved out of apps_shared** into the appropriate `agentic_core/L*/` layer.

## Failure Modes (top-3 — see RUNBOOK.md for response)

1. **Non-deterministic cache key** (same input → different SHA-256) → halt all caching across all apps; this is a critical correctness failure. Investigate the input normalization.
2. **Validation framework leak** (validator allows invalid data through) → halt promotion of any change touching that validator; review across ALL apps_*  consumers.
3. **Domain-app import detected** (`apps_shared/foo.py` imports `apps_eval/...`) → CI gate fails; PR cannot merge until removed. The whole point of the layer is broken otherwise.

## Architectural Differentiation

apps_shared is the only in-portfolio component that:
- Is consumed by **all** other apps_*
- Has a **mechanical purity boundary** (W3 CI gate)
- Has **zero domain logic** (the SVP review states this; W3 enforces it)
- Has the **largest absolute size** (195 files, 2.9MB) but the **lowest test count** (13)

The 13:195 test:file ratio is a deliberate scoping choice — not all utilities need their own test, but **every behavior-change** to a tested utility needs a test added or updated.

## Out of Scope (for THIS layer's SLO)

- LLM inference (lives in `agentic_core/L3_orchestration/inference/`)
- Persistent state (lives in `agentic_core/L4_state/`)
- Routing / cognition (lives in `agentic_core/L0_routing/`, `L1_cognition/`)

## How These Numbers Were Derived

- µs-scale targets: pure-Python deterministic functions on small inputs — measured ad-hoc via `timeit` on the `cache_validator.compute_key()` function.
- 100% determinism: enforced by `tests/test_validators.py::test_cache_key_determinism`.
- Purity: enforced by W3 CI gate (this plan).

## Measurement Plan (W4.3)

- Coverage gate: `apps_shared` test coverage tracked separately; minimum 90% for utilities under `validators/`.
- W3 gate runs on every PR; failure blocks merge.
- Cold-import benchmark added to `tests/test_validators.py` to detect import-time regressions.
