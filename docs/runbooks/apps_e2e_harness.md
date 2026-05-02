# Apps_* End-to-End Auditability Harness — Runbook

**Plan**: `.windsurf/plans/apps-e2e-auditability-harness-7c2a91.md`
**Implementation**: 2026-05-01

The harness proves each runnable `apps_*` package routes through the governed `agentic_core` runtime spine and emits a complete, hash-bound, run_id-bound proof bundle.

## TL;DR — How to Run

```bash
# 1. Emit per-app proof bundles (real runs; ~15 min ceiling per app)
python -m tools.certification.apps_e2e.emit_proof_bundle --app apps_rg
python -m tools.certification.apps_e2e.emit_proof_bundle --all

# 2. Quick dry-run (uses existing on-disk run artifacts; seconds)
python -m tools.certification.apps_e2e.emit_proof_bundle --all --dry-run

# 3. Build the all-apps matrix from emitted bundles
python -m tools.certification.apps_e2e.matrix_builder --print-table

# 4. Nightly batch driver — runs every spec, builds matrix, prints durations
python -m tools.certification.apps_e2e.nightly_run            # live
python -m tools.certification.apps_e2e.nightly_run --dry-run  # ~5 s
python -m tools.certification.apps_e2e.nightly_run --skip apps_lic apps_research

# 5. Verifier — fail-closed checks
python -m pytest tests/runtime/test_apps_e2e_auditability_harness.py -q
python -m pytest tests/runtime/test_apps_e2e_matrix.py -q
python -m pytest tests/runtime/test_apps_e2e_anti_cheat.py -q

# 6. CI gate (non-subprocess; verifies bundles + matrix freshness)
python -m ops_scripts.ci.check_apps_e2e_harness

# 7. Legacy path migration helper (writes pointer in apps_rg_e2e/)
python -m tools.certification.apps_e2e.migrate_legacy_paths

# 8. Separate agentic_core spine harness (does NOT cover apps_*)
python -m tools.certification.agentic_core_e2e.run_core_proof --print-table
python -m pytest tests/runtime/test_agentic_core_spine_proof.py -q
```

## Architecture

```
tools/certification/
├── apps_e2e/                              # Apps→spine harness (W1-W4)
│   ├── __init__.py                        # schema versions
│   ├── app_specs.py                       # ★ declarative AppSpec registry (one entry per app)
│   ├── hash_utils.py                      # sha256 / git / iso-utc / detect_mock
│   ├── paths.py                           # AppCertPaths SSOT
│   ├── spine_signals.py                   # static-source overlay-respect scan
│   ├── stage_collectors.py                # find U0/L1/L0/L3/C0/PA/L2/Exit/L6/OTEL artifacts
│   ├── static_dag_inspector.py            # generic static-DAG proof emitter
│   ├── proof_bundle.py                    # AppE2EProofBundle assembler
│   ├── shared_verifier.py                 # ★ §10 fail-closed rules — single SSOT
│   ├── matrix_builder.py                  # apps_e2e_matrix.json roll-up
│   ├── emit_proof_bundle.py               # CLI: --app, --all, --dry-run
│   ├── nightly_run.py                     # CLI: full nightly batch + matrix
│   └── migrate_legacy_paths.py            # one-shot legacy_path_pointer writer
└── agentic_core_e2e/                      # Spine-alone harness (W5)
    ├── __init__.py
    ├── hash_utils.py                      # duplicated by design (no apps_e2e import)
    ├── scenarios.py                       # 7 canonical core scenarios
    └── run_core_proof.py                  # CLI

tests/
├── runtime/
│   ├── test_apps_e2e_auditability_harness.py   # parametrized over APP_SPECS
│   ├── test_apps_e2e_matrix.py
│   ├── test_apps_e2e_anti_cheat.py             # fabrication detection
│   └── test_agentic_core_spine_proof.py        # boundary invariant + scenarios
└── unit/apps_e2e/
    ├── test_app_specs.py
    ├── test_hash_utils.py
    ├── test_static_dag_inspector.py
    └── test_shared_verifier.py

.windsurf/schemas/
├── apps_e2e_proof_bundle.schema.json
├── apps_e2e_static_l3_dag_proof.schema.json
└── apps_e2e_matrix.schema.json

ops_scripts/ci/check_apps_e2e_harness.py        # CI gate (non-subprocess)
```

## Artifact Layout

```
artifacts/certification/apps_e2e/
├── apps_rg/
│   ├── apps_rg_e2e_proof.json
│   ├── apps_rg_static_l3_dag_proof.json
│   ├── apps_rg_artifact_manifest.json
│   └── apps_rg_run.log
├── apps_eval/...
├── apps_exec/...
├── apps_lic/...
├── apps_qna/...
├── apps_research/...
├── apps_rfp/...
├── apps_underwriting_ai/...                    # skeleton-only; honest fail-closed
└── apps_e2e_matrix.json                        # generated from bundles, not hand-authored

artifacts/certification/agentic_core_e2e/
├── agentic_core_spine_proof.json               # 7 scenarios; all not_implemented today
└── agentic_core_route_matrix.json
```

The legacy `artifacts/certification/apps_rg_e2e/` path remains in place; the new shared harness writes to the canonical `apps_e2e/<app>/` layout.

## Apps Covered (8 specs)

| App | Runnable | Expected Route | Static DAG | C0 | PA | L2 | UWG |
|---|:---:|---|:---:|:---:|:---:|:---:|:---:|
| apps_rg | ✅ | UNKNOWN→BYPASS | ✅ | ❌ | ❌ | ✅ | ❌ |
| apps_eval | ✅ | UNKNOWN | ❌ | ✅ | ✅ | ✅ | ❌ |
| apps_exec | ✅ | UNKNOWN | ❌ | ❌ | ✅ | ✅ | ❌ |
| apps_lic | ✅ | MANAGED_WORKFLOW | ✅ | ✅ | ✅ | ✅ | ❌ |
| apps_qna | ✅ | BYPASS | ❌ | ❌ | ❌ | ❌ | ❌ |
| apps_research | ✅ | UNKNOWN | ❌ | ✅ | ✅ | ✅ | ❌ |
| apps_rfp | ✅ | UNKNOWN | ❌ | ✅ | ✅ | ✅ | ❌ |
| apps_underwriting_ai | ❌ | n/a | n/a | n/a | n/a | n/a | n/a |

## Adding a new app

```python
# tools/certification/apps_e2e/app_specs.py — add one entry to APP_SPECS:
AppSpec(
    app_name="apps_newthing",
    app_package="apps_newthing",
    runnable=True,
    expected_route_form="UNKNOWN",
    expects_static_dag=False,
    expects_c0_grounding=True,
    expects_prompt_assembly=True,
    expects_l2_execution=True,
    expects_durable_mutation=False,
    runs_root_glob="artifacts/apps_newthing/runs/*",
    notes="One-liner about the app",
),
```

That's it. No new test file, no new emitter, no new verifier rule. The shared core picks up the spec automatically.

## Pass/Fail Semantics

* **`harness_pass=true`** — the emitter ran (always true; harness honesty).
* **`success=true`** — the app actually routed through the spine end-to-end with all required artifacts hash-matching and run_id threading.
* **Verifier failure** — the bundle is INTERNALLY INCONSISTENT (claimed success without evidence, hash mismatch, etc.). NOT triggered by `success=false`.

A bundle that honestly declares `success=false` with a populated `blocking_gaps[]` is a passing verifier outcome — that's exactly the fail-closed honesty the harness is built to preserve.

## Anti-Cheat (§10) Fail-Closed Rules

The shared verifier (`shared_verifier.verify_bundle`) enforces:

1. All 36 required top-level fields present
2. `app_name` matches AppSpec; `entrypoint_command` starts with `python -m <pkg>`
3. ISO-UTC timestamps
4. `harness_pass=true` (the emitter must run)
5. `static_dag_ref` resolves and hashes match
6. Every `run_info.artifacts[]` entry hash-matches its file on disk
7. No stale artifacts in run dir (5 s clock-skew tolerance)
8. `blocking_gaps[]` is `list[str]` and non-empty when `success=false`
9. **Anti-cheat**: `success=true` requires every runtime ref to be a real, hash-matching file
10. **Anti-cheat**: `success=true` requires single-run-id threading across all stages
11. MANAGED_WORKFLOW: runtime L3 `dag_sha256` matches static DAG proof
12. L3 bypass: `l3_bypass_reason` ∈ {TERMINAL_SHORTCIRCUIT, SINGLE_STEP_ROUTE, FALLBACK_RET, NO_MANAGED_WORKFLOW_REQUIRED}
13. `synthetic_trace_detected=true` and `success=true` is mutually exclusive
14. Exit X3 disposition ∈ {EXIT_OK, EXIT_PARTIAL, EXIT_FAIL, EXIT_ROLLBACK}
15. L6 exhaust references the Exit packet ID and is observed AFTER it
16. `app_overlay_authority_status="overlay_violated"` and `success=true` is mutually exclusive

## Boundary Invariant: Apps Harness vs Core Harness

`tools.certification.apps_e2e.*` and `tools.certification.agentic_core_e2e.*` MUST NOT import each other. Enforced by `tests/runtime/test_agentic_core_spine_proof.py::test_boundary_invariant_no_apps_e2e_imports` and its dual.

The two harnesses share NO code; they share a discipline: same hash format, same `success`/`harness_pass` semantics, same fail-closed honesty.

## Test Counts (as of 2026-05-01 commit)

| Suite | Pass | Skip |
|---|---:|---:|
| `tests/unit/apps_e2e/` | 28 | 0 |
| `tests/runtime/test_apps_e2e_auditability_harness.py` | 24 | 0 |
| `tests/runtime/test_apps_e2e_matrix.py` | 8 | 0 |
| `tests/runtime/test_apps_e2e_anti_cheat.py` | 8 | 1 |
| `tests/runtime/test_agentic_core_spine_proof.py` | 6 | 0 |
| `tests/agentic_core/L0_routing/test_composition_root.py` | 15 | 0 |
| `tests/agentic_core/L0_routing/test_composition_root_run_scenario.py` | 6 | 0 |
| `tests/unit/apps_shared/test_apps_e2e_dry_run.py` | 5 | 0 |
| **Total** | **100** | **1** |

(Test table lists harness-owned suites only; the broader repo test suite is unchanged.)

## NEXT_STEP Closures (2026-05-01)

All three deferred items closed:

**1. `agentic_core.L0_routing.composition_root.run_scenario` hook** — ADDED. The hook lives in `agentic_core/L0_routing/composition_root.py` and uses a honest inner-status protocol (`ran` / `not_implemented` / `error` / `skipped`). The `terminal_cache` scenario now passes through a real L4 evidence-resolver probe (determinism + fail-closed default). The 6 other scenarios return `not_implemented` with a structured reason pointing to `agentic_core/L3_orchestration/` for future wire-in. Core harness now reports 1/7 pass instead of 0/7 not-executable.

**2. `apps_lic` canonical L3 DAG YAML** — ADDED. `apps_lic/config/l3_dag.yaml` and `apps_lic/config/route_registry.yaml` author the 9-stage HOP pipeline (profile_analysis → research → sender_grounding → routing → generation → validation → gate_decision / qa_report → integration) as canonical YAML. Derived by producer-consumer matching from `apps_lic/config/hop_pipeline.py::_STAGE_SPECS`. Static-DAG proof: 9 nodes, 15 edges, no cycle, max_depth=6, all invariants pass, registry binding matches. `static_l3_dag_missing` no longer appears in apps_lic's blocking_gaps.

**3. First live nightly sweep** — CLOSED 2026-05-02 05:55 UTC. **All 7/7 runnable apps emit clean exit=0 bundles by default.**

| App | exit_code | duration | mechanism | bundle.success | gaps |
|---|---:|---:|---|:-:|---:|
| apps_rg | 0 | ~118 s | live `--target-company / --auto-research-tavily` | **True** | 0 |
| apps_qna | 0 | ~1.5 s | own `--dry-run` (BYPASS app) | False | 6 (legit) |
| apps_eval | 0 | ~0.9 s | `--apps-e2e-dry-run` short-circuit | False | 9 |
| apps_exec | 0 | ~0.8 s | `--apps-e2e-dry-run` short-circuit | False | 8 |
| apps_lic | 0 | ~0.8 s | `--apps-e2e-dry-run` short-circuit | False | 9 |
| apps_research | 0 | ~0.8 s | `--apps-e2e-dry-run` short-circuit | False | 9 |
| apps_rfp | 0 | ~0.8 s | `--apps-e2e-dry-run` short-circuit | False | 9 |
| apps_underwriting_ai | n/a | n/a | `runnable=False` (skeleton) | False | 1 |

**Shared short-circuit helper**: `apps_shared/_apps_e2e_dry_run.py::maybe_short_circuit(app_name)` is called as the first statement in each runnable app's `__main__.main()`. When `--apps-e2e-dry-run` is in `sys.argv` it prints a structured `APPS_E2E_DRY_RUN: {...}` marker line and exits 0 BEFORE `_adg_bootstrap()` and `run_main()` delegation. The flag is namespaced (not bare `--dry-run`) to avoid collision with `apps_qna`'s own CLI.

**5 dedicated tests** in `tests/unit/apps_shared/test_apps_e2e_dry_run.py` cover: no-op when absent, exits 0 when present, marker JSON shape, namespaced flag invariant, exports.

**Why `success=True` only for apps_rg**: the other 6 apps don't yet emit spine receipts (RouteContract, L1PlanContract, L3OrchestrationReceipt, ExitReviewPacket, RuntimeExhaustBundle, OTEL trace). Those are app-owner deliverables tracked in app-specific plans. The harness-level objective — "every app emits a hash-bound bundle by default" — is fully satisfied.

**4. Pre-existing composition_root test failures** — FIXED 2026-05-02. `tests/agentic_core/L0_routing/test_composition_root.py::test_install_default_resolvers_success` and `::test_install_default_resolvers_l4_import_failure` were failing because they tried to `mock.patch` `set_evidence_resolver` as a module-level attribute of `composition_root`, but it's imported locally inside `install_default_resolvers()`. Fix: patch the source module (`agentic_core.L4_state.utils.memory.semantic_cache_manager.set_evidence_resolver`) and use `sys.modules[target] = None` to simulate genuine import failure. No changes to production code.

## Two-Gate Certification (2026-05-02 — plan `apps-e2e-two-gate-certification-d8b3a1`)

The harness now ships **TWO** CI gates with separate semantics:

| Gate | Mode | Required? | Verifies |
|---|---|---|---|
| **`apps_e2e_bundle_emission`** | smoke | YES (must pass) | Bundle is hash-bound, run_id-bound, schema-valid. Honest fail-closed bundles pass. |
| **`apps_e2e_spine_certification`** | strict | INFORMATIONAL until critical mass | Every `certification_required` app has `success=True`, no `blocking_gaps`, all required receipts present + hash-verified, computed `certification_level=SPINE_COMPLETE_CERTIFIED`. |

### Five certification levels (verifier-computed; bundle-declared value never trusted)

| Level | Meaning |
|---|---|
| `EMITS_BUNDLE` | Valid hash-bound bundle exists. Smoke-only. |
| `FAILS_CLOSED_WITH_GAPS` | success=False with explicit non-empty `blocking_gaps`. Honest. Strict-mode FAIL. |
| `SPINE_COMPLETE_CERTIFIED` | success=True, gaps=0, all required receipts present + hash-verified, runtime_mode=live_run. |
| `WAIVED_SKELETON` | `runnable=False` with valid waiver triple. |
| `WAIVED_NOT_RUNTIME_APP` | `certification_required=False` with valid waiver triple. |

### Current matrix (post-W6, 2026-05-02 06:46 UTC)

```
                          smoke     strict       computed level
apps_rg                   PASS      PASS         SPINE_COMPLETE_CERTIFIED
apps_qna                  PASS      PASS         WAIVED_NOT_RUNTIME_APP
apps_underwriting_ai      PASS      PASS         WAIVED_SKELETON
apps_eval                 PASS      FAIL         FAILS_CLOSED_WITH_GAPS
apps_exec                 PASS      FAIL         FAILS_CLOSED_WITH_GAPS
apps_lic                  PASS      FAIL         FAILS_CLOSED_WITH_GAPS
apps_research             PASS      FAIL         FAILS_CLOSED_WITH_GAPS
apps_rfp                  PASS      FAIL         FAILS_CLOSED_WITH_GAPS
                          ----      ----
                          8/8       3/8 (5 to wire through spine)
```

### Verifier CLI

```bash
# Smoke — bundle emission only
python -m tools.certification.apps_e2e.verifier_cli --mode smoke

# Warn — same checks; always exits 0; emits gap diff to stderr
python -m tools.certification.apps_e2e.verifier_cli --mode warn

# Strict — full S1-S19 + computed level == SPINE_COMPLETE_CERTIFIED
python -m tools.certification.apps_e2e.verifier_cli --mode strict
```

`--mode` is REQUIRED (no implicit default — forces deliberate choice).

### Negative controls

`tests/runtime/test_apps_e2e_two_gate_negative_controls.py` — **23 tests** (full N1–N20 coverage + 3 positive controls), mutate the apps_rg baseline bundle (or use synthetic managed-workflow fixtures for the L3-RAN path) and assert specific violations fire. Covers all 20 negative controls (N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, N16, N18, N19, N20) plus N17 (fixture_data_used legitimacy, MUST PASS) and the unmutated baseline (MUST PASS, run twice — once at suite start and once after all mutations to detect state pollution). Synthetic fixtures live inline in the test file with `_negative_control_fixture: true` sentinels and clearly-marked purposes; they cannot be mistaken for real runtime evidence.

### Shared spine emission (`apps_shared.spine_emission`)

Any runtime app can reach SPINE_COMPLETE_CERTIFIED by wrapping its main
work in the shared `governed_run(EmissionConfig)` context manager:

```python
from apps_shared.spine_emission import EmissionConfig, governed_run
from apps_shared.spine_emission.contracts import L1PlanStep

cfg = EmissionConfig(
    app_name="apps_X",
    entrypoint_command="python -m apps_X",
    runs_root=repo_root / "artifacts" / "apps_X" / "runs",
    route_registry_path=repo_root / "apps_X" / "config" / "route_registry.yaml",
    l3_dag_path=None,  # or the real l3_dag.yaml for MANAGED_WORKFLOW apps
    plan_steps=[L1PlanStep(step_id="...", name="...", kind="...")],
    plan_rationale="...",
    expects_c0_grounding=False,
    expects_prompt_assembly=True,
    expects_static_dag=False,
    expected_execution_form="SINGLE_STEP",  # or MANAGED_WORKFLOW
    expected_l3_path="BYPASSED",             # or RAN
    selected_capability="apps_X.v1",
    repo_root=repo_root,
)
with governed_run(cfg, cli_args=argv) as gr:
    with gr.span("L2_execute"):
        gr.mark_stage("L2_execute", "ok")
```

The helper emits the canonical receipts to `artifacts/<app>/runs/<ts>/`
with the filenames the verifier's `_STAGE_KEYWORDS` look for. 10 unit
tests in `tests/unit/apps_shared/spine_emission/` pin the contract
shape.

Convention: each wired app provides a `--apps-e2e-live` flag in its
`__main__.py` that selects this path. The existing `--apps-e2e-dry-run`
short-circuit is preserved for fast smoke CI.

**State 2026-05-02 (ADR-081, FINAL)**: **8 of 8 apps pass strict**.
Certified via `apps_shared.spine_emission`: apps_rg (baseline) +
apps_exec + apps_lic + apps_eval + apps_research + apps_rfp. Waived:
apps_qna + apps_underwriting_ai. Gate 2 flipped BLOCKING in the nightly
workflow on 2026-05-02.

### `--apps-e2e-dry-run` is NEVER certification

Dry-run is a smoke-only path. The strict verifier rejects bundles whose `runtime_mode_classification ∈ {dry_run_short_circuit, fixture_runtime, mock_runtime, standalone_orchestrator_pre_spine, skeleton_only}`. Only `live_run` is approved. Adding `--apps-e2e-dry-run` to a strict CI driver does NOT silently downgrade certification — strict explicitly fails.

## CI Integration

`.github/workflows/apps-e2e-harness-nightly.yml` defines two jobs:

* **`harness-verifier`** — runs on every push to main, every PR touching the harness, and inside the nightly. Cheap (~10 s): unit tests + dry-run bundles + verifier + CI gate.
* **`nightly-emit`** — runs on cron (`42 3 * * *`) and `workflow_dispatch`. Heavy (~30-60 min): live `python -m apps_*` for every runnable spec, matrix build, full verifier, core spine proof. Uploads bundles + matrix as a 30-day GitHub artifact.

The `workflow_dispatch` event takes a `skip_apps` input for skipping individual apps that are known to time out.

## Legacy Path Note

The original `tools/certification/apps_rg_e2e/` emitter (~36 KB, 4 files) remains in place — it is the historical apps_rg-only proof bundle and a peer reference. The shared `tools/certification/apps_e2e/` harness supersedes it for new work. `tools/certification/apps_e2e/migrate_legacy_paths.py` writes a `legacy_path_pointer.json` in the legacy directory pointing consumers to the canonical bundle.
