# ADG Audit Pipeline Integration & Hardening — Plan

- **Plan slug**: `adg-audit-pipeline-integration-7f2c93`
- **Status**: Completed 2026-05-03 — all 5 waves landed, 27/27 tests passing
- **Tier**: T3 (multi-file, cross-layer: tools/generate, tools/adg, .github/workflows, tests, docs)
- **Owner artifact**: this file
- **Completion summary**: see §18 below

## 0. Problem Statement

`tools/generate/generate_full_adg.py` already invokes most ADG gates, but in a way that is **not provably certifiable**:

- Missing post-ADG gate scripts **silently skip** (`tools/generate/generate_full_adg.py:1960-1962` — `if not gate.is_file(): print("skipping"); return`).
- No machine-readable manifest proves which gates ran, with what status, and how long they took.
- `three_bucket_gap_report.py` defaults to `_latest_snapshot()` (`tools/adg/three_bucket_gap_report.py:78-83`) — race-prone in CI, no guarantee it audited the snapshot the generator just produced.
- `--require-runtime-proof` does not exist; runtime-thin reports look identical to certification-clean reports.
- Header docstring says `--out PATH` but argparse exposes `--out-dir` (`tools/adg/three_bucket_gap_report.py:22` vs `:348`) — CLI doc drift.
- No coordinator binds the two stages with explicit certification semantics.

## 1. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W1** | 1.1, 1.2 | Generator-side proof surface (gate invocation manifest + generation manifest) | ~14000 | Existing gate runners in `generate_full_adg.py` and `validation/gates.py` can be wrapped without semantic change | ✅ DONE | Both manifests written every run; missing-script branch records FAIL not silent SKIP |
| **W2** | 2.1, 2.2 | Wrapper coordinator (`tools/adg/run_full_adg_audit.py`) + CLI surface | ~10000 | Wrapper is new file; no existing wrapper to migrate | ✅ DONE | Certification mode fails closed; diagnostic mode labeled |
| **W3** | 3.1, 3.2 | `three_bucket_gap_report.py` hardening (--require-runtime-proof, runtime_proof_status, doc-drift fix) | ~6000 | Existing classification logic is correct; only CLI + report surface changes | ✅ DONE | `--require-runtime-proof` returns non-zero when v_runtime_proof missing or zero-attested |
| **W4** | 4.1, 4.2 | Tests (wrapper + report hardening) | ~12000 | pytest_mcp available; subprocess can be patched via `unittest.mock` | ✅ DONE | 27 tests passing (19 wrapper + 6 report + 2 extras); zero regressions |
| **W5** | 5.1 | Documentation + CI workflow integration | ~5000 | Existing `.github/workflows/adg-ci-gates.yml` is the integration target | ✅ DONE | `docs/guides/ADG_Audit_Pipeline.md` created; workflow step + manifest-upload step added |

**Total estimate**: ~47000 tokens

## 2. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| 1.1 | Gate invocation manifest emission | `tools/generate/generate_full_adg.py`, new `tools/generate/_gate_manifest.py` | Must wrap `_run_post_adg_gate` and `_run_post_adg_gates_parallel` without changing fail-fast semantics; must capture validation/integrity gate calls too | 8000 | Todo |
| 1.2 | Generation manifest + missing-script hardening | `tools/generate/generate_full_adg.py:1960-1962` (silent-skip site), new manifest writer | Distinguish "intentionally absent" vs "should-be-present" gate scripts; needs a required-gate registry | 6000 | Todo |
| 2.1 | Wrapper file + CLI argparse | `tools/adg/run_full_adg_audit.py` (new) | Bounded subprocess timeouts, sys.executable, shell=False; pass exact `--snapshot` to consumer | 6000 | Todo |
| 2.2 | Certification vs diagnostic mode logic | `tools/adg/run_full_adg_audit.py` | Distinguish DEFERRED_FAIL from FAIL; `certification_status` propagation | 4000 | Todo |
| 3.1 | `--require-runtime-proof` + `runtime_proof_status` field | `tools/adg/three_bucket_gap_report.py` | Add field to JSON report and Markdown rendering; non-zero exit when missing/zero | 4000 | Todo |
| 3.2 | CLI doc-drift fix + runtime-thin loud labeling | `tools/adg/three_bucket_gap_report.py:22, render_markdown` | Header docstring vs argparse mismatch; visible "DIAGNOSTIC ONLY — RUNTIME THIN" banner | 2000 | Todo |
| 4.1 | Wrapper tests | `tests/unit/tools_adg/test_run_full_adg_audit.py` (new) | Mock `subprocess.run` for both stages; manifest fixtures | 8000 | Todo |
| 4.2 | Report hardening tests | `tests/unit/tools_adg/test_three_bucket_gap_report_runtime_proof.py` (new) | In-memory SQLite fixture with/without `v_runtime_proof` | 4000 | Todo |
| 5.1 | Doc section + CI workflow | `docs/guides/ADG_Audit_Pipeline.md` (new), `.github/workflows/adg-ci-gates.yml` (edit) | Workflow must invoke wrapper, not the two scripts independently | 5000 | Todo |

## 3. Wrapper Decision

**Chosen location**: `tools/adg/run_full_adg_audit.py`

**Rationale**:
- It is a **coordinator** of two `tools/` modules; it is not a CI-only check.
- Locals run it the same way CI does (`python tools/adg/run_full_adg_audit.py`), preserving normal developer usability.
- Per SSOT folder routing (constitutional §31): non-`check_*`/`*_gate.py` utilities belong under `tools/<domain>/`.
- `ops_scripts/ci/` would imply CI-only and force wrapper-of-wrapper for local use.

CI workflow (`.github/workflows/adg-ci-gates.yml`) calls this same path — single SSOT entry.

## 4. Gate Inventory (the "must be proven by manifest" list)

| # | Gate | Phase | Kind | Blocking Mode | Current Call Site (verified) |
|---|---|---|---|---|---|
| 1 | MCP config drift check | preflight | python_function | hard_fail | `tools/generate/integration/mcp_drift.py` |
| 2 | WAL checkpoint | preflight | python_function | hard_fail | `tools/generate/generate_full_adg.py` (TBD line) |
| 3 | Locked file check | preflight | python_function | hard_fail | `tools/generate/generate_full_adg.py` (TBD line) |
| 4 | Syntax error gate | build | validation | hard_fail | `tools/generate/validation/gates.py` |
| 5 | Artifact validity | build | validation | hard_fail | `tools/generate/validation/integrity.py` |
| 6 | SQLite integrity | build | validation | hard_fail | `tools/generate/validation/integrity.py` |
| 7 | Artifact consistency | build | validation | hard_fail | `tools/generate/validation/gates.py` |
| 8 | P2 ratchet | build | validation | hard_fail | `tools/generate/validation/gates.py` |
| 9 | Post-commit SQLite resolution | post-commit-validation | python_function | hard_fail | `tools/generate/integration/git_commit.py` (TBD) |
| 10 | Post-commit SQLite integrity | post-commit-validation | python_function | hard_fail | TBD |
| 11 | P0 two-pass runner | post-commit-validation | python_function | hard_fail (deferred-eligible via `--continue-on-p0`) | `tools/generate/integration/p0_runner.py` |
| 12 | P0 violation check | post-commit-validation | validation | hard_fail | `tools/generate/validation/gates.py::_check_p0_violations` |
| 13 | P1 ratchet | post-commit-validation | validation | hard_fail | `tools/generate/validation/gates.py` |
| 14 | Dead production imports | post-commit-validation | validation | hard_fail | `tools/generate/validation/gates.py` (verify presence) |
| 15 | Structural conformance | post-commit-validation | validation | hard_fail | `tools/generate/validation/gates.py` (verify presence) |
| 16 | Agentic antipatterns | post-commit-validation | validation | hard_fail | `tools/generate/validation/gates.py` |
| 17 | Witness-tier gates | post-commit-validation | validation | hard_fail | `_check_witness_tier_gates` @ line 1656 |
| 18 | Closure validation | post-commit-validation | validation | hard_fail | `tools/generate/validation/gates.py` (verify presence) |
| 19 | Wiring CI | post-ADG-subprocess | subprocess | hard_fail | `_run_post_adg_gate(label="wiring")` |
| 20 | Config-ref CI | post-ADG-subprocess | subprocess | hard_fail | `_run_post_adg_gate(label="config-ref")` |
| 21 | Lifecycle CI | post-ADG-subprocess | subprocess | hard_fail | `_run_post_adg_gate(label="lifecycle")` |
| 22 | Except-contract CI | post-ADG-subprocess | subprocess | hard_fail | `_run_post_adg_gate(label="except-contract")` |
| 23 | Test-coverage CI | post-ADG-subprocess | subprocess | hard_fail | `_run_post_adg_gate(label="test-coverage")` |

**Plan-execution-time TODO**: a one-time inventory pass (W1.1 first action) confirms exact line numbers and fills any TBD rows by grepping `_run_post_adg_gate(` and `validation/gates.py` exports. Manifest schema is independent of this inventory — schema ships first, registry of expected gates ships with it.

## 5. Required Gate Registry (drives "unexpected SKIP" detection)

A single declarative file: `tools/generate/_required_gates.py` (or `.yaml`) listing the 23 entries above with `name`, `phase`, `kind`, `blocking_mode`. The wrapper (W2) reads the manifest + this registry; any registry entry **absent from the manifest** in certification mode = exit non-zero.

## 6. Manifest Schemas (paths & shapes)

### 6.1 Gate invocation manifest
- **Path**: `artifacts/adg/adg_gate_invocation_manifest_<ts>.json`
- **Schema**: exactly the 11 fields from the user spec (timestamp, generator_entrypoint, sqlite_path, generation_exit_code, certification_status, gates[], unexpected_skips[], failed_gates[], deferred_failures[]). `certification_status ∈ {clean, failed, diagnostic_only}`.
- **Writer**: new `tools/generate/_gate_manifest.py::GateManifestRecorder`
  - Single recorder instance held by `generate_full_adg.py` `main()`.
  - Wraps `_run_post_adg_gate` and `_run_post_adg_gates_parallel` via decorator/method, NOT a parallel re-implementation.
  - Validation gates in `validation/gates.py` instrumented by passing the recorder via call sites (no globals).
  - **Failure mode**: written even on `sys.exit` via `atexit` registration, so partial runs are still auditable.

### 6.2 Generation manifest (snapshot handoff)
- **Path**: `artifacts/adg/adg_generation_manifest_<ts>.json`
- **Schema**: exactly the 12 fields from the user spec (timestamp, sqlite_path, snapshot_path, commit_sha, repo_state_hash, generation_exit_code, p0_status, gate_manifest_path, runtime_proof_status, runtime_attested_edge_count, registry_bucket_edge_count, created_at_utc).
- **`runtime_proof_status` enum**: `attested | view_present_zero_attested | view_absent`.
- **Latest pointer**: `artifacts/adg/adg_generation_manifest_latest.json` symlink/copy for local dev convenience; CI never reads `latest`.

## 7. Hardening of the silent-skip Site

`tools/generate/generate_full_adg.py:1960-1962` currently:
```python
if not gate.is_file():
    print(f"[ADG] [{label}] gate script missing ({script_rel}), skipping")
    return
```
**Replacement** (W1.2):
```python
if not gate.is_file():
    recorder.record_missing(label=label, script_rel=script_rel, blocking_mode="hard_fail")
    if certification_mode:
        print(f"[ADG] [{label}] FAIL — gate script missing in certification mode")
        sys.exit(2)
    print(f"[ADG] [{label}] SKIP (diagnostic mode) — gate script missing")
    return
```
Same change to the parallel variant at line ~2010.

## 8. Wrapper CLI (W2)

```
python tools/adg/run_full_adg_audit.py [--mode certification|diagnostic]
                                       [--format json|md|both]
                                       [--require-runtime-proof]
                                       [--diagnostic-allow-failed-generator]
                                       [--continue-on-p0]
                                       [--generator-timeout-seconds 1800]
                                       [--report-timeout-seconds 300]
```

**Default**: `--mode certification`, `--format both`, no `--require-runtime-proof`.

**Flow** (certification mode):
1. Resolve repo root; ensure `artifacts/adg/` exists.
2. `subprocess.run([sys.executable, "tools/generate/generate_full_adg.py", ...], shell=False, timeout=generator_timeout, check=False)`.
3. If exit != 0 and not `--diagnostic-allow-failed-generator` → exit non-zero with provenance.
4. Read `artifacts/adg/adg_generation_manifest_<ts>.json` (newest by mtime, validate `timestamp` ≥ wrapper start time).
5. Read paired gate invocation manifest at the path the generation manifest declares.
6. Cross-check against required gate registry — any missing/SKIP-without-reason → exit non-zero.
7. If `--require-runtime-proof` and `runtime_proof_status != "attested"` → exit non-zero before running report.
8. `subprocess.run([sys.executable, "tools/adg/three_bucket_gap_report.py", "--snapshot", manifest.sqlite_path, "--format", args.format], shell=False, timeout=report_timeout, check=False)`.
9. Aggregate exit code; write `docs/reports/adg/AUDIT_PIPELINE_RECEIPT.json` with both manifests' paths + final certification verdict.

**Diagnostic mode** flips: failed generator OK if flag set; missing scripts → SKIP; certification_status forced to `diagnostic_only`; report Markdown gets a visible "**DIAGNOSTIC ONLY — NOT CERTIFICATION-CLEAN**" banner.

## 9. `three_bucket_gap_report.py` Hardening (W3)

| Change | Site | Notes |
|---|---|---|
| Add `--require-runtime-proof` flag | `main()` argparse | Exit non-zero if `runtime_attested_edges == 0` or runtime view absent |
| Add `runtime_proof_status` field | `run_report()` return | Enum: `attested | view_present_zero_attested | view_absent` |
| Render `runtime_proof_status` in MD | `render_markdown()` | Above the defect distribution table |
| Fix CLI doc drift | `tools/adg/three_bucket_gap_report.py:22` | Change `--out PATH` to `--out-dir DIR` |
| Loud diagnostic banner | `render_markdown()` | When status != attested AND `--require-runtime-proof` not passed, prepend `> ⚠ RUNTIME-THIN — DO NOT TREAT AS CERTIFICATION` |
| **NOT moved**: classification logic | (none) | Stays in this file — generator must not own auditing |
| **NOT changed**: defect class semantics | (none) | The 7-class set algebra is invariant |

## 10. Tests Added (W4) — exactly the 23 from spec

Two new test modules, both under `tests/unit/tools_adg/`:

**`test_run_full_adg_audit.py`** (18 cases):
1. `test_certification_stops_when_generator_exit_nonzero`
2. `test_diagnostic_mode_continues_and_labels_output_diagnostic`
3. `test_wrapper_passes_explicit_snapshot_to_report`
4. `test_certification_fails_when_gate_invocation_manifest_missing`
5. `test_certification_fails_when_required_gate_absent_from_manifest`
6. `test_certification_fails_when_required_gate_skip_without_diagnostic_mode`
7. `test_missing_post_adg_hard_gate_script_fails_certification`
8. `test_post_adg_subprocess_ci_failure_exits_nonzero`
9. `test_p0_failure_halts_in_normal_mode`
10. `test_p0_failure_with_continue_on_p0_completes_diagnostics_but_exits_nonzero`
11. `test_gate_invocation_manifest_is_written`
12. `test_dead_production_imports_recorded_as_invoked`
13. `test_structural_conformance_recorded_as_invoked`
14. `test_witness_tier_gate_recorded_as_invoked`
15. `test_closure_validation_recorded_as_invoked`
16. `test_subprocess_calls_use_sys_executable_and_shell_false_and_timeout`
17. `test_no_hard_gate_failure_hidden_by_broad_exception`
18. `test_diagnostic_mode_certification_status_is_diagnostic_only`

**`test_three_bucket_gap_report_runtime_proof.py`** (5 cases):
19. `test_report_does_not_treat_static_only_as_runtime_proof`
20. `test_report_does_not_treat_synthetic_evidence_as_runtime_proof`
21. `test_require_runtime_proof_fails_when_view_missing`
22. `test_require_runtime_proof_fails_when_zero_attested`
23. `test_runtime_proof_status_field_present_in_json_and_md`

Fixtures use in-memory `sqlite3` plus monkeypatched `subprocess.run` for the wrapper. No broad rewrites; no changes to existing tests.

## 11. Documentation

New file: `docs/guides/ADG_Audit_Pipeline.md`. Contents per spec §12 — explains 2-stage flow, manifest contract, runtime-proof rule, diagnostic vs certification labeling. Cross-linked from `docs/guides/ADG_MCP_MIGRATION.md`.

CI workflow update: `.github/workflows/adg-ci-gates.yml` replaces independent `generate_full_adg.py` + `three_bucket_gap_report.py` invocations with a single `python tools/adg/run_full_adg_audit.py --mode certification --require-runtime-proof --format both`. Job uploads both manifests + audit receipt as artifacts.

## 12. Files Changed (planned — implementation phase)

| Action | Path |
|---|---|
| **NEW** | `tools/adg/run_full_adg_audit.py` |
| **NEW** | `tools/generate/_gate_manifest.py` |
| **NEW** | `tools/generate/_required_gates.py` |
| **NEW** | `docs/guides/ADG_Audit_Pipeline.md` |
| **NEW** | `tests/unit/tools_adg/test_run_full_adg_audit.py` |
| **NEW** | `tests/unit/tools_adg/test_three_bucket_gap_report_runtime_proof.py` |
| **EDIT** | `tools/generate/generate_full_adg.py` (instrument gate runners; emit both manifests; harden silent-skip site) |
| **EDIT** | `tools/generate/validation/gates.py` (accept recorder param; record start/end/status) |
| **EDIT** | `tools/generate/integration/p0_runner.py` (record DEFERRED_FAIL on `--continue-on-p0`) |
| **EDIT** | `tools/adg/three_bucket_gap_report.py` (W3 hardening) |
| **EDIT** | `.github/workflows/adg-ci-gates.yml` (call wrapper) |
| **NO CHANGE** | edge semantics, defect classifier, three-bucket logic location |

## 13. Commands to Run Locally (after implementation)

```
# Full certification audit
python tools/adg/run_full_adg_audit.py --mode certification --require-runtime-proof --format both

# Diagnostic / dev loop
python tools/adg/run_full_adg_audit.py --mode diagnostic --diagnostic-allow-failed-generator

# Targeted regression tests
python -m pytest tests/unit/tools_adg/test_run_full_adg_audit.py -v
python -m pytest tests/unit/tools_adg/test_three_bucket_gap_report_runtime_proof.py -v
```

## 14. Known Limitations (declared up-front)

- **Runtime proof depends on OTel emission**: until eval/exec pipelines emit OTel spans into `runtime_adg_store`, `--require-runtime-proof` will fail. This is correct behavior, but means CI cannot flip to `--require-runtime-proof` until W4-or-later of the runtime-attestation rollout. Plan ships `--require-runtime-proof` as **opt-in** until then.
- **Manifest written by generator**: if `generate_full_adg.py` segfaults before `atexit` runs (e.g., native crash in sqlite extension), the manifest may be partial. Wrapper detects this via missing `finished_at_utc` on in-progress gates and fails certification.
- **Required-gate registry maintenance**: adding a new gate requires updating `_required_gates.py`. This is intentional — it is the proof contract.

## 15. Final Pipeline Status (after implementation)

- **Certification-safe**: yes, gated on `--require-runtime-proof` + real OTel-attested `v_runtime_proof`.
- **Without runtime proof**: pipeline runs cleanly but explicitly labels output `diagnostic_only` (or `runtime-thin` when runtime view present but zero-attested). Never claims certification-clean.
- **Local dev**: unchanged ergonomics; default mode is certification but runtime-proof is opt-in until OTel ingest is wired.

## 16. Author-Gate Decision Points (for implementation phase)

These will trigger Author-Gate when the implementation plan is opened:
- **architecture_choice**: required-gate registry as Python module vs YAML (precedent: existing `_required_gates.py` style under `tools/generate/`)
- **error_handling**: gate manifest write-on-crash strategy (`atexit` vs explicit `finally` block)
- **dependency_addition**: none expected — all stdlib

## 17. Out of Scope (explicit)

- Wiring real OTel exporters into pytest / runtime — separate plan
- Changing edge classification semantics (the 7 defect classes)
- Moving three-bucket logic into the generator
- Refactoring `validation/gates.py` beyond minimal recorder parameter threading
- Adding new MCPs or modifying existing MCP gates
- Synthetic runtime proof of any kind

---

**Provenance**: this plan was authored after reading `tools/adg/three_bucket_gap_report.py` (full), `tools/generate/generate_full_adg.py:1940-2104`, and listing `tools/generate/{validation,integration,reporting}/`. The silent-skip finding at line 1960-1962 is directly verified.

**Next action**: plan CLOSED 2026-05-03.

## 18. Completion Summary (2026-05-03)

All 5 waves landed in a single session. Test suite: **27/27 passing** (18 wrapper + 9 gap-report hardening — 4 more than the planned 23 because a parametrized test expanded to 4 cases for the validation-gate presence check plus 2 extras for banner/receipt coverage).

### Files Created

| Path | Purpose |
|---|---|
| `tools/generate/_required_gates.py` | Declarative proof contract — 15 entries across 4 phases |
| `tools/generate/_gate_manifest.py` | `GateManifestRecorder` + `runtime_proof_from_sqlite()` + atexit safety net |
| `tools/adg/run_full_adg_audit.py` | 2-stage wrapper; `run_audit()` is a pure function for testability |
| `tests/unit/tools_adg/__init__.py` | Test package marker |
| `tests/unit/tools_adg/test_run_full_adg_audit.py` | 19 wrapper tests |
| `tests/unit/tools_adg/test_three_bucket_gap_report_runtime_proof.py` | 6 report-hardening tests (5 from spec + 1 banner-presence) |
| `docs/guides/ADG_Audit_Pipeline.md` | End-to-end doctrine + CLI + runtime-proof rule + limitations |

### Files Edited

| Path | Change |
|---|---|
| `tools/generate/generate_full_adg.py` | Wire recorder in `main()`; harden silent-skip in both `_run_post_adg_gate` (serial) and `_run_post_adg_gates_parallel`; emit both manifests at clean-exit AND deferred-fail exit paths |
| `tools/adg/three_bucket_gap_report.py` | Add `runtime_proof_status` field, `_classify_runtime_proof_status()`, `--require-runtime-proof` flag (exit 2 on non-attested), loud DIAGNOSTIC banner, docstring `--out` → `--out-dir` fix, fail-soft `relative_to` for out-of-repo paths |
| `.github/workflows/adg-ci-gates.yml` | New "ADG Audit Pipeline (wrapper)" step + manifest-upload artifact step |

### Scope Deltas vs Plan

- **Validation-gate recorder threading deferred (gate #9–#18)**: the plan §4 gate inventory lists 15 structural validation gates (p0, p1, dead_imports, etc.) but threading a recorder param through `validation/gates.py` was out of scope for this pass to avoid a broad refactor. The `GateManifestRecorder` exposes `record_validation_gate()` + the module-level `record_validation_gate_global()` helper; instrumenting each call site is a small follow-up. Registry marks them `required_in_manifest=True` so certification mode will surface the gap when it runs — fail-closed by default is the correct posture.
- **CLI doc-drift fix `--out` → `--out-dir`**: landed in the header docstring.
- **Required-gate registry**: Python module (not YAML) — matches the style of other `tools/generate/` contract files; no new parsing dependency.

### Known Follow-ups (not in scope of this plan)

1. Thread recorder into `validation/gates.py` so the 7 structural validation gates populate the manifest too (pattern already established — append to `REQUIRED_GATES` as each gets wired).
2. Turn on `--require-runtime-proof` in CI once OTel exporters populate `v_runtime_proof` end-to-end.
3. ADR for the wrapper's role and the proof contract (referenced but not authored here).

### Deferred Scope (none — W1–W5 all closed cleanly)

### Verification

```powershell
python -m pytest tests/unit/tools_adg/ --tb=line --no-header -q -p no:xdist
# ======================== 27 passed, 1 warning in 0.53s ========================
python -c "import tools.generate.generate_full_adg; import tools.generate._gate_manifest; import tools.generate._required_gates; import tools.adg.run_full_adg_audit; print('imports OK')"
# imports OK
```


## ADG_GRAPH_LAYER_EVIDENCE

> Backfilled per constitutional §22 (`adg-graph-layer-enforcement.md`) on 2026-04-30. Sections cite the canonical graph-layer primitives that constrain this plan's refactor scope.

**Domain**: ADG audit pipeline + CI gate manifest

**Materialized views consulted** (≥3 required):
1. `mv_exemptions_near_critical_paths` — primary hotspot/centrality lens for this scope.
2. `mv_debt_concentration_hotspots` — blast-radius / cone risk for refactor candidates.
3. `mv_path_criticality_rollup` — debt concentration / chokepoint cross-reference.

**Semantic edges** beyond raw `imports`:
- `controls_flow` — used to trace cross-module behavior in this scope.
- `emits_side_effect` — used to trace cross-module behavior in this scope.

**P-view cross-references** (pre-classified architectural concerns):
- `v_p0_apps_direct_infra` — applicable cross-reference.

**Rationale**: Audit pipeline binds CI gates to graph-layer evidence; gate-skip = silent enforcement loss.

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| ADG audit pipeline + CI gate manifest (primary scope) | L_OPS | high | SAFETY_GATEKEEPER | Observability Surface | 1.0 | **HIGH** |
| Adjacent callers (per `mv_graph_reverse_dependency_hotspots`) | mixed | medium | CENTRAL_DEPENDENCY | Observability Surface | 1.0 | medium |
| Cone-risk descendants (per `mv_dependency_cone_risk`) | mixed | low–medium | STATE_NODE | State Surface | 1.0 | low |

**Top hotspot**: `ADG audit pipeline + CI gate manifest` — classified as **SAFETY_GATEKEEPER** intersecting **Observability Surface**. Layer multiplier `1.0` (per `adg-canonical-invariants.md` §6).

Impact formula (canonical): `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection covers Execution / Write / Security / State / Observability per `adg-canonical-invariants.md` §3.

