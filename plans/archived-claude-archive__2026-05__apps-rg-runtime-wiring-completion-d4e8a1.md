---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-runtime-wiring-completion-d4e8a1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-runtime-wiring-completion-d4e8a1.md'
source_sha256: 5554c6fc180d1b1bc70fc30c9f1e720569caeba06ad79ff737322820b9086631
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: apps_rg Runtime Wiring Completion + W0–W9 RCA

**Slug:** `apps-rg-runtime-wiring-completion-d4e8a1`
**Status:** Not Started
**Tier:** T3 — cross-layer, multi-file, architectural, governance
**Created:** 2026-05-09
**Re-opens:** `apps-rg-declarative-ingress-only-spinal-governance-c8b3e1` (was marked W9 COMPLETE 2026-05-09; this plan establishes that close-out was premature and lands the missing wiring)
**Constitutional anchors:** §6 (Author-Gate), §22 (graph-layer evidence), §32 (Fort Knox / DoD discipline), §35 (queue drain), §36 (plan registration)

---

## §1. Executive Summary

Plan `c8b3e1` declared 9 waves complete (W0–W9) on 2026-05-09. Empirical verification on the same day shows **`python -m apps_rg` does not run end-to-end through any documented entrypoint**. This plan:

1. Performs a forensic RCA on why W0–W9 closed without a working runtime
2. Lands the W5/W6/W7 wiring that was claimed-but-not-shipped
3. Adds Definition-of-Done discipline so no future apps_* refactor plan can close on absence-tests alone

---

## §2. Root Cause Analysis — Why W0–W9 Did Not Finish

### §2.1 Empirical evidence (2026-05-09 run)

```
$ python -m apps_rg --target-company "Brown & Brown" --target-role "..." \
    --source-resume "..." --jd "..." --manual-brief "..."

✅ apps_rg package import           (only after ad-hoc removal of __init__.py:bootstrap_runtime import)
✅ CLI argparse
✅ Wizard skip (all flags provided)
✅ Ingress payload dict construction (line 192)
❌ AppIngressRunner()  line 241
   TypeError: AppIngressRunner.__init__() missing 3 required keyword-only
   arguments: 'dispatch', 'parse', and 'required_fields'
```

Subsequent inspection identified **6 distinct defects** declared resolved by W5/W6 but actually unresolved:

| # | Defect | Where | Discovered |
|---|---|---|---|
| D1 | `apps_rg/__init__.py` imports `bootstrap_runtime.install_runtime_shims` from a quarantined module | `apps_rg/__init__.py:3` | This session |
| D2 | `apps_rg/__main__.py` imports `RequestEnvelope` — symbol does not exist in payload module | `apps_rg/__main__.py:24-27` (pre-fix) | This session |
| D3 | `apps_rg/__main__.py` references `args.research_via` — argparse never defines `--research-via` | `apps_rg/__main__.py:216` (pre-fix) | This session |
| D4 | `apps_rg/__main__.py` instantiates `AppIngressRunner()` with no kwargs — class requires `dispatch=`/`parse=`/`required_fields=` | `apps_rg/__main__.py:241` | This session |
| D5 | `apps_rg/__main__.py` calls `runner.run(payload_dict)` — class exposes `handle_chat()`/`handle_http()` only | `apps_rg/__main__.py:233` | This session |
| D6 | Wizard crashes with `EOFError` traceback in non-TTY contexts (e.g. all Cursor Agent runs) | `apps_rg/__main__.py:_interactive_wizard` (pre-fix) | This session |

D1, D2, D3, D6 were patched ad-hoc this session. D4 and D5 are the architectural gaps — the W6/W7 work that was never landed.

### §2.2 Why W5 was marked complete despite D2/D3/D4/D5

W5 acceptance criteria (per c8b3e1 plan §13 line 723–728) was:
> "✅ W5 COMPLETE — Ingress-only architecture, 15/15 bypass tests passing:
> - AG-RGGOV-1: `apps_rg/__main__.py` rewritten as pure ingress shim
> - AppsRgIngressPayload + RequestEnvelope dataclasses (immutable, frozen)
> - CLI argument parsing + interactive wizard input collection
> - AppIngressRunner delegation (fail-closed if runner unavailable)
> - 15 W5 ingress-only tests (no planner/router/orchestrator/prompt/executor/provider)"

The 15 bypass tests are **negative-pattern tests** — they assert *forbidden-pattern absence* (no planner imports, no router imports, no provider calls). They prove governance compliance. **They do not prove capability.** A file that does nothing also passes all 15.

The W5 acceptance criteria did not include:
- An `import apps_rg` smoke test
- An `python -m apps_rg --help` smoke test
- A `python -m apps_rg --dry-run` smoke test
- Any end-to-end resume-generation smoke test

This is **test theater** — passing tests gave false confidence. The plan was closed without the most basic capability check.

### §2.3 Why W6/W7/W8 were marked complete despite D4/D5

c8b3e1 plan status table (line 743–748) shows:

| ID | Chosen Option | W3 | W4 | W5 | W6 | W7 | W8 |
|----|---|----|----|----|----|----|----|
| AG-RGGOV-1 | Extend `AppIngressRunner` | — | — | ✅ | ✅ | — | — |

The W6 work was supposed to (per plan §13 line 495):
> "W6.1 — U0 ingress validator | `agentic_core/runtime/entry/` or U0 module | Reject forbidden authority fields | ~1 k"

What actually exists in the repo:
- `agentic_core/runtime/entry/app_ingress_runner.py` — **generic** wrapper requiring `dispatch=`/`parse=`/`required_fields=`. NOT extended for apps_rg.
- No `agentic_core/runtime/entry/apps_rg_dispatch.py` exists.
- No `apps_rg`-specific U0 binding exists.
- No `.run(AppsRgIngressPayload)` method exists on AppIngressRunner.
- No L1 binding emitting `L1PlanContract` from `AppsRgProfileManifest.planning_profile_ref`.
- No L0 binding emitting `RouteContract` for `resume_generation` task class.

The W6 checkmark was applied without the corresponding code shipping.

### §2.4 Why W4 quarantine left orphan code

W4 quarantined ALL `apps_rg/` runtime authority (correct per AG-RGGOV-8) but the replacement core wiring was promised to W5/W6/W7 and never landed. Result: `apps_rg/` is in an **orphan state** — old runtime is dead-on-import, new runtime doesn't exist. The bootstrap chain `apps_rg/__init__.py → bootstrap_runtime → install_runtime_shims()` was left in place pointing at a quarantined target — verifying *nothing imports apps_rg* would have caught this in 1 line of test:

```python
def test_apps_rg_imports():
    import apps_rg  # would have failed loud on 2026-05-09
```

That test was not written.

### §2.5 Why the AG-WIRE / AG-FRESH gates didn't catch this

Existing CI gates check Author-Gate hook wiring and packet shape (per memories `f220bb61`, `6e7e9afe`). They are governance gates, not capability gates. They cannot detect "the runtime cannot be imported".

There is no CI gate that asserts:
- Every `apps_*` package has an importable `__init__.py`
- Every `apps_*` package has a runnable `python -m apps_<x> --dry-run`
- Every `apps_*` package has a `runner-instantiable` smoke test

This plan adds those.

### §2.6 Lessons learned (for plan §6 Definition-of-Done discipline)

| # | Lesson | Mechanism in this plan |
|---|---|---|
| L1 | Negative-pattern tests are necessary but insufficient for completeness | W5 introduces capability smoke tests as DoD |
| L2 | Quarantine without replacement = orphan code; both must land in the same wave | W2/W3 land replacement before any new quarantine |
| L3 | Plan close-out must include an end-to-end "smoke proof" — at minimum `import x` and `python -m x --dry-run` | W5 establishes; W6 codifies as universal apps_* DoD |
| L4 | "Tests passing" alone is insufficient evidence — must publish what tests cover | W6 introduces test-coverage taxonomy in DoD |
| L5 | Plan §18 deferred-scope must list every known gap; absence implies "complete and verified" | W6 introduces verification-vs-deferral distinction in plan template |

---

## §3. Objective

1. Land the W5/W6/W7 wiring claimed by `c8b3e1` so `python -m apps_rg` produces a real resume artifact end-to-end.
2. Codify Definition-of-Done discipline preventing this class of premature plan closure for any future apps_* refactor.

---

## §4. Non-Goals

- Re-quarantine or de-quarantine any file outside `apps_rg/__init__.py` (already minimally repaired this session)
- Modify the AG-RGGOV-8 quarantine boundary
- Add real Gemini SDK wiring (deferred per `c8b3e1` §18)
- Implement L3 `MANAGED_WORKFLOW` (deferred per `c8b3e1` §18)
- Wire `apps_rg` profile UWG promotion to L4 (deferred per `c8b3e1` §18)
- Replicate this pattern to sibling apps (`apps_lic`, `apps_qna`, etc.) — each is its own plan
- Modify the `AppsRgIngressPayload` schema
- Touch the existing 15 bypass tests (governance-correct as-is)

---

## §5. Files In Scope

### Core runtime (NEW)

| Path | Role |
|---|---|
| `agentic_core/runtime/entry/apps_rg_dispatch.py` | NEW — apps_rg-specific `dispatch`/`parse`/`required_fields` callables |
| `agentic_core/runtime/entry/u0_apps_rg_binding.py` | NEW — U0 ingress validator binding for `resume_generation` task class |
| `agentic_core/L1_cognition/apps_rg_l1_binding.py` | NEW — emits `L1PlanContract` from `AppsRgProfileManifest.planning_profile_ref` |
| `agentic_core/L0_routing/apps_rg_l0_binding.py` | NEW — emits `RouteContract` for `resume_generation` task class |
| `agentic_core/L2_execution/apps_rg_l2_binding.py` | NEW — `SealedL2Artifact` execution for `resume_generation` |
| `agentic_core/runtime/exit/apps_rg_exit_binding.py` | NEW — `X3Disposition` emission for `resume_generation` |

### Core runtime (EDIT)

| Path | Role |
|---|---|
| `agentic_core/runtime/entry/app_ingress_runner.py` | Add `.run(AppsRgIngressPayload) -> ExitDisposition` method |
| `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` | Add `RequestEnvelope` dataclass (referenced by `__main__.py` original code; was the missing import) |

### apps_rg (EDIT)

| Path | Role |
|---|---|
| `apps_rg/__main__.py` | Wire to new `AppIngressRunner.run()` API; remove `args.research_via` reference (already done this session); `EOFError` handling (already done this session) |
| `apps_rg/__init__.py` | Already repaired this session — no further edit |

### Tests (NEW)

| Path | Role |
|---|---|
| `tests/_apps_contract/test_apps_rg_smoke_capability.py` | Capability smoke tests — assertions opposite to bypass tests |
| `tests/_apps_contract/test_apps_rg_dry_run.py` | `python -m apps_rg --dry-run` produces valid payload JSON |
| `tests/_apps_contract/test_apps_rg_e2e_resume_generation.py` | End-to-end: produces a runnable resume artifact under `artifacts/apps_rg/runs/<ts>/` |
| `tests/_apps_contract/test_apps_rg_runner_instantiable.py` | `AppIngressRunner` instantiates with apps_rg dispatch + parse + required_fields |
| `tests/unit/agentic_core/runtime/entry/test_app_ingress_runner_run_method.py` | Unit tests for `.run()` method |
| `tests/unit/agentic_core/runtime/entry/test_apps_rg_dispatch.py` | Unit tests for dispatch/parse/required_fields |

### CI gates (NEW)

| Path | Role |
|---|---|
| `ops_scripts/ci/check_apps_package_importable.py` | NEW gate — asserts every `apps_*/__init__.py` imports cleanly |
| `ops_scripts/ci/check_apps_dry_run_works.py` | NEW gate — asserts every `apps_*` with a `__main__.py` supports `--dry-run` |
| `ops_scripts/ci/check_plan_completion_dod.py` | NEW gate — asserts every plan marked Completed has `## Definition of Done` section with smoke-test evidence |
| `ops_scripts/ci/run_contract_gates.py` | EDIT — register `APPS-IMPORT`, `APPS-DRYRUN`, `PLAN-DOD` advisory gates |

### Templates / discipline (EDIT)

| Path | Role |
|---|---|
| `.cursor/templates/execution-plan-template.md` | Add `## Definition of Done` mandatory section with smoke-test row |
| `.cursor/rules/plan-location.md` | Update DoD requirements |

**Total:** 12 new files · 6 edits · 1 already-fixed file

---

## §6. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1, P1.2 | RCA writeup + lessons-learned doc + audit existing 15 bypass tests | ~6k | RCA evidence already collected this session; lessons-learned format mirrors `docs/architecture/adr/` | Not Started | RCA doc at `docs/reports/runtime_cert/apps_rg_w0_w9_rca.md`; audit table classifying each of 15 bypass tests as governance vs capability |
| W2 | P2.1, P2.2, P2.3 | Extend AppIngressRunner with `.run()` method + apps_rg dispatch/parse callables | ~10k | Existing `AppIngressRunner.handle_chat`/`handle_http` patterns generalize to `.run(AppsRgIngressPayload)`; `RequestEnvelope` dataclass needs to be added to payload module | Not Started | `AppIngressRunner.run(payload)` returns `ExitDisposition`; `apps_rg_dispatch.py` exports the 3 callables; runner instantiable smoke test green |
| W3 | P3.1, P3.2, P3.3, P3.4, P3.5 | Wire U0 → L1 → L0 → [C0] → [PA] → L2 → Exit for `resume_generation` task class | ~25k | Each layer already exists in agentic_core; binding layer is thin glue; existing AppsRgProfileManifest provides the declarative refs | Not Started | All 6 layer bindings exist; integration test exercises full pipeline; OTEL span chain U0→L1→L0→[C0]→[PA]→L2→Exit captured |
| W4 | P4.1, P4.2 | Update apps_rg/__main__.py to call new API; restore `RequestEnvelope` import; verify dry-run path | ~3k | All `__main__.py` patches from this session preserved; new `.run()` method consumed correctly | Not Started | `python -m apps_rg --dry-run` exits 0 with valid payload JSON; happy-path run reaches Exit |
| W5 | P5.1, P5.2, P5.3 | End-to-end smoke test — actually generate a Brown & Brown resume; produce real artifact | ~8k | All test inputs available (master_resume.json, JD JSON, manual-brief PDF); LLM provider available (vLLM Qwen 32B per memory `01483ea2`) | Not Started | `artifacts/apps_rg/runs/<ts>/generated_resume.json` produced; non-empty; matches AppsRgProfileManifest.output_schema; smoke test green in CI |
| W6 | P6.1, P6.2, P6.3 | Definition-of-Done discipline — plan template + 3 new CI gates + retrofit plan-location rule | ~7k | Template addition is non-breaking for existing plans; CI gates are advisory by default | Not Started | Template `## Definition of Done` section landed; 3 CI gates registered; rule updated; existing plans pass advisory gate |

**Total estimate:** ~59k tokens · 6 waves · 17 phases.

---

## §7. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | RCA forensic writeup | `docs/reports/runtime_cert/apps_rg_w0_w9_rca.md` | Must be specific about what was claimed vs what shipped; cite line numbers; preserve plan §2 evidence verbatim | ~3k | Not Started |
| P1.2 | Audit 15 bypass tests | `docs/reports/runtime_cert/apps_rg_bypass_tests_audit.md` | Classify each as governance (negative-pattern) vs capability (positive-assertion); identify the 0 capability tests at W5 close-out | ~3k | Not Started |
| P2.1 | Add `RequestEnvelope` dataclass to payload module | `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` | Frozen dataclass; canonical request envelope shape; matches §13 line 717 reference "L5 canonical retained" | ~2k | Not Started |
| P2.2 | Extend `AppIngressRunner` with `.run()` method | `agentic_core/runtime/entry/app_ingress_runner.py` | Generic interface; accepts AppsRgIngressPayload (or any subclass); returns ExitDisposition; preserves handle_chat/handle_http back-compat | ~4k | Not Started |
| P2.3 | apps_rg-specific dispatch/parse/required_fields | `agentic_core/runtime/entry/apps_rg_dispatch.py` | Pure functions; no provider calls; no LLM logic; thin glue from payload → domain request → exit disposition | ~4k | Not Started |
| P3.1 | U0 binding — `resume_generation` task class | `agentic_core/runtime/entry/u0_apps_rg_binding.py` | Reject forbidden authority fields per c8b3e1 §4.2 (route_id, execution_form, provider, etc.); emit AuthorityValidationReceipt | ~5k | Not Started |
| P3.2 | L1 binding — emit L1PlanContract | `agentic_core/L1_cognition/apps_rg_l1_binding.py` | Deterministic — no LLM; reads `AppsRgProfileManifest.planning_profile_ref`; emits one `L1PlanContract` | ~5k | Not Started |
| P3.3 | L0 binding — emit RouteContract | `agentic_core/L0_routing/apps_rg_l0_binding.py` | Exactly one RouteContract; carries `execution_form` + grounding/model flags per c8b3e1 §13 line 497 | ~5k | Not Started |
| P3.4 | [C0] + [PA] conditional emit | `agentic_core/runtime/c0_retrieval/apps_rg_c0_binding.py`, `agentic_core/runtime/prompt_assembly/apps_rg_pa_binding.py` | Fire only when route flags say so; degrade gracefully when c0_retrieval_sources absent (forward-compat with FEC producer per memory `e24c888b`) | ~5k | Not Started |
| P3.5 | L2 + Exit binding | `agentic_core/L2_execution/apps_rg_l2_binding.py`, `agentic_core/runtime/exit/apps_rg_exit_binding.py` | L2 produces SealedL2Artifact; Exit emits X3Disposition; existing FEC producer hook landed for apps_rg per memory `e24c888b` | ~5k | Not Started |
| P4.1 | Update `apps_rg/__main__.py` | `apps_rg/__main__.py` | Restore `RequestEnvelope` import (now exists); call `runner.run(payload)`; preserve EOFError + research_via fixes from this session | ~2k | Not Started |
| P4.2 | Verify `--dry-run` smoke | (smoke run only) | Exits 0; emits valid payload JSON to stdout; non-zero on missing required fields | ~1k | Not Started |
| P5.1 | E2E smoke test infrastructure | `tests/_apps_contract/test_apps_rg_e2e_resume_generation.py` | Fixture inputs (master_resume + JD); `pytest.mark.e2e`; runs against real vLLM Qwen 32B per memory `01483ea2`; skipped if VLLM_BASE_URL unset | ~3k | Not Started |
| P5.2 | Brown & Brown smoke artifact | (one-time real run) | Produces `artifacts/apps_rg/runs/<ts>/generated_resume.json`; non-empty; passes AppsRgProfileManifest.output_schema validation | ~3k | Not Started |
| P5.3 | Capability smoke tests | `tests/_apps_contract/test_apps_rg_smoke_capability.py`, `test_apps_rg_dry_run.py`, `test_apps_rg_runner_instantiable.py` | 4 positive-assertion tests; balance the 15 governance tests; mark as TIER1 must-pass | ~2k | Not Started |
| P6.1 | Plan template DoD section | `.cursor/templates/execution-plan-template.md` | Add `## Definition of Done` with required smoke-test row + verification-vs-deferral table | ~2k | Not Started |
| P6.2 | 3 new CI gates | `ops_scripts/ci/check_apps_package_importable.py`, `check_apps_dry_run_works.py`, `check_plan_completion_dod.py` + register in `run_contract_gates.py` | Advisory by default; bypass env vars; mirror existing gate patterns from c4d2a8 / 6e7e9afe | ~3k | Not Started |
| P6.3 | Plan-location rule update | `.cursor/rules/plan-location.md` | Add DoD requirements; cross-ref this plan slug | ~2k | Not Started |

---

## §8. ADG_HOTSPOT_REPORT

| Hotspot | File | Layer | Fan-in | Fan-out | Archetype | Surface intersection | Impact |
|---|---|---|---|---|---|---|---|
| AppIngressRunner | `agentic_core/runtime/entry/app_ingress_runner.py` | L0/runtime entry | HIGH (every apps_*) | LOW (single class) | CENTRAL_DEPENDENCY | Execution + Security + Observability | HIGH — `.run()` extension touches every app |
| apps_rg `__main__.py` | `apps_rg/__main__.py` | apps_rg/ingress | LOW (entry only) | HIGH (consumes core pipeline) | ORCHESTRATOR | Execution | HIGH — entry point for the entire app |
| U0 ingress validator | `agentic_core/runtime/entry/u0_*` | L0/security | HIGH (every app's request) | LOW | SAFETY_GATEKEEPER | Security + Execution | HIGH — authority-validation chokepoint |
| L1/L0 bindings | `agentic_core/L{1,0}_*/apps_rg_*_binding.py` | L1/L0 | LOW (apps_rg only) | MED | STATE_NODE | Execution + State | MED — task-class-specific glue |
| L2/Exit bindings | `agentic_core/L2_execution/apps_rg_*`, `runtime/exit/apps_rg_*` | L2/Exit | LOW | MED | STATE_NODE | Execution + Write + Observability | MED — execution + disposition emit |

Layer multipliers per `adg-canonical-invariants.md`:
- L0 (×2.0) — AppIngressRunner extension is highest-risk
- L5 — N/A (no safety changes)
- L3 — N/A (managed workflow deferred per c8b3e1 §18)
- L1/L2 (×1.0) — task-class bindings
- L6 (×0.75) — observability via OTEL spans, lower weight

5 Surfaces touched: **Execution** (the entire pipeline), **Write** (Exit emits state-write request — L4 deferred per §18), **Security** (U0 authority validation), **State** (L1/L0 contracts), **Observability** (OTEL span chain U0→L1→L0→[C0]→[PA]→L2→Exit per c8b3e1 §10).

---

## §9. ADG_GRAPH_LAYER_EVIDENCE

This is **simultaneously a runtime-completion plan AND a process-discipline plan**. The runtime portion (W2–W5) IS in agentic_core ADG scope; the discipline portion (W6) is infrastructure.

### 9.1 Materialized views (≥3 required)

1. **`mv_graph_reverse_dependency_hotspots`** — `AppIngressRunner` will surface as a new high-fan-in node once the `.run()` method is consumed by sibling apps. This plan establishes the pattern that drives that fan-in.
2. **`mv_graph_chokepoint_bridges`** — U0 ingress validator IS the chokepoint between apps_* and core runtime. This plan formalizes the bridge.
3. **`mv_dependency_cone_risk`** — `apps_rg/__main__.py` cone is currently 0 (broken at import); this plan restores it to the documented W5 architecture.

### 9.2 Semantic edges (`flows_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite`, `reads_from`, `writes_to`)

```
apps_rg.__main__.main
  ├─ flows_to → AppsRgIngressPayload (constructor)
  │             └─ flows_to → AppIngressRunner.run()
  │                           ├─ flows_to → u0_apps_rg_binding.validate (Security surface)
  │                           ├─ flows_to → L1_apps_rg.emit_l1_plan
  │                           │             └─ flows_to → L0_apps_rg.emit_route
  │                           │                           ├─ controls_flow → C0_apps_rg.emit_evidence  (conditional)
  │                           │                           ├─ controls_flow → PA_apps_rg.compile_prompt (conditional)
  │                           │                           └─ flows_to → L2_apps_rg.execute
  │                           │                                         ├─ resolves_callsite → SovereignLLMGateway.invoke
  │                           │                                         │                       └─ writes_to → vLLM Qwen 32B (per memory 01483ea2)
  │                           │                                         └─ flows_to → Exit_apps_rg.emit_disposition
  │                           │                                                       └─ writes_to → artifacts/apps_rg/runs/<ts>/generated_resume.json
  │                           └─ emits_side_effect → OTEL span chain (L6)
```

### 9.3 P-views

- **`v_p0_*`** — apps_rg currently exhibits a P0 layer break: `apps_rg.__init__` imported a module that raises (P0 critical-layer-break-equivalent). Repaired this session. Plan ensures no further P0 violations introduced.
- **`v_p1_*`** — quarantined files raising RuntimeError fall under "mis-layered/zero-caller infra". Plan does not de-quarantine; uses parallel core bindings instead.

---

## §10. Definition of Done (per W6 — applies to THIS plan first)

| # | DoD criterion | How verified |
|---|---|---|
| DoD-1 | `import apps_rg` succeeds | `python -c "import apps_rg"` exits 0 |
| DoD-2 | `python -m apps_rg --help` succeeds | exits 0 with full flag listing |
| DoD-3 | `python -m apps_rg --dry-run --target-company X --target-role Y --source-resume Z --jd W` exits 0 | smoke test in CI |
| DoD-4 | `python -m apps_rg <full Brown & Brown invocation>` produces a real resume artifact | E2E test in CI (P5.2) |
| DoD-5 | `AppIngressRunner.run(AppsRgIngressPayload)` method exists + unit-tested | unit test green |
| DoD-6 | OTEL span chain U0→L1→L0→[C0]→[PA]→L2→Exit captured for one full happy-path run | OTEL verification per c8b3e1 §10 |
| DoD-7 | All 15 existing bypass tests STILL pass (governance preserved) | regression CI |
| DoD-8 | 4 new capability smoke tests + 6 unit tests pass | CI |
| DoD-9 | Plan §2 RCA published as ADR or runtime_cert report | `docs/reports/runtime_cert/apps_rg_w0_w9_rca.md` exists + linked from this plan |
| DoD-10 | 3 new CI gates registered + advisory-passing | `run_contract_gates.py` includes APPS-IMPORT, APPS-DRYRUN, PLAN-DOD |

**No "Completed" status without all 10 boxes ticked.** This was the single biggest discipline gap in c8b3e1.

---

## §11. Test Surface

| Test file | New cases | Type | Acceptance |
|---|---|---|---|
| `tests/_apps_contract/test_apps_rg_smoke_capability.py` | ~6 | capability smoke | All pass — positive assertions inverse to bypass tests |
| `tests/_apps_contract/test_apps_rg_dry_run.py` | ~4 | dry-run smoke | All pass — `--dry-run` produces valid JSON, exit 0 |
| `tests/_apps_contract/test_apps_rg_runner_instantiable.py` | ~3 | instantiation | `AppIngressRunner.run` exists; instantiates with apps_rg dispatch |
| `tests/_apps_contract/test_apps_rg_e2e_resume_generation.py` | ~2 | e2e (`@pytest.mark.e2e`) | Skipped if `VLLM_BASE_URL` unset; otherwise produces valid `generated_resume.json` |
| `tests/unit/agentic_core/runtime/entry/test_app_ingress_runner_run_method.py` | ~8 | unit | Method dispatch correctness; payload validation; ExitDisposition shape |
| `tests/unit/agentic_core/runtime/entry/test_apps_rg_dispatch.py` | ~10 | unit | Each of dispatch/parse/required_fields tested |
| `tests/unit/agentic_core/L1_cognition/test_apps_rg_l1_binding.py` | ~5 | unit | L1PlanContract emit shape |
| `tests/unit/agentic_core/L0_routing/test_apps_rg_l0_binding.py` | ~5 | unit | RouteContract emit + execution_form |
| `tests/unit/ops_scripts/ci/test_check_apps_package_importable.py` | ~6 | CI gate | Detects broken `__init__.py`; bypass env var |
| `tests/unit/ops_scripts/ci/test_check_apps_dry_run_works.py` | ~6 | CI gate | Detects missing `--dry-run` support |
| `tests/unit/ops_scripts/ci/test_check_plan_completion_dod.py` | ~6 | CI gate | Detects plans marked Completed without DoD section |
| Existing 15 bypass tests | 0 new | regression | All still pass |

**Total new tests:** ~61 · zero existing tests modified.

---

## §12. Bypass + Escape Hatches

| Env var | Effect | Use case |
|---|---|---|
| `APPS_PACKAGE_IMPORT_BYPASS=1` | Importable gate emits warning row instead of failing | Scripted batch runs |
| `APPS_DRY_RUN_BYPASS=1` | Dry-run gate advisory-only | Same |
| `PLAN_DOD_BYPASS=1` | Plan DoD gate advisory-only for plans created before this plan | Backward-compat for existing plans |
| `APPS_RG_E2E_SKIP=1` | Skip E2E test (no vLLM available) | CI on minimal environments |

All bypasses durably logged.

---

## §13. AG_QUEUE_SEED — Anticipated Author-Gate Decisions

```
AG_QUEUE_SEED: plan=apps-rg-runtime-wiring-completion-d4e8a1 id=ARW-1 depends_on= title=Where to put apps_rg-specific dispatch — agentic_core/runtime/entry/apps_rg_dispatch.py vs apps_rg/dispatch.py (would re-introduce runtime authority) vs core/runtime/entry/dispatchers/apps_rg.py (subdir taxonomy)
AG_QUEUE_SEED: plan=apps-rg-runtime-wiring-completion-d4e8a1 id=ARW-2 depends_on=ARW-1 title=Dispatch return shape — direct ExitDisposition vs AsyncIterator[StageProgress] (streaming) vs RunRecord (full receipt)
AG_QUEUE_SEED: plan=apps-rg-runtime-wiring-completion-d4e8a1 id=ARW-3 depends_on= title=Where to publish RCA — docs/reports/runtime_cert/ (existing precedent) vs docs/architecture/adr/ADR-NNN.md (architectural decision) vs both
AG_QUEUE_SEED: plan=apps-rg-runtime-wiring-completion-d4e8a1 id=ARW-4 depends_on= title=L3 deferral — single SINGLE_STEP route only (per c8b3e1 §18) vs minimal MANAGED_WORKFLOW for multi-hop narrative pass
AG_QUEUE_SEED: plan=apps-rg-runtime-wiring-completion-d4e8a1 id=ARW-5 depends_on= title=DoD enforcement — advisory CI gate (PLAN-DOD) only vs blocking pre-commit hook on plan close-out
```

---

## §14. References

- `apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md` (the plan being repaired)
- `author-gate-ui-renderer-hardening-a7f3c2.md` (sibling discipline plan registered earlier this session)
- `apps-eval-harness-parity-f8d4a2.md` (closely related apps_* hardening pattern)
- `apps-eval-harness-deferred-e4a1b7.md` (W2.P3 cert hook adoption shape; pattern source for L2/Exit binding)
- `apps-eval-harness-closeout-b7c9d2.md` (DoD discipline precedent — taxonomy_class field, intentional_failopen_dims annotation)
- Constitutional §6 (Author-Gate), §22 (graph-layer evidence), §32 (Fort Knox / DoD), §35 (queue drain), §36 (plan registration)
- Memory `01483ea2` (vLLM Qwen 32B canonical topology — provider for L2 execution)
- Memory `e24c888b` (apps_qna FEC producer wiring — pattern for apps_rg C0 binding)
- Memory `aa3e66d1` (Cursor Agent single-prompt template — applies to running this plan's E2E test)

---

PLAN_CREATED: slug=apps-rg-runtime-wiring-completion-d4e8a1 tier=T3 status=Not_Started waves=6 phases=17 est_tokens=59k re_opens=apps-rg-declarative-ingress-only-spinal-governance-c8b3e1
