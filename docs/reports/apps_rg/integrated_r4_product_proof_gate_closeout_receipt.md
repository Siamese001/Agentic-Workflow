# Integrated-R4 Product Proof Gate — Closeout Receipt

PLAN_ID: integrated-r4-product-proof-gate

## STATUS: PASS

## SCOPE_MATCH

- Shared integrated-R4 product proof gate module added
- Validator CLI (`python -m apps_rg.runtime.integrated_product_proof_gate`)
- `guard_reject_non_product_for_certification` extended with optional `run_dir` → integrated validation
- Ten required guard tests + SP-001..SP-005 regression (24 tests)

## SCOPE_DRIFT

- None (no integrated R4 refactor; no `agentic_core` edits)

## FILES_CHANGED

- [integrated_product_proof_gate.py](apps_rg/runtime/integrated_product_proof_gate.py)
- [non_product_proof_stamp.py](apps_rg/runtime/non_product_proof_stamp.py)
- [test_integrated_product_proof_gate.py](tests/unit/apps_rg/test_integrated_product_proof_gate.py)
- [integrated_r4_product_proof_gate_closeout_receipt.md](docs/reports/apps_rg/integrated_r4_product_proof_gate_closeout_receipt.md)

## COMMANDS_RUN (exit codes)

| Command | Exit |
|---------|------|
| `python -m pytest … test_integrated_product_proof_gate.py + SP-001..005` | 0 |
| `python -m apps_rg --help` | 0 |
| `python -m apps_rg --section executive_summary --dry-run` + Brown & Brown targeting | 0 |
| `python -m apps_rg.runtime.integrated_product_proof_gate <section_run_dir> --json` | 1 |
| `python -m apps_rg.runtime.integrated_product_proof_gate certification/.../r4_latest --json --allow-contract-test-only` | 0 |
| `python -m apps_rg.runtime.integrated_product_proof_gate certification/.../r4_latest --json` | 3 (BLOCKED) |

## TESTS_GATES

- `tests/unit/apps_rg/test_integrated_product_proof_gate.py` → 12 passed
- SP-001 `test_orchestrate_full_resume_non_product_classification.py` → passed
- SP-002 `test_demo_harness_fail_closed.py` → passed
- SP-003 `test_resume_package_x3_offline_rollup_not_exit_x3.py` → passed
- SP-004 `test_section_l7_refs_do_not_upgrade_proof.py` → passed
- SP-005 `test_ci_rollup_not_product_certification.py` → passed
- **Total: 24 passed**

## PRODUCT_PROOF_GUARD

| Field | Value |
|-------|-------|
| Guard path | [integrated_product_proof_gate.py](apps_rg/runtime/integrated_product_proof_gate.py) |
| API | `validate_integrated_product_proof`, `reject_non_integrated_product_claim`, `ProductProofValidationResult` |
| Consumers wired | [non_product_proof_stamp.py](apps_rg/runtime/non_product_proof_stamp.py) `guard_reject_non_product_for_certification(..., run_dir=)` |
| CLI | `python -m apps_rg.runtime.integrated_product_proof_gate <run_dir> [--json] [--allow-contract-test-only]` |
| Rejection classifications | OFFLINE_LANE_ROLLUP, OFFLINE_PACKAGE_ROLLUP, DEMO_HARNESS, LANE_DEV_HARNESS, SECTION_L7_CORRELATION, MOCK/FIXTURE/OFFLINE_STUB/CONTRACT_TEST (for product claims), PLUMBING_ONLY (harvested) |
| Required artifacts | how_trace, spine_proof, l7_route_family_coverage, integrated manifest, route_contract, exit/x3 disposition, runtime_exhaust, no-bypass assertions |

## VALIDATION_RESULTS

| Target | Result |
|--------|--------|
| Section run `exec_summary_20260520_151944` | FAIL — `section_mode; non_product_classification` |
| Orchestrator stamp (tmp) | FAIL — `OFFLINE_LANE_ROLLUP_NOT_PRODUCT_SPINE` |
| Package X3 stamp (tmp) | FAIL — `OFFLINE_PACKAGE_ROLLUP`, `package_x3_only` |
| Demo harness stamp (tmp) | FAIL — `DEMO_HARNESS_NOT_RUNTIME_PROOF` |
| CI lane-dev stamp (tmp) | FAIL — `LANE_DEV_HARNESS` |
| Integrated R4 `r4_latest` fixture | BLOCKED (default) / CONTRACT_TEST PASS with `--allow-contract-test-only`; no live `artifacts/apps_rg/runs/cli_*` whole-run on disk |

## SHADOW_REGRESSION_CHECK

| ID | Status |
|----|--------|
| SP-001 | PASS (orchestrator stamp tests) |
| SP-002 | PASS (demo fail-closed) |
| SP-003 | PASS (package X3 not exit) |
| SP-004 | PASS (section L7 correlation) |
| SP-005 | PASS (CI rollup classification) |

## PROOF_CLASSIFICATION

- Non-product paths: `INTEGRATED_PRODUCT_PROOF_REJECTED` (FAIL)
- Contract fixture without canonical command: `CONTRACT_TEST_PROOF` (PASS, non-product)
- Product runtime (canonical whole-run): `INTEGRATED_R4_PRODUCT_RUNTIME` (requires `python -m apps_rg` evidence)

## PROTECTED_PATHS_TOUCHED

- `apps_rg/runtime/*` guard modules only

## FORBIDDEN_FILES_TOUCHED

- None (`agentic_core` untouched)

## EXPLICIT_NON_CLAIMS

- No product/Fort Knox/L7 proof unless canonical whole-run integrated R4 artifacts inspected with command evidence
- No section-only proof upgraded
- No package X3 treated as Exit X3
- No offline rollup treated as runtime proof

## NEXT_BLOCKER

- No `artifacts/apps_rg/runs/cli_*` integrated whole-run with `python -m apps_rg` command evidence on disk; live product PASS requires env/provider/judge availability for canonical full run
