# Integrated-R4 Live Product Proof Attempt — Receipt

PLAN_ID: integrated-r4-live-product-proof-attempt

## STATUS: BLOCKED

Live canonical whole-run executed; integrated-R4 spine artifacts present; **product proof validator BLOCKED** because integrated outcome was not authorized (`X3A`, L2 fault, executive_summary `PHASE1_NO_RUN_DIR`).

## SCOPE_MATCH

- Preflight + canonical `python -m apps_rg` whole-run (no `--section`)
- Artifact inspection on `artifacts/apps_rg/runs/cli_3c776e966765`
- Product proof validator + negative controls
- Tiny guard fix: live outcome blockers (no integrated R4 refactor)

## SCOPE_DRIFT

- Guard tightened (`_live_product_outcome_blockers`) to prevent PASS when `apps_rg_product_outcome_authorized=false` or integrated `X3A`

## FILES_CHANGED

- [integrated_product_proof_gate.py](apps_rg/runtime/integrated_product_proof_gate.py) — live outcome blockers + shallowest-path artifact resolution
- [integrated_r4_live_product_proof_attempt_receipt.md](docs/reports/apps_rg/integrated_r4_live_product_proof_attempt_receipt.md)

## COMMANDS_RUN (exit codes)

| Command | Exit |
|---------|------|
| `git status --short` | 0 |
| `python -m pytest …` (gate + SP-001..005, 24 tests) | 0 |
| `python -m apps_rg --help` | 0 |
| Canonical whole-run (below) | **1** |
| `python -m apps_rg.runtime.integrated_product_proof_gate artifacts/apps_rg/runs/cli_3c776e966765 --json` | **3** (BLOCKED) |
| Validator section-only dir | 1 (FAIL) |
| Validator `r4_latest` (no `--allow-contract-test-only`) | 3 (BLOCKED) |

## CANONICAL_COMMAND

```text
python -m apps_rg --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.txt
```

Evidence: modular lane `run_manifest.json` files record equivalent argv via `apps_rg/__main__.py` (no `--section`).

## LATEST_INTEGRATED_RUN_DIR

[artifacts/apps_rg/runs/cli_3c776e966765](artifacts/apps_rg/runs/cli_3c776e966765)

## ARTIFACTS_INSPECTED

| Artifact | Present | Notes |
|----------|---------|-------|
| [r4_run_manifest.json](artifacts/apps_rg/runs/cli_3c776e966765/r4_run_manifest.json) | yes | `apps_rg_product_outcome_authorized: false`, `x3_disposition: X3A`, L2 fault |
| [integrated_runtime_artifact_manifest.json](artifacts/apps_rg/runs/cli_3c776e966765/integrated_runtime_artifact_manifest.json) | yes | `integrated_r4_deterministic_pipeline` |
| [RUN_BUNDLE_INDEX.json](artifacts/apps_rg/runs/cli_3c776e966765/RUN_BUNDLE_INDEX.json) | yes | `bundle_kind: integrated_run` |
| [agentic_core_how_trace.json](artifacts/apps_rg/runs/cli_3c776e966765/agentic_core_how_trace.json) | yes | `forbidden_action_assertions` present |
| [agentic_core_spine_proof.json](artifacts/apps_rg/runs/cli_3c776e966765/agentic_core_spine_proof.json) | yes | `R1B_TERMINAL_SHORTCIRCUIT_BLOCKED`, blocking_gaps listed |
| [agentic_core_l7_route_family_coverage.json](artifacts/apps_rg/runs/cli_3c776e966765/agentic_core_l7_route_family_coverage.json) | yes | |
| [route_contract.json](artifacts/apps_rg/runs/cli_3c776e966765/route_contract.json) | yes | |
| [x3_disposition_receipt.json](artifacts/apps_rg/runs/cli_3c776e966765/x3_disposition_receipt.json) | yes | Integrated Exit **X3A** (not ALLOW) |
| [runtime_exhaust_bundle.json](artifacts/apps_rg/runs/cli_3c776e966765/runtime_exhaust_bundle.json) | yes | |
| [modular_r4/generate_resume_step_receipt.json](artifacts/apps_rg/runs/cli_3c776e966765/modular_r4/generate_resume_step_receipt.json) | yes | `decisive_status: FAIL`, `executive_summary:PHASE1_NO_RUN_DIR` |
| executive_summary lane dir | **no** | Fatal: `MISSING_LANE_RUN` / `PHASE1_NO_RUN_DIR` |

## PRODUCT_PROOF_VALIDATOR_RESULT

**BLOCKED** — `INTEGRATED_R4_PRODUCT_RUNTIME` artifact envelope satisfied, but live blockers:

- `apps_rg_product_outcome_authorized_false`
- `l2_fault: … executive_summary:PHASE1_NO_RUN_DIR`
- `integrated_x3_disposition:X3A`
- `spine_status:R1B_TERMINAL_SHORTCIRCUIT_BLOCKED`
- `spine_proof_blocking_gaps`

## MISSING_ARTIFACTS (product proof)

- **executive_summary** lane run directory (never materialized — recipe fatal)
- **outputs/generated_resume.json** / **outputs/resume.docx** per [r4_run_manifest.json](artifacts/apps_rg/runs/cli_3c776e966765/r4_run_manifest.json) (product outcome not authorized)

## PROVIDER_JUDGE_STATUS

- **Qwen vLLM**: live probe pass (`http://localhost:8000`); competencies lane `REAL_LLM`, section `X3_ALLOW`
- **X1D judges (competencies)**: Gemini Pro MODEL_BACKED_FAIL (decisive); OpenAI PASS; Anthropic soft-fail
- **IBM narrative**: `X3_REVIEW_JUDGE_SOFT_FAIL` (degraded warning, not fatal)
- **Integrated Exit**: **X3A** — product outcome **not authorized**

## NEGATIVE_CONTROL_RESULTS

| Control | Validator | Expected |
|---------|-----------|----------|
| Section-only `exec_summary_20260520_151944` | FAIL (`section_mode`) | fail |
| `r4_latest` without canonical cmd | BLOCKED | blocked |
| `r4_latest` `--allow-contract-test-only` | PASS `CONTRACT_TEST_PROOF` | contract-only |
| SP-001..SP-005 pytest | 24 passed | pass |

## SP_001_TO_SP_005_REGRESSION

24 passed (gate + shadow remediation tests).

## PROOF_CLASSIFICATION

- **Attempt**: `INTEGRATED_R4_WHOLE_RUN_BLOCKED` — artifacts present, live product proof denied
- **Not claimed**: `LIVE_RUNTIME_PROOF`, `RELEASE_ELIGIBLE_PROOF`, Fort Knox/L7 certification

## PROTECTED_PATHS_TOUCHED

- [integrated_product_proof_gate.py](apps_rg/runtime/integrated_product_proof_gate.py) only

## FORBIDDEN_FILES_TOUCHED

- None (`agentic_core` not edited this attempt)

## EXPLICIT_NON_CLAIMS

- No section-only proof upgraded
- No package X3 treated as Exit X3
- No offline rollup treated as runtime proof
- No Fort Knox/L7/product proof — validator BLOCKED on canonical whole-run
- Contract fixture (`r4_latest`) is not live product proof

## NEXT_BLOCKER

Remediate **executive_summary** `PHASE1_NO_RUN_DIR` inside modular R4 whole-run so recipe can pass and integrated Exit can reach product-authorized disposition.
