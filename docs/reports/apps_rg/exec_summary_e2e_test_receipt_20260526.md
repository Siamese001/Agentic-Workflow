# Executive summary — end-to-end test receipt (2026-05-26)

## Layer 1 — Deterministic pytest (no live Qwen)

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -m pytest `
  tests/_apps_contract/test_exec_summary_x2_product_gates.py `
  tests/unit/apps_rg/runtime/exit/test_executive_summary_x3_aggregate.py `
  tests/_apps_contract/test_section_x2_x1d_drift_ci.py `
  tests/unit/apps_rg/test_executive_summary_x2_x1d_adversarial.py `
  tests/_apps_contract/test_exec_summary_section_pipeline.py `
  -q -k "not test_live_cli"
```

| Result | Detail |
|--------|--------|
| **83 passed** | ~248s |
| Skipped | `test_live_cli_subprocess_when_vllm_available` (deselected via `-k`) |
| Coverage | Brown fixture (W3), X2/X1D drift, in-process lane harness (mock Qwen + mock judges) |

## Layer 2 — Live Brown SVP section lane (Qwen @ 24k)

**Pre:** `local-qwen-vllm` up, `max_model_len=24576`

```powershell
$env:VLLM_MAX_MODEL_LEN = '24576'
$env:APPS_RG_EXEC_SUMMARY_VERIFY_VLLM_CONTEXT_WINDOW = '1'

python -m apps_rg --section executive_summary `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd_exec.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md `
  --allow-non-allow-exit-zero
```

| Run | Artifact | X3 | Hardening gates |
|-----|----------|-----|-----------------|
| [exec_summary_20260526_191701](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_191701) | ~258s | `X3_REVIEW_JUDGE_SOFT_FAIL` (anthropic) | All W0/W1 coverage gates **PASS**; judges ran |
| [exec_summary_20260526_192652](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_192652) | ~73s | `X3_BLOCK` (synthesis + mechanical opener) | W0/W1 coverage gates **PASS**; `x1d_evaluator_mode=NO_JUDGE_ROWS_EMITTED` (W2) |

**Hardening gates verified on both live runs (when present in artifact):**

- `x2_unsupported_claim_zero` — PASS (no S5 false UNSUPPORTED regression)
- `x2_claim_ledger_row_count_matches_sentence_count` — PASS on 191701; PASS on 192652
- `x2_self_check_claim_ledger_consistent` — PASS when coverage passes
- `x2_claim_field_maps_to_display_sentence` — PASS

Live variance is **model prose quality** (synthesis / opener stack), not claim-coverage checker regressions.

## Layer 3 — Full modular R4 (optional, not run here)

Whole-resume E2E (all generated lanes):

```powershell
$env:PYTEST_APPS_RG_INTEGRATED_LIVE = '1'
python -m pytest tests/_apps_contract/test_integrated_spine_live_provider_e2e.py -q
```

Or CLI without `--section` (tens of minutes with live Qwen). See [integrated_r4_live_product_proof_attempt_receipt.md](integrated_r4_live_product_proof_attempt_receipt.md).

## Layer 4 — Live contract harness (other lanes)

```powershell
python ops_scripts/apps_rg/run_contract_harness_live.py
```

IBM/unify bullets/narrative subprocess lanes — serial, ~tens of minutes. Not part of this exec-summary hardening slice.

## E2E verdict

| Scope | Status |
|-------|--------|
| Claim-coverage hardening (W0–W3) | **PASS** (pytest + live gate artifacts) |
| Full product ALLOW / certification | **PARTIAL** (live LLM variance; judge or synthesis gates) |
| Recommended CI fast path | Layer 1 only (`APPS_RG_CONTRACT_HARNESS_FAST=1` skips live CLI) |

Related: [exec_summary_claim_coverage_hardening_receipt_20260526.md](exec_summary_claim_coverage_hardening_receipt_20260526.md)
