# whole-run-phase1-x3-dispatch-remediation — W4 closeout receipt

**PLAN_ID:** `whole-run-phase1-x3-dispatch-remediation-f2a8c4`  
**Plan file:** [.cursor/plans/whole-run-phase1-x3-dispatch-remediation-f2a8c4.md](../../.cursor/plans/whole-run-phase1-x3-dispatch-remediation-f2a8c4.md)  
**Generated:** 2026-05-26

---

## STATUS: PARTIAL

| Wave | Status | Evidence |
|------|--------|----------|
| W1 RC-1 dict-safe X3 | PASS | 8 tests in [test_phase1_dispatch_x3_dict_pass.py](../../tests/unit/apps_rg/test_phase1_dispatch_x3_dict_pass.py) |
| W2 RC-2 resolve/abort decoupling | PASS | [test_modular_phase1_resolve_abort_decoupling.py](../../tests/unit/apps_rg/test_modular_phase1_resolve_abort_decoupling.py) |
| W3 allow_non_allow flag parity | PASS | [test_modular_phase1_allow_non_allow_exit_zero.py](../../tests/unit/apps_rg/test_modular_phase1_allow_non_allow_exit_zero.py) |
| W4 runtime whole-run | PARTIAL | Post-fix run [full_resume_983aac3da43f](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f); 1/7 lanes recipe-materialized; exit 1 |

**W4 is PARTIAL (not BLOCKED):** runtime executed; RC-1/RC-2 seams are proven against the pre-remediation baseline. Full 7/7 lane execution did not complete because wave-0 `executive_summary` returned a **legitimate** dispatch error (`X3_REVIEW_JUDGE_SOFT_FAIL`, Anthropic 3.4 &lt; 4.0), which triggers `phase1_aborted` under product fail-closed — not the false `getattr(x3, "pass_")` regression.

---

## Baseline vs post-remediation (integrated whole-run)

| Metric | Pre-fix [full_resume_1bffb730f966](artifacts/apps_rg/runtime_proofs/full_resume_1bffb730f966) | Post-fix [full_resume_983aac3da43f](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f) |
|--------|---------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| `lanes_executed` | 0 | **1** |
| `executive_summary` recipe row | `PHASE1_NO_RUN_DIR` | **`REAL_LLM`** / `X3_REVIEW_JUDGE_SOFT_FAIL` (degraded, not missing) |
| Exec summary on-disk pointer | Present but recipe ignored | [latest_successful_real_run.json](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f/lanes/executive_summary/latest_successful_real_run.json) resolved |
| `phase1_lane_inventory` exec status | `dispatch_error:lane_exit_error` (false negative: dict `pass` misread) | `dispatch_error:lane_exit_error` (**true negative**: `pass: false`, soft-fail judges) |
| Waves 1–2 lanes | `NOT_RUN` / `PHASE1_NO_RUN_DIR` | Same (aborted after wave-0 dispatch hard-fail) |
| Whole-run exit | 1 | 1 |

---

## W4.1 — Runtime proof run

**Command (WSL):**

```bash
bash ops_scripts/apps_rg/run_integrated_e2e_wsl.sh
```

Equivalent:

```bash
python -m apps_rg \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md \
  --provider qwen_vllm \
  --allow-non-allow-exit-zero
```

| Field | Value |
|-------|-------|
| Run dir | [full_resume_983aac3da43f](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f) |
| Wall time | ~283s (terminal capture) |
| Shell exit | 1 |
| vLLM | `Qwen/Qwen2.5-32B-Instruct-AWQ` @ `max_model_len=24576` (healthy preflight) |

**Terminal tail (judge regen):**

```text
Judge regen cycle 1 rejected: delta_scope_violation (floor ?). Published scratch (min ?).
Judge regen cycle 2 rejected: delta_scope_violation (floor ?). Published scratch (min ?).
Judge regen cycle 3 rejected: delta_scope_violation (floor ?). Published scratch (min 3.4).
```

**Executive summary X1D (excerpt from [command_output.txt](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f/lanes/executive_summary/command_output.txt)):**

| Provider | Score | Pass |
|----------|------:|------|
| Gemini Pro | 4.5 | True |
| OpenAI ChatGPT | 4.3 | True |
| Anthropic Claude | 3.4 | False |

**Key receipts:**

- [generate_resume_step_receipt.json](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f/modular_r4/generate_resume_step_receipt.json) — `lanes_executed: 1`, `decisive_status: FAIL` (six lanes `PHASE1_NO_RUN_DIR`; exec summary in `degraded_allowed_lane_warnings`)
- [phase1_lane_inventory.json](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f/modular_r4/phase1_lane_inventory.json) — `phase1_allow_non_allow_exit_zero_effective: false` (product fail-closed)
- [section_provider_calls.json](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f/modular_r4/section_provider_calls.json) — exec summary `provider_call_attempted: true`
- [full_run_section_status.json](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f/full_run_section_status.json) — exec summary `REAL_LLM`, `x2_pass: PASS`, `x3_code: X3_REVIEW_JUDGE_SOFT_FAIL`

---

## W4.2 — Verifier

| Command | Result |
|---------|--------|
| `python ops_scripts/apps_rg/verify_governed_spine_e2e.py --section-dir …/lanes/executive_summary` | **PASS** (governed spine; `x3_code: X3_REVIEW_JUDGE_SOFT_FAIL`) |
| `python ops_scripts/apps_rg/verify_governed_spine_e2e.py --integrated-dir …/full_resume_983aac3da43f` | **FAIL** — `section_mode; non_product_classification` (integrated gate taxonomy; not RC-1/RC-2) |

---

## Unit regression (W1–W3 + edge hardening)

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_phase1_dispatch_x3_dict_pass.py \
  tests/unit/apps_rg/test_modular_phase1_lane_dispatch_status.py \
  tests/unit/apps_rg/test_modular_phase1_resolve_abort_decoupling.py \
  tests/unit/apps_rg/test_modular_phase1_allow_non_allow_exit_zero.py \
  tests/unit/apps_rg/test_phase1_parallel_dispatcher.py \
  tests/unit/apps_rg/test_modular_resume_generation_phase1.py \
  tests/unit/apps_rg/test_integrated_executive_summary_materialization_w8c.py \
  tests/unit/apps_rg/runtime/test_product_fail_closed_p0.py \
  tests/unit/apps_rg/test_prompt_judge_x2_alignment_w0.py \
  -q -p pytest_timeout -o addopts=
```

**Result:** 85 passed (2026-05-26 closeout).

**E2E harness:** [run_governed_spine_e2e_proof.sh](../../ops_scripts/apps_rg/run_governed_spine_e2e_proof.sh) hardened (`pipefail`, `full_resume_*` discovery, CLI exit capture).

---

## Definition of Done

| DoD | Status | Note |
|-----|--------|------|
| DoD-1 dict-safe X3 | PASS | Unit tests |
| DoD-2 resolve despite dispatch error | PASS | Unit tests |
| DoD-3 multi-lane smoke | **PARTIAL** | 1/7 lanes; wave-0 soft-fail abort |
| DoD-4 recipe not false `PHASE1_NO_RUN_DIR` for exec | **PASS** | Exec summary materialized |
| DoD-5 closeout on disk | PASS | This file |

---

## Remaining blocker (out of plan scope)

**Wave-0 `X3_REVIEW_JUDGE_SOFT_FAIL`** (Anthropic Claude 3.4 &lt; 4.0) → `exit_status: error` → `phase1_dispatch_hard_failed` → `phase1_aborted` → waves 1–2 never dispatch. This is expected product fail-closed behavior after W1 correctly reads `pass: false` from the X3 dict.

**Follow-ups (separate work):**

1. Judge calibration / [executive_summary_anthropic_soft_fail_repair](executive_summary_anthropic_soft_fail_repair_closeout_receipt.md) — restore wave-0 `X3_ALLOW` or policy to continue Phase-1 on review-only soft fail.
2. Optional proof rerun: `APPS_RG_PHASE1_MAX_PARALLEL=1` if wave-1 vLLM saturation appears after (1).
3. Integrated verifier `section_mode` classification — product-proof gate, not dispatch plumbing.

---

## EXPLICIT_NON_CLAIMS

- Whole-run `outcome_authorized=true` or exit 0
- 7/7 lanes `REAL_LLM` in one run
- Fort Knox / L7 product certification
- Integrated `verify_governed_spine_e2e --integrated-dir` PASS
