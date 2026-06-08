---
slug: otel-provider-bootstrap-9082d0
plan_type: platform_core_change
status: Completed
supersedes: []
---

# OTEL Provider Bootstrap — make spans actually generate (opt-in, generic core)

## Context (SCQA)

- **Situation.** The repo ships a real OpenTelemetry SDK and span-emitting code at L2/L3/spine, plus a
  collector compose file and an `otel_mcp` reader.
- **Complication.** No recording `TracerProvider`+exporter is ever installed on the product run path,
  so every span is dropped. Empirically `artifacts/apps_rg/runs/` has 0 run dirs and 0 `*otel*`/`*span*`
  files. The "OTEL-shaped" data produced (`spine_span_emit_receipt.jsonl`, hand-materialized
  `runtime_adg/*.json`) is not real OTLP telemetry.
- **Question.** How do we make OTEL spans export end-to-end without adding default overhead or
  app-coupling in core?
- **Answer.** Add one generic, env-gated, fail-soft `TracerProvider` bootstrap in `agentic_core/tracing/`,
  invoke it once at the core spine chokepoint every app crosses, and add a defensive cache-reset so the
  L2 emitter cannot strand a no-op tracer. Default OFF; activated only by standard OTEL env vars.

### Root causes (directly observed)
1. Exporter attaches only when `enable_otlp_grpc/http=True` (default False); factory flips on only if
   `OTEL_TRACES_EXPORTER=otlp` — `apps_shared/utils/open_telemetry_tracing_adapter_util.py:300-301,341-392,1008-1027`.
2. L2 emitter caches the ProxyTracerProvider no-op tracer for the process —
   `agentic_core/L2_execution/observability/l2_otel_emitter.py:75-99`.
3. apps_rg spine OTEL dual-write gated off by default — `apps_rg/runtime/spine/spine_span_emit.py:94,110`.
4. No collector runs by default — `docker-compose.otel.yml`, `config/otel/collector-config.yaml`.
5. No startup bootstrap; only `scripts/proof/otel_bootstrap.py:95` (proof/cert) installs a provider.

> L7 `HowTrace`/evidence traces do not satisfy OTEL (post-hoc flat 10-stage governance ledger, no
> span tree, no ns timing, bespoke hash-bound schema, fail-closed, in-house verifiers only). Out of scope.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1 | New `provider_bootstrap.py` + unit test | ~6k | OTEL SDK importable (confirmed) | **Completed** | bootstrap installs recording provider when env set; clean no-op when unset; idempotent; never raises |
| W2 | P2 | L2 emitter `reset_l2_tracer_cache()` + regression test | ~4k | `_TRACER` globals as observed | **Completed** | proxy cached pre-bootstrap → recording after; no-op fallback intact |
| W3 | P3 | Wire seam at `integrated_single_action_spine_run.py:762` + contract test | ~5k | seam is shared chokepoint for all apps | **Completed** | spine installs recording provider when env set; proxy untouched when unset |
| W4 | P4 | E2E verification (in-memory; console+collector if Docker) | ~5k | Docker optional | **Completed** | 13 scoped tests green; in-memory exporter proof passes; spans non-empty |
| W5 | P5 | Migration + CoreAddition receipts; `/core-boundary-audit` | ~4k | receipt schema as in glob-lock rule | **Completed** | boundary_audit_passed; app_specific_literals_added: [] |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1 | Bootstrap module | `agentic_core/tracing/provider_bootstrap.py`, `tests/unit/agentic_core/tracing/test_provider_bootstrap.py` | once-per-process provider semantics; fail-soft | ~6k | **Completed** |
| P2 | Cache-reset hook | `agentic_core/L2_execution/observability/l2_otel_emitter.py`, new regression test | don't weaken existing no-op fallback | ~4k | **Completed** |
| P3 | Seam wire-up | `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py`, `tests/unit/agentic_core/runtime/entrypoints/test_spine_bootstraps_otel_provider.py` | call must precede first emit; never raise | ~5k | **Completed** |
| P4 | Verification | (read-only) tests + optional docker compose | Docker availability | ~5k | **Completed** |
| P5 | Governance | `artifacts/governance/migration_receipts/*.json` | CoreAddition gate | ~4k | **Completed** |

## Approach

### New module `agentic_core/tracing/provider_bootstrap.py`
`ensure_tracer_provider_from_env() -> str` — env-gated (no-op when `OTEL_TRACES_EXPORTER` unset),
idempotent double-guard (`_BOOTSTRAPPED` + `get_tracer_provider()` real-provider check, since
`set_tracer_provider` is once-per-process), env-driven exporter (`otlp` HTTP/gRPC per
`OTEL_EXPORTER_OTLP_PROTOCOL`/`_ENDPOINT`, plus a `console` branch), `BatchSpanProcessor`, generic
`service.name` default (`agentic_core` — no app literal), whole body fail-soft `try/except`. Mirrors the
proven construction in `scripts/proof/otel_bootstrap.py:41-97` and
`open_telemetry_tracing_adapter_util.py:326-392` but as a lightweight, default-OFF, core-resident fn.

### Seam `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py`
First executable statement of `run_integrated_single_action_spine` (line 762, after docstring close at
761): import + call `ensure_tracer_provider_from_env()`. Shared chokepoint for apps_rg full run
(`run_whole_run_with_route_governance`), section lanes (`run_canonical_apps_rg_from_cli_primitives`),
and the `apps_rg/runtime/orchestration/integrated_spine_runner.py` shim. Runs before first L2 emit (~:852).

### Cache-reset `agentic_core/L2_execution/observability/l2_otel_emitter.py`
Add `reset_l2_tracer_cache()` (clears `_TRACER`/`_OTEL_AVAILABLE` under `_TRACER_LOCK`); bootstrap calls
it best-effort post-install. Keep the existing lazy-resolve no-op fallback (constitutional fail-soft).
L3 sink (`otel_sdk_sink.py:137-163`) builds fresh per call → ordering alone fixes it, no edit.

## Definition of Done

| # | DoD item | Verify / Defer |
|---|---|---|
| 1 | `ensure_tracer_provider_from_env()` installs a recording SDK provider when `OTEL_TRACES_EXPORTER` set | Verify: `test_provider_bootstrap.py` |
| 2 | Clean no-op + byte-identical behavior when env unset (default OFF) | Verify: `test_bootstrap_noop_when_env_unset` |
| 3 | Idempotent + never raises (SDK-missing → sentinel) | Verify: idempotency + never-raise tests |
| 4 | L2 emitter resolves a recording tracer after bootstrap (no stranded no-op) | Verify: `test_l2_emitter_resolves_after_bootstrap.py` |
| 5 | Core spine installs the provider once when env set; proxy untouched when unset | Verify: `test_spine_bootstraps_otel_provider.py` |
| 6 | Smoke run: `python -m apps_rg --section executive_summary ...` exits 0 with `OTEL_TRACES_EXPORTER=console` and emits span JSON | Verify (W4); Defer collector proof if Docker unavailable |
| 7 | Migration + CoreAddition receipts written; `/core-boundary-audit` passes, no app literals in core | Verify: W5 |

## Verification

1. `python -m pytest tests/unit/agentic_core/tracing/test_provider_bootstrap.py tests/unit/agentic_core/L2_execution/observability/ -v`
2. `python -m pytest tests/_apps_contract/test_spine_bootstraps_otel_provider.py -v`
3. Console proof: `$env:OTEL_TRACES_EXPORTER="console"; python -m apps_rg --section executive_summary ...` → span JSON on stdout.
4. Collector proof (opt-in, Docker): `docker compose -f docker-compose.otel.yml up -d`; export OTLP env; run; assert `artifacts/otel_collector_export/spans.json` non-empty; `down`.
5. Runtime-ADG ingest: feed a captured span through `agentic_core/L6_observability/runtime_trace/otel_runtime_ingest.py:emit_span_to_runtime_adg`; assert snapshot count +1.

## Notes
- T3 cross-layer change in `agentic_core/` → CoreAddition receipt + boundary audit required (W5).
- Work isolated in worktree `C:/Git/Otel_analysis` (branch `Otel_analysis`).
