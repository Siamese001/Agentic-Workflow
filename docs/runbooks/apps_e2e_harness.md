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
| **Total** | **95** | **1** |

(Test table lists harness-owned suites only; the broader repo test suite is unchanged.)

## NEXT_STEP Closures (2026-05-01)

All three deferred items closed:

**1. `agentic_core.L0_routing.composition_root.run_scenario` hook** — ADDED. The hook lives in `agentic_core/L0_routing/composition_root.py` and uses a honest inner-status protocol (`ran` / `not_implemented` / `error` / `skipped`). The `terminal_cache` scenario now passes through a real L4 evidence-resolver probe (determinism + fail-closed default). The 6 other scenarios return `not_implemented` with a structured reason pointing to `agentic_core/L3_orchestration/` for future wire-in. Core harness now reports 1/7 pass instead of 0/7 not-executable.

**2. `apps_lic` canonical L3 DAG YAML** — ADDED. `apps_lic/config/l3_dag.yaml` and `apps_lic/config/route_registry.yaml` author the 9-stage HOP pipeline (profile_analysis → research → sender_grounding → routing → generation → validation → gate_decision / qa_report → integration) as canonical YAML. Derived by producer-consumer matching from `apps_lic/config/hop_pipeline.py::_STAGE_SPECS`. Static-DAG proof: 9 nodes, 15 edges, no cycle, max_depth=6, all invariants pass, registry binding matches. `static_l3_dag_missing` no longer appears in apps_lic's blocking_gaps.

**3. First live nightly sweep** — RUN. Bounded 60 s-per-app probe captured in `tools/certification/apps_e2e/live_sweep_findings.yaml`. Updated 2026-05-02:

| App | Status | Closure |
|---|---|---|
| apps_rg | works (reference) | full end-to-end success |
| apps_qna | **wired 2026-05-02** | `build --config .../synthetic_mini/interview.yaml --dry-run`; exit=0; 6 remaining gaps legitimate (BYPASS app, no spine receipts) |
| apps_eval / apps_exec / apps_lic / apps_research / apps_rfp | timeout @ 60 s | **app-owner**: each `__main__.py` is 8KB+ of lifecycle trace emits driving full runs; adding `--dry-run` requires app-owner knowledge of run_main() signatures |
| apps_underwriting_ai | skeleton | correctly classified |

**Harness correctness unchanged**: `emit_proof_bundle.py` catches `TimeoutExpired`, emits fail-closed bundle with `exit_code=-1`. Per-app `--dry-run` hooks live in each app's `__main__.py` — they are app-owner additions, not harness responsibilities.

**4. Pre-existing composition_root test failures** — FIXED 2026-05-02. `tests/agentic_core/L0_routing/test_composition_root.py::test_install_default_resolvers_success` and `::test_install_default_resolvers_l4_import_failure` were failing because they tried to `mock.patch` `set_evidence_resolver` as a module-level attribute of `composition_root`, but it's imported locally inside `install_default_resolvers()`. Fix: patch the source module (`agentic_core.L4_state.utils.memory.semantic_cache_manager.set_evidence_resolver`) and use `sys.modules[target] = None` to simulate genuine import failure. No changes to production code.

## CI Integration

`.github/workflows/apps-e2e-harness-nightly.yml` defines two jobs:

* **`harness-verifier`** — runs on every push to main, every PR touching the harness, and inside the nightly. Cheap (~10 s): unit tests + dry-run bundles + verifier + CI gate.
* **`nightly-emit`** — runs on cron (`42 3 * * *`) and `workflow_dispatch`. Heavy (~30-60 min): live `python -m apps_*` for every runnable spec, matrix build, full verifier, core spine proof. Uploads bundles + matrix as a 30-day GitHub artifact.

The `workflow_dispatch` event takes a `skip_apps` input for skipping individual apps that are known to time out.

## Legacy Path Note

The original `tools/certification/apps_rg_e2e/` emitter (~36 KB, 4 files) remains in place — it is the historical apps_rg-only proof bundle and a peer reference. The shared `tools/certification/apps_e2e/` harness supersedes it for new work. `tools/certification/apps_e2e/migrate_legacy_paths.py` writes a `legacy_path_pointer.json` in the legacy directory pointing consumers to the canonical bundle.
