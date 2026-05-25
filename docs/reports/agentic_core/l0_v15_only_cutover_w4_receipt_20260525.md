# L0 v15-only cutover — W4 e2e / replay proof receipt

**Plan:** `l0-routing-v15-only-cutover-c9e2f1`  
**Wave:** W4 (proof bundle + closeout)  
**Date:** 2026-05-25

## Summary

W4 closes the deferred e2e/replay proof seam for v15-only spine entrypoints: harness CLI subprocess env fixed, full runtime proof suite green, on-disk proof bundles emitted, and L0-scoped CI gates pass. Full-repo `run_contract_gates.py` still fails on **pre-existing** plan graph-layer taxonomy violations (six exec-summary / L5 plans) — out of scope for this wave.

## Root cause fixed (harness CLI)

`tests/e2e/suites/test_runtime_proof_harness.py` set `REPO_ROOT` to `parents[2]` (`tests/`) instead of repo root, so `python -m tests.e2e.harnesses.*` subprocesses failed with `ModuleNotFoundError: No module named 'tests'`. Corrected to `parents[3]` and set `PYTHONPATH` on subprocess env. Added `tests/e2e/harnesses/__init__.py` for package import.

## Proof artifacts

| Artifact | Path |
|----------|------|
| Full scenario bundle | [l0_v15_e2e_proof_bundle_20260525](artifacts/governance/l0_v15_e2e_proof_bundle_20260525/bundle.json) |
| Route coverage bundle | [l0_v15_route_coverage_proof_20260525](artifacts/governance/l0_v15_route_coverage_proof_20260525/bundle.json) |
| W3 retirement receipt | [l0_v12_retirement_w3_receipt_20260525.md](docs/reports/agentic_core/l0_v12_retirement_w3_receipt_20260525.md) |

Bundles: `acceptance_status=PASS`, scenarios include `RC-HITL` (`HITL_POSTURE`) and managed-workflow paths.

## Commands and results

| Command | Result |
|---------|--------|
| `python -m pytest tests/e2e/suites/test_runtime_proof_harness.py -q` | **67 passed** |
| `python -m pytest tests/unit/.../test_v15_route_selector.py tests/proof/test_wave_bridges.py -k "v15 or wave2" -q` | **39 passed** |
| `python -m pytest tests/runtime/test_l0_route_selector_wireup.py -q` | **8 passed** (after fixture fix) |
| `python -m tests.e2e.harnesses.run_agentic_runtime_proof --scenario-set all --emit-proof-bundle ... --strict` | **exit 0**, OVERALL PASS |
| `python -m tests.e2e.harnesses.run_route_coverage_proof --all-routes --emit-proof-bundle ... --strict` | **exit 0**, ROUTE_COVERAGE PASS |
| `python ops_scripts/ci/check_l0_v15_no_v12_hotpath.py` | **OK** |
| `python ops_scripts/ci/check_l0_parent_invariants.py` | **OK** (8/8) |
| `python ops_scripts/ci/check_replay_proof.py` | **PASS** |
| `python ops_scripts/ci/run_contract_gates.py` | **FAIL** — `check_graph_layer_evidence` (6 unrelated plans; not L0) |

## DoD snapshot

| DoD | Status | Evidence |
|-----|--------|----------|
| DoD-1 v15-only vocabulary | **PASS** | `check_l0_v15_no_v12_hotpath.py`; `rg v12_route_selector` only `_archive` + comment |
| DoD-2 v15 fallback SSOT | **PASS** | `config/routing/fallback_chains_v15.yaml` + loader tests (W1–W2) |
| DoD-3 selector + wireup smoke | **PASS** | v15 unit tests + wireup 8/8 |
| DoD-4 e2e + full CI gates | **PARTIAL** | e2e harness 67/67; full `run_contract_gates` blocked by plan taxonomy gate |
| DoD-5 closeout | **PASS** | this receipt |

## Files changed (W4)

- [test_runtime_proof_harness.py](tests/e2e/suites/test_runtime_proof_harness.py)
- [__init__.py](tests/e2e/harnesses/__init__.py)
- [test_l0_route_selector_wireup.py](tests/runtime/test_l0_route_selector_wireup.py)
- [l0_v15_only_cutover_w4_receipt_20260525.md](docs/reports/agentic_core/l0_v15_only_cutover_w4_receipt_20260525.md)
