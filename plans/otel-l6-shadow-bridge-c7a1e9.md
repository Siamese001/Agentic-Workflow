---
plan_id: otel-l6-shadow-bridge-c7a1e9
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "artifacts/governance/migration_receipts/2026-06-14_otel-l6-shadow-bridge.json"
dod_exempt: false
supersedes: []
---

# OTEL → L6 Shadow Observability Bridge (retrospective)

Generate runtime OTEL/span evidence, seal it into runtime exhaust, and make it consumable by L6 shadow evaluation — implemented as generic, app-agnostic `agentic_core` infrastructure.

> Retrospective record. Work was executed from a user-supplied plan in one session, committed as
> `b388d9c` and opened as draft PR #364. This file is the durable disk SSOT record (the repo is
> disk-only; Notion plan registration is retired — constitutional §36). It also captures the two RCAs
> and the mid-flight test fix encountered during execution.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W6
LAST_COMPLETED_WAVE: W6
LAST_UPDATED: 2026-06-14

---

## Context (SCQA)

- **Situation** — Runtime tracing pieces existed (`provider_bootstrap`, `l2_otel_emitter`, the exit-eval `otel_sdk_sink`, the `runtime_span_emitter` dict-span records) and L6 shadow_eval ingest existed, but they were not connected.
- **Complication** — Traces were never automatically harvested into `RuntimeExhaustBundle` evidence nor consumed by L6 shadow evaluation; `EvaluationPipeline` silently defaulted to `NoOpSpanSink`; L6 was driven only by proof scripts/tests.
- **Question** — How do we generate trace evidence, seal it into runtime exhaust, and make it usable by L6 shadow observability without breaking process-map law (L6 read-only, post-boundary, no L4 write) or requiring an external OTLP collector?
- **Answer** — Add the smallest safe end-to-end path: a central env-gated tracing bootstrap seam → a traced Exit-eval factory → a pure runtime-span→L6 `raw_exhaust` adapter → an X1H observable-trace validator → a read-only post-boundary L6 runner, with deterministic local span records as the L6 source.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Preflight inventory + characterization tests | ~12k | Code facts match the supplied plan | ✅ DONE | Real callsites mapped; 5 regression files added demonstrating the gap |
| W2 | W2.1 | Central env-gated tracing bootstrap seam | ~6k | `provider_bootstrap` is fail-soft | ✅ DONE | `bootstrap_runtime_tracing()` returns structured status; never raises |
| W3 | W3.1 | Traced Exit-eval factory + lazy export | ~7k | `EvaluationPipeline` accepts `span_sink` | ✅ DONE | Factory injects `build_span_sink()`; direct ctor stays no-op |
| W4 | W4.1, W4.2 | Runtime-span → L6 `raw_exhaust` adapter + X1H validator | ~14k | L6 ingest event/source shape stable | ✅ DONE | Linked, stage-mapped events; L6 ingest consumes; PASS/PARTIAL/FAIL validator |
| W5 | W5.1, W5.2 | Read-only post-boundary L6 runner + spine bootstrap wiring | ~8k | L6 observer law (no L4 write) | ✅ DONE | 6A+observer over sealed exhaust only; spine uses the seam; no L4 write/promotion |
| W6 | W6.1, W6.2 | Test-fix (spine pollution RCA) + validation + receipt | ~9k | OTEL SDK installed in env | ✅ DONE | 18 tests green; 0 new regressions vs baseline; boundary receipt written |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Preflight inventory (read-only) | ✅ DONE |
| W1.2 | Characterization tests (5 files) | ✅ DONE |
| W2.1 | `runtime_tracing.bootstrap_runtime_tracing` seam | ✅ DONE |
| W3.1 | `build_evaluation_pipeline_with_tracing` + lazy export | ✅ DONE |
| W4.1 | `shadow_raw_exhaust_adapter.build_l6_shadow_raw_exhaust` | ✅ DONE |
| W4.2 | `observable_trace_check` (X1H) | ✅ DONE |
| W5.1 | `post_boundary_runner.run_l6_shadow_from_sealed_exhaust` | ✅ DONE |
| W5.2 | Spine bootstrap wiring (`integrated_single_action_spine_run`) | ✅ DONE |
| W6.1 | Test-fix: late binding (frozen-spy pollution RCA) | ✅ DONE |
| W6.2 | Validation + boundary/Core-Addition receipt | ✅ DONE |

---

## Out Of Scope

- Wiring an orchestrated runtime entrypoint that actually emits `_completed_spans` into the post-Exit handoff (R4 deterministic spine emits none). The pure bridge + runner + tests are in place; live harvest is the remaining integration step.
- Repairing the two pre-existing/broken CI gates (`guardian-contract-gate` missing-file, `ADG Delta` generator crash) — repo-wide, unrelated to this diff; left untouched per user decision.
- The v6 `ExitEvalPipeline` Exit plane (the factory targets the X1A–X1G `EvaluationPipeline` plane).

---

## Wave 1 — Preflight + characterization tests

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — read-only inventory + new test files only.

**Phases**:
- **W1.1** — Preflight inventory (read-only) | ~6k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Characterization tests (5 files) | ~6k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Real Exit/runtime callsites and the L6 ingest contract verified against the supplied plan.
- Five regression files added; the gap (no-op sink, no bridge, readiness honesty) demonstrated.

---

## Wave 2 — Central tracing bootstrap seam

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — `runtime_tracing.bootstrap_runtime_tracing` | ~6k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Env-gated, fail-soft, returns `RuntimeTracingStatus`; local capture always on; external OTLP default-OFF.

---

## Wave 3 — Traced Exit-eval factory

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — `build_evaluation_pipeline_with_tracing` + lazy `__init__` export | ~7k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Factory bootstraps tracing then injects `build_span_sink()`; bare `EvaluationPipeline` still defaults to `NoOpSpanSink`.

---

## Wave 4 — Runtime-span → L6 bridge + X1H validator

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — `shadow_raw_exhaust_adapter.build_l6_shadow_raw_exhaust` | ~8k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** — `observable_trace_check` (X1H) | ~6k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Adapter is pure (no fs/OTEL/L4); produces linked, stage-mapped events L6 ingest consumes into normalized evidence.
- Validator returns PASS/PARTIAL/FAIL and never raises.

---

## Wave 5 — Post-boundary L6 runner + spine wiring

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — `post_boundary_runner.run_l6_shadow_from_sealed_exhaust` | ~4k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.2** — Spine bootstrap wiring | ~4k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- 6A ingest + observer run over sealed exhaust only; 6B only when scorable + baseline supplied; no L4 write, no promotion.
- Spine bootstraps tracing through the new seam.

---

## Wave 6 — Test-fix, validation, receipt

WAVE_ID: W6
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Phases**:
- **W6.1** — Test-fix: late binding (frozen-spy pollution RCA) | ~5k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W6.2** — Validation + boundary/Core-Addition receipt | ~4k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- 18 tests green; baseline comparison shows 0 new failures (same 120 pre-existing v6 failures with/without).
- `GENERIC_INFRASTRUCTURE` boundary receipt recorded.

---

## Execution Details

### W2.1 — runtime_tracing seam
**Scope**: `agentic_core/tracing/runtime_tracing.py` — `bootstrap_runtime_tracing()` / `RuntimeTracingStatus`. Resolves `provider_bootstrap` via the **module** (late binding) so a monkeypatched bootstrap is honored.

### W4.1 — shadow adapter
**Scope**: `agentic_core/runtime/exhaust/shadow_raw_exhaust_adapter.py` — `build_l6_shadow_raw_exhaust(...)`, `_span_to_event`/`_span_to_source_manifest` (comprehensions, no long for-loops → progress-bar gate clean). Empty `l5_certification_ref` → L6 ingest's sanctioned MISSING sentinel.

### W6 — Validation
**Commands**:
```bash
python -m pytest \
  tests/unit/agentic_core/tracing/test_runtime_tracing_bootstrap.py \
  tests/unit/agentic_core/runtime/exhaust/test_shadow_raw_exhaust_adapter.py \
  tests/unit/agentic_core/runtime/exhaust/test_observable_trace_check.py \
  tests/unit/agentic_core/L3_orchestration/exit_eval/test_span_sink_wiring_regression.py \
  tests/unit/agentic_core/L6_observability/shadow_eval/test_trace_readiness_regression.py -n0 -q
```

---

## Gap Register

**GAP-1: Live orchestrated harvest not yet wired (deferred)**
- The pure bridge + post-boundary runner + tests exist, but no orchestrated entrypoint feeds real `_completed_spans` into the post-Exit handoff. The R4 deterministic spine emits no orchestrator spans, so wiring an orchestrated producer is the remaining integration step.

**GAP-2 (RCA — test fix): spine bootstrap test pollution**
- *Symptom*: `test_spine_installs_recording_provider_when_env_set` failed (ProxyTracerProvider) after my change; passed in isolation, failed in batch.
- *Root cause* (DIRECTLY OBSERVED): `runtime_tracing.py` used a module-level `from provider_bootstrap import ensure_tracer_provider_from_env`. A sibling test monkeypatched that function to a spy; the spine's first call imported `runtime_tracing` at that moment, **freezing the spy** into its namespace — which then ran (and never installed a provider) in the next test.
- *Fix*: resolve through the `provider_bootstrap` module attribute at call time (late binding). Both spine bootstrap tests pass; 18/18 green.
- *Recurrence guard*: prefer late-binding (`module.attr()`) over `from module import attr` for anything tests may monkeypatch.

**GAP-3 (RCA — operational): local ADG repro runaway (~1.5 h)**
- *Symptom*: a `generate_full_adg.py` build ran ~1.5 h after my `timeout 200`-bounded background repro reported `Terminated`/`EXIT=124`.
- *Root cause* (DIRECTLY OBSERVED): `run_full_adg_audit.py:236` spawns the generator via `subprocess.run`; `timeout 200` SIGTERM'd only the direct child (wrapper), orphaning the grandchild to PID 1, which kept building until container reclaim (`uptime` = up 12 min). `subprocess.run`'s `timeout=` only kills its child on its *own* TimeoutExpired, not when its parent is SIGTERM'd externally.
- *Recurrence guard*: don't run heavy ADG builds locally for attribution (the syntax gate + scoped tests + the parallel Consolidated contract gates already answered it); if a heavy subprocess must be bounded, kill the **process group** (`timeout -k -s TERM … setsid <cmd>`) — constitutional §11.

---

## Definition of Done

DoD-1: End-to-end bridge exists — runtime span records → sealed `raw_exhaust` → L6 normalized evidence + honest readiness, with no live OTEL backend.
- Evidence: `test_shadow_raw_exhaust_adapter.py` + `test_trace_readiness_regression.py` (adapter feeds real `shadow_eval.ingest`).
- Status: DONE

DoD-2: Smoke run of the new surface passes.
- Evidence: `python -m pytest <5 regression files> -n0 -q` exits 0 (16 passed); CI `runtime-spine-smoke` green (exercises the spine bootstrap edit).
- Status: DONE

DoD-3: Test count + zero regressions.
- Evidence: 18 tests pass; baseline diff = same 120 pre-existing v6 failures with and without this diff (+8 new passing, 0 new failures).
- Status: DONE

DoD-4: CI validating gates green.
- Evidence: `Consolidated contract gates` ✅, `GitGuardian` ✅, `runtime-spine-smoke` ✅ on PR #364.
- Status: DONE

DoD-5: Boundary / Core-Addition receipt recorded (no app leakage).
- Evidence: `artifacts/governance/migration_receipts/2026-06-14_otel-l6-shadow-bridge.json` (classification `GENERIC_INFRASTRUCTURE`; grep confirms zero app literals).
- Status: DONE

DoD-6: Process-map law preserved.
- Evidence: post_boundary_runner imports no OTEL/L4/UWG-write; adapter+validator pure; external OTLP env-gated/default-OFF.
- Status: DONE

### Verification vs Deferral

| Item | Verified | Deferred |
|---|---|---|
| Runtime-span → L6 `raw_exhaust` bridge | ✅ unit + real L6 ingest | — |
| Eval-readiness honesty (evidence present/absent) | ✅ | — |
| Factory injects live span sink (not silent no-op) | ✅ | — |
| Spine bootstraps via the seam | ✅ (runtime-spine-smoke) | — |
| Live orchestrated `_completed_spans` harvest at Exit 5.7 | — | ⏳ needs an orchestrated producer (GAP-1) |
| guardian-contract-gate / ADG Delta gates | n/a — pre-existing repo-wide breakage | left out of scope per user |

---

## Scope Expansion Authorization

No in-flight scope expansion. The single deferral (GAP-1, live harvest) was surfaced in the PR body and this register, not silently absorbed.

> **Documentation ≠ Authorization.** This retrospective record does not retroactively authorize anything; it records what was built, verified, and deferred.

---

## Supersedes

| Predecessor slug | Reason |
|---|---|

_None — net-new plan._

---

## Marker Quick Reference

```
WAVE_COMPLETE: plan=otel-l6-shadow-bridge-c7a1e9 wave=6 note="+18 tests, 7 files, scope=otel-l6-bridge"
PLAN_COMPLETE: plan=otel-l6-shadow-bridge-c7a1e9 note="bridge + factory + adapter + validator + runner shipped; live harvest deferred (GAP-1)"
```
